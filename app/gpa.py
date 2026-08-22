"""
คำนวณเกรด — "ให้คำปรึกษาด้านผลการเรียน" (Requirement ข้อ 4.4)

**ทุกอย่างในไฟล์นี้เป็นการคำนวณล้วน ไม่มี LLM ไม่มี I/O** เหตุผลเดียวกับ
:mod:`app.planner`: ถ้าตอบเลขผิด นักศึกษาวางแผนผิดจริง (เข้าใจว่าลุ้นเกียรตินิยม
ได้ทั้งที่ไปไม่ถึงแล้ว) ข้อ 4.4 เองก็ระบุว่าการคำนวณต้องเป็น deterministic code

ที่ต้องรู้ก่อนอ่านผลลัพธ์
------------------------

* **ระบบนี้ไม่เก็บเกรด** (ดู ``db/migrations/001_init.sql`` ส่วนที่ 3) — GPAX
  ปัจจุบันมาจากที่ผู้ใช้พิมพ์บอกในแชท ใช้คำนวณแล้วทิ้ง ไม่เขียนลงตารางใด ๆ
  จึงไม่ต้องขอความยินยอมเพิ่ม และคำเคลมในบทที่ 3 ยังเป็นจริง
* จำนวน "หน่วยกิตที่คิดเกรดแล้ว" **ไม่เท่ากับ** ``Progress.passed_credits``
  เสมอไป ต่างกันจริงสามกรณี: วิชาที่ติด F (คิดใน GPAX แต่ไม่ผ่าน), วิชา
  เทียบโอน (ผ่านแต่ไม่คิดเกรด), วิชาที่ตัดสินผลเป็น S/U → ชั้นที่เรียกใช้
  ต้องบอกผู้ใช้ว่าใช้เลขอะไรคิด และให้แก้ได้ ห้ามเอาของ planner ไปใช้เงียบ ๆ
* ตารางแต้มเกรดและเกณฑ์เกียรตินิยมข้างล่าง **ยังไม่ได้ยืนยันกับเล่มข้อบังคับ
  RMU** (ไม่มีระเบียบเรื่องการวัดผลในคลังเอกสารที่ scrape มา — ตรวจ 23 ส.ค.
  2026) จึงทำเป็นค่าคงที่จุดเดียวให้แก้ง่าย และคำตอบต้องบอกว่าคิดด้วยสเกลไหน
* **การลงเรียนซ้ำเพื่อแก้เกรด** ยังไม่รองรับ เพราะไม่รู้ว่าข้อบังคับให้นับ
  ทั้งสองครั้งหรือให้แทนครั้งเก่า ซึ่งเปลี่ยนคำตอบคนละทาง — ยังไม่รู้ = ไม่ตอบ
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

# ── ค่าคงที่ที่ยังต้องยืนยันกับเล่มข้อบังคับ ─────────────────────────────────

#: แต้มประจำเกรด (สเกล 8 ระดับที่ใช้กันทั่วไปในมหาวิทยาลัยไทย)
#:
#: W (ถอน) / S / U / I / P ไม่อยู่ในนี้เพราะไม่นำมาคิดค่าเฉลี่ย — ถ้าผู้ใช้
#: ถามถึง ต้องตอบว่าไม่คิดในค่าเฉลี่ย ไม่ใช่ให้แต้ม 0 (คนละความหมายกับ F)
GRADE_POINTS: dict[str, float] = {
    "A": 4.0,
    "B+": 3.5,
    "B": 3.0,
    "C+": 2.5,
    "C": 2.0,
    "D+": 1.5,
    "D": 1.0,
    "F": 0.0,
}

MAX_GRADE_POINT = 4.0

#: เกรดที่เอามาไล่ "ถ้าได้เท่านี้ทุกวิชาที่เหลือ" — ตอบข้อ 4.4 หัวข้อ
#: "วิเคราะห์หลายกรณี" ไม่ไล่ครบ 8 ระดับเพราะข้อความจะยาวเกินจำเป็น
#: (D/D+ ไม่ค่อยมีใครตั้งเป้า และ F แปลว่าไม่จบ ไม่ใช่ GPAX ต่ำ)
SCENARIO_GRADES: tuple[str, ...] = ("A", "B+", "B", "C+", "C")

#: เกณฑ์เกียรตินิยม — **ยังไม่ยืนยัน** ตัวเลขที่พบทั่วไปคือ 3.50 / 3.25
#: และยังมีเงื่อนไขอื่นที่ระบบไม่รู้ (ไม่เคยได้ F, ไม่เคยลงซ้ำ, จบในเวลา,
#: ไม่ใช่นักศึกษาเทียบโอน) → คำตอบต้องพูดว่า "เฉพาะเกณฑ์ GPAX" เท่านั้น
HONORS_FIRST = 3.50
HONORS_SECOND = 3.25

# ความคลาดเคลื่อนที่ยอมให้ตอนเทียบ float — 3.4999999 ต้องนับว่าถึง 3.50
EPSILON = 1e-9


# ── ปัดเศษ ───────────────────────────────────────────────────────────────────


def round_gpax(value: float) -> float:
    """
    ปัดเป็นทศนิยม 2 ตำแหน่งแบบครึ่งขึ้น — ใช้กับ "ผลลัพธ์ที่คาดว่าจะได้"

    ไม่ใช้ :func:`round` ของ Python เพราะมันปัดครึ่งไปหาเลขคู่
    (``round(2.675, 2)`` ได้ 2.67) ซึ่งอธิบายให้ผู้ใช้ไม่ได้

    >>> round_gpax(2.6666666)
    2.67
    >>> round_gpax(2.675)
    2.68
    >>> round_gpax(3.0)
    3.0
    """
    return math.floor(value * 100 + 0.5) / 100


def ceil_gpax(value: float) -> float:
    """
    ปัด **ขึ้น** 2 ตำแหน่ง — ใช้กับ "แต้มที่ต้องได้เป็นอย่างน้อย"

    ต้องปัดขึ้นเท่านั้น: ถ้าต้องได้เฉลี่ย 3.4167 แล้วไปบอกว่า 3.41
    นักศึกษาทำตามแล้วยังไม่ถึงเป้า — คำแนะนำที่ปัดลงคือคำแนะนำที่ผิด

    >>> ceil_gpax(3.4167)
    3.42
    >>> ceil_gpax(3.0)
    3.0
    """
    return math.ceil(value * 100 - EPSILON) / 100


# ── สูตรหลัก 2 สูตร ที่ครอบทุกหัวข้อย่อยของข้อ 4.4 ────────────────────────────


def project_gpax(
    gpax: float, credits_counted: int, added_credits: int, grade_point: float
) -> float:
    """
    GPAX ใหม่ ถ้าได้ ``grade_point`` เท่ากันหมดในอีก ``added_credits`` หน่วยกิต

    ``(แต้มรวมเดิม + แต้มใหม่) / หน่วยกิตรวม`` — สูตรเดียวนี้ตอบได้ทั้ง
    "วิเคราะห์หลายกรณี" และ "ตรวจสอบผลกระทบของวิชาเดียว" (ใส่หน่วยกิตวิชานั้น)

    >>> project_gpax(2.75, 66, 54, 4.0)   # เหลือ 54 นก. ได้ A หมด
    3.3125
    >>> round_gpax(project_gpax(2.75, 66, 54, 3.0))
    2.86
    >>> project_gpax(0.0, 0, 12, 3.5)     # ปี 1 ยังไม่มีเกรดเลย
    3.5

    ไม่มีหน่วยกิตเลยทั้งสองฝั่ง = ยังไม่มีอะไรให้คิด

    >>> project_gpax(0.0, 0, 0, 4.0)
    0.0
    """
    total_credits = credits_counted + added_credits
    if total_credits <= 0:
        return 0.0
    return (gpax * credits_counted + grade_point * added_credits) / total_credits


def required_average(
    gpax: float, credits_counted: int, remaining_credits: int, target: float
) -> float | None:
    """
    แต้มเฉลี่ยที่ต้องได้ในหน่วยกิตที่เหลือ เพื่อให้ GPAX สุดท้ายถึง ``target``

    คืน ``None`` เมื่อไม่เหลือหน่วยกิตให้เก็บแล้ว (GPAX เปลี่ยนไม่ได้อีก)

    ค่าที่ได้ **ไม่ถูกตัดเพดาน** โดยเจตนา: เกิน 4.00 คือสัญญาณว่าเป้านี้
    เป็นไปไม่ได้ ซึ่งผู้ใช้ต้องรู้ ไม่ใช่ปัดลงมาเป็น 4.00 ให้ดูเหมือนทำได้

    >>> round(required_average(2.75, 66, 54, 3.0), 4)
    3.3056
    >>> required_average(2.0, 100, 20, 4.0) > MAX_GRADE_POINT   # ไปไม่ถึงแล้ว
    True
    >>> required_average(3.9, 100, 20, 3.0) < 0                 # ถึงแน่แล้ว
    True
    >>> required_average(2.75, 120, 0, 3.0) is None
    True
    """
    if remaining_credits <= 0:
        return None
    total_credits = credits_counted + remaining_credits
    return (target * total_credits - gpax * credits_counted) / remaining_credits


# ── ผลลัพธ์ที่ส่งต่อให้ชั้นประกอบคำตอบ ─────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Scenario:
    """หนึ่งบรรทัดของ "ถ้าได้เกรดนี้ทุกวิชาที่เหลือ" """

    grade: str
    grade_point: float
    final_gpax: float
    honors: str | None = None


@dataclass(frozen=True, slots=True)
class TargetPlan:
    """
    เป้าหมายหนึ่งเป้า ตอบได้ครบว่า "ต้องได้เท่าไร" และ "ทำได้จริงไหม"

    :attr:`achievable` แยกจาก :attr:`guaranteed` เพราะเป็นสองคำตอบที่ต่างกัน:
    เป้าที่ยังทำได้แต่ต้องพยายาม กับเป้าที่ถึงแน่แล้วไม่ว่าจะได้เกรดอะไร
    """

    target: float
    required: float | None
    grade: str | None
    achievable: bool
    guaranteed: bool
    best_possible: float
    remaining_credits: int
    label: str = ""

    @property
    def hopeless(self) -> bool:
        """เป้านี้ปิดประตูแล้ว — ต้องบอกตรง ๆ ไม่ใช่ให้กำลังใจแบบผิดข้อมูล"""
        return not self.achievable


def is_valid_gpax(value: float) -> bool:
    """
    >>> is_valid_gpax(2.75), is_valid_gpax(0.0), is_valid_gpax(4.0)
    (True, True, True)
    >>> is_valid_gpax(4.01), is_valid_gpax(-0.5)
    (False, False)
    """
    return 0.0 <= value <= MAX_GRADE_POINT + EPSILON


def lowest_grade_reaching(average: float) -> str | None:
    """
    เกรดต่ำสุดที่แต้มยังถึง ``average`` — ``None`` ถ้าเกิน A

    >>> lowest_grade_reaching(3.3056)
    'B+'
    >>> lowest_grade_reaching(3.5)
    'B+'
    >>> lowest_grade_reaching(4.0)
    'A'
    >>> lowest_grade_reaching(4.2) is None
    True
    """
    for grade in sorted(GRADE_POINTS, key=lambda name: GRADE_POINTS[name]):
        if GRADE_POINTS[grade] + EPSILON >= average:
            return grade
    return None


def honors_rank(gpax: float) -> str | None:
    """
    ได้เกียรตินิยมอันดับไหน **โดยดูแค่ GPAX** (เงื่อนไขอื่นระบบไม่รู้)

    >>> honors_rank(3.62)
    'อันดับ 1'
    >>> honors_rank(3.25)
    'อันดับ 2'
    >>> honors_rank(3.24) is None
    True
    """
    if gpax + EPSILON >= HONORS_FIRST:
        return "อันดับ 1"
    if gpax + EPSILON >= HONORS_SECOND:
        return "อันดับ 2"
    return None


# ── ฟังก์ชันที่ชั้นคำตอบเรียกใช้จริง ────────────────────────────────────────────


def scenarios(
    gpax: float,
    credits_counted: int,
    remaining_credits: int,
    grades: tuple[str, ...] = SCENARIO_GRADES,
) -> tuple[Scenario, ...]:
    """
    "ถ้าได้ A ทุกวิชา / B+ ทุกวิชา / ... GPAX สุดท้ายเป็นเท่าไร"

    ตอบข้อ 4.4 หัวข้อ "วิเคราะห์หลายกรณีของผลการเรียน" ตรง ๆ

    >>> for row in scenarios(2.75, 66, 54, grades=('A', 'B', 'C')):
    ...     print(row.grade, row.final_gpax, row.honors)
    A 3.31 อันดับ 2
    B 2.86 None
    C 2.41 None

    ไม่เหลือหน่วยกิตแล้ว = ไม่มีกรณีให้วิเคราะห์

    >>> scenarios(3.2, 120, 0)
    ()
    """
    if remaining_credits <= 0:
        return ()
    rows = []
    for grade in grades:
        point = GRADE_POINTS[grade]
        final = round_gpax(project_gpax(gpax, credits_counted, remaining_credits, point))
        rows.append(
            Scenario(
                grade=grade,
                grade_point=point,
                final_gpax=final,
                honors=honors_rank(final),
            )
        )
    return tuple(rows)


def plan_target(
    gpax: float,
    credits_counted: int,
    remaining_credits: int,
    target: float,
    *,
    label: str = "",
) -> TargetPlan:
    """
    ต้องได้เกรดเท่าไรในวิชาที่เหลือ เพื่อให้ GPAX ถึง ``target``

    ตอบข้อ 4.4 สามหัวข้อรวดเดียว: "คำนวณ GPA เป้าหมาย", "เกรดเฉลี่ยสะสม
    ที่ต้องการ" และ "เกรดที่ต้องได้ในรายวิชาที่เหลือ"

    เป้าที่ทำได้:

    >>> plan = plan_target(2.75, 66, 54, 3.0)
    >>> plan.required, plan.grade, plan.achievable, plan.guaranteed
    (3.31, 'B+', True, False)

    เป้าที่ปิดประตูแล้ว — ต้องรู้ว่าสูงสุดที่ทำได้คือเท่าไร:

    >>> plan = plan_target(1.88, 90, 30, 3.0)
    >>> plan.achievable, plan.best_possible
    (False, 2.41)
    >>> plan.hopeless
    True

    เป้าที่ถึงแน่แล้วไม่ว่าจะได้อะไร:

    >>> plan_target(3.9, 100, 20, 3.0).guaranteed
    True

    เก็บครบแล้ว แก้ไม่ได้อีก:

    >>> done = plan_target(3.2, 120, 0, 3.5)
    >>> done.required is None, done.achievable
    (True, False)
    """
    best = round_gpax(
        project_gpax(gpax, credits_counted, remaining_credits, MAX_GRADE_POINT)
    )
    needed = required_average(gpax, credits_counted, remaining_credits, target)

    if needed is None:
        # ไม่เหลือหน่วยกิตให้เก็บ → GPAX ปัจจุบันคือคำตอบสุดท้ายไปแล้ว
        return TargetPlan(
            target=target,
            required=None,
            grade=None,
            achievable=gpax + EPSILON >= target,
            guaranteed=gpax + EPSILON >= target,
            best_possible=round_gpax(gpax),
            remaining_credits=0,
            label=label,
        )

    guaranteed = needed <= EPSILON
    achievable = needed <= MAX_GRADE_POINT + EPSILON
    return TargetPlan(
        target=target,
        required=ceil_gpax(max(needed, 0.0)),
        grade=lowest_grade_reaching(needed) if achievable else None,
        achievable=achievable,
        guaranteed=guaranteed,
        best_possible=best,
        remaining_credits=remaining_credits,
        label=label,
    )


def honors_outlook(
    gpax: float, credits_counted: int, remaining_credits: int
) -> tuple[TargetPlan, ...]:
    """
    ยังลุ้นเกียรตินิยมได้ไหม — คิดเฉพาะเกณฑ์ GPAX

    เหลือ 30 หน่วยกิต GPAX 3.20 — อันดับ 1 ปิดประตูแล้ว (ต้องได้เฉลี่ย 4.4
    ซึ่งเกิน A) แต่อันดับ 2 ยังลุ้นได้ถ้าได้ B+ ขึ้นไปทุกวิชา

    >>> for plan in honors_outlook(3.20, 90, 30):
    ...     print(plan.label, plan.required, plan.grade, plan.achievable)
    เกียรตินิยมอันดับ 1 4.4 None False
    เกียรตินิยมอันดับ 2 3.4 B+ True
    """
    return (
        plan_target(
            gpax, credits_counted, remaining_credits, HONORS_FIRST,
            label="เกียรตินิยมอันดับ 1",
        ),
        plan_target(
            gpax, credits_counted, remaining_credits, HONORS_SECOND,
            label="เกียรตินิยมอันดับ 2",
        ),
    )


def course_impact(
    gpax: float, credits_counted: int, course_credits: int, grade: str
) -> float:
    """
    "ถ้าวิชานี้ได้เกรดนี้ GPAX จะเป็นเท่าไร" — ข้อ 4.4 หัวข้อ "ตรวจสอบผลกระทบ"

    สูตรเดียวกับ :func:`project_gpax` แค่ใส่หน่วยกิตของวิชาเดียว

    >>> course_impact(2.75, 66, 3, 'A')
    2.8
    >>> course_impact(2.75, 66, 3, 'F')
    2.63
    """
    return round_gpax(
        project_gpax(gpax, credits_counted, course_credits, GRADE_POINTS[grade])
    )


# ── อ่านตัวเลขจากข้อความที่ผู้ใช้พิมพ์ ──────────────────────────────────────────
#
# แยกไว้ที่นี่ (ไม่ใช่ใน progress.py) เพราะเป็นความรู้เรื่อง "เลขแบบไหนคือเกรด"
# ซึ่งเป็นเรื่องเดียวกับสูตรข้างบน ส่วน progress.py ตัดสินแค่ว่าคำถามควรมาทางนี้ไหม

# เลข 0–4 ทศนิยมไม่เกิน 2 ตำแหน่ง และต้องไม่มีเลขติดหน้า/หลัง
#
# ตัวกันเลขติดกันสำคัญมาก: รหัสวิชา '1109902' และปีการศึกษา '2568' มีเลข
# 0–4 อยู่ข้างใน ถ้าไม่กัน "เกรดวิชา 1109902" จะถูกอ่านว่า GPAX = 1
NUMBER_PATTERN = re.compile(r"(?<![\d.])([0-4](?:\.\d{1,2})?)(?![\d])")

# คำที่บอกว่า "เลขถัดจากนี้คือเป้าหมาย" ไม่ใช่ผลปัจจุบัน
#
# ไม่ใส่ "ต้องได้" เพราะมันมักเป็นตัวคำถามเอง ("ต้องได้เกรดเท่าไหร่")
# ไม่ใช่ค่าของเป้า
TARGET_CUE = re.compile(
    r"อยากได้|อยากให้ได้|อยากขึ้น|ต้องการ|เป้า|ให้ถึง|ให้ได้|ทำให้ได้|ขึ้นเป็น|ไปถึง|target"
)

# "เก็บไปแล้ว 66 หน่วยกิต" — ให้ผู้ใช้แก้จำนวนหน่วยกิตที่คิดเกรดแล้วได้เอง
#
# จำเป็นจริง ไม่ใช่ของแถม: หน่วยกิตที่ planner รู้คือ "วิชาที่ผ่าน" ซึ่งไม่ตรงกับ
# "หน่วยกิตที่คิดใน GPAX" เมื่อมีวิชาติด F / เทียบโอน / ตัดสินผลเป็น S-U
CREDITS_COUNTED_PATTERN = re.compile(
    r"(?:เก็บ(?:ไป|มา)?(?:แล้ว)?|คิดเกรด(?:ไป|แล้ว)?|นับเกรด(?:ไป|แล้ว)?|ลงไป(?:แล้ว)?)"
    r"\s*(\d{1,3})\s*(?:นก\.?|หน่วยกิต)"
)

HONORS_CUE = re.compile(r"เกียรตินิยม|honors?")


@dataclass(frozen=True, slots=True)
class GradeQuestion:
    """ตัวเลขที่แกะได้จากข้อความหนึ่งข้อความ — ``None`` = ผู้ใช้ไม่ได้บอกมา"""

    gpax: float | None = None
    target: float | None = None
    credits_counted: int | None = None
    wants_honors: bool = False


def parse_question(text: str) -> GradeQuestion:
    """
    แกะ GPAX ปัจจุบัน / เป้าหมาย / หน่วยกิตที่คิดเกรดแล้ว ออกจากข้อความไทย

    >>> parse_question("เกรดตอนนี้ 2.75 อยากได้ 3.00")
    GradeQuestion(gpax=2.75, target=3.0, credits_counted=None, wants_honors=False)

    ลำดับกลับกันก็ต้องได้เหมือนกัน — คนพิมพ์ไม่ได้เรียงตามที่เราคิด

    >>> parse_question("อยากได้ 3 ตอนนี้ได้ 2.75")
    GradeQuestion(gpax=2.75, target=3.0, credits_counted=None, wants_honors=False)

    บอกมาตัวเดียว = ยังไม่มีเป้า (ชั้นคำตอบจะไล่กรณีให้ดูแทน)

    >>> parse_question("GPA 1.88 จบได้ไหม").gpax
    1.88

    รหัสวิชากับปีการศึกษาต้องไม่ถูกอ่านเป็นเกรด

    >>> parse_question("เกรดวิชา 1109902 เทอม 2568")
    GradeQuestion(gpax=None, target=None, credits_counted=None, wants_honors=False)

    แก้จำนวนหน่วยกิตที่คิดเกรดแล้วเองได้

    >>> parse_question("เกรด 2.5 เก็บไปแล้ว 72 หน่วยกิต").credits_counted
    72

    >>> parse_question("ยังลุ้นเกียรตินิยมได้ไหม เกรด 3.4").wants_honors
    True
    """
    found = [(m.start(), float(m.group(1))) for m in NUMBER_PATTERN.finditer(text)]
    cue = TARGET_CUE.search(text)
    gpax: float | None = None
    target: float | None = None

    if cue is None:
        values = [value for _, value in found]
    else:
        after = [value for pos, value in found if pos >= cue.end()]
        before = [value for pos, value in found if pos < cue.end()]
        if after:
            target = after[0]
            values = before + after[1:]
        else:
            values = before

    if target is None and len(values) > 1:
        # ไม่มีคำใบ้ว่าเลขไหนคือเป้า → ตีความว่า "ตอนนี้เท่านี้ อยากได้เท่านี้"
        gpax, target = values[0], values[1]
    elif values:
        gpax = values[0]

    credits = CREDITS_COUNTED_PATTERN.search(text)
    return GradeQuestion(
        gpax=gpax if gpax is not None and is_valid_gpax(gpax) else None,
        target=target if target is not None and is_valid_gpax(target) else None,
        credits_counted=int(credits.group(1)) if credits else None,
        wants_honors=bool(HONORS_CUE.search(text)),
    )
