"""
เทส ``app.ai_chat`` — โหมดปรึกษา AI (ชั้นที่ 3, Requirement ข้อ 9)

เป้าหมายที่ล็อกไว้:

1. **เงื่อนไขไม่ครบ → คืน ``None``** เพื่อให้ router ถอยกลับไปตอบ fallback
   (ไม่ใช่ 500 ไม่ใช่เงียบ) ทั้งหกกรณี: ไม่มี settings, ไม่มี llm, ปิดสวิตช์,
   ไม่มี key, ไม่มี DB, ไม่มี user_hash
2. **เข้าโหมดชัด ๆ** — ปุ่ม postback หรือข้อความนำหน้า "ปรึกษา" เท่านั้นที่
   เปิด session/เรียก LLM; ข้อความธรรมดาที่ไม่มี session เปิดอยู่ต้องคืน
   ``None`` ให้ router ไป search/fallback (**ไม่เสีย token ฟรี**)
3. **ออกได้ 4 ทาง** — ปุ่มจบ, คำออก (exact match เท่านั้น), timeout, ครบรอบ
4. **บริบทแยกตามผู้ใช้** — ``ensure_user`` ถูกเรียกด้วย ``user_hash`` และ
   ประวัติถูกดึงด้วย ``user_id`` ที่คืนมา ไม่ปนกันข้ามคน
5. **system prompt ห้ามเดาข้อมูลราชการ** — ตรวจว่าข้อความบังคับอยู่ในนั้น
6. **กัน context บวม** — ข้อความยาวพิเศษถูกตัดเพดานก่อนนับงบ
7. **LLM พัง → โยน ``LlmError``** ให้ผู้เรียก fallback (ไม่กลืน)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
NOW = datetime.now(timezone.utc)


def session_row(turn_count: int = 1, age_minutes: float = 0.0) -> dict:
    """แถว session ตามที่ ``active_ai_session_by_hash`` คืนมา"""
    return {
        "id": 3,
        "last_active_at": NOW - timedelta(minutes=age_minutes),
        "turn_count": turn_count,
    }


def db_with_session(session: dict | None) -> FakeWriteDatabase:
    """fake ที่ (อาจจะ) มี session เปิดอยู่ของ user คนนี้"""
    rules: dict = {"RETURNING id": {"id": 7}}
    if session is not None:
        rules["JOIN app_users"] = session
    return FakeWriteDatabase(rules)


# ── เงื่อนไขไม่ครบ → คืน None ──────────────────────────────────────────────


async def test_returns_none_when_disabled() -> None:
    result = await ai_chat.dispatch(
        settings(ai_chat_enabled=False), make_llm(Recorder((200, chat_ok()))),
        db_with_session(None), USER_HASH, "ปรึกษา อ่านหนังสือยังไง",
    )
    assert result is None


async def test_returns_none_without_llm_key() -> None:
    llm = LlmClient(make_settings(), Recorder((200, chat_ok())).client())
    result = await ai_chat.dispatch(
        make_settings(), llm, db_with_session(None), USER_HASH, "ปรึกษา ถาม",
    )
    assert result is None


async def test_returns_none_without_db() -> None:
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), None, USER_HASH, "ปรึกษา ถาม"
    )
    assert result is None


async def test_returns_none_without_user_hash() -> None:
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), db_with_session(None), None, "ปรึกษา ถาม"
    )
    assert result is None


async def test_returns_none_without_settings_or_llm() -> None:
    db = db_with_session(None)
    assert await ai_chat.dispatch(None, None, db, USER_HASH, "ปรึกษา ถาม") is None
    assert await ai_chat.dispatch(settings(), None, db, USER_HASH, "ปรึกษา ถาม") is None
    assert await ai_chat.dispatch(None, make_llm(Recorder()), db, USER_HASH, "ปรึกษา ถาม") is None


async def test_plain_text_without_session_returns_none_and_calls_no_llm() -> None:
    """
    ข้อความธรรมดาที่ไม่มี session เปิดอยู่ = ไม่ใช่เรื่องของชั้นนี้
    router จะเอาไป search/fallback ต่อ — **LLM ต้องไม่ถูกเรียก**
    """
    recorder = Recorder((200, chat_ok()))
    result = await ai_chat.dispatch(
        settings(), make_llm(recorder), db_with_session(None), USER_HASH,
        "อ่านหนังสือยังไง",
    )
    assert result is None
    assert recorder.count == 0


# ── เข้าโหมด: ปุ่ม / คำนำหน้า "ปรึกษา" ──────────────────────────────────────


async def test_enter_with_prefix_and_question_answers_and_opens_session() -> None:
    db = db_with_session(None)
    recorder = Recorder((200, chat_ok()))

    result = await ai_chat.dispatch(
        settings(), make_llm(recorder), db, USER_HASH, "ปรึกษา อ่านหนังสือยังไง"
    )

    assert result is not None
    assert result.answered_by == "ai_chat"
    assert result.intent_key == "ai_chat"
    assert result.llm_model == "gemini-3.5-flash-lite"
    assert result.prompt_tokens == 120
    assert result.output_tokens == 40
    assert "แนะนำให้อ่าน" in result.messages[0]["text"]
    assert result.user_id == 7

    # session ถูกเปิด (INSERT INTO ai_sessions) และนับรอบแล้ว (UPDATE turn_count)
    assert any("INSERT INTO ai_sessions" in sql for sql, _ in db.calls)
    assert any("turn_count = turn_count + 1" in sql for sql, _ in db.executed)

    # LLM ได้คำถามจริง ไม่ใช่ข้อความรวมคำนำหน้า
    payload = recorder.json_body()
    assert payload["messages"][-1]["content"] == "อ่านหนังสือยังไง"


async def test_enter_with_prefix_only_opens_session_without_llm_call() -> None:
    db = db_with_session(None)
    recorder = Recorder((200, chat_ok()))

    result = await ai_chat.dispatch(
        settings(), make_llm(recorder), db, USER_HASH, "ปรึกษา"
    )

    assert result is not None
    assert result.intent_key == "ai_session_open"
    assert "โหมดปรึกษาเปิดแล้ว" in result.messages[0]["text"]
    assert recorder.count == 0, "เข้าโหมดเฉย ๆ ต้องไม่เสีย token"


async def test_enter_by_postback_opens_session() -> None:
    db = db_with_session(None)
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), db, USER_HASH, "",
        is_session_postback=True,
    )
    assert result is not None
    assert result.intent_key == "ai_session_open"


async def test_enter_again_while_session_open_continues_not_duplicates() -> None:
    """เข้าโหมดซ้ำระหว่างเปิดอยู่ = ถามต่อ — ห้าม INSERT session แถวที่สอง"""
    db = db_with_session(session_row())
    recorder = Recorder((200, chat_ok()))

    result = await ai_chat.dispatch(
        settings(), make_llm(recorder), db, USER_HASH, "",
        is_session_postback=True,
    )

    assert result is not None
    assert result.intent_key == "ai_chat", "ต้องตอบ LLM ต่อ ไม่ใช่เปิด session ซ้ำ"
    inserts = [sql for sql, _ in db.calls if "INSERT INTO ai_sessions" in sql]
    assert inserts == []


# ── ระหว่างอยู่ในโหมด ────────────────────────────────────────────────────────


async def test_in_session_plain_text_goes_to_llm() -> None:
    db = db_with_session(session_row())
    recorder = Recorder((200, chat_ok()))

    result = await ai_chat.dispatch(
        settings(), make_llm(recorder), db, USER_HASH, "แล้วต้องทำยังไงอีก"
    )

    assert result is not None
    assert result.intent_key == "ai_chat"
    assert recorder.count == 1


async def test_in_session_history_is_fetched_for_the_same_user() -> None:
    """บริบทแยกตามผู้ใช้ — ประวัติถูกดึงด้วย user_id จาก ensure_user"""
    db = db_with_session(session_row())
    recorder = Recorder((200, chat_ok()))

    await ai_chat.dispatch(
        settings(), make_llm(recorder), db, USER_HASH, "ถามต่อ"
    )

    assert db.params_for("INSERT INTO app_users") == (USER_HASH,)
    assert db.params_for("FROM chat_logs")[0] == 7


# ── ออกโหมด: ปุ่ม / คำออก / timeout / ครบรอบ ────────────────────────────────


async def test_end_postback_closes_open_session() -> None:
    db = db_with_session(session_row())
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), db, USER_HASH, "",
        is_end_postback=True,
    )

    assert result is not None
    assert result.intent_key == "ai_session_close"
    assert "จบโหมดปรึกษาแล้ว" in result.messages[0]["text"]
    assert db.executed_for("ended_at = now()") == ("button", 3)


async def test_end_postback_without_session_still_replies() -> None:
    """ไม่มี session ก็ต้องตอบ (user กดปุ่มของเราต้องไม่เงียบ) แต่ไม่เขียน DB"""
    db = db_with_session(None)
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), db, USER_HASH, "",
        is_end_postback=True,
    )
    assert result is not None
    assert result.intent_key == "ai_session_close"
    assert db.executed == []


async def test_exit_keyword_closes_session() -> None:
    db = db_with_session(session_row())
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), db, USER_HASH, "ออก"
    )
    assert result is not None
    assert result.intent_key == "ai_session_close"
    assert db.executed_for("ended_at = now()") == ("keyword", 3)


async def test_exit_keyword_without_session_falls_through() -> None:
    """พิมพ์ "ออก" โดยไม่มีโหมด = ข้อความธรรมดา ให้ router ไป search/fallback"""
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), db_with_session(None),
        USER_HASH, "ออก",
    )
    assert result is None


async def test_exit_requires_exact_match_not_substring() -> None:
    """
    contains ไม่ได้ — "อยาก**ออก**กลางคันต้องทำไง" เป็นคำถามในโหมด
    ไม่ใช่คำสั่งออก (exact match หลัง strip เท่านั้น)
    """
    db = db_with_session(session_row())
    recorder = Recorder((200, chat_ok()))

    result = await ai_chat.dispatch(
        settings(), make_llm(recorder), db, USER_HASH, "อยากออกกลางคันต้องทำไง"
    )

    assert result is not None
    assert result.intent_key == "ai_chat", "ต้องตอบเป็นคำถาม ไม่ใช่ปิดโหมด"
    closed = [sql for sql, _ in db.executed if "ended_at = now()" in sql]
    assert closed == [], "คำถามในโหมดต้องไม่ปิด session"


async def test_expired_session_answers_timeout_close_on_next_message() -> None:
    """ว่างเกิน 30 นาที → ข้อความถัดไปปิด session และบอกให้เริ่มใหม่"""
    db = db_with_session(session_row(age_minutes=31))
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), db, USER_HASH,
        "กลับมาคุยต่อ",
    )

    assert result is not None
    assert result.intent_key == "ai_session_timeout"
    assert db.executed_for("ended_at = now()") == ("timeout", 3)


async def test_enter_with_expired_session_closes_old_and_opens_new() -> None:
    db = db_with_session(session_row(age_minutes=31))
    result = await ai_chat.dispatch(
        settings(), make_llm(Recorder((200, chat_ok()))), db, USER_HASH, "ปรึกษา"
    )

    assert result is not None
    assert result.intent_key == "ai_session_open"
    # ปิดเก่า (timeout) แล้วเปิดใหม่
    assert db.executed_for("ended_at = now()") == ("timeout", 3)
    assert any("INSERT INTO ai_sessions" in sql for sql, _ in db.calls)


async def test_turn_limit_closes_session_without_llm_call() -> None:
    db = db_with_session(session_row(turn_count=20))
    recorder = Recorder((200, chat_ok()))

    result = await ai_chat.dispatch(
        settings(), make_llm(recorder), db, USER_HASH, "ถามอีกข้อ"
    )

    assert result is not None
    assert result.intent_key == "ai_session_turn_limit"
    assert "ครบตามที่ระบบกำหนด" in result.messages[0]["text"]
    assert db.executed_for("ended_at = now()") == ("turn_limit", 3)
    assert recorder.count == 0


async def test_turn_limit_is_configurable() -> None:
    db = db_with_session(session_row(turn_count=2))
    result = await ai_chat.dispatch(
        settings(ai_chat_session_max_turns=2), make_llm(Recorder((200, chat_ok()))),
        db, USER_HASH, "ถามอีกข้อ",
    )
    assert result is not None and result.intent_key == "ai_session_turn_limit"


# ── LLM พัง ─────────────────────────────────────────────────────────────────


async def test_empty_llm_answer_raises() -> None:
    """LLM ตอบว่าง (safety filter) → ต้องโยน LlmError ไม่ใช่ส่งบับเบิลเปล่า"""
    with pytest.raises(LlmError):
        await ai_chat.dispatch(
            settings(), make_llm(Recorder((200, chat_ok("")))),
            db_with_session(session_row()), USER_HASH, "ถามต่อ",
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


# ── router: ถอยกลับเป็น fallback / เสนอทางเข้าโหมด ──────────────────────────


async def test_router_falls_back_when_no_llm() -> None:
    """ไม่มี LLM → handle_text ยังตอบ fallback แบบเดิม ไม่พัง"""
    result = await bot_router.handle_text("ปรึกษา อ่านหนังสือยังไง", FakeWriteDatabase())
    assert result.answered_by == "fallback"


async def test_router_answers_ai_chat_on_consult_prefix() -> None:
    db = db_with_session(None)
    result = await bot_router.handle_text(
        "ปรึกษา อ่านหนังสือยังไง",
        db,
        settings=settings(),
        llm=make_llm(Recorder((200, chat_ok()))),
        user_hash=USER_HASH,
    )
    assert result.answered_by == "ai_chat"


async def test_router_search_miss_does_not_call_llm_anymore() -> None:
    """
    หัวใจของการกัน token: search ไม่เจอ **ต้องไม่ยิง LLM ทันที**
    แต่ตอบ fallback พร้อมปุ่ม "ปรึกษา AI" ให้ user เลือกเข้าโหมดเอง
    """
    recorder = Recorder((200, chat_ok()))
    result = await bot_router.handle_text(
        "อ่านหนังสือยังไง",
        db_with_session(None),
        settings=settings(),
        llm=make_llm(recorder),
        user_hash=USER_HASH,
    )
    assert result.answered_by == "fallback"
    assert recorder.count == 0
    labels = [
        item["action"]["label"] for item in result.messages[0]["quickReply"]["items"]
    ]
    assert "ปรึกษา AI" in labels


async def test_router_falls_back_on_llm_error() -> None:
    db = db_with_session(session_row())
    recorder = Recorder((200, chat_ok("")))  # ตอบว่าง → LlmError
    result = await bot_router.handle_text(
        "ถามต่อในโหมด", db, settings=settings(), llm=make_llm(recorder), user_hash=USER_HASH
    )
    assert result.answered_by == "fallback"
    assert "ขัดข้อง" in result.messages[0]["text"]


async def test_router_ai_session_postback_without_llm_falls_back() -> None:
    """ปุ่มปรึกษา AI ตอนยังไม่ตั้ง key → fallback ไม่ใช่เงียบ"""
    result = await bot_router.handle_postback(
        "action=ai_session", FakeWriteDatabase(), settings=make_settings(), llm=None
    )
    assert result.answered_by == "fallback"
