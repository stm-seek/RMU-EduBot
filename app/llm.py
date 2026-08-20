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
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass

import httpx

from .config import Settings

log = logging.getLogger("app.llm")

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}

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
    def __init__(self, status_code: int | None, body: str) -> None:
        super().__init__(f"LLM error {status_code}: {body[:400]}")
        self.status_code = status_code
        self.body = body


class LlmClient:
    """
    เรียก chat completion + embedding

    LLM และ embedding แยก config ได้ เพราะบางกรณีอยากใช้ Gemini ตอบ
    แต่รัน BGE-M3 เองสำหรับ embedding (ฟรีและรองรับไทยดี)
    """

    def __init__(self, settings: Settings, http: httpx.AsyncClient) -> None:
        self._settings = settings
        self._http = http

    async def _request_with_retry(
        self,
        url: str,
        payload: dict,
        api_key: str,
        timeout: float,
        max_attempts: int = 3,
    ) -> dict:
        """retry เฉพาะ error ที่ retry ได้ (429/5xx) — ไม่ retry 400/401"""
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._http.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=timeout,
                )
            except httpx.TimeoutException as exc:
                last_error = LlmError(None, f"timeout หลัง {timeout}s")
                log.warning("LLM timeout (ครั้งที่ %d/%d)", attempt, max_attempts)
                if attempt == max_attempts:
                    raise last_error from exc
                await asyncio.sleep(2**attempt)
                continue

            if response.status_code < 400:
                return response.json()

            if response.status_code in RETRYABLE_STATUS and attempt < max_attempts:
                wait = 2**attempt
                log.warning(
                    "LLM %s (ครั้งที่ %d/%d) — รอ %ds",
                    response.status_code,
                    attempt,
                    max_attempts,
                    wait,
                )
                await asyncio.sleep(wait)
                continue

            raise LlmError(response.status_code, response.text)

        raise last_error or LlmError(None, "เรียก LLM ไม่สำเร็จ")

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
        เรียก chat completion

        ``messages`` ใช้รูปแบบ OpenAI: ``[{"role": "system"|"user"|"assistant",
        "content": "..."}]``
        """
        settings = self._settings
        settings.require("llm_api_key")

        started = asyncio.get_event_loop().time()
        payload = {
            "model": model or settings.llm_model,
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
        )

        latency_ms = int((asyncio.get_event_loop().time() - started) * 1000)
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
        if finish_reason == "length" and not HAS_REAL_CONTENT.search(text):
            raise LlmError(
                None,
                f"โมเดลใช้ token หมดไปกับการคิดก่อนตอบจนไม่เหลือให้ตอบ "
                f"(finish_reason=length, max_tokens={payload['max_tokens']}, "
                f"ได้กลับมา {text.strip()!r}) — ต้องเพิ่ม LLM_MAX_OUTPUT_TOKENS",
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
