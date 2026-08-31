"""
เทสชั้น planner ที่ต่อกับบทสนทนา (:mod:`app.progress`)

สิ่งที่ไฟล์นี้ยืนยัน:

1. ปุ่ม/ข้อความเรื่องความก้าวหน้าถูกส่งไปที่ชั้น planner **ไม่ใช่** ไปค้นเอกสาร
2. ยังไม่ได้ติ๊กวิชา → บอกวิธีให้ข้อมูล ไม่เดาจากชั้นปี และป้ายเป็น ``no_data``
3. คำตอบต้องมีคำเตือนว่ายังไม่มีข้อมูลวิชาบังคับก่อน (ตราบใดที่ตารางยังว่าง)
4. ข้อความที่ส่งออกไม่ละเมิด limit ของ LINE
"""

from __future__ import annotations

import pytest

from app import progress as prog
from app import router

from .helpers import FakeDatabase, assert_line_limits, flex_body_text, make_settings

USER_HASH = "hash-for-test"

PLAN_ROWS = [
    {
        "course_code": "1000001",
        "course_code_full": "1000001-1",
        "std_year": 1,
        "std_semester": 1,
        "credits": 3,
        "name_th": "วิชาปีหนึ่งเทอมหนึ่ง",
        "opens_sem1": True,
    },
    {
        "course_code": "2000001",
        "course_code_full": "2000001-1",
        "std_year": 2,
        "std_semester": 1,
        "credits": 3,
        "name_th": "วิชาปีสองเทอมหนึ่ง",
        "opens_sem1": True,
    },
]


def db_with(passed: list[str], *, profile: dict | None = None) -> FakeDatabase:
    """FakeDatabase ที่ตอบครบทุกคิวรีที่ :func:`app.progress.load_progress` ถาม"""
    return FakeDatabase(
        {
            "FROM app_users u": profile
            if profile is not None
            else {
                "id": 7,
                "program_code": "643170151",
                "study_year": 2,
                "entry_year": 2564,
                "completed_courses": len(passed),
            },
            "FROM curriculum_rules cr": PLAN_ROWS,
            "FROM prerequisites p": [],
            "FROM user_completed_courses": [{"course_code": code} for code in passed],
            "FROM programs": {
                "program_code": "643170151",
                "program_name": "การจัดการนวัตกรรมดิจิทัล",
                "total_credits": 120,
            },
            "FROM offerings o": [],
            "FROM offerings": {"acad_year": 2568, "semester": 2, "offerings": 45},
            # SQL_COURSE_BY_CODE — ทางตอบรายละเอียดวิชาแบบเดิม
            "FROM courses c": {
                "course_code": "2000001",
                "name_th": "วิชาปีสองเทอมหนึ่ง",
                "credits": 3,
                "credits_text": "3 (2-2-5)",
                "opens_sem1": True,
            },
        }
    )


@pytest.fixture
def settings():
    return make_settings(liff_id="1234-abcd")


# ── การส่งต่อคำถาม ───────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "ความก้าวหน้าเป็นยังไง",
        "เหลืออีกกี่วิชา",
        "จบได้ไหม",
        "หน่วยกิตที่เหลือ",
        # สำนวน "เท่าไหร่" — เคยตกไป fallback ทั้งชุด (เจอตอนทดสอบจริง
        # 23 ส.ค. 2026: "เรียนไปได้เท่าไหร่แล้ว" ได้ answered_by=fallback)
        "เรียนไปได้เท่าไหร่แล้ว",
        "ผ่านไปได้เท่าไรแล้ว",
        "เหลืออีกเท่าไหร่",
    ],
)
@pytest.mark.asyncio
async def test_progress_questions_reach_the_planner(text: str, settings) -> None:
    result = await router.handle_text(
        text, db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )

    assert result.answered_by == "planner"
    assert result.intent_key == "progress"
    assert_line_limits(result.messages)


@pytest.mark.parametrize("text", ["เทอมหน้าลงอะไรดี", "เทอมถัดไปเรียนอะไรต่อ"])
@pytest.mark.asyncio
async def test_next_term_questions_reach_the_planner(text: str, settings) -> None:
    result = await router.handle_text(
        text, db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )

    assert result.answered_by == "planner"
    assert result.intent_key == "next_term"


@pytest.mark.asyncio
async def test_progress_button_uses_the_planner(settings) -> None:
    result = await router.handle_postback(
        "action=progress", db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )

    assert result.answered_by == "planner"
    assert_line_limits(result.messages)


@pytest.mark.asyncio
async def test_next_button_asks_for_next_term(settings) -> None:
    result = await router.handle_postback(
        "action=progress&next=1",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )

    assert result.intent_key == "next_term"


# ── ยังไม่มีข้อมูลของผู้ใช้ ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_profile_asks_to_tick_courses_instead_of_guessing(settings) -> None:
    """
    ไม่มีแถวผู้ใช้ → ต้องบอกวิธีให้ข้อมูล ไม่ใช่เดาจากชั้นปี

    เดาแล้วผิดแบบที่ผู้ใช้จับไม่ได้ เพราะคำตอบหน้าตาเหมือนของจริงเป๊ะ
    """
    result = await router.handle_postback(
        "action=progress", db_with([], profile=None), settings=settings, user_hash=USER_HASH
    )
    text = result.messages[0]["text"]

    assert result.answered_by == "no_data"
    assert result.intent_key == "progress_no_profile"
    assert "ติ๊ก" in text
    assert "รหัสผ่าน" in text, "ต้องบอกว่าไม่ได้ขอรหัสผ่านระบบทะเบียน"


@pytest.mark.asyncio
async def test_profile_without_ticked_courses_also_asks_first(settings) -> None:
    profile = {
        "id": 7,
        "program_code": "643170151",
        "study_year": 3,
        "entry_year": 2564,
        "completed_courses": 0,
    }
    result = await router.handle_postback(
        "action=progress", db_with([], profile=profile), settings=settings, user_hash=USER_HASH
    )

    assert result.intent_key == "progress_no_profile"


@pytest.mark.asyncio
async def test_liff_button_is_omitted_when_liff_id_missing() -> None:
    """ปุ่มที่กดแล้วไปหน้าเปล่าแย่กว่าไม่มีปุ่ม"""
    result = await router.handle_postback(
        "action=progress",
        db_with([], profile=None),
        settings=make_settings(liff_id=""),
        user_hash=USER_HASH,
    )
    labels = [
        item["action"]["label"]
        for item in result.messages[0]["quickReply"]["items"]
    ]

    assert "ติ๊กวิชาที่ผ่านแล้ว" not in labels


@pytest.mark.asyncio
async def test_without_database_answers_no_data(settings) -> None:
    result = await router.handle_postback(
        "action=progress", None, settings=settings, user_hash=USER_HASH
    )

    assert result.answered_by == "no_data"


# ── เนื้อหาคำตอบ ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_overview_reports_numbers_from_the_database(settings) -> None:
    result = await router.handle_postback(
        "action=progress", db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )
    text = flex_body_text(result.messages[0])

    assert "ผ่านแล้ว 1/2 วิชา" in text
    assert "3 หน่วยกิต" in text
    assert "120 หน่วยกิต" in text, "ต้องอ้างหน่วยกิตที่หลักสูตรกำหนด"
    assert "2000001" in text, "วิชาที่ยังไม่ผ่านต้องถูกแสดง"


@pytest.mark.asyncio
async def test_answer_warns_that_prerequisites_are_unknown(settings) -> None:
    """
    ตาราง prerequisites ยังว่างจริง — ถ้าไม่เตือน นักศึกษาจะเข้าใจว่าลำดับนี้
    คือเงื่อนไขวิชาบังคับก่อน แล้วไปลงวิชาที่ลงไม่ได้
    """
    result = await router.handle_postback(
        "action=progress", db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )

    assert "แผนการเรียนแนะนำ" in flex_body_text(result.messages[0])


@pytest.mark.asyncio
async def test_eligibility_question_answers_from_user_state(settings) -> None:
    """"ลงวิชา 2000001 ได้ไหม" ต้องตอบจากสถานะจริง ไม่ใช่รายละเอียดวิชาเฉย ๆ"""
    result = await router.handle_text(
        "ลงวิชา 2000001 ได้ไหม",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )

    assert result.answered_by == "planner"
    assert result.intent_key == "eligibility"
    assert "ลงได้ครับ" in result.messages[0]["text"]


@pytest.mark.asyncio
async def test_eligibility_says_passed_when_already_done(settings) -> None:
    result = await router.handle_text(
        "1000001 ลงได้ไหม", db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )

    assert "ผ่านวิชานี้แล้ว" in result.messages[0]["text"]


@pytest.mark.asyncio
async def test_course_code_without_eligibility_words_still_shows_course_details(
    settings,
) -> None:
    """พิมพ์รหัสเปล่า ๆ = ถามรายละเอียดวิชา ต้องไม่ถูกชั้น planner ยึดไป"""
    result = await router.handle_text(
        "2000001", db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )

    assert result.answered_by == "course"


@pytest.mark.asyncio
async def test_next_term_lists_only_courses_open_that_semester(settings) -> None:
    """
    เทอมล่าสุดในคลังคือ 2568/2 → เทอมถัดไปคือภาคเรียนที่ 1
    วิชาที่เปิดเฉพาะเทอม 2 ต้องไม่ถูกเสนอ
    """
    result = await router.handle_postback(
        "action=progress&next=1",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )
    text = flex_body_text(result.messages[0])

    assert "ภาคเรียนที่ 1" in text
    assert "2000001" in text
    assert f"เพดานที่ใช้คิด {settings.planner_max_credits}" in text


# ── ข้อ 4.4 ให้คำปรึกษาด้านผลการเรียน ────────────────────────────────────────


@pytest.mark.parametrize(
    "text, intent",
    [
        ("เกรดตอนนี้ 2.75 อยากได้ 3.00", "gpa_target"),
        ("GPA 3.4 ยังลุ้นเกียรตินิยมได้ไหม", "gpa_honors"),
        ("เกรด 2.5 ตอนนี้เป็นยังไง", "gpa_scenarios"),
        ("เกรดเฉลี่ยต้องได้เท่าไหร่", "gpa_need_gpax"),
    ],
)
@pytest.mark.asyncio
async def test_grade_questions_reach_the_planner(text: str, intent: str, settings) -> None:
    """คำถามเรื่องเกรดต้องเข้าชั้นคำนวณ ไม่ใช่ปล่อยให้ LLM เดาเลข"""
    result = await router.handle_text(
        text, db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )

    assert result.answered_by == "planner"
    assert result.intent_key == intent
    assert_line_limits(result.messages)


@pytest.mark.parametrize(
    "text", ["ขอใบเกรด", "ขอใบรายงานผลการเรียน", "ขอ transcript ยื่นที่ไหน"]
)
@pytest.mark.asyncio
async def test_asking_for_a_transcript_is_not_a_gpa_question(text: str, settings) -> None:
    """
    "ขอใบเกรด" คือคำขอเอกสาร ไม่ใช่คำถามคำนวณเกรด

    เคสนี้เป็น false positive ที่เกิดง่ายมาก เพราะคำว่า "เกรด" อยู่ในทั้งสอง
    เรื่อง — ถ้าชั้นเกรดดูดไป ผู้ใช้จะได้ตารางคำนวณแทนวิธีขอเอกสาร
    """
    result = await router.handle_text(
        text, db_with(["1000001"]), settings=settings, user_hash=USER_HASH
    )

    assert not (result.intent_key or "").startswith("gpa")


@pytest.mark.asyncio
async def test_gpa_prompt_already_knows_the_remaining_credits(settings) -> None:
    """
    ขอแค่ GPAX เลขเดียว — "เหลืออีกกี่หน่วยกิต" ระบบรู้เองจากวิชาที่ติ๊กไว้

    นี่คือสิ่งที่ทำให้ต่างจากเว็บคิดเกรดทั่วไป ถ้าคำตอบไม่บอกตัวเลขนี้
    ผู้ใช้จะไม่เห็นความต่าง แล้วไปกรอกเว็บอื่นเองอยู่ดี
    """
    result = await router.handle_text(
        "เกรดเฉลี่ยคิดยังไง",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )
    text = result.messages[0]["text"]

    assert result.intent_key == "gpa_need_gpax"
    assert "117 หน่วยกิต" in text, "120 - 3 ที่ผ่านแล้ว"
    assert "ไม่เก็บเกรด" in text


@pytest.mark.asyncio
async def test_reachable_target_reports_the_grade_needed(settings) -> None:
    """เป้าที่ยังทำได้ ต้องบอกทั้งแต้มเฉลี่ยและเกรดที่เทียบเท่า"""
    result = await router.handle_text(
        "เกรดตอนนี้ 2.75 อยากได้ 3.00",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )
    text = result.messages[0]["text"]

    assert "3.01" in text, "ต้องปัดขึ้นจาก 3.0064 ไม่ใช่ปัดลงเป็น 3.00"
    assert "B+" in text
    assert "117 หน่วยกิต" in text
    assert_line_limits(result.messages)


@pytest.mark.asyncio
async def test_impossible_target_says_so_and_gives_the_ceiling(settings) -> None:
    """
    เป้าที่ไปไม่ถึงต้องบอกตรง ๆ พร้อมเพดานจริง

    ให้กำลังใจแบบผิดข้อมูลแย่กว่าบอกความจริง เพราะนักศึกษาจะวางแผนต่อ
    บนตัวเลขที่เป็นไปไม่ได้ทั้งปี
    """
    result = await router.handle_text(
        "เกรด 2.75 อยากได้ 4.00",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )
    text = result.messages[0]["text"]

    assert "ไปไม่ถึง" in text
    assert "3.97" in text, "ได้ A ทุกวิชาที่เหลือได้สูงสุดเท่านี้"


@pytest.mark.asyncio
async def test_honors_answer_covers_both_ranks_and_admits_unknown_rules(
    settings,
) -> None:
    result = await router.handle_text(
        "เกรด 2.0 ยังลุ้นเกียรตินิยมได้ไหม",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )
    text = result.messages[0]["text"]

    assert "เกียรตินิยมอันดับ 1" in text and "เกียรตินิยมอันดับ 2" in text
    assert "เงื่อนไขอื่นที่ระบบยังไม่รู้" in text, "ห้ามเคลมว่ารู้เกณฑ์ครบ"
    assert_line_limits(result.messages)


@pytest.mark.asyncio
async def test_grade_answer_discloses_the_scale_it_used(settings) -> None:
    """
    สเกลแต้มเกรดยังไม่ได้ยืนยันกับข้อบังคับ RMU → ต้องบอกว่าคิดด้วยอะไร

    ถ้าสเกลจริงต่างจากนี้ ตัวเลขทุกตัวเปลี่ยน ผู้ใช้ต้องตรวจได้เอง
    """
    result = await router.handle_text(
        "เกรด 2.75 อยากได้ 3.00",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )
    text = result.messages[0]["text"]

    assert "A 4.00" in text and "B+ 3.50" in text
    assert "ยังไม่ได้ยืนยันกับข้อบังคับ" in text


@pytest.mark.asyncio
async def test_grade_question_without_ticked_courses_asks_for_them(settings) -> None:
    """ไม่รู้ว่าเหลือกี่หน่วยกิต = คำนวณไม่ได้ ต้องชวนไปติ๊ก ไม่ใช่เดา"""
    result = await router.handle_text(
        "เกรด 2.75 อยากได้ 3.00", db_with([]), settings=settings, user_hash=USER_HASH
    )

    assert result.answered_by == "no_data"
    assert result.intent_key == "progress_no_profile"
    assert "เกรด" in result.messages[0]["text"]


@pytest.mark.asyncio
async def test_manual_credit_override_is_used_and_acknowledged(settings) -> None:
    """
    ผู้ใช้แก้หน่วยกิตที่คิดเกรดได้เอง เพราะของ planner ไม่ตรงเมื่อมีวิชาติด F

    ถ้าเตือนว่า "อาจไม่ตรง" แล้วไม่ให้ทางแก้ คำเตือนนั้นก็ไร้ประโยชน์
    """
    result = await router.handle_text(
        "เกรด 2.75 เก็บไปแล้ว 66 หน่วยกิต อยากได้ 3.00",
        db_with(["1000001"]),
        settings=settings,
        user_hash=USER_HASH,
    )
    text = result.messages[0]["text"]

    assert "คิดเกรดแล้ว 66 หน่วยกิต" in text
    assert "ใช้จำนวนหน่วยกิตที่คุณบอกมาคิด" in text
