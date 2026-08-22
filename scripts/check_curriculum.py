#!/usr/bin/env python3
import sys
sys.path.insert(0, "app")
from config import Settings
import psycopg

settings = Settings()
with psycopg.connect(settings.database_url) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT std_year, std_semester, COUNT(*) as courses
            FROM curriculum_rules
            WHERE program_code = '643170151'
            GROUP BY std_year, std_semester
            ORDER BY std_year, std_semester
        """)

        print("สรุปแผนการเรียนตามปี/เทอม:")
        print("ปี    เทอม    จำนวนวิชา")
        print("-" * 30)
        for row in cur.fetchall():
            print(f"{row[0]:<6}{row[1]:<9}{row[2]}")

        cur.execute("SELECT COUNT(*) FROM curriculum_rules WHERE program_code = '643170151'")
        total = cur.fetchone()[0]
        print(f"\nรวมทั้งหมด: {total} วิชา")
