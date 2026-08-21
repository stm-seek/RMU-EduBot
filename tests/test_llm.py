"""
เทส LLM client แบบ OpenAI-compatible

เป้าหมายของ client ตัวนี้คือ **สลับ provider ได้ด้วย base_url + api_key เท่านั้น**
เทสจึงล็อกรูปแบบ request ตามสเปก OpenAI ไว้ (``/chat/completions``,
``/embeddings``, ``Authorization: Bearer``) เพราะถ้าเพี้ยนไปแม้แต่นิด
จะใช้กับ Gemini/OpenAI/Ollama ร่วมกันไม่ได้

เทส retry ทุกตัว **patch ``asyncio.sleep`` เป็น no-op** และฉีด jitter คงที่
— ของจริงรอ 0.5/1/2 วินาที ถ้าไม่ patch ชุดเทสจะช้าจนคนไม่อยากรัน และถ้าไม่
ฉีด jitter ผลจะสุ่มไปด้วย (ดู ``no_sleep`` และ ``llm_client`` ข้างล่าง)
"""

from __future__ import annotations

import json
from typing import Callable

import httpx
import pytest

from app import llm as llm_module
from app.llm import ChatResult, LlmClient, LlmError

from .helpers import Recorder, make_settings

PROMPT = [{"role": "user", "content": "ถอนรายวิชาวันสุดท้ายวันไหน"}]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """ตัดเวลารอ backoff ออกจากเทส (ของจริง 0.5 + 1 + 2 วินาที)"""

    async def _instant(_seconds: float) -> None:
        return None

    monkeypatch.setattr(llm_module.asyncio, "sleep", _instant)


def llm_settings(**overrides):
    # ปิด fallback เป็นค่าเริ่มต้นของเทสส่วนใหญ่ — เทสเก่าทุกตัวเขียนไว้ตอนที่
    # ยังไม่มีฟีเจอร์นี้ และต้องยืนยันว่าพฤติกรรม "โมเดลเดียว" ยังเหมือนเดิม
    overrides.setdefault("llm_fallback_models", "")
    return make_settings(llm_api_key="test_llm_key", **overrides)


def make_client(settings, http: httpx.AsyncClient, **kwargs) -> LlmClient:
    """
    ``LlmClient`` ที่ jitter เป็น 0 คงที่ — เทสจึง deterministic

    ของจริงใช้ ``random.random()`` ซึ่งถ้าปล่อยไว้ เทสที่นับเวลา/งบเวลา
    จะผ่านหรือไม่ผ่านแบบสุ่ม
    """
    kwargs.setdefault("jitter", lambda: 0.0)
    return LlmClient(settings, http, **kwargs)


def make_http(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def chat_response(text: str = "ตอบแล้วครับ", **extra) -> dict:
    body = {
        "model": "gemini-3.6-flash",
        "choices": [{"message": {"role": "assistant", "content": text}}],
        "usage": {"prompt_tokens": 120, "completion_tokens": 45},
    }
    body.update(extra)
    return body


# ── chat: request ที่ส่งออกไป ───────────────────────────────────────────────


async def test_chat_requires_api_key() -> None:
    recorder = Recorder((200, chat_response()))

    async with recorder.client() as http:
        with pytest.raises(RuntimeError, match="LLM_API_KEY"):
            await LlmClient(make_settings(), http).chat(PROMPT)

    assert recorder.count == 0, "ไม่มี key ต้องไม่ยิง request"


async def test_chat_request_follows_openai_spec() -> None:
    recorder = Recorder((200, chat_response()))
    settings = llm_settings()

    async with recorder.client() as http:
        await LlmClient(settings, http).chat(PROMPT)

    request = recorder.requests[0]
    assert str(request.url) == f"{settings.llm_base_url}/chat/completions"
    assert request.headers["authorization"] == "Bearer test_llm_key"
    assert recorder.json_body() == {
        "model": settings.llm_model,
        "messages": PROMPT,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_output_tokens,
    }


async def test_chat_allows_per_call_overrides() -> None:
    """
    บางงานต้องคุมค่าเอง เช่นเรียบเรียงผลจาก planner ควรใช้ temperature ต่ำ
    """
    recorder = Recorder((200, chat_response()))

    async with recorder.client() as http:
        await LlmClient(llm_settings(), http).chat(
            PROMPT, temperature=0.0, max_tokens=64, model="gemini-2.5-flash"
        )

    body = recorder.json_body()
    assert body["temperature"] == 0.0
    assert body["max_tokens"] == 64
    assert body["model"] == "gemini-2.5-flash"


async def test_chat_temperature_zero_is_not_treated_as_missing() -> None:
    """
    ``temperature=0.0`` เป็น falsy — ถ้าโค้ดเช็คด้วย ``or`` จะถูกแทนด้วยค่า default
    เงียบ ๆ ทำให้คำตอบไม่ deterministic ตามที่สั่ง
    """
    recorder = Recorder((200, chat_response()))

    async with recorder.client() as http:
        await LlmClient(llm_settings(llm_temperature=0.7), http).chat(
            PROMPT, temperature=0.0
        )

    assert recorder.json_body()["temperature"] == 0.0


async def test_chat_base_url_has_no_double_slash() -> None:
    """config strip ``/`` ท้าย base_url ไว้ — ป้องกัน ``//chat/completions``"""
    recorder = Recorder((200, chat_response()))
    settings = llm_settings(llm_base_url="https://api.openai.com/v1/")

    async with recorder.client() as http:
        await LlmClient(settings, http).chat(PROMPT)

    assert str(recorder.requests[0].url) == "https://api.openai.com/v1/chat/completions"


# ── chat: การอ่าน response ──────────────────────────────────────────────────


async def test_chat_parses_text_and_usage() -> None:
    """token count ต้องเก็บได้ เพราะใช้ log ต้นทุนลง ``chat_logs``"""
    recorder = Recorder((200, chat_response("  ตอบแล้วครับ  ")))

    async with recorder.client() as http:
        result = await LlmClient(llm_settings(), http).chat(PROMPT)

    assert isinstance(result, ChatResult)
    assert result.text == "ตอบแล้วครับ", "ต้อง strip ช่องว่างหัวท้าย"
    assert result.model == "gemini-3.6-flash"
    assert result.prompt_tokens == 120
    assert result.output_tokens == 45
    assert result.latency_ms is not None and result.latency_ms >= 0


async def test_chat_handles_response_without_choices() -> None:
    """
    provider บางตัวคืน ``choices`` ว่างเมื่อโดน safety filter
    ต้องได้ ``text=''`` ให้ caller ไป fallback ต่อ ไม่ใช่ ``KeyError``
    """
    recorder = Recorder((200, {"model": "m", "choices": []}))

    async with recorder.client() as http:
        result = await LlmClient(llm_settings(), http).chat(PROMPT)

    assert result.text == ""
    assert result.prompt_tokens is None


async def test_chat_handles_null_content() -> None:
    recorder = Recorder((200, {"choices": [{"message": {"content": None}}]}))

    async with recorder.client() as http:
        result = await LlmClient(llm_settings(), http).chat(PROMPT)

    assert result.text == ""


# ── retry ───────────────────────────────────────────────────────────────────


async def test_retries_on_server_error_then_succeeds() -> None:
    recorder = Recorder((500, {"error": "internal"}), (200, chat_response()))

    async with recorder.client() as http:
        result = await LlmClient(llm_settings(), http).chat(PROMPT)

    assert recorder.count == 2
    assert result.text == "ตอบแล้วครับ"


async def test_retries_on_rate_limit() -> None:
    """429 คือเคสที่เจอบ่อยสุดกับ free tier ของ Gemini"""
    recorder = Recorder((429, {"error": "rate limited"}), (200, chat_response()))

    async with recorder.client() as http:
        await LlmClient(llm_settings(), http).chat(PROMPT)

    assert recorder.count == 2


async def test_does_not_retry_client_error() -> None:
    """
    400/401 retry ไปก็ได้ผลเดิม — เสียเวลาและเสียโควตาเปล่า
    (key ผิดจะได้ 400 จาก Gemini ทันที)
    """
    recorder = Recorder((400, {"error": {"message": "Please pass a valid API key"}}))

    async with recorder.client() as http:
        with pytest.raises(LlmError) as info:
            await LlmClient(llm_settings(), http).chat(PROMPT)

    assert recorder.count == 1
    assert info.value.status_code == 400
    assert "valid API key" in info.value.body


async def test_gives_up_after_four_attempts_on_the_same_model() -> None:
    """
    เพดานต่อโมเดลคือ 4 ครั้ง (ปรับจาก 3 เมื่อ 21 ส.ค. 2026)

    ของจริงวัดได้ว่า 503 ``high demand`` ของ Gemini เป็น spike ต่อ request
    ยิงใหม่อีกไม่กี่วินาทีก็ผ่าน จึง "รอสั้นลองมากครั้ง" แทน "รอนานยอมแพ้เร็ว"
    แต่ไม่ลองเกินนี้ เพราะต้องเหลือเวลาให้ไล่โมเดลสำรองในงบเดียวกัน
    """
    recorder = Recorder((503, {"error": "unavailable"}))

    async with recorder.client() as http:
        with pytest.raises(LlmError) as info:
            await LlmClient(llm_settings(), http).chat(PROMPT)

    assert recorder.count == llm_module.MAX_ATTEMPTS_PER_MODEL == 4
    assert info.value.status_code == 503


async def test_timeout_becomes_llm_error() -> None:
    """
    timeout ต้องกลายเป็น ``LlmError`` ไม่ใช่ ``httpx.TimeoutException`` หลุดออกไป
    — caller (router) จับ ``LlmError`` แล้วตอบ fallback ให้ user
    """
    attempts = 0

    def timeout_handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("อืดเกินไป", request=request)

    async with make_http(timeout_handler) as http:
        with pytest.raises(LlmError, match="timeout"):
            await LlmClient(llm_settings(), http).chat(PROMPT)

    assert attempts == llm_module.MAX_ATTEMPTS_PER_MODEL


async def test_chat_rejects_empty_answer_when_reasoning_ate_the_budget() -> None:
    """
    โมเดล thinking ใช้ token หมดไปกับการคิดจนไม่เหลือให้ตอบ

    ยืนยันกับ ``gemini-3.6-flash`` ของจริงเมื่อ 19 ส.ค. 2026: ``max_tokens=16``
    ได้ ``finish_reason='length'``, ``completion_tokens=0`` และ message
    **ไม่มี key ``content`` เลย** ถ้าปล่อยผ่านบอทจะส่งบับเบิลเปล่าให้นักศึกษา
    แบบเงียบ ๆ ซึ่งแย่กว่าตอบว่าไม่รู้ (ตาม Requirement ข้อ 14)
    """
    recorder = Recorder(
        (
            200,
            {
                "model": "gemini-3.6-flash",
                "choices": [
                    {"message": {"role": "assistant"}, "finish_reason": "length"}
                ],
                "usage": {"prompt_tokens": 14, "completion_tokens": 0},
            },
        )
    )

    async with recorder.client() as http:
        with pytest.raises(LlmError, match="LLM_MAX_OUTPUT_TOKENS"):
            await LlmClient(llm_settings(), http).chat(PROMPT)


async def test_chat_keeps_finish_reason_for_logging() -> None:
    """
    ``finish_reason`` ต้องไม่ถูกทิ้ง — ใช้แยกใน ``chat_logs`` ว่าคำตอบจบเองหรือ
    ถูกตัดกลางทาง ซึ่งเป็นตัวเลขที่ต้องรายงานในธีสิส
    """
    recorder = Recorder(
        (
            200,
            chat_response(
                choices=[
                    {
                        "message": {"role": "assistant", "content": "ตอบแล้วครับ"},
                        "finish_reason": "stop",
                    }
                ]
            ),
        )
    )

    async with recorder.client() as http:
        result = await LlmClient(llm_settings(), http).chat(PROMPT)

    assert result.text == "ตอบแล้วครับ"
    assert result.finish_reason == "stop"


async def test_retries_twice_then_succeeds_on_the_third_call() -> None:
    """
    เคสที่เจอจริงบน production 21 ส.ค. 2026: 503 ``high demand`` ติดกันสองครั้ง
    แล้วครั้งที่ 3 ผ่าน — ผู้ใช้ต้องได้คำตอบ ไม่ใช่ข้อความ "ระบบขัดข้อง"
    """
    recorder = Recorder(
        (503, {"error": {"code": 503, "message": "high demand"}}),
        (503, {"error": {"code": 503, "message": "high demand"}}),
        (200, chat_response()),
    )

    async with recorder.client() as http:
        result = await make_client(llm_settings(), http).chat(PROMPT)

    assert recorder.count == 3
    assert result.text == "ตอบแล้วครับ"


# ── เชนโมเดลสำรอง (แก้ 503 high demand ที่โมเดลหลักล่มยาว) ───────────────────


class FakeClock:
    """
    นาฬิกาปลอมสำหรับเทสงบเวลา — คืนค่าตามลำดับที่กำหนด (ค่าท้ายค้างไว้)

    ต้องปลอมเพราะเทสจะรอเวลาจริงไม่ได้ และการนับเวลาจริงบนเครื่องที่รันเทส
    ทำให้ผลลัพธ์แกว่งตามความเร็วเครื่อง
    """

    def __init__(self, *values: float) -> None:
        self._values = list(values)
        self.calls = 0

    def __call__(self) -> float:
        value = self._values[min(self.calls, len(self._values) - 1)]
        self.calls += 1
        return value


def chain_settings(**overrides):
    """settings ที่เปิดเชนสำรอง 2 ตัว (ชื่อโมเดลตรงกับที่ยืนยันกับ API จริง)"""
    return make_settings(
        llm_api_key="test_llm_key",
        llm_model="gemini-3.5-flash-lite",
        llm_fallback_models="gemini-3.1-flash-lite, gemini-3-flash-preview",
        **overrides,
    )


def only_model_works(
    good_model: str | None,
) -> tuple[Callable[[httpx.Request], httpx.Response], list[str]]:
    """
    handler ที่ตอบ 200 ให้โมเดลเดียว ที่เหลือ 503 (เลียนแบบ high demand)

    ``good_model=None`` = ทุกโมเดล 503 คืน list ของชื่อโมเดลที่ถูกยิงจริงมาด้วย
    เพื่อให้เทสตรวจได้ว่าไล่เชนตามลำดับและไม่ยิงซ้ำโมเดลที่ล่มแล้ว
    """
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        model = json.loads(request.content)["model"]
        seen.append(model)
        if model != good_model:
            return httpx.Response(
                503, json={"error": {"code": 503, "message": "high demand"}}
            )
        # provider สะท้อนชื่อโมเดลที่ตอบจริงกลับมาในฟิลด์ ``model``
        return httpx.Response(200, json=chat_response(model=model))

    return handler, seen


async def test_switches_to_the_fallback_model_when_the_primary_is_overloaded() -> None:
    """
    หัวใจของการแก้ 21 ส.ค. 2026 — วัดของจริงแล้วว่า 503 เกิดแยกกันต่อโมเดล
    (นาทีเดียวกัน ``gemini-3.5-flash-lite`` 503 แต่ ``gemini-3.1-flash-lite``
    ตอบได้ปกติ) retry อย่างเดียวจึงไม่พอถ้าโมเดลหลักล่มยาว

    ``ChatResult.model`` ต้องเป็นชื่อโมเดล **ที่ตอบจริง** เพราะ ``app/ai_chat.py``
    log ค่านี้ลง ``chat_logs`` และธีสิสใช้ตัวเลขนี้รายงาน
    """
    handler, seen = only_model_works("gemini-3.1-flash-lite")

    async with make_http(handler) as http:
        result = await make_client(chain_settings(), http).chat(PROMPT)

    assert result.text == "ตอบแล้วครับ"
    assert result.model == "gemini-3.1-flash-lite", "ต้องเป็นโมเดลที่ตอบจริง"
    # ลองโมเดลหลักครบ 4 ครั้งก่อน แล้วค่อยข้ามไปสำรองตัวแรก
    assert seen == ["gemini-3.5-flash-lite"] * 4 + ["gemini-3.1-flash-lite"]


async def test_raises_when_every_model_in_the_chain_is_overloaded() -> None:
    """
    ทุกตัวในเชน 503 → ต้องโยน ``LlmError`` ออกไปให้ router ตอบ fallback ตามเดิม
    (ห้ามคืนคำตอบว่างเงียบ ๆ ซึ่งจะกลายเป็นบับเบิลเปล่าใน LINE)
    """
    handler, seen = only_model_works(None)

    async with make_http(handler) as http:
        with pytest.raises(LlmError) as info:
            await make_client(chain_settings(), http).chat(PROMPT)

    assert info.value.status_code == 503
    assert len(seen) == 3 * llm_module.MAX_ATTEMPTS_PER_MODEL, "3 โมเดล × 4 ครั้ง"
    assert seen[-1] == "gemini-3-flash-preview", "ตัวสุดท้ายในเชนต้องถูกลองด้วย"


@pytest.mark.parametrize("status", [400, 401])
async def test_client_error_skips_both_retry_and_fallback(status: int) -> None:
    """
    key ผิด/payload ผิด = สลับโมเดลก็พังเหมือนกัน — ต้องเด้งทันทีที่ยิงครั้งแรก

    ถ้าปล่อยให้ไล่เชน จะกลายเป็นยิงเปล่า 12 ครั้งทุกครั้งที่ตั้ง ``.env`` ผิด
    แล้ว config ที่ผิดจะถูกกลบด้วยข้อความ 503 จนหาสาเหตุไม่เจอ
    """
    recorder = Recorder((status, {"error": {"message": "Please pass a valid API key"}}))

    async with recorder.client() as http:
        with pytest.raises(LlmError) as info:
            await make_client(chain_settings(), http).chat(PROMPT)

    assert recorder.count == 1, "ห้าม retry และห้ามสลับโมเดล"
    assert info.value.status_code == status
    assert info.value.retryable is False


async def test_stops_when_the_wall_clock_budget_is_used_up() -> None:
    """
    เพดานเวลารวมคุม **ทั้งเชน** — เลยงบแล้วต้องเลิกทันที ห้ามลองโมเดลถัดไป

    เหตุผล: reply token ของ LINE อายุสั้น ถ้าไล่ 3 โมเดล × งบต่อโมเดล
    ผู้ใช้จะรอเป็นนาทีแล้วสุดท้ายตอบผ่าน reply ไม่ได้ (ต้องไป push ซึ่งกินโควตา)

    นาฬิกาปลอมกระโดดไป 40 วินาที (เกินงบ 28) หลังยิงครั้งแรก
    """
    clock = FakeClock(0.0, 0.0, 40.0)
    handler, seen = only_model_works(None)

    async with make_http(handler) as http:
        client = make_client(chain_settings(), http, clock=clock)
        with pytest.raises(LlmError, match="เกินงบ"):
            await client.chat(PROMPT)

    assert seen == ["gemini-3.5-flash-lite"], "หมดงบแล้วห้ามยิงต่อ ไม่ว่ากี่โมเดล"


async def test_does_not_fall_back_when_output_budget_was_eaten_by_thinking() -> None:
    """
    ``finish_reason=length`` + ไม่มีเนื้อ = ``LLM_MAX_OUTPUT_TOKENS`` ตั้งต่ำเกินไป
    ซึ่งใช้ร่วมกันทุกโมเดลในเชน → สลับไปก็เจอเหมือนเดิม เสีย token เปล่า
    จึงตั้งใจให้เด้งออกทันทีเพื่อให้เห็นว่าเป็นปัญหา config ไม่ใช่โมเดลล่ม
    """
    recorder = Recorder(
        (
            200,
            {
                "model": "gemini-3.5-flash-lite",
                "choices": [
                    {"message": {"role": "assistant"}, "finish_reason": "length"}
                ],
                "usage": {"prompt_tokens": 14, "completion_tokens": 0},
            },
        )
    )

    async with recorder.client() as http:
        with pytest.raises(LlmError, match="LLM_MAX_OUTPUT_TOKENS"):
            await make_client(chain_settings(), http).chat(PROMPT)

    assert recorder.count == 1, "ห้ามสลับโมเดลเพราะ max_tokens ไม่พอ"


async def test_empty_fallback_setting_keeps_the_old_single_model_behaviour() -> None:
    """
    regression guard: ``LLM_FALLBACK_MODELS`` ว่าง = ปิดฟีเจอร์สนิท

    ยิงแค่โมเดลหลักตามจำนวนครั้งของโมเดลเดียว ไม่มีชื่อโมเดลอื่นหลุดออกไป
    (สำคัญกับคนที่ใช้ provider อื่นซึ่งไม่มีโมเดลชื่อ gemini-* อยู่จริง)
    """
    handler, seen = only_model_works(None)

    async with make_http(handler) as http:
        with pytest.raises(LlmError):
            await make_client(llm_settings(), http).chat(PROMPT)

    assert seen == [llm_settings().llm_model] * llm_module.MAX_ATTEMPTS_PER_MODEL


async def test_explicit_model_argument_is_not_repeated_in_the_chain() -> None:
    """
    ผู้เรียกระบุ ``model=`` ที่ตรงกับตัวในเชนสำรอง — ต้องไม่ยิงโมเดลนั้นซ้ำสองรอบ
    (เสียเวลาในงบเดียวกันไปกับโมเดลที่เพิ่งล่มไปเมื่อกี้)
    """
    handler, seen = only_model_works(None)

    async with make_http(handler) as http:
        with pytest.raises(LlmError):
            await make_client(chain_settings(), http).chat(
                PROMPT, model="gemini-3.1-flash-lite"
            )

    assert seen[: llm_module.MAX_ATTEMPTS_PER_MODEL] == ["gemini-3.1-flash-lite"] * 4
    assert seen.count("gemini-3.1-flash-lite") == 4, "ห้ามยิงซ้ำรอบสอง"
    assert set(seen) == {"gemini-3.1-flash-lite", "gemini-3-flash-preview"}


# ── embedding ───────────────────────────────────────────────────────────────


async def test_embed_empty_list_skips_request() -> None:
    recorder = Recorder((200, {"data": []}))

    async with recorder.client() as http:
        assert await LlmClient(llm_settings(), http).embed([]) == []

    assert recorder.count == 0


async def test_embed_falls_back_to_llm_key() -> None:
    """ไม่ตั้ง ``EMBEDDING_API_KEY`` → ใช้ ``LLM_API_KEY`` (provider เดียวกัน)"""
    recorder = Recorder((200, {"data": [{"index": 0, "embedding": [0.1] * 768}]}))

    async with recorder.client() as http:
        await LlmClient(llm_settings(), http).embed(["ทดสอบ"])

    assert recorder.requests[0].headers["authorization"] == "Bearer test_llm_key"


async def test_embed_prefers_dedicated_key() -> None:
    """
    แยก key ได้เพราะอาจใช้ Gemini ตอบ แต่รัน BGE-M3 เองสำหรับ embedding
    """
    recorder = Recorder((200, {"data": [{"index": 0, "embedding": [0.1] * 768}]}))
    settings = llm_settings(embedding_api_key="embed_key")

    async with recorder.client() as http:
        await LlmClient(settings, http).embed(["ทดสอบ"])

    assert recorder.requests[0].headers["authorization"] == "Bearer embed_key"
    assert str(recorder.requests[0].url) == f"{settings.embedding_base_url}/embeddings"
    assert recorder.json_body() == {
        "model": settings.embedding_model,
        "input": ["ทดสอบ"],
        # ต้องมี — ถ้าหายไป gemini จะคืน 3072 มิติแล้ว insert ลง vector(768) ไม่ผ่าน
        "dimensions": settings.embedding_dim,
    }


async def test_embed_requires_some_key() -> None:
    recorder = Recorder((200, {"data": []}))

    async with recorder.client() as http:
        with pytest.raises(RuntimeError, match="EMBEDDING_API_KEY"):
            await LlmClient(make_settings(), http).embed(["ทดสอบ"])

    assert recorder.count == 0


async def test_embed_reorders_by_index() -> None:
    """
    provider ไม่รับประกันลำดับ — ถ้าไม่เรียงตาม ``index`` embedding จะไปผูกกับ
    ข้อความผิดตัว แล้ว RAG จะ retrieve ผิดทั้งระบบโดยไม่มี error ให้เห็น
    """
    recorder = Recorder(
        (
            200,
            {
                "data": [
                    {"index": 2, "embedding": [0.3] * 768},
                    {"index": 0, "embedding": [0.1] * 768},
                    {"index": 1, "embedding": [0.2] * 768},
                ]
            },
        )
    )

    async with recorder.client() as http:
        vectors = await LlmClient(llm_settings(), http).embed(["ก", "ข", "ค"])

    assert [round(vector[0], 1) for vector in vectors] == [0.1, 0.2, 0.3]


async def test_embed_rejects_wrong_dimension() -> None:
    """
    มิติไม่ตรงกับ ``vector(N)`` ใน Postgres จะ insert ไม่ผ่าน
    → ดักที่นี่ให้ error อ่านง่ายกว่าไปพังที่ DB
    """
    recorder = Recorder((200, {"data": [{"index": 0, "embedding": [0.1] * 1024}]}))

    async with recorder.client() as http:
        with pytest.raises(RuntimeError, match="EMBEDDING_DIM=768"):
            await LlmClient(llm_settings(embedding_dim=768), http).embed(["ทดสอบ"])


async def test_embed_one_returns_single_vector() -> None:
    recorder = Recorder((200, {"data": [{"index": 0, "embedding": [0.5] * 768}]}))

    async with recorder.client() as http:
        vector = await LlmClient(llm_settings(), http).embed_one("คำถามของผู้ใช้")

    assert len(vector) == 768


async def test_embed_one_raises_when_nothing_returned() -> None:
    recorder = Recorder((200, {"data": []}))

    async with recorder.client() as http:
        with pytest.raises(RuntimeError, match="embedding"):
            await LlmClient(llm_settings(), http).embed_one("คำถาม")
