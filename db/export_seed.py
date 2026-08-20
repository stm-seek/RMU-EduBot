"""
Export ข้อมูลจาก SQLite knowledge base เป็นไฟล์ ``.sql`` สำหรับ Postgres

ทำไมต้องมีขั้นนี้ (ไม่ต่อ Postgres ตรง ๆ):

* ได้ไฟล์ SQL ที่ **อ่านได้ ตรวจได้ commit ได้** → แนบเป็นภาคผนวกในธีสิสได้
* deploy ที่ไหนก็ ``psql -f`` ได้เลย ไม่ต้องมี Python/scraper บนเครื่องนั้น
* ไม่ต้องรัน scraper ซ้ำตอน deploy (เว็บ RMU ล่มบ่อย ยิงซ้ำเสี่ยงพลาด)

รันด้วย::

    python -m db.export_seed                     # เขียน db/seed/002_seed_data.sql
    python -m db.export_seed --stdout            # พิมพ์ออกจอ

ผลลัพธ์เป็น idempotent — ใช้ ``ON CONFLICT DO UPDATE`` ทุกตาราง
รันซ้ำได้ไม่พัง และอัปเดตค่าให้เป็นของใหม่
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = REPO_ROOT / "kb" / "data" / "rmu_kb.db"
OUTPUT_FILE = REPO_ROOT / "db" / "seed" / "002_seed_data.sql"


# ── ตัวช่วยแปลงค่าเป็น SQL literal ───────────────────────────────────────────


def sql_value(value, *, as_bool: bool = False, as_json: bool = False) -> str:
    """
    แปลงค่า Python เป็น SQL literal ที่ปลอดภัย

    >>> sql_value(None)
    'NULL'
    >>> sql_value(42)
    '42'
    >>> sql_value("O'Brien")
    "'O''Brien'"
    >>> sql_value(1, as_bool=True)
    'TRUE'
    >>> sql_value('', as_bool=True)
    'FALSE'
    """
    if value is None or value == "":
        # ค่าว่างของคอลัมน์ bool ต้องเป็น FALSE ไม่ใช่ NULL (มี NOT NULL)
        return "FALSE" if as_bool else "NULL"

    if as_bool:
        return "TRUE" if int(value) else "FALSE"

    if as_json:
        if isinstance(value, str):
            # ค่าใน SQLite เก็บเป็น JSON string อยู่แล้ว — validate ก่อน
            json.loads(value)
            text = value
        else:
            text = json.dumps(value, ensure_ascii=False)
        return "'" + text.replace("'", "''") + "'::jsonb"

    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)

    return "'" + str(value).replace("'", "''") + "'"


def sql_text_array(items: list[str]) -> str:
    """
    แปลง list เป็น Postgres text[]

    >>> sql_text_array([])
    "'{}'::text[]"
    >>> sql_text_array(['ดรอปเรียน', 'ลาพัก'])
    "ARRAY['ดรอปเรียน','ลาพัก']::text[]"
    """
    if not items:
        return "'{}'::text[]"
    inner = ",".join("'" + item.replace("'", "''") + "'" for item in items)
    return f"ARRAY[{inner}]::text[]"


# ── นิยามการ export ต่อ 1 ตาราง ─────────────────────────────────────────────
#
# (ตาราง, คอลัมน์, คอลัมน์ที่เป็น conflict target, คอลัมน์ bool, คอลัมน์ json)
TABLE_SPECS: list[tuple[str, list[str], list[str], set[str], set[str]]] = [
    (
        "programs",
        [
            "program_id", "faculty_id", "level_id", "program_code", "program_name",
            "faculty_name", "level_name", "degree_name", "department_name",
            "total_credits", "source_url", "scraped_at",
        ],
        ["program_id"],
        set(),
        set(),
    ),
    (
        "categories",
        [
            "program_id", "row_id", "parent_row_id", "number", "depth", "label",
            "required_credits", "is_leaf", "selection_mode",
        ],
        ["program_id", "row_id"],
        {"is_leaf"},
        set(),
    ),
    (
        "courses",
        [
            "course_id", "course_code", "name_th", "name_en", "credits_text",
            "credits", "description_th", "faculty_text", "source_url", "scraped_at",
        ],
        ["course_id"],
        set(),
        set(),
    ),
    (
        "program_courses",
        ["program_id", "category_row_id", "course_id", "position"],
        ["program_id", "category_row_id", "course_id"],
        set(),
        set(),
    ),
    (
        "offerings",
        [
            "course_id", "course_code", "acad_year", "semester", "section",
            "course_group", "schedule_raw", "instructors", "seats_total",
            "seats_taken", "seats_left", "status", "source_url", "scraped_at",
        ],
        ["course_id", "acad_year", "semester", "section", "schedule_raw"],
        set(),
        set(),
    ),
    (
        "offering_patterns",
        [
            "course_code", "opens_sem1", "opens_sem2", "opens_sem3",
            "terms_observed", "terms_found", "detail", "computed_at",
        ],
        ["course_code"],
        {"opens_sem1", "opens_sem2", "opens_sem3"},
        {"detail"},
    ),
    (
        "documents",
        [
            "category", "title", "url", "doc_type", "audience", "keywords", "note",
            "source_page", "http_status", "content_type", "content_length",
            "is_available", "checked_at", "scraped_at",
        ],
        ["url"],
        {"is_available"},
        set(),
    ),
    (
        "instructors",
        [
            "full_name", "name_normalized", "title_prefix", "email", "phone",
            "building", "floor", "room", "office_hours", "other_contact",
            "manual_source", "source_url", "scraped_at",
        ],
        ["full_name"],
        set(),
        set(),
    ),
    (
        "prerequisites",
        ["program_code", "course_code", "requires_code", "kind", "source", "updated_at"],
        ["program_code", "course_code", "requires_code"],
        set(),
        set(),
    ),
    (
        "curriculum_rules",
        [
            "program_code", "course_code", "std_year", "std_semester",
            "is_fixed_term", "note", "source", "verified_by", "updated_at",
        ],
        ["program_code", "course_code"],
        {"is_fixed_term"},
        set(),
    ),
]


def emit_table(
    conn: sqlite3.Connection,
    table: str,
    columns: list[str],
    conflict: list[str],
    bools: set[str],
    jsons: set[str],
    out,
) -> int:
    """เขียน INSERT ... ON CONFLICT DO UPDATE ของตารางหนึ่ง"""
    available = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
    missing = [c for c in columns if c not in available]
    if missing:
        print(f"  ! {table}: ไม่มีคอลัมน์ {missing} ใน SQLite — ข้าม", file=sys.stderr)
        return 0

    rows = conn.execute(
        f"SELECT {', '.join(columns)} FROM {table}"
    ).fetchall()
    if not rows:
        out.write(f"\n-- {table}: ไม่มีข้อมูล (ข้าม)\n")
        return 0

    updatable = [c for c in columns if c not in conflict]
    out.write(f"\n-- ── {table} ({len(rows)} แถว) ")
    out.write("─" * max(0, 58 - len(table)) + "\n")

    for row in rows:
        values = []
        for column in columns:
            values.append(
                sql_value(
                    row[column],
                    as_bool=column in bools,
                    as_json=column in jsons,
                )
            )
        out.write(
            f"INSERT INTO {table} ({', '.join(columns)})\n"
            f"VALUES ({', '.join(values)})\n"
        )
        if updatable:
            sets = ",\n    ".join(f"{c} = EXCLUDED.{c}" for c in updatable)
            out.write(
                f"ON CONFLICT ({', '.join(conflict)}) DO UPDATE SET\n    {sets};\n"
            )
        else:
            out.write(f"ON CONFLICT ({', '.join(conflict)}) DO NOTHING;\n")

    return len(rows)


def emit_affiliations(conn: sqlite3.Connection, out) -> int:
    """
    instructor_affiliations อ้าง instructor_id ที่เป็น autoincrement
    → id ฝั่ง Postgres ไม่ตรงกับ SQLite ต้อง lookup ด้วย full_name แทน
    """
    rows = conn.execute(
        """
        SELECT i.full_name, a.group_name, a.group_code, a.position, a.is_chair
          FROM instructor_affiliations a
          JOIN instructors i ON i.id = a.instructor_id
         ORDER BY i.full_name, a.group_name
        """
    ).fetchall()
    if not rows:
        return 0

    out.write(f"\n-- ── instructor_affiliations ({len(rows)} แถว) ")
    out.write("─" * 30 + "\n")
    out.write("-- ใช้ SELECT id FROM instructors WHERE full_name = ...\n")
    out.write("-- เพราะ instructor_id เป็น IDENTITY ค่าจึงไม่ตรงกับฝั่ง SQLite\n")

    for row in rows:
        out.write(
            "INSERT INTO instructor_affiliations "
            "(instructor_id, group_name, group_code, position, is_chair)\n"
            "SELECT i.id, "
            f"{sql_value(row['group_name'])}, "
            f"{sql_value(row['group_code'])}, "
            f"{sql_value(row['position'])}, "
            f"{sql_value(row['is_chair'], as_bool=True)}\n"
            f"  FROM instructors i WHERE i.full_name = {sql_value(row['full_name'])}\n"
            "ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET\n"
            "    group_code = EXCLUDED.group_code,\n"
            "    is_chair   = EXCLUDED.is_chair;\n"
        )
    return len(rows)


def emit_slots(conn: sqlite3.Connection, out) -> int:
    """
    offering_slots อ้าง offering_id (IDENTITY) เช่นกัน
    → lookup ผ่าน natural key ของ offerings
    """
    rows = conn.execute(
        """
        SELECT o.course_id, o.acad_year, o.semester, o.section, o.schedule_raw,
               s.day_code, s.start_min, s.end_min, s.room
          FROM offering_slots s
          JOIN offerings o ON o.id = s.offering_id
         ORDER BY o.course_code, o.section, s.day_code, s.start_min
        """
    ).fetchall()
    if not rows:
        return 0

    out.write(f"\n-- ── offering_slots ({len(rows)} แถว) ")
    out.write("─" * 36 + "\n")
    out.write("-- lookup offering_id จาก natural key (course_id, ปี, เทอม, หมู่, ตาราง)\n")

    for row in rows:
        out.write(
            "INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)\n"
            "SELECT o.id, "
            f"{sql_value(row['day_code'])}, "
            f"{sql_value(row['start_min'])}, "
            f"{sql_value(row['end_min'])}, "
            f"{sql_value(row['room'])}\n"
            "  FROM offerings o\n"
            f" WHERE o.course_id = {sql_value(row['course_id'])}\n"
            f"   AND o.acad_year = {sql_value(row['acad_year'])}\n"
            f"   AND o.semester = {sql_value(row['semester'])}\n"
            f"   AND o.section = {sql_value(row['section'])}\n"
            f"   AND o.schedule_raw = {sql_value(row['schedule_raw'])}\n"
            "  AND NOT EXISTS (\n"
            "      SELECT 1 FROM offering_slots x\n"
            "       WHERE x.offering_id = o.id\n"
            f"         AND x.day_code = {sql_value(row['day_code'])}\n"
            f"         AND x.start_min = {sql_value(row['start_min'])}\n"
            "  );\n"
        )
    return len(rows)


def export(out) -> dict[str, int]:
    if not SQLITE_DB.exists():
        raise SystemExit(
            f"ไม่พบ {SQLITE_DB}\nรัน scraper ก่อน: python -m kb.scrape_programs ..."
        )

    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    counts: dict[str, int] = {}

    try:
        out.write("-- " + "=" * 74 + "\n")
        out.write("--  Seed data — สร้างอัตโนมัติจาก kb/data/rmu_kb.db\n")
        out.write("--  ห้ามแก้ไฟล์นี้ด้วยมือ ให้แก้ที่ scraper แล้ว export ใหม่\n")
        out.write(f"--  สร้างเมื่อ: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")
        out.write("--\n")
        out.write("--  ต้องรัน 001_init.sql ก่อน\n")
        out.write("--  รันซ้ำได้ (idempotent ผ่าน ON CONFLICT)\n")
        out.write("-- " + "=" * 74 + "\n\n")
        out.write("BEGIN;\n")

        for table, columns, conflict, bools, jsons in TABLE_SPECS:
            counts[table] = emit_table(
                conn, table, columns, conflict, bools, jsons, out
            )

        counts["instructor_affiliations"] = emit_affiliations(conn, out)
        counts["offering_slots"] = emit_slots(conn, out)

        out.write("\nCOMMIT;\n")
    finally:
        conn.close()

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export SQLite knowledge base เป็น Postgres seed SQL"
    )
    parser.add_argument("--stdout", action="store_true", help="พิมพ์ออกจอแทนเขียนไฟล์")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    args = parser.parse_args()

    if args.stdout:
        counts = export(sys.stdout)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as handle:
            counts = export(handle)

        size_kb = args.output.stat().st_size / 1024
        rel = args.output.relative_to(REPO_ROOT)
        print(f"เขียน {rel} ({size_kb:.0f} KB)\n")
        for table, count in counts.items():
            marker = "" if count else "   <-- ว่าง"
            print(f"  {table:<26} {count:>5} แถว{marker}")
        print(f"\n  รวม {sum(counts.values())} แถว")
        print(f"\nนำเข้าด้วย:\n  psql $DATABASE_URL -f {rel.as_posix()}")


if __name__ == "__main__":
    main()
