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

from ..helpers import assert_line_limits, flex_body_text

pytestmark = pytest.mark.integration


def _quick_reply_data(result: rt.RouteResult) -> list[str]:
    items = result.messages[0].get("quickReply", {}).get("items", [])
    return [item["action"]["data"] for item in items if item["action"].get("data")]


def _flex_documents_parts(message: dict) -> tuple[str, list[str], list[str]]:
    """
    ผ่า flex message ของรายการเอกสาร — คืน ``(altText, URL ทุกปุ่ม, ข้อความ
    ทุกกล่อง)`` เพราะข้อมูลที่เคยอยู่ใน ``text`` เดียวตอนนี้กระจายอยู่ใน
    กล่องของฟอง (แถวละฉบับ แตะเปิดทั้งแถว)
    """
    assert message.get("type") == "flex", message
    texts: list[str] = []
    urls: list[str] = []

    def walk(node: dict) -> None:
        if node.get("text"):
            texts.append(node["text"])
        if node.get("type") in ("button", "box") and node.get("action"):
            urls.append(node["action"]["uri"])
        for child in node.get("contents", []) or []:
            walk(child)
        for part in ("header", "hero", "body", "footer"):
            if node.get(part):
                walk(node[part])

    walk(message["contents"])
    return message["altText"], urls, texts


def test_document_menu_buttons_all_lead_to_real_answers(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    เมนูหมวดเอกสารสร้างปุ่มจากข้อมูลจริง 11 หมวด — ทุกปุ่มต้องกดได้

    ถ้าหมวดใดสะกดไม่ตรงกับที่ ``documents_in_category`` ใช้ค้น จะได้
    ``answered_by == "no_data"`` ซึ่งเป็นทางที่ผู้ใช้เจอบั๊กจริง ๆ

    คำตอบรายหมวดเป็น **Flex Message** (ฟองเดียว แถวละฉบับ) — ตรวจว่าทุก
    หมวดมีแถวแตะเปิดลิงก์และทุกแถวเป็น ``https://`` (ลิงก์ขาด = แถวเสีย)
    """
    menu = run(rt.handle_postback("action=documents", live_db))
    assert_line_limits(menu.messages)
    assert menu.answered_by == "quick_reply"

    targets = [
        data for data in _quick_reply_data(menu) if "cat=" in data
    ]
    assert len(targets) == 11

    for data in targets:
        answer = run(rt.handle_postback(data, live_db))
        assert answer.answered_by == "quick_reply", data
        assert_line_limits(answer.messages)
        assert answer.messages[0]["type"] == "flex", data
        _, urls, _ = _flex_documents_parts(answer.messages[0])
        assert urls, f"ทุกหมวดต้องมีแถวแตะเปิดเอกสาร: {data}"
        assert all(url.startswith("https://") for url in urls), data
        assert all(url.isascii() for url in urls), (
            f"URL ภาษาไทยต้อง encode ก่อนส่ง: {data}"
        )
        assert answer.citations, "citations ต้องตามมาด้วยสำหรับ chat_logs"


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
        assert answer.answered_by == "quick_reply", group
        assert answer.intent_key == f"instructors:{group}"
        assert_line_limits(answer.messages)
        assert group in flex_body_text(answer.messages[0])


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
    คำตอบเรื่องแผนการเรียนต้องพูดตัวเลขจริง และยอมรับส่วนที่ยังไม่รู้

    สถานะจริงตั้งแต่ 22 ส.ค. 2026: ``curriculum_rules`` มี 32 วิชาแล้ว
    (จึงคำนวณความก้าวหน้าได้) แต่ ``prerequisites`` ยังว่าง → ต้องไม่เคลม
    ว่ารู้เงื่อนไขวิชาบังคับก่อน
    """
    answer = run(rt.handle_postback("action=plan", live_db))
    text = answer.messages[0]["text"]

    assert answer.answered_by == "quick_reply"
    assert_line_limits(answer.messages)
    assert "แผนการเรียนมาตรฐาน 32 วิชา" in text
    assert "68 วิชา" in text
    assert "45 วิชา" in text
    assert "เทอม 1: 37" in text and "เทอม 2: 33" in text
    assert "ไม่ใช่เงื่อนไขบังคับ" in text
    assert "ยังจัดแผนรายเทอมให้ไม่ได้" not in text


def test_course_code_typed_as_text_answers_from_real_data(
    live_db: Database, run: Callable[..., Any]
) -> None:
    answer = run(rt.handle_text("1109902 เปิดเทอมไหน", live_db))
    text = answer.messages[0]["text"]

    assert answer.intent_key == "course:1109902"
    assert answer.answered_by == "course", "พิมพ์รหัสมาเอง ไม่ได้กดปุ่ม"
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


def test_course_button_examples_are_all_tappable(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ปุ่ม "ค้นรายวิชา" บน Rich Menu → ปุ่มวิชาตัวอย่าง → คำตอบจริง

    เทสทั้งวงจรกับข้อมูลจริง เพราะรหัสตัวอย่างมาจาก DB ไม่ได้ hardcode
    ถ้า re-scrape แล้วรหัสเปลี่ยน เทสนี้ยังต้องเขียว (ไม่ผูกกับรหัสตัวใด)
    """
    help_answer = run(rt.handle_postback("action=course&src=rich", live_db))

    assert help_answer.answered_by == "rich_menu"
    assert help_answer.intent_key == "course"
    assert_line_limits(help_answer.messages)
    assert "68 วิชา" in help_answer.messages[0]["text"]

    targets = [data for data in _quick_reply_data(help_answer) if "code=" in data]
    assert len(targets) == rt.SAMPLE_COURSE_COUNT

    for data in targets:
        code = rt.parse_postback_data(data)["code"]
        answer = run(rt.handle_postback(data, live_db))

        # ปุ่มตัวอย่างอยู่ใน Quick Reply ของคำตอบ ไม่ใช่บน Rich Menu
        # → ต้องนับเป็น quick_reply แม้ต้นทางจะกดมาจากเมนู
        assert answer.answered_by == "quick_reply", data
        assert answer.intent_key == f"course:{code}", data
        assert_line_limits(answer.messages)
        assert "เทอม" in answer.messages[0]["text"], code
        assert "ยังไม่พบว่าเปิดสอน" not in answer.messages[0]["text"], code


def test_course_without_pattern_does_not_claim_a_term(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    100 จาก 145 วิชาไม่มีแถวใน ``offering_patterns`` → ``opens_sem*`` เป็น ``None``

    ต้องตอบว่า "ยังไม่พบว่าเปิดสอน" ไม่ใช่เดาเทอมหรือพังเพราะ ``None``
    """
    answer = run(rt.handle_text("1109905", live_db))
    text = answer.messages[0]["text"]

    assert answer.answered_by == "course"
    assert "ภาษาจีนเพื่อการสื่อสาร" in text
    assert "ยังไม่พบว่าเปิดสอนในเทอมที่เก็บข้อมูลไว้" in text
    assert "เคยเปิด" not in text


def test_loan_menu_count_matches_loan_answer_count(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    เมนูบอกกี่ฉบับ กดเข้าไปต้องได้เท่านั้น — **เคยเป็นบั๊กที่แก้แล้ว**

    เดิม ``_documents_answer`` ไม่ส่ง ``limit`` → ใช้ default 10 ของ
    ``documents_in_category`` ทำให้เมนูเขียน "(12 ฉบับ)" แต่คำตอบแสดง
    แค่ 10 และเอกสาร 2 ฉบับท้ายหมวดเข้าถึงไม่ได้เลยจากบอท

    หมายเหตุ: ค่า default ของ ``documents_in_category`` **ยังเป็น 10**
    (ดู ``test_10_repository.py::test_default_limit_hides_two_loan_documents``)
    ที่แก้คือ router ส่ง limit เอง — ตอนย้ายเป็นฟองเดียวก็ต้องไม่ตัดแถวสั้น
    """
    menu = run(rt.handle_postback("action=documents", live_db))
    answer = run(rt.handle_postback("action=documents&cat=loan", live_db))
    message = answer.messages[0]

    assert "(12 ฉบับ)" in menu.messages[0]["text"]
    assert_line_limits(answer.messages)
    assert message["type"] == "flex"

    alt_text, urls, texts = _flex_documents_parts(message)
    # altText (ข้อความในรายการแชท) ต้องบอกจำนวนจริง และฟองเดียวต้องมีแถวครบ 12 แถว
    assert "12 ฉบับ" in alt_text
    rows = [
        content
        for content in message["contents"]["body"]["contents"]
        if content.get("type") == "box" and content.get("action")
    ]
    assert len(rows) == 12
    assert len(urls) == 12
    joined = "\n".join(texts)
    # สองฉบับที่เคยหายไปต้องอยู่ในแถวแล้ว
    assert "111 ตัวอย่างการทำสัญญา กรอ." in joined
    assert "หน้ารวมข้อมูลการกู้ยืมเงินเพื่อการศึกษา" in joined


def test_gpa_answer_uses_the_real_credit_numbers(
    live_db: Database, run: Callable[..., Any]
) -> None:
    """
    ข้อ 4.4 ต่อกับตัวเลขจริงของ planner — จุดที่ integration ต้องยืนยัน

    เทสระดับ unit ป้อนแผนสมมุติ 2 วิชา จึงไม่เคยเจอว่า "หน่วยกิตที่เหลือ"
    ที่คำตอบพูด มาจาก ``programs.total_credits`` จริงหรือไม่ ถ้าสองชั้นนี้
    หลุดจากกัน ตัวเลขในคำตอบจะดูสมเหตุสมผลแต่ผิด ซึ่งผู้ใช้จับไม่ได้

    ตัวเลขวันนี้ (23 ส.ค. 2026): ติ๊ก 22 วิชาแรกของแผน = 66 นก.
    หลักสูตรกำหนด 120 → เหลือ 54
    """
    from app import gpa
    from app import repository as repo

    from .conftest import TEST_HASH_PREFIX, cleanup_test_rows

    hash_value = TEST_HASH_PREFIX + "gpa"
    program_code = "643170151"

    user_id = run(repo.ensure_user(live_db, hash_value))
    run(repo.set_user_program(live_db, hash_value, program_code=program_code))
    plan = run(repo.curriculum_plan(live_db, program_code))
    ticked = plan[:22]
    run(
        repo.replace_completed_courses(
            live_db, user_id, [row["course_code"] for row in ticked]
        )
    )

    try:
        counted = sum(int(row["credits"] or 0) for row in ticked)
        program = run(repo.program_info(live_db, program_code))
        remaining = int(program["total_credits"]) - counted
        assert (counted, remaining) == (66, 54), "ข้อมูลจริงเปลี่ยนไป ให้แก้ตัวเลขในเทส"

        answer = run(
            rt.handle_text("เกรดตอนนี้ 2.75 อยากได้ 3.00", live_db, user_hash=hash_value)
        )
        text = answer.messages[0]["text"]

        assert answer.answered_by == "planner"
        assert answer.intent_key == "gpa_target"
        assert_line_limits(answer.messages)

        # ตัวเลขในคำตอบต้องเป็นชุดเดียวกับที่ repository รายงาน ไม่ใช่ค่าคงที่
        assert f"คิดเกรดแล้ว {counted} หน่วยกิต" in text
        assert f"เหลืออีก {remaining} หน่วยกิต" in text

        expected = gpa.plan_target(2.75, counted, remaining, 3.0)
        assert f"{expected.required:.2f}" in text
        assert expected.grade is not None and expected.grade in text

        # เป้าที่ไปไม่ถึงต้องบอกเพดานจริง ไม่ใช่ให้กำลังใจแบบผิดข้อมูล
        hopeless = run(
            rt.handle_text("เกรด 1.88 อยากได้ 3.00", live_db, user_hash=hash_value)
        )
        hopeless_text = hopeless.messages[0]["text"]
        ceiling = gpa.plan_target(1.88, counted, remaining, 3.0)

        assert ceiling.achievable is False
        assert "ไปไม่ถึง" in hopeless_text
        assert f"{ceiling.best_possible:.2f}" in hopeless_text
    finally:
        run(cleanup_test_rows(live_db))
