"""
ชั้นเชื่อมต่อฐานข้อมูล — psycopg 3 + connection pool (async)

**ทำไมต้องมี pool**: FastAPI รับหลาย request พร้อมกัน ถ้าเปิด connection ใหม่
ทุกครั้งจะช้า (TCP + auth ทุกรอบ) และ Postgres มี ``max_connections`` จำกัด
บน free tier ของ Supabase/Neon ยิ่งน้อย → เปิดค้างไว้ไม่กี่ตัวแล้วหมุนใช้

**ทำไมไม่ใช้ ORM**: query ในโปรเจกต์นี้ต้องใช้ของเฉพาะ Postgres
(``pgvector`` cosine distance, ``pg_trgm`` similarity, ``FILTER (WHERE ...)``)
เขียน SQL ตรง ๆ อ่านง่ายกว่าและคุมได้ว่าใช้ index ตัวไหน

**สถานะ**: รันกับ Postgres 17 + pgvector จริงแล้ว (ดู ``tests/integration/``)
โครงสร้างยังคงแยกเป็น Protocol ไว้:

* ทุกอย่างคุยผ่าน :class:`SupportsQuery` → เทสด้วย fake ได้ทั้งชั้น
* ``database_url`` ว่าง หรือต่อ DB ไม่ได้ **ตอนสตาร์ท** → แอปยังขึ้นได้
  แล้วบอทตอบว่า "ยังไม่มีข้อมูล" แทนที่จะพังทั้งระบบ

**ข้อควรรู้**: คำสัญญาข้อหลังจริงแค่ตอนสตาร์ท ถ้า DB ล่ม *กลาง* บทสนทนา
query จะโยน exception ออกมา — คนเรียกต้องดักเอง (``app.router`` ดักไว้ที่
``_guard`` แล้ว) ไม่ใช่หน้าที่ของชั้นนี้ที่จะกลืน error เพราะการกลืนตรงนี้
จะทำให้แยกไม่ออกว่า "ไม่มีข้อมูล" กับ "ถามฐานข้อมูลไม่ได้"
"""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any, Protocol, Sequence, runtime_checkable

log = logging.getLogger("app.db")

# ค่า default ของ pool — ตั้งไว้ต่ำเพราะ free tier ให้ connection น้อย
DEFAULT_MIN_SIZE = 1
DEFAULT_MAX_SIZE = 4
DEFAULT_CONNECT_TIMEOUT = 10.0

WINDOWS_LOOP_HINT = (
    "psycopg async ใช้กับ ProactorEventLoop (ค่า default ของ Windows) ไม่ได้ — "
    "ให้รันเซิร์ฟเวอร์ด้วย `python run.py` (ตั้ง SelectorEventLoop ไว้ให้แล้ว) "
    "แทน `uvicorn app.main:app` ตรง ๆ"
)


def loop_is_incompatible(loop: object, platform: str = sys.platform) -> bool:
    """
    เช็คว่า event loop ที่กำลังรันใช้กับ psycopg async ได้ไหม

    บน Windows ค่า default คือ ``ProactorEventLoop`` ซึ่ง **ไม่มี**
    ``add_reader``/``add_writer`` ที่ psycopg ต้องใช้ → ต้องเป็น
    ``SelectorEventLoop`` แทน (ดู :mod:`run`)

    ดักไว้เองเพื่อให้ error อ่านรู้เรื่องทันที ไม่ใช่รอ pool timeout 10 วินาที
    แล้วได้ข้อความจาก psycopg ที่ไม่บอกว่าต้องแก้ที่ไหน

    >>> class ProactorEventLoop: pass
    >>> loop_is_incompatible(ProactorEventLoop(), 'win32')
    True
    >>> class SelectorEventLoop: pass
    >>> loop_is_incompatible(SelectorEventLoop(), 'win32')
    False
    >>> loop_is_incompatible(ProactorEventLoop(), 'linux')
    False
    """
    if not platform.startswith("win"):
        return False
    return type(loop).__name__ == "ProactorEventLoop"


@runtime_checkable
class SupportsQuery(Protocol):
    """
    สัญญาที่ชั้น repository ต้องการจากฐานข้อมูล

    แยกเป็น Protocol เพื่อให้เทสส่ง fake เข้าไปได้ โดยไม่ต้องมี Postgres
    (และภายหลังจะเปลี่ยน driver ก็ไม่ต้องแก้ repository)
    """

    async def fetch_all(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> list[dict]: ...

    async def fetch_one(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> dict | None: ...


@runtime_checkable
class SupportsExecute(SupportsQuery, Protocol):
    """
    สัญญาสำหรับ **ทางเขียน** (``INSERT`` / ``UPDATE`` / ``DELETE``)

    แยกออกจาก :class:`SupportsQuery` โดยตั้งใจ: ชั้น repository ที่อ่านอย่างเดียว
    ไม่ควรได้สิทธิ์เขียน และ fake ในเทสเดิมที่มีแค่ ``fetch_*`` ยังใช้ได้ต่อ
    ไม่ต้องแก้ทั้งไฟล์
    """

    async def execute(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> int: ...


class Database:
    """
    ห่อ ``psycopg_pool.AsyncConnectionPool`` เท่าที่ใช้

    import ``psycopg`` แบบ lazy (ตอน :meth:`open`) เพื่อให้ import โมดูลนี้
    ได้โดยไม่ต้องติดตั้ง driver — สำคัญตอนรันเทสที่ไม่แตะ DB
    """

    def __init__(
        self,
        dsn: str,
        *,
        min_size: int = DEFAULT_MIN_SIZE,
        max_size: int = DEFAULT_MAX_SIZE,
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
    ) -> None:
        if not dsn:
            raise ValueError("ต้องระบุ DATABASE_URL")
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._connect_timeout = connect_timeout
        self._pool: Any | None = None
        self._row_factory: Any | None = None

    # ── วงจรชีวิต ───────────────────────────────────────────────────────────

    async def open(self) -> None:
        """
        เปิด pool และรอให้ต่อได้จริงก่อนคืนค่า

        ``wait=True`` สำคัญ: ถ้า DSN ผิดหรือ DB ยังไม่ขึ้น เราอยากรู้ตอนสตาร์ท
        ไม่ใช่ตอน user ยิงคำถามเข้ามาแล้วรอ timeout
        """
        if loop_is_incompatible(asyncio.get_running_loop()):
            raise RuntimeError(WINDOWS_LOOP_HINT)

        from psycopg.rows import dict_row
        from psycopg_pool import AsyncConnectionPool

        self._row_factory = dict_row
        pool = AsyncConnectionPool(
            conninfo=self._dsn,
            min_size=self._min_size,
            max_size=self._max_size,
            # ตรวจ connection ก่อนส่งให้ผู้ใช้ — กัน connection ค้างหลัง DB restart
            check=AsyncConnectionPool.check_connection,
            open=False,
        )
        try:
            await pool.open(wait=True, timeout=self._connect_timeout)
        except BaseException:
            # ปิด pool ที่เปิดค้างไว้ ไม่งั้น worker task จะวน retry ต่อไป
            # ตลอดอายุ process
            #
            # กรณี PoolTimeout psycopg ปิดให้เองอยู่แล้วใน ``wait()`` และ
            # ``close()`` เป็น idempotent → เรียกซ้ำได้ไม่มีผลข้างเคียง
            # แต่ทางที่ไม่ใช่ timeout (เช่น DSN ผิดรูป) ไม่มีใครปิดให้
            await pool.close(timeout=1.0)
            raise

        self._pool = pool
        log.info(
            "ต่อฐานข้อมูลได้ (pool %d-%d connection)", self._min_size, self._max_size
        )

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            log.info("ปิด connection pool")

    @property
    def is_open(self) -> bool:
        return self._pool is not None

    # ── query ───────────────────────────────────────────────────────────────

    async def fetch_all(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> list[dict]:
        pool = self._require_pool()
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=self._row_factory) as cur:
                await cur.execute(sql, params)
                return list(await cur.fetchall())

    async def fetch_one(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> dict | None:
        pool = self._require_pool()
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=self._row_factory) as cur:
                await cur.execute(sql, params)
                return await cur.fetchone()

    async def execute(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> int:
        """
        รันคำสั่งที่ **ไม่คืนแถว** แล้วคืนจำนวนแถวที่กระทบ

        ต้องแยกจาก :meth:`fetch_all` เพราะ ``fetch_all`` เรียก ``fetchall()``
        เสมอ ซึ่ง ``INSERT``/``UPDATE``/``DELETE`` ที่ไม่มี ``RETURNING``
        ทำให้ psycopg โยน ``ProgrammingError: the last operation didn't
        produce records`` **หลังคำสั่งทำงานไปแล้ว** แล้ว ``pool.connection()``
        เห็น exception → rollback ทั้ง transaction → เขียนไม่ลงเลย

        ``pool.connection()`` commit ให้เองตอนออกจาก context ถ้าไม่มี exception
        ถ้าต้องการค่าที่เขียนกลับมาด้วย ให้ใส่ ``RETURNING`` แล้วเรียก
        :meth:`fetch_one` แทน

        คืน ``cursor.rowcount`` — ``-1`` หมายถึง driver บอกจำนวนไม่ได้
        """
        pool = self._require_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                return cur.rowcount

    async def healthy(self) -> bool:
        """
        ใช้ใน ``/health`` — ต่อได้จริงไหม ไม่ใช่แค่ "ตั้งค่า DATABASE_URL แล้ว"

        ไม่ให้ error หลุดออกไป เพราะ health check ต้องตอบได้เสมอ
        """
        if self._pool is None:
            return False
        try:
            row = await self.fetch_one("SELECT 1 AS ok")
            return bool(row and row.get("ok") == 1)
        except Exception as exc:  # pragma: no cover - ต้องมี DB จริงจะทดสอบได้
            log.warning("ตรวจสุขภาพฐานข้อมูลไม่ผ่าน: %s", exc)
            return False

    def _require_pool(self) -> Any:
        if self._pool is None:
            raise RuntimeError("ยังไม่ได้เปิด connection pool (เรียก open() ก่อน)")
        return self._pool


async def connect(settings: Any) -> Database | None:
    """
    สร้าง :class:`Database` จาก settings — คืน ``None`` ถ้าต่อไม่ได้

    เจตนา: **ห้ามทำให้แอปสตาร์ทไม่ขึ้นเพราะ DB** ฟีเจอร์ที่ไม่ต้องใช้ DB
    (verify webhook, ตอบเมนู, LIFF login) ต้องทำงานได้ต่อ
    ส่วนที่ต้องใช้ DB จะตอบว่า "ยังไม่มีข้อมูล" ซึ่งดีกว่าเงียบหรือ 500
    """
    if not settings.database_url:
        log.warning("ยังไม่ได้ตั้ง DATABASE_URL — ฟีเจอร์ที่ต้องใช้ฐานข้อมูลจะตอบว่าไม่มีข้อมูล")
        return None

    database = Database(
        settings.database_url,
        connect_timeout=settings.db_connect_timeout_seconds,
    )
    try:
        await database.open()
    except Exception as exc:
        log.error("ต่อฐานข้อมูลไม่ได้ (%s: %s) — แอปจะทำงานต่อแบบไม่มี DB", type(exc).__name__, exc)
        return None
    return database
