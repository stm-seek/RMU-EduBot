"""ตรวจความถูกต้องของข้อมูลใน knowledge base (อ่านอย่างเดียว ไม่แก้ DB)"""

import sqlite3
import sys
from pathlib import Path

DB = Path(r"D:\repo\line-bot-jang\kb\data\rmu_kb.db")
PROGRAM_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 59721

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

prog = conn.execute(
    "SELECT * FROM programs WHERE program_id = ?", (PROGRAM_ID,)
).fetchone()
print(f"หลักสูตร : {prog['program_code']} {prog['program_name']}")
print(f"คณะ      : {prog['faculty_name']}")
print(f"ระดับ     : {prog['level_name']}")
print(f"รวม      : {prog['total_credits']} หน่วยกิต")
print(f"ที่มา     : {prog['source_url'][:96]}")
print()

rows = conn.execute(
    """
    SELECT c.row_id, c.number, c.depth, c.label, c.required_credits,
           c.is_leaf, c.selection_mode,
           COUNT(pc.course_id)          AS n_courses,
           COALESCE(SUM(co.credits), 0) AS sum_credits
      FROM categories c
      LEFT JOIN program_courses pc
             ON pc.program_id = c.program_id AND pc.category_row_id = c.row_id
      LEFT JOIN courses co ON co.course_id = pc.course_id
     WHERE c.program_id = ?
     GROUP BY c.row_id
     ORDER BY c.row_id
    """,
    (PROGRAM_ID,),
).fetchall()

print("โครงสร้างหลักสูตร")
print("-" * 104)
for r in rows:
    indent = "  " * r["depth"]
    need = r["required_credits"]
    mode = {"required": "เรียนทุกวิชา", "elective": "เลือก"}.get(
        r["selection_mode"], "-"
    )
    note = ""
    if r["is_leaf"]:
        if r["selection_mode"] == "required" and need is not None:
            note = "OK" if r["sum_credits"] == need else f"!! sum={r['sum_credits']}"
        elif r["selection_mode"] == "elective" and need is not None:
            note = "OK" if r["sum_credits"] >= need else f"!! sum={r['sum_credits']}"
    print(
        f"{indent}{r['number'] or '-':<7} {r['label'][:44]:<44} "
        f"{str(need) + ' นก.':>8}  {mode:<12} วิชา={r['n_courses']:<3} {note}"
    )

top = sum(r["required_credits"] or 0 for r in rows if r["depth"] == 0)
print("-" * 104)
print(f"ผลรวมหมวดบนสุด = {top} นก. (ในตาราง programs = {prog['total_credits']})")

print("\nตัวอย่างรายวิชาในหมวดบังคับเฉพาะด้าน (2.1)")
print("-" * 104)
for r in conn.execute(
    """
    SELECT co.course_code, co.name_th, co.name_en, co.credits_text
      FROM program_courses pc
      JOIN courses co ON co.course_id = pc.course_id
      JOIN categories ca ON ca.program_id = pc.program_id
                        AND ca.row_id = pc.category_row_id
     WHERE pc.program_id = ? AND ca.number = '2.1'
     ORDER BY pc.position
     LIMIT 8
    """,
    (PROGRAM_ID,),
):
    print(
        f"  {r['course_code']:<9} {(r['name_th'] or '')[:40]:<40} "
        f"{(r['name_en'] or '')[:34]:<34} {r['credits_text']}"
    )

bad = conn.execute(
    "SELECT COUNT(*) FROM courses WHERE credits IS NULL OR course_code = ''"
).fetchone()[0]
missing_th = conn.execute(
    "SELECT COUNT(*) FROM courses WHERE name_th IS NULL OR name_th = ''"
).fetchone()[0]
total = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
print(f"\nคุณภาพข้อมูล: courses={total}  credits/code เสีย={bad}  ไม่มีชื่อไทย={missing_th}")

# ── offering pattern: วิชานี้เปิดเทอมไหน ────────────────────────────────────
print("\nOffering pattern (ใช้แทนแผนการเรียนที่ระบบทะเบียนไม่มี)")
print("-" * 104)
pattern_rows = conn.execute(
    """
    SELECT ca.number, co.course_code, co.name_th,
           op.opens_sem1, op.opens_sem2, op.terms_found, op.terms_observed
      FROM program_courses pc
      JOIN courses co ON co.course_id = pc.course_id
      JOIN categories ca ON ca.program_id = pc.program_id
                        AND ca.row_id = pc.category_row_id
      LEFT JOIN offering_patterns op ON op.course_code = co.course_code
     WHERE pc.program_id = ?
     ORDER BY ca.number, co.course_code
    """,
    (PROGRAM_ID,),
).fetchall()

only1 = only2 = both = never = 0
never_list: list[str] = []
for r in pattern_rows:
    s1, s2 = bool(r["opens_sem1"]), bool(r["opens_sem2"])
    if s1 and s2:
        both += 1
    elif s1:
        only1 += 1
    elif s2:
        only2 += 1
    else:
        never += 1
        never_list.append(f"{r['course_code']} {(r['name_th'] or '')[:30]}")

print(f"  เปิดทั้ง 2 เทอม  : {both:>3} วิชา  (ยืดหยุ่น เลื่อนได้)")
print(f"  เปิดเทอม 1 เท่านั้น: {only1:>3} วิชา  (พลาดแล้วรอ 1 ปี)")
print(f"  เปิดเทอม 2 เท่านั้น: {only2:>3} วิชา  (พลาดแล้วรอ 1 ปี)")
print(f"  ไม่พบว่าเปิดเลย  : {never:>3} วิชา  (ต้องสอบถามคณะ)")
for item in never_list[:10]:
    print(f"      - {item}")
if len(never_list) > 10:
    print(f"      ... และอีก {len(never_list) - 10} วิชา")

n_off = conn.execute("SELECT COUNT(*) FROM offerings").fetchone()[0]
n_slot = conn.execute("SELECT COUNT(*) FROM offering_slots").fetchone()[0]
terms = conn.execute(
    "SELECT DISTINCT acad_year, semester FROM offerings ORDER BY acad_year, semester"
).fetchall()
term_text = ", ".join(f"{t['acad_year']}/{t['semester']}" for t in terms)
print(f"\n  offerings={n_off} แถว  slots={n_slot} คาบ  เทอมที่สำรวจ: {term_text}")

# ── สิ่งที่ยังต้องกรอกมือ ───────────────────────────────────────────────────
n_prereq = conn.execute("SELECT COUNT(*) FROM prerequisites").fetchone()[0]
n_rules = conn.execute("SELECT COUNT(*) FROM curriculum_rules").fetchone()[0]
print("\nข้อมูลที่ระบบทะเบียนไม่มี (ต้องกรอกมือจาก มคอ.2)")
print("-" * 104)
print(f"  prerequisites   : {n_prereq} แถว  {'<-- ยังว่าง' if not n_prereq else ''}")
print(f"  curriculum_rules: {n_rules} แถว  {'<-- ยังว่าง' if not n_rules else ''}")

conn.close()
