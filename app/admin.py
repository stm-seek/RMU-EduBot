"""
หน้า admin — API ของ ``web/admin/index.html``

**ทำไมต้องมี auth**

เซิร์ฟเวอร์ตัวนี้เปิดออกอินเทอร์เน็ตผ่าน cloudflared (URL เดาไม่ได้ก็จริง แต่
"เดาไม่ได้" ไม่ใช่การป้องกัน) และหน้านี้ **แก้คำตอบที่บอทเอาไปตอบนักศึกษาได้
ตรง ๆ** ถ้าเปิดโล่ง ใครเจอ URL ก็เขียนข้อมูลเท็จลงคลังคำตอบของคณะได้

**ทำไมเปลี่ยนจาก LINE Login มาเป็น username + password ของระบบเราเอง**

เดิมหน้านี้ตรวจ LIFF ID token แล้วเทียบ ``line_user_hash`` กับรายชื่อใน
``ADMIN_USER_HASHES`` (.env) — ใช้ได้ แต่การเพิ่ม/ถอนคนต้องแก้ไฟล์บนเครื่องจริง
แล้วรีสตาร์ตเซิร์ฟเวอร์ และคนที่จะเป็น admin ต้องไปขุด hash ของตัวเองจาก log
ก่อน ซึ่งเป็นขั้นตอนที่ส่งต่อให้เจ้าหน้าที่ทำเองไม่ได้จริง

ระบบใหม่: บัญชีอยู่ในตาราง ``admin_accounts`` (``db/migrations/008_admin_accounts.sql``)
สร้าง/รีเซ็ตด้วย ``python scripts/admin_user.py --username <ชื่อ>`` ไม่ต้องรีสตาร์ต

ฝั่ง **นักศึกษา** (``/liff``, ``/api/liff/*``) ยังใช้ LINE Login เหมือนเดิมและ
ต้องใช้ต่อ — ที่เปลี่ยนคือหน้า admin เท่านั้น

**ข้อตกลงที่ห้ามแก้**

* รหัสผ่านเก็บเป็น **scrypt** (``hashlib`` ของ stdlib) salt สุ่มต่อแถว และฝัง
  พารามิเตอร์ไว้ในสตริง — ไม่มีที่ไหนในระบบเก็บรหัสผ่านเป็น plaintext
* เทียบค่าลับด้วย :func:`hmac.compare_digest` เท่านั้น (constant-time)
* **ห้าม log รหัสผ่าน / password_hash / cookie token** ไม่ว่ากรณีใด
* ข้อความปฏิเสธของ ``/login`` เป็น**ข้อความเดียวกันเป๊ะ**ทั้งกรณีไม่มีบัญชีชื่อ
  นั้นและกรณีรหัสผิด และกรณีไม่มีบัญชีก็ยัง **hash หลอกหนึ่งครั้ง** ให้เวลาตอบ
  ใกล้เคียงกัน ไม่งั้นหน้านี้กลายเป็นเครื่องมือไล่ตรวจว่าใครเป็น admin

**fail closed:** ไม่มีบัญชีที่ ``is_active`` เลย = ไม่มีใครเข้าได้ (403) และ
``ADMIN_SESSION_SECRET`` ว่าง = ล็อกอินไม่ได้เลย (503) ไม่ใช่ปล่อยผ่าน
ข้อความที่ส่งออกไป **ไม่บอก**ว่าระบบยังตั้งไม่เสร็จ ส่วน log ฝั่งเราบอกตรง ๆ
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import secrets
import time
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from . import admin_repo
from . import ai_chat
from .config import Settings, get_settings
from .db import SupportsExecute, SupportsQuery

log = logging.getLogger("app.admin")

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── ยูทิลิตี้ร่วม ─────────────────────────────────────────────────────────────
#
# ``get_db`` อยู่ใน :mod:`app.main` ซึ่ง import ไฟล์นี้ → import ตรง ๆ จะวน
# ต้อง import **ข้างในฟังก์ชัน** เท่านั้น (จุดนี้พังตอนสตาร์ต ไม่ใช่ตอนรัน
# จึงเห็นเร็ว แต่ก็สับสนพอที่จะเขียนเตือนไว้)


def _http_error(status: int, detail: str):
    from fastapi import HTTPException

    return HTTPException(status_code=status, detail=detail)


def _writable_db() -> SupportsExecute:
    from .main import get_db

    db = get_db()
    if db is None or not isinstance(db, SupportsExecute):
        raise _http_error(503, "ฐานข้อมูลยังไม่พร้อม — ลองอีกครั้งในอีกสักครู่")
    return db


def _readable_db() -> SupportsQuery:
    from .main import get_db

    db = get_db()
    if db is None:
        raise _http_error(503, "ฐานข้อมูลยังไม่พร้อม — ลองอีกครั้งในอีกสักครู่")
    return db


# ── รหัสผ่าน: scrypt จาก stdlib ──────────────────────────────────────────────
#
# ไม่มี bcrypt/passlib ในโปรเจกต์นี้และไม่ต้องเพิ่ม — ``hashlib.scrypt`` เป็น KDF
# แบบ memory-hard ที่อยู่ใน stdlib ตั้งแต่ Python 3.6 (พึ่ง OpenSSL ที่ติดมาแล้ว)
#
# ค่าพารามิเตอร์ n=16384, r=8, p=1 → ใช้หน่วยความจำ ~16 MB และเวลา ~46 ms ต่อครั้ง
# (วัดบนเครื่องที่พัฒนา 29 ส.ค. 2026) หนักพอให้การไล่เดาแบบออฟไลน์แพงจริง และ
# เบาพอที่การล็อกอินไม่หนืด — ต่ำกว่าเพดาน maxmem ดีฟอลต์ของ OpenSSL (32 MB)
#
# **ค่าพวกนี้ฝังไปในสตริงที่เก็บ** ตอน verify อ่านจากสตริง ไม่ใช่จากค่าคงที่ในไฟล์นี้
# → ขึ้นค่า n ในอนาคตได้โดยรหัสผ่านเก่ายังใช้ได้ (ดูเหตุผลเต็มใน 008_admin_accounts.sql)

SCRYPT_N = 16_384
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32
SCRYPT_SALT_BYTES = 16

# ความยาวรหัสผ่านขั้นต่ำ — ใช้ทั้งที่นี่และใน ``scripts/admin_user.py``
MIN_PASSWORD_LENGTH = 12
# เพดานความยาวที่ยอมคำนวณ — ไม่ใช่เรื่องความแข็งของรหัส แต่กันคนยิง body ยาว
# 1 MB มาให้เซิร์ฟเวอร์ scrypt ทีละ 16 MB ซ้ำ ๆ (DoS ราคาถูก)
MAX_PASSWORD_LENGTH = 1_024


def _b64(raw: bytes) -> str:
    """base64 แบบตัด ``=`` ท้าย — ให้ ``$``/``.`` เป็นตัวคั่นเดียวในสตริงที่เก็บ"""
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def hash_password(password: str) -> str:
    """
    รหัสผ่าน → สตริง ``scrypt$n$r$p$salt$hash`` (salt สุ่มใหม่ทุกครั้ง)

    >>> hash_password('a-long-enough-password').split('$')[:4]
    ['scrypt', '16384', '8', '1']

    รหัสเดียวกัน hash สองครั้งต้องได้ค่า**ไม่เหมือนกัน** — ถ้าเหมือนกันหมายถึง
    salt ไม่ได้สุ่มจริง แล้วตารางสำเร็จรูป (rainbow table) ใช้ได้ทันที:

    >>> hash_password('a-long-enough-password') == hash_password('a-long-enough-password')
    False
    """
    salt = secrets.token_bytes(SCRYPT_SALT_BYTES)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${_b64(salt)}${_b64(derived)}"


def verify_password(password: str, stored: str) -> bool:
    """
    เทียบรหัสผ่านกับสตริงที่เก็บไว้ — เทียบผลลัพธ์แบบ constant-time

    >>> stored = hash_password('a-long-enough-password')
    >>> verify_password('a-long-enough-password', stored)
    True
    >>> verify_password('wrong-password-entirely', stored)
    False

    สตริงที่ parse ไม่ได้ = ไม่ผ่าน ไม่ใช่ระเบิด (แถวใน DB ถูกแก้มือได้ และ
    exception ตรงนี้จะกลายเป็น 500 ที่บอกคนนอกว่าเราเก็บอะไรไว้รูปแบบไหน):

    >>> verify_password('x', 'ไม่ใช่รูปแบบที่รู้จัก')
    False
    >>> verify_password('x', '')
    False
    """
    if len(password) > MAX_PASSWORD_LENGTH:
        return False
    try:
        scheme, n_text, r_text, p_text, salt_text, hash_text = stored.split("$")
        if scheme != "scrypt":
            return False
        expected = _unb64(hash_text)
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=_unb64(salt_text),
            n=int(n_text),
            r=int(r_text),
            p=int(p_text),
            dklen=len(expected),
        )
    except Exception:
        # ห้าม log ค่า ``stored`` ตรงนี้ — มันคือ password hash
        return False
    return hmac.compare_digest(derived, expected)


# hash หลอกที่เอาไว้ "เผาเวลา" เมื่อ **ไม่มี** บัญชีชื่อที่ยิงเข้ามา รหัสผ่านของมัน
# เป็นค่าสุ่มตอน import — ไม่มีใครรู้และไม่ต้องรู้ (verify ไม่ผ่านเสมอ)
#
# ถ้าไม่ทำขั้นนี้ การตอบกรณี "ไม่มี username นี้" จะเร็วกว่ากรณี "รหัสผิด" ราว
# 46 ms ซึ่งจับเวลาแยกได้ง่ายจากภายนอก แล้วหน้านี้ก็กลายเป็นเครื่องมือไล่ตรวจว่า
# ใครเป็น admin ทั้งที่ข้อความตอบกลับเหมือนกันเป๊ะ
_DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


# ── เซสชัน: cookie ที่เซ็นด้วย HMAC (ไม่มีตารางเซสชัน) ────────────────────────
#
# token = ``<username_b64>.<เวลาหมดอายุ>.<hmac_b64>`` เซ็นด้วย ``ADMIN_SESSION_SECRET``
# ตรวจ **ทั้งลายเซ็นและเวลาหมดอายุ** ทุก request (ลายเซ็นถูกแต่หมดอายุ = ปฏิเสธ)
#
# ทำไมเป็น cookie ไม่ใช่ token ที่ JS ถือไว้: ``HttpOnly`` ทำให้ JS อ่านไม่ได้ →
# XSS ในหน้านี้ขโมย token ไปใช้ที่อื่นไม่ได้ ซึ่ง localStorage ทำแบบนั้นไม่ได้
#
# **ข้อจำกัดที่ต้องรู้: ยกเลิกกลางทางไม่ได้** — token เป็น stateless ไม่มีตาราง
# เซสชันให้ลบ ปิดบัญชีด้วย ``scripts/admin_user.py --deactivate`` แล้ว cookie ใบที่
# ออกไปก่อนหน้านั้น **ยังใช้ได้จนหมดอายุ** (อย่างมาก 8 ชั่วโมงตาม
# ``ADMIN_SESSION_MAX_AGE_SECONDS``) ทางเดียวที่ตัดทันทีคือเปลี่ยน
# ``ADMIN_SESSION_SECRET`` แล้วรีสตาร์ต ซึ่ง **เตะทุกคนออกพร้อมกัน** ไม่ใช่คนเดียว
#
# ยอมข้อจำกัดนี้เพราะ admin มีไม่กี่คนและอายุ token สั้น ส่วนตารางเซสชันแลกมาด้วย
# การ query DB ทุก request และยังต้องมีงานเก็บกวาดแถวหมดอายุ

SESSION_COOKIE = "admin_session"


def _sign(body: str, secret: str) -> str:
    return _b64(
        hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    )


def make_session_token(username: str, secret: str, max_age_seconds: int) -> str:
    """
    ออก token สำหรับ cookie — ผูกกับ ``username`` และเวลาหมดอายุ

    >>> token = make_session_token('somchai', 'กุญแจลับ', 60)
    >>> read_session_token(token, 'กุญแจลับ')
    'somchai'

    กุญแจไม่ตรง = อ่านไม่ออก (นี่คือสิ่งที่เกิดขึ้นเมื่อเปลี่ยน secret แล้วรีสตาร์ต):

    >>> read_session_token(token, 'กุญแจอื่น') is None
    True
    """
    expires_at = int(time.time()) + max_age_seconds
    body = f"{_b64(username.encode('utf-8'))}.{expires_at}"
    return f"{body}.{_sign(body, secret)}"


def read_session_token(token: str, secret: str) -> str | None:
    """
    token → username ถ้าลายเซ็นถูก **และ** ยังไม่หมดอายุ ไม่งั้นคืน ``None``

    หมดอายุแล้วต้องปฏิเสธแม้ลายเซ็นถูก ไม่งั้นอายุ cookie ไม่มีความหมายเลย
    (ผู้ใช้ลบ ``Max-Age`` ของ cookie ฝั่งตัวเองได้ ตัวที่บังคับจริงคือค่าในนี้):

    >>> stale = make_session_token('somchai', 'กุญแจลับ', -1)
    >>> read_session_token(stale, 'กุญแจลับ') is None
    True

    ค่าที่ไม่ใช่รูปแบบของเราเลย = ``None`` ไม่ใช่ระเบิด (cookie แก้มือได้ทุกไบต์):

    >>> read_session_token('ขยะ', 'กุญแจลับ') is None
    True
    >>> read_session_token('', 'กุญแจลับ') is None
    True
    """
    try:
        username_b64, expires_text, signature = token.split(".")
        body = f"{username_b64}.{expires_text}"
        # เทียบลายเซ็นก่อนเชื่อค่าอะไรข้างในเลย และเทียบแบบ constant-time
        if not hmac.compare_digest(signature, _sign(body, secret)):
            return None
        if int(expires_text) <= int(time.time()):
            return None
        return _unb64(username_b64).decode("utf-8")
    except Exception:
        return None


# ── กันไล่เดารหัสผ่าน (หน้านี้เปิดออกอินเทอร์เน็ต) ─────────────────────────────
#
# นับความล้มเหลวต่อคู่ ``(username, ip)`` ครบ 5 ครั้ง → ล็อก 15 นาที และระหว่างล็อก
# **แม้ใส่รหัสถูกก็ไม่ให้เข้า** ไม่งั้นการล็อกไม่ได้ชะลออะไรเลยสำหรับคนที่เดาถูกใน
# ครั้งที่ 6 ล็อกอินสำเร็จ = ล้างตัวนับของคู่นั้น
#
# **ตัวนับอยู่ใน memory ของ process** → หายเมื่อรีสตาร์ตเซิร์ฟเวอร์ (คนที่ถูกล็อก
# อยู่จะหลุดล็อกทันที) และถ้าวันหนึ่งรัน uvicorn หลาย worker จะนับแยกกันคนละ worker
# ทำให้เพดานจริงกลายเป็น 5 × จำนวน worker — ตอนนี้รัน worker เดียวจึงยอมรับได้
# ถ้าจะเพิ่ม worker ต้องย้ายตัวนับไปที่ที่ใช้ร่วมกัน (ตารางใน DB หรือ Redis) ก่อน
#
# เรื่อง ip: หลัง cloudflared ทุก request มาจาก 127.0.0.1 ตัวนับจึงกลายเป็นการนับ
# ต่อ username เกือบสนิท ซึ่งยัง**กันการเดารหัสของบัญชีหนึ่งได้** (สิ่งที่ทำไม่ได้คือ
# แยกคนร้ายออกจากเจ้าตัวที่พิมพ์รหัสผิดเองในเวลาเดียวกัน — เจ้าตัวจะถูกล็อกด้วย)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60

_failed_logins: dict[tuple[str, str], tuple[int, float]] = {}


def _lock_key(username: str, client_ip: str) -> tuple[str, str]:
    return (username.strip().lower(), client_ip)


def locked_seconds_left(username: str, client_ip: str) -> int:
    """
    เหลืออีกกี่วินาทีที่ยังถูกล็อก — ``0`` = ไม่ได้ถูกล็อก

    >>> reset_failed_logins()
    >>> locked_seconds_left('somchai', '1.1.1.1')
    0
    >>> for _ in range(MAX_FAILED_ATTEMPTS):
    ...     _ = record_failed_login('somchai', '1.1.1.1')
    >>> 0 < locked_seconds_left('somchai', '1.1.1.1') <= LOCKOUT_SECONDS
    True

    คนละ ip ไม่ติดล็อกของกันและกัน (บัญชีเดียวกันแต่คนละที่ — คนที่ถูกคนอื่นเดา
    รหัสอยู่ต้องยังทำงานได้จากเครื่องตัวเอง):

    >>> locked_seconds_left('somchai', '2.2.2.2')
    0
    >>> reset_failed_logins()
    """
    count, last_failure = _failed_logins.get(_lock_key(username, client_ip), (0, 0.0))
    if count < MAX_FAILED_ATTEMPTS:
        return 0
    left = int(last_failure + LOCKOUT_SECONDS - time.time())
    return left if left > 0 else 0


def record_failed_login(username: str, client_ip: str) -> int:
    """
    บันทึกความล้มเหลวหนึ่งครั้ง → คืนจำนวนครั้งที่สะสมอยู่

    เงียบไปเกิน ``LOCKOUT_SECONDS`` แล้วเริ่มนับใหม่ ไม่งั้นคนที่พิมพ์ผิดเดือนละ
    ครั้งจะสะสมครบ 5 แล้วถูกล็อกทั้งที่ไม่มีใครกำลังเดาอะไรเลย

    >>> reset_failed_logins()
    >>> record_failed_login('somchai', '1.1.1.1')
    1
    >>> record_failed_login('somchai', '1.1.1.1')
    2
    >>> reset_failed_logins()
    """
    key = _lock_key(username, client_ip)
    now = time.time()
    count, last_failure = _failed_logins.get(key, (0, 0.0))
    if now - last_failure > LOCKOUT_SECONDS:
        count = 0
    count += 1
    _failed_logins[key] = (count, now)
    return count


def clear_failed_logins(username: str, client_ip: str) -> None:
    """ล็อกอินสำเร็จ = ล้างตัวนับของคู่นั้น (ไม่ใช่ของทั้งระบบ)"""
    _failed_logins.pop(_lock_key(username, client_ip), None)


def reset_failed_logins() -> None:
    """ล้างตัวนับทั้งหมด — มีไว้ให้เทส/doctest เริ่มจากสถานะสะอาด"""
    _failed_logins.clear()


# ── ด่านตรวจสิทธิ์ของทุก endpoint ────────────────────────────────────────────

SESSION_EXPIRED_DETAIL = "เซสชันหมดอายุ — กรุณาเข้าสู่ระบบใหม่"
BAD_CREDENTIALS_DETAIL = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
NO_ACCESS_DETAIL = "ยังไม่มีสิทธิ์เข้าหน้านี้"


def _client_ip(request: Request) -> str:
    """
    ip ของคนยิง — ใช้เป็นส่วนหนึ่งของกุญแจนับความล้มเหลวเท่านั้น

    **ไม่ได้ใช้ตัดสินสิทธิ์** จึงไม่ต้องกังวลว่า ``X-Forwarded-For`` ปลอมได้
    (ปลอมได้จริง และผลของการปลอมคือทำให้ตัวนับ*ของตัวเอง*กระจาย — ซึ่งเป็นเหตุผล
    ที่กุญแจผูกกับ username ด้วย ไม่ใช่ ip เพียว ๆ)
    """
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _session_secret(settings: Settings) -> str:
    """
    กุญแจเซ็น cookie — ว่าง = 503 พร้อม**บอกชื่อตัวแปรที่ต้องตั้ง**

    บอกชื่อตัวแปรออกไปได้เพราะมันเป็นชื่อ ไม่ใช่ค่า และคนที่เจอ error นี้คือคนตั้ง
    ระบบที่ต้องรู้ว่าต้องไปเติมอะไร (แนวเดียวกับ ``Settings.require``)
    """
    if not settings.admin_session_secret:
        log.warning(
            "มีคนเรียก API ของหน้า admin แต่ยังไม่ได้ตั้ง ADMIN_SESSION_SECRET "
            "ใน .env — ปฏิเสธทุกคน"
        )
        raise _http_error(
            503,
            "เซิร์ฟเวอร์ยังไม่ได้ตั้ง ADMIN_SESSION_SECRET ใน .env — สร้างค่าด้วย "
            'python -c "import secrets; print(secrets.token_urlsafe(48))" '
            "แล้วรีสตาร์ตเซิร์ฟเวอร์",
        )
    return settings.admin_session_secret


def require_admin(request: Request, settings: Settings) -> str:
    """
    ตรวจ cookie แล้วคืน ``username`` ของคนที่ล็อกอินอยู่

    เป็น **ฟังก์ชันธรรมดา ไม่ใช่ dependency** ด้วยเหตุผลเดียวกับ
    :func:`app.main.verify_or_401`: endpoint พวกนี้ประกาศ body ของตัวเองอยู่แล้ว
    ถ้าตัวตรวจสิทธิ์ประกาศ body ด้วย FastAPI จะบังคับให้ body ซ้อนเป็นสองก้อน

    ไม่มี cookie / cookie ปลอม / cookie หมดอายุ → 401 **ข้อความเดียวกันทั้งสามกรณี**
    เพราะคนใช้ต้องทำเหมือนกันหมด (ล็อกอินใหม่) และการแยกข้อความจะบอกคนที่กำลังลอง
    แก้ cookie ว่าเดามาใกล้แค่ไหน
    """
    secret = _session_secret(settings)
    token = request.cookies.get(SESSION_COOKIE)
    username = read_session_token(token, secret) if token else None
    if not username:
        raise _http_error(401, SESSION_EXPIRED_DETAIL)
    return username


class AdminRequest(BaseModel):
    """
    body พื้นฐานของทุก endpoint — **ว่างเปล่า** ตัวตนมาจาก cookie ไม่ใช่จาก body

    เหลือคลาสนี้ไว้ (ไม่ลบ) เพราะทุกฟอร์มสืบทอดมันอยู่ และถ้าวันหนึ่งต้องมีฟิลด์
    ที่ทุก endpoint ต้องส่ง (เช่น CSRF token) จะได้เติมที่เดียว
    """


SettingsDep = Annotated[Settings, Depends(get_settings)]


# ── endpoints: เข้า/ออกระบบ ──────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """
    ฟอร์มล็อกอิน — ช่องนี้เป็น**ที่เดียว**ในระบบที่รับรหัสผ่านเป็น plaintext

    ``max_length`` ของ ``password`` คือ :data:`MAX_PASSWORD_LENGTH` เพื่อให้คำขอ
    ที่ยาวเกินถูกปฏิเสธที่ชั้น validate ก่อนถึง scrypt (ไม่ใช่หลังจากนั้น)
    ไม่ได้บังคับ ``MIN_PASSWORD_LENGTH`` ที่นี่: ความยาวขั้นต่ำเป็นกฎของตอน
    **ตั้ง** รหัส ถ้าเอามาบังคับตอนล็อกอินด้วย ข้อความ error จะบอกคนเดารหัสว่า
    รหัสจริงยาวเกิน 12 ตัวแน่ ๆ
    """

    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)


def _cookie_is_secure(request: Request) -> bool:
    """
    ควรติดแฟล็ก ``Secure`` ไหม — ติดเมื่อคำขอนี้มาทาง https

    ติดตายไม่ได้: ตอน dev เปิด ``http://127.0.0.1:8001`` เบราว์เซอร์จะ**ทิ้ง**
    cookie ที่มี ``Secure`` ทั้งใบ (ล็อกอินผ่านแต่ request ถัดไป 401 วนไปเรื่อย)
    ตอนใช้จริงผ่าน cloudflared เข้ามาเป็น https จึงได้แฟล็กนี้เอง
    (cloudflared ต่อกับเราด้วย http จึงต้องดู ``X-Forwarded-Proto`` ด้วย)
    """
    forwarded = request.headers.get("x-forwarded-proto", "").split(",")[0].strip()
    return (forwarded or request.url.scheme).lower() == "https"


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    settings: SettingsDep,
) -> dict:
    """
    ตรวจ username + password แล้วออก cookie เซสชัน

    ลำดับของการตรวจในนี้ตั้งใจทั้งหมด:

    1. ``ADMIN_SESSION_SECRET`` ว่าง → 503 (ออก cookie ที่เซ็นด้วยค่าว่างไม่ได้)
    2. ถูกล็อกอยู่ → 429 **ก่อน**แตะ DB และก่อนคำนวณ scrypt — ไม่งั้นการล็อก
       ไม่ได้ลดต้นทุนของการถูกยิงรัว และคนที่เดาถูกในครั้งที่ 6 ก็จะเข้าได้
    3. ไม่มีบัญชี active เลยในระบบ → 403 ข้อความกลาง ๆ + log ฝั่งเราบอกตรง ๆ
    4. เทียบรหัส — ไม่มีบัญชีชื่อนั้นก็ยัง hash หลอกหนึ่งครั้ง (เวลาเท่ากัน)

    ปิดบัญชี (``is_active = false``) แล้วยังเทียบรหัสจริงก่อนปฏิเสธ ด้วยเหตุผล
    เดียวกันเรื่องเวลา และคำตอบที่ได้เหมือนกรณีรหัสผิดเป๊ะ — คนถูกถอนสิทธิ์ไม่ควร
    แยกออกได้ว่าตัวเองถูกปิดหรือจำรหัสผิด
    """
    secret = _session_secret(settings)
    username = payload.username.strip()
    client_ip = _client_ip(request)

    left = locked_seconds_left(username, client_ip)
    if left > 0:
        minutes = max(1, -(-left // 60))  # ปัดขึ้น: เหลือ 30 วิ ต้องอ่านว่า 1 นาที
        raise _http_error(
            429,
            f"ใส่รหัสผิดหลายครั้งเกินไป — ลองอีกครั้งในอีก {minutes} นาที",
        )

    db = _readable_db()
    if not await admin_repo.has_active_account(db):
        # ห้ามบอกออกไปว่า "ยังไม่ได้สร้างบัญชี" — คนนอกไม่ต้องรู้ว่าระบบตั้งไม่เสร็จ
        log.warning(
            "มีคนพยายามล็อกอินหน้า admin แต่ยังไม่มีบัญชีที่ใช้งานอยู่ในตาราง "
            "admin_accounts — สร้างด้วย: python scripts/admin_user.py --username <ชื่อ>"
        )
        raise _http_error(403, NO_ACCESS_DETAIL)

    account = await admin_repo.find_account(db, username)
    stored = account["password_hash"] if account else _DUMMY_HASH
    password_ok = verify_password(payload.password, stored)

    if not (account and account["is_active"] and password_ok):
        count = record_failed_login(username, client_ip)
        if count >= MAX_FAILED_ATTEMPTS:
            # username กับ ip log ได้ (ต้องใช้ตามรอย) รหัสผ่าน**ห้าม**
            log.warning(
                "ล็อกการล็อกอิน admin: username=%r ip=%s ผิดครบ %d ครั้ง "
                "ล็อก %d นาที",
                username,
                client_ip,
                count,
                LOCKOUT_SECONDS // 60,
            )
        raise _http_error(401, BAD_CREDENTIALS_DETAIL)

    canonical = account["username"]
    clear_failed_logins(username, client_ip)
    if isinstance(db, SupportsExecute):
        await admin_repo.touch_last_login(db, canonical)

    max_age = settings.admin_session_max_age_seconds
    response.set_cookie(
        SESSION_COOKIE,
        make_session_token(canonical, secret, max_age),
        max_age=max_age,
        httponly=True,
        samesite="lax",
        secure=_cookie_is_secure(request),
        path="/",
    )
    log.info("admin ล็อกอินสำเร็จ: username=%r ip=%s", canonical, client_ip)
    return {"success": True, "username": canonical, "expires_in": max_age}


@router.post("/logout")
async def logout(request: Request, response: Response) -> dict:
    """
    ล้าง cookie ฝั่งเบราว์เซอร์

    **ไม่ต้องมีสิทธิ์ก็เรียกได้** และไม่แตะ DB: token เป็น stateless ยกเลิกฝั่ง
    เซิร์ฟเวอร์ไม่ได้อยู่แล้ว (ดูบล็อกคอมเมนต์เรื่องเซสชันข้างบน) สิ่งที่ทำได้จริงคือ
    บอกเบราว์เซอร์ให้ลบใบที่ถืออยู่ — คนที่ก๊อป token ออกไปแล้วยังใช้ได้จนหมดอายุ
    """
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=_cookie_is_secure(request),
    )
    return {"success": True}


# ── โครง body ของแต่ละฟอร์ม ─────────────────────────────────────────────────
#
# ทุกตัวมี ``max_length`` ทุกช่องโดยเจตนา: หน้านี้เขียนลงตารางที่บอทอ่านไปตอบ
# ข้อความยาว 1 MB ไม่ได้ทำให้ DB พัง แต่ทำให้บอทส่งข้อความไม่ผ่าน LINE
# (เพดาน 5,000 ตัวอักษรต่อข้อความ) ซึ่งจะไปโผล่เป็น "บอทเงียบ" ตอนตอบ
# ไม่ใช่ error ตอนบันทึก — จับที่นี่ให้คนกรอกเห็นทันที
#
# ``answer`` 4,000 ตัว = เผื่อ LINE 5,000 ไว้ให้หัวข้อ/ลิงก์ที่บอทต่อท้ายเอง


class FaqSaveRequest(AdminRequest):
    intent_key: str = Field(min_length=2, max_length=80)
    question: str = Field(min_length=2, max_length=500)
    answer: str = Field(min_length=2, max_length=4_000)
    category: str | None = Field(default=None, max_length=80)
    # คำพ้องที่ควรแมตช์คำถามนี้ — ส่งเป็น list จากหน้าเว็บ (แยกคอมมาให้แล้ว)
    variants: list[str] = Field(default_factory=list, max_length=40)
    source_url: str | None = Field(default=None, max_length=500)


class DocumentSaveRequest(AdminRequest):
    url: str = Field(min_length=8, max_length=500)
    title: str = Field(min_length=2, max_length=300)
    category: str = Field(min_length=1, max_length=80)
    doc_type: str | None = Field(default=None, max_length=40)
    audience: str = Field(default="student", pattern="^(student|staff)$")
    keywords: str | None = Field(default=None, max_length=500)
    note: str | None = Field(default=None, max_length=500)


class InstructorSaveRequest(AdminRequest):
    # ชื่อเป็น **กุญแจ ไม่ใช่ช่องแก้** (ดูเหตุผลใน app/admin_repo.py)
    full_name: str = Field(min_length=2, max_length=200)
    title_prefix: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=60)
    building: str | None = Field(default=None, max_length=120)
    floor: str | None = Field(default=None, max_length=40)
    room: str | None = Field(default=None, max_length=60)
    office_hours: str | None = Field(default=None, max_length=300)
    other_contact: str | None = Field(default=None, max_length=300)
    # ที่มาของข้อมูลที่กรอกมือ — schema 001 สั่งไว้ว่าห้ามเดาเบอร์/ห้อง
    manual_source: str | None = Field(default=None, max_length=300)


class CurriculumRuleSaveRequest(AdminRequest):
    program_code: str = Field(min_length=3, max_length=20)
    # 7 หลัก ใช้ JOIN courses — บังคับด้วย pattern เพราะใส่รหัสเต็มลงช่องนี้
    # แล้วจะหาชื่อวิชาไม่เจอโดยไม่มี error อะไรเลย
    course_code: str = Field(pattern=r"^\d{7}$")
    course_code_full: str | None = Field(default=None, max_length=20)
    std_year: int = Field(ge=1, le=8)
    std_semester: int = Field(ge=1, le=3)
    is_fixed_term: bool = False
    note: str | None = Field(default=None, max_length=500)
    source: str = Field(min_length=2, max_length=200)


class PrerequisiteSaveRequest(AdminRequest):
    program_code: str = Field(min_length=3, max_length=20)
    course_code: str = Field(pattern=r"^\d{7}$")
    requires_code: str = Field(pattern=r"^\d{7}$")
    kind: str = Field(default="hard", pattern="^(hard|soft|concurrent)$")
    source: str = Field(min_length=2, max_length=200)


class PromptRuleSaveRequest(AdminRequest):
    """
    กฎเสริมของ AI หนึ่งข้อ — ช่องเดียวที่หน้าเว็บแตะ prompt ของ AI ได้

    **ไม่มีช่องใดในนี้ที่แก้ prompt หลักได้** prompt หลักอยู่ใน
    ``app/ai_chat.py`` (ค่าคงที่ในโค้ด) ที่นี่ส่งได้แค่ข้อความที่จะถูก
    **ต่อท้าย** ในบล็อก "ข้อจำกัดเพิ่มเติม" เท่านั้น

    ``max_length`` ของ ``rule_text`` ตรงกับ ``ai_chat.PROMPT_RULE_TEXT_LIMIT``
    และ CHECK ใน migration 009 — สามที่ต้องเท่ากัน ไม่งั้นคนกรอกจะเจอ error
    จาก Postgres (อ่านไม่รู้เรื่อง) แทน error จากฟอร์ม
    """

    rule_key: str = Field(min_length=2, max_length=80)
    rule_text: str = Field(min_length=2, max_length=ai_chat.PROMPT_RULE_TEXT_LIMIT)
    # บันทึกภายใน ไม่ถูกส่งให้ AI — มีไว้ให้คนถัดไปรู้ว่ากฎข้อนี้มาจากเรื่องอะไร
    note: str | None = Field(default=None, max_length=500)


class ToggleRequest(AdminRequest):
    # ชื่อตารางถูกจำกัดด้วย ``TABLE_KEYS`` ไม่ใช่ด้วย pattern — allowlist
    # อยู่ที่เดียวกับ SQL ของมัน จะไม่มีวันหลุดกัน
    table: str = Field(min_length=3, max_length=40)
    key: list[str] = Field(min_length=1, max_length=3)
    is_active: bool


class ChatLogsRequest(AdminRequest):
    unanswered_only: bool = True
    limit: int = Field(default=100, ge=1, le=500)


class StateRequest(AdminRequest):
    program_code: str | None = Field(default=None, max_length=20)


# ── endpoints ───────────────────────────────────────────────────────────────
#
# ทุกตัวเป็น POST รวมทั้งตัวที่แค่ "อ่าน" — ตั้งใจให้เหมือนกันหมดทั้งชุด
# เพื่อให้หน้าเว็บมีฟังก์ชันยิงตัวเดียว และเพื่อไม่ให้พารามิเตอร์ (เช่น program_code)
# ไปนอนอยู่ใน access log ของ uvicorn และของ cloudflared
# (ดู memory: access log ของ uvicorn อยู่ที่ stdout)
#
# ตัวตนของคนยิงมาจาก **cookie** ที่ ``/login`` ออกให้ ไม่ได้มาจาก body — เพิ่ม
# endpoint ใหม่ต้องเรียก ``require_admin(request, settings)`` เองทุกครั้ง
# (ลืมแล้วไม่มีอะไรฟ้อง จึงมีเทสไล่เช็คทุก route ใน tests/test_admin.py)


@router.get("/config")
async def admin_config(settings: SettingsDep) -> dict:
    """
    ค่าที่หน้า admin ต้องใช้ก่อนล็อกอิน — **ไม่ต้องมีสิทธิ์ก็เรียกได้**

    ไม่มี ``liff_id`` อีกแล้ว: หน้านี้ไม่ใช้ LINE Login แล้ว (ฝั่งนักศึกษายังใช้)
    เหลือ ``program_code`` ให้หน้าเว็บรู้ว่าจะโหลดหลักสูตรไหนเป็นค่าเริ่มต้น

    ``configured`` = มีบัญชี admin ที่เปิดใช้อยู่ไหม — ส่งออกไปได้เพราะเป็น
    **สถานะการตั้งค่า ไม่ใช่รายชื่อ** (ไม่มีชื่อผู้ใช้หรือ hash ของใครออกไป) และ
    endpoint นี้ไม่ต้องมีสิทธิ์ก็เรียกได้ จึงตอบ ``False`` เมื่อยังไม่มีบัญชีเพื่อให้
    หน้าเว็บบอกคนตั้งระบบได้ว่าต้องรัน ``scripts/admin_user.py`` ก่อน
    — ต่างจาก ``/login`` ที่**ห้าม**บอกเรื่องนี้ เพราะที่นั่นคือปากประตูที่คนนอกยิง

    DB ยังไม่พร้อม = ตอบ ``configured: false`` ไม่ใช่ 503: หน้าเว็บเรียกตัวนี้เป็น
    อย่างแรกสุด ถ้าพังทั้งหน้าเพราะ DB ยัง cold start คนจะเห็นหน้าขาว ๆ เฉย ๆ
    """
    from .main import get_db

    db = get_db()
    configured = bool(db) and await admin_repo.has_active_account(db)
    return {
        "program_code": settings.default_program_code,
        "configured": configured,
    }


@router.post("/state")
async def admin_state(
    request: Request,
    settings: SettingsDep,
    payload: StateRequest | None = None,
) -> dict:
    """
    ทุกตารางที่หน้านี้แก้ได้ ในหนึ่ง request

    ส่งมาทีเดียวหมดเพราะหน้าเว็บเป็นไฟล์เดียวไม่มี router — โหลดครั้งเดียว
    แล้วสลับแท็บในหน้าได้เลย ไม่ต้องยิงใหม่ทุกครั้งที่กดแท็บ (ตารางใหญ่สุด
    33 แถว ขนาดรวมไม่ถึงร้อย KB)
    """
    admin = require_admin(request, settings)
    payload = payload or StateRequest()
    db = _readable_db()
    program = payload.program_code or settings.default_program_code
    log.info("admin เปิดหน้า: username=%r", admin)
    prompt_rules = await admin_repo.list_prompt_rules(db)
    return {
        "program_code": program,
        "counts": await admin_repo.counts(db),
        "faqs": await admin_repo.list_faqs(db),
        "documents": await admin_repo.list_documents(db),
        "instructors": await admin_repo.list_instructors(db),
        "curriculum_rules": await admin_repo.list_curriculum_rules(db, program),
        "prerequisites": await admin_repo.list_prerequisites(db, program),
        "ai_prompt_rules": prompt_rules,
        "ai_prompt": _prompt_preview(prompt_rules),
        "audit": await admin_repo.list_audit(db),
    }


def _prompt_preview(rows: list[dict]) -> dict:
    """
    ตัวอย่าง prompt ที่ AI จะได้รับ — ประกอบด้วย :mod:`app.ai_chat` ตัวจริง

    ส่ง ``core`` (prompt หลัก) ออกไป **เพื่อให้อ่าน ไม่ใช่เพื่อให้แก้**: หน้าเว็บ
    แสดงเป็นข้อความอ่านอย่างเดียว คนกรอกจึงเห็นด้วยตาว่าส่วนไหนแก้ได้ ส่วนไหน
    อยู่ในโค้ด (ไม่มี endpoint ใดในไฟล์นี้รับ ``core`` กลับเข้ามา)

    ประกอบจากแถวที่เพิ่งอ่านมาสด ๆ ไม่ใช่จาก cache ของ ``ai_chat`` — หน้า admin
    ต้องเห็นผลของสิ่งที่ตัวเองเพิ่งบันทึกทันที ส่วนบอทจะตามมาช้าสุดตาม
    ``cache_seconds`` (หน้าเว็บบอกตัวเลขนี้ให้คนกรอกรู้)
    """
    active = [row["rule_text"] for row in rows if row.get("is_active")]
    composed = ai_chat.compose_system_prompt(active)
    return {
        "core": ai_chat.SYSTEM_PROMPT,
        "extra": composed[len(ai_chat.SYSTEM_PROMPT):],
        "active_count": len(active),
        "max_active": ai_chat.PROMPT_RULE_LIMIT,
        "cache_seconds": int(ai_chat.PROMPT_RULES_CACHE_TTL),
    }


@router.post("/chat_logs")
async def admin_chat_logs(
    request: Request,
    settings: SettingsDep,
    payload: ChatLogsRequest | None = None,
) -> dict:
    """
    คำถามที่บอทตอบไม่ได้ — รายการงานของคนเขียน FAQ

    แยกจาก ``/state`` เพราะเป็นตารางเดียวที่โตเรื่อย ๆ ไม่ควรโหลดมาทุกครั้ง
    ที่เปิดหน้า และเพราะมันคือข้อความที่นักศึกษาพิมพ์เอง ควรต้อง "กดดู"
    ไม่ใช่เด้งขึ้นมาเอง
    """
    require_admin(request, settings)
    payload = payload or ChatLogsRequest()
    rows = await admin_repo.list_chat_logs(
        _readable_db(),
        unanswered_only=payload.unanswered_only,
        limit=payload.limit,
    )
    return {"rows": rows, "unanswered_only": payload.unanswered_only}


# ── endpoints: บันทึก ───────────────────────────────────────────────────────
#
# ทุกตัวคืน ``{"ok": True, "action": "create"|"update", "changes": {...}}``
# เหมือนกันหมด เพื่อให้หน้าเว็บมีตัวจัดการผลลัพธ์ตัวเดียว และเพื่อให้คนกดเห็น
# ว่า "บันทึกแล้วเปลี่ยนอะไรไปจริง ๆ" — กดบันทึกแล้วไม่มีอะไรเปลี่ยน
# (changes ว่าง) เป็นข้อมูลที่มีประโยชน์ ไม่ใช่ความล้มเหลว


def _saved(result: dict) -> dict:
    return {"ok": True, **result}


def _lookup_error(exc: LookupError):
    """แถวที่อ้างถึงไม่มี = 404 ไม่ใช่ 500 (คนกรอกผิด ไม่ใช่ระบบพัง)"""
    return _http_error(404, str(exc))


@router.post("/faq")
async def save_faq(
    payload: FaqSaveRequest, request: Request, settings: SettingsDep
) -> dict:
    """
    เขียน FAQ หนึ่งข้อ — นี่คือช่องทางเดียวที่ตาราง ``faqs`` มีข้อมูลได้

    scraper เอาคำตอบพวกนี้มาให้ไม่ได้ (มันเป็นความรู้ที่อยู่ในหัวคน เช่น
    "ดรอปวิชาทำยังไง") ตารางนี้จึงว่างมาตลอด — ดูช่องว่างที่วัดไว้ใน
    ``app/router.py`` ที่ยังตอบคำถามกลุ่มนี้ไม่ได้
    """
    admin = require_admin(request, settings)
    result = await admin_repo.save_faq(
        _writable_db(),
        admin_username=admin,
        intent_key=payload.intent_key.strip(),
        question=payload.question.strip(),
        answer=payload.answer.strip(),
        category=payload.category,
        variants=[v.strip() for v in payload.variants if v.strip()],
        source_url=payload.source_url,
    )
    return _saved(result)


@router.post("/document")
async def save_document(
    payload: DocumentSaveRequest, request: Request, settings: SettingsDep
) -> dict:
    """เพิ่ม/แก้เอกสารหนึ่งฉบับ (``url`` เป็นกุญแจ)"""
    admin = require_admin(request, settings)
    result = await admin_repo.save_document(
        _writable_db(),
        admin_username=admin,
        url=payload.url.strip(),
        title=payload.title.strip(),
        category=payload.category.strip(),
        doc_type=payload.doc_type,
        audience=payload.audience,
        keywords=payload.keywords,
        note=payload.note,
    )
    return _saved(result)


@router.post("/instructor")
async def save_instructor(
    payload: InstructorSaveRequest, request: Request, settings: SettingsDep
) -> dict:
    """
    แก้ข้อมูลติดต่ออาจารย์ — ช่องที่ scraper เอามาให้ไม่ได้

    วัดจากข้อมูลจริง: เว็บคณะมีแต่ชื่อกับอีเมล ``phone``/``room`` ว่าง 0/28 แถว
    ทำให้บอทต้องตอบ "ไม่มีข้อมูล" ทุกครั้งที่มีคนถามว่าอาจารย์อยู่ห้องไหน
    """
    admin = require_admin(request, settings)
    try:
        result = await admin_repo.save_instructor(
            _writable_db(),
            admin_username=admin,
            full_name=payload.full_name.strip(),
            title_prefix=payload.title_prefix,
            email=payload.email,
            phone=payload.phone,
            building=payload.building,
            floor=payload.floor,
            room=payload.room,
            office_hours=payload.office_hours,
            other_contact=payload.other_contact,
            manual_source=payload.manual_source,
        )
    except LookupError as exc:
        raise _lookup_error(exc) from exc
    return _saved(result)


@router.post("/curriculum_rule")
async def save_curriculum_rule(
    payload: CurriculumRuleSaveRequest, request: Request, settings: SettingsDep
) -> dict:
    """
    เพิ่ม/แก้กฎแผนการเรียนหนึ่งวิชา (ปี/ภาคที่หลักสูตรวางไว้)

    ``source`` บังคับกรอก เพราะข้อมูลชุดนี้คือสิ่งที่ planner เอาไปบอกนักศึกษา
    ว่าเทอมหน้าควรลงอะไร — ถ้าไม่รู้ว่าใครบอกมา ก็แก้กลับไม่ได้เมื่อผิด
    """
    admin = require_admin(request, settings)
    result = await admin_repo.save_curriculum_rule(
        _writable_db(),
        admin_username=admin,
        program_code=payload.program_code.strip(),
        course_code=payload.course_code,
        course_code_full=payload.course_code_full,
        std_year=payload.std_year,
        std_semester=payload.std_semester,
        is_fixed_term=payload.is_fixed_term,
        note=payload.note,
        source=payload.source.strip(),
    )
    return _saved(result)


@router.post("/prerequisite")
async def save_prerequisite(
    payload: PrerequisiteSaveRequest, request: Request, settings: SettingsDep
) -> dict:
    """
    เพิ่ม/แก้เงื่อนไขวิชาบังคับก่อน — ตารางนี้ยังว่างทั้งตาราง

    ผลของการที่มันว่าง: ``Progress.prereq_known`` เป็น ``False`` ทำให้หน้า LIFF
    ต้องขึ้นคำเตือนว่า "ลำดับที่เห็นคือเทอมที่แผนแนะนำเท่านั้น" กรอกตารางนี้
    จากเล่ม มคอ.2 แล้วคำเตือนนั้นจะหายไปเอง และ planner จะเช็คให้ได้จริง
    """
    admin = require_admin(request, settings)
    result = await admin_repo.save_prerequisite(
        _writable_db(),
        admin_username=admin,
        program_code=payload.program_code.strip(),
        course_code=payload.course_code,
        requires_code=payload.requires_code,
        kind=payload.kind,
        source=payload.source.strip(),
    )
    return _saved(result)


@router.post("/ai_prompt_rule")
async def save_prompt_rule(
    payload: PromptRuleSaveRequest, request: Request, settings: SettingsDep
) -> dict:
    """
    เพิ่ม/แก้ **ข้อจำกัดเพิ่มเติม** ของ AI หนึ่งข้อ

    ขอบเขตที่ endpoint นี้ทำได้ (และทำได้แค่นี้จริง ๆ):

    * เขียนข้อความหนึ่งบรรทัดลงตาราง ``ai_prompt_rules``
    * ข้อความนั้นถูกต่อ **ท้าย** ``ai_chat.SYSTEM_PROMPT`` ในบล็อกที่มีหัวเรื่อง
      กำกับว่าเป็นข้อจำกัดเพิ่มเติม และมีบรรทัดปิดท้ายบอกโมเดลว่าห้ามถือว่า
      บล็อกนี้ยกเลิกกฎด้านบน (ดู :func:`app.ai_chat.compose_system_prompt`)

    สิ่งที่ทำ **ไม่ได้**: แก้/ลบ/แทนที่ prompt หลัก — prompt หลักเป็นค่าคงที่ใน
    โค้ดและไม่มี route ไหนในไฟล์นี้เขียนมันได้

    การตรวจก่อนเขียน (ทำที่นี่ที่เดียว ชั้น repo ไม่ตรวจ):

    * ตัวอักษรควบคุม/หลายบรรทัด → ยุบเป็นบรรทัดเดียว (กันการแทรกหัวเรื่องปลอม
      เข้าไปในโครงสร้าง prompt)
    * ล้างแล้วเหลือสั้นเกินไป = 400 (ช่องว่าง/ขีดเปล่า ๆ ไม่ใช่กฎ)
    * เพดานจำนวนข้อที่ *เปิดใช้* — บล็อกกฎเสริมยาวกว่ากฎหลักเท่ากับกลบกฎหลัก
      ในทางปฏิบัติ และกินงบ token ของประวัติสนทนาทุกข้อความ
    """
    admin = require_admin(request, settings)

    rule_text = ai_chat.clean_prompt_rule(payload.rule_text)
    if len(rule_text) < 2:
        raise _http_error(400, "ข้อความของกฎสั้นเกินไป (ต้องมีอย่างน้อย 2 ตัวอักษร)")

    rule_key = ai_chat.clean_prompt_rule(payload.rule_key)
    if len(rule_key) < 2:
        raise _http_error(400, "rule_key สั้นเกินไป (ต้องมีอย่างน้อย 2 ตัวอักษร)")

    db = _writable_db()

    # เช็คเพดานเฉพาะตอน "สร้างข้อใหม่" — แถวใหม่เกิดมาพร้อม is_active = TRUE
    # ส่วนการแก้ข้อความของข้อเดิมไม่ได้เพิ่มจำนวนข้อที่เปิดใช้ (upsert ไม่แตะ
    # is_active) จึงไม่ควรถูกบล็อกเวลาที่ข้ออื่นเต็มเพดานอยู่แล้ว
    if await admin_repo.fetch_row(db, "ai_prompt_rules", (rule_key,)) is None:
        active = await admin_repo.active_prompt_rule_count(db)
        if active >= ai_chat.PROMPT_RULE_LIMIT:
            raise _http_error(
                400,
                f"เปิดใช้กฎเสริมได้สูงสุด {ai_chat.PROMPT_RULE_LIMIT} ข้อ "
                f"(ตอนนี้เปิดอยู่ {active} ข้อ) — ปิดข้อที่ไม่ใช้ก่อนเพิ่มข้อใหม่",
            )

    result = await admin_repo.save_prompt_rule(
        db,
        admin_username=admin,
        rule_key=rule_key,
        rule_text=rule_text,
        note=(payload.note or None),
    )
    log.info(
        "admin แก้กฎเสริมของ AI: rule_key=%r action=%s (username=%r)",
        rule_key,
        result["action"],
        admin,
    )
    return _saved(result)


@router.post("/toggle")
async def toggle(
    payload: ToggleRequest, request: Request, settings: SettingsDep
) -> dict:
    """
    เปิด/ปิดหนึ่งแถว — **นี่คือปุ่มที่แทนการลบ** ทั้งหน้านี้ไม่มี DELETE

    ``key`` ต้องมีจำนวนช่องเท่ากับกุญแจของตารางนั้นพอดี ส่งมาไม่ครบแล้ว
    ปล่อยผ่านจะกลายเป็น ``UPDATE`` ที่ขาดเงื่อนไข = ปิดทั้งตารางในคลิกเดียว
    จึงเช็คจำนวนตรงนี้ก่อนแตะฐานข้อมูล
    """
    admin = require_admin(request, settings)

    expected = admin_repo.TABLE_KEYS.get(payload.table)
    if expected is None:
        raise _http_error(400, f"ตาราง {payload.table!r} ไม่อยู่ในรายการที่แก้ได้")
    if len(payload.key) != len(expected):
        raise _http_error(
            400,
            f"ตาราง {payload.table} ต้องระบุกุญแจ {len(expected)} ช่อง "
            f"({', '.join(expected)}) แต่ส่งมา {len(payload.key)}",
        )

    db = _writable_db()

    # เพดานจำนวนกฎเสริมที่เปิดใช้ ต้องบังคับที่ปุ่มเปิดด้วย ไม่ใช่แค่ตอนเพิ่ม
    # ข้อใหม่ — ไม่งั้นเลี่ยงได้ด้วยการเพิ่มให้เต็ม ปิดหนึ่งข้อ เพิ่มอีกข้อ
    # แล้วเปิดข้อที่ปิดไว้กลับมา (จำนวนข้อที่เปิดใช้จะเกินเพดานทันที)
    if payload.table == "ai_prompt_rules" and payload.is_active:
        active = await admin_repo.active_prompt_rule_count(db)
        if active >= ai_chat.PROMPT_RULE_LIMIT:
            raise _http_error(
                400,
                f"เปิดใช้กฎเสริมได้สูงสุด {ai_chat.PROMPT_RULE_LIMIT} ข้อ "
                f"(ตอนนี้เปิดอยู่ {active} ข้อ) — ปิดข้ออื่นก่อนเปิดข้อนี้",
            )

    try:
        result = await admin_repo.toggle_row(
            db,
            admin_username=admin,
            table=payload.table,
            key=tuple(payload.key),
            is_active=payload.is_active,
        )
    except LookupError as exc:
        raise _lookup_error(exc) from exc
    log.info(
        "admin %s แถว %s ของ %s (username=%r)",
        "เปิด" if payload.is_active else "ปิด",
        admin_repo.row_key(payload.table, tuple(payload.key)),
        payload.table,
        admin,
    )
    return _saved(result)
