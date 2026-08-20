"""
เทส ``app.ai_chat`` — ชั้นที่ 3 (Requirement ข้อ 9)

เป้าหมายที่ล็อกไว้:

1. **เงื่อนไขไม่ครบ → คืน ``None``** เพื่อให้ router ถอยกลับไปตอบ fallback
   (ไม่ใช่ 500 ไม่ใช่เงียบ) ทั้งสี่กรณี: ปิดสวิตช์, ไม่มี key, ไม่มี DB, ไม่มี
   user_hash
2. **บริบทแยกตามผู้ใช้** — ``ensure_user`` ถูกเรียกด้วย ``user_hash`` และ
   ประวัติถูกดึงด้วย ``user_id`` ที่คืนมา ไม่ปนกันข้ามคน
3. **system prompt ห้ามเดาข้อมูลราชการ** — ตรวจว่าข้อความบังคับอยู่ในนั้น
4. **กัน context บวม** — ข้อความยาวพิเศษถูกตัดเพดานก่อนนับงบ
5. **LLM พัง → โยน ``LlmError``** ให้ผู้เรียก fallback (ไม่กลืน)
"""

from __future__ import annotations

import httpx
import pytest

from app import ai_chat, router as bot_router
from app.config import Settings
from app.llm import LlmClient, LlmError

from .helpers import FakeWriteDatabase, Recorder, make_settings


def chat_ok(text: str = "แนะนำให้อ่านเป็นรอบสั้น ๆ ครับ") -> dict:
    return {
        "model": "gemini-3.5-flash-lite",
        "choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 120, "completion_tokens": 40},
    }


def make_llm(recorder: Recorder) -> LlmClient:
    return LlmClient(make_settings(llm_api_key="test_key"), recorder.client())


def settings(**overrides) -> Settings:
    return make_settings(llm_api_key="test_key", **overrides)


USER_HASH = "a" * 64


# ── เงื่อนไขไม่ครบ → คืน None ──────────────────────────────────────────────


async def test_returns_none_when_disabled() -> None:
    db = FakeWriteDatabase({"RETURNING id": {"id": 7}})
    result = await ai_chat.answer(
        settings(ai_chat_enabled=False), make_llm(Recorder((200, chat_ok()))),
        db, USER_HASH, "อ่านหนังสือยังไง",
    )
    assert result is None


async def test_returns_none_without_llm_key() -> None:
    db = FakeWriteDatabase({"RETURNING id": {"id": 7}})
    llm = LlmClient(make_settings(), Recorder((200, chat_ok())).client())
    result = await ai_chat.answer(
        make_settings(), llm, db, USER_HASH, "อ่านหนังสือยังไง",
    )
    assert result is None


async def test_returns_none_without_db() -> None:
    result = await ai_chat.answer(
        settings(), make_llm(Recorder((200, chat_ok()))), None, USER_HASH, "ถาม"
    )
    assert result is None


async def test_returns_none_without_user_hash() -> None:
    db = FakeWriteDatabase({"RETURNING id": {"id": 7}})
    result = await ai_chat.answer(
        settings(), make_llm(Recorder((200, chat_ok()))), db, None, "ถาม"
    )
    assert result is None


# ── เงื่อนไขครบ → ตอบด้วย LLM ─────────────────────────────────────────────


async def test_answers_with_llm_and_logs_model_tokens() -> None:
    db = FakeWriteDatabase({"RETURNING id": {"id": 7}})
    recorder = Recorder((200, chat_ok()))

    result = await ai_chat.answer(settings(), make_llm(recorder), db, USER_HASH, "อ่านหนังสือยังไง")

    assert result is not None
    assert result.answered_by == "ai_chat"
    assert result.llm_model == "gemini-3.5-flash-lite"
    assert result.prompt_tokens == 120
    assert result.output_tokens == 40
    assert "แนะนำให้อ่าน" in result.messages[0]["text"]
    assert result.user_id == 7


async def test_ensures_user_before_reading_history() -> None:
    """user_id จาก ensure_user ต้องถูกใช้ดึงประวัติ — แยกบริบทตามผู้ใช้"""
    db = FakeWriteDatabase({"RETURNING id": {"id": 42}})
    await ai_chat.answer(
        settings(), make_llm(Recorder((200, chat_ok()))), db, USER_HASH, "ถาม"
    )

    # ensure_user ถูกเรียกด้วย hash
    assert db.params_for("INSERT INTO app_users") == (USER_HASH,)
    # ดึงประวัติด้วย user_id ที่คืนมา ไม่ใช่ hash
    history_params = db.params_for("FROM chat_logs")
    assert history_params[0] == 42


async def test_empty_llm_answer_raises() -> None:
    """LLM ตอบว่าง (safety filter) → ต้องโยน LlmError ไม่ใช่ส่งบับเบิลเปล่า"""
    db = FakeWriteDatabase({"RETURNING id": {"id": 7}})
    with pytest.raises(LlmError):
        await ai_chat.answer(
            settings(), make_llm(Recorder((200, chat_ok("")))), db, USER_HASH, "ถาม"
        )


# ── system prompt ──────────────────────────────────────────────────────────


def test_system_prompt_forbids_making_up_official_data() -> None:
    assert "ห้ามแต่งข้อมูลทางการ" in ai_chat.SYSTEM_PROMPT
    assert "ภาษาไทย" in ai_chat.SYSTEM_PROMPT


def test_system_prompt_forbids_collecting_personal_data() -> None:
    assert "รหัสนักศึกษา" in ai_chat.SYSTEM_PROMPT


# ── กัน context บวม ────────────────────────────────────────────────────────


def test_history_messages_keep_user_before_assistant_old_to_new() -> None:
    """
    ลำดับที่ส่งเข้า LLM ต้องเป็น user→assistant ต่อรอบ และเก่า→ใหม่
    (เคยมีบั๊กจริง: กลับทั้งก้อนแล้ว assistant นำหน้า user ในแต่ละรอบ)
    """
    rows = [
        {"message_text": "ถามแรก", "response_text": "ตอบแรก"},
        {"message_text": "ถามสอง", "response_text": "ตอบสอง"},
    ]
    messages = ai_chat.build_history_messages(rows, max_chars=10_000)
    assert messages == [
        {"role": "user", "content": "ถามแรก"},
        {"role": "assistant", "content": "ตอบแรก"},
        {"role": "user", "content": "ถามสอง"},
        {"role": "assistant", "content": "ตอบสอง"},
    ]


def test_history_messages_respect_char_budget() -> None:
    rows = [
        {"message_text": "ก" * 800, "response_text": "ข" * 800},
        {"message_text": "สั้น", "response_text": "สั้น"},
    ]
    messages = ai_chat.build_history_messages(rows, max_chars=1_000)

    # รอบล่าสุดต้องอยู่ และรอบที่ยาวจนเกินงบต้องถูกตัดออก
    assert any(m["content"] == "สั้น" for m in messages)
    total = sum(len(m["content"]) for m in messages)
    assert total <= 1_000


def test_history_entries_are_truncated() -> None:
    rows = [{"message_text": "ย" * 5_000, "response_text": "ซ" * 5_000}]
    messages = ai_chat.build_history_messages(rows, max_chars=100_000)
    for m in messages:
        assert len(m["content"]) <= ai_chat.HISTORY_ENTRY_LIMIT


def test_build_messages_starts_with_system_and_ends_with_question() -> None:
    history = [
        {"role": "user", "content": "เก่า"},
        {"role": "assistant", "content": "ตอบเก่า"},
    ]
    messages = ai_chat.build_messages(history, "คำถามใหม่")
    assert messages[0]["role"] == "system"
    assert messages[-1] == {"role": "user", "content": "คำถามใหม่"}
    assert messages[1:-1] == history


# ── router ถอยกลับเป็น fallback ────────────────────────────────────────────


async def test_router_falls_back_when_no_llm() -> None:
    """ไม่มี LLM → handle_text ยังตอบ fallback แบบเดิม ไม่พัง"""
    result = await bot_router.handle_text("อ่านหนังสือยังไง", FakeWriteDatabase())
    assert result.answered_by == "fallback"


async def test_router_uses_ai_chat_when_available() -> None:
    db = FakeWriteDatabase({"RETURNING id": {"id": 1}})
    result = await bot_router.handle_text(
        "อ่านหนังสือยังไง",
        db,
        settings=settings(),
        llm=make_llm(Recorder((200, chat_ok()))),
        user_hash=USER_HASH,
    )
    assert result.answered_by == "ai_chat"


async def test_router_falls_back_on_llm_error() -> None:
    db = FakeWriteDatabase({"RETURNING id": {"id": 1}})
    recorder = Recorder((200, chat_ok("")))  # ตอบว่าง → LlmError
    result = await bot_router.handle_text(
        "อ่านหนังสือยังไง", db, settings=settings(), llm=make_llm(recorder), user_hash=USER_HASH
    )
    assert result.answered_by == "fallback"
    assert "ขัดข้อง" in result.messages[0]["text"]
