"""
เทส repository — SQL ของชั้นที่ 1

Postgres ยังรันบนเครื่อง dev ไม่ได้ (Docker ติด WSL2) จึงแยกเทสเป็นสองด้าน
ให้ครอบสิ่งที่ตรวจได้จริงโดยไม่มี DB:

1. **SQL ถูกต้องและอ้างตารางที่มีจริง** — parse ด้วย ``sqlglot`` แล้วเทียบชื่อ
   ตารางกับ migration ทุกไฟล์ (จับ typo เช่น ``document`` vs ``documents``
   ที่ปกติจะรู้ตัวตอนรัน query จริงเท่านั้น)
2. **ส่ง parameter ถูกตำแหน่ง และรับผลลัพธ์ว่างได้** — เทสด้วย
   :class:`tests.helpers.FakeDatabase`

สิ่งที่ยังเทสไม่ได้และต้องรันกับ Postgres จริงภายหลัง: index ถูกใช้จริงไหม,
ผลของ ``similarity()`` กับข้อความไทย, และ ``ON CONFLICT`` ของ seed
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import sqlglot
from sqlglot import exp

from app import repository as repo
from app.config import REPO_ROOT

from .helpers import FakeDatabase

MIGRATIONS_DIR = Path(REPO_ROOT, "db", "migrations")


def schema_tables() -> set[str]:
    """ชื่อตารางจาก **ทุก migration** (001_init.sql, 002_ai_sessions.sql, ...)"""
    tables: set[str] = set()
    for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
        sql = migration.read_text(encoding="utf-8")
        tables.update(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?(\w+)", sql))
    return tables


def normalize(sql: str) -> str:
    """
    ทำให้ SQL ของ psycopg parse ได้

    * ``%s`` เป็น placeholder ของ psycopg → แทนด้วยค่าคงที่
    * ``%%`` คือ ``%`` ตัวจริง (ตัวดำเนินการ similarity ของ pg_trgm)
      ที่ต้อง escape เพราะ psycopg ใช้ ``%`` เป็นสัญลักษณ์พิเศษ
    """
    return sql.replace("%s", "1").replace("%%", "%")


# ── SQL ถูกต้องเชิงโครงสร้าง ────────────────────────────────────────────────


def test_every_query_is_registered() -> None:
    """
    ทุกค่าคงที่ ``SQL_*`` ต้องอยู่ใน ``ALL_QUERIES`` ไม่งั้นเทสข้างล่างจะข้ามไป
    (เพิ่ม query ใหม่แล้วลืมลงทะเบียน = ไม่มีใครตรวจ SQL นั้นเลย)
    """
    declared = {
        name for name in dir(repo) if name.startswith("SQL_") and name != "SQL_"
    }
    assert declared == set(repo.ALL_QUERIES)


@pytest.mark.parametrize("name", sorted(repo.ALL_QUERIES))
def test_query_parses_as_postgres(name: str) -> None:
    tree = sqlglot.parse_one(normalize(repo.ALL_QUERIES[name]), dialect="postgres")
    assert tree is not None, f"{name} parse ไม่ได้"


def cte_names(tree: exp.Expression) -> set[str]:
    """
    ชื่อ CTE (``WITH x AS (...)``) ในคิวรี

    ต้องหักออกก่อนเทียบกับตารางจริง ไม่งั้นคิวรีที่ใช้ CTE จะถูกมองว่าอ้างตาราง
    ที่ไม่มีใน schema (เจอกับ ``SQL_REPLACE_COMPLETED_COURSES`` ซึ่งใช้ CTE
    ชื่อ incoming/removed/added เพื่อแทนที่ทั้งชุดใน statement เดียว)
    """
    return {cte.alias_or_name for cte in tree.find_all(exp.CTE)}


@pytest.mark.parametrize("name", sorted(repo.ALL_QUERIES))
def test_query_only_uses_existing_tables(name: str) -> None:
    """ชื่อตารางต้องมีอยู่ใน migration จริง"""
    tree = sqlglot.parse_one(normalize(repo.ALL_QUERIES[name]), dialect="postgres")
    used = {table.name for table in tree.find_all(exp.Table)}
    unknown = used - schema_tables() - cte_names(tree)

    assert not unknown, f"{name} อ้างตารางที่ไม่มีใน migration: {sorted(unknown)}"


@pytest.mark.parametrize("name", sorted(repo.ALL_QUERIES))
def test_query_has_no_string_interpolation(name: str) -> None:
    """
    ค่าจากผู้ใช้ต้องเข้ามาทาง ``%s`` เท่านั้น — ห้าม f-string/format

    ถ้ามี ``{`` อยู่ใน SQL แปลว่ามีคนเผลอเขียน f-string ซึ่งเปิดช่อง SQL injection
    """
    assert "{" not in repo.ALL_QUERIES[name]


def test_document_queries_exclude_dead_links_and_staff_docs() -> None:
    """
    ส่งลิงก์ตายให้นักศึกษาแย่กว่าไม่ส่ง (32 ฉบับ เข้าได้จริง 31)
    และเอกสารของเจ้าหน้าที่ไม่ควรโผล่ในคำตอบของนักศึกษา
    """
    for name in ("SQL_DOCUMENT_CATEGORIES", "SQL_DOCUMENTS_IN_CATEGORY", "SQL_SEARCH_DOCUMENTS"):
        sql = repo.ALL_QUERIES[name]
        assert "audience = 'student'" in sql, name
        assert "is_available" in sql, name


# ── parameter + การรับผลลัพธ์ ───────────────────────────────────────────────


async def test_documents_in_category_passes_category_and_limit() -> None:
    db = FakeDatabase()
    await repo.documents_in_category(db, "loan", limit=3)

    assert db.params_for("WHERE category = %s") == ("loan", 3)


async def test_search_documents_repeats_keyword_for_every_placeholder() -> None:
    """
    query นี้ใช้คำค้น **3 ครั้ง** (word_similarity 2 ทิศทางแรก + ทิศทางที่สอง)
    แล้วปิดท้ายด้วยเกณฑ์คะแนนกับ limit — ถ้าส่งไม่ครบ psycopg จะ error
    "not enough arguments"

    เทสนับจาก ``%s`` ในตัว SQL ตรง ๆ เพื่อให้แก้ query แล้วลืมแก้ params ไม่ผ่าน
    """
    db = FakeDatabase()
    await repo.search_documents(db, "ดรอปเรียน", limit=5)

    params = db.params_for("word_similarity")
    assert params == (
        "ดรอปเรียน",
        "ดรอปเรียน",
        "ดรอปเรียน",
        repo.SEARCH_MIN_SCORE,
        5,
    )
    assert repo.SQL_SEARCH_DOCUMENTS.count("%s") == len(params)


async def test_search_instructors_repeats_name_for_every_placeholder() -> None:
    """เหตุผลเดียวกับเอกสาร แต่ใช้ชื่อ 2 ครั้ง (ไม่มีคอลัมน์ title แยก)"""
    db = FakeDatabase()
    await repo.search_instructors(db, "ธรัช", limit=3)

    params = db.params_for("word_similarity")
    assert params == ("ธรัช", "ธรัช", repo.SEARCH_MIN_SCORE, 3)
    assert repo.SQL_SEARCH_INSTRUCTORS.count("%s") == len(params)


async def test_search_min_score_is_overridable_but_defaults_to_the_measured_value() -> None:
    """
    เกณฑ์ต้องส่งเป็น parameter ไม่ใช่พึ่ง GUC ``pg_trgm.word_similarity_threshold``
    เพราะ GUC เป็นค่า **ต่อ session** → กับ connection pool จะได้ผลไม่คงที่
    """
    db = FakeDatabase()
    await repo.search_documents(db, "กยศ", min_score=0.1)

    assert db.params_for("word_similarity")[3] == 0.1
    assert repo.SEARCH_MIN_SCORE == 0.6


async def test_instructors_in_group_passes_group_and_limit() -> None:
    db = FakeDatabase()
    await repo.instructors_in_group(db, "สาขาวิชาเทคโนโลยีมัลติมีเดีย", limit=12)

    assert db.params_for("instructor_affiliations") == (
        "สาขาวิชาเทคโนโลยีมัลติมีเดีย",
        12,
    )


async def test_planning_coverage_repeats_program_code_three_times() -> None:
    db = FakeDatabase()
    await repo.planning_coverage(db, "643170151")

    params = db.params_for("curriculum_rules")
    assert params == ("643170151",) * 3
    assert repo.SQL_PLANNING_COVERAGE.count("%s") == len(params)


async def test_contact_coverage_defaults_when_row_missing() -> None:
    """
    fetch_one คืน ``None`` ได้ (ตารางว่าง) — ต้องได้ dict ที่มี key ครบ
    ไม่ใช่ ``None`` ที่จะทำให้ชั้นแสดงผลพัง
    """
    coverage = await repo.instructor_contact_coverage(FakeDatabase())

    assert coverage == {"total": 0, "with_email": 0, "with_phone": 0, "with_room": 0}


async def test_course_by_code_returns_none_when_not_found() -> None:
    assert await repo.course_by_code(FakeDatabase(), "9999999") is None


async def test_course_by_code_returns_row() -> None:
    db = FakeDatabase({"FROM courses": {"course_code": "7010102", "name_th": "วิชาทดสอบ"}})
    course = await repo.course_by_code(db, "7010102")

    assert course is not None and course["name_th"] == "วิชาทดสอบ"
    assert db.params_for("FROM courses") == ("7010102",)


async def test_list_queries_return_empty_list_not_none() -> None:
    """
    handler เช็คด้วย ``if not rows`` — ถ้าได้ ``None`` แทน ``[]`` จะยังผ่าน
    แต่ถ้ามีใครวนลูปทันทีจะพัง จึงล็อกให้เป็นลิสต์เสมอ
    """
    db = FakeDatabase()

    assert await repo.document_categories(db) == []
    assert await repo.instructor_groups(db) == []
    assert await repo.offerings_for_course(db, "7010102") == []
    assert await repo.search_instructors(db, "สมชาย") == []
