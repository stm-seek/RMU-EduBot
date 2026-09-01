"""
Planner Engine — คำนวณความก้าวหน้าตามหลักสูตร (Requirement ข้อ 4.1 หมวด 3)

**ทุกอย่างในไฟล์นี้เป็นการคำนวณล้วน ไม่มี LLM ไม่มี I/O**

เหตุผลที่แยกออกมาแบบนี้ ไม่ใช่แค่เรื่องความสะอาด: ตัวเลขหน่วยกิตกับลำดับวิชา
เป็นข้อมูลที่ **ถ้าตอบผิดนักศึกษาเสียหายจริง** (ลงวิชาไม่ได้ จบช้าไปหนึ่งเทอม)
LLM จะเอาไปเรียบเรียงเป็นภาษาคนได้ แต่ห้ามเป็นคนคิดเลข — ดู ``app/ai_chat.py``

รับ input เป็นโครงสร้างข้อมูลเปล่า ๆ (list[dict] ที่มาจาก repository) ไม่รับ
connection เพื่อให้เทสยิงเคสตรง ๆ ได้โดยไม่ต้องมี Postgres

ข้อจำกัดที่ต้องรู้ก่อนอ่านผลลัพธ์:

* ``prerequisites`` ยังว่าง (0 แถว — ระบบทะเบียนไม่เผยแพร่ ต้องกรอกจาก มคอ.2)
  → :attr:`Progress.prereq_known` จะเป็น ``False`` และลำดับที่ได้คือ
  "เทอมที่แผนแนะนำ" เท่านั้น **ไม่ใช่** เงื่อนไขวิชาบังคับก่อนจริง
* วิชาที่นักศึกษาผ่านแล้วมาจากการติ๊กเองใน LIFF (``user_completed_courses``)
  ไม่ได้ดึงจากระบบทะเบียน → ถ้าติ๊กผิด ผลก็ผิดตามด้วย
* ไม่เก็บเกรด → คิด "ผ่าน/ไม่ผ่าน" ได้ แต่คิด GPA ไม่ได้ (นั่นคือข้อ 4.4)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

# เพดานหน่วยกิตต่อภาคเรียนปกติ — ค่า default ของ RMU ระดับปริญญาตรีภาคปกติ
#
# ยังไม่ยืนยันกับเล่มข้อบังคับ (ไม่มีในคลังเอกสารที่ scrape มา) จึงทำเป็น
# parameter ทุกที่ที่ใช้ ไม่ hardcode ลงตรรกะ — ดู settings.planner_max_credits
DEFAULT_MAX_CREDITS_PER_TERM = 22

# วิชาที่หน่วยกิตมากกว่าหรือเท่ากับค่านี้ = "วิชาบล็อก" ลงเดี่ยวทั้งเทอม
#
# ในหลักสูตรนี้คือ 7073401 ฝึกประสบการณ์ 12 นก. (0-0-640 ชั่วโมง) ซึ่งเอาไป
# รวมกับวิชาอื่นไม่ได้จริง — แต่ ``curriculum_rules.is_fixed_term`` เป็น FALSE
# ทุกแถวเพราะระบบทะเบียนไม่ได้บอก จึงอาศัย "หน่วยกิตเยอะผิดปกติ" เป็นสัญญาณ
# แทนการเดาเป็นรายวิชา (เกณฑ์ 9 = สามวิชาปกติ ไม่มีวิชาบรรยายไหนถึง)
BLOCK_COURSE_CREDITS = 9

HARD = "hard"
SOFT = "soft"
CONCURRENT = "concurrent"


@dataclass(frozen=True, slots=True)
class PlannedCourse:
    """หนึ่งแถวใน ``curriculum_rules`` + ชื่อ/หน่วยกิตจาก ``courses``"""

    course_code: str
    std_year: int
    std_semester: int
    name: str | None = None
    credits: int | None = None
    is_fixed_term: bool = False
    note: str | None = None
    # เปิดสอนเทอมไหนบ้าง (จาก offering_patterns) — ว่าง = ไม่รู้
    opens: frozenset[int] = frozenset()
    # หมวดในโครงสร้างหลักสูตร ('2.2' = วิชาเลือกเฉพาะด้าน) — None = ยังไม่กรอก
    group_code: str | None = None
    group_label: str | None = None

    @property
    def has_term(self) -> bool:
        """
        แผนกำหนดเทอมให้วิชานี้ไหม

        วิชาเลือกไม่มีเทอมกำหนด (``std_year``/``std_semester`` เป็น NULL ใน DB
        แล้วกลายเป็น 0 ตอนอ่านเข้ามา) เพราะนักศึกษาเลือกลงเทอมไหนก็ได้
        ต้องแยกให้ออกจาก "ปี 0" ที่ไม่มีอยู่จริงในหลักสูตร

        >>> PlannedCourse('7073312', 0, 0).has_term
        False
        """
        return self.std_year > 0

    @property
    def term_label(self) -> str:
        """
        >>> PlannedCourse('7071101', 2, 1).term_label
        'ปี 2 เทอม 1'
        >>> PlannedCourse('7073312', 0, 0, group_label='วิชาเลือกเฉพาะด้าน').term_label
        'วิชาเลือกเฉพาะด้าน'
        >>> PlannedCourse('7073312', 0, 0).term_label
        'ไม่กำหนดเทอม'
        """
        if not self.has_term:
            return self.group_label or "ไม่กำหนดเทอม"
        return f"ปี {self.std_year} เทอม {self.std_semester}"

    @property
    def term_order(self) -> tuple[int, int]:
        """
        คีย์เรียงตามเทอมในแผน — วิชาไม่มีเทอมไปท้ายสุด

        ถ้าคืน ``(0, 0)`` ตามค่าที่อ่านมาดิบ ๆ วิชาเลือกจะถูกเรียงมา**ก่อน**
        วิชาบังคับปี 1 ทั้งหมด แล้วตัวแนะนำเทอมหน้าจะเสนอวิชาเลือกก่อนวิชาที่
        แผนวางไว้ ซึ่งทำให้นักศึกษาเก็บวิชาบังคับไม่ทันและจบช้า

        >>> PlannedCourse('7073312', 0, 0).term_order
        (99, 99)
        """
        if not self.has_term:
            return (99, 99)
        return (self.std_year, self.std_semester)


@dataclass(frozen=True, slots=True)
class Requirement:
    """วิชาบังคับก่อนหนึ่งตัวที่ยังไม่ผ่าน"""

    requires_code: str
    kind: str = HARD
    name: str | None = None


@dataclass(frozen=True, slots=True)
class CourseStatus:
    """สถานะของวิชาหนึ่งตัวสำหรับนักศึกษาหนึ่งคน"""

    course: PlannedCourse
    passed: bool = False
    # hard prereq ที่ยังไม่ผ่าน — มีตัวใดตัวหนึ่ง = ลงเทอมนี้ไม่ได้
    blockers: tuple[Requirement, ...] = ()
    # concurrent = ลงพร้อมกันได้, soft = แนะนำให้ผ่านก่อนแต่ไม่บังคับ
    co_requisites: tuple[Requirement, ...] = ()
    advisories: tuple[Requirement, ...] = ()

    @property
    def eligible(self) -> bool:
        """ลงได้เลยไหม (ยังไม่ผ่าน + ไม่มี hard prereq ค้าง)"""
        return not self.passed and not self.blockers


@dataclass(frozen=True, slots=True)
class GroupProgress:
    """
    ความก้าวหน้าของหมวดหนึ่งใน ``curriculum_groups``

    หมวดวิชาเลือกมี "คลัง" ให้เลือกมากกว่าโควตาเสมอ (เช่นหมวด 2.2 มีให้เลือก
    20 กว่าวิชา แต่ต้องเก็บแค่ 18 นก.) จึงต้องแยก ``passed_credits`` ที่ผ่านจริง
    ออกจาก ``counted_credits`` ที่นับให้ตามหลักสูตร — ส่วนเกินไม่ทำให้จบเร็วขึ้น
    """

    group_code: str
    group_label: str
    required_credits: int
    passed_credits: int = 0
    is_choice: bool = False
    sort_order: int = 0

    @property
    def counted_credits(self) -> int:
        """
        นับได้ไม่เกินโควตา — เพดานนี้คือหัวใจของสูตรเปอร์เซ็นต์

        คนที่เก็บหมวด 2.2 ไป 21 นก. จากโควตา 18 ต้องนับให้ 18 ไม่ให้ส่วนเกิน
        ไปดันเปอร์เซ็นต์รวมทะลุ 100 (หรือกลบหมวดอื่นที่ยังขาด)

        >>> GroupProgress('2.2', 'เลือกเฉพาะด้าน', 18, 21).counted_credits
        18
        """
        return min(self.passed_credits, self.required_credits)

    @property
    def complete(self) -> bool:
        return self.counted_credits >= self.required_credits

    @property
    def percent(self) -> float:
        """
        โควตา 0 นก. = ไม่มีอะไรต้องเก็บ ถือว่าครบแล้ว (ไม่ใช่ 0%)

        >>> GroupProgress('9.9', 'หมวดว่าง', 0).percent
        100.0
        """
        if self.required_credits <= 0:
            return 100.0
        return round(100.0 * self.counted_credits / self.required_credits, 1)


@dataclass(frozen=True, slots=True)
class Progress:
    """ผลรวมความก้าวหน้า — ทุกตัวเลขในนี้คำนวณมาแล้ว ไม่ต้องคิดต่อ"""

    program_code: str
    statuses: tuple[CourseStatus, ...]
    total_credits_required: int | None = None
    # prerequisites มีข้อมูลไหม — ถ้า False ต้องบอกผู้ใช้ว่าลำดับเป็นแค่ "แผนแนะนำ"
    prereq_known: bool = False
    # วิชาที่ติ๊กว่าผ่านแล้วแต่ไม่อยู่ในแผน (เลือกเสรี / เทียบโอน)
    passed_outside_plan: tuple[str, ...] = ()
    # ความก้าวหน้ารายหมวด — ว่าง = หลักสูตรนี้ยังไม่ได้กรอก curriculum_groups
    groups: tuple[GroupProgress, ...] = ()
    # เลือกเสรีที่นักศึกษากรอกเอง (ไม่มีรายวิชาให้ติ๊ก จึงรับเป็นจำนวนหน่วยกิต)
    free_elective_credits: int = 0

    @property
    def complete_group_codes(self) -> frozenset[str]:
        """หมวดที่เก็บครบโควตาแล้ว — ไม่ต้องเสนอวิชาในหมวดนี้อีก"""
        return frozenset(g.group_code for g in self.groups if g.complete)

    @property
    def passed_statuses(self) -> tuple[CourseStatus, ...]:
        return tuple(s for s in self.statuses if s.passed)

    @property
    def remaining(self) -> tuple[CourseStatus, ...]:
        """ยังไม่ผ่าน — เรียงตามเทอมในแผน (ค้างนานสุดมาก่อน)"""
        return tuple(
            sorted(
                (s for s in self.statuses if not s.passed),
                key=lambda s: (s.course.term_order, s.course.course_code),
            )
        )

    @property
    def eligible_now(self) -> tuple[CourseStatus, ...]:
        return tuple(s for s in self.remaining if s.eligible)

    @property
    def blocked(self) -> tuple[CourseStatus, ...]:
        return tuple(s for s in self.remaining if s.blockers)

    @property
    def plan_courses(self) -> int:
        return len(self.statuses)

    @property
    def passed_credits(self) -> int:
        return sum(s.course.credits or 0 for s in self.passed_statuses)

    @property
    def remaining_plan_credits(self) -> int:
        return sum(s.course.credits or 0 for s in self.remaining)

    @property
    def counted_credits(self) -> int:
        """
        หน่วยกิตที่นับให้ตามหลักสูตร — ไม่ใช่หน่วยกิตที่ผ่านมาทั้งหมด

        ต่างจาก :attr:`passed_credits` เมื่อมีข้อมูลหมวด เพราะวิชาเลือกที่เก็บ
        เกินโควตาหมวดหนึ่งเอาไปนับให้หมวดอื่นไม่ได้ (ดู
        :attr:`GroupProgress.counted_credits`) ไม่มีข้อมูลหมวด = เท่ากับของดิบ
        """
        if not self.groups:
            return self.passed_credits
        return sum(g.counted_credits for g in self.groups)

    @property
    def percent_complete(self) -> float:
        """
        คิดจาก **หน่วยกิตที่นับให้ได้ / หน่วยกิตทั้งหลักสูตร** เมื่อมีข้อมูลหมวด

        เหตุที่ต้องคิดแบบโควตา: วิชาเลือกในคลังมีมากกว่าที่ต้องเรียน (68 แถวใน
        แผน แต่จบด้วย 120 นก.) ถ้านับ "จำนวนวิชาที่ผ่าน / จำนวนวิชาในแผน" คน
        ที่เก็บวิชาบังคับครบจะได้ตัวเลขต่ำลงทันทีที่มีวิชาเลือกเข้ามาในแผน และ
        การเก็บวิชาเลือกเกินโควตาก็จะดันตัวเลขเกิน 100 ทั้งสองทางผิดทั้งคู่

        ไม่มีข้อมูลหมวด (หรือไม่รู้หน่วยกิตรวมของหลักสูตร) ยังใช้สูตรเดิม =
        **สัดส่วนจำนวนวิชาในแผน** ซึ่งเป็นค่าประมาณเท่านั้น ไม่ใช่ความจริงตาม
        โครงสร้างหลักสูตร — หลักสูตรที่ยังไม่ได้กรอก ``curriculum_groups`` จึง
        ยังตอบได้ แต่ตัวเลขหยาบกว่า

        >>> Progress('x', ()).percent_complete
        0.0
        """
        total = self.total_credits_required
        if self.groups and total:
            return round(100.0 * min(self.counted_credits, total) / total, 1)
        if not self.statuses:
            return 0.0
        return round(100.0 * len(self.passed_statuses) / len(self.statuses), 1)

    @property
    def credits_left_to_graduate(self) -> int | None:
        """
        หน่วยกิตที่ยังต้องเก็บตามหลักสูตร

        ใช้ฐานเดียวกับ :attr:`percent_complete` (คือ :attr:`counted_credits`)
        ไม่ใช่หน่วยกิตที่ผ่านดิบ ๆ ไม่งั้นสองตัวเลขนี้จะขัดกันเอง — เคยเป็นบั๊ก
        จริงที่บอก "ครบ 100%" พร้อมกับ "เหลืออีก 15 นก."

        เมื่อยังไม่มีข้อมูลหมวด ค่านี้เป็น **ค่าประมาณสูงสุด**: เก็บแต่วิชาที่
        ติ๊ก จึงไม่รู้ว่าเลือกเสรีที่ลงไปแล้วครบหรือยัง ("ไม่เกินเท่านี้")
        """
        if self.total_credits_required is None:
            return None
        return max(0, self.total_credits_required - self.counted_credits)


# ── การคำนวณ ────────────────────────────────────────────────────────────────


def _as_course(
    row: Mapping, group_labels: Mapping[str, str] | None = None
) -> PlannedCourse:
    """
    แถวจาก repository → :class:`PlannedCourse` (ทนกับคอลัมน์ที่ไม่มี)

    ``group_labels`` (รหัสหมวด → ชื่อหมวด) มาจาก ``curriculum_groups`` เพราะ
    ``curriculum_rules`` เก็บแต่รหัสหมวด แต่ชื่อหมวดคือสิ่งที่ผู้ใช้ต้องเห็น
    แทนคำว่า "ปี 0 เทอม 0" ในวิชาเลือก
    """
    opens = {
        semester
        for semester, key in ((1, "opens_sem1"), (2, "opens_sem2"), (3, "opens_sem3"))
        if row.get(key)
    }
    group_code = row.get("group_code")
    group_code = str(group_code) if group_code else None
    group_label = row.get("group_label")
    if not group_label and group_code and group_labels:
        group_label = group_labels.get(group_code)
    return PlannedCourse(
        course_code=str(row["course_code"]),
        std_year=int(row["std_year"] or 0),
        std_semester=int(row["std_semester"] or 0),
        name=row.get("name_th") or row.get("name"),
        credits=row.get("credits"),
        is_fixed_term=bool(row.get("is_fixed_term")),
        note=row.get("note"),
        opens=frozenset(opens),
        group_code=group_code,
        group_label=str(group_label) if group_label else None,
    )


def index_prerequisites(rows: Iterable[Mapping]) -> dict[str, tuple[Requirement, ...]]:
    """
    ``prerequisites`` → dict: รหัสวิชา → เงื่อนไขทั้งหมดของวิชานั้น

    >>> idx = index_prerequisites([
    ...     {'course_code': '7071201', 'requires_code': '7071107', 'kind': 'hard'},
    ...     {'course_code': '7071201', 'requires_code': '7071101', 'kind': 'soft'},
    ... ])
    >>> [r.requires_code for r in idx['7071201']]
    ['7071107', '7071101']
    """
    index: dict[str, list[Requirement]] = {}
    for row in rows:
        index.setdefault(str(row["course_code"]), []).append(
            Requirement(
                requires_code=str(row["requires_code"]),
                kind=str(row.get("kind") or HARD),
                name=row.get("requires_name"),
            )
        )
    return {code: tuple(reqs) for code, reqs in index.items()}


def _group_progress(
    group_rows: Iterable[Mapping],
    statuses: Sequence[CourseStatus],
    free_elective_credits: int,
) -> tuple[GroupProgress, ...]:
    """
    ผลรวมรายหมวดจากวิชาที่ติ๊กแล้ว

    "เลือกเสรี" คือหมวดที่ ``is_choice`` แต่ไม่มีแถวใน ``curriculum_rules`` ชี้มา
    เลย — นักศึกษาลงวิชาจากคณะไหนก็ได้ ระบบจึงไม่มีรายวิชาให้ติ๊ก ต้องรับเป็น
    จำนวนหน่วยกิตที่ผู้ใช้กรอกเองแทน (ถ้าไปนับจากวิชาที่ติ๊ก หมวดนี้จะค้าง 0
    ตลอดชีวิตและเปอร์เซ็นต์รวมจะไม่มีวันถึง 100)
    """
    passed_by_group: dict[str, int] = {}
    courses_by_group: set[str] = set()
    for status in statuses:
        code = status.course.group_code
        if not code:
            continue
        courses_by_group.add(code)
        if status.passed:
            passed_by_group[code] = passed_by_group.get(code, 0) + (
                status.course.credits or 0
            )

    groups: list[GroupProgress] = []
    for row in group_rows:
        code = str(row["group_code"])
        is_choice = bool(row.get("is_choice"))
        if is_choice and code not in courses_by_group:
            passed_credits = max(0, int(free_elective_credits or 0))
        else:
            passed_credits = passed_by_group.get(code, 0)
        groups.append(
            GroupProgress(
                group_code=code,
                group_label=str(row.get("group_label") or code),
                required_credits=int(row.get("required_credits") or 0),
                passed_credits=passed_credits,
                is_choice=is_choice,
                sort_order=int(row.get("sort_order") or 0),
            )
        )
    return tuple(groups)


def evaluate(
    program_code: str,
    plan_rows: Sequence[Mapping],
    passed_codes: Iterable[str],
    *,
    prereq_rows: Sequence[Mapping] = (),
    total_credits_required: int | None = None,
    group_rows: Iterable[Mapping] = (),
    free_elective_credits: int = 0,
) -> Progress:
    """
    รวมทุกอย่างเป็นสถานะเดียว — จุดเข้าหลักของ planner

    ``passed_codes`` คือรหัส 7 หลักที่นักศึกษาติ๊กว่าผ่านแล้ว
    ``group_rows`` คือ ``curriculum_groups`` ของหลักสูตรนั้น — ไม่ส่งมาก็ยังได้
    คำตอบ แต่เปอร์เซ็นต์จะเป็นสูตรนับวิชาแบบหยาบ (ดู
    :attr:`Progress.percent_complete`)

    >>> plan = [
    ...     {'course_code': '7071107', 'std_year': 1, 'std_semester': 2, 'credits': 3},
    ...     {'course_code': '7071201', 'std_year': 2, 'std_semester': 1, 'credits': 3},
    ... ]
    >>> prereq = [{'course_code': '7071201', 'requires_code': '7071107', 'kind': 'hard'}]
    >>> p = evaluate('x', plan, [], prereq_rows=prereq)
    >>> [s.course.course_code for s in p.eligible_now]
    ['7071107']
    >>> [s.course.course_code for s in p.blocked]
    ['7071201']
    >>> evaluate('x', plan, ['7071107'], prereq_rows=prereq).percent_complete
    50.0
    """
    passed = {str(code) for code in passed_codes}
    prereq_index = index_prerequisites(prereq_rows)
    group_rows = tuple(group_rows)
    group_labels = {
        str(row["group_code"]): str(row.get("group_label") or row["group_code"])
        for row in group_rows
    }

    statuses: list[CourseStatus] = []
    for row in plan_rows:
        course = _as_course(row, group_labels)
        requirements = prereq_index.get(course.course_code, ())
        unmet = [req for req in requirements if req.requires_code not in passed]
        statuses.append(
            CourseStatus(
                course=course,
                passed=course.course_code in passed,
                blockers=tuple(req for req in unmet if req.kind == HARD),
                co_requisites=tuple(req for req in unmet if req.kind == CONCURRENT),
                advisories=tuple(req for req in unmet if req.kind == SOFT),
            )
        )

    in_plan = {status.course.course_code for status in statuses}
    return Progress(
        program_code=program_code,
        statuses=tuple(statuses),
        total_credits_required=total_credits_required,
        prereq_known=bool(prereq_index),
        passed_outside_plan=tuple(sorted(passed - in_plan)),
        groups=_group_progress(group_rows, statuses, free_elective_credits),
        free_elective_credits=max(0, int(free_elective_credits or 0)),
    )


# ── เสนอวิชาสำหรับเทอมถัดไป ─────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TermSuggestion:
    """ตะกร้าวิชาที่เสนอให้ลงหนึ่งเทอม"""

    semester: int
    picks: tuple[CourseStatus, ...] = ()
    # ค้างจากเทอมก่อน ๆ ตามแผน (ควรเก็บให้ทันก่อนไปตัวใหม่)
    overdue: tuple[CourseStatus, ...] = ()
    # ไม่ได้เลือกเพราะเต็มเพดานหน่วยกิตแล้ว
    deferred: tuple[CourseStatus, ...] = ()
    # ยังลงไม่ได้เพราะติด hard prereq
    blocked: tuple[CourseStatus, ...] = ()
    # ลงได้แต่ offering_patterns บอกว่า **เทอมนี้ไม่เปิด** → ต้องรออีกเทอม
    not_offered: tuple[CourseStatus, ...] = ()
    max_credits: int = DEFAULT_MAX_CREDITS_PER_TERM
    # วิชาที่ไม่รู้ว่าเปิดเทอมนี้ไหม (offering_patterns ไม่มีข้อมูล)
    unknown_offering: tuple[str, ...] = ()
    # เสนอวิชาบล็อก (ฝึกประสบการณ์) เดี่ยว ๆ ทั้งเทอม
    block_only: bool = False

    @property
    def credits(self) -> int:
        return sum(s.course.credits or 0 for s in self.picks)


def suggest_term(
    progress: Progress,
    semester: int,
    *,
    max_credits: int = DEFAULT_MAX_CREDITS_PER_TERM,
    block_credits: int = BLOCK_COURSE_CREDITS,
    up_to_term: tuple[int, int] | None = None,
) -> TermSuggestion:
    """
    เลือกวิชาสำหรับภาคเรียน ``semester`` (1 / 2 / 3) จากวิชาที่ลงได้

    กติกาการเรียง — ทั้งหมดเป็นกฎที่อธิบายได้ ไม่มีการสุ่มและไม่มี LLM:

    1. วิชาที่ ``offering_patterns`` บอกชัดว่า **เทอมนี้ไม่เปิด** ถูกคัดออกก่อน
       (ไป ``not_offered``) — เสนอวิชาที่ลงไม่ได้จริงคือการให้ข้อมูลผิด
       วิชาที่ไม่มีข้อมูลการเปิดเลยยังเสนอได้ แต่ต่อท้ายและติดธงไว้
    2. วิชาที่ **ค้าง** (แผนวางไว้ก่อนเทอมปัจจุบัน) มาก่อน — จบช้าเพราะวิชาค้าง
       เจ็บกว่าเรียนวิชาของเทอมนี้ช้าไปหนึ่งเทอม
    3. วิชาที่รู้ว่าเปิดเทอมนี้ มาก่อนวิชาที่ไม่รู้
    4. ที่เหลือเรียงตามเทอมในแผน แล้วตามรหัสวิชา (ผลลัพธ์คงที่ ทดสอบได้)
    5. **วิชาบล็อก** (>= ``BLOCK_COURSE_CREDITS`` นก. เช่นฝึกประสบการณ์) ไปท้ายสุด
       และลงเดี่ยวเสมอ — ถ้ายังมีวิชาอื่นให้เก็บ ให้เก็บวิชาอื่นก่อน
    6. หยุดเมื่อหน่วยกิตจะเกิน ``max_credits`` — ตัวที่ไม่ได้ไปอยู่ ``deferred``
    7. วิชาในหมวดที่เก็บครบโควตาแล้ว (``curriculum_groups``) ถูกคัดออกทั้งหมด
       — ไม่ใช่เลื่อน เพราะไม่ต้องเรียนอีกแล้ว

    ``up_to_term`` = (ปี, เทอม) ที่นักศึกษาอยู่ตอนนี้ ใช้ตัดสินว่าอะไร "ค้าง"
    ถ้าไม่ส่งมา ถือว่าไม่มีวิชาค้าง (ไม่รู้ก็ไม่เดา)

    >>> plan = [
    ...     {'course_code': 'A', 'std_year': 1, 'std_semester': 1, 'credits': 3, 'opens_sem1': True},
    ...     {'course_code': 'B', 'std_year': 2, 'std_semester': 1, 'credits': 3, 'opens_sem1': True},
    ...     {'course_code': 'C', 'std_year': 2, 'std_semester': 2, 'credits': 3, 'opens_sem2': True},
    ... ]
    >>> s = suggest_term(evaluate('x', plan, []), 1, max_credits=3, up_to_term=(2, 1))
    >>> [x.course.course_code for x in s.picks], [x.course.course_code for x in s.overdue]
    (['A'], ['A'])
    >>> [x.course.course_code for x in s.deferred]
    ['B']
    >>> [x.course.course_code for x in s.not_offered]
    ['C']
    """
    remaining = progress.remaining
    overdue = (
        tuple(s for s in remaining if s.course.term_order < up_to_term)
        if up_to_term
        else ()
    )
    overdue_codes = {s.course.course_code for s in overdue}

    def offered(status: CourseStatus) -> bool:
        """ไม่มีข้อมูลการเปิด = ไม่ตัดออก (ไม่รู้ ไม่ใช่ไม่เปิด)"""
        opens = status.course.opens
        return not opens or semester in opens

    done_groups = progress.complete_group_codes

    def quota_done(status: CourseStatus) -> bool:
        """
        วิชาในหมวดที่เก็บครบโควตาแล้ว ไม่ต้องเสนอ

        หมวดวิชาเลือกมีวิชาในคลังมากกว่าโควตา คนที่เก็บครบ 18 นก. แล้วยังมีวิชา
        ที่ "ยังไม่ผ่าน" เหลืออีกสิบกว่าตัวตลอด ถ้าเสนอต่อจะกินเพดานหน่วยกิตของ
        เทอมไปจากวิชาบังคับที่ยังขาด — และตัดออกเลยไม่ใช่ ``deferred`` เพราะมัน
        ไม่ใช่ "เลื่อนไปเทอมหน้า" แต่ไม่ต้องเรียนอีกแล้ว
        """
        code = status.course.group_code
        return bool(code) and code in done_groups

    eligible = tuple(s for s in remaining if s.eligible and not quota_done(s))
    not_offered = tuple(s for s in eligible if not offered(s))

    def is_block(status: CourseStatus) -> bool:
        return (status.course.credits or 0) >= block_credits

    def sort_key(status: CourseStatus) -> tuple:
        return (
            1 if is_block(status) else 0,
            0 if status.course.course_code in overdue_codes else 1,
            0 if semester in status.course.opens else 1,
            status.course.term_order,
            status.course.course_code,
        )

    candidates = sorted((s for s in eligible if offered(s)), key=sort_key)

    picks: list[CourseStatus] = []
    deferred: list[CourseStatus] = []
    used = 0
    for status in candidates:
        credits = status.course.credits or 0
        # วิชาบล็อกลงร่วมกับอะไรไม่ได้ — ทั้งตัวมันไม่แทรกเข้ากลุ่มที่มีคนอยู่แล้ว
        # และเมื่อมันถูกเลือกเดี่ยว ตัวอื่นก็เข้าไม่ได้อีก
        if is_block(status) and picks:
            deferred.append(status)
            continue
        if picks and any(is_block(p) for p in picks):
            deferred.append(status)
            continue
        if used + credits > max_credits and picks:
            deferred.append(status)
            continue
        picks.append(status)
        used += credits

    return TermSuggestion(
        semester=semester,
        picks=tuple(picks),
        overdue=overdue,
        deferred=tuple(deferred),
        blocked=progress.blocked,
        not_offered=not_offered,
        max_credits=max_credits,
        unknown_offering=tuple(
            s.course.course_code for s in picks if not s.course.opens
        ),
        block_only=any(is_block(s) for s in picks),
    )


def find_status(progress: Progress, course_code: str) -> CourseStatus | None:
    """
    หาสถานะของวิชาเดียว — ใช้ตอบ "ลงวิชา 7071201 ได้เลยไหม"

    >>> p = evaluate('x', [{'course_code': 'A', 'std_year': 1, 'std_semester': 1}], [])
    >>> find_status(p, 'A').course.course_code
    'A'
    >>> find_status(p, 'ZZ') is None
    True
    """
    for status in progress.statuses:
        if status.course.course_code == course_code:
            return status
    return None
