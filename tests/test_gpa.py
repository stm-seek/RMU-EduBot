"""
เทสการคำนวณเกรด (Requirement ข้อ 4.4) — คำนวณล้วน ไม่ต้องมี DB ไม่ต้องมีเน็ต

โฟกัสอยู่ที่ **เคสที่ตอบผิดแล้วนักศึกษาวางแผนผิดจริง**:

* บอกว่า "ยังลุ้นได้" ทั้งที่ได้ A ทุกวิชาแล้วก็ไปไม่ถึง → เสียเวลาทั้งปี
* ปัดแต้มที่ต้องได้ลง → ทำตามแล้วยังไม่ถึงเป้า
* อ่านรหัสวิชา/ปีการศึกษาเป็นเกรด → คำนวณจากเลขมั่ว
* หารด้วยศูนย์ตอนยังไม่มีเกรดเลย (นักศึกษาปี 1 เทอม 1) → บอตพัง
"""

from __future__ import annotations

import pytest

from app import gpa


# ── สูตรหลัก ─────────────────────────────────────────────────────────────────


def test_projection_matches_hand_calculation() -> None:
    """GPAX 2.75 จาก 66 นก. + อีก 54 นก. ได้ B หมด = (181.5 + 162) / 120"""
    assert gpa.project_gpax(2.75, 66, 54, 3.0) == pytest.approx(343.5 / 120)


def test_projection_survives_a_student_with_no_grades_yet() -> None:
    """
    ปี 1 เทอม 1 ยังไม่มีเกรดเลย — ต้องไม่หารด้วยศูนย์

    เป็นเคสที่เกิดขึ้นจริงกับผู้ใช้กลุ่มแรกของบอท (นักศึกษาใหม่)
    """
    assert gpa.project_gpax(0.0, 0, 18, 3.5) == 3.5
    assert gpa.project_gpax(0.0, 0, 0, 4.0) == 0.0


def test_required_average_is_none_when_nothing_is_left() -> None:
    """เก็บครบแล้ว GPAX เปลี่ยนไม่ได้อีก — ต้องไม่คืนเลขให้เข้าใจผิดว่ายังแก้ได้"""
    assert gpa.required_average(2.75, 120, 0, 3.0) is None


def test_required_average_is_not_capped_at_four() -> None:
    """
    เกิน 4.00 คือข้อมูลที่ผู้ใช้ต้องรู้ ไม่ใช่ค่าที่ต้องปัดลงให้ดูสวย

    ถ้าตัดเพดานที่นี่ ชั้นคำตอบจะแยกไม่ออกระหว่าง "ต้องได้ A หมด"
    กับ "ไปไม่ถึงแล้ว" ซึ่งเป็นคำแนะนำคนละเรื่องกัน
    """
    needed = gpa.required_average(1.88, 90, 30, 3.0)
    assert needed is not None and needed > gpa.MAX_GRADE_POINT


# ── การปัดเศษ ────────────────────────────────────────────────────────────────


def test_required_average_rounds_up_never_down() -> None:
    """
    ต้องได้เฉลี่ย 3.3056 → ต้องบอก 3.31 ไม่ใช่ 3.30

    ปัดลงคือคำแนะนำที่ผิด: ทำตามเป๊ะแล้วยังไม่ถึงเป้า
    """
    plan = gpa.plan_target(2.75, 66, 54, 3.0)
    assert plan.required == 3.31


def test_rounding_does_not_use_bankers_rounding() -> None:
    """round() ของ Python ปัดครึ่งไปหาเลขคู่ (2.675 -> 2.67) ซึ่งอธิบายให้ผู้ใช้ไม่ได้"""
    assert gpa.round_gpax(2.675) == 2.68
    assert round(2.675, 2) == 2.67, "ยืนยันว่า round() ของ Python ทำแบบนั้นจริง"


# ── ทำได้ / ทำไม่ได้ / ถึงแน่แล้ว — สามคำตอบที่ต้องไม่ปนกัน ────────────────────


def test_impossible_target_is_reported_as_impossible() -> None:
    """
    GPAX 1.88 เหลือ 30 นก. อยากได้ 3.00 — ได้ A ทุกวิชาก็ได้แค่ 2.41

    ต้องตอบว่าไปไม่ถึง พร้อมบอกเพดานจริง ไม่ใช่ให้กำลังใจแบบผิดข้อมูล
    """
    plan = gpa.plan_target(1.88, 90, 30, 3.0)

    assert plan.achievable is False
    assert plan.hopeless is True
    assert plan.grade is None, "ไปไม่ถึงแล้ว จะแนะนำเกรดไม่ได้"
    assert plan.best_possible == 2.41


def test_target_already_secured_is_not_reported_as_work_to_do() -> None:
    """GPAX 3.9 เหลือ 20 นก. อยากได้ 3.00 — ได้ F ทุกวิชาก็ยังถึง"""
    plan = gpa.plan_target(3.9, 100, 20, 3.0)

    assert plan.guaranteed is True
    assert plan.achievable is True


def test_exactly_four_point_zero_still_counts_as_achievable() -> None:
    """
    ต้องได้ A ทุกวิชาพอดี = ยังทำได้ ห้ามตกไปอยู่ฝั่ง "เป็นไปไม่ได้"

    เคสขอบที่พลาดง่ายเพราะเทียบ float — 3.9999999 ต้องนับว่าถึง 4.00
    """
    plan = gpa.plan_target(3.0, 60, 60, 3.5)

    assert plan.required == 4.0
    assert plan.achievable is True
    assert plan.grade == "A"


def test_finished_student_cannot_change_the_outcome() -> None:
    """เก็บครบ 120 นก. แล้ว — ตอบได้แค่ว่าถึงหรือไม่ถึง ไม่ใช่ต้องทำอะไรต่อ"""
    reached = gpa.plan_target(3.60, 120, 0, 3.50)
    missed = gpa.plan_target(3.20, 120, 0, 3.50)

    assert reached.required is None and reached.achievable is True
    assert missed.required is None and missed.achievable is False
    assert missed.remaining_credits == 0


# ── วิเคราะห์หลายกรณี ────────────────────────────────────────────────────────


def test_scenarios_are_ordered_high_to_low_and_carry_honors_flags() -> None:
    rows = gpa.scenarios(2.75, 66, 54)

    assert [row.grade for row in rows] == ["A", "B+", "B", "C+", "C"]
    assert [row.final_gpax for row in rows] == sorted(
        (row.final_gpax for row in rows), reverse=True
    )
    assert rows[0].honors == "อันดับ 2", "3.31 ถึงเกณฑ์อันดับ 2 (3.25)"
    assert rows[-1].honors is None


def test_scenarios_are_empty_when_no_credits_remain() -> None:
    """ไม่เหลือหน่วยกิต = ไม่มีกรณีให้วิเคราะห์ ต้องไม่ปั้นตารางเปล่าออกมา"""
    assert gpa.scenarios(3.2, 120, 0) == ()


# ── เกียรตินิยม ──────────────────────────────────────────────────────────────


def test_honors_outlook_separates_a_closed_door_from_an_open_one() -> None:
    """GPAX 3.20 เหลือ 30 นก. — อันดับ 1 ต้องเฉลี่ย 4.4 (ปิด) อันดับ 2 ยังลุ้นได้"""
    first, second = gpa.honors_outlook(3.20, 90, 30)

    assert first.label == "เกียรตินิยมอันดับ 1"
    assert first.achievable is False
    assert second.achievable is True
    assert second.grade == "B+"


def test_honors_rank_uses_the_documented_thresholds() -> None:
    assert gpa.honors_rank(gpa.HONORS_FIRST) == "อันดับ 1"
    assert gpa.honors_rank(gpa.HONORS_SECOND) == "อันดับ 2"
    assert gpa.honors_rank(gpa.HONORS_SECOND - 0.01) is None


# ── ผลกระทบของวิชาเดียว ───────────────────────────────────────────────────────


def test_one_course_moves_the_gpax_both_ways() -> None:
    """ข้อ 4.4 "ตรวจสอบผลกระทบ" — วิชา 3 นก. ตัวเดียวขยับ GPAX ได้จริง"""
    assert gpa.course_impact(2.75, 66, 3, "A") == 2.8
    assert gpa.course_impact(2.75, 66, 3, "F") == 2.63


# ── อ่านตัวเลขจากข้อความจริง ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "text, gpax, target",
    [
        ("เกรดตอนนี้ 2.75 อยากได้ 3.00", 2.75, 3.0),
        ("อยากได้ 3 ตอนนี้ได้ 2.75", 2.75, 3.0),
        ("gpa 2.5 อยากขึ้นเป็น 3.25", 2.5, 3.25),
        ("เกรด 2.75 3.00", 2.75, 3.0),
        ("GPA 1.88 จบได้ไหม", 1.88, None),
        ("อยากได้ 3.5 ต้องทำยังไง", None, 3.5),
        ("เกรดเฉลี่ยคิดยังไง", None, None),
    ],
)
def test_parsing_finds_the_numbers_in_real_phrasings(
    text: str, gpax: float | None, target: float | None
) -> None:
    """
    คนพิมพ์ไม่เรียงลำดับตามที่เราคิด — ต้องรอดทั้งสองทาง

    เคส "เกรด 2.75 3.00" (ไม่มีคำใบ้เลย) ตีความว่าเลขแรกคือตอนนี้
    เลขที่สองคือเป้า ซึ่งเป็นลำดับที่คนพิมพ์กันโดยธรรมชาติ
    """
    question = gpa.parse_question(text)

    assert question.gpax == gpax
    assert question.target == target


@pytest.mark.parametrize(
    "text",
    [
        "เกรดวิชา 1109902",       # รหัสวิชา 7 หลัก
        "เกรดเทอม 2568",          # ปีการศึกษา
        "เกรดเฉลี่ย 22 หน่วยกิต",  # เพดานหน่วยกิต
    ],
)
def test_parsing_ignores_numbers_that_are_not_grades(text: str) -> None:
    """
    เลขที่ไม่ใช่เกรดต้องไม่ถูกอ่านเป็นเกรด

    ถ้าไม่กัน "เกรดวิชา 1109902" จะกลายเป็น GPAX = 1 แล้วบอตคำนวณจากเลขมั่ว
    โดยที่ผู้ใช้ไม่รู้เลยว่าตัวเลขมาจากไหน
    """
    assert gpa.parse_question(text).gpax is None


def test_parsing_rejects_out_of_range_values() -> None:
    """เกรด 5.00 ไม่มีในสเกล — ต้องทิ้ง ไม่ใช่คำนวณต่อ"""
    assert gpa.parse_question("เกรด 5.00").gpax is None
    assert gpa.parse_question("เกรด 4.00").gpax == 4.0


def test_parsing_reads_a_manual_credit_override() -> None:
    """
    ผู้ใช้ต้องแก้จำนวนหน่วยกิตที่คิดเกรดแล้วได้เอง

    เพราะ "วิชาที่ผ่าน" ที่ planner รู้ ไม่เท่ากับ "หน่วยกิตที่คิดใน GPAX"
    เมื่อมีวิชาติด F / เทียบโอน / ตัดสินผลเป็น S-U
    """
    assert gpa.parse_question("เกรด 2.5 เก็บไปแล้ว 72 หน่วยกิต").credits_counted == 72
    assert gpa.parse_question("เกรด 2.5 คิดเกรดแล้ว 72 นก.").credits_counted == 72
    assert gpa.parse_question("เกรด 2.5").credits_counted is None


def test_parsing_flags_an_honors_question() -> None:
    assert gpa.parse_question("ยังลุ้นเกียรตินิยมได้ไหม เกรด 3.4").wants_honors is True
    assert gpa.parse_question("เกรด 3.4 อยากได้ 3.5").wants_honors is False
