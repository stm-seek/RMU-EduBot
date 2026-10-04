"""
สร้าง message object ของ LINE Messaging API

แยกออกมาเป็นฟังก์ชันเพื่อให้มี **ที่เดียว** ที่รู้เรื่องข้อจำกัดของ LINE
และเทสได้โดยไม่ต้องยิง API จริง

ข้อจำกัดที่ยืนยันจากเอกสาร LINE:

* reply ได้สูงสุด **5 message objects** ต่อครั้ง
* text message ยาวสุด **5,000 ตัวอักษร**
* Quick Reply สูงสุด **13 ปุ่ม** และ **แสดงผลได้แค่ iOS/Android ไม่ขึ้นบน Desktop**
* label ของ action ยาวสุด 20 ตัวอักษร, postback data ยาวสุด 300 ตัวอักษร
* Flex Message (ข้อจำกัดของมันแยกอยู่ที่ :mod:`app.line.flex`)
"""

from __future__ import annotations

MAX_MESSAGES_PER_REPLY = 5
MAX_TEXT_LENGTH = 5000
MAX_QUICK_REPLY_ITEMS = 13
MAX_LABEL_LENGTH = 20
MAX_POSTBACK_DATA_LENGTH = 300
MAX_DISPLAY_TEXT_LENGTH = 300


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
    ปุ่มที่ส่ง postback event กลับมา

    ค่าปริยายจะ **โชว์ข้อความของ user เป็นฟอง** เท่ากับ ``label`` ที่กด
    (เมื่อก่อนไม่โชว์ → ในแชทเงียบเหมือนไม่ได้กดอะไร) ธรรมเนียมของ ``display_text``:

    * ``None`` (ไม่ส่งมา) → โชว์ฟอง = ``label``
    * ``""`` (สตริงว่าง) → **ไม่โชว์ฟองเลย** สำหรับปุ่มนำทางที่ฟองเป็นสัญญาณรบกวน
      (เช่น ปุ่ม "เมนูหลัก" ที่ต่อท้ายแทบทุกคำตอบ)
    * สตริงอื่น → โชว์ข้อความนั้นแทน (เช่นอยากให้ฟองอ่านเป็นประโยคเต็ม)

    ``data`` ไม่ถูกแตะ — ``src=rich`` และพารามิเตอร์อื่นยังอยู่ครบ

    >>> postback_action('ดูเดดไลน์', 'action=deadline')
    {'type': 'postback', 'label': 'ดูเดดไลน์', 'data': 'action=deadline', 'displayText': 'ดูเดดไลน์'}
    >>> 'displayText' in postback_action('เมนูหลัก', 'action=menu', '')
    False
    """
    label = truncate(label, MAX_LABEL_LENGTH)
    action: dict = {
        "type": "postback",
        "label": label,
        "data": truncate(data, MAX_POSTBACK_DATA_LENGTH),
    }
    # None = ไม่ได้ส่งมา → ใช้ label (ที่ตัดแล้ว) เป็นฟอง; "" = ตั้งใจปิดฟอง (ปุ่มนำทาง)
    bubble = label if display_text is None else display_text
    if bubble:
        action["displayText"] = truncate(bubble, MAX_DISPLAY_TEXT_LENGTH)
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
    postback_action("วางแผนการเรียน", "action=study_plan"),
    postback_action("วางแผนเกรด", "action=grade_plan"),
    postback_action("ปฏิทินการศึกษา", "action=calendar"),
    postback_action("เอกสาร/คำร้อง", "action=documents"),
    postback_action("ติดต่ออาจารย์", "action=instructors"),
    postback_action("ทุน/กู้ยืม", "action=loan"),
    # แบบประเมินระบบ (งานวิจัย/ธีสิส) — ต้องอยู่ในเมนูหลัก เพราะทั้งอาจารย์
    # ผู้เชี่ยวชาญและนักศึกษาต้องเข้าถึงได้เองโดยไม่ต้องให้ใครส่งลิงก์ให้
    # 7 ปุ่มยังห่างเพดาน 13 ของ LINE (ที่เหลือเผื่อปุ่มพิเศษ)
    postback_action("แบบประเมิน", "action=survey"),
]

# ปุ่มทางกลับแบบสั้นสำหรับคำตอบ fallback — ให้ผู้ใช้เปิดเมนูหลักได้ทันที
# แม้ไม่ได้อยู่ในบริบทของ Quick Reply ชุดเต็ม
# ปิดฟอง (display_text="") เพราะเป็นปุ่มนำทางที่ต่อท้ายแทบทุกคำตอบ — ขึ้นฟอง
# "เมนูหลัก" ทุกครั้งที่กดคือสัญญาณรบกวน ไม่ใช่คำถามของผู้ใช้
MAIN_MENU_FALLBACK_ACTION = postback_action("เมนูหลัก", "action=menu", "")

# ── แบบประเมินระบบ (งานวิจัย) ────────────────────────────────────────────────
# เก็บ URL ไว้ที่เดียว: ลิงก์ฟอร์มยาวและก๊อปผิดง่าย ถ้ากระจายหลายที่แล้ว
# เปลี่ยนฟอร์มทีหลังจะเหลือลิงก์เก่าค้างอยู่จุดใดจุดหนึ่งแน่นอน
#
# ตัด ``?usp=header`` / ``?usp=publish-editor`` ที่ติดมาจากหน้าแก้ฟอร์มออกแล้ว
# — พารามิเตอร์นั้นไม่จำเป็นสำหรับคนตอบแบบประเมิน

SURVEY_EXPERT_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSd8bpokRe6f0Tl9RLFddC1zYRsRWGyu1fknhIYdG_J4PQgH2A/viewform"
)
SURVEY_STUDENT_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSea1Tcb0p6LI6QCr01ACnjDaOSEPC2tjth1NyH-tagSp2Heig/viewform"
)

SURVEY_EXPERT_TITLE = (
    "แบบประเมินคุณภาพระบบแชทบอทให้คำปรึกษาด้านการเรียนด้วย AI สำหรับผู้เชี่ยวชาญ"
)
SURVEY_STUDENT_TITLE = (
    "แบบประเมินความพึงพอใจและการยอมรับเทคโนโลยี (TAM) ของแชทบอท AI "
    "ให้คำปรึกษาด้านการเรียน สำหรับนักศึกษา"
)


def survey_message() -> dict:
    """
    แบบประเมินระบบ 2 ใบ — ผู้เชี่ยวชาญ / นักศึกษา

    ใส่ **ทั้งชื่อเต็มและ URL ไว้ในตัวข้อความ** ไม่พึ่งแค่ปุ่ม เพราะ Quick Reply
    ไม่ขึ้นบน LINE เดสก์ท็อป (และหายไปเมื่อผู้ใช้พิมพ์ข้อความอื่นต่อ) —
    อาจารย์ที่เปิดบนคอมต้องก๊อปลิงก์ไปเองได้

    >>> SURVEY_EXPERT_URL in survey_message()['text']
    True
    >>> [i['action']['type'] for i in survey_message()['quickReply']['items']][:2]
    ['uri', 'uri']
    """
    return text_message(
        "แบบประเมินระบบ (สำหรับงานวิจัย)\n\n"
        "ขอความกรุณาช่วยประเมินระบบนี้ครับ เลือกใบที่ตรงกับท่าน\n\n"
        "1) สำหรับอาจารย์/ผู้เชี่ยวชาญ\n"
        f"{SURVEY_EXPERT_TITLE}\n"
        f"{SURVEY_EXPERT_URL}\n\n"
        "2) สำหรับนักศึกษา\n"
        f"{SURVEY_STUDENT_TITLE}\n"
        f"{SURVEY_STUDENT_URL}\n\n"
        "กดปุ่มด้านล่าง หรือก๊อปลิงก์ไปเปิดในเบราว์เซอร์ได้เลยครับ",
        quick_reply(
            [
                uri_action("สำหรับผู้เชี่ยวชาญ", SURVEY_EXPERT_URL),
                uri_action("สำหรับนักศึกษา", SURVEY_STUDENT_URL),
                *MAIN_MENU_ACTIONS,
            ]
        ),
    )

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
        quick_reply([MAIN_MENU_FALLBACK_ACTION, *MAIN_MENU_ACTIONS]),
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


# ── ทักทาย / พูดคุยเล็ก ๆ (ตอบด้วย keyword ก่อน ไม่เรียก LLM) ────────────────
# พิมพ์ทักทาย/ขอบคุณ/ลา/ขอเมนู แล้วเดิมตกไป search → ไม่เจอ → fallback ห้วน ๆ
# ตอบสั้น ๆ อย่างเป็นมิตรแล้วชี้เข้าเมนูหลักทันที (Quick Reply ไม่ขึ้นบนเดสก์ท็อป
# แต่เมนูหลัก 7 ปุ่มยังต่อท้ายได้เผื่อคนใช้มือถือ)


def greeting_message() -> dict:
    """ตอบคำทักทาย — อุ่น ๆ สั้น ๆ แล้วชวนเลือกหัวข้อจากเมนู"""
    return text_message(
        "สวัสดีครับ ผมเป็นผู้ช่วยให้คำปรึกษาด้านการเรียน\n"
        "อยากให้ช่วยเรื่องไหน เลือกจากเมนูด้านล่าง หรือพิมพ์คำถามมาได้เลยครับ",
        quick_reply(MAIN_MENU_ACTIONS),
    )


def thanks_message() -> dict:
    """ตอบคำขอบคุณ — รับคำแล้วเปิดทางถามต่อ ไม่ปล่อยให้บทสนทนาจบห้วน"""
    return text_message(
        "ยินดีครับ ถ้ามีอะไรให้ช่วยอีก เลือกจากเมนูด้านล่างหรือพิมพ์มาได้เลยครับ",
        quick_reply(MAIN_MENU_ACTIONS),
    )


def goodbye_message() -> dict:
    """ตอบคำลา — อวยพรสั้น ๆ แล้วบอกวิธีกลับมาใช้งาน"""
    return text_message(
        "ด้วยความยินดีครับ ขอให้เรียนราบรื่นนะครับ\n"
        "กลับมาถามได้ทุกเมื่อ กดเมนูด้านล่างเพื่อเริ่มใหม่ได้เลยครับ",
        quick_reply(MAIN_MENU_ACTIONS),
    )


def help_message() -> dict:
    """ตอบคำขอความช่วยเหลือ/ขอเมนู — บอกสิ่งที่ทำได้แล้วโชว์เมนูหลัก"""
    return text_message(
        "ผมช่วยได้หลายเรื่องครับ เช่น\n"
        "  • หาเอกสาร/แบบฟอร์มคำร้อง\n"
        "  • ข้อมูลติดต่ออาจารย์\n"
        "  • พิมพ์รหัสวิชา 7 หลัก เพื่อดูรายละเอียดรายวิชา\n"
        "  • วางแผนการเรียน/วางแผนเกรด และตรวจสอบจบ\n"
        "  • กด “ปรึกษา AI” เพื่อสอบถามคำแนะนำการเรียนทั่วไป\n"
        "เลือกจากเมนูด้านล่างได้เลยครับ",
        quick_reply(MAIN_MENU_ACTIONS),
    )
