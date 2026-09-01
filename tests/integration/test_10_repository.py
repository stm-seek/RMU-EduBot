"""
เทส ``app.repository`` ทั้ง 19 ฟังก์ชันกับ Postgres จริง + ข้อมูล seed จริง

ต่างจาก :mod:`tests.test_repository` (ที่ parse SQL ด้วย ``sqlglot`` + ยิง
``FakeDatabase``) ไฟล์นี้ยืนยัน **ค่าที่ออกมาจริง** ซึ่ง mock พิสูจน์ให้ไม่ได้:
ผลของ ``word_similarity()`` กับภาษาไทย, การเรียงลำดับที่ Postgres ทำ,
``LEFT JOIN`` ที่คืน ``NULL`` และ CHECK constraint ของ ``ai_sessions``

ค่าที่ hardcode ไว้ทั้งหมดมาจาก ``db/seed/002_seed_data.sql`` ถ้า seed เปลี่ยน
``test_00_smoke.py`` จะพังก่อนเป็นตัวบอก
"""

from __future__ import annotations

import inspect
import re
from typing import Any, Callable

import pytest

from app import ai_chat, repository as repo
from app.config import get_settings
from app.db import Database

pytestmark = pytest.mark.integration

# หมวดเอกสาร + จำนวน ตามลำดับที่ SQL_DOCUMENT_CATEGORIES คืนมา
# (count desc, category asc) — ตอนนี้เข้าได้ครบทุกฉบับ (รอบตรวจ 22 ส.ค. 2026
# เว็บที่เคยล่มอย่าง e-activity กลับมาแล้ว และเพิ่มปฏิทินสหกิจศึกษาในหมวด
# internship) ถ้ามีลิงก์ตายอีก ผลรวมตรงนี้จะน้อยกว่าแถวในตาราง
REAL_CATEGORIES = [
    ("loan", 12),
    ("registration", 5),
    ("internship", 4),
    ("curriculum", 3),
    ("exam_prep", 2),
    ("regulation", 2),
    ("activity", 1),
    ("calendar", 1),
    ("it_account", 1),
    ("scholarship", 1),
    ("staff", 1),
]

REAL_GROUPS = [
    ("สาขาเทคโนโลยีสารสนเทศ (IT)", 9),
    ("สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน (MTA)", 7),
    ("สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล (CTD)", 6),
    ("สาขาการจัดการนวัตกรรมดิจิทัล (MDI)", 5),
    ("ระดับปรัชญาดุษฎีบัณฑิต (ปร.ด.การจัดการเทคโนโลยี)", 3),
    ("ระดับปริญญามหาบัณฑิต (วท.ม.การจัดการเทคโนโลยี)", 3),
]

IT_GROUP = REAL_GROUPS[0][0]

# วิชาศึกษาทั่วไปที่เปิดหลายหมู่เรียนทุกเทอม — ใช้เทส offerings/limit/ordering
COURSE_WITH_MANY_OFFERINGS = "1109902"
# วิชาที่ไม่มีแถวใน offering_patterns → ทดสอบผล LEFT JOIN
COURSE_WITHOUT_PATTERN = "1109905"
COURSE_MISSING = "9999999"

# ── เอกสาร ──────────────────────────────────────────────────────────────────


def test_document_categories_matches_real_seed(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """หมวด + จำนวน + ลำดับ ต้องตรงกับข้อมูลจริงทั้งชุด"""
    rows = run(repo.document_categories(live_db))

    assert [(row["category"], row["total"]) for row in rows] == REAL_CATEGORIES


def test_document_categories_counts_every_row_when_links_are_alive(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ตาราง ``documents`` มี 33 แถว และรวมทุกหมวดต้องได้ 33 เท่ากัน

    ณ รอบตรวจ 22 ส.ค. 2026 ลิงก์เข้าได้ครบทุกฉบับ (``e-activity`` ที่เคยล่ม
    กลับมาแล้ว) ตัวกรองลิงก์ตายจึงไม่มีอะไรให้ตัดในชุดข้อมูลนี้ — ผลของตัวกรอง
    ยังมีเทสระดับ SQL ครอบคลุมใน ``tests/test_repository.py`` แยกไว้ ถ้าวันใด
    ลิงก์ตายอีกครั้ง ผลรวมตรงนี้จะมีค่าน้อยกว่าแถวในตาราง นั่นคือตัวกรองทำงาน
    """
    rows = run(repo.document_categories(live_db))
    total = sum(row["total"] for row in rows)
    table_rows = run(live_db.fetch_one("SELECT count(*) AS n FROM documents"))

    assert table_rows is not None and table_rows["n"] == 33
    assert total == 33


def test_documents_in_category_returns_real_rows(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(repo.documents_in_category(live_db, "registration"))

    assert len(rows) == 5
    assert set(rows[0]) == {"title", "url", "doc_type", "note"}
    # ORDER BY title — Postgres collation C.UTF-8 เรียงไทยแบบ code point
    assert [row["title"] for row in rows] == sorted(row["title"] for row in rows)
    assert rows[0]["title"] == "หน้ารวมเอกสาร/คำร้องทั่วไป คณะวิทยาศาสตร์และเทคโนโลยี"
    assert all(row["url"].startswith("https://") for row in rows)


def test_documents_in_category_unknown_returns_empty_list(
    live_db: Database, run: Callable[..., Any]
) -> None:
    assert run(repo.documents_in_category(live_db, "ไม่มีหมวดนี้")) == []


def test_documents_in_category_honours_limit(
    live_db: Database, run: Callable[..., Any]
) -> None:
    assert len(run(repo.documents_in_category(live_db, "loan", limit=3))) == 3


def test_default_limit_hides_two_loan_documents(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    **บันทึกบั๊กที่เจอกับข้อมูลจริง** (ไม่ได้แก้ตามคำสั่งของงานนี้)

    ``documents_in_category`` มี ``limit`` default = 10 และ
    ``app.router._documents_answer`` เรียกโดย **ไม่ส่ง limit**
    หมวด ``loan`` มีเอกสารใช้ได้ 12 ฉบับ → นักศึกษาเห็นแค่ 10
    และหัวข้อความยังพิมพ์ว่า "(10 ฉบับ)" ขัดกับเมนูหมวดที่บอก "12 ฉบับ"

    mock จับไม่ได้เพราะ ``FakeDatabase`` คืนไม่กี่แถว — ต้องมีข้อมูลจริงเท่านั้น
    """
    default = run(repo.documents_in_category(live_db, "loan"))
    everything = run(repo.documents_in_category(live_db, "loan", limit=1000))

    assert len(default) == 10, "ค่า default ของ limit เปลี่ยนไปแล้ว?"
    assert len(everything) == 12
    hidden = [row["title"] for row in everything if row not in default]
    assert hidden == [
        "111 ตัวอย่างการทำสัญญา กรอ. กับธนาคารอิสลาม",
        "หน้ารวมข้อมูลการกู้ยืมเงินเพื่อการศึกษา",
    ], hidden


@pytest.mark.xfail(
    strict=True,
    reason="บั๊ก: limit default 10 < จำนวนเอกสารจริงในหมวด loan (12) "
    "— เมนูบอก 12 แต่กดเข้าไปเห็น 10 (ยังไม่แก้ ตามขอบเขตงาน)",
)
def test_default_limit_should_cover_whole_category(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """เมื่อแก้บั๊กข้างบนแล้ว เทสนี้จะ XPASS → ให้ลบ marker ``xfail`` ออก"""
    counts = {row["category"]: row["total"] for row in run(repo.document_categories(live_db))}
    for category, total in counts.items():
        rows = run(repo.documents_in_category(live_db, category))
        assert len(rows) == total, f"หมวด {category}: เมนูบอก {total} แต่ได้ {len(rows)}"


# ── search_documents (pg_trgm) — ฟังก์ชันเสี่ยงสุด ยังไม่มีใครเรียกในแอป ─────


def test_search_documents_runs_at_all(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ข้อแรกสุด: ``%%`` ที่ escape ไว้ต้องกลายเป็นตัวดำเนินการ ``%`` ของ pg_trgm จริง

    ถ้า escape ผิด psycopg จะโยน error เรื่องจำนวน argument ไม่ตรง
    ซึ่งเป็นสิ่งเดียวที่ mock ยืนยันไม่ได้เลย
    """
    rows = run(repo.search_documents(live_db, "หนังสือรับรองรายได้ครอบครัว"))

    assert [row["title"] for row in rows] == [
        "102 หนังสือรับรองรายได้ครอบครัว (กยศ.)",
        "103 หนังสือรับรองรายได้ครอบครัว (กรอ.)",
    ]
    assert set(rows[0]) == {"title", "url", "category", "keywords", "score"}
    # ``word_similarity()`` เป็น real (float4) → psycopg แปลงเป็น float ของ Python
    assert isinstance(rows[0]["score"], float)
    # ชื่อเอกสารตรงกับคำค้นทั้งคำ → เต็ม 1.0 ทั้งคู่ แล้วเรียงต่อด้วย title
    # (ตอนใช้ ``similarity()`` ค่านี้เคยเป็น 0.4x และต่างกันเล็กน้อย)
    assert [row["score"] for row in rows] == [pytest.approx(1.0), pytest.approx(1.0)]


def test_search_documents_honours_limit(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(repo.search_documents(live_db, "หนังสือรับรองรายได้ครอบครัว", limit=1))

    assert len(rows) == 1
    assert rows[0]["title"] == "102 หนังสือรับรองรายได้ครอบครัว (กยศ.)"


def test_search_documents_partial_query_ranks_exact_keyword_first(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    คำค้นบางส่วน: เอกสารที่มี keyword ตรงคำมาก่อนเอกสารที่แค่คล้าย

    ``ลงทะเบียน`` ตรงกับ keyword ของเอกสารหมวด registration เต็ม ๆ (1.0)
    ส่วน ``ปฏิทินการศึกษา`` ติดมาด้วยที่ 0.8 เพราะ keyword มีคำว่า
    "ลงทะเบียนเรียน" อยู่ — เรียงคะแนนแล้วตัวที่ตรงจริงอยู่บนสุด
    (ก่อนแก้บั๊ก ``similarity()`` ให้ 0.3333 เฉียดเกณฑ์ และได้แถวเดียว)
    """
    rows = run(repo.search_documents(live_db, "ลงทะเบียน"))

    assert [row["title"] for row in rows] == [
        "เอกสารขอยืนยันลงทะเบียนเรียน (ล่าช้า)",
        "ปฏิทินการศึกษา (ระบบบริการการศึกษา)",
    ]
    assert rows[0]["category"] == "registration"
    assert rows[0]["score"] == pytest.approx(1.0)
    assert rows[1]["score"] == pytest.approx(0.8)


def test_search_documents_finds_short_queries_users_actually_type(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    คำสั้น ๆ ที่คนพิมพ์จริงต้องเจอ — **เคยเป็นบั๊กที่แก้แล้ว**

    เดิม ``similarity()`` เทียบคำค้นสั้นกับ ``keywords`` ทั้งก้อน → 0 แถวทุกคำ
    (ดู :func:`test_search_documents_root_cause_is_whole_string_similarity`)
    ตอนนี้ ``word_similarity`` สองทิศทางให้ผลตามที่ผู้ใช้คาด

    ``ดรอป``/``ใบรับรอง`` ยังได้ 0 แถว — นั่นคือ **ช่องว่างของข้อมูล**
    (คลังไม่มีเอกสารเรื่องนั้นเลย) ไม่ใช่บั๊กของ query
    """
    found = {
        keyword: [row["title"] for row in run(repo.search_documents(live_db, keyword))]
        for keyword in ("กยศ", "กู้ยืม", "ฝึกงาน", "ปฏิทิน", "ดรอป", "ใบรับรอง")
    }

    assert len(found["กยศ"]) == 5
    assert len(found["กู้ยืม"]) == 4
    assert len(found["ฝึกงาน"]) == 4
    assert found["ปฏิทิน"] == [
        "ปฏิทินการศึกษา (ระบบบริการการศึกษา)",
        "ปฏิทินสหกิจศึกษา (ศูนย์สหกิจศึกษาฯ)",
    ]
    assert all(title.startswith(("1", "หน้ารวม")) for title in found["กยศ"]), found["กยศ"]
    # ช่องว่างของข้อมูล ไม่ใช่ของ query — บันทึกไว้ให้รอบ re-scrape เก็บเพิ่ม
    assert found["ดรอป"] == []
    assert found["ใบรับรอง"] == []


def test_search_documents_tolerates_thai_misspelling(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    พิมพ์ผิดทีละตัวยังเจอ — **เคยเป็นบั๊กที่แก้แล้ว** (เดิมได้ 0 แถว)

    ``ลงทะเบียง`` → 0.8, ``ทุนการศึกส`` → 0.818 ทั้งคู่ผ่านเกณฑ์
    แต่คะแนนต่ำกว่าตอนสะกดถูก (1.0) → ลำดับยังบอกความมั่นใจได้
    """
    misspelled = run(repo.search_documents(live_db, "ลงทะเบียง"))
    assert [row["title"] for row in misspelled] == [
        "เอกสารขอยืนยันลงทะเบียนเรียน (ล่าช้า)",
        "ปฏิทินการศึกษา (ระบบบริการการศึกษา)",
    ]
    assert misspelled[0]["score"] == pytest.approx(0.8)

    scholarship = run(repo.search_documents(live_db, "ทุนการศึกส"))
    assert [row["title"] for row in scholarship] == [
        "ข่าวทุนการศึกษา คณะวิทยาศาสตร์และเทคโนโลยี"
    ]
    # สะกดถูกได้คะแนนสูงกว่าเสมอ
    correct = run(repo.search_documents(live_db, "ทุนการศึกษา"))
    assert correct[0]["title"] == scholarship[0]["title"]
    assert correct[0]["score"] > scholarship[0]["score"]


def test_search_documents_root_cause_is_whole_string_similarity(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ชี้สาเหตุให้ชัด เพื่อให้คนแก้ไม่ต้องไปเดาใหม่

    ``similarity(a, b)`` คิดจาก **เซตของ trigram ทั้งสตริง** →
    คำค้นสั้นเทียบกับ ``keywords`` ที่เอาหลายคำมาต่อด้วย ``,`` จะได้คะแนนต่ำ
    ตลอด ไม่มีทางถึงเกณฑ์ 0.3 ของ ``%``

    ``word_similarity(query, keywords)`` (ตัวดำเนินการ ``<%``) เทียบคำค้นกับ
    "ส่วนที่ดีที่สุด" ของอีกฝั่ง → ได้ 1.0 สำหรับคำที่มีอยู่จริง
    นั่นคือตัวดำเนินการที่ query นี้ควรใช้
    """
    row = run(
        live_db.fetch_one(
            "SELECT count(*) AS have_keyword,"
            "       max(similarity(keywords, %s)) AS best_similarity,"
            "       max(word_similarity(%s, keywords)) AS best_word_similarity"
            " FROM documents"
            " WHERE audience = 'student' AND keywords LIKE %s",
            ("กู้ยืม", "กู้ยืม", "%กู้ยืม%"),
        )
    )

    assert row is not None
    assert row["have_keyword"] == 4, "มีเอกสารที่ keywords มีคำว่า กู้ยืม อยู่จริง"
    assert row["best_similarity"] < 0.3, row["best_similarity"]
    assert row["best_word_similarity"] == pytest.approx(1.0)
    # เกณฑ์ของ ``%`` เป็นค่า default ของ Postgres ไม่ได้ถูกตั้งเองในโปรเจกต์
    limit = run(live_db.fetch_one("SELECT show_limit() AS l"))
    assert limit is not None and limit["l"] == pytest.approx(0.3)


def test_search_documents_should_find_documents_containing_the_keyword(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    เคยเป็น ``xfail(strict=True)`` — บั๊กเดิมคือ ``SQL_SEARCH_DOCUMENTS`` ใช้
    ``similarity()`` / ``%`` เทียบคำค้นสั้นกับ ``keywords`` ที่เป็นสตริงยาว
    ทำให้คะแนนไม่ถึงเกณฑ์ 0.3 → หาไม่เจอทุกคำที่คนพิมพ์จริง

    แก้แล้วโดยเปลี่ยนไป ``word_similarity`` (ดูคอมเมนต์ใน ``app/repository.py``)
    เทสนี้จึงผ่านของจริง ไม่ใช่ผ่านเพราะ marker
    """
    assert run(repo.search_documents(live_db, "กยศ")), "ควรเจอเอกสาร กยศ. ที่มีอยู่ 6 ฉบับ"
    assert run(repo.search_documents(live_db, "กู้ยืม")), "ควรเจอเอกสารกู้ยืม 4 ฉบับ"


# ── อาจารย์ ─────────────────────────────────────────────────────────────────


def test_instructor_groups_matches_real_seed(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(repo.instructor_groups(live_db))

    assert [(row["group_name"], row["total"]) for row in rows] == REAL_GROUPS


def test_instructor_groups_counts_people_not_rows(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ``count(DISTINCT instructor_id)`` สำคัญกับข้อมูลชุดนี้จริง

    อาจารย์ 28 คน แต่มีสังกัด 33 แถว เพราะ 3 คนสังกัดหลายกลุ่ม
    (ธารีชล 3, อภิชาติ 3, ธรัช 2) ถ้าเขียน ``count(*)`` เฉย ๆ ผลรวมจะยังได้ 33
    เท่ากันพอดี — บั๊กแบบนี้ mock ที่ใส่ข้อมูลคนละคนต่อกลุ่มจับไม่ได้
    """
    rows = run(repo.instructor_groups(live_db))
    assert sum(row["total"] for row in rows) == 33

    people = run(
        live_db.fetch_one(
            "SELECT count(DISTINCT instructor_id) AS people,"
            "       count(*) AS affiliations"
            " FROM instructor_affiliations"
        )
    )
    assert people == {"people": 28, "affiliations": 33}


def test_instructors_in_group_puts_chair_first(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(repo.instructors_in_group(live_db, IT_GROUP))

    assert len(rows) == 9
    assert set(rows[0]) == {
        "full_name",
        "title_prefix",
        "email",
        "room",
        "office_hours",
        "position",
        "is_chair",
    }
    assert rows[0]["is_chair"] is True
    assert rows[0]["full_name"] == "อาจารย์ ดร.วีระพน ภานุรักษ์"
    assert rows[0]["position"] == "ประธานหลักสูตรเทคโนโลยีสารสนเทศ"
    # ที่เหลือไม่ใช่ประธาน และเรียงตามชื่อ
    assert not any(row["is_chair"] for row in rows[1:])
    assert [row["full_name"] for row in rows[1:]] == sorted(
        row["full_name"] for row in rows[1:]
    )


def test_instructors_in_group_unknown_returns_empty_list(
    live_db: Database, run: Callable[..., Any]
) -> None:
    assert run(repo.instructors_in_group(live_db, "สาขาที่ไม่มีอยู่")) == []


def test_instructors_in_group_honours_limit(
    live_db: Database, run: Callable[..., Any]
) -> None:
    assert len(run(repo.instructors_in_group(live_db, IT_GROUP, limit=2))) == 2


def test_room_and_office_hours_are_always_null(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    query เลือก ``room`` / ``office_hours`` มาแสดง แต่ข้อมูลจริงว่างทั้ง 28 คน

    ``app.router._instructors_answer`` เช็ค ``if row.get('room')`` ไว้แล้ว
    → ไม่พัง แต่บรรทัด "ห้อง"/"เวลาเข้าพบ" จะไม่เคยขึ้นเลยกับข้อมูลชุดนี้
    """
    rows = run(repo.instructors_in_group(live_db, IT_GROUP))

    assert all(row["room"] is None for row in rows)
    assert all(row["office_hours"] is None for row in rows)


# ── search_instructors (pg_trgm) — อีกตัวที่ยังไม่มีใครเรียกในแอป ────────────


def test_search_instructors_finds_by_partial_first_name(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(repo.search_instructors(live_db, "ธรัช"))

    assert len(rows) == 1
    assert set(rows[0]) == {
        "full_name",
        "title_prefix",
        "email",
        "room",
        "office_hours",
        "score",
    }
    assert rows[0]["full_name"] == "ผู้ช่วยศาสตราจารย์ ดร.ธรัช อารีราษฎร์"
    assert rows[0]["email"] == "dr.tharach@rmu.ac.th"
    # ชื่อต้นตรงทั้งคำใน ``name_normalized`` → 1.0
    # (ตอนใช้ ``similarity()`` ได้แค่ 1/3 เพราะเทียบกับชื่อ-นามสกุลทั้งก้อน)
    assert rows[0]["score"] == pytest.approx(1.0)


def test_search_instructors_finds_by_partial_surname(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(repo.search_instructors(live_db, "อารีราษฎร์"))

    assert [row["full_name"] for row in rows] == [
        "ผู้ช่วยศาสตราจารย์ ดร.ธรัช อารีราษฎร์"
    ]
    assert rows[0]["score"] == pytest.approx(1.0)


def test_search_instructors_tolerates_misspelling(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    สะกดนามสกุลผิด (``อารีราด`` แทน ``อารีราษฎร์``) ยังเจอ — ต่างจากเอกสาร

    เพราะ ``name_normalized`` เป็นสตริงสั้น trigram ที่เหมือนกันจึงมีสัดส่วนสูง
    """
    rows = run(repo.search_instructors(live_db, "ธรัช อารีราด"))

    assert [row["full_name"] for row in rows] == [
        "ผู้ช่วยศาสตราจารย์ ดร.ธรัช อารีราษฎร์"
    ]
    assert rows[0]["score"] > 0.6


def test_search_instructors_tolerates_one_letter_typo(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ``วีระพล`` (จริงคือ ``วีระพน``) ต้องเจอ — **เคยเป็นบั๊กที่แก้แล้ว**

    เก็บการวัดด้วย ``similarity()`` ไว้เป็นหลักฐานว่าทำไมต้องเปลี่ยนตัวดำเนินการ:
    ค่าเดิม 0.2778 ต่ำกว่าเกณฑ์ 0.3 อยู่นิดเดียว → หาไม่เจอ
    ``word_similarity`` ให้ 0.714 กับชื่อเดียวกัน → เจอ
    """
    rows = run(repo.search_instructors(live_db, "วีระพล"))

    assert [row["full_name"] for row in rows] == ["อาจารย์ ดร.วีระพน ภานุรักษ์"]
    assert rows[0]["score"] == pytest.approx(0.714286, abs=1e-6)

    old_operator = run(
        live_db.fetch_one(
            "SELECT max(similarity(name_normalized, %s)) AS best FROM instructors",
            ("วีระพล",),
        )
    )
    assert old_operator is not None and 0.27 < old_operator["best"] < 0.3


def test_search_instructors_orders_by_score_then_name(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    นามสกุลเดียวกันสองคน → คะแนนเท่ากัน (1.0) แล้วตัดสินด้วย ``full_name``

    collation ``C.UTF-8`` เรียงตาม code point → ``ว`` (U+0E27) มาก่อน
    ``เ`` (U+0E40) ดังนั้น "วีระพน" ขึ้นก่อน "เดือนเพ็ญ" ไม่ใช่ลำดับตามพยัญชนะไทย
    """
    rows = run(repo.search_instructors(live_db, "ภานุรักษ์"))

    assert [row["full_name"] for row in rows] == [
        "อาจารย์ ดร.วีระพน ภานุรักษ์",
        "อาจารย์ ดร.เดือนเพ็ญ ภานุรักษ์",
    ]
    assert [row["score"] for row in rows] == [pytest.approx(1.0), pytest.approx(1.0)]

    assert len(run(repo.search_instructors(live_db, "ภานุรักษ์", limit=1))) == 1


def test_search_instructors_unknown_name_returns_empty_list(
    live_db: Database, run: Callable[..., Any]
) -> None:
    assert run(repo.search_instructors(live_db, "สมชาย ใจดี")) == []


def test_instructor_contact_coverage_has_no_phone_numbers(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ค่าจริงจากเว็บคณะ: มีอีเมล 26/28 ไม่มีเบอร์โทรและห้องทำงานเลย

    ``app.router._contact_caveat`` พึ่งตัวเลขนี้ในการบอกผู้ใช้ตรง ๆ ว่า
    "ยังไม่มีเบอร์โทรในระบบ" — ถ้าค่าเปลี่ยน ข้อความนั้นจะกลายเป็นคำโกหก
    """
    coverage = run(repo.instructor_contact_coverage(live_db))

    assert coverage == {
        "total": 28,
        "with_email": 26,
        "with_phone": 0,
        "with_room": 0,
    }


# ── แผนการเรียน / รายวิชา / วิชาที่เปิด ──────────────────────────────────────


def test_planning_coverage_reports_zero_prerequisites(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ตารางที่ยังว่างต้องรายงานเป็น 0 (ไม่ใช่ ``None``) ขณะที่ตัวอื่นมีค่าจริง

    ตัวเลขชุดนี้คือสิ่งที่บอทเอาไปพูดว่า "ตอบอะไรได้/ไม่ได้" ตาม Requirement
    ข้อ 14 — ถ้า 0 กลายเป็น ``None`` router จะแสดง 0 เหมือนกันแต่เงื่อนไข
    ``if not patterns and not rules`` จะเปลี่ยนพฤติกรรม

    ``curriculum_rules`` = 32 ตั้งแต่ 22 ส.ค. 2026 (นำเข้าแผนการเรียนจริง)
    ส่วน ``prerequisites`` ยังเป็น 0 เพราะระบบทะเบียนไม่เผยแพร่วิชาบังคับก่อน
    """
    coverage = run(repo.planning_coverage(live_db, get_settings().default_program_code))

    assert coverage == {
        "curriculum_rules": 32,
        "prerequisites": 0,
        "patterns": 45,
        "opens_sem1": 37,
        "opens_sem2": 33,
        "opens_sem3": 0,
        "program_courses": 68,
    }
    assert all(isinstance(value, int) for value in coverage.values())


def test_planning_coverage_unknown_program_keeps_global_counts(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ``patterns`` นับทั้งตาราง ไม่กรองด้วย ``program_code`` (ตามที่ SQL เขียนไว้)

    → รหัสหลักสูตรที่ไม่มีอยู่ยังได้ 45 กลับมา แต่ ``program_courses`` เป็น 0
    ถ้าวันหลังมีหลายหลักสูตรจริง ตัวเลข ``patterns`` จะกำกวม บันทึกไว้ตรงนี้
    """
    coverage = run(repo.planning_coverage(live_db, "0000000"))

    assert coverage["program_courses"] == 0
    assert coverage["patterns"] == 45
    assert coverage["curriculum_rules"] == 0


def test_course_by_code_returns_real_course_with_pattern(
    live_db: Database, run: Callable[..., Any]
) -> None:
    course = run(repo.course_by_code(live_db, COURSE_WITH_MANY_OFFERINGS))

    assert course is not None
    assert course["course_code"] == "1109902"
    assert course["name_th"] == "ภาษาไทยเพื่อการสื่อสาร"
    assert course["name_en"] == "Thai Language for Communication"
    assert course["credits"] == 3
    assert course["credits_text"] == "3 (2-2-5)"
    assert course["description_th"].startswith("พัฒนาทักษะการฟัง การพูด")
    assert course["source_url"].startswith("https://regis.rmu.ac.th/")
    # คอลัมน์จาก LEFT JOIN offering_patterns
    assert (course["opens_sem1"], course["opens_sem2"], course["opens_sem3"]) == (
        True,
        True,
        False,
    )
    assert course["terms_observed"] == 4
    assert course["terms_found"] == 4


def test_course_by_code_missing_returns_none(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """ต้องได้ ``None`` ไม่ใช่ exception — router เช็ค ``if not course``"""
    assert run(repo.course_by_code(live_db, COURSE_MISSING)) is None


def test_course_without_pattern_returns_nulls_from_left_join(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    145 วิชา มี pattern แค่ 45 → อีก 100 วิชาได้ ``None`` จาก LEFT JOIN

    ``app.router._course_answer`` วน ``if opens`` อยู่ ซึ่งรับ ``None`` ได้
    แต่ ``terms_observed`` เป็น ``None`` ด้วย → ต้องมี ``or 0`` เสมอ
    """
    course = run(repo.course_by_code(live_db, COURSE_WITHOUT_PATTERN))

    assert course is not None
    assert course["name_th"] == "ภาษาจีนเพื่อการสื่อสาร"
    assert course["opens_sem1"] is None
    assert course["opens_sem2"] is None
    assert course["opens_sem3"] is None
    assert course["terms_observed"] is None
    assert course["terms_found"] is None


def test_sample_courses_only_returns_courses_with_a_known_term(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    วิชาตัวอย่างบนปุ่ม "ค้นรายวิชา" ต้องกดแล้วได้คำตอบที่ดู **สมบูรณ์**

    SQL ใช้ INNER JOIN ``offering_patterns`` โดยเจตนา — ถ้าหลุดวิชาที่ไม่มี
    pattern เข้ามา ผู้ใช้จะกดปุ่มตัวอย่างของเราเองแล้วเจอ
    "ยังไม่พบว่าเปิดสอน" ซึ่งเป็นการแนะนำตัวที่แย่ที่สุด
    """
    rows = run(
        repo.sample_courses(live_db, get_settings().default_program_code, limit=3)
    )

    assert len(rows) == 3
    assert set(rows[0]) == {"course_code", "name_th"}
    for row in rows:
        assert re.fullmatch(r"\d{7}", row["course_code"]), row
        assert row["name_th"]
        course = run(repo.course_by_code(live_db, row["course_code"]))
        assert course is not None
        assert any(
            course[key] for key in ("opens_sem1", "opens_sem2", "opens_sem3")
        ), row["course_code"]


def test_sample_courses_respects_limit_and_program(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """หลักสูตรที่ไม่มีในระบบต้องได้ลิสต์ว่าง ไม่ใช่วิชาของหลักสูตรอื่น"""
    assert len(run(repo.sample_courses(live_db, "643170151", limit=1))) == 1
    assert run(repo.sample_courses(live_db, "ไม่มีหลักสูตรนี้", limit=3)) == []


def test_offerings_for_course_returns_newest_term_first(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(repo.offerings_for_course(live_db, COURSE_WITH_MANY_OFFERINGS))

    assert len(rows) == 6, "limit default = 6"
    assert set(rows[0]) == {
        "acad_year",
        "semester",
        "section",
        "schedule_raw",
        "instructors",
        "seats_total",
        "seats_left",
        "status",
    }
    assert rows[0]["acad_year"] == 2568 and rows[0]["semester"] == 2
    assert rows[0]["section"] == "1"
    assert rows[0]["schedule_raw"] == "TU13:00-16:20 350804"
    assert rows[0]["instructors"] == "อาจารย์จำรัส สุขแป"
    assert rows[0]["status"] == "ปกติ"
    # เรียงเทอมใหม่ก่อนเสมอ
    terms = [(row["acad_year"], row["semester"]) for row in rows]
    assert terms == sorted(terms, reverse=True)


def test_offerings_section_order_is_textual_not_numeric(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ``offerings.section`` เป็น ``text`` → ``ORDER BY section`` ได้ 1, 10, 2

    ผลจริง: หมู่ 10 (ที่นั่ง 1 ที่ ไม่มีตารางเรียน) แทรกขึ้นมาก่อนหมู่ 2
    และเบียดหมู่ 3-9 ตกออกจาก ``LIMIT 6``
    → นักศึกษาเห็นหมู่เรียนไม่ครบและลำดับดูสับสน
    บันทึกเป็นพฤติกรรมจริง (ยังไม่แก้ ตามขอบเขตงาน) ถ้าจะแก้ควรเรียงด้วย
    ``ORDER BY ... nullif(regexp_replace(section, '\\D', '', 'g'), '')::int``
    """
    rows = run(repo.offerings_for_course(live_db, COURSE_WITH_MANY_OFFERINGS, limit=6))
    sem_2568_1 = [
        row["section"] for row in rows if (row["acad_year"], row["semester"]) == (2568, 1)
    ]

    assert sem_2568_1 == ["1", "10", "2"]


def test_offerings_for_course_covers_all_four_seeded_terms(
    live_db: Database, run: Callable[..., Any]
) -> None:
    rows = run(repo.offerings_for_course(live_db, COURSE_WITH_MANY_OFFERINGS, limit=100))
    terms = sorted({(row["acad_year"], row["semester"]) for row in rows}, reverse=True)

    assert len(rows) == 36
    assert terms == [(2568, 2), (2568, 1), (2567, 2), (2567, 1)]


def test_offerings_for_course_unknown_returns_empty_list(
    live_db: Database, run: Callable[..., Any]
) -> None:
    assert run(repo.offerings_for_course(live_db, COURSE_MISSING)) == []


def test_latest_term_is_2568_semester_2(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """4 เทอมใน seed: 2567/1, 2567/2, 2568/1, 2568/2 → ล่าสุดคือ 2568/2"""
    term = run(repo.latest_term(live_db))

    assert term == {"acad_year": 2568, "semester": 2, "offerings": 45}


def test_latest_term_agrees_with_max_over_offerings(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    เทียบกับการนับแบบตรง ๆ — ดัก ``ORDER BY`` ที่ผิดชนิดข้อมูล

    ``semester`` เป็น ``smallint`` (ไม่ใช่ text) จึงเรียงเป็นตัวเลขได้ถูก
    ต่างจาก ``section`` ที่เป็น text
    """
    grouped = run(
        live_db.fetch_all(
            "SELECT acad_year, semester, count(*) AS offerings FROM offerings"
            " GROUP BY acad_year, semester ORDER BY acad_year DESC, semester DESC"
        )
    )

    assert len(grouped) == 4
    assert run(repo.latest_term(live_db)) == grouped[0]
    assert sum(row["offerings"] for row in grouped) == 337


# ── บทสนทนา + โหมดปรึกษา AI (ทางเขียน — ใช้ fixture test_user) ─────────────
#
# กลุ่มนี้ต่างจากข้างบนตรงที่ต้อง INSERT/UPDATE จริง (ensure_user,
# insert_chat_log, ai_sessions) — ``row_count_guard`` ใน conftest จะ
# เทียบจำนวนแถวทั้ง 20 ตารางก่อน/หลัง session ให้ถ้ามีอะไรค้าง


def test_ensure_user_inserts_once_then_upserts_same_id(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """``ON CONFLICT DO UPDATE`` ต้องคืน id เดิม ไม่ใช่แถวที่สอง"""
    from .conftest import TEST_HASH_PREFIX

    first = run(repo.ensure_user(live_db, TEST_HASH_PREFIX + "user"))
    second = run(repo.ensure_user(live_db, TEST_HASH_PREFIX + "user"))

    assert first == second == test_user


def test_chat_log_round_trips_with_null_user(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ``user_id=NULL`` ได้ (event ใน group ไม่มี userId)

    **บันทึกความเข้าใจผิดที่ง่ายจะเกิด**: ``insert_chat_log`` คืน
    ``cursor.rowcount`` (= 1) **ไม่ใช่ id ของแถว** เพราะ SQL ไม่มี
    ``RETURNING`` และ ``Database.execute`` คืน rowcount — ใครจะเอา id
    ไปใช้ต่อต้องเติม ``RETURNING id`` แล้วใช้ ``fetch_one``
    """
    affected = run(
        repo.insert_chat_log(
            live_db,
            user_id=None,
            message_text="itest-ข้อความจาก group",
            answered_by="fallback",
            intent_key=None,
            confidence=None,
            response_text="ขออภัยครับ ระบบยังไม่พบข้อมูล...",
            citations=None,
            latency_ms=None,
            llm_model=None,
            prompt_tokens=None,
            output_tokens=None,
        )
    )
    assert affected == 1, "คืนจำนวนแถวที่กระทบ ไม่ใช่ id"

    row = run(
        live_db.fetch_one(
            "SELECT user_id, message_text, answered_by, citations FROM chat_logs"
            " WHERE message_text = %s",
            ("itest-ข้อความจาก group",),
        )
    )
    assert row == {
        "user_id": None,
        "message_text": "itest-ข้อความจาก group",
        "answered_by": "fallback",
        "citations": None,
    }

    # แถวนี้ไม่มี FK → cleanup ตาม hash กวาดไม่เจอ ต้องลบเองที่นี่
    # (ถ้าลืม ``row_count_guard`` จะฟ้องตอน teardown ของ session)
    deleted = run(
        live_db.fetch_all(
            "DELETE FROM chat_logs WHERE message_text = %s RETURNING id",
            ("itest-ข้อความจาก group",),
        )
    )
    assert len(deleted) == 1


def test_chat_log_stores_citations_as_jsonb_and_token_counts(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """
    ``citations`` ต้องกลับมาเป็น object ของ Python และคอลัมน์ต้นทุน LLM
    ต้องเก็บได้จริง (ใช้วัดผลธีสิส: ต้นทุน token ต่อคำตอบ)
    """
    payload = [{"title": "ระเบียบการลงทะเบียน", "url": "https://sci.rmu.ac.th/?p=1"}]
    run(
        repo.insert_chat_log(
            live_db,
            user_id=test_user,
            message_text="ปรึกษา อ่านหนังสือยังไง",
            answered_by="ai_chat",
            intent_key="ai_chat",
            confidence=None,
            response_text="แนะนำให้อ่านเป็นรอบสั้น ๆ ครับ",
            citations=payload,
            latency_ms=1234,
            llm_model="gemini-3.5-flash-lite",
            prompt_tokens=120,
            output_tokens=40,
        )
    )

    row = run(
        live_db.fetch_one(
            "SELECT citations, latency_ms, llm_model, prompt_tokens, output_tokens"
            " FROM chat_logs WHERE user_id = %s",
            (test_user,),
        )
    )
    assert row is not None
    assert row["citations"] == payload  # jsonb → list[dict] ไม่ใช่สตริง
    assert row["latency_ms"] == 1234
    assert row["llm_model"] == "gemini-3.5-flash-lite"
    assert (row["prompt_tokens"], row["output_tokens"]) == (120, 40)


def test_chat_log_records_delivery_status_and_rejects_unknown_values(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """
    ``status`` แยกรอบที่ส่งถึงผู้ใช้ออกจากรอบที่ **คิดคำตอบได้แต่ส่งไม่ถึง**

    เดิมรอบที่ส่งไม่ถึงไม่ถูกบันทึกเลย ทำให้ธีสิสนับอัตราการตอบสำเร็จเกินจริง
    เทสนี้ยืนยันสามอย่างที่ mock พิสูจน์ให้ไม่ได้: ค่า default ของคอลัมน์,
    ค่า send_failed เขียนลงได้จริง และ CHECK ปฏิเสธค่าที่พิมพ์ผิด
    (ต้องใช้ migration 004 — ถ้าเทสนี้ฟ้องว่าไม่มีคอลัมน์ ให้รัน ``make migrate``)
    """
    for status, message in (
        (repo.CHAT_STATUS_DELIVERED, "itest-ส่งถึงแล้ว"),
        (repo.CHAT_STATUS_SEND_FAILED, "itest-ส่งไม่ถึง"),
    ):
        run(
            repo.insert_chat_log(
                live_db,
                user_id=test_user,
                message_text=message,
                answered_by="ai_chat",
                intent_key="ai_chat",
                confidence=None,
                response_text="คำตอบที่ router คิดไว้",
                citations=None,
                latency_ms=None,
                llm_model=None,
                prompt_tokens=None,
                output_tokens=None,
                status=status,
            )
        )

    rows = run(
        live_db.fetch_all(
            "SELECT message_text, status FROM chat_logs WHERE user_id = %s"
            " ORDER BY message_text",
            (test_user,),
        )
    )
    assert rows == [
        {"message_text": "itest-ส่งถึงแล้ว", "status": repo.CHAT_STATUS_DELIVERED},
        {"message_text": "itest-ส่งไม่ถึง", "status": repo.CHAT_STATUS_SEND_FAILED},
    ]

    # ค่าที่ไม่อยู่ใน CHECK ต้องถูกปฏิเสธ ไม่ใช่เข้าไปเงียบ ๆ แล้วเจอตอนสรุปผล
    with pytest.raises(Exception, match="chat_logs_status_check"):
        run(
            live_db.fetch_all(
                "INSERT INTO chat_logs (user_id, answered_by, status)"
                " VALUES (%s, %s, %s) RETURNING id",
                (test_user, "search", "ส่งไม่ได้"),
            )
        )


def test_recent_chat_returns_only_ai_rows_newest_last(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """
    กรองเฉพาะ ``answered_by='ai_chat'`` ที่มี ``response_text`` และเรียง
    เก่า → ใหม่ (LLM ต้องได้บริบทตามลำดับจริง)
    """
    for index, answered_by in enumerate(
        ["rich_menu", "ai_chat", "search", "ai_chat", "ai_chat"], start=1
    ):
        run(
            repo.insert_chat_log(
                live_db,
                user_id=test_user,
                message_text=f"คำถามที่ {index}",
                answered_by=answered_by,
                intent_key="ai_chat" if answered_by == "ai_chat" else None,
                confidence=None,
                response_text=f"คำตอบที่ {index}" if answered_by == "ai_chat" else None,
                citations=None,
                latency_ms=None,
                llm_model="gemini-3.5-flash-lite" if answered_by == "ai_chat" else None,
                prompt_tokens=None,
                output_tokens=None,
            )
        )

    rows = run(repo.recent_chat(live_db, test_user, turns=10))

    assert [row["message_text"] for row in rows] == ["คำถามที่ 2", "คำถามที่ 4", "คำถามที่ 5"]
    # LIMIT ทำงานจริง — ขอ 2 ได้ 2 ล่าสุด (เก่า → ใหม่)
    assert [row["message_text"] for row in run(repo.recent_chat(live_db, test_user, 2))] == [
        "คำถามที่ 4",
        "คำถามที่ 5",
    ]


def test_ai_session_lifecycle_open_touch_end(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """
    วนครบ 4 ฟังก์ชัน ai_sessions บน DB จริง:

    เปิด → ไม่ซ้ำ (NOT EXISTS atomically) → อ่านได้ทั้งทาง user_id/hash →
    touch นับรอบ → ปิดด้วยเหตุผลที่ CHECK constraint รับ
    """
    from .conftest import TEST_HASH_PREFIX

    hash_value = TEST_HASH_PREFIX + "user"
    session_id = run(repo.open_ai_session(live_db, hash_value))
    assert session_id > 0

    # เปิดซ้ำระหว่างยังเปิดอยู่ = RETURNING ไม่คืนแถว → ``int(row["id"])``
    # พัง — ผู้เรียกต้องเช็ค active_ai_session_by_hash ก่อนเสมอ (dispatch ทำ)
    with pytest.raises(Exception):
        run(repo.open_ai_session(live_db, hash_value))

    by_user = run(repo.active_ai_session(live_db, test_user))
    by_hash = run(repo.active_ai_session_by_hash(live_db, hash_value))
    assert by_user is not None and by_user["id"] == session_id
    assert by_user["turn_count"] == 0
    assert by_hash is not None and by_hash["id"] == session_id

    touched = run(repo.touch_ai_session(live_db, session_id))
    assert touched == 1
    by_hash = run(repo.active_ai_session_by_hash(live_db, hash_value))
    assert by_hash is not None and by_hash["turn_count"] == 1

    ended = run(repo.end_ai_session(live_db, session_id, "button"))
    assert ended == 1
    assert run(repo.active_ai_session(live_db, test_user)) is None
    assert run(repo.active_ai_session_by_hash(live_db, hash_value)) is None

    reason = run(
        live_db.fetch_one("SELECT end_reason FROM ai_sessions WHERE id = %s", (session_id,))
    )
    assert reason == {"end_reason": "button"}


def test_ai_session_end_rejects_unknown_reason(
    live_db: Database, run: Callable[..., Any], test_user: int
) -> None:
    """CHECK constraint ของ migration 002 ต้องบังคับจริงกับ DB ไม่ใช่แค่ใน SQL"""
    from .conftest import TEST_HASH_PREFIX

    session_id = run(repo.open_ai_session(live_db, TEST_HASH_PREFIX + "user"))
    with pytest.raises(Exception) as failure:
        run(repo.end_ai_session(live_db, session_id, "เหตุผลมั่ว"))
    assert "end_reason" in str(failure.value) or "check" in str(failure.value).lower()

    # ปิดจริงให้เรียบร้อย — ไม่งั้น session ค้างจะพาเทสถัดไปงง
    run(repo.end_ai_session(live_db, session_id, "button"))


# ── Planner: แผนการเรียน + วิชาที่ผ่านของผู้ใช้ ───────────────────────────────


def test_curriculum_plan_returns_one_row_per_course_with_a_name(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    32 วิชา ไม่ซ้ำ และต้องมีชื่อวิชาครบทุกแถว

    เคยพลาดมาแล้วสองแบบที่เทสนี้ดักไว้:

    1. เก็บรหัสเต็ม ('7071102-3') ลง ``course_code`` → JOIN ``courses``
       ไม่ติดเลยทั้ง 32 วิชา ชื่อหายหมดแบบไม่มี error
    2. ``courses.course_code`` ซ้ำได้ (7071102 มี 3 แถว) → JOIN ธรรมดา
       ทำให้ 32 วิชาบวมเป็น 50 กว่าแถว แล้วหน่วยกิตรวมผิดตามไปด้วย
    """
    rows = run(repo.curriculum_plan(live_db, get_settings().default_program_code))
    codes = [row["course_code"] for row in rows]

    assert len(rows) == 32
    assert len(set(codes)) == 32, "แถวซ้ำ = LATERAL dedupe พัง"
    assert all(row["name_th"] for row in rows), "ต้องมีชื่อวิชาครบทุกแถว"
    assert all(row["credits"] for row in rows)
    assert all(len(code) == 7 and code.isdigit() for code in codes)
    assert all(row["course_code_full"] for row in rows)


def test_curriculum_plan_matches_the_registrar_study_plan(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    โครงของแผนต้องตรงกับหน้า Student_Studyplan.asp ที่ scrape มา

    ล็อกไว้เพราะเคยนำเข้าได้ 31 แถว (ปี 1 เทอม 1 หายไป 1 วิชา) แล้วรายงานว่า
    สำเร็จ — ตัวเลขต่อเทอมคือที่เดียวที่จับความผิดพลาดแบบนั้นได้
    """
    rows = run(repo.curriculum_plan(live_db, get_settings().default_program_code))
    per_term: dict[tuple[int, int], int] = {}
    for row in rows:
        key = (row["std_year"], row["std_semester"])
        per_term[key] = per_term.get(key, 0) + 1

    assert per_term == {
        (1, 1): 6,
        (1, 2): 6,
        (2, 1): 5,
        (2, 2): 5,
        (3, 1): 4,
        (3, 2): 2,
        (4, 1): 3,
        (4, 2): 1,
    }
    # 31 วิชา x 3 นก. + ฝึกประสบการณ์ 12 นก.
    assert sum(row["credits"] for row in rows) == 105


def test_prerequisites_for_program_is_still_empty(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ยังไม่มีวิชาบังคับก่อน — ระบบทะเบียนไม่เผยแพร่ ต้องกรอกจากเล่ม มคอ.2

    เทสนี้ไม่ใช่การล็อก "ต้องว่างตลอดไป" แต่เป็นหลักฐานว่าตอนนี้ว่างจริง
    วันที่กรอกข้อมูลเข้าไปแล้ว ให้แก้เทสนี้พร้อมกับคำเตือนใน
    ``app/progress.py::prereq_caveat``
    """
    rows = run(
        repo.prerequisites_for_program(live_db, get_settings().default_program_code)
    )

    assert rows == []


def test_program_info_reports_total_credits(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    หน่วยกิตของหลักสูตร (120) มากกว่าผลรวมของแผน (105 + เลือกเสรี 6 = 111)

    planner ต้องคิด "เหลืออีกกี่หน่วยกิต" จากตัวเลขของหลักสูตร ไม่ใช่จากแผน
    ไม่งั้นจะบอกนักศึกษาว่าเหลือน้อยกว่าจริง
    """
    program = run(repo.program_info(live_db, get_settings().default_program_code))

    assert program is not None
    assert program["total_credits"] == 120
    assert program["program_name"] == "การจัดการนวัตกรรมดิจิทัล"


def test_user_profile_is_none_before_the_user_exists(
    live_db: Database, run: Callable[..., Any]
) -> None:
    from .conftest import TEST_HASH_PREFIX

    assert run(repo.user_profile(live_db, TEST_HASH_PREFIX + "ยังไม่เคยมี")) is None


def test_completed_courses_round_trip(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """ติ๊ก → อ่านกลับ → เอาออก → ล้างหมด ครบวงจรที่หน้า LIFF ใช้จริง"""
    from .conftest import TEST_HASH_PREFIX

    hash_value = TEST_HASH_PREFIX + "planner"
    user_id = run(repo.ensure_user(live_db, hash_value))
    profile = run(
        repo.set_user_program(
            live_db, hash_value, program_code="643170151", study_year=3
        )
    )
    assert profile is not None and profile["study_year"] == 3

    added = run(
        repo.replace_completed_courses(live_db, user_id, ["7071101", "7071102"])
    )
    assert added == {"removed": 0, "added": 2}

    rows = run(repo.completed_courses(live_db, user_id))
    assert [row["course_code"] for row in rows] == ["7071101", "7071102"]
    assert all(row["source"] == "self_report" for row in rows)

    # ส่งชุดใหม่ที่เอาออกหนึ่งตัว — ต้องลบตัวที่หายไป ไม่ใช่เพิ่มซ้อน
    changed = run(repo.replace_completed_courses(live_db, user_id, ["7071101"]))
    assert changed == {"removed": 1, "added": 0}

    seen = run(repo.user_profile(live_db, hash_value))
    assert seen is not None and seen["completed_courses"] == 1

    # ลิสต์ว่าง = ผู้ใช้เอาติ๊กออกหมด ต้องล้างได้ (ไม่ใช่ no-op)
    cleared = run(repo.replace_completed_courses(live_db, user_id, []))
    assert cleared == {"removed": 1, "added": 0}
    assert run(repo.completed_courses(live_db, user_id)) == []


def test_replace_completed_courses_is_idempotent(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """ส่งชุดเดิมซ้ำต้องไม่เพิ่มแถว (ON CONFLICT DO NOTHING) และไม่ลบของเดิม"""
    from .conftest import TEST_HASH_PREFIX

    hash_value = TEST_HASH_PREFIX + "idempotent"
    user_id = run(repo.ensure_user(live_db, hash_value))
    codes = ["7071101", "7071102", "7071102"]  # ส่งซ้ำมาในลิสต์เดียวก็ต้องรอด

    first = run(repo.replace_completed_courses(live_db, user_id, codes))
    second = run(repo.replace_completed_courses(live_db, user_id, codes))

    assert first == {"removed": 0, "added": 2}
    assert second == {"removed": 0, "added": 0}
    assert len(run(repo.completed_courses(live_db, user_id))) == 2


def test_active_prompt_rules_reads_the_real_table(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    กฎเสริมของ AI — สิ่งที่เทสได้ *เฉพาะ* กับ Postgres จริงคือ "ตารางมีจริง"

    unit test ใช้ DB ปลอมจึงผ่านได้แม้ยังไม่ได้รัน ``009_ai_prompt_rules.sql``
    บนเครื่องนั้น (migration ใน ``db/migrations/`` รันเองแค่ตอนสร้าง volume
    ครั้งแรก) — ตัวนี้จะแดงถ้าลืมรันมือ

    ตารางนี้เริ่มต้น **ว่าง** และไม่มี seed → เทสไม่ยืนยันจำนวนแถว แต่ยืนยันว่า
    แถวที่คืนมามีคอลัมน์ที่ ``app.ai_chat`` ใช้ และเป็นข้อที่เปิดใช้เท่านั้น
    """
    rows = run(repo.active_prompt_rules(live_db, ai_chat.PROMPT_RULE_LIMIT))

    assert isinstance(rows, list)
    assert len(rows) <= ai_chat.PROMPT_RULE_LIMIT
    for row in rows:
        assert row["rule_key"]
        assert row["rule_text"]

    # กฎหลักต้องอยู่ครบเสมอ ไม่ว่าตารางจะมีอะไรอยู่
    composed = ai_chat.compose_system_prompt(
        [row["rule_text"] for row in rows]
    )
    assert composed.startswith(ai_chat.SYSTEM_PROMPT)


# ── search_faqs (pg_trgm เหมือน search_documents) ────────────────────────────


def test_search_faqs_runs_and_respects_threshold(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ยืนยันว่า SQL ของชั้น FAQ รันบน Postgres จริงได้ — เหมือน
    :func:`test_search_documents_runs_at_all` ประเด็นคือ ``%%`` ที่ escape ไว้
    ต้องกลายเป็นตัวดำเนินการของ pg_trgm ไม่ใช่ placeholder ของ psycopg

    ``faqs`` ไม่มี seed และผู้ดูแลเพิ่มเองได้จากหน้า ``/admin`` → เทสนี้
    **ไม่ยืนยันเนื้อหา** แถว แต่ยืนยันสัญญาของฟังก์ชันที่ router พึ่งพา:
    เกณฑ์คะแนนเป็นตัวตัด, ``limit`` ถูกเคารพ, และมี ``score`` ให้เอาไปเก็บเป็น
    ``confidence`` ใน ``chat_logs``
    """
    question = "ลงทะเบียนเรียนล่าช้าต้องทำอย่างไร"

    # คะแนนเต็ม 1.0 เป็นเพดาน → เกณฑ์เกิน 1.0 ต้องไม่เหลือแถวใด ๆ
    assert run(repo.search_faqs(live_db, question, min_score=1.01)) == []

    rows = run(repo.search_faqs(live_db, question, limit=2, min_score=0.0))
    assert isinstance(rows, list)
    assert len(rows) <= 2

    scores = [row["score"] for row in rows]
    assert all(isinstance(score, float) for score in scores)
    assert scores == sorted(scores, reverse=True), "ต้องเรียงคะแนนมากไปน้อย"
    for row in rows:
        assert row["score"] >= 0.0


# ── ยามเฝ้าความครบถ้วน ───────────────────────────────────────────────────────

COVERED_FUNCTIONS = frozenset(
    {
        # ทางอ่าน (ข้อมูล seed)
        "document_categories",
        "documents_in_category",
        "search_documents",
        "search_faqs",
        "instructor_groups",
        "instructors_in_group",
        "search_instructors",
        "instructor_contact_coverage",
        "planning_coverage",
        "course_by_code",
        "sample_courses",
        "offerings_for_course",
        "latest_term",
        # ทางอ่าน (planner)
        "curriculum_plan",
        "prerequisites_for_program",
        "program_info",
        "user_profile",
        "completed_courses",
        "active_prompt_rules",
        # ทางเขียน (บทสนทนา + โหมดปรึกษา AI)
        "ensure_user",
        "insert_chat_log",
        "recent_chat",
        "open_ai_session",
        "active_ai_session",
        "active_ai_session_by_hash",
        "touch_ai_session",
        "end_ai_session",
        # ทางเขียน (LIFF ติ๊กวิชาที่ผ่าน)
        "set_user_program",
        "replace_completed_courses",
    }
)


def test_every_repository_function_is_covered_by_this_module() -> None:
    """
    เพิ่มฟังก์ชันใหม่ใน ``app.repository`` แล้วลืมเทสกับ DB จริง = เทสนี้พัง

    เช็คสองชั้น: ชื่อครบ และมีการเรียกจริงในไฟล์นี้ (กันการเติมชื่อลงลิสต์เฉย ๆ)
    """
    public = {
        name
        for name, value in vars(repo).items()
        if inspect.iscoroutinefunction(value) and not name.startswith("_")
    }

    assert public == COVERED_FUNCTIONS, f"ต่างกัน: {public ^ COVERED_FUNCTIONS}"

    source = inspect.getsource(inspect.getmodule(test_every_repository_function_is_covered_by_this_module))
    for name in COVERED_FUNCTIONS:
        # ยอมให้ขึ้นบรรทัดใหม่หลังวงเล็บได้ (ฟังก์ชันทางเขียนมี argument เยอะ)
        called = re.search(rf"repo\.{name}\(\s*live_db", source)
        assert called, f"ยังไม่มีเทสที่เรียก repo.{name}()"

