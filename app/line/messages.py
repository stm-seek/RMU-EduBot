"""
สร้าง message object ของ LINE Messaging API

แยกออกมาเป็นฟังก์ชันเพื่อให้มี **ที่เดียว** ที่รู้เรื่องข้อจำกัดของ LINE
และเทสได้โดยไม่ต้องยิง API จริง

ข้อจำกัดที่ยืนยันจากเอกสาร LINE:

* reply ได้สูงสุด **5 message objects** ต่อครั้ง
* text message ยาวสุด **5,000 ตัวอักษร**
* Quick Reply สูงสุด **13 ปุ่ม** และ **แสดงผลได้แค่ iOS/Android ไม่ขึ้นบน Desktop**
* label ของ action ยาวสุด 20 ตัวอักษร, postback data ยาวสุด 300 ตัวอักษร
"""

from __future__ import annotations

MAX_MESSAGES_PER_REPLY = 5
MAX_TEXT_LENGTH = 5000
MAX_QUICK_REPLY_ITEMS = 13
MAX_LABEL_LENGTH = 20
MAX_POSTBACK_DATA_LENGTH = 300


def truncate(text: str, limit: int) -> str:
    """
    ตัดข้อความให้พอดี limit โดยเติม '…' ถ้าถูกตัด

    >>> truncate('สวัสดี', 10)
    'สวัสดี'
    >>> truncate('abcdefghij', 5)
    'abcd…'
    """
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "\u2026"


def text_message(text: str, quick_reply: dict | None = None) -> dict:
    """
    สร้าง text message

    >>> text_message('สวัสดีครับ')
    {'type': 'text', 'text': 'สวัสดีครับ'}
    >>> len(text_message('ก' * 6000)['text'])
    5000
    """
    message: dict = {"type": "text", "text": truncate(text, MAX_TEXT_LENGTH)}
    if quick_reply:
        message["quickReply"] = quick_reply
    return message


def postback_action(label: str, data: str, display_text: str | None = None) -> dict:
    """
    ปุ่มที่ส่ง postback event กลับมา (ไม่โชว์ข้อความของ user ถ้าไม่ตั้ง displayText)

    ใช้กับ Rich Menu / Quick Reply ที่ต้องการให้ระบบรู้ intent แน่ ๆ
    ไม่ต้องเดาจากข้อความ

    >>> postback_action('ดูเดดไลน์', 'action=deadline')
    {'type': 'postback', 'label': 'ดูเดดไลน์', 'data': 'action=deadline'}
    """
    action: dict = {
        "type": "postback",
        "label": truncate(label, MAX_LABEL_LENGTH),
        "data": truncate(data, MAX_POSTBACK_DATA_LENGTH),
    }
    if display_text:
        action["displayText"] = display_text
    return action


def message_action(label: str, text: str | None = None) -> dict:
    """
    ปุ่มที่ส่งข้อความแทน user (ข้อความจะโชว์ในแชท)

    >>> message_action('ทุนการศึกษา')
    {'type': 'message', 'label': 'ทุนการศึกษา', 'text': 'ทุนการศึกษา'}
    """
    return {
        "type": "message",
        "label": truncate(label, MAX_LABEL_LENGTH),
        "text": text or label,
    }


def uri_action(label: str, uri: str) -> dict:
    """
    ปุ่มเปิดลิงก์ — ใช้ส่งเอกสาร/แบบฟอร์มให้นักศึกษา

    >>> uri_action('ดาวน์โหลด', 'https://example.com/a.pdf')
    {'type': 'uri', 'label': 'ดาวน์โหลด', 'uri': 'https://example.com/a.pdf'}
    """
    return {
        "type": "uri",
        "label": truncate(label, MAX_LABEL_LENGTH),
        "uri": uri,
    }


def quick_reply(actions: list[dict]) -> dict:
    """
    ห่อ action เป็น quickReply object (ตัดเหลือ 13 ปุ่มตาม limit ของ LINE)

    >>> qr = quick_reply([message_action(f'ปุ่ม{i}') for i in range(20)])
    >>> len(qr['items'])
    13
    >>> qr['items'][0]['type']
    'action'
    """
    items = [
        {"type": "action", "action": action}
        for action in actions[:MAX_QUICK_REPLY_ITEMS]
    ]
    return {"items": items}


def clamp_messages(messages: list[dict]) -> list[dict]:
    """
    ตัดจำนวน message ให้ไม่เกิน 5 ตาม limit ของ reply API

    ถ้าเกิน LINE จะ reject ทั้ง request (ไม่ใช่ตัดให้เอง)

    >>> len(clamp_messages([text_message('x')] * 9))
    5
    """
    return messages[:MAX_MESSAGES_PER_REPLY]


# ── ข้อความมาตรฐานของระบบ ───────────────────────────────────────────────────

MAIN_MENU_ACTIONS = [
    postback_action("แผนการเรียน", "action=plan"),
    postback_action("ปฏิทินการศึกษา", "action=calendar"),
    postback_action("เอกสาร/คำร้อง", "action=documents"),
    postback_action("ติดต่ออาจารย์", "action=instructors"),
    postback_action("ทุน/กู้ยืม", "action=loan"),
]

# ── โหมดปรึกษา AI ───────────────────────────────────────────────────────────
# LLM ตอบเฉพาะเมื่อ user "เข้าโหมด" แล้ว (กันเสีย token ฟรีกับทุก search miss)
# ทางเข้า: ปุ่มนี้ หรือนำหน้าข้อความด้วย "ปรึกษา" ทางออก: ปุ่มจบ/คำออก/
# ว่างเกินกำหนด/ครบเพดานรอบ — กติกาทั้งหมดอยู่ที่ ``app.ai_chat.dispatch``

CONSULT_AI_ACTION = postback_action("ปรึกษา AI", "action=ai_session")
CONSULT_EXIT_ACTION = postback_action("จบการปรึกษา", "action=ai_end")


def _consult_quick_reply() -> dict:
    """ปุ่มจบการปรึกษา + เมนูหลัก — อยู่ระหว่างโหมดต้องมีทางออกเสมอ"""
    return quick_reply([CONSULT_EXIT_ACTION, *MAIN_MENU_ACTIONS])


def ai_session_message(text: str) -> dict:
    """คำตอบจาก AI ระหว่างอยู่ในโหมดปรึกษา — ปุ่มจบการปรึกษาต้องตามมาด้วย"""
    return text_message(text, _consult_quick_reply())


def session_open_message() -> dict:
    """ตอบเมื่อเพิ่งเข้าโหมดปรึกษา — บอกกติกาและวิธีออกให้ชัด"""
    return text_message(
        "ได้ครับ โหมดปรึกษาเปิดแล้ว\n\n"
        "พิมพ์คำถามเรื่องการเรียน/ชีวิตมหาวิทยาลัยมาได้เลย\n"
        "เช่น การปรับตัว การจัดการเวลา เทคนิคอ่านหนังสือ การเตรียมสอบ\n\n"
        "พิมพ์ “ออก” หรือกดปุ่ม “จบการปรึกษา” เมื่อคุยเสร็จ\n"
        "(โหมดจะปิดเองอัตโนมัติถ้าว่างเกิน 30 นาที)",
        _consult_quick_reply(),
    )


def session_closed_message() -> dict:
    """ตอบเมื่อจบโหมดปรึกษา (ปุ่ม/คำออก/หมดเวลา/ครบรอบ ใช้ร่วมกัน)"""
    return text_message(
        "รับทราบครับ จบโหมดปรึกษาแล้ว\n"
        "ถ้าอยากคุยอีกครั้ง กดปุ่ม “ปรึกษา AI” หรือพิมพ์ข้อความที่\n"
        "ขึ้นต้นด้วย “ปรึกษา” ได้เลยครับ",
        quick_reply([CONSULT_AI_ACTION, *MAIN_MENU_ACTIONS]),
    )


def session_turn_limit_message() -> dict:
    """ตอบเมื่อครบเพดานรอบต่อ session — เสนอให้เริ่มใหม่ ไม่ใช่เงียบ"""
    return text_message(
        "รอบนี้เราคุยกันครบตามที่ระบบกำหนดแล้วครับ\n"
        "กดปุ่ม “ปรึกษา AI” เพื่อเริ่มปรึกษาหัวข้อใหม่ได้เลย",
        quick_reply([CONSULT_AI_ACTION, *MAIN_MENU_ACTIONS]),
    )


def fallback_message() -> dict:
    """
    ข้อความเมื่อระบบไม่เข้าใจคำถาม (Requirement ข้อ 14)

    **ห้ามให้ LLM เดาคำตอบ** เรื่องกฎระเบียบ/กำหนดการ เพราะถ้าตอบผิด
    นักศึกษาเสียหายจริง — เสนอเมนูให้เลือกและช่องทางติดต่อเจ้าหน้าที่แทน
    """
    return text_message(
        "ขออภัยครับ ระบบยังไม่พบข้อมูลที่ตรงกับคำถามนี้\n\n"
        "ลองเลือกหัวข้อด้านล่าง หรือติดต่อสำนักส่งเสริมวิชาการและงานทะเบียน\n"
        "โทร 0-4372-2118 ต่อ 269",
        quick_reply(MAIN_MENU_ACTIONS),
    )


def no_data_message(topic: str) -> dict:
    """
    ใช้เมื่อรู้ว่า "ไม่มีข้อมูลในระบบ" — ต่างจาก fallback ที่ไม่เข้าใจคำถาม

    เช่น ถามเบอร์โทรอาจารย์ ซึ่งเว็บคณะไม่มีข้อมูลนี้ (0/28 คน)
    ต้องบอกตรง ๆ ว่าไม่มี ห้ามเดา
    """
    return text_message(
        f"ระบบยังไม่มีข้อมูล{topic}ครับ\n\n"
        "ข้อมูลนี้ไม่ได้เผยแพร่บนเว็บไซต์ของคณะ "
        "แนะนำให้ติดต่อสำนักงานคณะโดยตรง",
        quick_reply(MAIN_MENU_ACTIONS),
    )
