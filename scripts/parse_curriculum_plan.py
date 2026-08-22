#!/usr/bin/env python3
"""
Parse curriculum plan from snapshot and generate SQL INSERT statements
สำหรับกรอกข้อมูลตาราง curriculum_rules
"""

import re
from pathlib import Path

# อ่าน snapshot
snapshot_file = Path(__file__).parent.parent / "snapshot_curriculum_plan.txt"
with open(snapshot_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Parse ข้อมูล
curriculum_data = []
current_year = None
current_semester = None
program_code = "643170151"  # การจัดการนวัตกรรมดิจิทัล

for line in lines:
    # หาปีการศึกษา เช่น "ปีการศึกษา 2564/1"
    year_match = re.search(r'ปีการศึกษา\s+(\d{4})/(\d)', line)
    if year_match:
        acad_year = int(year_match.group(1))
        semester = int(year_match.group(2))

        # คำนวณชั้นปีและเทอม (2564/1 = ปี 1 เทอม 1)
        # ปีการศึกษาที่เข้า 2564 → ปี 1
        base_year = 2564
        years_elapsed = acad_year - base_year

        if semester == 1:
            std_year = years_elapsed + 1
            std_semester = 1
        else:  # semester == 2
            std_year = years_elapsed + 1
            std_semester = 2

        current_year = std_year
        current_semester = std_semester
        print(f"# {acad_year}/{semester} → ปี {std_year} เทอม {std_semester}")
        continue

    # หารหัสวิชา เช่น "7071101-3"
    course_match = re.search(r'StaticText "(\d{7}-\d)"', line)
    if course_match and current_year and current_semester:
        course_code = course_match.group(1)
        curriculum_data.append({
            "program_code": program_code,
            "course_code": course_code,
            "std_year": current_year,
            "std_semester": current_semester
        })

# แสดงผลลัพธ์
print(f"\nพบรายวิชาทั้งหมด: {len(curriculum_data)} วิชา\n")

# สร้าง SQL INSERT
sql_statements = []
sql_statements.append("-- curriculum_rules สำหรับหลักสูตร 643170151 : การจัดการนวัตกรรมดิจิทัล")
sql_statements.append("-- สร้างจากแผนการเรียนมาตรฐาน")
sql_statements.append("")
sql_statements.append("BEGIN;")
sql_statements.append("")

for i, item in enumerate(curriculum_data, 1):
    # ตรวจสอบว่าวิชานี้เปิดเทอมเดียวหรือไม่ (ยังไม่รู้ ให้ default FALSE)
    # TODO: ต้องเช็คจาก offering_patterns
    is_fixed_term = "FALSE"

    sql = (
        f"INSERT INTO curriculum_rules "
        f"(program_code, course_code, std_year, std_semester, is_fixed_term, note, source, updated_at) VALUES\n"
        f"('{item['program_code']}', '{item['course_code']}', {item['std_year']}, {item['std_semester']}, "
        f"{is_fixed_term}, NULL, 'แผนการเรียนจากระบบทะเบียน 2024-08-22', now())"
    )

    # เพิ่ม ; ที่ท้าย หรือ , ถ้ายังไม่ใช่ตัวสุดท้าย
    if i < len(curriculum_data):
        sql += ";"

    sql_statements.append(sql)

sql_statements.append("")
sql_statements.append("COMMIT;")

# เขียนไฟล์ SQL
output_file = Path(__file__).parent.parent / "db" / "seed" / "003_curriculum_rules.sql"
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_statements))

print(f"✅ สร้าง SQL ไฟล์: {output_file}")
print(f"   จำนวน: {len(curriculum_data)} แถว")
print("\nตัวอย่าง SQL ที่สร้าง:")
print("\n".join(sql_statements[:15]))
print("...")
