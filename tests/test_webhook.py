"""
เทส ``POST /webhook`` แบบ end-to-end (ยังไม่แตะเน็ตเวิร์กจริง)

ลำดับที่ไฟล์นี้ล็อกไว้ และห้ามเปลี่ยน:

1. verify signature (เร็ว)
2. **ตอบ 200 ทันที** — ถ้าช้า LINE จะ retry แล้ว user ได้ข้อความซ้ำ
3. ประมวลผลใน background แล้วค่อย reply/push

และเงื่อนไขที่เพิ่งแก้บั๊กไป: **คิดคำตอบก่อน แล้วค่อยสร้าง ``LineClient``**
เพื่อให้ตอน dev ที่ยังไม่มี ``LINE_CHANNEL_ACCESS_TOKEN`` ได้ log ที่อ่านรู้เรื่อง
ไม่ใช่ traceback ทุก event (ซึ่งทำให้ทดสอบ router ไม่ได้เลย)
"""

from __future__ import annotations

import json
import logging

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.line.signature import compute_signature

from .helpers import (
    TEST_ACCESS_TOKEN,
    TEST_CHANNEL_SECRET,
    TEST_REPLY_TOKEN,
    TEST_USER_ID,
    FakeDatabase,
    Recorder,
    make_settings,
)

REPLY_PATH = "/v2/bot/message/reply"
PUSH_PATH = "/v2/bot/message/push"


# ── ตัวช่วยประกอบ request ───────────────────────────────────────────────────


def encode(payload: dict) -> bytes:
    """LINE ส่ง JSON ที่ไม่ escape ภาษาไทย — เลียนแบบให้ตรง"""
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def post(
    client: TestClient, body: bytes, signature: str | None = None
) -> httpx.Response:
    """
    ยิง webhook — ``signature=None`` หมายถึง **ไม่ส่ง header เลย**
    """
    headers = {"Content-Type": "application/json"}
    if signature is not None:
        headers["X-Line-Signature"] = signature
    return client.post("/webhook", content=body, headers=headers)


def post_signed(
    client: TestClient, payload: dict, *, secret: str = TEST_CHANNEL_SECRET
) -> httpx.Response:
    body = encode(payload)
    return post(client, body, compute_signature(secret, body))


def envelope(*events: dict) -> dict:
    return {"destination": "Ubotdestination0000000000000000", "events": list(events)}


def message_event(text: str = "เทอมหน้าควรลงวิชาอะไร", **overrides) -> dict:
    event = {
        "type": "message",
        "mode": "active",
        "timestamp": 1_700_000_000_000,
        "webhookEventId": "01H0000000000000000000000",
        "deliveryContext": {"isRedelivery": False},
        "replyToken": TEST_REPLY_TOKEN,
        "source": {"type": "user", "userId": TEST_USER_ID},
        "message": {"id": "444573844083572737", "type": "text", "text": text},
    }
    event.update(overrides)
    return event


def postback_event(data: str = "action=plan") -> dict:
    return {
        "type": "postback",
        "mode": "active",
        "timestamp": 1_700_000_000_000,
        "replyToken": TEST_REPLY_TOKEN,
        "source": {"type": "user", "userId": TEST_USER_ID},
        "postback": {"data": data},
    }


def follow_event() -> dict:
    return {
        "type": "follow",
        "mode": "active",
        "timestamp": 1_700_000_000_000,
        "replyToken": TEST_REPLY_TOKEN,
        "source": {"type": "user", "userId": TEST_USER_ID},
    }


def sending_settings(**overrides):
    """settings ที่ส่งข้อความได้จริง (มี access token)"""
    return make_settings(line_channel_access_token=TEST_ACCESS_TOKEN, **overrides)


# ── signature: ต้องปฏิเสธก่อนทำอะไรทั้งสิ้น ─────────────────────────────────


def test_rejects_wrong_signature(make_client) -> None:
    client = make_client()
    # HTTP header เป็น ASCII เท่านั้น — ใช้ค่าหน้าตาเหมือน base64 แต่ผิด
    wrong = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    response = post(client, encode(envelope(message_event())), wrong)

    assert response.status_code == 403
    assert response.json() == {"message": "invalid signature"}


def test_rejects_missing_signature_header(make_client) -> None:
    client = make_client()
    response = post(client, encode(envelope(message_event())))

    assert response.status_code == 403


def test_rejects_replayed_signature(make_client) -> None:
    """
    signature ที่ถูกต้องของ body เก่า ใช้กับ body ใหม่ไม่ได้

    ถ้าผ่านได้ = คนที่เคยเห็น request หนึ่งครั้งจะสั่งบอทได้ตลอดไป
    """
    client = make_client()
    old_body = encode(envelope(follow_event()))
    new_body = encode(envelope(message_event("ยิงแทรก")))

    response = post(client, new_body, compute_signature(TEST_CHANNEL_SECRET, old_body))

    assert response.status_code == 403


def test_rejects_signature_from_another_secret(make_client) -> None:
    client = make_client()
    payload = envelope(message_event())

    assert post_signed(client, payload, secret="secret-ของคนอื่น").status_code == 403


def test_refuses_everything_when_secret_not_configured(make_client) -> None:
    """
    ยังไม่ตั้ง ``LINE_CHANNEL_SECRET`` ต้อง 503 (ไม่ใช่ 200 แบบเงียบ ๆ)

    ถ้าปล่อย 200 จะดูเหมือนทำงานได้ ทั้งที่ verify ไม่ได้เลย
    """
    client = make_client(make_settings(line_channel_secret=""))
    response = post_signed(client, envelope(message_event()))

    assert response.status_code == 503


def test_verifies_against_raw_body_not_reserialized_json(make_client) -> None:
    """
    signature คำนวณจากไบต์ดิบ — ถ้าโค้ด parse JSON แล้ว dump ใหม่ก่อน verify
    request จริงจาก LINE (ที่จัดรูปแบบต่างจาก json.dumps ของเรา) จะถูกปฏิเสธทั้งหมด
    """
    client = make_client()
    body = b'{ "destination" : "Ub" ,  "events" : [ ] }'

    response = post(client, body, compute_signature(TEST_CHANNEL_SECRET, body))

    assert response.status_code == 200


# ── payload ที่ผิดรูป ───────────────────────────────────────────────────────


def test_invalid_json_returns_400(make_client) -> None:
    """signature ถูกแต่ body ไม่ใช่ JSON → 400 (ไม่ใช่ 500)"""
    client = make_client()
    body = "ไม่ใช่ json เลย".encode("utf-8")

    response = post(client, body, compute_signature(TEST_CHANNEL_SECRET, body))

    assert response.status_code == 400
    assert response.json() == {"message": "invalid json"}


def test_empty_events_returns_200(make_client) -> None:
    """
    ปุ่ม Verify ใน LINE Console ยิง ``{"events":[]}`` มา — ต้องตอบ 200
    ไม่งั้นตั้ง Webhook URL ไม่ผ่าน
    """
    client = make_client()
    response = post_signed(client, {"destination": "Ub", "events": []})

    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_missing_events_key_returns_200(make_client) -> None:
    client = make_client()
    assert post_signed(client, {"destination": "Ub"}).status_code == 200


# ── เส้นทางที่ตอบได้จริง ────────────────────────────────────────────────────


def test_text_message_gets_replied(make_client) -> None:
    """เคสหลัก: ข้อความไทย → 200 และ reply ออกไปที่ LINE จริง ๆ (mock)"""
    recorder = Recorder((200, {}))
    client = make_client(sending_settings(), recorder.client())

    response = post_signed(client, envelope(message_event()))

    assert response.status_code == 200
    assert recorder.paths() == [REPLY_PATH]
    body = recorder.json_body()
    assert body["replyToken"] == TEST_REPLY_TOKEN
    assert len(body["messages"]) <= 5
    assert body["messages"][0]["type"] == "text"


def test_postback_gets_replied(make_client) -> None:
    recorder = Recorder((200, {}))
    client = make_client(sending_settings(), recorder.client())

    response = post_signed(client, envelope(postback_event("action=documents")))

    assert response.status_code == 200
    assert recorder.paths() == [REPLY_PATH]


def test_follow_gets_welcome_message(make_client) -> None:
    recorder = Recorder((200, {}))
    client = make_client(sending_settings(), recorder.client())

    post_signed(client, envelope(follow_event()))

    assert recorder.paths() == [REPLY_PATH]
    assert recorder.json_body()["messages"][0]["quickReply"]["items"]


def test_non_text_message_says_so(make_client) -> None:
    """สติกเกอร์/รูป/เสียง — บอกตรง ๆ ว่ายังไม่รองรับ ไม่ใช่เงียบ"""
    recorder = Recorder((200, {}))
    client = make_client(sending_settings(), recorder.client())
    event = message_event()
    event["message"] = {"id": "1", "type": "sticker", "packageId": "1", "stickerId": "1"}

    post_signed(client, envelope(event))

    assert "ข้อความตัวอักษร" in recorder.json_body()["messages"][0]["text"]


def test_every_event_in_batch_is_processed(make_client) -> None:
    """
    LINE ส่งได้หลาย event ต่อ request — ถ้าประมวลผลแค่ตัวแรก
    user คนที่ 2 จะไม่ได้คำตอบ (และไม่มี error ให้เห็น)
    """
    recorder = Recorder((200, {}))
    client = make_client(sending_settings(), recorder.client())

    post_signed(client, envelope(message_event("คำถามที่ 1"), postback_event()))

    assert recorder.paths() == [REPLY_PATH, REPLY_PATH]


def test_falls_back_to_push_when_reply_token_expired(make_client) -> None:
    """
    RAG/LLM ช้าเกิน reply token หมดอายุ → ต้อง push ให้ user ได้คำตอบ
    """
    recorder = Recorder((400, {"message": "Invalid reply token"}), (200, {}))
    client = make_client(sending_settings(), recorder.client())

    response = post_signed(client, envelope(message_event()))

    assert response.status_code == 200
    assert recorder.paths() == [REPLY_PATH, PUSH_PATH]


def test_unknown_event_type_is_ignored_quietly(make_client) -> None:
    """
    LINE เพิ่ม event ใหม่ได้ตลอด (join / leave / memberJoined ...)
    ต้องไม่ส่งอะไรและไม่พัง
    """
    recorder = Recorder((200, {}))
    client = make_client(sending_settings(), recorder.client())
    event = {"type": "join", "replyToken": TEST_REPLY_TOKEN, "source": {"type": "group"}}

    response = post_signed(client, envelope(event))

    assert response.status_code == 200
    assert recorder.count == 0


# ── process_event: พฤติกรรมเมื่อ config ไม่ครบ ──────────────────────────────


async def test_process_event_without_token_logs_instead_of_raising(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """
    บั๊กที่แก้ไป: เดิมสร้าง ``LineClient`` ก่อนคิดคำตอบ → ทุก event เป็น
    traceback ``LINE_CHANNEL_ACCESS_TOKEN`` ทำให้ทดสอบ router ไม่ได้เลย

    ตอนนี้ต้อง: คิดคำตอบได้ครบ แล้ว log warning ว่าส่งไม่ได้ — **ไม่มี ERROR**
    """
    recorder = Recorder((200, {}))
    monkeypatch.setattr(main, "_http", recorder.client())

    with caplog.at_level(logging.DEBUG, logger="app.main"):
        await main.process_event(message_event(), make_settings())

    assert recorder.count == 0, "ไม่มี token ต้องไม่ยิง LINE API"

    errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
    assert errors == [], f"ไม่ควรมี ERROR/traceback: {[r.message for r in errors]}"

    warnings = [record for record in caplog.records if record.levelno == logging.WARNING]
    assert warnings, "ต้อง log warning บอกว่าส่งไม่ได้เพราะ config"
    text = caplog.text
    assert "LINE_CHANNEL_ACCESS_TOKEN" in text
    assert "router คิดคำตอบไว้แล้ว" in text


async def test_process_event_needs_reply_token_or_user_id(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """ไม่มีทั้ง replyToken และ userId = ตอบกลับไม่ได้ → เตือนแล้วจบ"""
    recorder = Recorder((200, {}))
    monkeypatch.setattr(main, "_http", recorder.client())
    event = message_event()
    del event["replyToken"]
    event["source"] = {"type": "user"}

    with caplog.at_level(logging.WARNING, logger="app.main"):
        await main.process_event(event, sending_settings())

    assert recorder.count == 0
    assert "ตอบไม่ได้" in caplog.text


async def test_process_event_swallows_line_api_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """
    background task ที่ปล่อย exception หลุด = ไม่มีใครเห็น
    → ต้องจับแล้ว log ให้ครบ (reply พัง แล้ว push พังด้วย)
    """
    recorder = Recorder((400, {"message": "Invalid reply token"}), (500, {}))
    monkeypatch.setattr(main, "_http", recorder.client())

    with caplog.at_level(logging.ERROR, logger="app.main"):
        await main.process_event(message_event(), sending_settings())

    assert "LINE API" in caplog.text


async def test_process_event_logs_which_channel_was_used(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """
    log ต้องบอก ``by=`` (ชั้นที่ตอบ) และ ``ผ่าน=`` (reply/push)
    — ตัวเลขนี้ใช้วัดผลในธีสิสว่าแต่ละชั้นรับภาระเท่าไหร่

    ใช้ ``action=menu`` เพราะเป็นหัวข้อเดียวที่ตอบได้โดยไม่ต้องมี DB
    """
    recorder = Recorder((200, {}))
    monkeypatch.setattr(main, "_http", recorder.client())

    with caplog.at_level(logging.INFO, logger="app.main"):
        await main.process_event(postback_event("action=menu"), sending_settings())

    assert "by=rich_menu" in caplog.text
    assert "ผ่าน=reply" in caplog.text


# ── build_result: แยกจากการส่งเพื่อให้เทสได้โดยไม่ต้องมี token ──────────────


async def test_build_result_ignores_unsupported_events() -> None:
    for event in [{"type": "join"}, {"type": "unsend"}, {}]:
        assert await main.build_result(event) is None


async def test_build_result_handles_missing_fields() -> None:
    """
    payload ที่ field หายต้องไม่ ``KeyError`` — เคยเจอ event ที่ไม่มี
    ``postback.data`` จาก Rich Menu รุ่นเก่า
    """
    result = await main.build_result({"type": "postback"})
    assert result is not None and result.answered_by == "fallback"

    result = await main.build_result({"type": "message", "message": {"type": "text"}})
    assert result is not None and result.answered_by == "fallback"


async def test_build_result_passes_db_to_router() -> None:
    """
    ``db`` ต้องส่งต่อไปถึง router ไม่งั้นชั้นที่ 1 จะตอบว่า "ไม่มีข้อมูล"
    ทั้งที่ต่อฐานข้อมูลได้แล้ว
    """
    db = FakeDatabase({"GROUP BY category": [{"category": "loan", "total": 12}]})

    result = await main.build_result(postback_event("action=documents"), db)

    assert result is not None and result.answered_by == "rich_menu"
    assert db.count == 1


async def test_process_event_reads_db_from_module_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    ``process_event`` รันใน background task ซึ่งไม่ผ่าน dependency injection
    → ต้องหยิบ pool จาก ``get_db()`` เอง
    """
    recorder = Recorder((200, {}))
    db = FakeDatabase({"GROUP BY category": [{"category": "loan", "total": 12}]})
    monkeypatch.setattr(main, "_http", recorder.client())
    monkeypatch.setattr(main, "_db", db)

    await main.process_event(postback_event("action=documents"), sending_settings())

    assert db.count == 1, "ต้องใช้ฐานข้อมูลที่เปิดไว้ตอน startup"
    assert recorder.paths() == [REPLY_PATH]
