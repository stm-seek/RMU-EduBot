"""
สร้าง / อัปโหลด / ตั้ง Rich Menu บน LINE

    python scripts/rich_menu.py --dry-run                 # ดู JSON + ตรวจภาพ
    python scripts/rich_menu.py                           # ลงจริง (ใช้ภาพใน assets/)
    python scripts/rich_menu.py --image path/to/menu.png   # ลงจริงด้วยภาพอื่น
    python scripts/rich_menu.py --list
    python scripts/rich_menu.py --delete richmenu-xxxx

ลำดับ 3 ขั้นบังคับตามเอกสาร LINE (ข้ามขั้นไหนก็ error):

1. ``POST api.line.me/v2/bot/richmenu``                    → ได้ ``richMenuId``
2. ``POST api-data.line.me/v2/bot/richmenu/{id}/content``   ← **โดเมนต่างกัน**
3. ``POST api.line.me/v2/bot/user/all/richmenu/{id}``       ตั้งเป็นเมนู default

**เปลี่ยนภาพของเมนูที่อัปโหลดแล้วไม่ได้** ต้องสร้างเมนูใหม่ทุกครั้งที่แก้ภาพ
→ สคริปต์นี้จึงมี ``--list`` / ``--delete`` มาให้เก็บกวาดของเก่า
(สร้าง/ลบ จำกัด 100 ครั้ง/ชั่วโมง — เหลือเฟือสำหรับงานนี้)

ผู้ใช้จะเห็นเมนูใหม่ **ตอนเปิดแชทครั้งถัดไป** อาจช้าได้ถึง 1 นาที
และ **Rich Menu ไม่ขึ้นบน LINE for PC** ต้องทดสอบบนมือถือ
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.line.rich_menu import build_rich_menu, image_problems  # noqa: E402

API = "https://api.line.me/v2/bot"
API_DATA = "https://api-data.line.me/v2/bot"

# ภาพต้นฉบับเก็บไว้ใน repo เพราะพิกัดปุ่มใน app/line/rich_menu.py วัดมาจากไฟล์นี้
# ทำภาพหายแล้วเลขพิกัดจะตรวจย้อนไม่ได้
DEFAULT_IMAGE = REPO_ROOT / "assets" / "rich_menu.png"


def check_image(path: Path) -> tuple[bytes, str]:
    """
    ตรวจภาพให้ครบทุกข้อจำกัด **ก่อน** ยิง API (กติกาอยู่ที่ app/line/rich_menu.py)
    """
    if not path.exists():
        raise SystemExit(f"ไม่พบไฟล์ภาพ {path}")

    data = path.read_bytes()
    try:
        mime, problems = image_problems(data)
    except ValueError as exc:
        raise SystemExit(f"ภาพใช้ไม่ได้: {exc}") from exc

    if problems:
        raise SystemExit("ภาพใช้ไม่ได้:\n  - " + "\n  - ".join(problems))

    print(f"ภาพผ่าน: {mime} {len(data):,} ไบต์")
    return data, mime


# ── ยิง API ─────────────────────────────────────────────────────────────────


def _client():
    """httpx client ที่ใส่ token ให้แล้ว — **ห้าม print ตัว token**"""
    import httpx

    from app.config import get_settings

    settings = get_settings()
    token = settings.line_channel_access_token
    if not token:
        raise SystemExit(
            "ยังไม่ได้ตั้ง LINE_CHANNEL_ACCESS_TOKEN ใน .env — ยิง API ไม่ได้"
        )
    return httpx.Client(
        headers={"Authorization": f"Bearer {token}"}, timeout=30.0
    )


def _ok(response) -> dict:
    if response.status_code != 200:
        raise SystemExit(
            f"LINE ตอบ {response.status_code}: {response.text[:400]}"
        )
    return response.json() if response.content else {}


def create_menu(client, menu: dict) -> str:
    body = _ok(client.post(f"{API}/richmenu", json=menu))
    menu_id = body["richMenuId"]
    print(f"1/3 สร้างเมนูแล้ว: {menu_id}")
    return menu_id


def upload_image(client, menu_id: str, data: bytes, mime: str) -> None:
    _ok(
        client.post(
            f"{API_DATA}/richmenu/{menu_id}/content",
            content=data,
            headers={"Content-Type": mime},
        )
    )
    print(f"2/3 อัปโหลดภาพแล้ว ({len(data):,} ไบต์)")


def set_default(client, menu_id: str) -> None:
    _ok(client.post(f"{API}/user/all/richmenu/{menu_id}"))
    print("3/3 ตั้งเป็นเมนู default ของทุกคนแล้ว")


def list_menus(client) -> None:
    for item in _ok(client.get(f"{API}/richmenu/list")).get("richmenus", []):
        size = item.get("size", {})
        print(
            f"{item['richMenuId']}  {size.get('width')}x{size.get('height')}"
            f"  areas={len(item.get('areas', []))}  {item.get('name', '')}"
        )


def delete_menu(client, menu_id: str) -> None:
    _ok(client.delete(f"{API}/richmenu/{menu_id}"))
    print(f"ลบ {menu_id} แล้ว")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE,
        help=f"ไฟล์ภาพเมนู (PNG/JPEG) — ไม่ส่งมาใช้ {DEFAULT_IMAGE.name} ใน assets/",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="พิมพ์ JSON + ตรวจภาพ ไม่ยิง API"
    )
    parser.add_argument(
        "--no-default",
        action="store_true",
        help="สร้าง+อัปโหลดแต่ยังไม่ตั้งเป็น default (ผู้ใช้จะยังไม่เห็น)",
    )
    parser.add_argument("--list", action="store_true", help="ดูเมนูที่มีอยู่บน LINE")
    parser.add_argument("--delete", metavar="RICHMENU_ID", help="ลบเมนูตาม id")
    args = parser.parse_args()

    menu = build_rich_menu()

    if args.dry_run:
        print(json.dumps(menu, ensure_ascii=False, indent=2))
        check_image(args.image)
        return

    with _client() as client:
        if args.list:
            list_menus(client)
            return
        if args.delete:
            delete_menu(client, args.delete)
            return

        data, mime = check_image(args.image)
        menu_id = create_menu(client, menu)
        upload_image(client, menu_id, data, mime)
        if args.no_default:
            print("ข้ามขั้นที่ 3 ตามที่สั่ง — ตั้ง default ภายหลังด้วย --list แล้วดู id")
        else:
            set_default(client, menu_id)
            print("เปิดแชทใหม่บนมือถือเพื่อดู (อาจช้าถึง 1 นาที · ไม่ขึ้นบน PC)")


if __name__ == "__main__":
    main()
