"""
อัปเดต Rich Menu ให้ตรงกับโค้ดล่าสุด — คำสั่งเดียวจบ ใช้หลัง ``git pull``

**ทำไมต้องมีสคริปต์นี้**: เมนูไม่ได้อยู่ใน git แต่อยู่บนเซิร์ฟเวอร์ LINE
``git pull`` จึงไม่ทำให้เมนูที่ผู้ใช้เห็นอัปเดตตาม และ LINE **แก้ภาพของใบที่
อัปโหลดไปแล้วไม่ได้** ต้องสร้างใบใหม่แล้วตั้งเป็น default ทุกครั้ง
``scripts/rich_menu.py`` ทำสามขั้นนั้นได้ แต่ไม่บอกว่า "ใบที่คนเห็นอยู่ตอนนี้
เก่าหรือยัง" และปล่อยใบเก่าค้างบน channel ทุกครั้งที่อัปเดต

    python scripts/update_rich_menu.py --dry-run     # เทียบของเดิมกับของใหม่ ไม่แก้อะไร
    python scripts/update_rich_menu.py               # อัปเดตจริง (ถามยืนยันก่อน)
    python scripts/update_rich_menu.py --yes         # อัปเดตจริง ไม่ถาม
    python scripts/update_rich_menu.py --check       # ตรวจอย่างเดียว (exit 0 = ตรงแล้ว)
    python scripts/update_rich_menu.py --prune --yes # เก็บกวาดใบเก่าที่ค้างทั้งหมด

เครื่องที่ลง Docker ล้วน (ไม่มี python/httpx บน host):

    docker compose run --rm tools scripts/update_rich_menu.py --dry-run

ลำดับการทำงาน

1. อ่านเมนู default ปัจจุบัน (ใบที่ผู้ใช้ทุกคนเห็น) มาเทียบกับ
   :func:`app.line.rich_menu.build_rich_menu` ของโค้ดตอนนี้ — เทียบชื่อ
   ข้อความแถบเมนู ลำดับช่อง/ข้อมูล postback และ **md5 ของภาพ** ที่ LINE เก็บไว้
   (ยืนยันกับ API จริงแล้วว่า LINE คืนภาพไบต์เดิมเป๊ะ จึงเทียบ md5 ได้)
2. ตรงอยู่แล้ว = ไม่ทำอะไร · ไม่ตรง = หาใบที่ตรงอยู่แล้วบน channel มาใช้ ถ้าไม่มี
   จึงสร้างใบใหม่ → อัปโหลดภาพ → ตั้ง default → ลบใบเก่าที่เพิ่งถูกแทนที่
3. ``--prune`` ลบใบเก่าที่ค้างทั้งหมดที่ชื่อเดียวกับเมนูหลัก (ใบโหมดปรึกษาและ
   เมนูที่ตั้งชื่ออื่นไม่ถูกแตะ)

ผู้ใช้จะเห็นเมนูใหม่ **ตอนเปิดแชทครั้งถัดไป** (อาจช้าถึง ~1 นาที) และ
**Rich Menu ไม่ขึ้นบน LINE for PC** ต้องดูบนมือถือ
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
# ให้ import ได้ทั้งตอนรันตรง ๆ (``python scripts/update_rich_menu.py``)
# และตอนเทส import เป็น ``scripts.update_rich_menu``
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

from rich_menu import (  # noqa: E402
    API,
    API_DATA,
    DEFAULT_IMAGE,
    api_client,
    check_image,
    create_menu,
    delete_menu,
    expect_ok,
    set_default,
    upload_image,
)

from app.config import get_settings  # noqa: E402
from app.line.rich_menu import MENU_NAME, build_rich_menu  # noqa: E402


# ── เทียบเมนูสองใบ (ไม่ต้องมี token ก็เทสได้) ────────────────────────────────


def slot_data(menu: dict) -> list[str]:
    """ข้อมูล postback ของทุกช่องตามลำดับ — ลายนิ้วมือของเมนูใบหนึ่ง"""
    return [area.get("action", {}).get("data", "") for area in menu.get("areas", [])]


def slot_labels(menu: dict) -> list[str]:
    """ป้ายชื่อช่องตามลำดับ (ใบที่ไม่มี label จะโชว์ data แทน)"""
    labels = []
    for area in menu.get("areas", []):
        action = area.get("action", {})
        labels.append(action.get("label") or action.get("data", "?"))
    return labels


def label_map(menu: dict) -> dict[str, str]:
    """data → ป้ายชื่อ ใช้แปลผลต่างให้เป็นข้อความที่อ่านออก"""
    return {
        area.get("action", {}).get("data", ""): area.get("action", {}).get("label", "")
        for area in menu.get("areas", [])
    }


def differences(current: dict, expected: dict) -> list[str]:
    """
    รายการที่เมนู ``current`` ต่างจาก ``expected`` (ลิสต์ว่าง = ตรงกันแล้ว)

    เทียบจาก ``data`` ไม่ใช่ ``label`` เพราะ ``data`` คือสิ่งที่ router เอาไป
    ทำงานจริง — ป้ายเปลี่ยนแต่ data เดิม = เมนูทำงานเหมือนเดิม ไม่ต้องเสียโควตา
    สร้างใบใหม่ (LINE ให้สร้าง/ลบได้ 100 ครั้ง/ชั่วโมง)

    >>> def mk(label, data):
    ...     return {"areas": [{"action": {"label": label, "data": data}}]}
    >>> old = mk("กู้ยืม กยศ.", "action=loan&src=rich")
    >>> new = mk("วางแผนเกรด", "action=grade_plan&src=rich")
    >>> for line in differences(old, new):
    ...     print(line)
    ช่องไม่ตรง — ตอนนี้: กู้ยืม กยศ.
    ช่องที่ต้องเป็น: วางแผนเกรด
    ช่องที่ยังขาด: วางแผนเกรด
    ช่องที่ต้องเอาออก: กู้ยืม กยศ.
    >>> differences(new, new)
    []
    """
    problems: list[str] = []

    if current.get("size") != expected.get("size"):
        problems.append(
            f"ขนาดไม่ตรง — ตอนนี้: {current.get('size')} ต้องเป็น: {expected['size']}"
        )
    if current.get("name") != expected.get("name"):
        problems.append(
            f"ชื่อเมนูไม่ตรง — ตอนนี้: {current.get('name')!r}"
            f" ต้องเป็น: {expected['name']!r}"
        )
    if current.get("chatBarText") != expected.get("chatBarText"):
        problems.append(
            "ข้อความแถบเมนูไม่ตรง — ตอนนี้: "
            f"{current.get('chatBarText')!r} ต้องเป็น: {expected['chatBarText']!r}"
        )

    old_data, new_data = slot_data(current), slot_data(expected)
    if old_data != new_data:
        problems.append("ช่องไม่ตรง — ตอนนี้: " + " | ".join(slot_labels(current)))
        problems.append("ช่องที่ต้องเป็น: " + " | ".join(slot_labels(expected)))
        names = {**label_map(current), **label_map(expected)}
        missing = [names.get(data, data) for data in new_data if data not in old_data]
        extra = [names.get(data, data) for data in old_data if data not in new_data]
        if missing:
            problems.append("ช่องที่ยังขาด: " + ", ".join(missing))
        if extra:
            problems.append("ช่องที่ต้องเอาออก: " + ", ".join(extra))

    return problems


# ── อ่านสถานะจริงจาก LINE (ใช้ helpers ตัวเดียวกับ scripts/rich_menu.py) ─────


def current_default_id(client) -> str | None:
    """id ของเมนู default ทั้งบัญชี — ``None`` = channel นี้ยังไม่เคยตั้งเมนู"""
    response = client.get(f"{API}/user/all/richmenu")
    if response.status_code == 404:
        # 404 = ยังไม่ตั้ง default ไม่ใช่ error (LINE ตอบแบบนี้ทั้งที่ token ถูก)
        return None
    return expect_ok(response).get("richMenuId")


def fetch_menu(client, menu_id: str) -> dict:
    """นิยามเมนูตามที่ LINE เก็บไว้ (ชื่อ/แถบเมนู/ช่อง)"""
    return expect_ok(client.get(f"{API}/richmenu/{menu_id}"))


def remote_image_md5(client, menu_id: str) -> str | None:
    """md5 ของภาพที่ LINE เก็บไว้ — ``None`` = อ่านไม่ได้ (ถือว่าไม่ตรง)"""
    response = client.get(f"{API_DATA}/richmenu/{menu_id}/content")
    if response.status_code != 200:
        return None
    return hashlib.md5(response.content).hexdigest()


def find_matching_menu(client, expected: dict, image_md5: str) -> str | None:
    """
    หาใบที่ "ตรงกับโค้ดแล้ว" ซึ่งมีอยู่บน channel แล้ว เพื่อตั้งเป็น default
    แทนการสร้างใบซ้ำ — channel ที่อัปเดตมาหลายรอบมักมีใบซ้ำค้างอยู่

    ตรวจชื่อ + ช่องก่อน แล้วค่อยขอภาพมาเทียบ md5 (ยิงขอภาพเฉพาะใบที่ผ่านสองด่านแรก)
    """
    response = client.get(f"{API}/richmenu/list")
    for item in expect_ok(response).get("richmenus", []):
        if item.get("name") != expected.get("name"):
            continue
        if slot_data(item) != slot_data(expected):
            continue
        if remote_image_md5(client, item["richMenuId"]) == image_md5:
            return item["richMenuId"]
    return None


def leftover_main_menus(client, keep_ids: set[str]) -> list[dict]:
    """
    ใบที่ชื่อเดียวกับเมนูหลักและไม่ได้ถูกใช้อยู่ — ของค้างจากรอบอัปเดตก่อน ๆ

    จำกัดที่ชื่อเมนูหลักโดยเจตนา: ใบโหมดปรึกษากับเมนูทดลองที่ตั้งชื่ออื่น
    จะไม่ถูกแตะแม้สั่ง ``--prune``
    """
    response = client.get(f"{API}/richmenu/list")
    return [
        item
        for item in expect_ok(response).get("richmenus", [])
        if item["richMenuId"] not in keep_ids and item.get("name") == MENU_NAME
    ]


def keep_ids(new_id: str | None) -> set[str]:
    """id ที่ห้ามลบ: ใบที่เพิ่งตั้งเป็น default + ใบโหมดปรึกษาที่ตั้งไว้ใน .env"""
    ids = {new_id} - {None}
    consult_id = get_settings().rich_menu_consult_id
    if consult_id:
        ids.add(consult_id)
    return ids


def confirm() -> bool:
    """
    ยืนยันก่อนแก้ของจริง — stdin ไม่ใช่ terminal (รันผ่าน pipe/สคริปต์)
    จะปฏิเสธพร้อมบอกให้ใส่ ``--yes`` ดีกว่าเดาว่าผู้ใช้ตอบว่าอะไร
    """
    if not sys.stdin.isatty():
        print("stdin ไม่ใช่ terminal จึงไม่ถามยืนยัน — ใส่ --yes ถ้าต้องการอัปเดตจริง")
        return False
    return input("อัปเดตเมนูเป็นใบใหม่? [y/N] ").strip().lower() in {"y", "yes", "ใช่"}


# ── main ───────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="อัปเดต Rich Menu ให้ตรงกับ build_rich_menu() ของโค้ดตอนนี้",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=None,
        help="ไฟล์ภาพเมนู (ไม่ส่ง = assets/rich_menu.png)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="เทียบ + พิมพ์แผน แต่ไม่แก้ของจริง"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="ไม่แก้ · exit 0 = ตรงแล้ว, exit 1 = ล้าสมัย (ใช้ในสคริปต์/CI ได้)",
    )
    parser.add_argument("--yes", action="store_true", help="ไม่ต้องถามยืนยัน")
    parser.add_argument(
        "--force", action="store_true", help="สร้างใบใหม่เสมอ แม้ตรวจว่าเมนูตรงกับโค้ดแล้ว"
    )
    parser.add_argument(
        "--keep-old", action="store_true", help="ไม่ลบใบเก่าที่เพิ่งถูกแทนที่"
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="ลบใบเก่าที่ค้างทั้งหมดที่ชื่อเดียวกับเมนูหลัก (ไม่แตะใบโหมดปรึกษา)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    image = args.image or DEFAULT_IMAGE

    expected = build_rich_menu()
    data, mime = check_image(image)  # ตรวจภาพให้ครบก่อนยิง API เสมอ
    local_md5 = hashlib.md5(data).hexdigest()

    with api_client() as client:
        default_id = current_default_id(client)
        current = fetch_menu(client, default_id) if default_id else None
        remote_md5 = remote_image_md5(client, default_id) if default_id else None

        print()
        print(f"เมนู default ตอนนี้: {default_id or '(ยังไม่มี)'}")
        if current:
            print(f"   ชื่อ : {current.get('name')}")
            print(f"   ช่อง : {' | '.join(slot_labels(current))}")
            print(f"   ภาพ  : {remote_md5 or 'อ่านไม่ได้'}")
        print(f"เมนูที่โค้ดต้องการ  : {expected['name']}")
        print(f"   ช่อง : {' | '.join(slot_labels(expected))}")
        print(f"   ภาพ  : {local_md5}  ({image})")
        print()

        problems = differences(current, expected) if current else [
            "ยังไม่มีเมนู default บน channel นี้"
        ]
        if current and remote_md5 != local_md5:
            problems.append("ภาพไม่ตรง — ไฟล์ในเครื่องไม่เหมือนภาพที่ LINE เก็บไว้")

        if problems:
            print("ยังไม่ตรงกับโค้ด:")
            for line in problems:
                print(f"   - {line}")
        elif not args.force:
            print("เมนูตรงกับโค้ดแล้ว — ไม่ต้องทำอะไร")

        if args.check:
            # 0 = ตรงแล้ว, 1 = ต้องอัปเดต (ให้เอาไปต่อในสคริปต์ได้)
            if problems:
                print("→ make rich-menu-update")
                return 1
            return 0

        if not problems and not args.force:
            return 0  # --dry-run จบตรงนี้เหมือนกัน

        # ไม่ต้องสร้างใบซ้ำถ้ามีใบที่ตรงอยู่แล้วค้างบน channel
        # --force = ผู้ใช้สั่งให้สร้างใหม่จริง ๆ จึงข้ามการหาใบเดิมบน channel
        reuse = None if args.force else find_matching_menu(client, expected, local_md5)
        print("แผนที่จะทำ:")
        if reuse:
            print(f"   • ตั้ง default เป็นใบที่มีอยู่แล้ว {reuse} (ไม่สร้างใบซ้ำ)")
        else:
            print("   • สร้างใบใหม่ → อัปโหลดภาพ → ตั้งเป็น default")
        if default_id and not args.keep_old:
            print(f"   • ลบใบเก่า {default_id}")
        if args.prune:
            print("   • ลบใบเก่าที่ค้างทั้งหมดที่ชื่อเดียวกับเมนูหลัก")

        if args.dry_run:
            print("(dry-run) ไม่แก้ของจริง")
            return 0

        if not args.yes and not confirm():
            print("ยกเลิก — ไม่ได้แก้อะไรบน LINE")
            return 1

        new_id = reuse
        if reuse is None:
            new_id = create_menu(client, expected)
            upload_image(client, new_id, data, mime)
        if new_id != default_id:
            set_default(client, new_id)
        else:
            print("3/3 เป็น default อยู่แล้ว")

        keep = keep_ids(new_id)
        if default_id and default_id not in keep and not args.keep_old:
            delete_menu(client, default_id)

        leftovers = leftover_main_menus(client, keep)
        if args.prune:
            for item in leftovers:
                delete_menu(client, item["richMenuId"])
        elif leftovers:
            print(
                f"มีใบเก่าค้างบน channel อีก {len(leftovers)} ใบ — "
                "ใส่ --prune รอบถัดไปเพื่อเก็บกวาด"
            )

        print("เปิดแชทใหม่บนมือถือเพื่อดู (อาจช้าถึง 1 นาที · ไม่ขึ้นบน LINE for PC)")
    return 0


if __name__ == "__main__":
    sys.exit(main())