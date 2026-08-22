"""
นิยาม Rich Menu 6 ช่อง — **ข้อมูล ไม่ใช่การกระทำ**

แยกไฟล์นี้ออกจากตัวยิง API (``scripts/rich_menu.py``) เพื่อให้เทสตรวจนิยาม
ได้โดยไม่ต้องมี token และไม่ต้องมีไฟล์ภาพ

ทำไมต้องมี ``src=rich`` ในทุกปุ่ม: LINE ส่ง postback event หน้าตาเหมือนกันเป๊ะ
ไม่ว่าจะกดจาก Rich Menu หรือจาก Quick Reply ในบทสนทนา ถ้าไม่ฝังที่มาไว้เอง
``chat_logs`` จะแยกสองพื้นผิวไม่ออก (ดู :func:`app.router._answer_surface`)

ข้อจำกัดที่ยืนยันจากเอกสาร LINE (2026-08):

* ภาพ JPEG/PNG ไม่เกิน **1 MB**, กว้าง **800–2500 px**, สูง **≥250 px**,
  และ **กว้าง/สูง ≥ 1.45** — ขนาดที่ LINE ใช้ในตัวอย่างคือ ``2500x1686``
  และ ``1200x810`` (ของเราใช้ 1200x810 ตามไฟล์ภาพที่ทำมาจริง)
* ``areas`` ไม่เกิน **20 ช่อง**, ``name`` ≤300, ``chatBarText`` ≤**14**
* postback ``data`` ≤300, ``label`` ของ action ใน Rich Menu ≤20 (ไม่บังคับใส่)
* **Rich Menu ไม่แสดงบน LINE for PC (macOS/Windows)** — เดโมต้องใช้มือถือ
* เปลี่ยนภาพของ Rich Menu ที่อัปโหลดแล้ว **ไม่ได้** ต้องสร้างเมนูใหม่
"""

from __future__ import annotations

import struct

# ── ข้อจำกัดของภาพ (ยืนยันจากเอกสาร LINE) ────────────────────────────────────

MAX_IMAGE_BYTES = 1_000_000
MIN_WIDTH, MAX_WIDTH = 800, 2500
MIN_HEIGHT = 250
MIN_RATIO = 1.45

# ขนาดของไฟล์ภาพที่ใช้จริง (``1200x810`` เป็นหนึ่งในขนาดที่ LINE ใช้ในตัวอย่าง
# ทางการ) — เปลี่ยนภาพเป็นขนาดอื่นต้องมาแก้ที่นี่ด้วย ไม่งั้น ``image_problems``
# จะฟ้องว่าพิกัดปุ่มไม่ตรงกับภาพ
MENU_WIDTH = 1200
MENU_HEIGHT = 810

CHAT_BAR_TEXT = "เมนู"
MENU_NAME = "RMU CS Assistant — เมนูหลัก 6 ช่อง"

# ── พิกัดที่วัดจากไฟล์ภาพจริง ────────────────────────────────────────────────
#
# ภาพเมนูไม่ใช่ตาราง 3x2 ที่ปูเต็มเฟรม — มี **แถบหัวเรื่อง** "เมนูหลัก" อยู่บนสุด
# กับ **แถบท้าย** ที่ชวนให้พิมพ์ถามอยู่ล่างสุด ถ้าปูปุ่มเต็มภาพแบบหาร 3 หาร 2
# เส้นแบ่งแถวจะตกที่ y=405 ซึ่ง **พาดกลางป้ายชื่อของการ์ดแถวบน** → แตะคำว่า
# "ปรึกษา AI" แล้วได้คำตอบของ "ค้นรายวิชา" ที่อยู่ใต้มัน
#
# เลขข้างล่างได้จากการสแกนภาพหาแถบพื้นน้ำเงินเข้มที่คั่นการ์ด แล้วขยายขอบไป
# กึ่งกลางร่อง → ไม่มีร่องที่กดไม่ติดระหว่างช่อง
# ส่วนแถบหัว (y<133) กับแถบท้าย (y≥758) **เจตนาปล่อยให้กดไม่ได้** เพราะแตะแล้ว
# เงียบดีกว่าแตะหัวเรื่องแล้วเด้งคำตอบที่ไม่ได้สั่ง
#
# **เปลี่ยนภาพเมื่อไรต้องวัดใหม่** — ``tests/test_rich_menu.py`` ยึดเลขชุดนี้ไว้
COLUMN_EDGES: tuple[int, ...] = (0, 403, 798, MENU_WIDTH)
ROW_EDGES: tuple[int, ...] = (133, 462, 758)

COLUMNS = len(COLUMN_EDGES) - 1
ROWS = len(ROW_EDGES) - 1

# เรียงตามลำดับที่วางบนภาพ: ซ้าย→ขวา แถวบนก่อน
# **ภาพเป็นเจ้าของลำดับ ไม่ใช่โค้ด** — สลับสองบรรทัดในนี้แล้วไม่แก้ภาพ
# = ปุ่มตอบผิดช่องทั้งใบ และ LINE ไม่ฟ้องอะไรเลย
#
# หลักการเลือก 6 ช่องนี้: **ทุกช่องต้องตอบได้ด้วยข้อมูลที่มีจริงวันนี้**
#   • เอกสาร 31 ฉบับ 10 หมวด, กู้ยืม 12 ฉบับ (หมวดใหญ่สุด), อาจารย์ 28 คน
#   • รายวิชา 145 วิชา (45 วิชารู้ว่าเปิดเทอมไหน)
#   • ปรึกษา AI = โหมดที่ต้องมีทางเข้าให้เห็น ไม่มีใครเดาว่าต้องพิมพ์ "ปรึกษา"
#   • ทำอะไรได้บ้าง = ข้อความต้อนรับเดิม (ไม่ต้องเขียนโค้ดใหม่)
#
# ที่ **ไม่** เอาเข้ามา:
#   • แผนการเรียน — prerequisites/curriculum_rules ยังว่าง (รอ มคอ.2)
#     ช่องที่ตอบว่า "ยังทำไม่ได้" ทุกครั้งสอนผู้ใช้ว่าเมนูนี้กดไปก็เท่านั้น
#   • ปฏิทินการศึกษา — มีเอกสารฉบับเดียว และอยู่ในช่อง "เอกสาร" ห่างไป 1 แท็ป
#   • เข้าสู่ระบบ (LIFF) — ยังไม่มีหน้าเว็บ กดแล้วเจอ error page
SLOTS: tuple[tuple[str, str], ...] = (
    ("ปรึกษา AI", "ai_session"),
    ("กู้ยืม กยศ.", "loan"),
    ("ติดต่ออาจารย์", "instructors"),
    ("ค้นรายวิชา", "course"),
    ("เอกสาร/คำร้อง", "documents"),
    ("ทำอะไรได้บ้าง", "menu"),
)


def cell_bounds(index: int) -> dict[str, int]:
    """
    พิกัดช่องที่ ``index`` (0 = ซ้ายบน) บนตาราง 3x2 ที่วัดจากภาพ

    ช่องติดกันสนิทไม่มีร่อง แต่ **ไม่กินแถบหัวเรื่องกับแถบท้ายภาพ**

    >>> cell_bounds(0)
    {'x': 0, 'y': 133, 'width': 403, 'height': 329}
    >>> cell_bounds(2)['width']
    402
    >>> cell_bounds(5)
    {'x': 798, 'y': 462, 'width': 402, 'height': 296}
    """
    if not 0 <= index < COLUMNS * ROWS:
        raise ValueError(f"ช่องที่ {index} อยู่นอกตาราง {COLUMNS}x{ROWS}")

    column, row = index % COLUMNS, index // COLUMNS
    x, right = COLUMN_EDGES[column], COLUMN_EDGES[column + 1]
    y, bottom = ROW_EDGES[row], ROW_EDGES[row + 1]

    return {"x": x, "y": y, "width": right - x, "height": bottom - y}


def postback_data(action: str) -> str:
    """
    postback data ของปุ่มบนเมนู — **ต้องมี ``src=rich`` เสมอ**

    >>> postback_data('loan')
    'action=loan&src=rich'
    """
    return f"action={action}&src=rich"


def build_rich_menu() -> dict:
    """
    rich menu object ที่ส่งเข้า ``POST /v2/bot/richmenu`` ได้ตรง ๆ

    >>> menu = build_rich_menu()
    >>> menu['size']
    {'width': 1200, 'height': 810}
    >>> len(menu['areas'])
    6
    >>> menu['areas'][1]['action']['data']
    'action=loan&src=rich'
    """
    return {
        "size": {"width": MENU_WIDTH, "height": MENU_HEIGHT},
        # false = แถบเมนูพับอยู่ตอนเปิดแชท ผู้ใช้กดเปิดเอง
        # true จะบังหน้าจอแชททันทีซึ่งกวนตอนอ่านคำตอบยาว ๆ
        "selected": False,
        "name": MENU_NAME,
        "chatBarText": CHAT_BAR_TEXT,
        "areas": [
            {
                "bounds": cell_bounds(index),
                "action": {
                    "type": "postback",
                    "label": label,
                    "data": postback_data(action),
                },
            }
            for index, (label, action) in enumerate(SLOTS)
        ],
    }


# ── ใบโหมดปรึกษา (สลับแสดงเฉพาะคนที่อยู่ในโหมด) ─────────────────────────────
#
# แยกจากใบหลักโดยเจตนา: คนที่อยู่ในโหมดปรึกษาต้องการ "ทางออก" ที่เห็นชัด
# (จบการปรึกษา) กับ "ทางกลับ" (เมนูหลัก) เท่านั้น — ปุ่มอื่นจะชวนเผลอออก
# จากโหมดโดยไม่ได้ตั้งใจ (เช่น กด กยศ. แล้ว search รับช่วงต่อทั้งที่ยัง
# คุยค้างอยู่) การสลับใช้ per-user link ใน ``app/main.py`` ไม่ใช้
# richmenuswitch action เพราะแบบนั้น **ไม่ส่ง postback กลับ webhook**
# = บันทึก ``chat_logs`` ไม่ได้ ซึ่งขัดหลักการวัดผลของโปรเจกต์

CONSULT_MENU_NAME = "RMU CS Assistant — โหมดปรึกษา AI"
CONSULT_CHAT_BAR_TEXT = "ปรึกษา AI"

# 2 ปุ่มแบ่งครึ่งโซนการ์ดของใบหลัก (y=133..758) พอดี — แถบหัว/ท้าย
# เจตนาปล่อยให้กดไม่ได้เหมือนใบหลัก และปุ่มทั้งสองมี handler ใน
# ``POSTBACK_HANDLERS`` อยู่แล้ว (ai_end / menu) ไม่ต้องเพิ่มโค้ดฝั่ง router
CONSULT_SLOTS: tuple[tuple[str, str], ...] = (
    ("จบการปรึกษา", "ai_end"),
    ("เมนูหลัก", "menu"),
)

CONSULT_COLUMN_EDGES: tuple[int, ...] = (0, MENU_WIDTH // 2, MENU_WIDTH)


def consult_cell_bounds(index: int) -> dict[str, int]:
    """
    พิกัดช่องของใบปรึกษา (0 = ซ้าย, 1 = ขวา) — ครึ่งซ้าย/ขวาของโซนการ์ด

    >>> consult_cell_bounds(0)
    {'x': 0, 'y': 133, 'width': 600, 'height': 625}
    >>> consult_cell_bounds(1)
    {'x': 600, 'y': 133, 'width': 600, 'height': 625}
    """
    if not 0 <= index < len(CONSULT_SLOTS):
        raise ValueError(f"ช่องที่ {index} อยู่นอกตารางใบปรึกษา")

    x, right = CONSULT_COLUMN_EDGES[index], CONSULT_COLUMN_EDGES[index + 1]
    y, bottom = ROW_EDGES[0], ROW_EDGES[-1]
    return {"x": x, "y": y, "width": right - x, "height": bottom - y}


def build_consult_rich_menu() -> dict:
    """
    ใบโหมดปรึกษา — ส่งเข้า ``POST /v2/bot/richmenu`` ได้ตรง ๆ เช่นกัน

    **ห้ามตั้งเป็น default ทั้งบัญชี** (``user/all``) — ไม่งั้นคนที่ไม่ได้
    อยู่ในโหมดจะเจอปุ่ม "จบการปรึกษา" แทนเมนูจริง
    """
    return {
        "size": {"width": MENU_WIDTH, "height": MENU_HEIGHT},
        "selected": False,
        "name": CONSULT_MENU_NAME,
        "chatBarText": CONSULT_CHAT_BAR_TEXT,
        "areas": [
            {
                "bounds": consult_cell_bounds(index),
                "action": {
                    "type": "postback",
                    "label": label,
                    "data": postback_data(action),
                },
            }
            for index, (label, action) in enumerate(CONSULT_SLOTS)
        ],
    }


# ── ตรวจภาพก่อนยิง API ───────────────────────────────────────────────────────


def image_size(data: bytes) -> tuple[str, int, int]:
    """
    อ่านชนิด/ขนาดภาพจาก header เอง — ไม่ต้องพึ่ง Pillow ที่โปรเจกต์ไม่ได้ใช้

    ตรวจจาก **magic bytes ไม่ใช่นามสกุล**: ไฟล์ ``.png`` ที่จริงเป็น JPEG
    จะถูกอัปโหลดด้วย Content-Type ผิดแล้ว LINE ตอบ 415

    >>> png = b'\\x89PNG\\r\\n\\x1a\\n' + b'x' * 8 + struct.pack('>II', 2500, 1686)
    >>> image_size(png)
    ('image/png', 2500, 1686)
    >>> image_size(b'GIF89a')
    Traceback (most recent call last):
    ValueError: รับได้แค่ PNG กับ JPEG (ตรวจจาก magic bytes ไม่ใช่นามสกุล)
    """
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return "image/png", width, height

    if data[:2] == b"\xff\xd8":
        offset = 2
        # ต้องอ่านได้ครบ 9 ไบต์จาก offset (marker 2 + length 2 + precision 1 +
        # สูง 2 + กว้าง 2) — ใช้ ``offset + 9 <= len(data)`` ไม่ใช่ ``len - 9``
        # ไม่งั้นพลาด SOF ที่อยู่ท้ายสุดพอดี
        while offset + 9 <= len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            # SOF0-3 / SOF5-7 / SOF9-11 = เฟรมที่เก็บขนาดภาพไว้ข้างใน
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB):
                height, width = struct.unpack(">HH", data[offset + 5 : offset + 9])
                return "image/jpeg", width, height
            offset += 2 + struct.unpack(">H", data[offset + 2 : offset + 4])[0]
        raise ValueError("ไฟล์ JPEG ไม่มี SOF marker — ไฟล์เสียหรือไม่ใช่ JPEG")

    raise ValueError("รับได้แค่ PNG กับ JPEG (ตรวจจาก magic bytes ไม่ใช่นามสกุล)")


def image_problems(data: bytes) -> tuple[str, list[str]]:
    """
    คืน ``(mime, ปัญหาที่เจอ)`` — ลิสต์ว่าง = ใช้ได้

    ตรวจให้ครบ **ก่อน** ยิง API เพราะการสร้างเมนูจำกัด 100 ครั้ง/ชั่วโมง
    และเมนูที่อัปโหลดภาพผิดไปแล้วแก้ภาพไม่ได้ ต้องสร้างใหม่ทิ้งของเก่า

    >>> image_problems(b'\\x89PNG\\r\\n\\x1a\\n' + b'x' * 8 + struct.pack('>II', 1200, 810))
    ('image/png', [])
    """
    mime, width, height = image_size(data)
    problems: list[str] = []

    if len(data) > MAX_IMAGE_BYTES:
        problems.append(f"ไฟล์ {len(data):,} ไบต์ เกิน 1 MB ({MAX_IMAGE_BYTES:,})")
    if not MIN_WIDTH <= width <= MAX_WIDTH:
        problems.append(f"กว้าง {width} px ต้องอยู่ระหว่าง {MIN_WIDTH}-{MAX_WIDTH}")
    if height < MIN_HEIGHT:
        problems.append(f"สูง {height} px ต้องไม่น้อยกว่า {MIN_HEIGHT}")
    if height and width / height < MIN_RATIO:
        problems.append(f"อัตราส่วน {width / height:.3f} ต้องไม่น้อยกว่า {MIN_RATIO}")
    if (width, height) != (MENU_WIDTH, MENU_HEIGHT):
        problems.append(
            f"ขนาด {width}x{height} ไม่ตรงกับพิกัดปุ่มที่คำนวณไว้สำหรับ "
            f"{MENU_WIDTH}x{MENU_HEIGHT} — ปุ่มจะไม่ตรงกับรูปที่ผู้ใช้เห็น"
        )

    return mime, problems
