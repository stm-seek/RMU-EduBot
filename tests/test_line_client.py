"""
เทส LINE Messaging API client

โจทย์หลักที่ client ตัวนี้ต้องแก้:

* **reply token ใช้ได้ครั้งเดียวและอายุสั้น** → reply ล้มเหลวต้อง fallback ไป push
  ไม่ใช่ปล่อยให้ user ไม่ได้คำตอบ
* **push กินโควตาฟรีรายเดือน ส่วน reply ไม่กิน** → ต้องลอง reply ก่อนเสมอ
* ``show_loading`` เป็น UX เสริม → ล้มเหลวได้แต่ห้ามทำให้คำตอบหลักหาย
"""

from __future__ import annotations

import pytest

from app.line.client import (
    API_BASE,
    LineApiError,
    LineClient,
    normalize_loading_seconds,
)

from .helpers import (
    TEST_ACCESS_TOKEN,
    TEST_REPLY_TOKEN,
    TEST_USER_ID,
    Recorder,
    make_settings,
)

MESSAGES = [{"type": "text", "text": "สวัสดีครับ"}]


def token_settings():
    return make_settings(line_channel_access_token=TEST_ACCESS_TOKEN)


# ── normalize_loading_seconds ───────────────────────────────────────────────


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        (-100, 5),  # ค่าติดลบ → ขั้นต่ำ
        (0, 5),
        (1, 5),
        (5, 5),
        (9, 5),  # ปัดลงให้หารด้วย 5 ลงตัว
        (12, 10),
        (20, 20),
        (59, 55),
        (60, 60),
        (61, 60),  # เกินเพดาน → 60
        (999, 60),
    ],
)
def test_normalize_loading_seconds(given: int, expected: int) -> None:
    """
    LINE บังคับ 5-60 วินาที และหารด้วย 5 ลงตัว — ส่งค่านอกช่วงจะได้ 400
    """
    assert normalize_loading_seconds(given) == expected


def test_normalize_loading_seconds_always_valid() -> None:
    """invariant: ผลลัพธ์ต้องผ่านเงื่อนไขของ LINE ทุกค่า input"""
    for seconds in range(-20, 200):
        result = normalize_loading_seconds(seconds)
        assert 5 <= result <= 60
        assert result % 5 == 0


# ── การสร้าง client ─────────────────────────────────────────────────────────


async def test_client_requires_access_token() -> None:
    """
    ยังไม่ตั้ง token ต้อง ``RuntimeError`` ที่อ่านรู้เรื่อง และ **ไม่ยิง request**

    (``process_event`` จับ error นี้แล้ว log ว่าคิดคำตอบไว้แล้วแต่ส่งไม่ได้
    — ดู :mod:`tests.test_webhook`)
    """
    recorder = Recorder((200, {}))

    async with recorder.client() as http:
        with pytest.raises(RuntimeError, match="LINE_CHANNEL_ACCESS_TOKEN"):
            LineClient(make_settings(), http)

    assert recorder.count == 0


async def test_client_sends_bearer_token() -> None:
    recorder = Recorder((200, {}))

    async with recorder.client() as http:
        await LineClient(token_settings(), http).reply(TEST_REPLY_TOKEN, MESSAGES)

    assert recorder.requests[0].headers["authorization"] == f"Bearer {TEST_ACCESS_TOKEN}"
    assert recorder.requests[0].headers["content-type"] == "application/json"


# ── reply / push ────────────────────────────────────────────────────────────


async def test_reply_payload_shape() -> None:
    recorder = Recorder((200, {}))

    async with recorder.client() as http:
        await LineClient(token_settings(), http).reply(TEST_REPLY_TOKEN, MESSAGES)

    assert str(recorder.requests[0].url) == f"{API_BASE}/message/reply"
    assert recorder.json_body() == {
        "replyToken": TEST_REPLY_TOKEN,
        "messages": MESSAGES,
    }


async def test_push_payload_shape() -> None:
    recorder = Recorder((200, {}))

    async with recorder.client() as http:
        await LineClient(token_settings(), http).push(TEST_USER_ID, MESSAGES)

    assert str(recorder.requests[0].url) == f"{API_BASE}/message/push"
    assert recorder.json_body() == {"to": TEST_USER_ID, "messages": MESSAGES}


async def test_thai_text_is_not_escaped_away() -> None:
    """
    ข้อความไทยต้องถึง LINE ครบ — เทสนี้จับกรณี encoding เพี้ยน
    (httpx ส่ง JSON เป็น UTF-8 escape ก็ได้ แต่ decode กลับต้องได้ข้อความเดิม)
    """
    recorder = Recorder((200, {}))
    thai = [{"type": "text", "text": "ลงทะเบียนเรียนภาคเรียนที่ 2/2568"}]

    async with recorder.client() as http:
        await LineClient(token_settings(), http).push(TEST_USER_ID, thai)

    assert recorder.json_body()["messages"] == thai


async def test_reply_raises_line_api_error_with_details() -> None:
    """เก็บ status + body ไว้ให้ debug ได้ (LINE บอกเหตุผลใน body)"""
    recorder = Recorder((400, {"message": "Invalid reply token"}))

    async with recorder.client() as http:
        with pytest.raises(LineApiError) as info:
            await LineClient(token_settings(), http).reply(TEST_REPLY_TOKEN, MESSAGES)

    assert info.value.status_code == 400
    assert "Invalid reply token" in info.value.body


# ── reply_or_push ───────────────────────────────────────────────────────────


async def test_reply_or_push_prefers_reply() -> None:
    """reply ไม่กินโควตา → สำเร็จแล้วต้องไม่ยิง push ตามอีก"""
    recorder = Recorder((200, {}))

    async with recorder.client() as http:
        channel = await LineClient(token_settings(), http).reply_or_push(
            TEST_REPLY_TOKEN, TEST_USER_ID, MESSAGES
        )

    assert channel == "reply"
    assert recorder.paths() == ["/v2/bot/message/reply"]


async def test_reply_or_push_falls_back_to_push_on_expired_token() -> None:
    """
    เคสที่เกิดจริงที่สุด: LLM คิดนานเกิน reply token หมดอายุ
    → ต้อง push ให้ user ได้คำตอบ ไม่ใช่เงียบหาย
    """
    recorder = Recorder(
        (400, {"message": "Invalid reply token"}),
        (200, {}),
    )

    async with recorder.client() as http:
        channel = await LineClient(token_settings(), http).reply_or_push(
            TEST_REPLY_TOKEN, TEST_USER_ID, MESSAGES
        )

    assert channel == "push"
    assert recorder.paths() == ["/v2/bot/message/reply", "/v2/bot/message/push"]
    assert recorder.json_body(1) == {"to": TEST_USER_ID, "messages": MESSAGES}


async def test_reply_or_push_raises_when_push_also_fails() -> None:
    """
    push พังด้วย (เช่นโควตาหมด) → ต้องโยน error ให้ caller log
    ไม่ใช่กลืนแล้วรายงานว่าส่งสำเร็จ
    """
    recorder = Recorder(
        (400, {"message": "Invalid reply token"}),
        (429, {"message": "You have reached your monthly limit."}),
    )

    async with recorder.client() as http:
        with pytest.raises(LineApiError) as info:
            await LineClient(token_settings(), http).reply_or_push(
                TEST_REPLY_TOKEN, TEST_USER_ID, MESSAGES
            )

    assert info.value.status_code == 429


# ── show_loading ────────────────────────────────────────────────────────────


async def test_show_loading_payload_is_normalized() -> None:
    recorder = Recorder((200, {}))

    async with recorder.client() as http:
        await LineClient(token_settings(), http).show_loading(TEST_USER_ID, 12)

    assert recorder.paths() == ["/v2/bot/chat/loading/start"]
    assert recorder.json_body() == {"chatId": TEST_USER_ID, "loadingSeconds": 10}


async def test_show_loading_swallows_errors() -> None:
    """
    เป็นแค่ UX เสริม — ถ้าพังต้องไม่ทำให้ flow การตอบคำถามล้ม
    (เช่นแชทกลุ่มที่ LINE ไม่รองรับ loading animation)
    """
    recorder = Recorder((400, {"message": "The chat is not supported"}))

    async with recorder.client() as http:
        await LineClient(token_settings(), http).show_loading(TEST_USER_ID)

    assert recorder.count == 1


# ── Rich Menu เฉพาะผู้ใช้ (สลับใบตามโหมดปรึกษา) ─────────────────────────────

CONSULT_MENU_ID = "richmenu-testconsult000000000000000000"


async def test_link_rich_menu_posts_empty_body() -> None:
    """
    LINE รับ ``POST /user/{userId}/richmenu/{richMenuId}`` **ตัวเปล่า** —
    ส่ง json ไปด้วยก็ 200 เหมือนกัน แต่สัญญาของ API คือไม่มี body
    """
    recorder = Recorder((200, {}))

    async with recorder.client() as http:
        await LineClient(token_settings(), http).link_rich_menu(
            TEST_USER_ID, CONSULT_MENU_ID
        )

    request = recorder.requests[0]
    assert request.method == "POST"
    assert request.url.path == f"/v2/bot/user/{TEST_USER_ID}/richmenu/{CONSULT_MENU_ID}"
    assert request.content == b"", "link rich menu ต้องไม่ส่ง body"
    assert request.headers["authorization"] == f"Bearer {TEST_ACCESS_TOKEN}"


async def test_unlink_rich_menu_uses_delete() -> None:
    recorder = Recorder((200, {}))

    async with recorder.client() as http:
        await LineClient(token_settings(), http).unlink_rich_menu(TEST_USER_ID)

    request = recorder.requests[0]
    assert request.method == "DELETE"
    assert request.url.path == f"/v2/bot/user/{TEST_USER_ID}/richmenu"


async def test_link_rich_menu_raises_on_unknown_menu() -> None:
    """
    id ผิด (เช่นยังไม่ตั้ง .env หลังลบเมนู) → ต้องโยนให้ ``app/main.py``
    จับแล้วแค่ log ไม่ใช่พังเงียบ — ผู้ใช้ยังเห็นเมนูเดิมซึ่งยอมรับได้
    """
    recorder = Recorder((404, {"message": "The rich menu does not exist."}))

    async with recorder.client() as http:
        with pytest.raises(LineApiError) as info:
            await LineClient(token_settings(), http).link_rich_menu(
                TEST_USER_ID, CONSULT_MENU_ID
            )

    assert info.value.status_code == 404


# ── get_bot_info ────────────────────────────────────────────────────────────


async def test_get_bot_info_uses_get_and_returns_json() -> None:
    """ใช้ตรวจว่า access token ใช้ได้จริงตอน health check"""
    recorder = Recorder((200, {"userId": "Ubot", "displayName": "ผู้ช่วยวิชาการ"}))

    async with recorder.client() as http:
        info = await LineClient(token_settings(), http).get_bot_info()

    assert recorder.requests[0].method == "GET"
    assert str(recorder.requests[0].url) == f"{API_BASE}/info"
    assert info["displayName"] == "ผู้ช่วยวิชาการ"


async def test_get_bot_info_raises_on_invalid_token() -> None:
    recorder = Recorder((401, {"message": "Authentication failed"}))

    async with recorder.client() as http:
        with pytest.raises(LineApiError) as info:
            await LineClient(token_settings(), http).get_bot_info()

    assert info.value.status_code == 401
