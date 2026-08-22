"""
smoke test — ยืนยันว่า "Postgres จริง" ที่ใช้เทสคือของที่คาดไว้จริง

เทสในไฟล์นี้ต้องผ่าน **ก่อน** ไฟล์อื่นจะมีความหมาย: ถ้า extension หาย
หรือ seed ไม่ครบ ผลของเทส repository จะตีความไม่ได้เลย

ตั้งชื่อไฟล์เป็นเลขเพื่อคุมลำดับ (pytest เก็บไฟล์ตามชื่อ) — ให้ smoke มาก่อน
และเทสที่รีสตาร์ต container (``test_90_restart.py``) อยู่ท้ายสุด
"""

from __future__ import annotations

from typing import Any, Callable

import pytest

from app.db import Database

from .conftest import ALL_TABLES

pytestmark = pytest.mark.integration

# จำนวนแถวที่ seed ใส่ไว้ — 002_seed_data.sql (1,065 แถว)
# บวก 003_curriculum_rules.sql (แผนการเรียนของ 643170151 อีก 32 แถว)
EXPECTED_SEED_ROWS = {
    "curriculum_rules": 32,
    "programs": 2,
    "categories": 26,
    "courses": 145,
    "program_courses": 125,
    "offerings": 337,
    "offering_slots": 292,
    "offering_patterns": 45,
    "documents": 32,
    "instructors": 28,
    "instructor_affiliations": 33,
}

# ตารางที่ seed ตั้งใจปล่อยให้ว่าง — ถ้ามีข้อมูลโผล่มา แปลว่ามีคนรัน seed อื่นทับ
# และค่าที่เทสอื่นคาดไว้ (เช่น prerequisites = 0) จะไม่จริงอีกต่อไป
#
# ``curriculum_rules`` **ออกจากลิสต์นี้แล้ว** ตั้งแต่ 22 ส.ค. 2026: แผนการเรียน
# ของ 643170151 นำเข้าจริง 32 แถว (ดู db/seed/003_curriculum_rules.sql)
# ส่วน ``prerequisites`` ยังว่างอยู่ เพราะระบบทะเบียนไม่เผยแพร่วิชาบังคับก่อน
# ต้องกรอกจากเล่ม มคอ.2 ซึ่งยังไม่มี — planner รู้ตัวและบอกผู้ใช้ตรง ๆ
EXPECTED_EMPTY = (
    "prerequisites",
    "faqs",
    "rag_chunks",
    "scrape_runs",
    "liff_sessions",
    "user_completed_courses",
)

# ตารางปฏิบัติการที่รับ traffic จริงได้ทันทีที่บอททำงาน (มี user เทสต์จริง
# ใน LINE) → ห้าม assert ว่าว่าง แต่ต้องไม่มีแถวทดสอบ (prefix ``itest-``)
# ค้างจากรอบที่พังกลางทาง — ถ้ามี แปลว่า cleanup ใน conftest ทำงานไม่ครบ
OPERATIONAL_LEFTOVER_CHECKS = {
    "app_users": "line_user_hash LIKE 'itest-%'",
    "chat_logs": (
        "user_id IN (SELECT id FROM app_users WHERE line_user_hash LIKE 'itest-%')"
    ),
}


def test_loop_is_selector(selector_loop: Any) -> None:
    """
    กันความเข้าใจผิดข้อเดียวที่ทำให้เทสทั้งชุดพัง

    ถ้าอ่าน traceback ว่า ``Psycopg cannot use the 'ProactorEventLoop'``
    ให้กลับมาดู :mod:`tests.integration.conftest` — ไม่ใช่โค้ดที่กำลังเทส
    """
    from app.db import loop_is_incompatible

    assert not loop_is_incompatible(selector_loop), type(selector_loop).__name__


def test_select_one(live_db: Database, run: Callable[..., Any]) -> None:
    """เทสที่เล็กที่สุดที่พิสูจน์ว่า pool + driver + DB ต่อกันติดจริง"""
    assert run(live_db.fetch_one("SELECT 1 AS ok")) == {"ok": 1}


def test_healthy_is_true(live_db: Database, run: Callable[..., Any]) -> None:
    """``/health`` เรียกเมธอดนี้ — mock บอกได้แค่ว่า logic ถูก ไม่ได้บอกว่าต่อติด"""
    assert run(live_db.healthy()) is True


def test_extensions_installed(live_db: Database, run: Callable[..., Any]) -> None:
    """``pg_trgm`` ต้องมี ไม่งั้น ``%`` ใน SQL_SEARCH_* จะ error ไม่ใช่คืนศูนย์แถว"""
    rows = run(
        live_db.fetch_all(
            "SELECT extname, extversion FROM pg_extension ORDER BY extname"
        )
    )
    installed = {row["extname"] for row in rows}
    assert {"vector", "pg_trgm"} <= installed, installed


def test_server_encoding_is_utf8(live_db: Database, run: Callable[..., Any]) -> None:
    """ภาษาไทยจะกลายเป็น mojibake ทันทีถ้า encoding ไม่ใช่ UTF8"""
    row = run(live_db.fetch_one("SHOW server_encoding"))
    assert row == {"server_encoding": "UTF8"}


def test_every_table_from_migration_exists(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(
        live_db.fetch_all(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
    )
    present = {row["tablename"] for row in rows}
    missing = set(ALL_TABLES) - present
    assert not missing, f"ตารางหายไปจากฐานข้อมูล: {sorted(missing)}"


@pytest.mark.parametrize("table,expected", sorted(EXPECTED_SEED_ROWS.items()))
def test_seed_row_count(
    live_db: Database, run: Callable[..., Any], table: str, expected: int
) -> None:
    """
    ล็อกจำนวนแถวของข้อมูล seed

    เทสตัวอื่นยืนยันค่าจริง (เช่น "อีเมล 26 จาก 28 คน") ถ้าใครรัน seed ใหม่
    แล้วจำนวนเปลี่ยน เทสพวกนั้นจะพังแบบอ่านไม่รู้เรื่อง — ให้พังที่นี่ก่อน
    """
    row = run(live_db.fetch_one(f"SELECT count(*) AS n FROM {table}"))
    assert row is not None and row["n"] == expected


@pytest.mark.parametrize("table", EXPECTED_EMPTY)
def test_operational_table_is_empty(
    live_db: Database, run: Callable[..., Any], table: str
) -> None:
    row = run(live_db.fetch_one(f"SELECT count(*) AS n FROM {table}"))
    assert row is not None and row["n"] == 0, f"{table} ต้องว่าง (ได้ {row})"


@pytest.mark.parametrize("table,condition", sorted(OPERATIONAL_LEFTOVER_CHECKS.items()))
def test_no_test_rows_left_in_operational_tables(
    live_db: Database, run: Callable[..., Any], table: str, condition: str
) -> None:
    """
    ตารางปฏิบัติการมีแถวจาก user จริงได้เสมอ — แค่ห้ามมี **แถวทดสอบค้าง**

    ``conftest.cleanup_test_rows`` กวาดตาม prefix ``itest-`` อยู่แล้ว ถ้า
    เทสนี้แดงแปลว่า teardown ของ session ก่อนหน้าไม่ทำงาน
    """
    row = run(
        live_db.fetch_one(f"SELECT count(*) AS n FROM {table} WHERE {condition}")
    )
    assert row is not None and row["n"] == 0, f"{table} มีแถวทดสอบค้าง (ได้ {row})"


def test_thai_text_round_trips_from_seed(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ข้อความไทยจาก seed ต้องกลับมาเป็น ``str`` ที่ตรงตัวอักษรทุกตัว

    ถ้า driver/encoding ผิดจะได้ ``bytes`` หรือ mojibake — เช็คด้วยการเทียบ
    ทั้งตัวสตริงและจำนวนอักขระ (mojibake ทำให้จำนวนอักขระเปลี่ยน)
    """
    expected = "การจัดการนวัตกรรมดิจิทัล"
    row = run(
        live_db.fetch_one(
            "SELECT program_name, char_length(program_name) AS n"
            " FROM programs WHERE program_code = %s",
            ("643170151",),
        )
    )
    assert row is not None
    assert isinstance(row["program_name"], str)
    assert row["program_name"] == expected
    # ฝั่ง Postgres นับได้เท่ากับฝั่ง Python = ไม่มีการแปลง encoding หลงทาง
    assert row["n"] == len(expected) == 24


def test_thai_text_round_trips_both_ways(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ส่งไทยเข้าไปแล้วรับกลับมาผ่าน placeholder ``%s``

    ครอบคลุมตัวที่ยากจริง: สระ/วรรณยุกต์ซ้อน (``ษ์``), ไม้ยมก (``ๆ``),
    เลขไทย และวรรณยุกต์บนพยัญชนะที่มีหางล่าง
    """
    sample = "อาจารย์ ดร.วีระพน ภานุรักษ์ ๆ ๑๒๓ ฿"
    row = run(live_db.fetch_one("SELECT %s::text AS s", (sample,)))
    assert row is not None and row["s"] == sample
