"""
ตรวจ syntax ไฟล์ SQL ด้วย sqlglot (parse แบบ dialect=postgres)

ใช้เมื่อยังไม่มี Postgres ให้ต่อจริง — จับ syntax error ได้ก่อน deploy
**ไม่ใช่การทดแทนการรันจริง** ตัวนี้ไม่ตรวจ FK / constraint / extension

รันด้วย::

    python -m db.validate_sql
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import sqlglot
from sqlglot.errors import ParseError

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILES = [
    REPO_ROOT / "db" / "migrations" / "001_init.sql",
    REPO_ROOT / "db" / "migrations" / "002_ai_sessions.sql",
    REPO_ROOT / "db" / "migrations" / "003_answered_by_values.sql",
    REPO_ROOT / "db" / "migrations" / "004_chat_log_status.sql",
    REPO_ROOT / "db" / "migrations" / "005_planner.sql",
    REPO_ROOT / "db" / "migrations" / "006_admin.sql",
    REPO_ROOT / "db" / "migrations" / "007_answered_by_faq.sql",
    REPO_ROOT / "db" / "migrations" / "008_admin_accounts.sql",
    REPO_ROOT / "db" / "migrations" / "009_ai_prompt_rules.sql",
    REPO_ROOT / "db" / "seed" / "002_seed_data.sql",
    REPO_ROOT / "db" / "seed" / "003_curriculum_rules.sql",
]


def check_file(path: Path) -> tuple[int, list[str]]:
    """คืน (จำนวน statement ที่ parse ผ่าน, ลิสต์ error)"""
    sql = path.read_text(encoding="utf-8")
    errors: list[str] = []
    parsed = 0

    try:
        statements = sqlglot.parse(sql, dialect="postgres")
    except ParseError as exc:
        return 0, [f"parse ทั้งไฟล์ล้มเหลว: {exc}"]

    for statement in statements:
        if statement is None:
            continue
        parsed += 1

    # ── sanity check เชิงความหมายที่ sqlglot ไม่ตรวจ ─────────────────────────
    lowered = sql.lower()

    if "begin;" in lowered and "commit;" not in lowered:
        errors.append("มี BEGIN แต่ไม่มี COMMIT")

    # นับวงเล็บว่าสมดุล (จับกรณี string ไทยทำให้วงเล็บเพี้ยน)
    if sql.count("(") != sql.count(")"):
        errors.append(
            f"วงเล็บไม่สมดุล: '(' = {sql.count('(')}, ')' = {sql.count(')')}"
        )

    # single quote ต้องเป็นเลขคู่ (escape เป็น '' นับเป็น 2 ตัวอยู่แล้ว)
    if sql.count("'") % 2 != 0:
        errors.append(f"single quote เป็นเลขคี่ ({sql.count(chr(39))}) — อาจ escape พลาด")

    return parsed, errors


def summarize(path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    kinds: dict[str, int] = {}
    for match in re.finditer(
        r"^\s*(CREATE TABLE|CREATE INDEX|CREATE EXTENSION|INSERT INTO|COMMENT ON|ALTER TABLE)",
        sql,
        re.I | re.M,
    ):
        key = " ".join(match.group(1).upper().split())
        kinds[key] = kinds.get(key, 0) + 1
    for kind, count in sorted(kinds.items()):
        print(f"      {kind:<18} {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ตรวจ syntax ไฟล์ SQL")
    parser.add_argument("files", nargs="*", type=Path, default=None)
    args = parser.parse_args()

    files = args.files or DEFAULT_FILES
    total_errors = 0

    for path in files:
        if not path.exists():
            print(f"  ! ไม่พบ {path}")
            total_errors += 1
            continue

        parsed, errors = check_file(path)
        rel = path.relative_to(REPO_ROOT).as_posix()
        size_kb = path.stat().st_size / 1024
        status = "OK" if not errors else f"พบ {len(errors)} ปัญหา"
        print(f"\n  {rel}  ({size_kb:.0f} KB, {parsed} statements)  {status}")
        summarize(path)

        for error in errors:
            print(f"      ! {error}")
        total_errors += len(errors)

    print()
    if total_errors:
        print(f"พบปัญหารวม {total_errors} รายการ")
        sys.exit(1)
    print("syntax ผ่านทุกไฟล์")
    print("หมายเหตุ: ยังต้องรันบน Postgres จริงเพื่อตรวจ FK / constraint / extension")


if __name__ == "__main__":
    main()
