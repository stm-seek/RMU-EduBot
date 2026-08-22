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
