"""
เทส message builder — ที่เดียวที่รู้เรื่อง limit ของ LINE

ถ้าละเมิด limit LINE จะ **reject ทั้ง request** (ไม่ตัดให้เอง) → user ไม่ได้
คำตอบเลย และเราเห็นแค่ HTTP 400 ที่ debug ยาก จึงต้องดักที่ชั้นนี้
"""

from __future__ import annotations

from app.line import messages as msg

from .helpers import assert_line_limits

# ── truncate ────────────────────────────────────────────────────────────────


def test_truncate_keeps_short_text() -> None:
    assert msg.truncate("สวัสดี", 10) == "สวัสดี"
    assert msg.truncate("abcde", 5) == "abcde"


def test_truncate_adds_ellipsis_within_limit() -> None:
    result = msg.truncate("abcdefghij", 5)
    assert result == "abcd…"
    assert len(result) == 5


def test_truncate_counts_characters_not_bytes() -> None:
    """
    ไทย 1 ตัวอักษร = 3 ไบต์ใน UTF-8 แต่ LINE นับเป็น "ตัวอักษร"

    ถ้านับผิดเป็นไบต์ ข้อความไทยจะถูกตัดเหลือ 1/3 ของที่ควรได้
    """
    assert len(msg.truncate("ก" * 100, 50)) == 50


# ── text message ────────────────────────────────────────────────────────────


def test_text_message_basic_shape() -> None:
    assert msg.text_message("สวัสดีครับ") == {"type": "text", "text": "สวัสดีครับ"}


def test_text_message_clamps_at_5000_characters() -> None:
    message = msg.text_message("ก" * 6000)
    assert len(message["text"]) == msg.MAX_TEXT_LENGTH == 5000


def test_text_message_omits_empty_quick_reply() -> None:
    """ส่ง ``quickReply`` เป็น ``None``/``{}`` ไป LINE จะ error → ต้องไม่ใส่ key เลย"""
    assert "quickReply" not in msg.text_message("x")
    assert "quickReply" not in msg.text_message("x", None)
    assert "quickReply" not in msg.text_message("x", {})

    with_quick = msg.text_message("x", msg.quick_reply([msg.message_action("ก")]))
    assert with_quick["quickReply"]["items"][0]["action"]["label"] == "ก"


# ── action ──────────────────────────────────────────────────────────────────


def test_postback_action_shape_and_label_limit() -> None:
    action = msg.postback_action("ก" * 30, "action=plan")
    assert action["type"] == "postback"
    assert len(action["label"]) == msg.MAX_LABEL_LENGTH == 20
    assert action["data"] == "action=plan"
    assert "displayText" not in action


def test_postback_action_clamps_data_at_300() -> None:
    action = msg.postback_action("ปุ่ม", "action=plan&note=" + "x" * 400)
    assert len(action["data"]) == msg.MAX_POSTBACK_DATA_LENGTH == 300


def test_postback_action_accepts_display_text() -> None:
    action = msg.postback_action("แผนการเรียน", "action=plan", "ขอดูแผนการเรียน")
    assert action["displayText"] == "ขอดูแผนการเรียน"


def test_message_action_defaults_text_to_label() -> None:
    assert msg.message_action("ทุนการศึกษา") == {
        "type": "message",
        "label": "ทุนการศึกษา",
        "text": "ทุนการศึกษา",
    }
    assert msg.message_action("ทุน", "ขอข้อมูลทุน")["text"] == "ขอข้อมูลทุน"


def test_uri_action_never_truncates_url() -> None:
    """
    label ตัดได้ แต่ **URL ตัดไม่ได้** — ตัดแล้วลิงก์เสีย นักศึกษาเปิดเอกสารไม่ได้
    """
    long_url = "https://example.com/" + "a" * 400 + ".pdf"
    action = msg.uri_action("ดาวน์โหลดคำร้องขอเพิ่มรายวิชา", long_url)
    assert len(action["label"]) == msg.MAX_LABEL_LENGTH
    assert action["uri"] == long_url


# ── quick reply / clamp ─────────────────────────────────────────────────────


def test_quick_reply_clamps_to_13_items() -> None:
    quick = msg.quick_reply([msg.message_action(f"ปุ่ม{i}") for i in range(20)])
    assert len(quick["items"]) == msg.MAX_QUICK_REPLY_ITEMS == 13
    assert all(item["type"] == "action" for item in quick["items"])


def test_quick_reply_keeps_first_items_in_order() -> None:
    """ปุ่มสำคัญอยู่ต้นลิสต์ — ยืนยันว่าตัดท้าย ไม่ใช่สลับลำดับ"""
    actions = [msg.message_action(f"ปุ่ม{i}") for i in range(20)]
    labels = [item["action"]["label"] for item in msg.quick_reply(actions)["items"]]
    assert labels == [f"ปุ่ม{i}" for i in range(13)]


def test_quick_reply_accepts_empty_list() -> None:
    assert msg.quick_reply([]) == {"items": []}


def test_clamp_messages_limits_to_five() -> None:
    assert len(msg.clamp_messages([msg.text_message("x")] * 9)) == 5
    assert msg.clamp_messages([]) == []


def test_clamp_messages_does_not_mutate_input() -> None:
    original = [msg.text_message(str(i)) for i in range(9)]
    msg.clamp_messages(original)
    assert len(original) == 9


# ── ข้อความมาตรฐานของระบบ ───────────────────────────────────────────────────


def test_main_menu_actions_respect_all_limits() -> None:
    assert len(msg.MAIN_MENU_ACTIONS) <= msg.MAX_QUICK_REPLY_ITEMS
    for action in msg.MAIN_MENU_ACTIONS:
        assert action["type"] == "postback"
        assert 0 < len(action["label"]) <= msg.MAX_LABEL_LENGTH
        assert action["data"].startswith("action=")


def test_main_menu_actions_have_no_duplicates() -> None:
    """ปุ่มซ้ำ = กดแล้วได้ผลเหมือนกัน เปลืองพื้นที่เมนูที่มีจำกัด"""
    data = [action["data"] for action in msg.MAIN_MENU_ACTIONS]
    assert len(data) == len(set(data))


def test_fallback_message_admits_no_data_and_offers_contact() -> None:
    """
    Requirement ข้อ 14: ไม่มีข้อมูล → บอกตรง ๆ + ให้ช่องทางเจ้าหน้าที่

    ห้ามเดา เพราะถ้าตอบกฎระเบียบ/กำหนดการผิด นักศึกษาเสียหายจริง
    """
    message = msg.fallback_message()
    assert_line_limits([message])
    assert "ไม่พบข้อมูล" in message["text"]
    assert "0-4372-2118" in message["text"]
    assert message["quickReply"]["items"], "ต้องเสนอเมนูให้เลือกต่อ"


def test_no_data_message_names_the_missing_topic() -> None:
    """
    ต่างจาก fallback: อันนี้คือ "รู้ว่าไม่มีข้อมูลนี้ในระบบ"
    เช่นเบอร์โทรอาจารย์ ซึ่งเว็บคณะไม่เผยแพร่ (0/28 คน)
    """
    message = msg.no_data_message("เบอร์โทรอาจารย์")
    assert_line_limits([message])
    assert "เบอร์โทรอาจารย์" in message["text"]


# ── แบบประเมินระบบ (งานวิจัย) ────────────────────────────────────────────────


def test_survey_message_carries_the_full_official_titles() -> None:
    """
    ชื่อแบบประเมินต้องตรงกับใบจริงทุกตัวอักษร เพราะเป็นหลักฐานในเล่มธีสิสว่า
    เก็บข้อมูลจากเครื่องมือใบไหน — ย่อชื่อในแชทแล้วผู้ตอบจะไม่รู้ว่ากรอกใบไหนไป
    """
    message = msg.survey_message()

    assert_line_limits([message])
    assert msg.SURVEY_EXPERT_TITLE in message["text"]
    assert msg.SURVEY_STUDENT_TITLE in message["text"]


def test_survey_urls_have_no_editor_only_query_string() -> None:
    """
    ลิงก์ที่ก๊อปจากหน้าแก้ฟอร์มติด ``?usp=header`` / ``?usp=publish-editor`` มา
    ซึ่งเป็นพารามิเตอร์ของฝั่งเจ้าของฟอร์ม ไม่ใช่ของผู้ตอบ — ต้องเป็น
    ``/viewform`` เปล่า ๆ
    """
    for url in (msg.SURVEY_EXPERT_URL, msg.SURVEY_STUDENT_URL):
        assert url.startswith("https://docs.google.com/forms/d/e/")
        assert url.endswith("/viewform")
        assert "?" not in url


def test_survey_buttons_are_links_not_postbacks() -> None:
    """
    ต้องเป็น ``uri`` action — ``postback`` เปิดหน้าเว็บไม่ได้ ผู้ประเมินจะกดแล้ว
    ไม่เกิดอะไรขึ้น (เหตุผลเดียวกับปุ่ม LIFF บนเมนูต้อนรับ)
    """
    items = msg.survey_message()["quickReply"]["items"]
    first_two = [item["action"] for item in items[:2]]

    assert [action["type"] for action in first_two] == ["uri", "uri"]
    assert [action["label"] for action in first_two] == [
        "สำหรับผู้เชี่ยวชาญ",
        "สำหรับนักศึกษา",
    ]
    for action in first_two:
        assert len(action["label"]) <= msg.MAX_LABEL_LENGTH


def test_survey_message_keeps_a_way_back_to_the_menu() -> None:
    """ปุ่มลิงก์ออกนอกแอปสองปุ่มแล้วจบ = ผู้ใช้ค้างอยู่กับฟอง ต้องมีเมนูต่อท้าย"""
    items = msg.survey_message()["quickReply"]["items"]
    data = [item["action"].get("data") for item in items]

    assert all(action["data"] in data for action in msg.MAIN_MENU_ACTIONS)


def test_main_menu_has_a_survey_entry() -> None:
    """
    แบบประเมินคือเครื่องมือเก็บข้อมูลของธีสิส ถ้าไม่มีปุ่มบนเมนูหลักก็ไม่มี
    ทางเข้าเลย (ต้องส่งลิงก์ให้เป็นราย ๆ ซึ่งทำกับนักศึกษาทั้งชั้นไม่ได้)
    """
    data = [action["data"] for action in msg.MAIN_MENU_ACTIONS]
    assert "action=survey" in data
