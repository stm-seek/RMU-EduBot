"""
เทส router 3 ชั้น

สิ่งที่เทสนี้ยึดไว้ไม่ให้หลุด แม้ภายในจะเปลี่ยนไปอย่างไร:

* ทุกเส้นทางคืนข้อความที่ **ไม่ละเมิด limit ของ LINE**
* ``answered_by`` ถูกต้อง เพราะใช้วัดผลในธีสิสว่าแต่ละชั้นรับภาระเท่าไหร่
  และ fallback rate เป็นเท่าไหร่ (Requirement ข้อ 4.4)
  โดยเฉพาะ ``no_data`` (เข้าใจคำถามแต่ไม่มีข้อมูล) ต้องไม่ปนกับ
  ``fallback`` (ไม่เข้าใจคำถาม)
* **ไม่มีข้อมูลต้องบอกตรง ๆ ห้ามเดา** — รวมถึงตอนต่อ DB ไม่ได้
* postback ที่ไม่รู้จักต้องไม่พัง (ปุ่มเก่าใน Rich Menu ของ user ที่ยังไม่อัปเดต)
"""

from __future__ import annotations

from app import router as bot_router
from app.line import messages as msg

from .helpers import FakeDatabase, assert_line_limits

# ── ข้อมูลตัวอย่างที่สะท้อนของจริงใน knowledge base ──────────────────────────

CATEGORY_ROWS = [
    {"category": "loan", "total": 12},
    {"category": "registration", "total": 5},
    {"category": "internship", "total": 3},
]

DOCUMENT_ROWS = [
    {
        "title": "เอกสารขอเพิ่มรายวิชาเรียน",
        "url": "https://sci.rmu.ac.th/wp-content/uploads/2024/08/add.pdf",
        "doc_type": "pdf",
        "note": None,
    },
    {
        "title": "เอกสารขอขยายหน่วยกิต",
        "url": "https://sci.rmu.ac.th/wp-content/uploads/2024/08/credit.pdf",
        "doc_type": "pdf",
        "note": "ต้องให้อาจารย์ที่ปรึกษาเซ็นก่อน",
    },
]

GROUP_ROWS = [
    {"group_name": "สาขาวิชาเทคโนโลยีมัลติมีเดียและแอนิเมชัน", "total": 8},
    {"group_name": "สาขาวิชาวิทยาการคอมพิวเตอร์", "total": 6},
]

# **ต้องตรงกับรูปร่างข้อมูลจริง**: ตรวจกับ DB แล้วทั้ง 28 แถวมี ``full_name``
# ที่มีคำนำหน้าอยู่ในตัวแล้ว และ ``title_prefix`` เก็บคำนำหน้าเดิมซ้ำอีกที
# mock เดิมแยกสองฟิลด์ออกจากกันซึ่งไม่ใช่ของจริง → บั๊ก "คำนำหน้าซ้ำสองรอบ"
# ที่นักศึกษาเห็นบนหน้าจอจึงไม่โผล่ในเทสเลย
INSTRUCTOR_ROWS = [
    {
        "full_name": "ผศ.ดร.สมชาย ใจดี",
        "title_prefix": "ผศ.ดร",
        "email": "somchai@rmu.ac.th",
        "room": "SC-301",
        "office_hours": "จ-ศ 13.00-16.00",
        "position": "ประธานสาขา",
        "is_chair": True,
    },
    {
        "full_name": "อ.สมหญิง รักเรียน",
        "title_prefix": "อ",
        "email": None,
        "room": None,
        "office_hours": None,
        "position": None,
        "is_chair": False,
    },
]

# ตรงกับสถานะจริง: มี offering_patterns แต่ prerequisites/curriculum_rules ยังว่าง
COVERAGE_NO_PLAN = {
    "curriculum_rules": 0,
    "prerequisites": 0,
    "patterns": 45,
    "opens_sem1": 30,
    "opens_sem2": 33,
    "opens_sem3": 4,
    "program_courses": 125,
}

CONTACT_COVERAGE = {"total": 28, "with_email": 21, "with_phone": 0, "with_room": 5}


def documents_db() -> FakeDatabase:
    # ลำดับสำคัญ: ตัวที่เฉพาะเจาะจงกว่าต้องอยู่ก่อน
    return FakeDatabase(
        {
            "WHERE category = %s": DOCUMENT_ROWS,
            "GROUP BY category": CATEGORY_ROWS,
        }
    )


def instructors_db() -> FakeDatabase:
    return FakeDatabase(
        {
            "GROUP BY group_name": GROUP_ROWS,
            "JOIN instructor_affiliations": INSTRUCTOR_ROWS,
            "with_email": CONTACT_COVERAGE,
        }
    )


def plan_db(coverage: dict | None = None) -> FakeDatabase:
    return FakeDatabase({"curriculum_rules": coverage or COVERAGE_NO_PLAN})


# ── parse_postback_data ─────────────────────────────────────────────────────


def test_parse_postback_data_basic() -> None:
    assert bot_router.parse_postback_data("action=plan&term=1") == {
        "action": "plan",
        "term": "1",
    }


def test_parse_postback_data_handles_empty_and_none() -> None:
    """``data`` หายไปจาก payload ได้ — ต้องได้ dict ว่าง ไม่ใช่ exception"""
    assert bot_router.parse_postback_data("") == {}
    assert bot_router.parse_postback_data(None) == {}  # type: ignore[arg-type]


def test_parse_postback_data_decodes_percent_encoding() -> None:
    """
    ชื่อกลุ่มอาจารย์ (ไทย) ถูก URL-encode ตอนอยู่ใน postback data
    ต้อง decode กลับเป็นข้อความเดิม ไม่งั้น query หาไม่เจอ
    """
    encoded = "action=instructors&g=%E0%B8%AA%E0%B8%B2%E0%B8%82%E0%B8%B2"
    assert bot_router.parse_postback_data(encoded)["g"] == "สาขา"


def test_parse_postback_data_ignores_malformed_pairs() -> None:
    """
    บันทึกพฤติกรรมจริงของ :func:`urllib.parse.parse_qsl` — ค่าว่างถูกทิ้ง

    สำคัญเพราะ handler เช็ค ``action`` จาก dict นี้: ถ้าได้ ``{'action': ''}``
    แทน ``{}`` เส้นทางจะเปลี่ยน
    """
    assert bot_router.parse_postback_data("action=") == {}
    assert bot_router.parse_postback_data("action") == {}
    assert bot_router.parse_postback_data("&&") == {}


def test_parse_postback_data_last_value_wins() -> None:
    assert bot_router.parse_postback_data("action=plan&action=loan")["action"] == "loan"


# ── join_lines ──────────────────────────────────────────────────────────────


def test_join_lines_never_cuts_a_line_in_half() -> None:
    """
    ตัดกลาง URL แล้วนักศึกษากดลิงก์ไม่ได้ — ต้องตัดทั้งบรรทัดแล้วบอกว่ามีต่อ
    """
    url = "https://sci.rmu.ac.th/" + "a" * 200 + ".pdf"
    lines = [url] * 50
    text = bot_router.join_lines("เอกสาร", lines)

    assert len(text) <= msg.MAX_TEXT_LENGTH
    for line in text.split("\n"):
        assert line in ("เอกสาร", "", url) or line.startswith("(แสดง")
    assert "แสดง" in text, "ต้องบอกว่าแสดงไม่ครบ"


def test_join_lines_omits_notice_when_everything_fits() -> None:
    text = bot_router.join_lines("หัวข้อ", ["ก", "ข"], "ท้าย")
    assert "แสดง" not in text
    assert text == "หัวข้อ\n\nก\nข\n\nท้าย"


# ── ชั้นที่ 1: postback เมื่อไม่มี DB ────────────────────────────────────────


async def test_postback_without_db_answers_no_data() -> None:
    """
    ต่อ DB ไม่ได้ → ต้องบอกว่า "ยังไม่มีข้อมูล" ทุกหัวข้อที่ต้องใช้ DB
    ห้าม 500 และห้ามเงียบ (LINE จะ retry แล้ว user ได้ข้อความซ้ำ)
    """
    for action in ["documents", "instructors", "plan", "loan", "calendar"]:
        result = await bot_router.handle_postback(f"action={action}", None)

        assert_line_limits(result.messages)
        assert result.answered_by == "no_data", action
        assert result.intent_key == action, action


async def test_menu_works_without_db() -> None:
    """เมนูหลักไม่ต้องใช้ DB — ต้องใช้งานได้เสมอ"""
    result = await bot_router.handle_postback("action=menu", None)

    assert result.answered_by == "quick_reply"
    assert result.intent_key == "menu"
    assert_line_limits(result.messages)


async def test_rich_menu_taps_are_distinguishable_from_quick_reply_taps() -> None:
    """
    LINE ส่ง postback event หน้าตาเหมือนกันทุกอย่างไม่ว่ากดจาก Rich Menu หรือ
    Quick Reply → ต้องฝัง ``src=rich`` ไว้ในปุ่มของ Rich Menu เอง

    ถ้าเทสนี้แดง แปลว่า ``chat_logs`` กลับไปนับสองพื้นผิวรวมกันอีกครั้ง
    แล้วเคลมในธีสิสว่า "Rich Menu รับภาระเท่านี้" ไม่ได้
    """
    from_rich = await bot_router.handle_postback("action=menu&src=rich", None)
    from_chat = await bot_router.handle_postback("action=menu", None)

    assert from_rich.answered_by == "rich_menu"
    assert from_chat.answered_by == "quick_reply"
    # ข้อความที่ผู้ใช้เห็นต้องเหมือนกันเป๊ะ — ต่างกันแค่ป้ายสำหรับวัดผล
    assert from_rich.messages == from_chat.messages


async def test_button_answer_marker_never_reaches_chat_logs() -> None:
    """
    ``BUTTON_ANSWER`` เป็นป้ายชั่วคราวระหว่างทาง ถ้าหลุดออกไปถึง ``chat_logs``
    แปลว่ามี handler ที่ถูกเรียกโดยไม่ผ่าน :func:`handle_postback`
    """
    for data in ["action=menu", "action=documents&src=rich", "action=plan"]:
        result = await bot_router.handle_postback(data, documents_db())
        assert result.answered_by != bot_router.BUTTON_ANSWER, data


async def test_unknown_action_falls_back() -> None:
    """ปุ่มเก่าใน Rich Menu ของ user ที่ยังไม่อัปเดตยิง action ที่เลิกใช้เข้ามา"""
    result = await bot_router.handle_postback("action=ที่เลิกใช้แล้ว", instructors_db())

    assert_line_limits(result.messages)
    assert result.answered_by == "fallback"
    assert result.intent_key is None


async def test_garbage_postback_falls_back() -> None:
    for data in ["", "ขยะ", "action=", "%%%%", "a" * 500]:
        result = await bot_router.handle_postback(data, instructors_db())
        assert result.answered_by == "fallback"
        assert_line_limits(result.messages)


async def test_every_menu_button_has_a_handler() -> None:
    """
    เพิ่มปุ่มในเมนูแล้วลืมเขียน handler → user กดแล้วได้ fallback
    ทั้งที่เป็นปุ่มของเราเอง
    """
    for action in msg.MAIN_MENU_ACTIONS:
        key = bot_router.parse_postback_data(action["data"])["action"]
        assert key in bot_router.POSTBACK_HANDLERS, f"ไม่มี handler สำหรับ {key!r}"


# ── เอกสาร ──────────────────────────────────────────────────────────────────


async def test_document_categories_lists_thai_labels_and_counts() -> None:
    result = await bot_router._document_categories_answer(documents_db())

    assert_line_limits(result.messages)
    # เรียก handler ตรง ๆ → ยังเป็นป้ายกลาง ๆ (handle_postback เท่านั้นที่แทน
    # ด้วยพื้นผิวจริง — ดู test_rich_menu_taps_are_distinguishable...)
    assert result.answered_by == bot_router.BUTTON_ANSWER
    assert result.intent_key == "documents"

    text = result.messages[0]["text"]
    assert "กู้ยืม กยศ." in text, "ต้องแปลรหัสหมวดเป็นภาษาไทย"
    assert "12 ฉบับ" in text


async def test_document_categories_offer_buttons_with_a_way_back() -> None:
    """ทุกหน้าต้องมีทางกลับเมนู ไม่ให้ user ติดอยู่ในหน้านั้น"""
    result = await bot_router._document_categories_answer(documents_db())
    items = result.messages[0]["quickReply"]["items"]
    data = [item["action"]["data"] for item in items]

    assert "action=documents&cat=loan" in data
    assert "action=menu" in data


async def test_documents_list_includes_titles_urls_and_notes() -> None:
    result = await bot_router._documents_answer(documents_db(), "registration")

    assert_line_limits(result.messages)
    text = result.messages[0]["text"]
    assert "เอกสารขอเพิ่มรายวิชาเรียน" in text
    assert "https://sci.rmu.ac.th/wp-content/uploads/2024/08/add.pdf" in text
    assert "ต้องให้อาจารย์ที่ปรึกษาเซ็นก่อน" in text


async def test_documents_list_records_citations() -> None:
    """
    Requirement ข้อ 11: ต้องอ้างอิงแหล่งที่มาได้ทุกคำตอบ
    → เก็บลิงก์ไว้ใน ``citations`` เพื่อเขียนลง ``chat_logs``
    """
    result = await bot_router._documents_answer(documents_db(), "registration")

    assert len(result.citations) == len(DOCUMENT_ROWS)
    assert all(citation["url"].startswith("https://") for citation in result.citations)


async def test_loan_button_maps_to_document_category() -> None:
    """ปุ่ม "ทุน/กู้ยืม" ในเมนู = เอกสารหมวด loan (ไม่ต้องกดสองชั้น)"""
    db = documents_db()
    result = await bot_router.handle_postback("action=loan", db)

    assert result.intent_key == "loan"
    assert db.params_for("WHERE category = %s")[0] == "loan"


async def test_calendar_button_maps_to_document_category() -> None:
    db = documents_db()
    await bot_router.handle_postback("action=calendar", db)

    assert db.params_for("WHERE category = %s")[0] == "calendar"


async def test_empty_category_answers_no_data() -> None:
    """หมวดที่ไม่มีเอกสารเลย — บอกว่าไม่มี ไม่ใช่โชว์หัวข้อว่าง ๆ"""
    result = await bot_router._documents_answer(FakeDatabase(), "activity")

    assert result.answered_by == "no_data"
    assert_line_limits(result.messages)


# ── อาจารย์ ─────────────────────────────────────────────────────────────────


async def test_instructor_groups_states_what_contact_info_exists() -> None:
    """
    เว็บคณะไม่เผยแพร่เบอร์โทร (0/28) — ต้องบอกตรง ๆ ไม่ใช่เว้นว่าง
    ไม่งั้นผู้ใช้จะคิดว่าระบบพัง หรือคาดหวังให้บอทเดาเบอร์ให้
    """
    result = await bot_router._instructor_groups_answer(instructors_db())

    assert_line_limits(result.messages)
    text = result.messages[0]["text"]
    assert "อีเมล 21/28 คน" in text
    assert "ยังไม่มีเบอร์โทรในระบบ" in text


async def test_instructor_group_labels_are_truncated_but_data_is_not() -> None:
    """
    ชื่อสาขายาวกว่า 20 ตัวอักษร → label ถูกตัด แต่ ``data`` ต้องครบ
    ไม่งั้น query หากลุ่มไม่เจอ
    """
    result = await bot_router._instructor_groups_answer(instructors_db())
    action = result.messages[0]["quickReply"]["items"][0]["action"]

    assert len(action["label"]) <= msg.MAX_LABEL_LENGTH
    assert GROUP_ROWS[0]["group_name"] in action["data"]


async def test_instructors_list_marks_missing_email_explicitly() -> None:
    result = await bot_router._instructors_answer(instructors_db(), "สาขาวิชาทดสอบ")

    assert_line_limits(result.messages)
    text = result.messages[0]["text"]
    assert "ผศ.ดร.สมชาย ใจดี" in text
    assert "somchai@rmu.ac.th" in text
    assert "ไม่มีข้อมูลในระบบ" in text, "คนที่ไม่มีอีเมลต้องบอกตรง ๆ"
    assert "SC-301" in text
    # กันบั๊กที่เจอกับข้อมูลจริง: เอา title_prefix มาต่อหน้า full_name อีกที
    # จะได้ "ผศ.ดรผศ.ดร.สมชาย ใจดี" ซึ่งนักศึกษาเห็นบนหน้าจอ
    assert "ผศ.ดรผศ.ดร." not in text, "คำนำหน้าซ้ำสองรอบ"
    assert "อ.อ.สมหญิง" not in text


async def test_instructors_intent_key_includes_group() -> None:
    result = await bot_router._instructors_answer(instructors_db(), "สาขาก")
    assert result.intent_key == "instructors:สาขาก"


# ── แผนการเรียน ─────────────────────────────────────────────────────────────


async def test_plan_reports_only_what_it_knows() -> None:
    """
    ไม่มีแผนปี/เทอมของหลักสูตรเลย → ห้ามรับปากว่าจัดแผนได้
    ต้องบอกเหตุผลและเสนอสิ่งที่ทำได้จริง (รหัสวิชา 7 หลัก) แทน
    """
    result = await bot_router._plan_answer(plan_db())

    assert_line_limits(result.messages)
    assert result.answered_by == bot_router.BUTTON_ANSWER
    text = result.messages[0]["text"]
    assert "45 วิชา" in text
    assert "ยังจัดแผนรายเทอมให้ไม่ได้" in text
    assert "รหัสวิชา 7 หลัก" in text


async def test_plan_offers_the_planner_once_the_study_plan_is_loaded() -> None:
    """
    สถานะจริงตอนนี้: มีแผนปี/เทอม 32 วิชา แต่ prerequisites ยังว่าง

    ต้องบอกว่าคำนวณความก้าวหน้าได้แล้ว **พร้อมกับ** ไม่เคลมว่ารู้เงื่อนไข
    วิชาบังคับก่อน — เคลมเกินตรงนี้แปลว่านักศึกษาจะเชื่อลำดับที่ไม่ได้ยืนยัน
    """
    with_plan = dict(COVERAGE_NO_PLAN, curriculum_rules=32)
    result = await bot_router._plan_answer(plan_db(with_plan))

    text = result.messages[0]["text"]
    labels = [item["action"]["label"] for item in result.messages[0]["quickReply"]["items"]]

    assert "แผนการเรียนมาตรฐาน 32 วิชา" in text
    assert "ยังจัดแผนรายเทอมให้ไม่ได้" not in text
    assert "ไม่ใช่เงื่อนไขบังคับ" in text
    # ปุ่มนี้อยู่ใน MAIN_MENU_ACTIONS อยู่แล้ว — ต้องมีใบเดียว ไม่ใช่สองใบซ้อน
    assert labels.count("ความก้าวหน้า") == 1


async def test_plan_switches_message_when_prerequisites_arrive() -> None:
    """เมื่อกรอก มคอ.2 แล้ว ข้อความต้องเปลี่ยนเป็นเชิญให้ถามได้เลย"""
    complete = dict(COVERAGE_NO_PLAN, curriculum_rules=68, prerequisites=24)
    result = await bot_router._plan_answer(plan_db(complete))

    text = result.messages[0]["text"]
    assert "ยังจัดแผนรายเทอมให้ไม่ได้" not in text
    assert "ถามได้เลย" in text
    assert "ไม่ใช่เงื่อนไขบังคับ" not in text


async def test_plan_answers_no_data_when_nothing_loaded() -> None:
    empty = dict.fromkeys(COVERAGE_NO_PLAN, 0)
    result = await bot_router._plan_answer(plan_db(empty))

    assert result.answered_by == "no_data"


# ── ข้อความอิสระ ────────────────────────────────────────────────────────────


async def test_course_code_is_answered_from_database() -> None:
    db = FakeDatabase(
        {
            "FROM courses": {
                "course_code": "7010102",
                "name_th": "การเขียนโปรแกรมคอมพิวเตอร์",
                "name_en": "Computer Programming",
                "credits_text": "3(2-2-5)",
                "description_th": "หลักการเขียนโปรแกรม ตัวแปร ชนิดข้อมูล",
                "source_url": "https://regis.rmu.ac.th/course.asp?id=1",
                "opens_sem1": True,
                "opens_sem2": False,
                "opens_sem3": False,
                "terms_observed": 4,
            }
        }
    )
    result = await bot_router.handle_text("อยากรู้เรื่องวิชา 7010102 ครับ", db)

    assert_line_limits(result.messages)
    assert result.answered_by == "course", "พิมพ์รหัสมาเอง ไม่ได้กดปุ่มอะไร"
    assert result.intent_key == "course:7010102"

    text = result.messages[0]["text"]
    assert "การเขียนโปรแกรมคอมพิวเตอร์" in text
    assert "3(2-2-5)" in text
    assert "เทอม 1" in text
    assert "เทอม 2" not in text, "ห้ามบอกว่าเปิดเทอมที่ไม่ได้เปิด"
    assert result.citations[0]["url"].startswith("https://regis.rmu.ac.th")


SAMPLE_COURSE_ROWS = [
    {"course_code": "1109901", "name_th": "ภาษาอังกฤษสำหรับชีวิตประจำวัน"},
    {"course_code": "1109902", "name_th": "ภาษาไทยเพื่อการสื่อสาร"},
    {"course_code": "7071203", "name_th": "การออกแบบและพัฒนาระบบงานสารสนเทศ"},
]


def course_help_db() -> FakeDatabase:
    """ลำดับสำคัญ: SQL ของทั้งสอง query มีคำว่า ``program_courses`` เหมือนกัน"""
    return FakeDatabase(
        {
            "ORDER BY op.terms_found": SAMPLE_COURSE_ROWS,
            "curriculum_rules": COVERAGE_NO_PLAN,
        }
    )


async def test_course_button_explains_how_to_use_and_offers_real_examples() -> None:
    """
    ปุ่ม "ค้นรายวิชา" บน Rich Menu กดแล้วต้องมีของให้กดต่อ

    Rich Menu สั่งให้ผู้ใช้พิมพ์ต่อไม่ได้ → ถ้าตอบแค่ "พิมพ์รหัสมา"
    คนที่ไม่รู้รหัสวิชาจะตันอยู่ตรงนั้น
    """
    result = await bot_router.handle_postback("action=course", course_help_db())

    assert_line_limits(result.messages)
    assert result.intent_key == "course"

    text = result.messages[0]["text"]
    assert "125 วิชา" in text, "ต้องบอกจำนวนวิชาที่มีจริง"
    assert "45 วิชา" in text
    assert "1109901" in text, "ตัวอย่างรหัสวิชาต้องเป็นของจริงจาก DB"

    items = result.messages[0]["quickReply"]["items"]
    codes = [
        bot_router.parse_postback_data(item["action"]["data"]).get("code")
        for item in items
    ]
    assert codes[:3] == ["1109901", "1109902", "7071203"]
    assert codes[-1] is None, "ปุ่มสุดท้ายต้องเป็นเมนูหลัก"


async def test_course_button_never_hardcodes_an_example_code() -> None:
    """
    ถ้า re-scrape แล้วรหัสตัวอย่างหายไป บอทต้องไม่แนะนำวิชาที่ตอบไม่ได้

    → ตัวอย่างในข้อความต้องมาจากแถวที่ query ได้จริงเท่านั้น
    """
    db = FakeDatabase({"curriculum_rules": COVERAGE_NO_PLAN})
    result = await bot_router.handle_postback("action=course", db)

    text = result.messages[0]["text"]
    assert "เช่น" not in text, "ไม่มีข้อมูลตัวอย่างแล้วห้ามยกตัวอย่าง"
    assert "พิมพ์รหัสวิชา 7 หลัก" in text
    assert result.messages[0]["quickReply"]["items"], "ยังต้องมีปุ่มเมนูหลัก"


async def test_course_button_with_code_answers_that_course_directly() -> None:
    """
    ปุ่มวิชาตัวอย่างต้องวิ่งเข้าเส้นทางเดียวกับที่ผู้ใช้พิมพ์รหัสมาเอง
    ไม่ใช่ code path แยกที่ต้องดูแลสองที่
    """
    db = FakeDatabase(
        {
            "FROM courses": {
                "course_code": "1109901",
                "name_th": "ภาษาอังกฤษสำหรับชีวิตประจำวัน",
                "credits_text": "3(2-2-5)",
                "opens_sem1": True,
                "terms_observed": 4,
            }
        }
    )
    result = await bot_router.handle_postback("action=course&code=1109901", db)

    assert_line_limits(result.messages)
    assert result.intent_key == "course:1109901"
    assert "ภาษาอังกฤษสำหรับชีวิตประจำวัน" in result.messages[0]["text"]


async def test_course_button_without_database_says_no_data() -> None:
    result = await bot_router.handle_postback("action=course", None)

    assert result.answered_by == "no_data"
    assert result.intent_key == "course"


async def test_course_without_offering_pattern_says_so() -> None:
    """
    วิชาที่ไม่เคยเจอในตารางสอน → บอกว่ายังไม่พบ ห้ามเดาว่าเปิดเทอมไหน
    """
    db = FakeDatabase({"FROM courses": {"course_code": "7010999", "name_th": "วิชาใหม่"}})
    result = await bot_router.handle_text("7010999", db)

    assert "ยังไม่พบว่าเปิดสอน" in result.messages[0]["text"]


async def test_unknown_course_code_answers_no_data() -> None:
    result = await bot_router.handle_text("1234567", FakeDatabase())

    assert result.answered_by == "no_data"
    assert result.intent_key == "course:1234567"


async def test_course_code_must_be_exactly_seven_digits() -> None:
    """
    รหัสวิชาของ regis.rmu.ac.th เป็นเลข 7 หลักเต็ม
    เลข 6 หรือ 8 หลักไม่ใช่รหัสวิชา — **ห้ามไปค้นตาราง ``courses``**

    ตอนนี้ข้อความอิสระจะถูกส่งไปค้นเอกสาร/อาจารย์ต่อ (ชั้นที่ 1 ทางพิมพ์)
    จึงมี query เกิดขึ้นได้ แต่ต้องไม่ใช่การ lookup รายวิชา
    """
    db = FakeDatabase()

    for text in ["123456", "123456789", "ปี 2568 เทอม 2", "โทร 0-4372-2118"]:
        result = await bot_router.handle_text(text, db)
        assert result.answered_by == "fallback", text

    touched_courses = [sql for sql, _ in db.calls if "FROM courses" in sql]
    assert touched_courses == [], "ไม่ควร lookup รายวิชาจากเลขที่ไม่ใช่ 7 หลัก"


async def test_any_seven_digit_number_is_looked_up_as_a_course_code() -> None:
    """
    ข้อจำกัดที่ยอมรับไว้: เลข 7 หลักลอย ๆ แยกจากรหัสวิชาไม่ได้ด้วยรูปแบบ
    (เบอร์โทรไม่มีขีดก็เป็น 7 หลักได้)

    ผลลัพธ์ที่ยอมรับได้คือ **ค้นแล้วไม่เจอ → บอกว่าไม่มีข้อมูล** ซึ่งซื่อสัตย์
    และไม่ทำให้เข้าใจผิด — ห้ามเดาว่าเป็นวิชาอะไร
    """
    db = FakeDatabase()
    result = await bot_router.handle_text("โทร 0437221 ต่อ 269", db)

    assert result.answered_by == "no_data"
    assert result.intent_key == "course:0437221"
    assert db.count == 1


async def test_free_text_without_course_code_falls_back_honestly() -> None:
    result = await bot_router.handle_text("ถอนรายวิชาวันสุดท้ายวันไหน", FakeDatabase())

    assert_line_limits(result.messages)
    assert result.answered_by == "fallback"
    assert result.confidence is None
    assert result.citations == []


async def test_long_question_is_truncated_in_echo() -> None:
    result = await bot_router.handle_text("ก" * 600, None)

    assert_line_limits(result.messages)
    assert "…" in result.messages[0]["text"]


async def test_blank_text_falls_back() -> None:
    for text in ["", "   ", "\n\t ", None]:
        result = await bot_router.handle_text(text, None)  # type: ignore[arg-type]
        assert result.answered_by == "fallback"
        assert_line_limits(result.messages)


# ── follow ──────────────────────────────────────────────────────────────────


async def test_follow_welcomes_with_capabilities() -> None:
    """
    ข้อความต้อนรับต้องบอกว่า "ทำอะไรได้จริง" ไม่ใช่สัญญาสิ่งที่ยังทำไม่ได้
    """
    result = await bot_router.handle_follow()

    assert_line_limits(result.messages)
    assert result.answered_by == "follow", "การเพิ่มเพื่อนไม่ใช่การกดปุ่ม"
    assert result.intent_key == "follow"
    assert result.messages[0]["quickReply"]["items"]
    assert "รหัสวิชา 7 หลัก" in result.messages[0]["text"]


async def test_menu_button_reuses_the_welcome_message_but_not_its_label() -> None:
    """
    ปุ่ม "เมนูหลัก" ใช้ข้อความเดียวกับตอนต้อนรับ แต่ต้องนับแยกกัน
    ไม่งั้นยอดกดเมนูจะบวกทุกครั้งที่มีคนเพิ่มเพื่อนใหม่
    """
    tapped = await bot_router.handle_follow(intent_key="menu")

    assert tapped.answered_by == bot_router.BUTTON_ANSWER
    assert tapped.messages == (await bot_router.handle_follow()).messages


# ── RouteResult ─────────────────────────────────────────────────────────────


def test_route_result_defaults_are_log_ready() -> None:
    """``citations`` ต้องเป็นลิสต์ใหม่ทุกครั้ง ไม่ใช่ mutable default ที่แชร์กัน"""
    first = bot_router.RouteResult(messages=[], answered_by="fallback")
    second = bot_router.RouteResult(messages=[], answered_by="fallback")

    first.citations.append({"title": "x"})
    assert second.citations == []
    assert first.intent_key is None
    assert first.llm_model is None


# ── ค้นด้วยคำที่พิมพ์มา (ชั้นที่ 1 ทางข้อความ) ─────────────────────────────────

SEARCH_DOCUMENT_ROWS = [
    {
        "title": "101 แบบคำขอกู้ยืมเงิน",
        "url": "https://sci.rmu.ac.th/wp-content/uploads/2016/07/101.pdf",
        "category": "loan",
        "keywords": "กู้ยืม,กยศ,แบบคำขอกู้ยืม",
        "score": 1.0,
    },
    {
        "title": "108 กยศ. แบบรายงานสถานภาพการศึกษา",
        "url": "https://sci.rmu.ac.th/wp-content/uploads/2016/07/108.pdf",
        "category": "loan",
        "keywords": "สถานภาพการศึกษา,กยศ",
        "score": 0.8,
    },
]

SEARCH_INSTRUCTOR_ROWS = [
    {
        "full_name": "ผศ.ดร.ธรัช อารีราษฎร์",
        "title_prefix": "ผศ.ดร",
        "email": "dr.tharach@rmu.ac.th",
        "room": None,
        "office_hours": None,
        "score": 1.0,
    }
]


def search_db(documents=None, instructors=None) -> FakeDatabase:
    """
    fake ที่แยกสอง query ค้นหาออกจากกันด้วยชื่อตารางใน SQL

    ทั้งสอง query มีคำว่า ``word_similarity`` เหมือนกัน จึงต้องจับด้วย
    ``FROM documents`` / ``FROM instructors`` ไม่ใช่ชื่อฟังก์ชัน
    """
    return FakeDatabase(
        {
            "FROM instructors i": instructors or [],
            "FROM documents d": documents or [],
        }
    )


async def test_free_text_finds_documents() -> None:
    result = await bot_router.handle_text("กยศ", search_db(SEARCH_DOCUMENT_ROWS))

    assert_line_limits(result.messages)
    assert result.answered_by == "search"
    assert result.intent_key == "search:documents"
    # ``confidence`` ต้องเป็นคะแนนจริงจาก pg_trgm ไม่ใช่ 1.0 แปะไว้เฉย ๆ
    assert result.confidence == 1.0
    text = result.messages[0]["text"]
    assert "101 แบบคำขอกู้ยืมเงิน" in text
    assert "https://sci.rmu.ac.th/wp-content/uploads/2016/07/101.pdf" in text
    assert "กู้ยืม กยศ." in text, "ต้องบอกหมวดเพื่อให้กดดูทั้งหมดต่อได้"


async def test_free_text_attaches_citations_for_every_document() -> None:
    """``chat_logs.citations`` ต้องเก็บครบ ไม่ใช่แค่ฉบับแรก"""
    result = await bot_router.handle_text("กยศ", search_db(SEARCH_DOCUMENT_ROWS))

    assert [c["title"] for c in result.citations] == [
        "101 แบบคำขอกู้ยืมเงิน",
        "108 กยศ. แบบรายงานสถานภาพการศึกษา",
    ]


async def test_free_text_finds_instructors_when_no_document_matches() -> None:
    result = await bot_router.handle_text(
        "ธรัช", search_db(instructors=SEARCH_INSTRUCTOR_ROWS)
    )

    assert result.answered_by == "search"
    assert result.intent_key == "search:instructors"
    text = result.messages[0]["text"]
    assert "ผศ.ดร.ธรัช อารีราษฎร์" in text
    assert "dr.tharach@rmu.ac.th" in text
    assert "ผศ.ดรผศ.ดร." not in text, "คำนำหน้าซ้ำสองรอบ"


async def test_instructor_search_wins_over_document_search() -> None:
    """
    **ลำดับสำคัญ**: ถามถึงตัวบุคคลต้องได้อีเมลของคนนั้น ไม่ใช่ลิงก์รายชื่อบุคลากร

    วัดกับข้อมูลจริงแล้วเอกสาร "ข้อมูลบุคลากรสายวิชาการ" มี keyword ว่า
    "อาจารย์" / "อีเมลอาจารย์" → ได้คะแนน 1.000 สูงกว่าตัวอาจารย์ที่ถามถึง
    (0.800) ถ้าเรียงด้วยคะแนนจะตอบผิดคน
    """
    db = search_db(documents=SEARCH_DOCUMENT_ROWS, instructors=SEARCH_INSTRUCTOR_ROWS)

    result = await bot_router.handle_text("อาจารย์ธรัชสอนวิชาอะไร", db)

    assert result.intent_key == "search:instructors"
    assert [sql for sql, _ in db.calls if "FROM documents d" in sql] == [], (
        "เจออาจารย์แล้วไม่ต้องยิง query เอกสารอีก"
    )


async def test_free_text_without_any_match_falls_back_honestly() -> None:
    """ไม่เจอ → ต้องบอกว่าไม่พบ ห้ามเดา และต้องไม่ใช่ ``search``"""
    result = await bot_router.handle_text("วันนี้กินอะไรดี", search_db())

    assert result.answered_by == "fallback"
    assert result.intent_key == "text"
    assert "ยังไม่พบข้อมูล" in result.messages[0]["text"]


async def test_free_text_search_is_skipped_without_a_database() -> None:
    result = await bot_router.handle_text("กยศ", None)

    assert result.answered_by == "fallback"


async def test_course_code_takes_priority_over_search() -> None:
    """รหัสวิชา 7 หลักชัดเจนกว่าคำค้น — ต้องไม่ไปยิง query ค้นหา"""
    db = search_db(SEARCH_DOCUMENT_ROWS)

    await bot_router.handle_text("1234567", db)

    assert [sql for sql, _ in db.calls if "word_similarity" in sql] == []


# ── DB ล่มกลางบทสนทนา ──────────────────────────────────────────────────────


class ExplodingDatabase:
    """
    fake ที่โยน exception ทุก query — เลียนแบบ DB ล่ม *หลัง* แอปสตาร์ทแล้ว

    ต่างจาก ``db=None`` (ต่อไม่ได้ตั้งแต่สตาร์ท) ซึ่งตอบ ``no_data``
    """

    async def fetch_all(self, sql: str, params=None) -> list[dict]:
        raise RuntimeError("server closed the connection unexpectedly")

    async def fetch_one(self, sql: str, params=None) -> dict | None:
        raise RuntimeError("server closed the connection unexpectedly")


async def test_database_failure_mid_conversation_still_answers() -> None:
    """
    บั๊กที่เทสนี้กัน: เดิมไม่มี try/except รอบ query เลย → exception ทะลุถึง
    ``app.main.process_event`` ที่ ``except Exception: log.exception(...)``
    → **นักศึกษาไม่ได้ข้อความอะไรกลับเลย (เงียบ)** ซึ่งแย่กว่าบอกว่าระบบขัดข้อง
    """
    result = await bot_router.handle_text("กยศ", ExplodingDatabase())

    assert_line_limits(result.messages)
    assert result.answered_by == "db_error"
    assert result.messages, "ต้องมีข้อความตอบกลับ ห้ามเงียบ"
    assert "ขัดข้อง" in result.messages[0]["text"]


async def test_database_failure_on_postback_still_answers() -> None:
    result = await bot_router.handle_postback("action=loan", ExplodingDatabase())

    assert result.answered_by == "db_error"
    assert result.intent_key == "loan"


async def test_db_error_is_not_confused_with_no_data() -> None:
    """
    สองอย่างนี้ต้องแยกกันทั้งข้อความและ ``answered_by``

    ถ้าใช้ค่าเดียวกัน ตัวเลขวัดผลจะนับ "DB ล่ม" เป็น "คลังข้อมูลไม่ครบ"
    และนักศึกษาจะเลิกถามเพราะคิดว่าไม่มีข้อมูลจริง
    """
    broken = await bot_router.handle_postback("action=loan", ExplodingDatabase())
    missing = await bot_router.handle_postback("action=loan", None)

    assert broken.answered_by == "db_error"
    assert missing.answered_by == "no_data"
    assert broken.messages[0]["text"] != missing.messages[0]["text"]


async def test_db_error_still_offers_the_menu() -> None:
    """ต้องมีทางกลับเมนู ไม่งั้น user ติดอยู่กับข้อความ error"""
    result = await bot_router.handle_text("กยศ", ExplodingDatabase())

    assert "quickReply" in result.messages[0]


# ── จำนวนเอกสารต่อหมวด ─────────────────────────────────────────────────────


async def test_documents_answer_asks_for_more_than_the_repository_default() -> None:
    """
    บั๊กที่เทสนี้กัน: เดิมเรียก ``documents_in_category`` โดยไม่ส่ง ``limit``
    → ได้ default 10 แต่หมวด ``loan`` มีเอกสารใช้ได้ 12 ฉบับ
    → เมนูบอก "12 ฉบับ" กดเข้าไปเห็น "(10 ฉบับ)" และ 2 ฉบับสุดท้าย
    **เข้าถึงไม่ได้เลยจากบอท** ทั้งที่ข้อความยังห่างเพดานตัวอักษรมาก
    """
    db = documents_db()

    await bot_router._documents_answer(db, "loan")

    params = db.params_for("WHERE category = %s")
    assert params is not None
    assert params[1] == bot_router.DOCUMENTS_PER_CATEGORY
    assert bot_router.DOCUMENTS_PER_CATEGORY > max(
        row["total"] for row in CATEGORY_ROWS
    ), "เพดานต้องมากกว่าหมวดที่ใหญ่สุด ไม่งั้นบั๊กเดิมกลับมา"
