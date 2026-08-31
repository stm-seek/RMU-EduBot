"""
สร้าง Flex Message — รายการต่าง ๆ ใน **ฟองเดียว** (แถวเรียงลง)

ออกแบบตามแบบที่ผู้ใช้เลือกเอง (23 ส.ค. 2026): หัวฟองน้ำเงินบอกชื่อหมวด
ตัวฟองเป็นแถวเอกสาร แถวละฉบับ (ไอคอน · ชื่อ · ชนิดไฟล์ · ปุ่ม ›)
แตะแถวไหนเปิดเอกสารนั้นทั้งแถว — ไม่ต้องเลื่อนดูทีละการ์ด

ตอนนี้ใช้แบบเดียวกันกับห้าเรื่อง (31 ส.ค. 2026) — เอกสารในหมวด, ผลค้นเอกสาร,
รายชื่ออาจารย์, ผลค้นอาจารย์, ความก้าวหน้า/วิชาเทอมถัดไป

**ทุกอย่างเป็นฟองเดียว ไม่ใช้ carousel** (ผู้ใช้สั่งไว้): ฟองเดียวอ่านจบใน
หน้าจอเดียว ไม่ต้องปัดข้าง และไม่ต้องกังวลเพดานจำนวนฟองของ LINE

ไฟล์นี้**รู้จักแค่การจัดหน้า** ไม่รู้จัก DB หรือ router — ``action`` ของแถว
ผู้เรียกส่งเข้ามาเอง (คีย์ ``action`` ในแต่ละ row) เพื่อไม่ให้ layer นี้
ต้องรู้รูปแบบ postback ของ router

ข้อจำกัดที่ยืนยันจากเอกสาร LINE:

* ``altText`` **ต้องมีเสมอ** — เป็นข้อความที่ขึ้นในรายการแชทและแจ้งเตือน
  (ถ้าไม่ส่ง ผู้ใช้จะเห็นเป็นช่องว่างก่อนเปิดดู)
* ``uri`` ของปุ่มยาวสุด **1,000 ตัวอักษร**
* ``action`` ตั้งบน ``box`` ได้ → แตะได้ทั้งแถว (ไม่ต้องมีปุ่มแยก)
"""

from __future__ import annotations

from urllib.parse import quote

# ── ข้อจำกัดของ Flex Message ────────────────────────────────────────────────

MAX_ALT_TEXT_LENGTH = 400
# แถวเอกสารต่อหนึ่งคำตอบ — 30 เผื่อโตได้อีกมาก (ตอนนี้หมวดใหญ่สุด
# ``loan`` มี 12 แถว) ถ้าวันไหนโตเกินนี้ ค่อยเพิ่มการแบ่งหน้า
MAX_ROWS = 30
MAX_URI_LENGTH = 1000

# ── ธีมสี (ตาม design ที่ผู้ใช้เลือกเอง 23 ส.ค. 2026) ────────────────────────

FLEX_COLOR_BRAND = "#2055A0"      # น้ำเงิน — หัวฟอง + วงปุ่ม ›
FLEX_COLOR_HEADER_SUB = "#DCE9FF"  # ฟ้าอ่อน — บรรทัดรองในหัวฟอง
FLEX_COLOR_ROW_BG = "#F4F7FC"      # พื้นแถวเอกสาร
FLEX_COLOR_INK = "#12345B"         # น้ำเงินเข้ม — ชื่อเอกสาร
FLEX_COLOR_STEEL = "#667085"       # เทาเหล็ก — คำอธิบาย + เท้าฟอง
FLEX_COLOR_FOOTER_BG = "#F8FAFC"   # พื้นเท้าฟอง
FLEX_COLOR_TRACK = "#DCE4F2"       # รางของแถบความก้าวหน้า (ส่วนที่ยังไม่ผ่าน)
FLEX_COLOR_WHITE = "#FFFFFF"

# ── ไอคอน (ตัวอักษรเดียว ไม่เอาจากข้างนอก — ใช้ซ้ำได้ทั้งเครื่อง) ─────────────

# ไอคอนหัวฟองแยกตามหมวด — หมวดที่ไม่อยู่ในนี้ใช้ไอคอนกลาง
# (เพิ่มหมวดใหม่อย่าลืมเพิ่มตรงนี้ด้วย ไม่งั้นหัวฟองจะใช้ 📄 ทั้งหมด)
CATEGORY_ICONS: dict[str, str] = {
    "loan": "🎓",
    "scholarship": "💰",
    "registration": "📝",
    "internship": "💼",
    "calendar": "📅",
    "curriculum": "📚",
    "regulation": "📜",
    "exam_prep": "✏️",
    "activity": "🎉",
    "it_account": "💻",
    "staff": "👥",
}
DEFAULT_CATEGORY_ICON = "📄"

# ชนิดเอกสาร — ป้ายใต้ชื่อแถว ดูจากนามสกุลใน ``url`` ไม่ใช่ ``doc_type``
# ของคลัง (คลังเก็บชนิดที่ตรวจเจอตอน scrape แต่ผู้ใช้จะกดเปิดของจริง)
_DOCUMENT_TYPE_LABELS: dict[str, str] = {
    ".pdf": "PDF",
    ".doc": "Word (DOC)",
    ".docx": "Word (DOCX)",
}


def document_kind(url: str) -> str:
    """
    ชนิดของเอกสารสำหรับป้ายใต้ชื่อแถว

    >>> document_kind('https://sci.rmu.ac.th/upload/add.pdf')
    'PDF'
    >>> document_kind('https://coopcenter.rmu.ac.th/page/')
    'หน้าเว็บ'
    """
    lowered = url.lower().split("?", 1)[0]
    for suffix, label in _DOCUMENT_TYPE_LABELS.items():
        if lowered.endswith(suffix):
            return label
    return "หน้าเว็บ"


def category_icon(category_key: str) -> str:
    """
    ไอคอนหัวฟองของหมวด

    >>> category_icon('loan')
    '🎓'
    >>> category_icon('หมวดที่ยังไม่มีไอคอน')
    '📄'
    """
    return CATEGORY_ICONS.get(category_key, DEFAULT_CATEGORY_ICON)


def documents_flex_message(
    category_label: str,
    rows: list[dict],
    quick_reply: dict | None = None,
    *,
    category_key: str = "",
) -> dict:
    """
    flex message รายการเอกสาร 1 หมวด — ฟองเดียว แถวละ 1 ฉบับ

    ``rows`` คือแถวจาก ``repository.documents_in_category``
    (``title`` / ``url`` / ``note``) — เกิน :data:`MAX_ROWS` จะแสดงเท่าที่
    ได้แล้วมีบรรทัดบอกจำนวนทั้งหมด (``citations`` ยังเก็บครบทุกฉบับ)
    """
    shown, total = rows[:MAX_ROWS], len(rows)

    body_contents: list[dict] = [document_row(row) for row in shown]
    if total > len(shown):
        body_contents.append(_hidden_notice(len(shown), total))

    message: dict = {
        "type": "flex",
        "altText": _alt_text(category_label, rows),
        "contents": {
            "type": "bubble",
            "size": "mega",
            "header": _header(category_label, total, category_key),
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "14px",
                "spacing": "sm",
                "contents": body_contents,
            },
            "footer": _footer(),
        },
    }
    if quick_reply:
        message["quickReply"] = quick_reply
    return message


def _alt_text(category_label: str, rows: list[dict]) -> str:
    """
    ข้อความที่ขึ้นในรายการแชท/แจ้งเตือนแทนการ์ด — ต้องสื่อว่าในนี้มีอะไร

    ชื่อเอกสารแรกสำคัญที่สุด เพราะผู้ใช้ต้องตัดสินใจก่อนว่าอยากเปิดดูไหม
    """
    parts = [f"เอกสารหมวด{category_label} {len(rows)} ฉบับ"]
    if rows:
        parts.append(f"เริ่มจาก {rows[0]['title']}")
    return truncate(" · ".join(parts), MAX_ALT_TEXT_LENGTH)


def _header(category_label: str, total: int, category_key: str) -> dict:
    return bubble_header(
        category_icon(category_key),
        category_label,
        f"{total} ฉบับ · เลือกเอกสารที่ต้องการ",
    )


def bubble_header(icon: str, title: str, subtitle: str) -> dict:
    """
    หัวฟองน้ำเงิน — ไอคอน+ชื่อเรื่องบรรทัดแรก คำอธิบายสั้นบรรทัดที่สอง

    แยกออกมาเพื่อให้ฟองทุกชนิด (เอกสาร/อาจารย์/ความก้าวหน้า) ใช้หัวเดียวกัน
    ไม่ใช่ต่างคนต่างจัด แล้วสีกับระยะเพี้ยนกันทีละฟอง
    """
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": FLEX_COLOR_BRAND,
        "paddingAll": "18px",
        "contents": [
            {
                "type": "text",
                "text": f"{icon}  {title}" if icon else title,
                "color": FLEX_COLOR_WHITE,
                "weight": "bold",
                "size": "xl",
                "wrap": True,
            },
            {
                "type": "text",
                "text": subtitle,
                "color": FLEX_COLOR_HEADER_SUB,
                "size": "sm",
                "margin": "4px",
                "wrap": True,
            },
        ],
    }


def document_row(row: dict, *, subtitle: str = "") -> dict:
    """
    แถวเอกสาร 1 แถว: ไอคอน · ชื่อ + ชนิดไฟล์ · วงปุ่ม ›

    ``action`` ตั้งบนกล่องแถวเลย → แตะตรงไหนของแถวก็เปิดเอกสาร
    ปุ่ม › ด้านขวาเป็นแค่สัญญาณว่าแถวนี้กดได้

    ``subtitle`` เขียนทับบรรทัดล่าง (ปกติเป็นชนิดไฟล์) — ผลค้นหาใช้ช่องนี้
    บอกหมวดด้วย เพราะผลค้นคาบหลายหมวด ต่างจากรายการในหมวดเดียว
    """
    return {
        "type": "box",
        "layout": "horizontal",
        "backgroundColor": FLEX_COLOR_ROW_BG,
        "cornerRadius": "10px",
        "paddingAll": "13px",
        "action": uri_action("เปิดเอกสาร", row["url"]),
        "contents": [
            {
                "type": "text",
                "text": DEFAULT_CATEGORY_ICON,
                "size": "lg",
                "flex": 0,
            },
            {
                "type": "box",
                "layout": "vertical",
                "flex": 1,
                "margin": "10px",
                "contents": [
                    {
                        "type": "text",
                        "text": row["title"],
                        "color": FLEX_COLOR_INK,
                        "weight": "bold",
                        "size": "md",
                        "wrap": True,
                    },
                    {
                        "type": "text",
                        "text": subtitle or document_kind(row["url"]),
                        "color": FLEX_COLOR_STEEL,
                        "size": "xs",
                        "margin": "3px",
                    },
                ],
            },
            {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": FLEX_COLOR_BRAND,
                "cornerRadius": "18px",
                "width": "42px",
                "height": "32px",
                "justifyContent": "center",
                "alignItems": "center",
                "flex": 0,
                "contents": [
                    {
                        "type": "text",
                        "text": "›",
                        "color": FLEX_COLOR_WHITE,
                        "size": "xl",
                        "weight": "bold",
                    }
                ],
            },
        ],
    }


def _hidden_notice(shown_count: int, total: int) -> dict:
    """บรรทัดบอกว่ามีเอกสารมากกว่าที่แสดง (เกินเพดานแถวต่อหนึ่งคำตอบ)"""
    return {
        "type": "text",
        "text": f"(แสดง {shown_count} จาก {total} รายการ — พิมพ์คำค้นเพื่อหาฉบับที่เหลือได้)",
        "color": FLEX_COLOR_STEEL,
        "size": "xs",
        "wrap": True,
        "margin": "8px",
    }


def _footer() -> dict:
    return bubble_footer("💡 แตะที่รายการเพื่อเปิดเอกสาร")


def bubble_footer(text: str) -> dict:
    """เท้าฟอง — คำใบ้หนึ่งบรรทัดว่าทำอะไรกับฟองนี้ได้"""
    return {
        "type": "box",
        "layout": "horizontal",
        "backgroundColor": FLEX_COLOR_FOOTER_BG,
        "paddingAll": "12px",
        "contents": [
            {
                "type": "text",
                "text": text,
                "color": FLEX_COLOR_STEEL,
                "size": "xs",
                "align": "center",
                "wrap": True,
                "flex": 1,
            }
        ],
    }


def truncate(text: str, limit: int) -> str:
    """
    ตัดข้อความให้พอดีขีด โดยเติม ``…`` ถ้าถูกตัด

    >>> truncate('แบบคำขอกู้ยืม', 20)
    'แบบคำขอกู้ยืม'
    >>> truncate('abcdefghij', 5)
    'abcd…'
    """
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


# ตัวอักษรที่ปล่อยผ่านได้ตาม RFC 3986 (reserved + unreserved) บวก ``%``
# เพื่อกัน encode ซ้ำใน URL ที่มี ``%xx`` อยู่แล้ว
_URI_SAFE_CHARS = ":/?#[]@!$&'()*+,;=%-._~"


def _encode_uri(uri: str) -> str:
    """
    ทำให้ ``uri`` เป็น URI ที่ถูกกฎหมายก่อนส่งให้ LINE

    **บั๊กที่เจอกับข้อมูลจริง**: ลิงก์เอกสารของเว็บคณะมีภาษาไทยในชื่อไฟล์
    (เช่น ``101-แบบคำขอกู้ยืมเงิน.pdf``) — พออยู่ในข้อความธรรมดาไม่เป็นไร
    แต่ใน ``action`` ของ Flex, LINE ตรวจฝั่งเซิร์ฟเวอร์แล้วปฏิเสธ 400
    ``Invalid action URI`` ทั้งข้อความ

    >>> _encode_uri('https://sci.rmu.ac.th/a-ขอกู้ยืม.pdf')
    'https://sci.rmu.ac.th/a-%E0%B8%82%E0%B8%AD%E0%B8%81%E0%B8%B9%E0%B9%89%E0%B8%A2%E0%B8%B7%E0%B8%A1.pdf'
    >>> _encode_uri('https://example.com/a.pdf')
    'https://example.com/a.pdf'
    >>> # ``%`` อยู่ใน safe — ไม่ encode ซ้ำ URL ที่มี ``%xx`` อยู่แล้ว
    >>> _encode_uri('https://example.com/a%E0%B8%81.pdf')
    'https://example.com/a%E0%B8%81.pdf'
    """
    return quote(uri, safe=_URI_SAFE_CHARS)


def uri_action(label: str, uri: str) -> dict:
    """ปุ่มเปิดลิงก์ของแถว — ``uri`` ยาวได้ 1,000 ตัวอักษร"""
    # ตัดทีหลังสุด: ``…`` ที่ ``truncate`` เติมถูก encode เป็น ``%E2%80%A6``
    # (8 ตัวอักษร) ถ้าตัดก่อนแล้วค่อย encode ผลลัพธ์อาจทะลุเพดานอีกครั้ง
    encoded = truncate(_encode_uri(uri), MAX_URI_LENGTH)
    return {
        "type": "uri",
        "label": truncate(label, 20),
        "uri": encoded,
    }


# ── ชิ้นส่วนแถวที่ฟองชนิดใหม่ใช้ร่วมกัน ────────────────────────────────────────
#
# แถวของทุกฟองหน้าตาเหมือนแถวเอกสาร (พื้นอ่อน มุมโค้ง) ต่างกันแค่ข้างใน
# เขียนเป็นชิ้นเล็กแล้วประกอบ ดีกว่าก๊อป dict ยาว ๆ ไปทีละฟอง


def _row_shell(contents: list[dict], action: dict | None = None) -> dict:
    """กล่องแถว — พื้นอ่อน มุมโค้ง กดได้ทั้งแถวถ้ามี ``action``"""
    row: dict = {
        "type": "box",
        "layout": "horizontal",
        "backgroundColor": FLEX_COLOR_ROW_BG,
        "cornerRadius": "10px",
        "paddingAll": "13px",
        "contents": contents,
    }
    if action:
        row["action"] = action
    return row


def _row_number(index: int) -> dict:
    """เลขลำดับหน้าแถว — แทนที่ ``1.`` ``2.`` ของคำตอบแบบข้อความเดิม"""
    return {
        "type": "text",
        "text": str(index),
        "color": FLEX_COLOR_BRAND,
        "weight": "bold",
        "size": "sm",
        "flex": 0,
        "align": "center",
    }


def _row_title(text: str) -> dict:
    return {
        "type": "text",
        "text": text,
        "color": FLEX_COLOR_INK,
        "weight": "bold",
        "size": "md",
        "wrap": True,
    }


def _row_detail(text: str) -> dict:
    """บรรทัดรายละเอียดใต้ชื่อแถว (อีเมล/ห้อง/หน่วยกิต ฯลฯ)"""
    return {
        "type": "text",
        "text": text,
        "color": FLEX_COLOR_STEEL,
        "size": "xs",
        "wrap": True,
        "margin": "3px",
    }


def _badge(text: str) -> dict:
    """ป้ายมุมขวาของแถว — ใช้บอกหน่วยกิต (ไม่ใช่ปุ่ม ไม่กดได้)"""
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": FLEX_COLOR_BRAND,
        "cornerRadius": "14px",
        "paddingAll": "6px",
        "width": "56px",
        "justifyContent": "center",
        "alignItems": "center",
        "flex": 0,
        "contents": [
            {
                "type": "text",
                "text": text,
                "color": FLEX_COLOR_WHITE,
                "size": "xs",
                "weight": "bold",
                "align": "center",
            }
        ],
    }


def _note(text: str) -> dict:
    """
    บรรทัดหมายเหตุท้ายตัวฟอง — คำเตือนที่ **ห้ามหาย** ตอนย้ายมาเป็น Flex

    เช่น "ยังไม่มีข้อมูลวิชาบังคับก่อน" หรือ "เว็บคณะไม่เผยแพร่เบอร์โทร"
    ถ้าตัดออกเพราะอยากให้การ์ดสวย นักศึกษาจะเข้าใจผิดว่าข้อมูลครบแล้ว
    """
    return {
        "type": "text",
        "text": text,
        "color": FLEX_COLOR_STEEL,
        "size": "xs",
        "wrap": True,
        "margin": "10px",
    }


def _bubble(
    *,
    alt_text: str,
    header: dict,
    body_contents: list[dict],
    footer_text: str,
    quick_reply: dict | None = None,
) -> dict:
    """ประกอบฟองมาตรฐาน — หัวน้ำเงิน · ตัวเป็นแถว · เท้าเป็นคำใบ้หนึ่งบรรทัด"""
    message: dict = {
        "type": "flex",
        "altText": truncate(alt_text, MAX_ALT_TEXT_LENGTH),
        "contents": {
            "type": "bubble",
            "size": "mega",
            "header": header,
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "14px",
                "spacing": "sm",
                "contents": body_contents,
            },
            "footer": bubble_footer(footer_text),
        },
    }
    if quick_reply:
        message["quickReply"] = quick_reply
    return message


def _rows_and_notes(
    rows: list[dict], total: int, notes: tuple[str, ...] | list[str] = ()
) -> list[dict]:
    """แถวที่แสดง + บรรทัดบอกจำนวนที่ถูกตัด + หมายเหตุ (ตัดว่างออกให้)"""
    contents = list(rows)
    if total > len(rows):
        contents.append(_hidden_notice(len(rows), total))
    contents.extend(_note(text) for text in notes if text)
    return contents


# ── ฟอง 2: ผลค้นหาเอกสาร ────────────────────────────────────────────────────


def document_search_flex_message(
    keyword: str, rows: list[dict], quick_reply: dict | None = None
) -> dict:
    """
    ผลค้นเอกสาร — ข้อมูลชนิดเดียวกับรายการในหมวด จึงใช้ :func:`document_row` ซ้ำ

    ต่างกันที่บรรทัดล่างของแถว: ผลค้นคาบหลายหมวด จึงบอกหมวดต่อท้ายชนิดไฟล์
    (ผู้เรียกใส่ชื่อหมวดไทยมาในคีย์ ``category_label`` — ไฟล์นี้ไม่รู้จักแมป
    ชื่อหมวด นั่นเป็นเรื่องของ router)
    """
    shown, total = rows[:MAX_ROWS], len(rows)
    body = [document_row(row, subtitle=_search_row_subtitle(row)) for row in shown]

    return _bubble(
        alt_text=_search_alt_text(keyword, f"เอกสาร {total} ฉบับ", rows, "title"),
        header=bubble_header(
            "🔎",
            f"ผลค้น “{truncate(keyword, 30)}”",
            f"เจอเอกสาร {total} ฉบับ",
        ),
        body_contents=_rows_and_notes(body, total),
        footer_text="💡 แตะที่รายการเพื่อเปิดเอกสาร · ปุ่มล่างดูทั้งหมดในหมวดนั้น",
        quick_reply=quick_reply,
    )


def _search_row_subtitle(row: dict) -> str:
    """ชนิดไฟล์ · หมวด — ข้ามส่วนที่ไม่มีข้อมูล ไม่เว้น ` · ` ค้างไว้"""
    parts = [document_kind(row["url"]), row.get("category_label") or ""]
    return " · ".join(part for part in parts if part)


def _search_alt_text(keyword: str, found: str, rows: list[dict], key: str) -> str:
    """altText ของผลค้น — บอกคำค้น จำนวนที่เจอ และรายการแรก"""
    parts = [f"ผลค้น “{keyword}” {found}"]
    if rows:
        parts.append(f"เริ่มจาก {rows[0].get(key) or ''}".strip())
    return " · ".join(parts)


# ── ฟอง 3: รายชื่ออาจารย์ (ทั้งกลุ่ม / ผลค้น) ────────────────────────────────
#
# **ไม่มี action บนแถว** ต่างจากแถวเอกสาร เพราะยังไม่มีลิงก์ต่อคนให้กด และ
# ``uri`` ของ LINE รับเฉพาะ http/https/tel/line — ``mailto:`` ไม่อยู่ในนั้น
# ปุ่มอีเมลจึงเสี่ยงถูกปฏิเสธ 400 ทั้งข้อความแบบเดียวกับบั๊กชื่อไฟล์ไทย
# (ดู :func:`_encode_uri`) เอาอีเมลขึ้นเป็นข้อความในแถวปลอดภัยกว่า


def instructor_row(index: int, row: dict) -> dict:
    """
    แถวอาจารย์: เลขลำดับ · ชื่อ · ตำแหน่ง/อีเมล/ห้อง/เวลาเข้าพบ

    ``email`` ที่ว่างต้องเขียนว่า "ไม่มีข้อมูลในระบบ" ไม่ใช่เว้นบรรทัดหาย —
    เหตุผลเดียวกับคำตอบแบบข้อความเดิม (เว้นว่างแล้วดูเหมือนระบบโหลดไม่ครบ)
    """
    details = [f"อีเมล: {row.get('email') or 'ไม่มีข้อมูลในระบบ'}"]
    if row.get("position"):
        details.insert(0, str(row["position"]))
    if row.get("room"):
        details.append(f"ห้อง: {row['room']}")
    if row.get("office_hours"):
        details.append(f"เวลาเข้าพบ: {row['office_hours']}")

    return _row_shell(
        [
            _row_number(index),
            {
                "type": "box",
                "layout": "vertical",
                "flex": 1,
                "margin": "10px",
                "contents": [
                    _row_title(row.get("name") or "(ไม่มีชื่อในคลังข้อมูล)"),
                    *[_row_detail(text) for text in details],
                ],
            },
        ]
    )


def instructors_flex_message(
    group_label: str,
    rows: list[dict],
    quick_reply: dict | None = None,
    *,
    notes: tuple[str, ...] | list[str] = (),
) -> dict:
    """รายชื่ออาจารย์ของหนึ่งกลุ่มวิชา — ฟองเดียว แถวละคน"""
    shown, total = rows[:MAX_ROWS], len(rows)
    body = [instructor_row(i, row) for i, row in enumerate(shown, start=1)]

    parts = [f"อาจารย์กลุ่ม{group_label} {total} คน"]
    if rows:
        parts.append(f"เริ่มจาก {rows[0].get('name') or ''}".strip())

    return _bubble(
        alt_text=" · ".join(parts),
        header=bubble_header("👥", f"อาจารย์กลุ่ม{group_label}", f"{total} คน"),
        body_contents=_rows_and_notes(body, total, notes),
        footer_text="💡 กดปุ่มด้านล่างเพื่อดูกลุ่มอื่น",
        quick_reply=quick_reply,
    )


def instructor_search_flex_message(
    keyword: str,
    rows: list[dict],
    quick_reply: dict | None = None,
    *,
    notes: tuple[str, ...] | list[str] = (),
) -> dict:
    """ผลค้นอาจารย์ — แถวเดียวกับรายชื่อทั้งกลุ่ม ต่างแค่หัวฟองบอกคำค้น"""
    shown, total = rows[:MAX_ROWS], len(rows)
    body = [instructor_row(i, row) for i, row in enumerate(shown, start=1)]

    return _bubble(
        alt_text=_search_alt_text(keyword, f"อาจารย์ {total} คน", rows, "name"),
        header=bubble_header(
            "🔎", f"ผลค้น “{truncate(keyword, 30)}”", f"เจออาจารย์ {total} คน"
        ),
        body_contents=_rows_and_notes(body, total, notes),
        footer_text="💡 ดูรายชื่อทั้งกลุ่มได้จากปุ่มด้านล่าง",
        quick_reply=quick_reply,
    )


# ── ฟอง 4-5: ความก้าวหน้า / วิชาเทอมถัดไป ───────────────────────────────────


def progress_bar(percent: int) -> dict:
    """
    แถบความก้าวหน้า — สิ่งที่คำตอบแบบข้อความทำไม่ได้ (เห็นทีเดียวว่าไปถึงไหน)

    ``percent`` ถูกบีบให้อยู่ 0-100 ก่อนใช้ เพราะ ``width`` ของ box รับเป็น
    เปอร์เซ็นต์ — ค่าเกิน 100% หรือค่าลบทำให้ LINE ปฏิเสธทั้งข้อความ
    และที่ 0% ไม่ใส่แท่งเลย (แท่งกว้าง 0 ขึ้นเป็นเส้นทึบบางรุ่น)
    """
    filled = max(0, min(100, int(percent)))
    track: dict = {
        "type": "box",
        "layout": "horizontal",
        "backgroundColor": FLEX_COLOR_TRACK,
        "cornerRadius": "6px",
        "height": "12px",
        "contents": [{"type": "filler"}],
    }
    if filled:
        track["contents"] = [
            {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": FLEX_COLOR_BRAND,
                "cornerRadius": "6px",
                "width": f"{filled}%",
                "contents": [{"type": "filler"}],
            },
            {"type": "filler"},
        ]
    return track


def course_row(row: dict) -> dict:
    """
    แถวรายวิชา: ชื่อวิชา · รหัส+เทอมที่แผนแนะนำ · ป้ายหน่วยกิตมุมขวา

    ``row`` เป็น dict ล้วน (``code`` / ``name`` / ``credits`` / ``term`` /
    ``note`` / ``action``) ไม่ใช่ ``planner.CourseStatus`` — ไฟล์นี้ไม่ควรรู้จัก
    ชนิดข้อมูลของ planner และ ``action`` ผู้เรียกส่งมาเอง (ดู docstring หัวไฟล์)
    """
    details = [text for text in [row.get("code"), row.get("term")] if text]
    lines = [_row_title(row.get("name") or "(ยังไม่มีชื่อวิชาในคลังข้อมูล)")]
    if details:
        lines.append(_row_detail(" · ".join(str(text) for text in details)))
    if row.get("note"):
        lines.append(_row_detail(str(row["note"])))

    contents: list[dict] = [
        {
            "type": "box",
            "layout": "vertical",
            "flex": 1,
            "contents": lines,
        }
    ]
    if row.get("credits"):
        contents.append(_badge(f"{row['credits']} นก."))

    return _row_shell(contents, row.get("action"))


def progress_flex_message(
    *,
    program_code: str,
    percent: int,
    passed_courses: int,
    plan_courses: int,
    passed_credits: int,
    remaining_headline: str,
    stats: tuple[str, ...] | list[str] = (),
    course_rows: list[dict],
    notes: tuple[str, ...] | list[str] = (),
    quick_reply: dict | None = None,
) -> dict:
    """
    ภาพรวมความก้าวหน้าตามหลักสูตร — แถบ % ด้านบน แล้วรายการวิชาที่เหลือ

    ตัวเลขทั้งหมดผู้เรียกคำนวณมาแล้ว (``app/planner.py``) ไฟล์นี้ไม่คิดเลขเอง
    """
    shown, total = course_rows[:MAX_ROWS], len(course_rows)
    summary: list[dict] = [
        {
            "type": "text",
            "text": f"{int(percent)}%",
            "color": FLEX_COLOR_BRAND,
            "weight": "bold",
            "size": "xxl",
        },
        progress_bar(percent),
        _row_detail(
            f"ผ่านแล้ว {passed_courses}/{plan_courses} วิชา"
            f" · {passed_credits} หน่วยกิต"
        ),
    ]
    summary.extend(_row_detail(text) for text in stats if text)

    body: list[dict] = [
        {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "13px",
            "backgroundColor": FLEX_COLOR_ROW_BG,
            "cornerRadius": "10px",
            "contents": summary,
        },
        _row_detail(remaining_headline),
    ]
    body.extend(
        _rows_and_notes([course_row(row) for row in shown], total, notes)
    )

    return _bubble(
        alt_text=(
            f"ความก้าวหน้า {program_code} ผ่านแล้ว {passed_courses}/{plan_courses}"
            f" วิชา ({int(percent)}%) · {remaining_headline}"
        ),
        header=bubble_header(
            "📈",
            "ความก้าวหน้าตามหลักสูตร",
            f"หลักสูตร {program_code}",
        ),
        body_contents=body,
        footer_text="💡 กด “เทอมหน้าลงอะไรดี” เพื่อดูวิชาที่ควรลงต่อ",
        quick_reply=quick_reply,
    )


def next_term_flex_message(
    *,
    semester: int,
    course_count: int,
    credits: int,
    max_credits: int,
    course_rows: list[dict],
    notes: tuple[str, ...] | list[str] = (),
    quick_reply: dict | None = None,
) -> dict:
    """ตะกร้าวิชาที่เสนอให้ลงเทอมถัดไป — แถวละวิชา ป้ายหน่วยกิตมุมขวา"""
    shown, total = course_rows[:MAX_ROWS], len(course_rows)
    body = [course_row(row) for row in shown]

    return _bubble(
        alt_text=(
            f"วิชาแนะนำภาคเรียนที่ {semester} {course_count} วิชา"
            f" {credits} หน่วยกิต"
        ),
        header=bubble_header(
            "🗓️",
            f"วิชาแนะนำ ภาคเรียนที่ {semester}",
            f"{course_count} วิชา {credits} หน่วยกิต · เพดานที่ใช้คิด {max_credits}",
        ),
        body_contents=_rows_and_notes(body, total, notes),
        footer_text="💡 ตัวเลขคำนวณจากแผนการเรียน ไม่ใช่การลงทะเบียนจริง",
        quick_reply=quick_reply,
    )
