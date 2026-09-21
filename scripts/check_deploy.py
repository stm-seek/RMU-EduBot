"""
ตรวจว่า **บอทที่ให้บริการจริง** ตรงกับโค้ดในโฟลเดอร์นี้หรือยัง

ใช้หลัง ``git pull``: การดึงโค้ดไม่ทำให้บอทที่ LINE คุยด้วยอัปเดต เพราะ image
คัดลอก ``app/`` ตอน build (ไม่มี bind mount) ต้องสั่ง
``docker compose up -d --build app`` ก่อน สคริปต์นี้จึงตอบคำถามเดียวว่า
"ตอนนี้ container เสิร์ฟโค้ดเวอร์ชันไหน" โดยไม่ต้องเดาจากหน้าจอ LINE

    python scripts/check_deploy.py        # หรือ make deploy

ทำสามอย่าง
1. เทียบ md5 ของ ``app/router.py`` ในคอนเทนเนอร์กับไฟล์ในโฟลเดอร์นี้
2. พิมพ์ข้อความ + ปุ่มที่บอทตอบจริงของ 3 หัวข้อที่เคยมีปัญหา (ขาดอีกกี่หน่วยกิต /
   ขาดวิชาเรียนอะไรบ้าง / คำนวณเกรด) โดยดึงจากโค้ด *ในคอนเทนเนอร์*
3. ออกด้วยรหัส 1 ถ้าโค้ดไม่ตรง — เอาไปต่อในสคริปต์ได้

ถ้าไม่พบคอนเทนเนอร์ = เครื่องนี้รันบอทบน host (``python run.py``) การแก้โค้ด
มีผลทันทีเมื่อรีสตาร์ต process
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CODE_FILE = "app/router.py"
CONTAINER_HINT = "rmu_bot_app"
INSIDE_SCRIPT = "/tmp/check_deploy_inside.py"

# หัวข้อที่เคยเจอปัญหาจริง: ข้อความในไฟล์ถูกแก้แล้วแต่บอทที่ LINE คุยด้วย
# ยังเสิร์ฟโค้ดชุดเก่า (ดู docs/dev-guide/08-pitfalls.md §8.2)
TOPICS = ("missing_credits", "missing_courses", "grade_plan")


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    """รันคำสั่ง docker — คืน stdout/stderr เป็นข้อความ ไม่ throw"""
    return subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )


def find_container() -> str | None:
    """id ของ container แอป — ถาม compose ก่อน แล้วค่อยหาด้วยชื่อ"""
    result = _run(["docker", "compose", "ps", "-q", "app"])
    if result.stdout.strip():
        return result.stdout.split()[0]

    result = _run(["docker", "ps", "--filter", f"name={CONTAINER_HINT}", "-q"])
    return result.stdout.split()[0] if result.stdout.strip() else None


def local_digest() -> str:
    return hashlib.md5((REPO_ROOT / CODE_FILE).read_bytes()).hexdigest()


def container_digest(container: str) -> str | None:
    result = _run(["docker", "exec", container, "md5sum", f"/app/{CODE_FILE}"])
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.split()[0]


def print_screens(container: str) -> None:
    """รันสคริปต์นี้ซ้ำในคอนเทนเนอร์ เพื่อดูข้อความที่บอทตอบจริง"""
    copied = _run(
        ["docker", "cp", str(Path(__file__).resolve()), f"{container}:{INSIDE_SCRIPT}"]
    )
    if copied.returncode != 0:
        print("ข้ามการตรวจข้อความ: คัดลอกสคริปต์เข้า container ไม่ได้")
        return

    result = _run(
        [
            "docker", "exec",
            "-e", "PYTHONPATH=/app",
            "-e", "PYTHONUTF8=1",
            container, "python", INSIDE_SCRIPT, "--screens",
        ]
    )
    print((result.stdout or result.stderr).strip())
    # ลบไฟล์ชั่วคราว (คัดลอกด้วย root จึงต้องลบด้วย root)
    _run(["docker", "exec", "-u", "root", container, "rm", "-f", INSIDE_SCRIPT])


def screens() -> int:
    """โหมดในคอนเทนเนอร์: พิมพ์ข้อความ + ปุ่มของหัวข้อที่เคยมีปัญหา"""
    import asyncio
    from app import router

    async def show() -> None:
        for action in TOPICS:
            result = await router.handle_postback(f"action={action}", None)
            message = result.messages[0]
            chips = [
                item["action"].get("label")
                for item in message.get("quickReply", {}).get("items", [])
            ]
            lines = (message.get("text") or "").strip().splitlines()
            print(f"— {action} ({result.answered_by})")
            print("   ปุ่ม:", " | ".join(chip for chip in chips if chip))
            print(f"   ท้ายข้อความ: {lines[-1] if lines else '(ว่าง)'}")

    asyncio.run(show())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--screens",
        action="store_true",
        help="ใช้ภายในคอนเทนเนอร์เท่านั้น (เรียกโดยไม่ต้องส่ง container)",
    )
    args = parser.parse_args(argv)
    if args.screens:
        return screens()

    container = find_container()
    if container is None:
        print("ไม่พบ container ของแอป (rmu_bot_app)")
        print(
            "→ เครื่องนี้รันบอทบน host: โค้ดใหม่มีผลทันที "
            "แต่ต้องรีสตาร์ต `python run.py`"
        )
        print("→ ถ้าต้องการรันแบบ container: docker compose up -d --build")
        return 1

    print(f"container: {container[:12]}")
    expected, actual = local_digest(), container_digest(container)
    if actual is None:
        print(f"อ่าน /app/{CODE_FILE} ในคอนเทนเนอร์ไม่ได้ — ตรวจ image เอง")
        return 1
    if actual != expected:
        print(f"โค้ดในคอนเทนเนอร์ไม่ตรงกับโฟลเดอร์นี้ ({CODE_FILE})")
        print(f"   ในคอนเทนเนอร์: {actual}")
        print(f"   ในโฟลเดอร์   : {expected}")
        print("   → docker compose up -d --build app   (แก้โค้ดแล้วต้อง build ใหม่)")
        return 1

    print(f"โค้ดตรงกัน ({CODE_FILE}) — container เสิร์ฟเวอร์ชันล่าสุด")
    print()
    print("ข้อความที่บอทตอบจริงตอนนี้ (ดึงจากในคอนเทนเนอร์):")
    print_screens(container)
    return 0


if __name__ == "__main__":
    sys.exit(main())
