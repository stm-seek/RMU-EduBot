"""ตรวจ signature ของ webhook จาก LINE Platform

LINE เซ็น request body ด้วย HMAC-SHA256 โดยใช้ *channel secret* เป็น key
แล้วส่งค่า base64 มาใน header ``X-Line-Signature``

**ถ้าไม่ตรวจ signature ใครก็ยิง webhook ปลอมเข้ามาได้** ทำให้บอทส่งข้อความ
ตามที่ผู้ไม่ประสงค์ดีสั่ง หรือทำให้ log เพี้ยน — ถือเป็นช่องโหว่ร้ายแรง
"""

from __future__ import annotations

import base64
import hashlib
import hmac


def compute_signature(channel_secret: str, body: bytes) -> str:
    """
    คำนวณค่า signature ที่ควรได้ (ใช้ทั้งตอน verify และตอนเขียนเทส)

    >>> compute_signature('secret', b'{"events":[]}')
    'pkK1lVPJPiJ+wPLziRD79xIxohl8AImYM8AEeM7IbzQ='
    """
    digest = hmac.new(
        channel_secret.encode("utf-8"), body, hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def verify_signature(channel_secret: str, body: bytes, signature: str | None) -> bool:
    """
    ตรวจว่า signature ตรงกับ body หรือไม่

    ใช้ :func:`hmac.compare_digest` เพื่อกัน timing attack — ห้ามใช้ ``==``

    >>> secret, body = 'secret', b'{"events":[]}'
    >>> verify_signature(secret, body, compute_signature(secret, body))
    True
    >>> verify_signature(secret, body, 'wrong-signature')
    False
    >>> verify_signature(secret, body, None)
    False
    >>> verify_signature('', body, 'anything')     # ไม่มี secret = ไม่ผ่าน
    False
    """
    if not signature or not channel_secret:
        return False
    expected = compute_signature(channel_secret, body)
    return hmac.compare_digest(expected, signature)
