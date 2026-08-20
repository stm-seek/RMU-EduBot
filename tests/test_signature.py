"""
เทส HMAC signature ของ webhook

นี่คือด่านความปลอดภัยชั้นเดียวของ ``/webhook`` — ถ้าพลาด ใครก็ยิง event ปลอม
เข้ามาสั่งให้บอทส่งข้อความได้ จึงเทสละเอียดกว่าส่วนอื่น
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import inspect

from app.line import signature as signature_module
from app.line.signature import compute_signature, verify_signature

SECRET = "test_channel_secret"


def test_compute_matches_line_formula() -> None:
    """ต้องเป็น ``base64(HMAC-SHA256(channel_secret, raw_body))`` เป๊ะ ๆ"""
    body = b'{"events":[{"type":"message"}]}'
    expected = base64.b64encode(
        hmac.new(SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    ).decode("utf-8")

    assert compute_signature(SECRET, body) == expected


def test_verify_accepts_matching_signature() -> None:
    body = b'{"events":[]}'
    assert verify_signature(SECRET, body, compute_signature(SECRET, body)) is True


def test_verify_rejects_tampered_body() -> None:
    """
    กันการดักแก้เนื้อหา — แก้ ``"1"`` เป็น ``"2"`` ก็ต้องไม่ผ่าน
    """
    original = b'{"events":[{"type":"message","id":"1"}]}'
    tampered = b'{"events":[{"type":"message","id":"2"}]}'
    signature = compute_signature(SECRET, original)

    assert verify_signature(SECRET, tampered, signature) is False


def test_verify_rejects_replayed_signature() -> None:
    """replay: เอา signature ที่ถูกต้องของ request เก่ามาใช้กับ body ใหม่"""
    old_body = b'{"events":[{"type":"follow"}]}'
    new_body = b'{"events":[{"type":"message"}]}'

    assert (
        verify_signature(SECRET, new_body, compute_signature(SECRET, old_body)) is False
    )


def test_verify_rejects_wrong_secret() -> None:
    body = b'{"events":[]}'
    assert (
        verify_signature("another_secret", body, compute_signature(SECRET, body))
        is False
    )


def test_verify_rejects_missing_signature_or_secret() -> None:
    """
    ทั้งสองกรณีต้องได้ ``False`` ไม่ใช่ ``True`` และไม่ใช่ exception

    ไม่มี secret แล้วปล่อยผ่าน = เปิดประตูให้ทุกคน (บั๊กคลาสสิกของ webhook)
    """
    body = b'{"events":[]}'
    assert verify_signature(SECRET, body, None) is False
    assert verify_signature(SECRET, body, "") is False
    assert verify_signature("", body, "anything") is False
    assert verify_signature("", body, None) is False


def test_verify_survives_garbage_signature() -> None:
    """
    ค่าขยะจาก probe ต้องได้ ``False`` เงียบ ๆ ห้าม raise

    ถ้า raise จะกลายเป็น HTTP 500 ซึ่งบอกคนยิงว่า input แบบนี้ทำให้เซิร์ฟเวอร์พัง
    """
    body = b'{"events":[]}'
    for junk in ["!!!not-base64!!!", "a", "=" * 44, "../../etc/passwd", "\x00"]:
        assert verify_signature(SECRET, body, junk) is False


def test_handles_thai_and_emoji_body() -> None:
    """
    body จริงเป็น UTF-8 ที่มีทั้งไทยและ emoji — ต้อง sign บนไบต์ดิบ
    ไม่ใช่บน ``str`` ที่ decode แล้ว (ไม่งั้น signature ไม่ตรงกับที่ LINE ส่งมา)
    """
    body = '{"text":"เทอมหน้าควรลงวิชาอะไร 🎓"}'.encode("utf-8")
    assert verify_signature(SECRET, body, compute_signature(SECRET, body)) is True


def test_handles_empty_body() -> None:
    """body ว่างต้องไม่ crash (เจอได้จาก health probe)"""
    assert verify_signature(SECRET, b"", compute_signature(SECRET, b"")) is True


def test_uses_constant_time_comparison() -> None:
    """
    ยืนยันจาก source ว่ายังเทียบด้วย :func:`hmac.compare_digest`

    วัด timing attack ในเทสไม่เสถียร → ตรวจว่าโค้ดยังเรียกฟังก์ชันที่ปลอดภัย
    (ถ้ามีใครเปลี่ยนไปใช้ ``==`` เทสนี้จะจับได้)
    """
    source = inspect.getsource(signature_module.verify_signature)
    assert "compare_digest" in source
