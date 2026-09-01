"""
เทส Planner Engine — ตรรกะการคำนวณล้วน ไม่ต้องมี DB ไม่ต้องมีเน็ต

โฟกัสของไฟล์นี้คือ **เคสที่ตอบผิดแล้วนักศึกษาเสียหายจริง**:

* นับหน่วยกิต/เปอร์เซ็นต์ผิด → เข้าใจผิดว่าใกล้จบ
* เสนอวิชาที่ยังลงไม่ได้ (ติดวิชาบังคับก่อน) → ไปลงแล้วถูกตัดออก
* เสนอวิชาที่เทอมนั้นไม่เปิด → เสียเวลาไปหนึ่งเทอม
* เสนอเกินเพดานหน่วยกิต → ลงทะเบียนไม่ผ่านทั้งใบ
"""

from __future__ import annotations

from app import planner


def plan_row(code: str, year: int, semester: int, credits: int = 3, **extra) -> dict:
    row = {
        "course_code": code,
        "std_year": year,
        "std_semester": semester,
        "credits": credits,
        "name_th": f"วิชา {code}",
    }
    row.update(extra)
    return row


# แผนย่อ 8 วิชา 2 ปี — พอครอบทุกกฎโดยยังอ่านออกด้วยตาเปล่า
SMALL_PLAN = [
    plan_row("1000001", 1, 1, opens_sem1=True),
    plan_row("1000002", 1, 1, opens_sem1=True),
    plan_row("1000003", 1, 2, opens_sem2=True),
    plan_row("1000004", 1, 2, opens_sem1=True, opens_sem2=True),
    plan_row("2000001", 2, 1, opens_sem1=True),
    plan_row("2000002", 2, 1, opens_sem1=True),
    plan_row("2000003", 2, 2, opens_sem2=True),
    plan_row("2000004", 2, 2, credits=12, opens_sem1=True, opens_sem2=True),
]


# ── นับความก้าวหน้า ─────────────────────────────────────────────────────────


def test_counts_nothing_passed() -> None:
    progress = planner.evaluate("p", SMALL_PLAN, [])

    assert progress.plan_courses == 8
    assert progress.passed_credits == 0
    assert progress.percent_complete == 0.0
    assert len(progress.remaining) == 8


def test_counts_passed_courses_and_credits() -> None:
    progress = planner.evaluate("p", SMALL_PLAN, ["1000001", "2000004"])

    assert len(progress.passed_statuses) == 2
    # 3 + 12 — ต้องอ่านหน่วยกิตจริงของแต่ละวิชา ไม่ใช่คูณ 3 เอา
    assert progress.passed_credits == 15
    assert progress.remaining_plan_credits == 6 * 3
    assert progress.percent_complete == 25.0


def test_remaining_is_sorted_by_plan_term() -> None:
    """เรียงตามเทอมในแผน — วิชาที่ค้างนานสุดต้องมาก่อน"""
    progress = planner.evaluate("p", list(reversed(SMALL_PLAN)), [])
    order = [status.course.course_code for status in progress.remaining]

    assert order == sorted(order)


def test_credits_left_uses_program_total_not_plan_total() -> None:
    """
    หน่วยกิตที่เหลือคิดจากที่หลักสูตรกำหนด ไม่ใช่ผลรวมของแผน

    แผนในระบบทะเบียนรวมได้ไม่ถึงหลักสูตร (ขาดช่องเลือกเสรี) — ถ้าคิดจากแผน
    จะบอกนักศึกษาว่าเหลือน้อยกว่าจริง ซึ่งเป็นความผิดพลาดที่เจ็บที่สุด
    """
    progress = planner.evaluate(
        "p", SMALL_PLAN, ["1000001", "1000002"], total_credits_required=120
    )

    assert progress.passed_credits == 6
    assert progress.credits_left_to_graduate == 114


def test_credits_left_is_none_without_program_total() -> None:
    assert planner.evaluate("p", SMALL_PLAN, []).credits_left_to_graduate is None


def test_passed_course_outside_plan_is_reported_not_dropped() -> None:
    """วิชาเลือกเสรี/เทียบโอนไม่อยู่ในแผน — ต้องไม่หายเงียบ"""
    progress = planner.evaluate("p", SMALL_PLAN, ["1000001", "9999999"])

    assert progress.passed_outside_plan == ("9999999",)
    assert len(progress.passed_statuses) == 1


# ── วิชาบังคับก่อน ───────────────────────────────────────────────────────────


def prereq(course: str, requires: str, kind: str = "hard") -> dict:
    return {"course_code": course, "requires_code": requires, "kind": kind}


def test_hard_prerequisite_blocks_course() -> None:
    progress = planner.evaluate(
        "p", SMALL_PLAN, [], prereq_rows=[prereq("2000001", "1000001")]
    )
    blocked = {status.course.course_code for status in progress.blocked}

    assert blocked == {"2000001"}
    assert "2000001" not in {s.course.course_code for s in progress.eligible_now}


def test_hard_prerequisite_clears_once_passed() -> None:
    progress = planner.evaluate(
        "p", SMALL_PLAN, ["1000001"], prereq_rows=[prereq("2000001", "1000001")]
    )

    assert progress.blocked == ()
    assert planner.find_status(progress, "2000001").eligible


def test_soft_and_concurrent_prerequisites_do_not_block() -> None:
    """
    soft = แนะนำ, concurrent = ลงพร้อมกันได้ — ทั้งสองห้ามกันไม่ให้ลง

    ถ้าเอาสองแบบนี้ไปกันด้วย ระบบจะบอกว่า "ลงไม่ได้" ทั้งที่ลงได้
    ซึ่งทำให้นักศึกษาเรียนช้ากว่าที่ควรโดยไม่มีเหตุผล
    """
    progress = planner.evaluate(
        "p",
        SMALL_PLAN,
        [],
        prereq_rows=[
            prereq("2000001", "1000001", "soft"),
            prereq("2000001", "1000002", "concurrent"),
        ],
    )
    status = planner.find_status(progress, "2000001")

    assert status.eligible
    assert [r.requires_code for r in status.advisories] == ["1000001"]
    assert [r.requires_code for r in status.co_requisites] == ["1000002"]


def test_prereq_known_flag_tells_the_truth() -> None:
    """
    ตาราง prerequisites ยังว่างจริงในระบบ — คำตอบต้องบอกผู้ใช้ได้ว่า
    ลำดับที่เห็นเป็นเพียงแผนแนะนำ ไม่ใช่เงื่อนไขบังคับ
    """
    assert planner.evaluate("p", SMALL_PLAN, []).prereq_known is False
    assert (
        planner.evaluate(
            "p", SMALL_PLAN, [], prereq_rows=[prereq("2000001", "1000001")]
        ).prereq_known
        is True
    )


# ── เสนอวิชาเทอมถัดไป ───────────────────────────────────────────────────────


def codes(statuses) -> list[str]:
    return [status.course.course_code for status in statuses]


def test_suggestion_skips_courses_not_open_this_semester() -> None:
    """เสนอวิชาที่เทอมนั้นไม่เปิด = ให้ข้อมูลผิด ต้องแยกไปบอกว่ารอเทอมหน้า"""
    suggestion = planner.suggest_term(planner.evaluate("p", SMALL_PLAN, []), 1)

    assert "1000003" not in codes(suggestion.picks)
    assert "1000003" in codes(suggestion.not_offered)
    assert "2000003" in codes(suggestion.not_offered)


def test_suggestion_keeps_courses_with_unknown_offering_but_flags_them() -> None:
    """ไม่มีข้อมูลว่าเปิดเทอมไหน ≠ ไม่เปิด — เสนอได้ แต่ต้องติดธงให้ผู้ใช้เช็ค"""
    plan = [plan_row("3000001", 1, 1)]  # ไม่มี opens_sem* เลย
    suggestion = planner.suggest_term(planner.evaluate("p", plan, []), 1)

    assert codes(suggestion.picks) == ["3000001"]
    assert suggestion.unknown_offering == ("3000001",)


def test_suggestion_never_exceeds_credit_cap() -> None:
    suggestion = planner.suggest_term(
        planner.evaluate("p", SMALL_PLAN, []), 1, max_credits=9
    )

    assert suggestion.credits <= 9
    assert suggestion.deferred, "วิชาที่เกินเพดานต้องถูกเลื่อน ไม่ใช่หายไป"


def test_suggestion_puts_overdue_courses_first() -> None:
    """ค้างจากปีก่อนต้องมาก่อนวิชาของเทอมนี้ — จบช้าเพราะวิชาค้างเจ็บกว่า"""
    progress = planner.evaluate("p", SMALL_PLAN, ["1000002"])
    suggestion = planner.suggest_term(
        progress, 1, max_credits=6, up_to_term=(2, 1)
    )

    # ค้าง = ทุกวิชาที่แผนวางไว้ก่อน (ปี 2 เทอม 1) และยังไม่ผ่าน
    assert codes(suggestion.overdue) == ["1000001", "1000003", "1000004"]
    # 1000003 เปิดแค่เทอม 2 → ค้างจริงแต่ลงเทอมนี้ไม่ได้ ต้องไม่ถูกเสนอ
    assert codes(suggestion.picks) == ["1000001", "1000004"]


def test_suggestion_excludes_blocked_courses() -> None:
    progress = planner.evaluate(
        "p", SMALL_PLAN, [], prereq_rows=[prereq("1000001", "9999999")]
    )
    suggestion = planner.suggest_term(progress, 1)

    assert "1000001" not in codes(suggestion.picks)
    assert "1000001" in codes(suggestion.blocked)


def test_block_course_is_suggested_alone() -> None:
    """
    ฝึกประสบการณ์ 12 นก. (0-0-640 ชม.) ลงร่วมกับวิชาอื่นไม่ได้จริง

    ``is_fixed_term`` เป็น FALSE ทุกแถวเพราะระบบทะเบียนไม่ได้บอก จึงใช้
    หน่วยกิตที่มากผิดปกติเป็นสัญญาณแทนการเดาเป็นรายวิชา
    """
    only_block = [plan_row("2000004", 2, 2, credits=12, opens_sem1=True)]
    suggestion = planner.suggest_term(planner.evaluate("p", only_block, []), 1)

    assert codes(suggestion.picks) == ["2000004"]
    assert suggestion.block_only is True


def test_block_course_waits_until_other_courses_are_done() -> None:
    progress = planner.evaluate("p", SMALL_PLAN, [])
    suggestion = planner.suggest_term(progress, 1, max_credits=22)

    assert "2000004" not in codes(suggestion.picks)
    assert "2000004" in codes(suggestion.deferred)
    assert suggestion.block_only is False


def test_suggestion_is_empty_when_everything_passed() -> None:
    progress = planner.evaluate("p", SMALL_PLAN, [row["course_code"] for row in SMALL_PLAN])
    suggestion = planner.suggest_term(progress, 1)

    assert suggestion.picks == ()
    assert progress.remaining == ()
    assert progress.percent_complete == 100.0

# ── วิชาเลือก: หมวด โควตา และการเรียงลำดับ ───────────────────────────────────
#
# วิชาเลือกใน curriculum_rules มี std_year/std_semester เป็น NULL เพราะลงเทอม
# ไหนก็ได้ ส่วนโควตา "ต้องเก็บให้ครบกี่หน่วยกิต" อยู่ใน curriculum_groups
# เคสในหมวดนี้คือเคสที่ตอบผิดแล้วนักศึกษาเข้าใจว่าใกล้จบทั้งที่ยังขาด


def elective_row(code: str, credits: int = 3, group: str = "2.2", **extra) -> dict:
    """แถววิชาเลือก — NULL ทั้งปีและเทอม เหมือนที่ออกมาจาก DB จริง"""
    row = {
        "course_code": code,
        "std_year": None,
        "std_semester": None,
        "credits": credits,
        "name_th": f"วิชาเลือก {code}",
        "group_code": group,
    }
    row.update(extra)
    return row


# 12 (บังคับ) + 18 (เลือกเฉพาะด้าน) + 6 (เลือกเสรี) = 36 นก. พอดี
GROUP_ROWS = [
    {
        "group_code": "1.1",
        "group_label": "วิชาบังคับ",
        "required_credits": 12,
        "is_choice": False,
        "sort_order": 10,
    },
    {
        "group_code": "2.2",
        "group_label": "วิชาเลือกเฉพาะด้าน",
        "required_credits": 18,
        "is_choice": True,
        "sort_order": 20,
    },
    {
        "group_code": "3.1",
        "group_label": "เลือกเสรี",
        "required_credits": 6,
        "is_choice": True,
        "sort_order": 30,
    },
]

CORE_CODES = ["1000001", "1000002", "1000003", "1000004"]
ELECTIVE_CODES = [f"70733{n:02d}" for n in range(1, 9)]  # คลัง 8 วิชา 24 นก.

# แผนเต็ม: บังคับ 4 วิชา (มีเทอม) + คลังวิชาเลือก 8 วิชา (ไม่มีเทอม)
GROUPED_PLAN = [
    plan_row("1000001", 1, 1, group_code="1.1", opens_sem1=True),
    plan_row("1000002", 1, 1, group_code="1.1", opens_sem1=True),
    plan_row("1000003", 1, 2, group_code="1.1", opens_sem1=True),
    plan_row("1000004", 2, 1, group_code="1.1", opens_sem1=True),
] + [elective_row(code, opens_sem1=True) for code in ELECTIVE_CODES]


def grouped(passed: list[str], *, free: int = 0) -> planner.Progress:
    return planner.evaluate(
        "p",
        GROUPED_PLAN,
        passed,
        total_credits_required=36,
        group_rows=GROUP_ROWS,
        free_elective_credits=free,
    )


def test_course_without_term_sorts_last_not_first() -> None:
    """
    วิชาไม่มีเทอมต้องไปท้ายสุด

    ก่อนแก้ ``term_order`` คืน ``(0, 0)`` ให้วิชาเลือก จึงเรียงมาก่อนวิชาบังคับ
    ปี 1 ทั้งหมด แล้วตัวแนะนำเทอมหน้าจะเสนอวิชาเลือกก่อนวิชาที่แผนวางไว้
    """
    progress = grouped([])
    order = [status.course.course_code for status in progress.remaining]

    assert order[:4] == CORE_CODES
    assert order[4:] == ELECTIVE_CODES

    picks = codes(planner.suggest_term(progress, 1, max_credits=99).picks)
    assert picks[:4] == CORE_CODES, "วิชาบังคับต้องมาก่อนวิชาเลือกในคำแนะนำ"


def test_course_without_term_never_shows_year_zero() -> None:
    """ผู้ใช้ต้องไม่เห็น "ปี 0 เทอม 0" ซึ่งไม่มีอยู่ในหลักสูตร"""
    course = planner.find_status(grouped([]), ELECTIVE_CODES[0]).course

    assert course.has_term is False
    assert "ปี 0" not in course.term_label
    # มีชื่อหมวดก็ใช้ชื่อหมวด (ชื่อมาจาก curriculum_groups ผ่าน group_code)
    assert course.term_label == "วิชาเลือกเฉพาะด้าน"
    assert course.group_code == "2.2"
    assert course.group_label == "วิชาเลือกเฉพาะด้าน"


def test_course_without_term_and_without_group_says_so() -> None:
    """ไม่รู้หมวด ก็บอกว่าไม่กำหนดเทอม ไม่เดาเป็นปี 0"""
    progress = planner.evaluate("p", [elective_row("7073399", group=None)], [])

    assert planner.find_status(progress, "7073399").course.term_label == "ไม่กำหนดเทอม"


def test_courses_with_term_keep_their_label() -> None:
    """วิชาบังคับต้องไม่กระทบจากการแก้เรื่องเทอมว่าง"""
    course = planner.PlannedCourse("1000001", 2, 1)

    assert course.has_term is True
    assert course.term_label == "ปี 2 เทอม 1"
    assert course.term_order == (2, 1)


def test_extra_credits_in_a_group_are_capped_at_the_quota() -> None:
    """
    เก็บเกินโควตาไม่ทำให้จบเร็วขึ้น — ต้องนับแค่เพดานของหมวด

    เก็บเลือกเฉพาะด้าน 21 นก. จากโควตา 18 → นับให้ 18 ส่วนเกิน 3 นก. เอาไป
    กลบหมวดอื่นที่ยังขาดไม่ได้ ไม่งั้นเปอร์เซ็นต์รวมจะทะลุ 100
    """
    progress = grouped(CORE_CODES + ELECTIVE_CODES[:7])  # 12 + 21 นก.
    by_code = {g.group_code: g for g in progress.groups}

    assert by_code["2.2"].passed_credits == 21
    assert by_code["2.2"].counted_credits == 18
    assert by_code["2.2"].complete is True
    assert by_code["2.2"].percent == 100.0
    # 12 + 18 + 0 (เลือกเสรียังไม่กรอก) = 30 จาก 36
    assert progress.passed_credits == 33
    assert progress.counted_credits == 30
    assert progress.percent_complete == 83.3


def test_percent_and_credits_left_agree_when_every_quota_is_met() -> None:
    """
    100% ต้องมาพร้อม "เหลือ 0 นก." เสมอ

    บั๊กเดิม: ติ๊กครบทุกวิชาในแผน 32 ตัวได้ 100% ทั้งที่ยังขาด 15 นก. เพราะ
    เปอร์เซ็นต์คิดจากจำนวนวิชา แต่หน่วยกิตที่เหลือคิดจากหน่วยกิตหลักสูตร
    """
    progress = grouped(CORE_CODES + ELECTIVE_CODES[:6], free=6)  # 12 + 18 + 6

    assert progress.counted_credits == 36
    assert progress.percent_complete == 100.0
    assert progress.credits_left_to_graduate == 0
    assert all(g.complete for g in progress.groups)


def test_percent_never_exceeds_one_hundred_with_overshoot_everywhere() -> None:
    """เก็บเกินทุกหมวด (24 จาก 18, เสรี 10 จาก 6) ก็ยังต้องเป็น 100 ไม่ใช่ 120"""
    progress = grouped(CORE_CODES + ELECTIVE_CODES, free=10)

    assert progress.percent_complete == 100.0
    assert progress.credits_left_to_graduate == 0


def test_free_elective_group_takes_the_number_the_student_typed() -> None:
    """
    เลือกเสรีไม่มีรายวิชาให้ติ๊ก (ลงคณะไหนก็ได้) จึงรับเป็นจำนวนหน่วยกิต

    ถ้าไปนับจากวิชาที่ติ๊ก หมวดนี้จะค้าง 0 ตลอดและเปอร์เซ็นต์รวมไม่มีวันถึง 100
    """
    free_group = {g.group_code: g for g in grouped([], free=3).groups}["3.1"]

    assert free_group.is_choice is True
    assert free_group.passed_credits == 3
    assert free_group.counted_credits == 3
    assert free_group.percent == 50.0
    assert grouped([], free=3).free_elective_credits == 3
    # ไม่กรอก = 0 ไม่ใช่เดาว่าครบ
    assert {g.group_code: g for g in grouped([]).groups}["3.1"].passed_credits == 0


def test_group_with_courses_ignores_the_free_elective_number() -> None:
    """หมวดที่มีวิชาในคลังต้องนับจากวิชาที่ติ๊กเท่านั้น แม้จะเป็นหมวดให้เลือก"""
    by_code = {g.group_code: g for g in grouped(ELECTIVE_CODES[:2], free=50).groups}

    assert by_code["2.2"].passed_credits == 6


def test_courses_in_a_completed_group_are_not_suggested() -> None:
    """เก็บครบโควตาแล้ว วิชาที่เหลือในคลังต้องไม่มาแย่งเพดานหน่วยกิตของเทอม"""
    progress = grouped(ELECTIVE_CODES[:6])  # เลือกเฉพาะด้านครบ 18 นก.
    suggestion = planner.suggest_term(progress, 1, max_credits=99)
    suggested = set(
        codes(suggestion.picks)
        + codes(suggestion.deferred)
        + codes(suggestion.not_offered)
    )

    assert suggested.isdisjoint(ELECTIVE_CODES[6:])
    assert set(CORE_CODES) <= suggested, "วิชาบังคับที่ยังขาดต้องยังถูกเสนอ"


def test_incomplete_group_still_gets_suggested() -> None:
    progress = grouped(ELECTIVE_CODES[:2])  # 6 จาก 18 นก. ยังไม่ครบ
    suggestion = planner.suggest_term(progress, 1, max_credits=99)

    assert set(ELECTIVE_CODES[2:]) <= set(codes(suggestion.picks))


# ── กันการถดถอย: ไม่มีข้อมูลหมวด ต้องได้ผลเหมือนก่อนแก้ ─────────────────────


def test_without_group_rows_everything_matches_the_old_formula() -> None:
    """
    หลักสูตรที่ยังไม่ได้กรอก curriculum_groups (มีอยู่จริงหลายใบ) ต้องไม่พัง

    เมื่อไม่มีข้อมูลหมวด สูตรเปอร์เซ็นต์ยังเป็น "จำนวนวิชาที่ผ่าน/วิชาในแผน"
    และหน่วยกิตที่เหลือยังคิดจากหน่วยกิตที่ผ่านดิบ ๆ ทุกตัวเลขต้องเท่าเดิม
    """
    progress = planner.evaluate(
        "p", SMALL_PLAN, ["1000001", "1000002"], total_credits_required=120
    )

    assert progress.groups == ()
    assert progress.free_elective_credits == 0
    assert progress.counted_credits == progress.passed_credits == 6
    assert progress.percent_complete == 25.0
    assert progress.credits_left_to_graduate == 114


def test_group_rows_without_program_total_falls_back_to_course_count() -> None:
    """ไม่รู้หน่วยกิตรวมของหลักสูตร = หารด้วยอะไรไม่ได้ ต้องถอยไปสูตรเดิม"""
    progress = planner.evaluate("p", GROUPED_PLAN, CORE_CODES, group_rows=GROUP_ROWS)

    assert progress.groups, "ยังต้องคืนข้อมูลรายหมวดให้หน้าเว็บแสดง"
    assert progress.percent_complete == round(100.0 * 4 / 12, 1)
    assert progress.credits_left_to_graduate is None


def test_empty_curriculum_does_not_crash_with_groups() -> None:
    """หลักสูตรที่ยังไม่มีแถวใน curriculum_rules เลย (เช่น 653170011)"""
    progress = planner.evaluate(
        "p", [], [], total_credits_required=120, group_rows=GROUP_ROWS
    )

    assert progress.percent_complete == 0.0
    assert progress.credits_left_to_graduate == 120
    assert planner.suggest_term(progress, 1).picks == ()


def test_group_quota_zero_is_complete_not_zero_percent() -> None:
    """โควตา 0 นก. = ไม่มีอะไรต้องเก็บ ห้ามรายงานว่าค้างอยู่ 0%"""
    group = planner.GroupProgress("9.9", "หมวดว่าง", 0)

    assert group.percent == 100.0
    assert group.complete is True
