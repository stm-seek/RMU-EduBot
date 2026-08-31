"""
สร้าง / รีเซ็ตรหัส / ปิด บัญชีผู้ดูแลหน้า ``/admin``

หน้า ``/admin`` ยืนยันตัวตนด้วย username + password ของระบบเราเอง (ไม่ใช่ LINE
Login) บัญชีอยู่ในตาราง ``admin_accounts`` และ **ไม่มีหน้าเว็บให้สมัคร** โดยเจตนา
— ประตูเดียวที่สร้างบัญชีได้คือสคริปต์นี้ ซึ่งต้องรันบนเครื่องที่มี ``.env`` จริง::

    set PYTHONUTF8=1
    python scripts/admin_user.py --username somchai      # สร้างใหม่ / รีเซ็ตรหัส
    python scripts/admin_user.py --list                  # ดูว่ามีใครอยู่
    python scripts/admin_user.py --deactivate somchai    # ถอนสิทธิ์ (ไม่ลบแถว)

**รหัสผ่านรับทาง prompt เท่านั้น ไม่มีอาร์กิวเมนต์ให้ใส่** เพราะค่าที่พิมพ์ใน
บรรทัดคำสั่งจะไปนอนอยู่ใน history ของ shell และใน process list ของเครื่อง

สคริปต์นี้ **ไม่ได้สร้างตาราง** ให้ — รัน ``db/migrations/008_admin_accounts.sql``
ก่อน (ไม่งั้นจะได้ error ว่าไม่มีตาราง ซึ่งบอกอยู่ในตัวว่าต้องทำอะไร)
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg  # noqa: E402

from app.admin import MIN_PASSWORD_LENGTH, hash_password  # noqa: E402
from app.admin_repo import (  # noqa: E402
    SQL_ADMIN_ACCOUNT_DEACTIVATE,
    SQL_ADMIN_ACCOUNT_LIST,
    SQL_ADMIN_ACCOUNT_UPSERT,
)
from app.config import get_settings  # noqa: E402

# รหัสที่เจอบ่อยที่สุดในลิสต์รหัสรั่ว — ไม่ได้พยายามเป็น blocklist ที่ครบ (ทำไม่ได้
# และไม่ใช่หน้าที่ของสคริปต์นี้) แค่กันค่าที่ถ้าหลุดออกไปจะโดนเดาในนาทีแรก
# ความยาวขั้นต่ำ 12 ตัวเป็นด่านหลัก ตัวนี้เป็นด่านเสริม
COMMON_PASSWORDS = frozenset(
    {
        "password",
        "password123",
        "passw0rd",
        "12345678",
        "123456789",
        "1234567890",
        "qwertyuiop",
        "adminadmin",
        "administrator",
        "letmeinplease",
    }
)


def _read_new_password(username: str) -> str:
    """
    ถามรหัสผ่านสองครั้ง (ไม่แสดงบนจอ) แล้วตรวจก่อนคืนค่า

    ตรวจสามอย่าง: พิมพ์ตรงกันสองครั้ง, ยาว >= 12 ตัว, ไม่ใช่รหัสที่เดาได้ทันที
    (รวมถึงชื่อผู้ใช้ตัวเอง ซึ่งเป็นสิ่งแรกที่คนเดาลอง)

    วนถามใหม่เมื่อไม่ผ่าน ไม่ใช่ยอมรับไปก่อน — หน้านี้เปิดออกอินเทอร์เน็ตและ
    แก้คำตอบที่บอทเอาไปตอบนักศึกษาได้
    """
    while True:
        first = getpass.getpass(f"รหัสผ่านใหม่ของ {username} (ไม่แสดงบนจอ): ")
        second = getpass.getpass("พิมพ์อีกครั้งเพื่อยืนยัน: ")
        if first != second:
            print("  ✗ สองครั้งไม่ตรงกัน — ลองใหม่")
            continue
        if len(first) < MIN_PASSWORD_LENGTH:
            print(f"  ✗ สั้นเกินไป (ต้องอย่างน้อย {MIN_PASSWORD_LENGTH} ตัว) — ลองใหม่")
            continue
        lowered = first.lower()
        if lowered in COMMON_PASSWORDS or lowered == username.lower():
            print("  ✗ รหัสนี้เดาได้ง่ายเกินไป — ลองใหม่")
            continue
        return first


def _create_or_reset(conn: psycopg.Connection, username: str) -> None:
    password = _read_new_password(username)
    with conn.cursor() as cur:
        # ส่งค่าเป็นพารามิเตอร์ ``%s`` เสมอ — ห้ามต่อสตริงเข้า SQL
        cur.execute(SQL_ADMIN_ACCOUNT_UPSERT, (username, hash_password(password)))
    conn.commit()
    # ห้าม print รหัสผ่านหรือ hash ออกจอ (จอนี้อาจถูกแคปหรืออยู่ใน log ของ CI)
    print(f"✓ ตั้งรหัสผ่านของ {username.lower()!r} แล้ว และเปิดใช้บัญชีนี้")
    print("  ล็อกอินที่หน้า /admin ได้เลย ไม่ต้องรีสตาร์ตเซิร์ฟเวอร์")


def _deactivate(conn: psycopg.Connection, username: str) -> None:
    with conn.cursor() as cur:
        cur.execute(SQL_ADMIN_ACCOUNT_DEACTIVATE, (username,))
        touched = cur.rowcount
    conn.commit()
    if not touched:
        raise SystemExit(f"ไม่มีบัญชีชื่อ {username!r} (ดูรายชื่อด้วย --list)")
    print(f"✓ ปิดบัญชี {username!r} แล้ว (แถวยังอยู่ ประวัติใน audit ยังอ้างชื่อนี้ได้)")
    print(
        "  หมายเหตุ: cookie ที่คนนี้ถืออยู่ **ยังใช้ได้จนหมดอายุ** (อย่างมาก 8 ชม.)\n"
        "  ต้องตัดทันที = เปลี่ยน ADMIN_SESSION_SECRET ใน .env แล้วรีสตาร์ต\n"
        "  ซึ่งเตะทุกคนออกพร้อมกัน ไม่ใช่คนเดียว"
    )


def _list(conn: psycopg.Connection) -> None:
    """แสดงรายชื่อ — **ไม่มีคอลัมน์ password_hash** ในผลลัพธ์โดยเจตนา"""
    with conn.cursor() as cur:
        cur.execute(SQL_ADMIN_ACCOUNT_LIST)
        rows = cur.fetchall()
    if not rows:
        print("ยังไม่มีบัญชีผู้ดูแลเลย — ตอนนี้ไม่มีใครเข้าหน้า /admin ได้ (fail closed)")
        return
    print(f"{'สถานะ':<8}{'ชื่อผู้ใช้':<24}{'สร้างเมื่อ':<22}เข้าครั้งล่าสุด")
    for username, is_active, created_at, last_login_at in rows:
        state = "เปิด" if is_active else "ปิด"
        last = last_login_at.strftime("%Y-%m-%d %H:%M") if last_login_at else "—"
        print(
            f"{state:<8}{username:<24}"
            f"{created_at.strftime('%Y-%m-%d %H:%M'):<22}{last}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="จัดการบัญชีผู้ดูแลหน้า /admin (รหัสผ่านถามทาง prompt เท่านั้น)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--username", help="สร้างบัญชีใหม่ หรือรีเซ็ตรหัสของบัญชีที่มีอยู่")
    group.add_argument("--deactivate", help="ปิดบัญชี (ไม่ลบแถว)")
    group.add_argument("--list", action="store_true", help="ดูรายชื่อบัญชีทั้งหมด")
    args = parser.parse_args()

    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("ยังไม่ได้ตั้ง DATABASE_URL ใน .env")

    with psycopg.connect(settings.database_url) as conn:
        if args.list:
            _list(conn)
        elif args.deactivate:
            _deactivate(conn, args.deactivate.strip())
        else:
            username = args.username.strip()
            if not username or len(username) > 80:
                raise SystemExit("ชื่อผู้ใช้ต้องยาว 1–80 ตัวอักษร")
            _create_or_reset(conn, username)


if __name__ == "__main__":
    main()
