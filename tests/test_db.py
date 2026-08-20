"""
เทสชั้นเชื่อมต่อฐานข้อมูล

ไฟล์นี้ครอบเฉพาะสิ่งที่ตรวจได้ **โดยไม่ต้องมี Postgres** ซึ่งก็คือส่วนที่พลาดง่ายสุด
(ของที่ต้องมี DB จริงอยู่ที่ ``tests/integration/`` แล้ว):

* ต่อ DB ไม่ได้ ต้อง **ไม่ทำให้แอปสตาร์ทไม่ขึ้น** (ฟีเจอร์อื่นต้องใช้งานต่อได้)
* เรียก query ก่อนเปิด pool ต้องได้ error ที่อ่านรู้เรื่อง ไม่ใช่ ``AttributeError``

* ``execute()`` ต้อง **ไม่** เรียก ``fetchall()`` — เป็นสาเหตุที่เขียน DB ไม่ลง
"""

from __future__ import annotations

import asyncio
import logging
import sys
import types

import pytest

from app import db as db_module
from app.db import (
    Database,
    SupportsExecute,
    SupportsQuery,
    connect,
    loop_is_incompatible,
)

from .helpers import FakeDatabase, make_settings


def test_requires_a_dsn() -> None:
    """DSN ว่างแล้วสร้าง pool ต่อ = ไปพังตอน connect ซึ่ง debug ยากกว่า"""
    with pytest.raises(ValueError, match="DATABASE_URL"):
        Database("")


def test_starts_closed() -> None:
    assert Database("postgresql://u:p@127.0.0.1:5432/db").is_open is False


async def test_query_before_open_raises_readable_error() -> None:
    database = Database("postgresql://u:p@127.0.0.1:5432/db")

    with pytest.raises(RuntimeError, match="open"):
        await database.fetch_all("SELECT 1")

    with pytest.raises(RuntimeError, match="open"):
        await database.fetch_one("SELECT 1")


async def test_healthy_is_false_before_open() -> None:
    """health check ต้องตอบได้เสมอ ห้าม raise"""
    assert await Database("postgresql://u:p@127.0.0.1:5432/db").healthy() is False


async def test_close_is_safe_when_never_opened() -> None:
    """เรียกตอน shutdown ได้เสมอ แม้ startup จะต่อ DB ไม่สำเร็จ"""
    await Database("postgresql://u:p@127.0.0.1:5432/db").close()


# ── connect() ───────────────────────────────────────────────────────────────


async def test_connect_returns_none_without_database_url(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.db"):
        assert await connect(make_settings(database_url="")) is None

    assert "DATABASE_URL" in caplog.text


async def test_connect_returns_none_when_database_unreachable(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """
    DB ล่มต้องไม่ทำให้แอปสตาร์ทไม่ขึ้น — verify webhook, เมนู และ LIFF login
    ไม่ต้องใช้ DB เลย ควรทำงานต่อได้
    """

    async def _boom(self) -> None:
        raise OSError("ต่อไม่ได้")

    monkeypatch.setattr(db_module.Database, "open", _boom)

    with caplog.at_level(logging.ERROR, logger="app.db"):
        assert await connect(make_settings()) is None

    assert "ต่อฐานข้อมูลไม่ได้" in caplog.text
    assert "OSError" in caplog.text, "ต้องบอกชนิด error ไว้ debug"


async def test_connect_returns_database_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened: list[str] = []

    async def _ok(self) -> None:
        opened.append(self._dsn)

    monkeypatch.setattr(db_module.Database, "open", _ok)
    database = await connect(make_settings())

    assert isinstance(database, Database)
    assert opened == [make_settings().database_url]


async def test_connect_uses_configured_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    ปรับได้ผ่าน ``DB_CONNECT_TIMEOUT_SECONDS`` — ตอน dev ที่ยังไม่มี DB
    ค่าต่ำทำให้สตาร์ทเร็วขึ้น ส่วน production ต้องเผื่อ cold start ของ managed DB
    """

    async def _ok(self) -> None:
        return None

    monkeypatch.setattr(db_module.Database, "open", _ok)
    database = await connect(make_settings(db_connect_timeout_seconds=2.5))

    assert database is not None
    assert database._connect_timeout == 2.5


# ── การจัดการ pool ที่เปิดไม่สำเร็จ ─────────────────────────────────────────


class FakePool:
    """pool ปลอมที่เปิดไม่สำเร็จ — ใช้ตรวจว่าเราปิดมันทิ้งจริง"""

    check_connection = staticmethod(lambda conn: None)
    instances: list["FakePool"] = []

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.closed = False
        FakePool.instances.append(self)

    async def open(self, **kwargs) -> None:
        raise TimeoutError("pool initialization incomplete")

    async def close(self, timeout: float = 5.0) -> None:
        self.closed = True
        self.close_timeout = timeout


def install_fake_pool(monkeypatch: pytest.MonkeyPatch) -> type[FakePool]:
    """
    แทน ``psycopg_pool`` ด้วยของปลอม + ปิดการตรวจ event loop

    ต้องปิด ``loop_is_incompatible`` เพราะ pytest-asyncio รันบน
    ``ProactorEventLoop`` (default ของ Windows) → guard จะยิงก่อนถึงโค้ด pool
    ถ้าวันหนึ่งเพิ่มเทสที่ต่อ Postgres จริง ต้องตั้ง loop ของ pytest เป็น
    Selector ด้วย (เหตุผลเดียวกับที่ต้องมี ``run.py``)
    """
    FakePool.instances = []
    monkeypatch.setattr(db_module, "loop_is_incompatible", lambda loop: False)
    monkeypatch.setitem(
        sys.modules, "psycopg_pool", types.SimpleNamespace(AsyncConnectionPool=FakePool)
    )
    monkeypatch.setitem(
        sys.modules, "psycopg.rows", types.SimpleNamespace(dict_row=object())
    )
    return FakePool


async def test_failed_open_closes_the_pool(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ถ้าไม่ปิด pool ที่เปิดค้าง worker task จะวน retry ต่อไปตลอดอายุ process
    (เจอจริงใน log: ``psycopg.pool | couldn't stop task 'pool-1-worker-0'``)

    ปิดด้วย timeout สั้นเพราะ pool ยังไม่เคยใช้งาน — ไม่มี connection ต้อง drain
    """
    pool_class = install_fake_pool(monkeypatch)

    with pytest.raises(TimeoutError):
        await Database("postgresql://u:p@127.0.0.1:5432/db").open()

    assert len(pool_class.instances) == 1
    assert pool_class.instances[0].closed is True
    assert pool_class.instances[0].close_timeout == 1.0


async def test_failed_open_leaves_database_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    install_fake_pool(monkeypatch)
    database = Database("postgresql://u:p@127.0.0.1:5432/db")

    with pytest.raises(TimeoutError):
        await database.open()

    assert database.is_open is False
    with pytest.raises(RuntimeError, match="open"):
        await database.fetch_all("SELECT 1")


async def test_pool_is_created_with_conservative_limits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    free tier ของ Supabase/Neon ให้ connection น้อย — เปิดเยอะจะโดนปฏิเสธ
    และต้องเปิด ``check`` ไว้ ไม่งั้น connection ค้างหลัง DB restart
    """
    pool_class = install_fake_pool(monkeypatch)

    with pytest.raises(TimeoutError):
        await Database("postgresql://u:p@127.0.0.1:5432/db").open()

    kwargs = pool_class.instances[0].kwargs
    assert kwargs["min_size"] == 1
    assert kwargs["max_size"] == 4
    assert kwargs["open"] is False, "ต้องเปิดเองทีหลังเพื่อรอ/จับ error ได้"
    assert kwargs["check"] is not None


# ── event loop บน Windows ───────────────────────────────────────────────────


async def test_open_refuses_incompatible_windows_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    ``ProactorEventLoop`` (default ของ Windows) ใช้กับ psycopg async ไม่ได้

    ถ้าไม่ดักไว้ จะได้ pool timeout 10 วินาที + ข้อความจาก psycopg
    ที่ไม่บอกว่าต้องแก้ที่ไหน (เจอจริงตอนรัน ``uvicorn`` ตรง ๆ บนเครื่องนี้)
    """
    monkeypatch.setattr(db_module, "loop_is_incompatible", lambda loop: True)

    with pytest.raises(RuntimeError, match="run.py"):
        await Database("postgresql://u:p@127.0.0.1:5432/db").open()


async def test_connect_explains_how_to_fix_the_loop(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(db_module, "loop_is_incompatible", lambda loop: True)

    with caplog.at_level(logging.ERROR, logger="app.db"):
        assert await connect(make_settings()) is None

    assert "run.py" in caplog.text


def test_loop_check_ignores_non_windows() -> None:
    """
    Linux/macOS ใช้ Selector อยู่แล้ว — ห้ามไปบล็อกการต่อ DB บน production
    """

    class ProactorEventLoop:
        pass

    assert loop_is_incompatible(ProactorEventLoop(), "linux") is False
    assert loop_is_incompatible(ProactorEventLoop(), "darwin") is False
    assert loop_is_incompatible(ProactorEventLoop(), "win32") is True


def test_runner_uses_default_loop_on_other_platforms() -> None:
    """
    Linux/macOS ใช้ Selector อยู่แล้ว — ไม่ต้องยุ่งกับ loop factory
    """
    import run

    assert run.loop_factory("linux") is None
    assert run.loop_factory("darwin") is None


def test_runner_forces_selector_loop_on_windows() -> None:
    """
    uvicorn บังคับ ``ProactorEventLoop`` บน Windows ผ่าน loop factory ของตัวเอง
    (ตั้ง event loop policy ไม่ช่วย — ทดลองแล้ว) → ``run.py`` ต้องส่ง
    factory ของตัวเองให้ ``asyncio.Runner``
    """
    import run

    assert run.loop_factory("win32") is asyncio.SelectorEventLoop


# ── Protocol ────────────────────────────────────────────────────────────────


def test_fake_database_satisfies_the_protocol() -> None:
    """
    ยืนยันว่า fake ในเทสมี method ครบตามที่ repository ต้องการ

    ถ้าวันหนึ่งเพิ่ม method ใน :class:`SupportsQuery` แล้วลืมเพิ่มใน fake
    เทสนี้จะจับได้ก่อนที่เทสอื่นจะ fail แบบสับสน
    """
    assert isinstance(FakeDatabase(), SupportsQuery)


def test_real_database_satisfies_the_protocol() -> None:
    assert isinstance(Database("postgresql://u:p@127.0.0.1:5432/db"), SupportsQuery)


def test_only_the_real_database_can_write() -> None:
    """
    :class:`SupportsExecute` แยกจาก :class:`SupportsQuery` โดยตั้งใจ

    fake ที่อ่านอย่างเดียวต้อง **ไม่** ผ่าน ``SupportsExecute`` เพื่อให้ชั้นที่
    ต้องเขียนจริง ๆ ประกาศ type ให้ตรง แล้วส่ง fake อ่านอย่างเดียวเข้าไปไม่ได้
    """
    assert isinstance(Database("postgresql://u:p@127.0.0.1:5432/db"), SupportsExecute)
    assert not isinstance(FakeDatabase(), SupportsExecute)


# ── ทางเขียน (execute) ───────────────────────────────────────────────────────
#
# บั๊กที่เทสชุดนี้กัน: เดิม ``app.db`` มีแค่ ``fetch_all``/``fetch_one`` ซึ่งเรียก
# ``fetchall()`` เสมอ → ``INSERT``/``UPDATE``/``DELETE`` ที่ไม่มี ``RETURNING``
# ทำให้ psycopg โยน ``ProgrammingError: the last operation didn't produce
# records`` **หลังคำสั่งทำงานไปแล้ว** แล้ว ``pool.connection()`` เห็น exception
# → rollback ทั้ง transaction → เขียนไม่ลงเลยแม้คำสั่งจะสำเร็จ


class RecordingCursor:
    """cursor ปลอมที่นับว่ามีใครไปเรียก ``fetch*`` หรือเปล่า"""

    def __init__(self, rowcount: int = 1) -> None:
        self.rowcount = rowcount
        self.executed: list[tuple] = []
        self.fetch_calls = 0
        self.row_factory: object | None = None

    async def execute(self, sql: str, params=None) -> None:
        self.executed.append((sql, params))

    async def fetchall(self) -> list[dict]:
        self.fetch_calls += 1
        return []

    async def fetchone(self) -> dict | None:
        self.fetch_calls += 1
        return None

    async def __aenter__(self) -> "RecordingCursor":
        return self

    async def __aexit__(self, *exc) -> bool:
        return False


class RecordingConnection:
    def __init__(self, cursor: RecordingCursor) -> None:
        self._cursor = cursor
        self.cursor_kwargs: dict = {}

    def cursor(self, **kwargs):
        self.cursor_kwargs = kwargs
        self._cursor.row_factory = kwargs.get("row_factory")
        return self._cursor

    async def __aenter__(self) -> "RecordingConnection":
        return self

    async def __aexit__(self, *exc) -> bool:
        return False


def working_database(cursor: RecordingCursor) -> Database:
    """
    :class:`Database` ที่มี pool ใช้งานได้ — แทน ``_pool`` ตรง ๆ

    ไม่ผ่าน :meth:`Database.open` เพราะไม่ต้องทดสอบการเปิด pool ซ้ำ
    (มีเทสของมันอยู่แล้วข้างบน) และการยัด ``_pool`` ตรง ๆ ทำให้เทสนี้
    เหลือเรื่องเดียวคือ "ใช้ cursor ถูกวิธีไหม"
    """
    database = Database("postgresql://u:p@127.0.0.1:5432/db")
    connection = RecordingConnection(cursor)
    database._pool = types.SimpleNamespace(connection=lambda: connection)
    database._row_factory = object()
    return database


async def test_execute_does_not_fetch_rows() -> None:
    """หัวใจของบั๊ก: ``INSERT`` ที่ไม่มี ``RETURNING`` ต้องไม่มีใครไปเรียก fetch"""
    cursor = RecordingCursor(rowcount=1)
    database = working_database(cursor)

    affected = await database.execute(
        "INSERT INTO chat_logs (user_id, answered_by) VALUES (%s, %s)", (1, "search")
    )

    assert affected == 1
    assert cursor.fetch_calls == 0, "execute() ต้องไม่เรียก fetchall/fetchone"
    assert cursor.executed == [
        (
            "INSERT INTO chat_logs (user_id, answered_by) VALUES (%s, %s)",
            (1, "search"),
        )
    ]


async def test_execute_uses_a_plain_cursor() -> None:
    """
    ไม่ต้องใส่ ``row_factory`` ให้ทางเขียน — ไม่มีแถวจะแปลง

    เช็คไว้เพราะถ้าเผลอ copy จาก ``fetch_all`` มาจะได้ ``dict_row`` ติดมาด้วย
    ซึ่งไม่ผิดแต่บอกเจตนาผิด
    """
    cursor = RecordingCursor()
    database = working_database(cursor)
    connection = database._pool.connection()

    await database.execute("DELETE FROM chat_logs")

    assert connection.cursor_kwargs == {}


async def test_execute_passes_through_rowcount_minus_one() -> None:
    """
    ``rowcount`` เป็น ``-1`` ได้เมื่อ driver บอกจำนวนไม่ได้ (เช่น DDL)
    ต้องส่งค่าต่อไปตรง ๆ ไม่ใช่แปลงเป็น 0 ซึ่งอ่านเหมือน "ไม่มีอะไรเปลี่ยน"
    """
    database = working_database(RecordingCursor(rowcount=-1))

    assert await database.execute("CREATE TEMP TABLE t (id int)") == -1


async def test_fetch_all_still_fetches() -> None:
    """คู่เทียบ — ยืนยันว่าแยกสองทางจริง ไม่ได้ปิด fetch ทั้งไฟล์"""
    cursor = RecordingCursor()
    database = working_database(cursor)

    assert await database.fetch_all("SELECT 1") == []
    assert cursor.fetch_calls == 1


async def test_execute_before_open_raises_readable_error() -> None:
    database = Database("postgresql://u:p@127.0.0.1:5432/db")

    with pytest.raises(RuntimeError, match="open"):
        await database.execute("DELETE FROM chat_logs")
