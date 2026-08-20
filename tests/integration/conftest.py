"""
fixture ของเทสที่ยิง Postgres จริง

**สามเรื่องที่ต้องเข้าใจก่อนแก้ไฟล์นี้**

1. **event loop** — บน Windows ``psycopg`` async ใช้ ``ProactorEventLoop``
   (ค่า default ของ Python) ไม่ได้ จะขึ้น
   ``Psycopg cannot use the 'ProactorEventLoop' to run in async mode``
   และ ``app.db.loop_is_incompatible()`` ดักไว้ก่อนแล้วด้วย
   ``pytest-asyncio`` สร้าง loop จาก policy ของระบบ = Proactor → **เทส async
   ธรรมดาพังทุกตัว** (ยืนยันแล้ว ไม่ใช่การเดา)

   ทางแก้: เทสในโฟลเดอร์นี้เป็นฟังก์ชัน ``def`` ธรรมดา (ไม่ใช่ ``async def``)
   แล้วรัน coroutine ผ่าน fixture :func:`run` ที่ถือ ``SelectorEventLoop``
   ของตัวเองไว้ทั้ง session — วิธีเดียวกับ ``run.py`` ที่รากโปรเจกต์
   ผลพลอยได้: ไม่ต้องพึ่งพฤติกรรมของ ``pytest-asyncio`` เลย และ pool
   ตัวเดียวใช้ได้ทั้ง session (connection ของ pool ผูกกับ loop ที่สร้างมัน)

2. **opt-in** — ชุดนี้จะรันเมื่อสั่งชัด ๆ เท่านั้น::

       pytest -m integration            # ปกติใช้แบบนี้
       RMU_DB_TESTS=1 pytest tests/integration

   ``pytest`` เปล่า ๆ จะ **skip** ทั้งชุด เพื่อให้เลข baseline ของเทส 244 ตัว
   เดิมอ่านได้เหมือนเดิม (และเครื่องที่ไม่มี Docker ก็ไม่พัง)

3. **read-only กับข้อมูล seed** — ห้าม INSERT/UPDATE/DELETE 10 ตารางที่ seed มา
   เขียนได้แค่ตารางปฏิบัติการที่ยังว่าง (``app_users``, ``chat_logs``,
   ``liff_sessions``, ``user_completed_courses``) และต้องลบทิ้งใน teardown
   :func:`row_count_guard` เทียบจำนวนแถวทั้ง 19 ตารางก่อน/หลัง session ให้
   ถ้าไม่เท่ากันจะ error ตอน teardown
"""

from __future__ import annotations

import asyncio
import os
import re
import socket
import subprocess
import sys
from typing import Any, Callable, Coroutine, Iterator, TypeVar
from urllib.parse import urlsplit

import pytest

from app.config import REPO_ROOT, get_settings
from app.db import Database

T = TypeVar("T")

OPT_IN_ENV = "RMU_DB_TESTS"

# ตารางทั้งหมดใน 001_init.sql — ใช้เทียบจำนวนแถวก่อน/หลัง session
ALL_TABLES = (
    "programs",
    "categories",
    "courses",
    "program_courses",
    "offerings",
    "offering_slots",
    "offering_patterns",
    "documents",
    "instructors",
    "instructor_affiliations",
    "prerequisites",
    "curriculum_rules",
    "faqs",
    "rag_chunks",
    "scrape_runs",
    "app_users",
    "chat_logs",
    "liff_sessions",
    "user_completed_courses",
)

# prefix ของแถวทดสอบ — teardown ลบตาม prefix นี้เท่านั้น
TEST_HASH_PREFIX = "itest-"


def pytest_configure(config: pytest.Config) -> None:
    """
    ลงทะเบียน marker เอง — **ห้ามแก้ ``pytest.ini``** (ไฟล์ config ที่รากโปรเจกต์
    มีคนอื่นแก้อยู่) และ ``addopts`` มี ``--strict-markers`` อยู่ ถ้าไม่ลงทะเบียน
    marker จะ error ทันทีตอน collect
    """
    config.addinivalue_line(
        "markers", "integration: ต้องมี Postgres จริงที่รันอยู่ (opt-in)"
    )
    config.addinivalue_line(
        "markers", "restart: รีสตาร์ต container ของฐานข้อมูล (ช้า ~10 วินาที)"
    )


def _opted_in(config: pytest.Config) -> bool:
    """สั่งรันชุดนี้ชัดเจนแล้วหรือยัง"""
    flag = os.environ.get(OPT_IN_ENV, "").strip().lower()
    if flag not in ("", "0", "false", "no"):
        return True
    expr = getattr(config.option, "markexpr", "") or ""
    return re.search(r"(?<!not\s)\bintegration\b", expr) is not None


def _tcp_reachable(dsn: str, timeout: float = 2.0) -> tuple[bool, str]:
    """
    เช็ค TCP ก่อนเปิด pool — ให้ skip ไว ๆ เมื่อ DB ไม่ได้รัน

    คืน ``(True, "")`` เมื่อแยก host/port จาก DSN ไม่ได้ (ไปลองเปิด pool จริงต่อ)
    """
    try:
        parts = urlsplit(dsn)
        host, port = parts.hostname, parts.port or 5432
    except ValueError:
        return True, ""
    if not host:
        return True, ""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, ""
    except OSError as exc:
        return False, f"ต่อ {host}:{port} ไม่ได้ ({exc})"


@pytest.fixture(scope="session")
def selector_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """
    event loop ที่ psycopg async ใช้ได้ — ตัวเดียวทั้ง session

    ต้องเป็นตัวเดียวเพราะ connection ใน pool ลงทะเบียน reader/writer ไว้กับ
    loop ที่สร้างมัน ถ้าเปลี่ยน loop กลาง session pool จะใช้ต่อไม่ได้
    """
    loop = (
        asyncio.SelectorEventLoop()
        if sys.platform.startswith("win")
        else asyncio.new_event_loop()
    )
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
def run(
    selector_loop: asyncio.AbstractEventLoop,
) -> Callable[[Coroutine[Any, Any, T]], T]:
    """รัน coroutine บน :func:`selector_loop` — ใช้แทน ``await`` ในเทส ``def``"""

    def _run(coro: Coroutine[Any, Any, T]) -> T:
        return selector_loop.run_until_complete(coro)

    return _run


@pytest.fixture(scope="session")
def dsn(pytestconfig: pytest.Config) -> str:
    """
    DSN จาก settings ของแอปเอง (อ่าน ``.env``) — **ห้าม hardcode รหัสผ่าน**

    skip พร้อมเหตุผลภาษาไทยเมื่อยังไม่ opt-in / ไม่มี DATABASE_URL / ต่อไม่ได้
    """
    if not _opted_in(pytestconfig):
        pytest.skip(
            "เทสชุดนี้ต้องสั่งรันเอง: `pytest -m integration` "
            f"หรือตั้ง {OPT_IN_ENV}=1 (ปล่อยให้ `pytest` เปล่า ๆ เห็นเลข baseline เดิม)"
        )
    url = get_settings().database_url
    if not url:
        pytest.skip("ยังไม่ได้ตั้ง DATABASE_URL ใน .env — ข้ามเทสที่ต้องใช้ Postgres จริง")
    ok, why = _tcp_reachable(url)
    if not ok:
        pytest.skip(f"Postgres ไม่ตอบ: {why} — สั่ง `docker compose up -d db` ก่อน")
    return url


@pytest.fixture(scope="session")
def live_db(dsn: str, run: Callable[..., Any]) -> Iterator[Database]:
    """
    ``app.db.Database`` ตัวจริงที่เปิด pool ค้างไว้ทั้ง session

    ใช้ของแอปเองทั้งก้อน (ไม่ใช่ psycopg ดิบ) เพื่อให้เทสยืนยันชั้นที่แอปใช้จริง
    """
    database = Database(dsn, connect_timeout=10.0)
    try:
        run(database.open())
    except Exception as exc:  # ต่อไม่ได้ = ไม่ใช่ความผิดของเทสตัวใด
        pytest.skip(f"เปิด connection pool ไม่ได้ ({type(exc).__name__}: {exc})")
    try:
        yield database
    finally:
        run(database.close())


async def cleanup_test_rows(db: Database) -> None:
    """
    ลบเฉพาะแถวที่เทสสร้าง — อ้างจาก ``line_user_hash`` ที่ขึ้นต้นด้วย prefix

    ลำดับสำคัญ: ``chat_logs.user_id`` เป็น ``ON DELETE SET NULL`` (ไม่ cascade)
    ถ้าลบ ``app_users`` ก่อน แถว log จะค้างแบบไม่มีเจ้าของและกวาดไม่ได้อีก

    ทุกคำสั่งต้องมี ``RETURNING`` เพราะ :class:`app.db.Database` มีแต่
    ``fetch_all``/``fetch_one`` ที่เรียก ``fetchall()`` เสมอ — DELETE เปล่า ๆ
    จะโยน ``ProgrammingError`` แล้ว transaction ถูก rollback ทั้งก้อน
    (ดู ``test_20_pool.py::test_write_without_returning_is_rejected``)
    """
    ids = await db.fetch_all(
        "SELECT id FROM app_users WHERE line_user_hash LIKE %s",
        (TEST_HASH_PREFIX + "%",),
    )
    if not ids:
        return
    keys = [row["id"] for row in ids]
    await db.fetch_all(
        "DELETE FROM chat_logs WHERE user_id = ANY(%s) RETURNING id", (keys,)
    )
    await db.fetch_all(
        "DELETE FROM liff_sessions WHERE user_id = ANY(%s) RETURNING id", (keys,)
    )
    await db.fetch_all(
        "DELETE FROM user_completed_courses WHERE user_id = ANY(%s) RETURNING id",
        (keys,),
    )
    await db.fetch_all("DELETE FROM app_users WHERE id = ANY(%s) RETURNING id", (keys,))


@pytest.fixture(scope="session", autouse=True)
def row_count_guard(
    live_db: Database, run: Callable[..., Any]
) -> Iterator[dict[str, int]]:
    """
    ฐานข้อมูลต้องจบ session ด้วยจำนวนแถวเท่ากับตอนเริ่ม

    ทำเป็น teardown (ไม่ใช่เทสตัวท้าย) เพื่อให้ทำงานแม้เทสอื่นล้มกลางทาง
    """

    async def snapshot() -> dict[str, int]:
        rows = await live_db.fetch_all(
            " UNION ALL ".join(
                f"SELECT '{name}' AS t, count(*) AS n FROM {name}"
                for name in ALL_TABLES
            )
        )
        return {row["t"]: row["n"] for row in rows}

    before = run(snapshot())
    try:
        yield before
    finally:
        # กวาดแถวทดสอบที่อาจค้าง (เช่นเทสล้มก่อนถึง teardown ของตัวเอง)
        run(cleanup_test_rows(live_db))
        after = run(snapshot())
        changed = {
            name: (before[name], after[name])
            for name in ALL_TABLES
            if before[name] != after[name]
        }
        assert not changed, f"จำนวนแถวเปลี่ยนหลังรันเทส (ตาราง: ก่อน→หลัง) {changed}"


@pytest.fixture(scope="session")
def docker_compose() -> Callable[[list[str]], "subprocess.CompletedProcess[str]"]:
    """
    เรียก ``docker compose`` ที่รากโปรเจกต์ — skip ถ้าไม่มี docker ให้ใช้

    อนุญาตแค่คำสั่งที่ **ไม่ทำลาย volume** (ชุดนี้ใช้แค่ ``restart``)
    เพราะ re-seed ใหม่ใช้เวลาหลายนาที และงานอื่นพึ่งฐานข้อมูลตัวนี้อยู่
    """

    def _run(args: list[str]) -> "subprocess.CompletedProcess[str]":
        forbidden = {"down", "rm", "kill", "stop"} & set(args)
        if forbidden:
            raise AssertionError(f"ห้ามสั่ง {sorted(forbidden)} — volume/ข้อมูลจะหาย")
        try:
            return subprocess.run(
                ["docker", "compose", *args],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=120,
            )
        except FileNotFoundError:
            pytest.skip("ไม่มีคำสั่ง docker ในเครื่องนี้ — ข้ามเทสที่ต้องรีสตาร์ต DB")

    return _run


@pytest.fixture
def test_user(live_db: Database, run: Callable[..., Any]) -> Iterator[int]:
    """``app_users`` หนึ่งแถวสำหรับเทสที่ต้องเขียนจริง — ลบทิ้งเสมอใน teardown"""
    run(cleanup_test_rows(live_db))  # กันแถวค้างจากเทสก่อนหน้าที่ล้มกลางทาง
    row = run(
        live_db.fetch_one(
            "INSERT INTO app_users (line_user_hash, program_code, study_year)"
            " VALUES (%s, %s, %s) RETURNING id",
            (TEST_HASH_PREFIX + "user", get_settings().default_program_code, 3),
        )
    )
    assert row is not None, "INSERT ... RETURNING ต้องคืนแถวกลับมา"
    try:
        yield int(row["id"])
    finally:
        run(cleanup_test_rows(live_db))

