"""
เทส Flex builder ทั้ง 5 ฟอง (:mod:`app.line.flex`)

design (23 ส.ค. 2026, ผู้ใช้เป็นเจ้าของแบบ): ฟองเดียว หัวน้ำเงินบอกชื่อหมวด
ตัวฟองเป็นแถวเอกสาร แถวละฉบับ แตะแถวเปิดเอกสารทั้งแถว

31 ส.ค. 2026 ขยายด้วยสไตล์เดิม: ผลค้นเอกสาร · รายชื่ออาจารย์ · ผลค้นอาจารย์ ·
ความก้าวหน้าตามหลักสูตร · วิชาเทอมถัดไป — **ทุกฟองเป็นฟองเดียว ไม่ใช่ carousel**
(ผู้ใช้สั่งไว้) เทสในไฟล์นี้จับสองเรื่อง: รูปทรงที่ LINE ยอมรับ (ผ่าน
``assert_line_limits``) และข้อความเตือนต่าง ๆ ที่ย้ายจากคำตอบแบบข้อความมาเป็น
แถวหมายเหตุ ต้องไม่หายไประหว่างทาง
"""

from __future__ import annotations

from app.line import flex
from app.line import messages as msg

from .helpers import assert_line_limits

# ── ชนิดเอกสาร + ไอคอน ──────────────────────────────────────────────────────


def test_document_kind_reads_the_url_suffix() -> None:
    assert flex.document_kind("https://sci.rmu.ac.th/uploads/add.pdf") == "PDF"
    assert flex.document_kind("https://sci.rmu.ac.th/uploads/a.doc") == "Word (DOC)"
    assert flex.document_kind("https://sci.rmu.ac.th/uploads/a.docx") == "Word (DOCX)"


def test_document_kind_falls_back_to_web_for_pages() -> None:
    assert flex.document_kind("https://coopcenter.rmu.ac.th/page/") == "หน้าเว็บ"
    assert flex.document_kind("https://reg.rmu.ac.th/") == "หน้าเว็บ"


def test_document_kind_ignores_query_string() -> None:
    """URL บางตัวมี ``?file=x.pdf`` — อย่าเอาส่วนหลัง ``?`` มาตัดสิน"""
    assert flex.document_kind("https://x.rmu.ac.th/download?file=g.pdf") == "หน้าเว็บ"
    assert flex.document_kind("https://x.rmu.ac.th/?p=1") == "หน้าเว็บ"


def test_category_icon_covers_every_known_category() -> None:
    """
    หมวดไหนที่รู้ชื่อก็ต้องมีไอคอนเป็นของตัวเอง — ถ้าเผลอลบหมวดออกจาก
    ``CATEGORY_ICONS`` หัวฟองจะใช้ 📄 หมด ซึ่งผู้ใช้แยกหมวดไม่ได้
    """
    assert flex.category_icon("loan") == "🎓"
    assert flex.category_icon("internship") == "💼"
    assert flex.category_icon("calendar") == "📅"
    # หมวดที่ยังไม่มีไอคอนใช้ไอคอนกลาง ไม่ใช่พัง
    assert flex.category_icon("หมวดใหม่") == flex.DEFAULT_CATEGORY_ICON


# ── รูปทรงของฟอง ────────────────────────────────────────────────────────────


def make_row(title: str = "แบบคำขอกู้ยืม", url: str = "https://example.com/a.pdf",
             note: str | None = None) -> dict:
    return {"title": title, "url": url, "doc_type": "pdf", "note": note}


def test_flex_message_is_a_single_bubble_with_rows() -> None:
    """ไม่ใช้การ์ดเลื่อนดูทีละใบแล้ว — ฟองเดียว แถวละฉบับ"""
    message = flex.documents_flex_message(
        "กู้ยืม กยศ.", [make_row(), make_row("ฉบับสอง")], category_key="loan"
    )

    assert message["type"] == "flex"
    assert_line_limits([message])

    bubble = message["contents"]
    assert bubble["type"] == "bubble"
    assert bubble["size"] == "mega"

    rows = [
        content for content in bubble["body"]["contents"]
        if content.get("type") == "box" and content.get("action")
    ]
    assert len(rows) == 2


def test_flex_message_without_quick_reply_has_no_key() -> None:
    """``quickReply`` ว่าง ๆ ส่งไป LINE จะ error → ต้องไม่ใส่ key เลย"""
    message = flex.documents_flex_message("ทุน", [make_row()])
    assert "quickReply" not in message

    with_quick = flex.documents_flex_message(
        "ทุน", [make_row()], msg.quick_reply([msg.message_action("ก")])
    )
    assert with_quick["quickReply"]["items"]


def test_alt_text_names_category_count_and_first_document() -> None:
    """
    altText คือสิ่งที่ขึ้นในรายการแชท/แจ้งเตือน — ต้องพอให้ผู้ใช้ตัดสินใจ
    ก่อนเปิดดู
    """
    rows = [make_row("แบบคำขอกู้ยืมเงิน"), make_row("หนังสือรับรองรายได้")]
    message = flex.documents_flex_message("กู้ยืม กยศ.", rows)

    assert message["altText"] == "เอกสารหมวดกู้ยืม กยศ. 2 ฉบับ · เริ่มจาก แบบคำขอกู้ยืมเงิน"


def test_alt_text_is_capped_at_400() -> None:
    rows = [make_row("ช" * 200)]
    message = flex.documents_flex_message("ข" * 200, rows)

    assert len(message["altText"]) <= flex.MAX_ALT_TEXT_LENGTH


def test_header_shows_icon_category_and_count() -> None:
    bubble = flex.documents_flex_message(
        "กู้ยืม กยศ.", [make_row()], category_key="loan"
    )["contents"]

    header_texts = [c["text"] for c in bubble["header"]["contents"]]
    assert "🎓" in header_texts[0], "หัวฟองต้องมีไอคอนของหมวด"
    assert "กู้ยืม กยศ." in header_texts[0]
    assert "1 ฉบับ" in header_texts[1], "หัวฟองต้องบอกจำนวนฉบับ"


def test_row_carries_title_kind_and_is_tappable_everywhere() -> None:
    row = flex.document_row(
        make_row("101 แบบคำขอกู้ยืมเงิน", "https://sci.rmu.ac.th/add.pdf")
    )

    assert row["type"] == "box"
    # แตะได้ทั้งแถว — ``action`` อยู่บนกล่องแถว ไม่ใช่ปุ่มข้างใน
    assert row["action"]["type"] == "uri"
    assert row["action"]["uri"] == "https://sci.rmu.ac.th/add.pdf"

    body_text = str(row["contents"])
    assert "101 แบบคำขอกู้ยืมเงิน" in body_text
    assert "PDF" in body_text, "ต้องมีป้ายชนิดไฟล์ให้รู้ก่อนเปิดว่าเป็นไฟล์อะไร"


def test_row_has_no_dead_arrow_without_action() -> None:
    """ทุกแถวต้องมี ``action`` — วงปุ่ม › ที่กดไม่ได้ทำให้ผู้ใช้งง"""
    for index in range(3):
        row = flex.document_row(make_row(f"ฉบับ {index}"))
        assert row.get("action"), f"แถวที่ {index} ไม่มี action"


# ── เพดานแถวต่อหนึ่งคำตอบ ───────────────────────────────────────────────────


def test_rows_over_the_limit_are_announced_not_dropped_silently() -> None:
    """
    เกินเพดานแถวต่อหนึ่งคำตอบ → แสดงเท่าที่ได้ แล้วมีบรรทัดบอกจำนวนทั้งหมด
    ชี้ให้พิมพ์คำค้น — ไม่ตัดชื่อทิ้งเงียบ ๆ
    """
    rows = [make_row(f"ฉบับ {index}") for index in range(flex.MAX_ROWS + 4)]
    message = flex.documents_flex_message("กู้ยืม กยศ.", rows)

    contents = message["contents"]["body"]["contents"]
    action_rows = [c for c in contents if c.get("action")]
    assert len(action_rows) == flex.MAX_ROWS

    notice = contents[-1]
    assert notice["type"] == "text"
    assert f"แสดง {flex.MAX_ROWS} จาก {flex.MAX_ROWS + 4} รายการ" in notice["text"]
    # altText ต้องนับครบทุกฉบับ ไม่ใช่นับแค่ที่ได้แถว
    assert f"{flex.MAX_ROWS + 4} ฉบับ" in message["altText"]


# ── ปุ่มเปิดเอกสาร ──────────────────────────────────────────────────────────


def test_uri_action_never_truncates_a_real_url() -> None:
    """URL ตัดแล้วเปิดไม่ได้ — ``uri`` ต้องครบ (ไม่เกินเพดาน)"""
    url = "https://sci.rmu.ac.th/" + "a" * 300 + ".pdf"
    action = flex.uri_action("เปิดเอกสารชื่อที่ยาวมากเป็นพิเศษ", url)

    assert action["uri"] == url
    assert len(action["label"]) <= msg.MAX_LABEL_LENGTH


def test_uri_action_percent_encodes_thai_file_names() -> None:
    """
    **บั๊กที่เจอกับข้อมูลจริง**: ลิงก์เอกสารของเว็บคณะมีภาษาไทยในชื่อไฟล์
    (``101-แบบคำขอกู้ยืมเงิน.pdf``) ในข้อความธรรมดาไม่เป็นไร แต่ ``action``
    ของ Flex ถูก LINE ตรวจฝั่งเซิร์ฟเวอร์แล้วปฏิเสธ 400 ``Invalid action URI``
    ทั้งข้อความ — ต้อง percent-encode ก่อนส่ง

    ตรวจเทียบกับค่าจริงของไฟล์นี้ (ยืนยันกับ ``urllib.parse.quote`` แล้ว)
    ไม่ใช่ค่าที่เดาขึ้นเอง
    """
    thai_url = (
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/"
        "101-แบบคำขอกู้ยืมเงิน.pdf"
    )
    action = flex.uri_action("เปิด", thai_url)

    assert action["uri"] == (
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/"
        "101-%E0%B9%81%E0%B8%9A%E0%B8%9A%E0%B8%84%E0%B8%B3%E0%B8%82%E0%B8%AD"
        "%E0%B8%81%E0%B8%B9%E0%B9%89%E0%B8%A2%E0%B8%B7%E0%B8%A1%E0%B9%80%E0%B8%87%E0%B8%B4%E0%B8%99.pdf"
    )
    # encode แล้วต้องเป็น ASCII ล้วน จึงจะปลอดภัยกับทุกฝั่ง
    assert action["uri"].isascii()


def test_uri_action_leaves_ascii_urls_untouched() -> None:
    assert flex.uri_action("เปิด", "https://example.com/a.pdf")["uri"] == (
        "https://example.com/a.pdf"
    )


def test_uri_action_does_not_double_encode_existing_percent_sequences() -> None:
    """URL ที่ encode มาแล้วจากต้นทาง ต้องไม่กลายเป็น ``%25E0...``"""
    assert flex.uri_action("เปิด", "https://example.com/a%E0%B8%81.pdf")["uri"] == (
        "https://example.com/a%E0%B8%81.pdf"
    )


def test_uri_action_respects_the_1000_character_cap_after_encoding() -> None:
    """เกิน 1,000 ตัวอักษร LINE จะ reject ทั้ง request → ตัดไว้ก่อน"""
    url = "https://sci.rmu.ac.th/" + "ก" * 2000 + ".pdf"
    action = flex.uri_action("เปิด", url)
    assert len(action["uri"]) <= flex.MAX_URI_LENGTH


# ── ฟอง 2: ผลค้นเอกสาร ──────────────────────────────────────────────────────


def search_doc_row(title: str = "101 แบบคำขอกู้ยืมเงิน", category: str = "กู้ยืม กยศ.") -> dict:
    return {
        "title": title,
        "url": "https://sci.rmu.ac.th/uploads/101.pdf",
        "doc_type": "pdf",
        "note": None,
        "category_label": category,
    }


def test_search_row_tells_both_file_kind_and_category() -> None:
    """
    ผลค้นคาบหลายหมวด — ถ้าไม่บอกหมวด ผู้ใช้เห็นชื่อคล้าย ๆ กันแล้วแยกไม่ออก
    ว่าฉบับไหนของหมวดไหน
    """
    message = flex.document_search_flex_message("กยศ", [search_doc_row()])
    body = str(message["contents"]["body"]["contents"])

    assert "PDF · กู้ยืม กยศ." in body


def test_search_row_without_category_has_no_dangling_separator() -> None:
    row = search_doc_row(category="")
    assert flex._search_row_subtitle(row) == "PDF"


def test_search_alt_text_names_keyword_count_and_first_hit() -> None:
    message = flex.document_search_flex_message(
        "กยศ", [search_doc_row(), search_doc_row("108 แบบรายงานสถานภาพ")]
    )

    assert message["altText"] == (
        "ผลค้น “กยศ” เอกสาร 2 ฉบับ · เริ่มจาก 101 แบบคำขอกู้ยืมเงิน"
    )


def test_search_bubble_rows_are_tappable_and_within_limits() -> None:
    message = flex.document_search_flex_message("กยศ", [search_doc_row()])

    assert_line_limits([message])
    rows = [c for c in message["contents"]["body"]["contents"] if c.get("action")]
    assert len(rows) == 1
    assert rows[0]["action"]["type"] == "uri"


# ── ฟอง 3: รายชื่ออาจารย์ ────────────────────────────────────────────────────


def instructor(name: str = "ผศ.ดร.สมชาย ใจดี", **overrides) -> dict:
    row = {
        "name": name,
        "position": "ประธานหลักสูตร",
        "email": "somchai@rmu.ac.th",
        "room": "SC-301",
        "office_hours": "จ-ศ 13:00-16:00",
    }
    row.update(overrides)
    return row


def test_instructor_row_keeps_every_detail_line() -> None:
    row = flex.instructor_row(1, instructor())
    body = str(row["contents"])

    assert "ผศ.ดร.สมชาย ใจดี" in body
    assert "ประธานหลักสูตร" in body
    assert "somchai@rmu.ac.th" in body
    assert "SC-301" in body
    assert "จ-ศ 13:00-16:00" in body


def test_instructor_row_says_missing_email_out_loud() -> None:
    """
    เว้นบรรทัดอีเมลว่างไว้ ผู้ใช้จะคิดว่าระบบโหลดไม่ครบแล้วถามซ้ำ —
    คำตอบแบบข้อความเดิมเขียนตรง ๆ ฟอง Flex ก็ต้องเขียนตรง ๆ เหมือนกัน
    """
    body = str(flex.instructor_row(2, instructor(email=None))["contents"])

    assert "อีเมล: ไม่มีข้อมูลในระบบ" in body


def test_instructor_row_is_deliberately_not_tappable() -> None:
    """
    ``mailto:`` ไม่อยู่ใน scheme ที่ ``uri`` action ของ LINE รับ (http/https/
    tel/line) — ใส่ไปเสี่ยงถูกปฏิเสธ 400 ทั้งข้อความ จึงตั้งใจไม่ให้แถวกดได้
    เทสนี้กันคนมาเติม action ทีหลังโดยไม่รู้เรื่องนี้
    """
    assert "action" not in flex.instructor_row(1, instructor())


def test_instructors_bubble_numbers_rows_and_names_the_group() -> None:
    message = flex.instructors_flex_message(
        "สาขาวิชาทดสอบ", [instructor(), instructor("อ.สมหญิง เก่งมาก")]
    )

    assert_line_limits([message])
    header = str(message["contents"]["header"]["contents"])
    assert "อาจารย์กลุ่มสาขาวิชาทดสอบ" in header
    assert "2 คน" in header
    body = str(message["contents"]["body"]["contents"])
    numbers = [c["contents"][0]["text"] for c in message["contents"]["body"]["contents"]]
    assert numbers == ["1", "2"], "แถวอาจารย์ต้องมีเลขลำดับเหมือนคำตอบแบบข้อความเดิม"
    assert message["altText"].startswith("อาจารย์กลุ่มสาขาวิชาทดสอบ 2 คน")


def test_instructor_notes_are_kept_as_rows() -> None:
    message = flex.instructors_flex_message(
        "สาขาวิชาทดสอบ", [instructor()], notes=["ข้อมูลอัปเดตล่าสุด ส.ค. 2568"]
    )

    assert "ข้อมูลอัปเดตล่าสุด ส.ค. 2568" in str(message["contents"]["body"])


def test_instructor_search_header_shows_the_keyword() -> None:
    message = flex.instructor_search_flex_message("ธรัช", [instructor("ผศ.ดร.ธรัช อารีราษฎร์")])

    assert_line_limits([message])
    assert "ธรัช" in str(message["contents"]["header"]["contents"])
    assert message["altText"] == (
        "ผลค้น “ธรัช” อาจารย์ 1 คน · เริ่มจาก ผศ.ดร.ธรัช อารีราษฎร์"
    )


# ── ฟอง 4-5: ความก้าวหน้า / วิชาเทอมถัดไป ───────────────────────────────────


def course(code: str = "2000001", name: str = "การเขียนโปรแกรม") -> dict:
    return {
        "code": code,
        "name": name,
        "credits": 3,
        "term": "ปี 2 เทอม 1",
        "note": None,
        "action": msg.postback_action("ดูวิชา", f"action=course&code={code}"),
    }


def bar_width(bar: dict) -> str | None:
    return bar["contents"][0].get("width")


def test_progress_bar_fills_the_given_percent() -> None:
    assert bar_width(flex.progress_bar(45)) == "45%"


def test_progress_bar_clamps_out_of_range_values() -> None:
    """
    ``width`` ของ box รับเป็นเปอร์เซ็นต์ — ค่าลบหรือเกิน 100 ทำให้ LINE
    ปฏิเสธทั้งข้อความ ไม่ใช่แค่วาดเพี้ยน
    """
    assert bar_width(flex.progress_bar(140)) == "100%"
    assert bar_width(flex.progress_bar(-20)) is None, "0% ต้องไม่มีแท่งเลย"


def test_progress_bar_at_zero_has_only_the_track() -> None:
    bar = flex.progress_bar(0)
    assert bar["contents"] == [{"type": "filler"}]


def test_course_row_shows_credits_as_a_badge_and_stays_tappable() -> None:
    row = flex.course_row(course())

    assert row["action"]["type"] == "postback"
    assert row["action"]["data"] == "action=course&code=2000001"
    body = str(row["contents"])
    assert "การเขียนโปรแกรม" in body
    assert "2000001 · ปี 2 เทอม 1" in body
    assert "3 นก." in body


def test_course_row_without_action_is_still_valid() -> None:
    """วิชาที่ยังไม่มีข้อมูลให้กดดู ต้องไม่ทำให้ทั้งฟองพัง"""
    row = flex.course_row({"code": "9999999", "name": "", "credits": 0})

    assert "action" not in row
    assert "(ยังไม่มีชื่อวิชาในคลังข้อมูล)" in str(row["contents"])


def test_progress_bubble_leads_with_the_percentage_and_the_bar() -> None:
    message = flex.progress_flex_message(
        program_code="ITEC",
        percent=50,
        passed_courses=1,
        plan_courses=2,
        passed_credits=3,
        remaining_headline="เหลืออีก 1 วิชา",
        stats=["หลักสูตรกำหนด 120 หน่วยกิต"],
        course_rows=[course()],
        notes=["ยังไม่มีข้อมูลวิชาบังคับก่อนในระบบ"],
    )

    assert_line_limits([message])
    summary = message["contents"]["body"]["contents"][0]["contents"]
    assert summary[0]["text"] == "50%"
    assert summary[1]["backgroundColor"] == flex.FLEX_COLOR_TRACK, "ชิ้นถัดมาคือแถบ"
    assert summary[2]["text"] == "ผ่านแล้ว 1/2 วิชา · 3 หน่วยกิต"
    assert summary[3]["text"] == "หลักสูตรกำหนด 120 หน่วยกิต"

    body = str(message["contents"]["body"]["contents"])
    assert "เหลืออีก 1 วิชา" in body
    assert "2000001" in body
    assert "ยังไม่มีข้อมูลวิชาบังคับก่อนในระบบ" in body


def test_progress_alt_text_carries_the_numbers() -> None:
    message = flex.progress_flex_message(
        program_code="ITEC",
        percent=50,
        passed_courses=1,
        plan_courses=2,
        passed_credits=3,
        remaining_headline="เหลืออีก 1 วิชา",
        course_rows=[course()],
    )

    assert message["altText"] == (
        "ความก้าวหน้า ITEC ผ่านแล้ว 1/2 วิชา (50%) · เหลืออีก 1 วิชา"
    )


def test_next_term_header_states_the_credit_cap_used() -> None:
    """
    เพดานหน่วยกิตคือค่าที่ตั้งไว้ใน config ไม่ใช่ข้อบังคับที่ยืนยันแล้ว —
    ต้องเขียนบนหน้าจอว่า "เพดานที่ใช้คิด" เพื่อไม่ให้ผู้ใช้เข้าใจว่าเป็นกฎ
    """
    message = flex.next_term_flex_message(
        semester=1,
        course_count=1,
        credits=3,
        max_credits=22,
        course_rows=[course()],
        notes=["วิชานี้ไม่เปิดเทอมนี้ตามข้อมูลที่มี"],
    )

    assert_line_limits([message])
    header = str(message["contents"]["header"]["contents"])
    assert "ภาคเรียนที่ 1" in header
    assert "1 วิชา 3 หน่วยกิต · เพดานที่ใช้คิด 22" in header
    assert "วิชานี้ไม่เปิดเทอมนี้ตามข้อมูลที่มี" in str(message["contents"]["body"])
    assert message["altText"] == "วิชาแนะนำภาคเรียนที่ 1 1 วิชา 3 หน่วยกิต"


def test_course_rows_over_the_limit_are_announced() -> None:
    rows = [course(f"200000{index}") for index in range(flex.MAX_ROWS + 2)]
    message = flex.next_term_flex_message(
        semester=1, course_count=len(rows), credits=99, max_credits=22, course_rows=rows
    )

    contents = message["contents"]["body"]["contents"]
    assert len([c for c in contents if c.get("action")]) == flex.MAX_ROWS
    assert f"แสดง {flex.MAX_ROWS} จาก {flex.MAX_ROWS + 2} รายการ" in contents[-1]["text"]
