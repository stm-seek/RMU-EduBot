"""
LLM client แบบ OpenAI-compatible — สลับ provider ได้ด้วย ``base_url`` + ``api_key``

ยืนยันแล้วว่า provider เหล่านี้ใช้ interface เดียวกันได้:

============ ==========================================================
Gemini       ``https://generativelanguage.googleapis.com/v1beta/openai``
OpenAI       ``https://api.openai.com/v1``
OpenRouter   ``https://openrouter.ai/api/v1``
Ollama       ``http://127.0.0.1:11434/v1``
vLLM         ``http://127.0.0.1:8000/v1``
============ ==========================================================

(ทดสอบ Gemini แล้ว: POST ``/chat/completions`` และ ``/embeddings`` ด้วย key ปลอม
ได้ ``400 {"error":{"message":"Please pass a valid API key"}}`` = endpoint มีจริง)

**ตั้งใจไม่ใช้ SDK ของเจ้าไหน** เพราะ SDK แต่ละตัวผูกกับ provider ของตัวเอง
เขียนตรง ๆ ด้วย httpx ทำให้สลับได้จริงและ debug ง่ายกว่า

**ทนต่อ 503 ของ free tier** (แก้ 21 ส.ค. 2026): Gemini คืน 503 ``high demand``
แบบสุ่มบ่อยมาก จึงมีสองชั้นซ้อนกัน — retry แบบรอสั้น ๆ หลายครั้ง (มี jitter)
และถ้าโมเดลนั้นล่มยาว ก็ไล่ ``LLM_FALLBACK_MODELS`` ต่อ ทั้งหมดอยู่ใต้เพดาน
เวลารวม ``LLM_RETRY_BUDGET_SECONDS`` เพราะปลายทางคือ reply token ของ LINE
ที่หมดอายุเร็ว
"""

from __future__ import annotations

import asyncio
import logging
import random
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import httpx

from .config import Settings

log = logging.getLogger("app.llm")

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}

# ── ค่า backoff (ปรับใหม่ 21 ส.ค. 2026 จากข้อมูล 503 ของจริง) ─────────────────
# เดิมรอ 2 แล้ว 4 วินาที แล้วยอมแพ้ที่ครั้งที่ 3 = ทั้งช้าและยังพลาด
# ของจริงพบว่า 503 ของ Gemini เป็น spike ต่อ request: ยิงใหม่อีกไม่กี่วินาที
# ต่อมาก็ผ่าน จึงเปลี่ยนเป็น **รอสั้น ๆ แต่ลองมากครั้ง** (0.5 → 1 → 2 วินาที)
RETRY_BASE_DELAY_SECONDS = 0.5
RETRY_MAX_DELAY_SECONDS = 4.0
# จำนวนครั้งต่อ 1 โมเดล — ตั้ง 4 เพราะเวลาที่เหลือต้องพอให้ไล่โมเดลสำรองต่อ
# ภายในงบเดียวกัน (4 ครั้ง = รอรวม 3.5 วิ + เวลา request) ไม่ใช่หมดไปกับ
# โมเดลเดียวที่กำลังล่มอยู่
MAX_ATTEMPTS_PER_MODEL = 4
# บวกสุ่มได้ถึง 25% ของเวลารอ — กัน request ของผู้ใช้หลายคนไป retry พร้อมกัน
# เป็นจังหวะเดียว (thundering herd) ซึ่งยิ่งทำให้โมเดลที่โอเวอร์โหลดอยู่แย่ลง
JITTER_RATIO = 0.25

# ตัวอักษรหรือตัวเลขของภาษาใดก็ได้ (รวมไทย) — ใช้ตัดสินว่าคำตอบมีเนื้อจริงไหม
HAS_REAL_CONTENT = re.compile(r"[^\W_]", re.UNICODE)


@dataclass
class ChatResult:
    """ผลจาก LLM + ข้อมูลที่ต้องใช้ log ต้นทุน/latency"""

    text: str
    model: str
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    # ต้องเก็บไว้แยกให้ออกว่า 'โมเดลไม่มีอะไรจะตอบ' กับ 'token หมดกลางทาง'
    finish_reason: str | None = None


class LlmError(RuntimeError):
    """
    ความล้มเหลวของ LLM ที่ caller (router) จับไปตอบ fallback ได้

    ``retryable`` บอกว่า "ลองใหม่/สลับโมเดลแล้วมีโอกาสได้ผลต่างจากเดิมไหม"
    ค่าเริ่มต้นเดาจาก status: ``None`` (timeout/เน็ตพัง) และ 429/5xx = ลองใหม่ได้
    ส่วน 400/401/403 (key ผิด/payload ผิด) ไม่ได้ — สลับโมเดลก็พังเหมือนกัน
    """

    def __init__(
        self, status_code: int | None, body: str, *, retryable: bool | None = None
    ) -> None:
        super().__init__(f"LLM error {status_code}: {body[:400]}")
        self.status_code = status_code
        self.body = body
        self.retryable = (
            (status_code is None or status_code in RETRYABLE_STATUS)
            if retryable is None
            else retryable
        )


class BudgetExceeded(LlmError):
    """หมดงบเวลารวมแล้ว — ห้ามลองต่อ ไม่ว่าจะเหลือโมเดลสำรองอีกกี่ตัว"""

    def __init__(self, budget: float) -> None:
        super().__init__(
            None,
            f"เลิก retry เพราะใช้เวลาไปเกินงบ {budget:.0f} วินาที "
            f"(กัน reply token ของ LINE หมดอายุ)",
            retryable=False,
        )



class LlmClient:
    """
    เรียก chat completion + embedding

    LLM และ embedding แยก config ได้ เพราะบางกรณีอยากใช้ Gemini ตอบ
    แต่รัน BGE-M3 เองสำหรับ embedding (ฟรีและรองรับไทยดี)

    ``sleep``/``jitter``/``clock`` มีไว้ให้เทสฉีดของปลอมเข้ามา — เทสจึงไม่ต้อง
    รอ backoff จริงและไม่ต้องพึ่ง ``random`` (deterministic) โค้ดโปรดักชัน
    ไม่ต้องส่งอะไรเลย
    """

    def __init__(
        self,
        settings: Settings,
        http: httpx.AsyncClient,
        *,
        sleep: Callable[[float], Awaitable[None]] | None = None,
        jitter: Callable[[], float] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._settings = settings
        self._http = http
        self._sleep = sleep
        self._jitter = jitter
        # monotonic เพราะต้องวัดช่วงเวลา ไม่ใช่เวลานาฬิกา (กันเวลาระบบถูกปรับ)
        self._clock = clock or time.monotonic

    # ── retry ───────────────────────────────────────────────────────────────

    async def _wait(self, seconds: float) -> None:
        await (self._sleep or asyncio.sleep)(seconds)

    def _backoff(self, attempt: int) -> float:
        """เวลารอก่อนลองครั้งถัดไป (วินาที) — exponential + jitter"""
        delay = min(
            RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)), RETRY_MAX_DELAY_SECONDS
        )
        return delay * (1 + JITTER_RATIO * (self._jitter or random.random)())

    async def _request_with_retry(
        self,
        url: str,
        payload: dict,
        api_key: str,
        timeout: float,
        max_attempts: int = MAX_ATTEMPTS_PER_MODEL,
        *,
        deadline: float | None = None,
    ) -> dict:
        """
        retry เฉพาะ error ที่ retry ได้ (429/5xx) — ไม่ retry 400/401

        ``deadline`` (เวลาตาม ``self._clock``) คือเพดานเวลารวม: เมื่อเลยแล้ว
        โยน :class:`BudgetExceeded` ทันที **ไม่ลองต่อ** และ timeout ของแต่ละ
        request ถูกหั่นให้ไม่เกินเวลาที่เหลือด้วย เพราะ ``LLM_TIMEOUT_SECONDS``
        (60 วิ) ยาวกว่างบทั้งก้อน — request เดียวที่ค้างจะกินงบหมดถ้าไม่หั่น
        """
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            remaining = None if deadline is None else deadline - self._clock()
            if remaining is not None and remaining <= 0:
                raise self._budget_error(last_error)

            try:
                response = await self._http.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=timeout if remaining is None else min(timeout, remaining),
                )
            except httpx.TimeoutException as exc:
                last_error = LlmError(None, f"timeout หลัง {timeout}s")
                log.warning("LLM timeout (ครั้งที่ %d/%d)", attempt, max_attempts)
                if attempt == max_attempts:
                    raise last_error from exc
                await self._sleep_before_retry(
                    attempt, max_attempts, deadline, last_error, "timeout"
                )
                continue

            if response.status_code < 400:
                return response.json()

            if response.status_code in RETRYABLE_STATUS and attempt < max_attempts:
                last_error = LlmError(response.status_code, response.text)
                await self._sleep_before_retry(
                    attempt, max_attempts, deadline, last_error, response.status_code
                )
                continue

            raise LlmError(response.status_code, response.text)

        raise last_error or LlmError(None, "เรียก LLM ไม่สำเร็จ")

    async def _sleep_before_retry(
        self,
        attempt: int,
        max_attempts: int,
        deadline: float | None,
        last_error: Exception,
        reason: int | str,
    ) -> None:
        """
        รอ backoff — แต่ถ้ารอแล้วจะเลยงบเวลา ให้เลิกตรงนี้เลย

        ไม่มีประโยชน์ที่จะนอนรอครบแล้วค่อยพบว่าหมดงบ เพราะเวลานั้นคือเวลาที่
        นักศึกษานั่งรออยู่หน้าจอ LINE จริง ๆ
        """
        wait = self._backoff(attempt)
        log.warning(
            "LLM %s (ครั้งที่ %d/%d) — รอ %.1fs", reason, attempt, max_attempts, wait
        )
        if deadline is not None and self._clock() + wait >= deadline:
            raise self._budget_error(last_error)
        await self._wait(wait)

    def _budget_error(self, last_error: Exception | None) -> BudgetExceeded:
        error = BudgetExceeded(self._settings.llm_retry_budget_seconds)
        if last_error is not None:
            # เก็บสาเหตุจริงไว้ใน log ด้วย ไม่ให้ "หมดงบเวลา" กลบว่าเจอ 503
            log.warning("%s — error ล่าสุดคือ %s", error, last_error)
        return error

    # ── chat ────────────────────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> ChatResult:
        """
        เรียก chat completion — ลองโมเดลหลักก่อน แล้วไล่ ``LLM_FALLBACK_MODELS``

        ``messages`` ใช้รูปแบบ OpenAI: ``[{"role": "system"|"user"|"assistant",
        "content": "..."}]``

        **ทำไมต้องมีเชนโมเดลสำรอง**: Gemini free tier คืน 503 ``high demand``
        แบบสุ่มถี่มาก (วัด 21 ส.ค. 2026: ยิงครั้งแรกได้ 503 ทั้ง 7 ครั้ง) และ
        วัดแล้วว่า 503 เกิดแยกกันเป็นก้อนต่อโมเดล — นาทีเดียวกันที่โมเดลหลัก
        503 โมเดลสำรองตอบได้ปกติ retry อย่างเดียวจึงไม่พอถ้าโมเดลหลักล่มยาว

        เงื่อนไขการสลับโมเดล: เฉพาะ error ที่ ``retryable`` (timeout / 429 / 5xx)
        ถ้าเป็น 400/401/403 (key ผิด, payload ผิด) จะเด้งออกทันทีไม่สลับ เพราะ
        โมเดลอื่นก็พังเหมือนกัน และเงียบไว้จะทำให้ config พังโดยไม่มีใครรู้

        เพดานเวลา ``LLM_RETRY_BUDGET_SECONDS`` คุม **ทั้งเชน** ไม่ใช่ต่อโมเดล
        (ไม่งั้น 3 โมเดล × 28 วิ = ผู้ใช้รอ 84 วิ แล้ว reply token หมดอายุไปแล้ว)
        """
        settings = self._settings
        settings.require("llm_api_key")

        primary = model or settings.llm_model
        # โมเดลหลักที่ผู้เรียกระบุมาห้ามซ้ำในเชน (เสียเวลายิงซ้ำโมเดลที่ล่มอยู่)
        chain = [primary] + [
            name for name in settings.llm_fallback_model_list if name != primary
        ]

        started = self._clock()
        deadline = started + settings.llm_retry_budget_seconds
        last_error: LlmError | None = None

        for index, candidate in enumerate(chain):
            try:
                return await self._chat_once(
                    messages,
                    candidate,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    started=started,
                    deadline=deadline,
                )
            except LlmError as exc:
                if not exc.retryable:
                    raise
                last_error = exc
                if index + 1 < len(chain):
                    log.warning(
                        "โมเดล %s ใช้ไม่ได้ (status=%s) — สลับไปใช้ %s",
                        candidate,
                        exc.status_code,
                        chain[index + 1],
                    )

        raise last_error or LlmError(None, "เรียก LLM ไม่สำเร็จ")

    async def _chat_once(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float | None,
        max_tokens: int | None,
        started: float,
        deadline: float,
    ) -> ChatResult:
        """
        ยิง chat completion ด้วยโมเดลเดียว (retry ภายในโมเดลนั้นเอง)

        ``latency_ms`` นับจาก ``started`` ของ **ทั้งเชน** ไม่ใช่จากโมเดลที่ตอบ
        เพราะเลขนี้ถูก log ลง ``chat_logs`` เป็นเวลาที่นักศึกษารอจริง
        """
        settings = self._settings
        payload = {
            "model": model,
            "messages": messages,
            "temperature": (
                settings.llm_temperature if temperature is None else temperature
            ),
            "max_tokens": max_tokens or settings.llm_max_output_tokens,
        }

        data = await self._request_with_retry(
            f"{settings.llm_base_url}/chat/completions",
            payload,
            settings.llm_api_key,
            settings.llm_timeout_seconds,
            deadline=deadline,
        )

        latency_ms = int((self._clock() - started) * 1000)
        usage = data.get("usage") or {}
        choices = data.get("choices") or []
        text = ""
        finish_reason = None
        if choices:
            finish_reason = choices[0].get("finish_reason")
            text = (choices[0].get("message") or {}).get("content") or ""

        # โมเดลตระกูล thinking (gemini-3.x flash) ใช้ token ไปกับการคิดก่อนตอบ
        # ถ้า max_tokens หมดตอนคิด response จะไม่มี key "content" เลย และ
        # finish_reason = "length" — ปล่อยผ่านแล้วบอทจะส่งบับเบิลเปล่าให้นักศึกษา
        # แบบเงียบ ๆ ซึ่งแย่กว่าตอบว่าไม่รู้ จึงโยน error ให้ caller ไป fallback
        # (ยืนยันกับ gemini-3.6-flash: max_tokens=16 ได้ completion_tokens=0)
        # เช็ค HAS_REAL_CONTENT ไม่ใช่แค่ strip() เพราะวัดของจริงแล้วพบว่า
        # max_tokens=16 บางครั้งได้ ":" กลับมา ซึ่ง strip() แล้วยังไม่ว่าง
        # แต่ก็ไม่ใช่คำตอบ — คำตอบที่ถูกตัดกลางประโยคแต่ยังมีเนื้อ ปล่อยผ่านไป
        # ให้ caller ตัดสินใจเองผ่าน finish_reason
        #
        # ``retryable=False`` ตั้งใจ: **ไม่สลับโมเดล**สำหรับเคสนี้ เพราะสาเหตุคือ
        # LLM_MAX_OUTPUT_TOKENS ตั้งต่ำเกินไป ซึ่งใช้กับทุกโมเดลในเชนเหมือนกัน
        # → สลับไปก็เจอเหมือนเดิม เสีย token เสียเวลาของนักศึกษา แล้วสุดท้าย
        # error ที่เด้งออกก็ตัวเดียวกัน ยอมเด้งเร็วเพื่อให้เห็นว่า config ผิด
        if finish_reason == "length" and not HAS_REAL_CONTENT.search(text):
            raise LlmError(
                None,
                f"โมเดลใช้ token หมดไปกับการคิดก่อนตอบจนไม่เหลือให้ตอบ "
                f"(finish_reason=length, max_tokens={payload['max_tokens']}, "
                f"ได้กลับมา {text.strip()!r}) — ต้องเพิ่ม LLM_MAX_OUTPUT_TOKENS",
                retryable=False,
            )

        return ChatResult(
            text=text.strip(),
            model=data.get("model") or payload["model"],
            prompt_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            latency_ms=latency_ms,
            finish_reason=finish_reason,
        )

    # ── embedding ───────────────────────────────────────────────────────────

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        สร้าง embedding หลายข้อความในครั้งเดียว

        ตรวจมิติที่ได้กับ ``EMBEDDING_DIM`` ด้วย เพราะถ้าไม่ตรงกับ
        ``vector(N)`` ใน Postgres จะ insert ไม่ผ่าน — ดักตรงนี้ให้ error
        อ่านง่ายกว่าไปพังที่ DB
        """
        if not texts:
            return []

        settings = self._settings
        if not settings.embedding_key:
            raise RuntimeError("ยังไม่ได้ตั้งค่าใน .env: EMBEDDING_API_KEY หรือ LLM_API_KEY")

        data = await self._request_with_retry(
            f"{settings.embedding_base_url}/embeddings",
            {
                "model": settings.embedding_model,
                "input": texts,
                # ต้องส่งไปเสมอ — gemini-embedding-* ให้ 3072 มิติเป็นค่าเริ่มต้น
                # ซึ่ง insert ลง vector(768) ไม่ผ่าน ขอ 768 แล้วได้เวกเตอร์ที่
                # normalize มาแล้ว (วัด L2 norm = 1.000 กับ gemini-embedding-2)
                # provider ที่ไม่รู้จักฟิลด์นี้จะมองข้ามไป ถ้าเจอที่ 400 ให้ดู
                # guard มิติข้างล่างเป็นตัวบอกว่าเพี้ยนตรงไหน
                "dimensions": settings.embedding_dim,
            },
            settings.embedding_key,
            settings.llm_timeout_seconds,
            # embedding ไม่มีเพดานเวลารวมและลองแค่ 3 ครั้งตามเดิม — ทางนี้ถูกเรียก
            # จากงาน ingest/scrape ที่ไม่มี reply token รออยู่ (รอ 40 วิ ไม่มีใคร
            # เดือดร้อน) และการยิงซ้ำหลายครั้งกิน quota embedding เปล่า ๆ
            max_attempts=3,
        )

        items = sorted(data.get("data") or [], key=lambda d: d.get("index", 0))
        vectors = [item["embedding"] for item in items]

        if vectors and len(vectors[0]) != settings.embedding_dim:
            raise RuntimeError(
                f"มิติ embedding ไม่ตรง: model ให้ {len(vectors[0])} "
                f"แต่ EMBEDDING_DIM={settings.embedding_dim} "
                f"(ต้องแก้ .env และ vector(N) ใน 001_init.sql ให้ตรงกัน แล้ว re-index)"
            )
        return vectors

    async def embed_one(self, text: str) -> list[float]:
        """embedding ข้อความเดียว — ใช้ตอนรับคำถามจาก user"""
        vectors = await self.embed([text])
        if not vectors:
            raise RuntimeError("ไม่ได้ embedding กลับมา")
        return vectors[0]
