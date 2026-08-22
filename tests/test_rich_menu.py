"""
เทสนิยาม Rich Menu — ตรวจได้โดยไม่ต้องมี token และไม่ต้องมีไฟล์ภาพ

สิ่งที่เทสนี้ยึดไว้:

* ทุกช่องบนเมนู **มี handler รองรับจริง** (กดแล้วต้องไม่ได้ fallback)
* ทุกช่องพา ``src=rich`` ไปด้วย ไม่งั้น ``chat_logs`` แยก Rich Menu กับ
  Quick Reply ไม่ออก แล้วเคลมยอดกดในธีสิสไม่ได้
* **ลำดับช่องตรงกับภาพ** และพิกัดปุ่มไม่พาดป้ายชื่อของการ์ดข้างเคียง
* ไม่ละเมิด limit ของ LINE (areas ≤20, label ≤20, data ≤300, chatBarText ≤14)
"""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from app import router as bot_router
from app.line import messages as msg
from app.line import rich_menu as rm

MENU = rm.build_rich_menu()
CONSULT_MENU = rm.build_consult_rich_menu()
MENU_IMAGE = Path(__file__).resolve().parent.parent / "assets" / "rich_menu.png"
CONSULT_IMAGE = Path(__file__).resolve().parent.parent / "assets" / "rich_menu_consult.png"


def _png(width: int, height: int, padding: int = 0) -> bytes:
    """PNG ปลอมที่มีแค่ header พอให้ ``image_size`` อ่านขนาดได้"""
    return (
        b"\x89PNG\r\n\x1a\n"
        + b"x" * 8
        + struct.pack(">II", width, height)
        + b"\x00" * padding
    )


# ── นิยามเมนู ────────────────────────────────────────────────────────────────


def test_menu_has_six_slots_within_line_limits() -> None:
    assert len(MENU["areas"]) == len(rm.SLOTS) == 6
    assert len(MENU["areas"]) <= 20, "LINE รับ areas ได้สูงสุด 20 ช่อง"
    assert len(MENU["name"]) <= 300
    assert len(MENU["chatBarText"]) <= 14, "chatBarText เกิน 14 ตัวอักษร LINE ปฏิเสธ"
    assert MENU["selected"] is False, "true จะบังหน้าจอแชททันทีตอนเปิดแชท"


def test_every_slot_action_has_a_router_handler() -> None:
    """
    ปุ่มบนเมนูที่ไม่มี handler = ผู้ใช้กดปุ่มของเราเองแล้วได้ "ไม่เข้าใจคำถาม"

    เป็นบั๊กที่แพงเพราะแก้ภาพเมนูที่อัปโหลดไปแล้วไม่ได้ ต้องสร้างเมนูใหม่
    """
    for _, action in rm.SLOTS:
        assert action in bot_router.POSTBACK_HANDLERS, action


def test_every_slot_is_tagged_as_coming_from_the_rich_menu() -> None:
    for area in MENU["areas"]:
        data = area["action"]["data"]
        params = bot_router.parse_postback_data(data)
        assert params["src"] == "rich", data
        assert bot_router._answer_surface(params) == "rich_menu", data


def test_slot_labels_and_data_fit_line_limits() -> None:
    for area in MENU["areas"]:
        action = area["action"]
        assert action["type"] == "postback"
        assert len(action["label"]) <= msg.MAX_LABEL_LENGTH, action["label"]
        assert len(action["data"]) <= msg.MAX_POSTBACK_DATA_LENGTH, action["data"]


def test_plan_and_liff_are_deliberately_left_out() -> None:
    """
    ``plan`` ตอบว่า "ยังจัดแผนรายเทอมให้ไม่ได้" ทุกครั้ง (รอ มคอ.2) และ
    หน้า LIFF ยังไม่มีอยู่จริง — ช่องที่กดแล้วผิดหวังทุกครั้งสอนผู้ใช้ว่า
    เมนูนี้ไม่ต้องกด เอากลับเข้ามาเมื่อข้อมูล/หน้าเว็บพร้อมแล้วเท่านั้น
    """
    actions = {action for _, action in rm.SLOTS}
    assert "plan" not in actions
    assert not any(action.startswith("liff") for action in actions)


def test_slot_order_matches_the_artwork() -> None:
    """
    **ภาพเป็นเจ้าของลำดับ ไม่ใช่โค้ด** — ``assets/rich_menu.png`` วางการ์ดไว้ว่า
    แถวบน = ปรึกษา AI / กู้ยืม / ติดต่ออาจารย์ แถวล่าง = ค้นรายวิชา / เอกสาร /
    ทำอะไรได้บ้าง

    เคยพลาดจริงมาแล้ว: นิยามในโค้ดเขียนไว้ก่อนได้ภาพ พอได้ภาพมาช่อง 1 กับ 5
    สลับที่กัน → กด "ปรึกษา AI" ได้รายการเอกสาร และ **LINE ไม่ฟ้องอะไรเลย**
    เพราะพิกัดถูกต้องตามสเปกทุกข้อ เทสนี้บังคับให้การสลับลำดับต้องเป็นความตั้งใจ
    """
    assert rm.SLOTS == (
        ("ปรึกษา AI", "ai_session"),
        ("กู้ยืม กยศ.", "loan"),
        ("ติดต่ออาจารย์", "instructors"),
        ("ค้นรายวิชา", "course"),
        ("เอกสาร/คำร้อง", "documents"),
        ("ทำอะไรได้บ้าง", "menu"),
    )


# ── พิกัดปุ่ม ────────────────────────────────────────────────────────────────


def test_cells_tile_the_card_area_without_gaps_or_overlap() -> None:
    """
    ร่องที่กดไม่ติดระหว่างการ์ด = ผู้ใช้กดแล้วคิดว่าบอทค้าง, ทับกัน = กดช่องหนึ่ง
    ได้คำตอบอีกช่อง ทั้งสองอย่างผู้ใช้เจอเองบนหน้าจอ แต่ API ไม่ฟ้อง
    """
    covered: set[tuple[int, int]] = set()
    total = 0

    for area in MENU["areas"]:
        bounds = area["bounds"]
        total += bounds["width"] * bounds["height"]
        cell = (bounds["x"], bounds["y"])
        assert cell not in covered, f"มีสองช่องเริ่มที่จุดเดียวกัน {cell}"
        covered.add(cell)
        assert bounds["x"] + bounds["width"] <= rm.MENU_WIDTH, bounds
        assert bounds["y"] + bounds["height"] <= rm.MENU_HEIGHT, bounds

    card_height = rm.ROW_EDGES[-1] - rm.ROW_EDGES[0]
    assert total == rm.MENU_WIDTH * card_height, "ช่องต้องปูเต็มพื้นที่การ์ดพอดี"


def test_the_title_and_footer_bands_are_deliberately_not_tappable() -> None:
    """
    แถบ "เมนูหลัก" ด้านบนกับแถบชวนพิมพ์ด้านล่างเป็นของประดับ — แตะแล้วเงียบ
    ดีกว่าแตะหัวเรื่องแล้วเด้งคำตอบที่ไม่ได้สั่ง

    และเส้นแบ่งแถวต้องอยู่ใน**ร่องระหว่างการ์ด** (วัดจากภาพได้ที่ y=459-464)
    ถ้าปูเต็มภาพแบบหาร 2 จะได้ y=405 ซึ่งพาดกลางป้ายชื่อของการ์ดแถวบน
    (การ์ดแถวบนจบที่ y=458) → แตะคำว่า "ปรึกษา AI" ได้คำตอบของ "ค้นรายวิชา"
    """
    tops = {area["bounds"]["y"] for area in MENU["areas"]}
    bottoms = {area["bounds"]["y"] + area["bounds"]["height"] for area in MENU["areas"]}

    assert min(tops) == rm.ROW_EDGES[0] > 0, "แถบหัวเรื่องต้องไม่ถูกครอบ"
    assert max(bottoms) == rm.ROW_EDGES[-1] < rm.MENU_HEIGHT, "แถบท้ายต้องไม่ถูกครอบ"
    assert 459 <= rm.ROW_EDGES[1] <= 465, "เส้นแบ่งแถวหลุดออกจากร่องระหว่างการ์ด"


def test_bounds_are_integers() -> None:
    """พิกัดที่เป็น float จะถูกส่งเป็นทศนิยมใน JSON แล้ว LINE ปฏิเสธทั้งก้อน"""
    for area in MENU["areas"]:
        for value in area["bounds"].values():
            assert isinstance(value, int), area["bounds"]


def test_cell_bounds_rejects_index_outside_the_grid() -> None:
    with pytest.raises(ValueError):
        rm.cell_bounds(6)


# ── ตรวจภาพ ─────────────────────────────────────────────────────────────────


def test_image_of_the_right_size_passes() -> None:
    mime, problems = rm.image_problems(_png(rm.MENU_WIDTH, rm.MENU_HEIGHT))

    assert mime == "image/png"
    assert problems == []


def test_the_shipped_menu_image_matches_the_layout() -> None:
    """
    ภาพต้นฉบับต้องอยู่ใน repo และขนาดต้องตรงกับพิกัดปุ่มเป๊ะ

    ผิดไปแม้ pixel เดียวปุ่มก็เลื่อนจากที่ผู้ใช้เห็น และ **เปลี่ยนภาพของเมนูที่
    อัปโหลดไปแล้วไม่ได้** ต้องสร้างเมนูใหม่ทั้งใบแล้วลบของเก่า (จำกัด 100 ครั้ง/ชม.)
    """
    assert MENU_IMAGE.exists(), f"ไม่พบภาพต้นฉบับ {MENU_IMAGE}"

    mime, problems = rm.image_problems(MENU_IMAGE.read_bytes())

    assert mime == "image/png"
    assert problems == []


def test_image_problems_reports_every_violation_at_once() -> None:
    """
    บอกครบทุกข้อในรอบเดียว — คนทำภาพจะได้แก้ทีเดียวจบ ไม่ใช่แก้แล้วรันแล้ว
    เจออีกข้อ (สร้างเมนูได้ 100 ครั้ง/ชั่วโมงเท่านั้น)
    """
    _, problems = rm.image_problems(_png(700, 700))

    assert len(problems) == 3
    assert any("กว้าง 700" in text for text in problems)
    assert any("อัตราส่วน 1.000" in text for text in problems)
    assert any("ไม่ตรงกับพิกัดปุ่ม" in text for text in problems)


def test_image_over_one_megabyte_is_rejected() -> None:
    oversize = _png(rm.MENU_WIDTH, rm.MENU_HEIGHT, padding=rm.MAX_IMAGE_BYTES)
    _, problems = rm.image_problems(oversize)

    assert any("เกิน 1 MB" in text for text in problems)


def test_jpeg_size_is_read_from_the_sof_marker() -> None:
    jpeg = (
        b"\xff\xd8"
        + b"\xff\xe0" + struct.pack(">H", 4) + b"\x00\x00"      # APP0 ที่ต้องข้าม
        + b"\xff\xc0" + struct.pack(">H", 11) + b"\x08"
        + struct.pack(">HH", 1686, 2500)
    )
    assert rm.image_size(jpeg) == ("image/jpeg", 2500, 1686)


def test_other_formats_are_rejected_by_magic_bytes_not_extension() -> None:
    with pytest.raises(ValueError, match="PNG กับ JPEG"):
        rm.image_size(b"GIF89a" + b"\x00" * 20)


# ── ใบโหมดปรึกษา (สลับตามโหมด) ─────────────────────────────────────────────


def test_consult_menu_has_two_slots_with_real_handlers() -> None:
    """
    คนในโหมดต้องการแค่ "ทางออก" กับ "ทางกลับ" — ปุ่มอื่นชวนเผลอออกโหมด
    ทั้งสอง action ต้องมีใน ``POSTBACK_HANDLERS`` อยู่แล้ว (ai_end/menu)
    """
    assert len(CONSULT_MENU["areas"]) == len(rm.CONSULT_SLOTS) == 2
    assert len(CONSULT_MENU["areas"]) <= 20
    assert len(CONSULT_MENU["name"]) <= 300
    assert len(CONSULT_MENU["chatBarText"]) <= 14
    assert CONSULT_MENU["selected"] is False
    for _, action in rm.CONSULT_SLOTS:
        assert action in bot_router.POSTBACK_HANDLERS, action


def test_consult_slots_match_the_artwork() -> None:
    """
    ภาพ ``assets/rich_menu_consult.png`` วาง "จบการปรึกษา" ไว้ซ้าย
    "เมนูหลัก" ไว้ขวา — สลับสองบรรทัดในโค้ดโดยไม่วาดภาพใหม่
    = ปุ่มตอบผิดช่องทั้งใบ
    """
    assert rm.CONSULT_SLOTS == (
        ("จบการปรึกษา", "ai_end"),
        ("เมนูหลัก", "menu"),
    )


def test_consult_slots_are_tagged_rich_menu() -> None:
    for area in CONSULT_MENU["areas"]:
        params = bot_router.parse_postback_data(area["action"]["data"])
        assert params["src"] == "rich", area["action"]["data"]
        assert bot_router._answer_surface(params) == "rich_menu"


def test_consult_slots_split_the_card_zone_in_half() -> None:
    """
    แบ่งโซนการ์ดของใบปรึกษา (y=164..729 วัดจาก artwork) เป็นสองครึ่งพอดี —
    ไม่ทับ ไม่ล้ำแถบหัว/ท้าย และเส้นแบ่งอยู่กลางร่องระหว่างการ์ด (x=600)
    """
    left, right = (area["bounds"] for area in CONSULT_MENU["areas"])
    assert left["x"] == 0 and right["x"] == rm.MENU_WIDTH // 2
    assert left["x"] + left["width"] == right["x"], "ช่องซ้ายต้องชนช่องขวาพอดี"
    assert right["x"] + right["width"] == rm.MENU_WIDTH
    for bounds in (left, right):
        assert bounds["y"] == rm.CONSULT_ROW_EDGES[0]
        assert bounds["y"] + bounds["height"] == rm.CONSULT_ROW_EDGES[-1]


def test_consult_cell_bounds_rejects_bad_index() -> None:
    with pytest.raises(ValueError):
        rm.consult_cell_bounds(2)


def test_consult_menu_is_not_a_default_menu() -> None:
    """
    docstring ของ :func:`build_consult_rich_menu` ห้ามตั้งเป็น ``user/all`` —
    ตรวจจากนิยาม: ``selected`` ต้อง False เสมอ (การสลับใช้ per-user link)
    """
    assert CONSULT_MENU["selected"] is False


def test_shipped_consult_image_passes_line_limits() -> None:
    """ภาพใบปรึกษาต้องอยู่ใน repo + ผ่าน ``image_problems`` ทุกข้อ"""
    assert CONSULT_IMAGE.exists(), f"ไม่พบภาพ {CONSULT_IMAGE}"
    mime, problems = rm.image_problems(CONSULT_IMAGE.read_bytes())
    assert mime == "image/png"
    assert problems == []
