"""
เทส connection pool ของ ``app.db`` กับ Postgres จริง

สองข้อที่ ``memory/postgres-never-run-for-real.md`` ระบุว่า "ยังพิสูจน์ไม่ได้"
ข้อแรกอยู่ในไฟล์นี้ (pool รับงานพร้อมกันได้จริง) ข้อที่สองอยู่ใน
``test_90_restart.py`` (ฟื้นตัวหลัง DB รีสตาร์ต)

``FakeDatabase`` ทำงานแบบ synchronous ทีละคำสั่ง → พิสูจน์เรื่อง concurrency
ไม่ได้เลย และ ``max_size`` ของ pool ก็ไม่มีความหมายกับ mock
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

import pytest

from app import repository as repo
from app.config import get_settings
from app.db import DEFAULT_MAX_SIZE, Database

pytestmark = pytest.mark.integration

CONCURRENT = 24


def test_pool_serves_concurrent_queries(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ยิง 24 query พร้อมกันผ่าน pool เดียว — ต้องสำเร็จทุกตัวและได้ผลของตัวเอง

    ใส่ ``pg_sleep(0.05)`` ให้ query ค้างจริง เพื่อบังคับให้ pool ต้องแจก
    connection หลายตัวพร้อมกัน (ถ้ารันทีละตัวจะใช้เวลา >= 1.2 วินาที)
    """

    async def body() -> list[dict]:
        return await asyncio.gather(
            *(
                live_db.fetch_one(
                    "SELECT %s::int AS i, pg_backend_pid() AS pid, pg_sleep(0.05)",
                    (index,),
                )
                for index in range(CONCURRENT)
            )
        )

    rows = run(body())

    assert len(rows) == CONCURRENT
    assert [row["i"] for row in rows] == list(range(CONCURRENT)), "ผลสลับกันระหว่าง task"
    backends = {row["pid"] for row in rows}
    # ใช้หลาย connection จริง แต่ไม่เกิน max_size ที่ตั้งไว้
    assert 1 < len(backends) <= DEFAULT_MAX_SIZE, backends


def test_pool_does_not_exceed_max_size(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ``max_size`` ต้องเป็นเพดานจริงฝั่ง Postgres ไม่ใช่แค่ตัวเลขใน Python

    สำคัญกับ free tier ของ Neon/Supabase ที่ ``max_connections`` น้อย

    **ห้ามนับ ``pg_stat_activity`` ทั้งฐาน** — ฐานเดียวกันมี client อื่นต่ออยู่จริง
    (uvicorn ที่รันอยู่มี pool ของตัวเอง + psql ที่เปิดดูข้อมูล) เทสเดิมนับรวม
    แล้วแดงทั้งที่ pool ของเทสไม่ได้ทำอะไรผิด → นับเฉพาะ backend ของ pool นี้
    โดยเก็บ ``pg_backend_pid()`` ที่ query ของเราวิ่งอยู่จริง
    """

    async def body() -> tuple[set[int], list[dict]]:
        rows = await asyncio.gather(
            *(
                live_db.fetch_one("SELECT pg_backend_pid() AS pid, pg_sleep(0.05)")
                for _ in range(CONCURRENT)
            )
        )
        ours = {row["pid"] for row in rows}
        alive = await live_db.fetch_all(
            "SELECT pid FROM pg_stat_activity"
            " WHERE pid = ANY(%s) AND datname = current_database()"
            "   AND backend_type = 'client backend'",
            (sorted(ours),),
        )
        return ours, alive

    ours, alive = run(body())

    # 24 query พร้อมกันแต่ใช้ connection ไม่เกินเพดาน
    assert 1 < len(ours) <= DEFAULT_MAX_SIZE, ours
    # และ pid เหล่านั้นเป็น connection ฝั่งเซิร์ฟเวอร์จริง (ไม่ใช่ตัวเลขลอย ๆ)
    assert {row["pid"] for row in alive} == ours


def test_pool_serves_all_repository_functions_concurrently(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    เคสที่ใกล้ของจริงที่สุด: หลาย request ยิงคนละ handler พร้อมกัน

    ``app.main.process_event`` รันเป็น background task → หลายคนกดเมนูพร้อมกัน
    จะเข้ามาแบบนี้เป๊ะ ๆ
    """
    program = get_settings().default_program_code

    async def body() -> list[Any]:
        return await asyncio.gather(
            repo.document_categories(live_db),
            repo.documents_in_category(live_db, "loan"),
            repo.search_documents(live_db, "หนังสือรับรองรายได้ครอบครัว"),
            repo.instructor_groups(live_db),
            repo.instructors_in_group(live_db, "สาขาเทคโนโลยีสารสนเทศ (IT)"),
            repo.search_instructors(live_db, "ภานุรักษ์"),
            repo.instructor_contact_coverage(live_db),
            repo.planning_coverage(live_db, program),
            repo.course_by_code(live_db, "1109902"),
            repo.offerings_for_course(live_db, "1109902"),
            repo.latest_term(live_db),
        )

    results = run(body())

    assert len(results) == 11
    assert all(result for result in results), "มีฟังก์ชันที่คืนค่าว่างระหว่างรันพร้อมกัน"
    assert results[6]["total"] == 28
    assert results[10] == {"acad_year": 2568, "semester": 2, "offerings": 45}


def test_fetch_all_really_returns_dict_rows(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ``row_factory=dict_row`` ต้องมีผลจริง — ทุก handler ใช้ ``row['ชื่อคอลัมน์']``

    ถ้าลืมตั้ง psycopg จะคืน tuple แล้วโค้ดทั้งชั้นพังด้วย ``TypeError``
    """
    rows = run(live_db.fetch_all("SELECT 1 AS a, 'ไทย' AS b"))

    assert rows == [{"a": 1, "b": "ไทย"}]
    assert isinstance(rows[0], dict)


def test_failed_query_does_not_poison_the_pool(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    query พังต้องไม่ทำให้ connection ที่คืนเข้า pool ใช้ต่อไม่ได้

    ถ้า transaction ที่ abort ไม่ถูก rollback ก่อนคืน connection คำสั่งถัดไป
    จะได้ ``current transaction is aborted`` — pool ของ psycopg จัดการให้เอง
    แต่เป็นสิ่งที่ mock ยืนยันไม่ได้ และเป็นทางที่แอปเดินจริงเมื่อ SQL ผิด
    """
    with pytest.raises(Exception) as failure:
        run(live_db.fetch_one("SELECT * FROM ตารางที่ไม่มีอยู่"))
    assert "ตารางที่ไม่มีอยู่" in str(failure.value)

    # ยิงซ้ำหลาย ๆ ครั้งให้แน่ใจว่าได้ connection ตัวที่เพิ่งพังกลับมาด้วย
    async def body() -> list[dict]:
        return await asyncio.gather(
            *(live_db.fetch_one("SELECT 1 AS ok") for _ in range(DEFAULT_MAX_SIZE * 2))
        )

    assert run(body()) == [{"ok": 1}] * (DEFAULT_MAX_SIZE * 2)
    assert run(live_db.healthy()) is True


def test_write_commits_and_is_visible_to_another_connection(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """
    เขียนแล้ว commit จริงไหม — ``Database`` ไม่มีเมธอด ``commit()`` ให้เรียกเลย

    ``pool.connection()`` ของ psycopg commit ให้ตอนออกจาก context โดยปริยาย
    ถ้าไม่ใช่แบบนั้น ชั้นที่จะเขียน ``chat_logs``/``app_users`` ต่อจากนี้จะ
    "ดูเหมือนทำงาน" แต่ข้อมูลหายทุกครั้ง

    พิสูจน์ด้วยการอ่านจาก **connection อื่น** (บังคับให้ pool ใช้ตัวใหม่ด้วย
    การจับ connection ค้างไว้พร้อมกันหลายตัว) เขียนเสร็จแล้วต้องเห็นข้อมูล
    """
    payload = [{"title": "ระเบียบการลงทะเบียน", "url": "https://sci.rmu.ac.th/?p=1"}]

    inserted = run(
        live_db.fetch_one(
            "INSERT INTO chat_logs"
            " (user_id, message_text, answered_by, intent_key, confidence,"
            "  response_text, citations, latency_ms)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)"
            " RETURNING id",
            (
                test_user,
                "ขอแบบฟอร์มลาพักการเรียน",
                "rich_menu",
                "documents:registration",
                1.0,
                "เอกสารหมวดลงทะเบียน/เพิ่ม-ถอน (5 ฉบับ)",
                json.dumps(payload, ensure_ascii=False),
                42,
            ),
        )
    )
    assert inserted is not None

    async def read_from_every_connection() -> list[dict]:
        return await asyncio.gather(
            *(
                live_db.fetch_one(
                    "SELECT message_text, response_text, citations, confidence"
                    " FROM chat_logs WHERE id = %s",
                    (inserted["id"],),
                )
                for _ in range(DEFAULT_MAX_SIZE * 2)
            )
        )

    rows = run(read_from_every_connection())

    assert len(rows) == DEFAULT_MAX_SIZE * 2
    for row in rows:
        assert row["message_text"] == "ขอแบบฟอร์มลาพักการเรียน"
        assert row["response_text"].startswith("เอกสารหมวดลงทะเบียน")
        # jsonb กลับมาเป็น object ของ Python แล้ว ไม่ใช่สตริง
        assert row["citations"] == payload
        assert row["confidence"] == pytest.approx(1.0)


def test_concurrent_writes_all_land(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """
    เขียนพร้อมกัน 12 แถวผ่าน pool 4 connection — ต้องได้ครบ ไม่ชนกัน

    ``chat_logs`` คือทางที่จะบันทึกทุกบทสนทนา (ใช้วัดผลในธีสิส) ถ้าเขียนหาย
    ตอนคนใช้พร้อมกัน ข้อมูลวิจัยจะเพี้ยนแบบตรวจไม่เจอ
    """
    total = 12

    async def body() -> None:
        await asyncio.gather(
            *(
                live_db.fetch_all(
                    "INSERT INTO chat_logs (user_id, message_text, answered_by)"
                    " VALUES (%s, %s, %s) RETURNING id",
                    (test_user, f"คำถามที่ {index}", "rich_menu"),
                )
                for index in range(total)
            )
        )

    run(body())
    rows = run(
        live_db.fetch_all(
            "SELECT message_text FROM chat_logs WHERE user_id = %s ORDER BY id",
            (test_user,),
        )
    )

    assert len(rows) == total
    assert {row["message_text"] for row in rows} == {
        f"คำถามที่ {index}" for index in range(total)
    }


def test_write_without_returning_is_rejected(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """
    **บันทึกช่องว่างของ API ที่เจอกับ DB จริง** (ไม่ได้แก้ตามขอบเขตงาน)

    :class:`app.db.Database` มีแต่ ``fetch_all`` / ``fetch_one`` ซึ่งเรียก
    ``cursor.fetchall()`` เสมอ → ``INSERT``/``UPDATE``/``DELETE`` ที่ไม่มี
    ``RETURNING`` จะได้ ``psycopg.ProgrammingError: the last operation didn't
    produce records`` **หลังจากคำสั่งทำงานไปแล้ว** แล้ว ``pool.connection()``
    เห็น exception → rollback ทั้ง transaction

    ผลคือชั้นนี้ยัง **เขียนฐานข้อมูลไม่ได้เลย** ถ้าไม่เติม ``RETURNING`` เอง
    ซึ่งเป็นปัญหาแน่ ๆ ตอนทำ ``chat_logs`` (Requirement ข้อ 12: log ทุกบทสนทนา)
    ทางแก้ที่ควรทำ: เพิ่มเมธอด ``execute()`` ที่ไม่เรียก ``fetchall()``

    mock จับไม่ได้เพราะ ``FakeDatabase.fetch_all`` คืนลิสต์ว่างเฉย ๆ
    """
    with pytest.raises(Exception) as failure:
        run(
            live_db.fetch_all(
                "INSERT INTO chat_logs (user_id, message_text, answered_by)"
                " VALUES (%s, %s, %s)",
                (test_user, "แถวนี้จะไม่ถูกบันทึก", "rich_menu"),
            )
        )
    assert "didn't produce records" in str(failure.value)

    # ยืนยันว่า rollback จริง — แถวไม่ถูก commit
    left = run(
        live_db.fetch_one(
            "SELECT count(*) AS n FROM chat_logs WHERE user_id = %s", (test_user,)
        )
    )
    assert left is not None and left["n"] == 0


def test_foreign_key_cascade_cleans_child_rows(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """
    ``user_completed_courses`` ผูก ``ON DELETE CASCADE`` — ยืนยันกับ DB จริง

    เกี่ยวกับ PDPA: ถ้านักศึกษาขอลบบัญชี ต้องลบวิชาที่เคยรายงานไว้ตามไปด้วย
    (``chat_logs`` ตั้งเป็น ``SET NULL`` โดยเจตนา เพื่อเก็บสถิติแบบไม่ระบุตัวตน)
    """
    run(
        live_db.fetch_all(
            "INSERT INTO user_completed_courses (user_id, course_code, source)"
            " VALUES (%s, %s, %s) RETURNING id",
            (test_user, "1109902", "self_report"),
        )
    )
    run(
        live_db.fetch_all(
            "DELETE FROM app_users WHERE id = %s RETURNING id", (test_user,)
        )
    )

    left = run(
        live_db.fetch_one(
            "SELECT count(*) AS n FROM user_completed_courses WHERE user_id = %s",
            (test_user,),
        )
    )
    assert left is not None and left["n"] == 0

