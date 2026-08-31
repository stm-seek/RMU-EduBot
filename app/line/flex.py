"""
สร้าง Flex Message — รายการเอกสารของหนึ่งหมวดใน **ฟองเดียว** (แถวเรียงลง)

ออกแบบตามแบบที่ผู้ใช้เลือกเอง (23 ส.ค. 2026): หัวฟองน้ำเงินบอกชื่อหมวด
ตัวฟองเป็นแถวเอกสาร แถวละฉบับ (ไอคอน · ชื่อ · ชนิดไฟล์ · ปุ่ม ›)
แตะแถวไหนเปิดเอกสารนั้นทั้งแถว — ไม่ต้องเลื่อนดูทีละการ์ด

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
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": FLEX_COLOR_BRAND,
        "paddingAll": "18px",
        "contents": [
            {
                "type": "text",
                "text": f"{category_icon(category_key)}  {category_label}",
                "color": FLEX_COLOR_WHITE,
                "weight": "bold",
                "size": "xl",
            },
            {
                "type": "text",
                "text": f"{total} ฉบับ · เลือกเอกสารที่ต้องการ",
                "color": FLEX_COLOR_HEADER_SUB,
                "size": "sm",
                "margin": "4px",
            },
        ],
    }


def document_row(row: dict) -> dict:
    """
    แถวเอกสาร 1 แถว: ไอคอน · ชื่อ + ชนิดไฟล์ · วงปุ่ม ›

    ``action`` ตั้งบนกล่องแถวเลย → แตะตรงไหนของแถวก็เปิดเอกสาร
    ปุ่ม › ด้านขวาเป็นแค่สัญญาณว่าแถวนี้กดได้
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
                        "text": document_kind(row["url"]),
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
    return {
        "type": "box",
        "layout": "horizontal",
        "backgroundColor": FLEX_COLOR_FOOTER_BG,
        "paddingAll": "12px",
        "contents": [
            {
                "type": "text",
                "text": "💡 แตะที่รายการเพื่อเปิดเอกสาร",
                "color": FLEX_COLOR_STEEL,
                "size": "xs",
                "align": "center",
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
