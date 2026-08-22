#!/usr/bin/env python3
"""
นำเข้า ``db/seed/003_curriculum_rules.sql`` (แผนการเรียนมาตรฐาน) ลง Postgres

รันด้วย::

    python scripts/import_curriculum_rules.py
    python scripts/import_curriculum_rules.py --file db/seed/003_curriculum_rules.sql

**ห้ามแยก statement ด้วย ``split(";")``** — เคยทำแล้วเสียข้อมูลเงียบ ๆ:
คอมเมนต์หัวไฟล์ไปติดอยู่กับ INSERT ตัวแรก (คอมเมนต์ไม่มี ``;`` ปิด) แล้วโค้ด
ที่กรอง ``startswith("--")`` ก็ทิ้งทั้งก้อน → หายไป 1 วิชา (1209903-1)
เข้าไป 31 แถวแต่รายงานว่าสำเร็จ psycopg ส่งหลาย statement ในครั้งเดียวได้
(เมื่อไม่มี parameter) จึงส่งทั้งไฟล์ไปเลย ให้ Postgres แยกเอง
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "app"))

import psycopg  # noqa: E402
from config import Settings  # noqa: E402

# psycopg คุม transaction เองแล้ว — ส่ง BEGIN/COMMIT ซ้ำจะได้
# "syntax error at or near COMMIT" (เจอจริงมาแล้ว)
TRANSACTION_KEYWORDS = re.compile(r"^\s*(BEGIN|COMMIT|ROLLBACK)\s*;\s*$", re.MULTILINE | re.IGNORECASE)


def strip_transaction_control(sql: str) -> str:
    """
    ตัด BEGIN/COMMIT ที่อยู่ **บรรทัดของตัวเอง** ออก

    >>> strip_transaction_control("BEGIN;\nINSERT INTO t VALUES (1);\nCOMMIT;\n").split()
    ['INSERT', 'INTO', 't', 'VALUES', '(1);']
    """
    return TRANSACTION_KEYWORDS.sub("", sql)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        type=Path,
        default=REPO_ROOT / "db" / "seed" / "003_curriculum_rules.sql",
    )
    parser.add_argument("--program", default="643170151")
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="ไม่ลบแถวเดิมของหลักสูตรนี้ก่อน (ปกติลบ เพื่อไม่ให้เหลือวิชาที่ถอดออกจากแผนแล้ว)",
    )
    args = parser.parse_args()

    sql = strip_transaction_control(args.file.read_text(encoding="utf-8"))
    settings = Settings()

    with psycopg.connect(settings.database_url) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM curriculum_rules WHERE program_code = %s", (args.program,)
        )
        before = cur.fetchone()[0]
        print(f"ก่อนนำเข้า: {before} แถว")

        if before and not args.keep_existing:
            cur.execute(
                "DELETE FROM curriculum_rules WHERE program_code = %s", (args.program,)
            )
            print(f"ลบแถวเดิม {cur.rowcount} แถว")

        cur.execute(sql)

        cur.execute(
            """
            SELECT std_year, std_semester, count(*) AS courses
            FROM curriculum_rules
            WHERE program_code = %s
            GROUP BY std_year, std_semester
            ORDER BY std_year, std_semester
            """,
            (args.program,),
        )
        rows = cur.fetchall()
        conn.commit()

    total = sum(row[2] for row in rows)
    print(f"\nนำเข้าแล้ว {total} แถว")
    print("ปี  เทอม  จำนวนวิชา")
    for year, semester, courses in rows:
        print(f"{year:<4}{semester:<6}{courses}")

    # จำนวนวิชาในไฟล์ต้องเท่ากับในตาราง — กันบั๊กแบบ 32→31 ซ้ำรอย
    in_file = len(re.findall(rf"\('{re.escape(args.program)}',", sql))
    if in_file != total:
        print(f"\n!! ไฟล์มี {in_file} วิชา แต่เข้าตาราง {total} แถว — ไม่ตรงกัน", file=sys.stderr)
        return 1
    print(f"\nตรงกับไฟล์ ({in_file} วิชา)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
