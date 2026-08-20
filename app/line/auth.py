"""
ยืนยันตัวตนผู้ใช้จาก LIFF อย่างปลอดภัย + hash user id ตาม PDPA

**ห้ามเชื่อ ``userId`` ที่ client ส่งมา** — LINE เตือนไว้ในเอกสารเองว่า
*"Don't send the details of the user profile obtained with
liff.getDecodedIDToken() and liff.getProfile() to the server from the LIFF app."*

``liff.getContext().userId`` เป็นแค่ string ในฝั่ง browser ใครก็ปลอมได้
ถ้า backend เชื่อค่านั้น → ยิง ``curl`` ด้วย userId ของคนอื่นก็ดูข้อมูลคนนั้นได้

flow ที่ถูกต้อง (ทดสอบ endpoint จริงแล้ว):

1. LIFF เรียก ``liff.getIDToken()`` แล้วส่ง token มาที่ backend
2. backend POST ``https://api.line.me/oauth2/v2.1/verify``
   แบบ **form-encoded** ด้วย ``id_token`` + ``client_id``
   (ยิงด้วย token ปลอมได้ ``400 {"error":"invalid_request",
   "error_description":"JWS format error"}`` = endpoint ถูกต้อง)
3. ใช้ ``sub`` จาก response เป็น user id ที่เชื่อถือได้

ID token อายุ **1 ชั่วโมง** — สั้นพอที่จะไม่ต้องเก็บไว้ยาว
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass

import httpx

from ..config import Settings

log = logging.getLogger("app.line.auth")

VERIFY_URL = "https://api.line.me/oauth2/v2.1/verify"


@dataclass(frozen=True)
class VerifiedUser:
    """
    ผลจากการ verify ID token — เชื่อถือได้เพราะ LINE ยืนยันแล้ว

    ``line_user_id`` คือค่าดิบ ใช้เฉพาะตอนเรียก Messaging API
    (push/loading ต้องใช้ค่าดิบ) — **ห้ามเก็บลง DB** ให้เก็บ ``user_hash``
    """

    line_user_id: str
    user_hash: str
    display_name: str | None = None
    picture_url: str | None = None
    email: str | None = None


class LiffAuthError(RuntimeError):
    """verify ID token ไม่ผ่าน"""


def hash_user_id(line_user_id: str, pepper: str) -> str:
    """
    hash user id ด้วย SHA-256 + pepper ก่อนเก็บลง DB (data minimization)

    ใช้ pepper ที่เก็บใน env (ไม่ใช่ salt ต่อแถว) เพราะต้อง **lookup ได้**
    จาก user id ที่ LINE ส่งมาในทุก webhook — ถ้าใช้ salt สุ่มต่อแถวจะหาไม่เจอ

    ผลลัพธ์ deterministic → ผู้ใช้เดิมได้ hash เดิมเสมอ:

    >>> a = hash_user_id('U1234567890', 'pepper-value-at-least-32-chars-long!')
    >>> b = hash_user_id('U1234567890', 'pepper-value-at-least-32-chars-long!')
    >>> a == b
    True
    >>> len(a)
    64

    เปลี่ยน pepper แล้ว hash เปลี่ยน (ห้ามเปลี่ยนหลัง production):

    >>> c = hash_user_id('U1234567890', 'different-pepper-value-32-chars-!!')
    >>> a == c
    False
    """
    if not pepper:
        raise RuntimeError(
            "ยังไม่ได้ตั้ง USER_ID_PEPPER — ห้ามเก็บ line_user_id แบบไม่ hash"
        )
    return hashlib.sha256(f"{line_user_id}{pepper}".encode("utf-8")).hexdigest()


def verify_hash(line_user_id: str, pepper: str, expected_hash: str) -> bool:
    """
    เทียบ hash แบบ constant-time

    >>> pepper = 'pepper-value-at-least-32-chars-long!'
    >>> h = hash_user_id('U1', pepper)
    >>> verify_hash('U1', pepper, h)
    True
    >>> verify_hash('U2', pepper, h)
    False
    """
    return hmac.compare_digest(hash_user_id(line_user_id, pepper), expected_hash)


async def verify_id_token(
    id_token: str, settings: Settings, http: httpx.AsyncClient
) -> VerifiedUser:
    """
    verify LIFF ID token กับ LINE แล้วคืนข้อมูลผู้ใช้ที่เชื่อถือได้

    ``client_id`` ต้องเป็น **LINE Login channel ID** ที่ LIFF app สังกัดอยู่
    ไม่ใช่ Messaging API channel ID — ถ้าใส่ผิด LINE จะปฏิเสธเพราะ ``aud``
    ไม่ตรง
    """
    settings.require("line_login_channel_id", "user_id_pepper")

    if not id_token:
        raise LiffAuthError("ไม่ได้ส่ง id_token มา")

    response = await http.post(
        VERIFY_URL,
        data={"id_token": id_token, "client_id": settings.line_login_channel_id},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        # ไม่ log ตัว token — เป็นข้อมูลอ่อนไหว
        log.warning("verify ID token ไม่ผ่าน: %s %s", response.status_code, response.text[:200])
        raise LiffAuthError(f"ID token ไม่ถูกต้อง (HTTP {response.status_code})")

    payload = response.json()
    subject = payload.get("sub")
    if not subject:
        raise LiffAuthError("response ไม่มี field 'sub'")

    # ตรวจ aud อีกชั้น กัน token ที่ออกให้ channel อื่น
    audience = payload.get("aud")
    if audience and audience != settings.line_login_channel_id:
        raise LiffAuthError(
            f"aud ไม่ตรงกับ channel นี้ (ได้ {audience!r})"
        )

    return VerifiedUser(
        line_user_id=subject,
        user_hash=hash_user_id(subject, settings.user_id_pepper),
        display_name=payload.get("name"),
        picture_url=payload.get("picture"),
        email=payload.get("email"),
    )
