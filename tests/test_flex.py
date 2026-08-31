"""
เทส Flex builder — รายการเอกสาร (:mod:`app.line.flex`)

design (23 ส.ค. 2026, ผู้ใช้เป็นเจ้าของแบบ): ฟองเดียว หัวน้ำเงินบอกชื่อหมวด
ตัวฟองเป็นแถวเอกสาร แถวละฉบับ แตะแถวเปิดเอกสารทั้งแถว
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
