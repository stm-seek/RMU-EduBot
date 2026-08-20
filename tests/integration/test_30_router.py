"""
เทส router ตั้งแต่ต้นจนจบด้วยข้อมูลจริง — ปุ่มที่บอทสร้างเอง กดแล้วต้องได้คำตอบ

เทสเดิม (:mod:`tests.test_router`) ใช้ ``FakeDatabase`` ที่ป้อนแถวสมมุติสั้น ๆ
จึงไม่เคยเจอของจริงสองอย่าง: ชื่อกลุ่มภาษาไทยที่มีวงเล็บ/จุด ต้องรอดจาก
``parse_qsl`` ใน postback data, และจำนวนแถวจริงที่ชน ``LIMIT``

ไม่แตะ LINE API เลย (เทสระดับ ``RouteResult`` เท่านั้น) และไม่เปิดเซิร์ฟเวอร์
"""

from __future__ import annotations

from typing import Any, Callable

import pytest

from app import repository as repo
from app import router as rt
from app.db import Database

from ..helpers import assert_line_limits

pytestmark = pytest.mark.integration


def _quick_reply_data(result: rt.RouteResult) -> list[str]:
    items = result.messages[0].get("quickReply", {}).get("items", [])
    return [item["action"]["data"] for item in items if item["action"].get("data")]


def test_document_menu_buttons_all_lead_to_real_answers(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    เมนูหมวดเอกสารสร้างปุ่มจากข้อมูลจริง 10 หมวด — ทุกปุ่มต้องกดได้

    ถ้าหมวดใดสะกดไม่ตรงกับที่ ``documents_in_category`` ใช้ค้น จะได้
    ``answered_by == "no_data"`` ซึ่งเป็นทางที่ผู้ใช้เจอบั๊กจริง ๆ
    """
    menu = run(rt.handle_postback("action=documents", live_db))
    assert_line_limits(menu.messages)
    assert menu.answered_by == "rich_menu"

    targets = [
        data for data in _quick_reply_data(menu) if "cat=" in data
    ]
    assert len(targets) == 10

    for data in targets:
        answer = run(rt.handle_postback(data, live_db))
        assert answer.answered_by == "rich_menu", data
        assert_line_limits(answer.messages)
        assert "https://" in answer.messages[0]["text"], data


def test_instructor_group_buttons_survive_postback_round_trip(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ชื่อกลุ่มจริงมีวงเล็บ จุด และช่องว่าง (เช่น ``ปร.ด.การจัดการเทคโนโลยี``)

    ค่านั้นถูกยัดเข้า postback data แบบไม่ urlencode แล้วอ่านกลับด้วย
    ``parse_qsl`` — ถ้ามีอักขระที่ ``parse_qsl`` แปลง (``&``, ``=``, ``+``)
    ชื่อจะเพี้ยนและ query จะไม่เจอใคร เทสนี้ยืนยันกับชื่อจริงทั้ง 6 กลุ่ม
    """
    menu = run(rt.handle_postback("action=instructors", live_db))
    assert_line_limits(menu.messages)

    groups = [row["group_name"] for row in run(repo.instructor_groups(live_db))]
    targets = [data for data in _quick_reply_data(menu) if "g=" in data]
    assert len(targets) == len(groups) == 6

    for data, group in zip(targets, groups):
        assert rt.parse_postback_data(data)["g"] == group, data
        answer = run(rt.handle_postback(data, live_db))
        assert answer.answered_by == "rich_menu", group
        assert answer.intent_key == f"instructors:{group}"
        assert_line_limits(answer.messages)
        assert group in answer.messages[0]["text"]


def test_instructor_answer_shows_real_contact_caveat(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """ตัวเลขในคำเตือนต้องเป็นค่าจริงจาก DB ไม่ใช่ข้อความคงที่"""
    menu = run(rt.handle_postback("action=instructors", live_db))
    text = menu.messages[0]["text"]

    assert "อีเมล 26/28 คน" in text
    assert "ยังไม่มีเบอร์โทรในระบบ" in text


def test_plan_answer_reports_the_real_gap(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    คำตอบเรื่องแผนการเรียนต้องพูดตัวเลขจริงและยอมรับว่าจัดแผนให้ไม่ได้

    (``prerequisites`` / ``curriculum_rules`` ยังว่าง รอ มคอ.2)
    """
    answer = run(rt.handle_postback("action=plan", live_db))
    text = answer.messages[0]["text"]

    assert answer.answered_by == "rich_menu"
    assert_line_limits(answer.messages)
    assert "68 วิชา" in text
    assert "45 วิชา" in text
    assert "เทอม 1: 37" in text and "เทอม 2: 33" in text
    assert "มคอ.2" in text


def test_course_code_typed_as_text_answers_from_real_data(
    live_db: Database, run: Callable[..., Any]
) -> None:
    answer = run(rt.handle_text("1109902 เปิดเทอมไหน", live_db))
    text = answer.messages[0]["text"]

    assert answer.intent_key == "course:1109902"
    assert answer.answered_by == "rich_menu"
    assert_line_limits(answer.messages)
    assert "ภาษาไทยเพื่อการสื่อสาร" in text
    assert "3 (2-2-5)" in text
    assert "เทอม 1, เทอม 2" in text
    assert "จาก 4 เทอมที่เก็บข้อมูลไว้" in text


def test_unknown_course_code_says_no_data(
    live_db: Database, run: Callable[..., Any]
) -> None:
    answer = run(rt.handle_text("9999999", live_db))

    assert answer.answered_by == "no_data"
    assert answer.intent_key == "course:9999999"
    assert_line_limits(answer.messages)


def test_course_without_pattern_does_not_claim_a_term(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    100 จาก 145 วิชาไม่มีแถวใน ``offering_patterns`` → ``opens_sem*`` เป็น ``None``

    ต้องตอบว่า "ยังไม่พบว่าเปิดสอน" ไม่ใช่เดาเทอมหรือพังเพราะ ``None``
    """
    answer = run(rt.handle_text("1109905", live_db))
    text = answer.messages[0]["text"]

    assert answer.answered_by == "rich_menu"
    assert "ภาษาจีนเพื่อการสื่อสาร" in text
    assert "ยังไม่พบว่าเปิดสอนในเทอมที่เก็บข้อมูลไว้" in text
    assert "เคยเปิด" not in text


def test_loan_menu_count_matches_loan_answer_count(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    เมนูบอกกี่ฉบับ กดเข้าไปต้องได้เท่านั้น — **เคยเป็นบั๊กที่แก้แล้ว**

    เดิม ``_documents_answer`` ไม่ส่ง ``limit`` → ใช้ default 10 ของ
    ``documents_in_category`` ทำให้เมนูเขียน "(12 ฉบับ)" แต่คำตอบเขียน
    "(10 ฉบับ)" และเอกสาร 2 ฉบับท้ายหมวดเข้าถึงไม่ได้เลยจากบอท

    หมายเหตุ: ค่า default ของ ``documents_in_category`` **ยังเป็น 10**
    (ดู ``test_10_repository.py::test_default_limit_hides_two_loan_documents``)
    ที่แก้คือ router ส่ง limit เอง
    """
    menu = run(rt.handle_postback("action=documents", live_db))
    answer = run(rt.handle_postback("action=documents&cat=loan", live_db))
    text = answer.messages[0]["text"]

    assert "(12 ฉบับ)" in menu.messages[0]["text"]
    assert "(12 ฉบับ)" in text
    # สองฉบับที่เคยหายไปต้องอยู่ในคำตอบแล้ว
    assert "111 ตัวอย่างการทำสัญญา กรอ." in text
    assert "หน้ารวมข้อมูลการกู้ยืมเงินเพื่อการศึกษา" in text
    assert_line_limits(answer.messages)
