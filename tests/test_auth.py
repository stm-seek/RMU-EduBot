"""
เทสการยืนยันตัวตนจาก LIFF + การ hash user id

สองเรื่องที่ห้ามพลาดในไฟล์นี้:

1. **ห้ามเชื่อ ``userId`` จาก client** — ต้อง POST
   ``https://api.line.me/oauth2/v2.1/verify`` แบบ form-encoded ด้วย
   ``id_token`` + ``client_id`` แล้วใช้ ``sub`` เท่านั้น
   (LINE เตือนเองในเอกสารว่าอย่าส่งข้อมูลจาก ``liff.getProfile()`` มาเชื่อ)
2. **ห้าม log ตัว ID token** — เป็นข้อมูลอ่อนไหว ใครได้ไปก็สวมรอยได้ 1 ชั่วโมง
"""

from __future__ import annotations

import logging
from urllib.parse import parse_qsl

import pytest

from app.line.auth import (
    VERIFY_URL,
    LiffAuthError,
    hash_user_id,
    verify_hash,
    verify_id_token,
)

from .helpers import (
    TEST_LOGIN_CHANNEL_ID,
    TEST_PEPPER,
    TEST_USER_ID,
    Recorder,
    make_settings,
)

VALID_TOKEN = "eyJhbGciOiJIUzI1NiJ9.dGhpcy1pcy1hLWZha2UtdG9rZW4.signature"


def auth_settings(**overrides):
    """settings ที่ตั้งค่า LIFF ครบ (เทสส่วนใหญ่ต้องการแบบนี้)"""
    return make_settings(
        line_login_channel_id=TEST_LOGIN_CHANNEL_ID,
        user_id_pepper=TEST_PEPPER,
        **overrides,
    )


# ── hash_user_id ────────────────────────────────────────────────────────────


def test_hash_is_deterministic_and_64_hex() -> None:
    """
    ต้อง deterministic เพราะทุก webhook ที่เข้ามาต้อง lookup ผู้ใช้เดิมให้เจอ
    (จึงใช้ pepper จาก env ไม่ใช่ salt สุ่มต่อแถว)
    """
    first = hash_user_id(TEST_USER_ID, TEST_PEPPER)
    second = hash_user_id(TEST_USER_ID, TEST_PEPPER)

    assert first == second
    assert len(first) == 64
    assert set(first) <= set("0123456789abcdef")


def test_hash_changes_with_pepper() -> None:
    """เปลี่ยน pepper แล้ว hash ต้องเปลี่ยน (ห้ามเปลี่ยนหลังขึ้น production)"""
    assert hash_user_id(TEST_USER_ID, TEST_PEPPER) != hash_user_id(
        TEST_USER_ID, "another-pepper-value-of-sufficient-length"
    )


def test_hash_differs_per_user() -> None:
    assert hash_user_id("U1", TEST_PEPPER) != hash_user_id("U2", TEST_PEPPER)


def test_hash_does_not_leak_user_id() -> None:
    """PDPA: ค่าที่เก็บลง DB ต้องไม่มี line_user_id ปนอยู่"""
    assert TEST_USER_ID not in hash_user_id(TEST_USER_ID, TEST_PEPPER)


def test_hash_refuses_empty_pepper() -> None:
    """
    ไม่มี pepper แล้วยัง hash ต่อ = เก็บ hash ที่ brute-force ได้ง่าย
    (line_user_id มีรูปแบบคาดเดาได้) → ต้อง raise ให้เห็นตอน dev
    """
    with pytest.raises(RuntimeError, match="USER_ID_PEPPER"):
        hash_user_id(TEST_USER_ID, "")


def test_verify_hash_matches_only_the_right_user() -> None:
    expected = hash_user_id("U1", TEST_PEPPER)

    assert verify_hash("U1", TEST_PEPPER, expected) is True
    assert verify_hash("U2", TEST_PEPPER, expected) is False


# ── verify_id_token: ทางที่สำเร็จ ───────────────────────────────────────────


async def test_verify_id_token_posts_form_encoded_to_line() -> None:
    """
    ยืนยันสัญญากับ LINE ให้ครบ: URL, content-type และ field ที่ส่ง

    ถ้าส่งเป็น JSON แทน form-encoded LINE จะปฏิเสธ — เทสนี้ล็อกไว้ไม่ให้พลาด
    """
    recorder = Recorder(
        (200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID, "name": "สมชาย"})
    )
    settings = auth_settings()

    async with recorder.client() as http:
        user = await verify_id_token(VALID_TOKEN, settings, http)

    request = recorder.requests[0]
    assert str(request.url) == VERIFY_URL
    assert request.method == "POST"
    assert request.headers["content-type"] == "application/x-www-form-urlencoded"
    assert dict(parse_qsl(recorder.text_body())) == {
        "id_token": VALID_TOKEN,
        "client_id": TEST_LOGIN_CHANNEL_ID,
    }

    assert user.line_user_id == TEST_USER_ID
    assert user.user_hash == hash_user_id(TEST_USER_ID, TEST_PEPPER)
    assert user.display_name == "สมชาย"


async def test_verify_id_token_accepts_response_without_aud() -> None:
    """บาง response ไม่มี ``aud`` — ยอมรับได้ แต่ต้องยังได้ ``sub``"""
    recorder = Recorder((200, {"sub": TEST_USER_ID}))

    async with recorder.client() as http:
        user = await verify_id_token(VALID_TOKEN, auth_settings(), http)

    assert user.line_user_id == TEST_USER_ID
    assert user.display_name is None


# ── verify_id_token: ทางที่ต้องปฏิเสธ ───────────────────────────────────────


async def test_verify_id_token_rejects_token_for_another_channel() -> None:
    """
    ``aud`` ไม่ตรง = token ออกให้แอปอื่น ห้ามรับ ไม่งั้นแอปอื่นสวมรอยผู้ใช้ได้
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": "9999999999"}))

    async with recorder.client() as http:
        with pytest.raises(LiffAuthError, match="aud"):
            await verify_id_token(VALID_TOKEN, auth_settings(), http)


async def test_verify_id_token_rejects_non_200() -> None:
    """
    token ปลอมจริง ๆ LINE ตอบ ``400 {"error":"invalid_request",
    "error_description":"JWS format error"}``
    """
    recorder = Recorder(
        (400, {"error": "invalid_request", "error_description": "JWS format error"})
    )

    async with recorder.client() as http:
        with pytest.raises(LiffAuthError, match="400"):
            await verify_id_token("ปลอม", auth_settings(), http)


async def test_verify_id_token_rejects_response_without_sub() -> None:
    """ไม่มี ``sub`` = ไม่รู้ว่าใคร ห้ามเดาจาก field อื่น"""
    recorder = Recorder((200, {"aud": TEST_LOGIN_CHANNEL_ID, "name": "สมชาย"}))

    async with recorder.client() as http:
        with pytest.raises(LiffAuthError, match="sub"):
            await verify_id_token(VALID_TOKEN, auth_settings(), http)


async def test_verify_id_token_rejects_empty_token_without_calling_line() -> None:
    """ไม่มี token ก็ไม่ต้องเปลือง request ไปถาม LINE"""
    recorder = Recorder((200, {"sub": TEST_USER_ID}))

    async with recorder.client() as http:
        with pytest.raises(LiffAuthError):
            await verify_id_token("", auth_settings(), http)

    assert recorder.count == 0


async def test_verify_id_token_requires_config() -> None:
    """
    config ไม่ครบต้องเป็น ``RuntimeError`` (คนละชนิดกับ ``LiffAuthError``)
    เพราะ endpoint แปลงเป็น 503 "เซิร์ฟเวอร์ยังไม่พร้อม" ไม่ใช่ 401 "คุณไม่มีสิทธิ์"
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID}))

    async with recorder.client() as http:
        with pytest.raises(RuntimeError, match="LINE_LOGIN_CHANNEL_ID"):
            await verify_id_token(
                VALID_TOKEN, make_settings(user_id_pepper=TEST_PEPPER), http
            )

        with pytest.raises(RuntimeError, match="USER_ID_PEPPER"):
            await verify_id_token(
                VALID_TOKEN,
                make_settings(
                    line_login_channel_id=TEST_LOGIN_CHANNEL_ID, user_id_pepper=""
                ),
                http,
            )

    assert recorder.count == 0, "config ไม่ครบต้องไม่ยิง request"


async def test_verify_id_token_never_logs_the_token(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """ID token อยู่ใน log = ใครอ่าน log ได้ก็สวมรอยผู้ใช้ได้ 1 ชั่วโมง"""
    recorder = Recorder((400, {"error": "invalid_request"}))

    with caplog.at_level(logging.DEBUG):
        async with recorder.client() as http:
            with pytest.raises(LiffAuthError):
                await verify_id_token(VALID_TOKEN, auth_settings(), http)

    assert VALID_TOKEN not in caplog.text
