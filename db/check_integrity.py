"""
ตรวจ integrity ของ seed data *ก่อน* นำเข้า Postgres

sqlglot ตรวจได้แค่ syntax — ตัวนี้ตรวจสิ่งที่จะทำให้ ``psql -f`` ล้มเหลวจริง:

* FK ชี้ไปหาแถวที่ไม่มี  (offerings.course_id → courses)
* CHECK constraint ไม่ผ่าน (semester 1-3, day_code, start_min 0-1439)
* ลำดับ INSERT ผิด (insert ลูกก่อนแม่)
* UNIQUE ซ้ำ

รันด้วย::

    python -m db.check_integrity
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = REPO_ROOT / "kb" / "data" / "rmu_kb.db"
SEED_FILE = REPO_ROOT / "db" / "seed" / "002_seed_data.sql"

VALID_DAYS = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}
VALID_KINDS = {"hard", "soft", "concurrent"}
VALID_MODES = {"required", "elective", None, ""}
VALID_AUDIENCE = {"student", "staff"}
VALID_STATUS = {"ok", "partial", "error"}


def check_data(conn: sqlite3.Connection) -> list[str]:
    """ตรวจข้อมูลใน SQLite ว่าจะผ่าน constraint ของ Postgres หรือไม่"""
    problems: list[str] = []

    def q(sql: str) -> list[sqlite3.Row]:
        return conn.execute(sql).fetchall()

    # ── FK integrity ────────────────────────────────────────────────────────
    orphans = q(
        """
        SELECT COUNT(*) AS n FROM offerings o
         WHERE NOT EXISTS (SELECT 1 FROM courses c WHERE c.course_id = o.course_id)
        """
    )[0]["n"]
    if orphans:
        problems.append(f"offerings มี course_id ที่ไม่มีใน courses: {orphans} แถว")

    orphans = q(
        """
        SELECT COUNT(*) AS n FROM program_courses pc
         WHERE NOT EXISTS (SELECT 1 FROM courses c WHERE c.course_id = pc.course_id)
        """
    )[0]["n"]
    if orphans:
        problems.append(f"program_courses มี course_id กำพร้า: {orphans} แถว")

    orphans = q(
        """
        SELECT COUNT(*) AS n FROM program_courses pc
         WHERE NOT EXISTS (
             SELECT 1 FROM programs p WHERE p.program_id = pc.program_id)
        """
    )[0]["n"]
    if orphans:
        problems.append(f"program_courses มี program_id กำพร้า: {orphans} แถว")

    orphans = q(
        """
        SELECT COUNT(*) AS n FROM categories c
         WHERE NOT EXISTS (
             SELECT 1 FROM programs p WHERE p.program_id = c.program_id)
        """
    )[0]["n"]
    if orphans:
        problems.append(f"categories มี program_id กำพร้า: {orphans} แถว")

    # categories.parent_row_id ต้องมีอยู่จริงในหลักสูตรเดียวกัน
    bad = q(
        """
        SELECT COUNT(*) AS n FROM categories c
         WHERE c.parent_row_id IS NOT NULL
           AND NOT EXISTS (
               SELECT 1 FROM categories p
                WHERE p.program_id = c.program_id AND p.row_id = c.parent_row_id)
        """
    )[0]["n"]
    if bad:
        problems.append(f"categories.parent_row_id ชี้ไปหาหมวดที่ไม่มี: {bad} แถว")

    # ── CHECK constraint ────────────────────────────────────────────────────
    bad = q("SELECT COUNT(*) AS n FROM offerings WHERE semester NOT IN (1,2,3)")[0]["n"]
    if bad:
        problems.append(f"offerings.semester อยู่นอกช่วง 1-3: {bad} แถว")

    rows = q("SELECT DISTINCT day_code FROM offering_slots WHERE day_code IS NOT NULL")
    invalid = [r["day_code"] for r in rows if r["day_code"] not in VALID_DAYS]
    if invalid:
        problems.append(f"offering_slots.day_code ไม่ถูกต้อง: {invalid}")

    bad = q(
        """
        SELECT COUNT(*) AS n FROM offering_slots
         WHERE (start_min IS NOT NULL AND (start_min < 0 OR start_min > 1439))
            OR (end_min   IS NOT NULL AND (end_min   < 0 OR end_min   > 1439))
        """
    )[0]["n"]
    if bad:
        problems.append(f"offering_slots เวลาอยู่นอกช่วง 0-1439 นาที: {bad} แถว")

    rows = q(
        "SELECT DISTINCT selection_mode FROM categories WHERE selection_mode IS NOT NULL"
    )
    invalid = [r["selection_mode"] for r in rows if r["selection_mode"] not in VALID_MODES]
    if invalid:
        problems.append(f"categories.selection_mode ไม่ถูกต้อง: {invalid}")

    rows = q("SELECT DISTINCT audience FROM documents")
    invalid = [r["audience"] for r in rows if r["audience"] not in VALID_AUDIENCE]
    if invalid:
        problems.append(f"documents.audience ไม่ถูกต้อง: {invalid}")

    bad = q(
        "SELECT COUNT(*) AS n FROM prerequisites WHERE course_code = requires_code"
    )[0]["n"]
    if bad:
        problems.append(f"prerequisites: วิชาเป็น prereq ของตัวเอง {bad} แถว")

    rows = q("SELECT DISTINCT kind FROM prerequisites")
    invalid = [r["kind"] for r in rows if r["kind"] not in VALID_KINDS]
    if invalid:
        problems.append(f"prerequisites.kind ไม่ถูกต้อง: {invalid}")

    bad = q(
        """
        SELECT COUNT(*) AS n FROM curriculum_rules
         WHERE (std_year IS NOT NULL AND (std_year < 1 OR std_year > 8))
            OR (std_semester IS NOT NULL AND (std_semester < 1 OR std_semester > 3))
        """
    )[0]["n"]
    if bad:
        problems.append(f"curriculum_rules ปี/เทอมอยู่นอกช่วง: {bad} แถว")

    # ── NOT NULL ────────────────────────────────────────────────────────────
    for table, column in [
        ("programs", "source_url"),
        ("programs", "scraped_at"),
        ("courses", "course_code"),
        ("courses", "scraped_at"),
        ("categories", "label"),
        ("categories", "depth"),
        ("documents", "url"),
        ("documents", "title"),
        ("instructors", "full_name"),
        ("instructors", "name_normalized"),
    ]:
        bad = q(
            f"SELECT COUNT(*) AS n FROM {table} "
            f"WHERE {column} IS NULL OR {column} = ''"
        )[0]["n"]
        if bad:
            problems.append(f"{table}.{column} ว่าง {bad} แถว (Postgres มี NOT NULL)")

    # ── UNIQUE ──────────────────────────────────────────────────────────────
    dup = q(
        """
        SELECT COUNT(*) AS n FROM (
            SELECT url FROM documents GROUP BY url HAVING COUNT(*) > 1)
        """
    )[0]["n"]
    if dup:
        problems.append(f"documents.url ซ้ำ {dup} ค่า")

    dup = q(
        """
        SELECT COUNT(*) AS n FROM (
            SELECT full_name FROM instructors GROUP BY full_name HAVING COUNT(*) > 1)
        """
    )[0]["n"]
    if dup:
        problems.append(f"instructors.full_name ซ้ำ {dup} ค่า")

    return problems


def check_insert_order() -> list[str]:
    """ตรวจว่าไฟล์ seed insert ตารางแม่ก่อนตารางลูก"""
    sql = SEED_FILE.read_text(encoding="utf-8")
    order: list[str] = []
    for match in re.finditer(r"INSERT INTO (\w+)", sql):
        table = match.group(1)
        if table not in order:
            order.append(table)

    # (ลูก, แม่) — ลูกต้องมาหลังแม่
    deps = [
        ("categories", "programs"),
        ("program_courses", "programs"),
        ("program_courses", "courses"),
        ("offerings", "courses"),
        ("offering_slots", "offerings"),
        ("instructor_affiliations", "instructors"),
    ]

    problems = []
    for child, parent in deps:
        if child in order and parent in order:
            if order.index(child) < order.index(parent):
                problems.append(
                    f"ลำดับ INSERT ผิด: {child} มาก่อน {parent} → FK จะพัง"
                )
        elif child in order and parent not in order:
            problems.append(f"{child} มีข้อมูล แต่ {parent} ไม่มี → FK จะพัง")

    print("  ลำดับ INSERT:")
    for index, table in enumerate(order, 1):
        print(f"    {index:>2}. {table}")

    return problems


def main() -> None:
    if not SQLITE_DB.exists():
        raise SystemExit(f"ไม่พบ {SQLITE_DB}")
    if not SEED_FILE.exists():
        raise SystemExit(f"ไม่พบ {SEED_FILE} — รัน python -m db.export_seed ก่อน")

    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    try:
        print("ตรวจ constraint / FK / NOT NULL / UNIQUE")
        print("-" * 76)
        data_problems = check_data(conn)
    finally:
        conn.close()

    print()
    order_problems = check_insert_order()

    problems = data_problems + order_problems
    print()
    if problems:
        print(f"พบ {len(problems)} ปัญหา — แก้ก่อนนำเข้า Postgres")
        print("-" * 76)
        for problem in problems:
            print(f"  ! {problem}")
        sys.exit(1)

    print("ผ่านทุกการตรวจ — seed data พร้อมนำเข้า Postgres")


if __name__ == "__main__":
    main()
