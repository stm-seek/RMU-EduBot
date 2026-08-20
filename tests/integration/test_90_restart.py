"""
เทสว่า connection pool ฟื้นตัวเองได้หลังฐานข้อมูลรีสตาร์ต

นี่คือข้อที่สองใน ``memory/postgres-never-run-for-real.md`` ที่ระบุว่ายังพิสูจน์
ไม่ได้ — ``app.db.Database.open()`` ส่ง ``check=AsyncConnectionPool.check_connection``
ให้ pool เพื่อ "กัน connection ค้างหลัง DB restart" ซึ่งเป็นคำที่ยังไม่มีใครทดสอบ

**ทำไมไฟล์นี้ชื่อขึ้นด้วย 90**: pytest เก็บไฟล์ตามลำดับชื่อ และเทสในนี้ทำให้
connection ทั้ง pool ตาย ต้องรันหลังไฟล์อื่นให้หมด (``live_db`` เป็น
fixture ระดับ session — pool ตัวเดียวกันทั้งชุด ซึ่งจงใจ เพราะอยากพิสูจน์ว่า
**pool ที่แอปใช้อยู่จริง** ฟื้นได้ ไม่ใช่ pool ใหม่ที่เพิ่งสร้าง)

รีสตาร์ตด้วย ``docker compose restart db`` เท่านั้น — **ห้าม ``down``/``down -v``**
เพราะ volume จะหายและต้อง re-seed ใหม่หลายนาที (fixture ``docker_compose``
บล็อกคำสั่งพวกนั้นไว้แล้ว)
"""

from __future__ import annotations

import asyncio
import subprocess
import time
from typing import Any, Callable

import pytest

from app import repository as repo
from app.db import DEFAULT_MAX_SIZE, Database

pytestmark = [pytest.mark.integration, pytest.mark.restart]

# เวลารอสูงสุดให้ pool กลับมาใช้ได้ (Postgres ใช้เวลาสตาร์ท + pool reconnect)
RECOVERY_DEADLINE_SECONDS = 60.0


def _backend_pids(db: Database, run: Callable[..., Any]) -> set[int]:
    """PID ของ backend ทุกตัวที่ pool ถืออยู่ — ยิงพร้อมกันให้ครบทุก connection"""

    async def body() -> list[dict]:
        return await asyncio.gather(
            *(
                db.fetch_one("SELECT pg_backend_pid() AS pid, pg_sleep(0.05)")
                for _ in range(DEFAULT_MAX_SIZE * 2)
            )
        )

    return {row["pid"] for row in run(body())}


def test_check_connection_recovers_after_database_restart(
    live_db: Database,
    run: Callable[..., Any],
    docker_compose: Callable[[list[str]], "subprocess.CompletedProcess[str]"],
) -> None:
    """
    รีสตาร์ต container แล้ว pool เดิมต้องกลับมาใช้ได้เอง ไม่ต้องรีสตาร์ตแอป

    ตรวจสามชั้น เพื่อไม่ให้ "ผ่าน" เพราะรีสตาร์ตไม่สำเร็จ:

    1. ``pg_postmaster_start_time()`` เปลี่ยน = Postgres ขึ้นใหม่จริง
    2. PID ของ backend ไม่ซ้ำกับก่อนรีสตาร์ตเลย = connection เดิมตายจริง
       และ pool ต่อใหม่จริง
    3. ``healthy()`` กลับมา ``True`` และข้อมูล seed ยังอยู่ (volume ไม่หาย)
    """
    before_start = run(live_db.fetch_one("SELECT pg_postmaster_start_time() AS t"))
    before_pids = _backend_pids(live_db, run)
    assert before_start is not None and before_pids

    result = docker_compose(["restart", "db"])
    assert result.returncode == 0, result.stderr or result.stdout

    started = time.monotonic()
    recovered = False
    while time.monotonic() - started < RECOVERY_DEADLINE_SECONDS:
        # healthy() กลืน exception ไว้เองอยู่แล้ว → ไม่ควรโยนอะไรออกมาทั้งช่วง DB ล่ม
        if run(live_db.healthy()):
            recovered = True
            break
        time.sleep(0.5)
    elapsed = time.monotonic() - started

    assert recovered, (
        f"pool ไม่ฟื้นภายใน {RECOVERY_DEADLINE_SECONDS} วินาที "
        "— ถ้าเจอเคสนี้ อย่าแก้ app/db.py ในงานนี้ ให้รายงานเป็นข้อค้นพบ"
    )

    after_start = run(live_db.fetch_one("SELECT pg_postmaster_start_time() AS t"))
    assert after_start is not None
    assert after_start["t"] > before_start["t"], "Postgres ไม่ได้รีสตาร์ตจริง"

    after_pids = _backend_pids(live_db, run)
    assert not (before_pids & after_pids), (
        f"ยังใช้ connection เดิมอยู่ ก่อน={sorted(before_pids)} หลัง={sorted(after_pids)}"
    )

    # ข้อมูลยังครบ = ใช้ restart ไม่ใช่ down -v
    documents = run(live_db.fetch_one("SELECT count(*) AS n FROM documents"))
    assert documents is not None and documents["n"] == 32

    print(f"\npool ฟื้นตัวใน {elapsed:.1f} วินาที (backend ใหม่หมดทั้ง pool)")


def test_repository_works_again_after_restart(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ต่อจากเทสข้างบน — query ของชั้นแอปต้องใช้ได้ตามปกติหลังฟื้น

    (pytest รันตามลำดับในไฟล์ เทสนี้จึงอยู่หลังเสมอ)
    """
    assert run(repo.latest_term(live_db)) == {
        "acad_year": 2568,
        "semester": 2,
        "offerings": 45,
    }
    assert len(run(repo.document_categories(live_db))) == 10

    async def concurrent() -> list[Any]:
        return await asyncio.gather(
            *(repo.instructor_contact_coverage(live_db) for _ in range(8))
        )

    coverage = run(concurrent())
    assert all(row["total"] == 28 for row in coverage)
