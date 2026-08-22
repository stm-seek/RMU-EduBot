"""
สร้างภาพ Rich Menu ใบโหมดปรึกษา (assets/rich_menu_consult.png)

เรียกซ้ำได้:

    set PYTHONUTF8=1
    python scripts/make_consult_image.py            # วาดภาพ
    python scripts/make_consult_image.py --check    # ตรวจว่าภาพที่มียังใช้ได้

โทนสี/โครงยึดจาก ``assets/rich_menu.png`` ใบหลัก (navy #012D71 + การ์ดเด่น)
เพื่อให้ทั้งสองใบดูเป็นชุดเดียวกัน:

* แถบหัว (y<133) และแถบท้าย (y≥758) เป็นแถบเจตนาไม่ให้กดเหมือนใบหลัก
* โซนการ์ด 2 ปุ่มอยู่ที่ y=133..758 พอดีกับ ``CONSULT_SLOTS`` ใน
  ``app/line/rich_menu.py`` — **เปลี่ยนเลขตรงนี้ต้องแก้ที่นั่นด้วย**
* ปุ่ม "จบการปรึกษา" ใช้สีส้ม (สีเด่นของใบหลัก = สีของ "ทางไปต่อ")
  ปุ่ม "เมนูหลัก" ใช้สีน้ำเงินสว่างรอง

ข้อจำกัดของ LINE ที่สคริปต์นี้เคารพ (ตรวจด้วย ``image_problems``):
PNG, 1200x810 เป๊ะ, ขนาดไฟล์ < 1 MB
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "assets" / "rich_menu_consult.png"

# ── โทนจากใบหลัก (วัดสีจาก assets/rich_menu.png จริง) ────────────────────────
NAVY = (1, 45, 113)          # พื้นทั้งใบ
NAVY_DARK = (2, 19, 80)      # การ์ด "ปรึกษา AI" ในใบหลัก — ใช้แถบหัวให้ตัดกันน้อย
CARD_ORANGE = (244, 166, 50) # ปุ่มเด่นในใบหลัก (เอกสาร/คำร้อง)
CARD_BLUE = (195, 216, 234)  # ปุ่มรองในใบหลัก (ค้นรายวิชา)
WHITE = (253, 253, 254)
TEXT_DARK = (7, 32, 76)

# โซนการ์ด — ต้องตรงกับ CONSULT_COLUMN_EDGES / ROW_EDGES ใน app/line/rich_menu.py
CARD_TOP, CARD_BOTTOM = 133, 758
MID_X = 600

FONT_BOLD = r"C:\Windows\Fonts\leelauib.ttf"   # Leelawadee UI Bold (มีในเครื่อง)
FONT_REGULAR = r"C:\Windows\Fonts\leelawui.ttf"  # Leelawadee UI Regular


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def _center_text(draw, center_xy, text: str, font, fill) -> None:
    """เขียนข้อความกึ่งกลางจุด (รองรับ 2 บรรทัดด้วย \\n)"""
    cx, cy = center_xy
    lines = text.split("\n")
    sizes = [_text_size(draw, line, font) for line in lines]
    line_gap = 14
    total_h = sum(h for _, h in sizes) + line_gap * (len(lines) - 1)
    y = cy - total_h // 2
    for line, (w, h) in zip(lines, sizes):
        draw.text((cx - w // 2, y), line, font=font, fill=fill)
        y += h + line_gap


def build() -> Image.Image:
    image = Image.new("RGB", (1200, 810), NAVY)
    draw = ImageDraw.Draw(image)

    # ── แถบหัว (เจตนาไม่ให้กด) ──────────────────────────────────────────────
    draw.rectangle((0, 0, 1199, CARD_TOP - 1), fill=NAVY_DARK)
    _center_text(
        draw, (600, CARD_TOP // 2), "โหมดปรึกษา AI", _font(56), WHITE
    )

    # ── แถบท้าย (เจตนาไม่ให้กด) ─────────────────────────────────────────────
    draw.rectangle((0, CARD_BOTTOM, 1199, 809), fill=NAVY_DARK)
    _center_text(
        draw,
        (600, (CARD_BOTTOM + 810) // 2),
        "พิมพ์คำถามต่อได้เลย",
        _font(30, bold=False),
        WHITE,
    )

    # ── การ์ด 2 ปุ่ม (โซนกดได้ y=133..758) ─────────────────────────────────
    cards = (
        # (ขอบเขต, สีการ์ด, ข้อความ, สีตัวอักษร)
        ((0, CARD_TOP, MID_X, CARD_BOTTOM), CARD_ORANGE, "จบการปรึกษา", TEXT_DARK),
        ((MID_X, CARD_TOP, 1200, CARD_BOTTOM), CARD_BLUE, "เมนูหลัก", TEXT_DARK),
    )
    label_font = _font(52)
    hint_font = _font(28, bold=False)
    for (x0, y0, x1, y1), color, label, text_color in cards:
        draw.rectangle((x0, y0, x1 - 1, y1 - 1), fill=color)
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        _center_text(draw, (cx, cy - 30), label, label_font, text_color)
        hint = "(ปิดโหมด)" if label == "จบการปรึกษา" else "(เปิดเมนูหลัก)"
        _center_text(draw, (cx, cy + 60), hint, hint_font, text_color)

    return image


def check(path: Path = OUT_PATH) -> list[str]:
    """ตรวจภาพที่มีอยู่ด้วยกฎเดียวกันกับตอนอัปโหลดจริง"""
    sys.path.insert(0, str(REPO_ROOT))
    from app.line.rich_menu import image_problems

    data = path.read_bytes()
    _, problems = image_problems(data)
    if not problems:
        problems = []
    size_kb = path.stat().st_size / 1024
    print(f"{path.name}: {size_kb:.0f} KB — {'ผ่าน' if not problems else 'ไม่ผ่าน'}")
    return problems


def main() -> None:
    if "--check" in sys.argv:
        problems = check()
        if problems:
            for problem in problems:
                print("  -", problem)
            sys.exit(1)
        return

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image = build()
    # optimize ให้เล็กสุดเท่าที่ PNG ทำได้ — ต้อง < 1 MB ตามกฎ LINE
    image.save(OUT_PATH, format="PNG", optimize=True)

    problems = check()
    if problems:
        for problem in problems:
            print("  -", problem)
        sys.exit(1)
    print(f"สร้างแล้ว: {OUT_PATH}")


if __name__ == "__main__":
    main()
