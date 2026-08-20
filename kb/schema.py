"""
SQLite schema for the RMU academic knowledge base.

ทุกตารางในไฟล์นี้เก็บ *ข้อมูลสาธารณะ* จาก regis.rmu.ac.th เท่านั้น
ไม่มีข้อมูลส่วนบุคคลของนักศึกษา (ชื่อ / รหัส นศ. / เกรด) อยู่ในนี้เลย
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent / "data" / "rmu_kb.db"

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── หลักสูตร ────────────────────────────────────────────────────────────────
-- 1 แถว = 1 หลักสูตร/ปีปรับปรุง เช่น 643170151 (MDI ปรับปรุง 64)
CREATE TABLE IF NOT EXISTS programs (
    program_id      INTEGER PRIMARY KEY,   -- programid ของ Vision Net เช่น 59721
    faculty_id      TEXT    NOT NULL,      -- facultyid เช่น '70'
    level_id        TEXT    NOT NULL,      -- levelid เช่น '31' = ป.ตรี 4 ปี ภาคปกติ
    program_code    TEXT,                  -- เช่น '643170151'
    program_name    TEXT,                  -- เช่น 'การจัดการนวัตกรรมดิจิทัล'
    faculty_name    TEXT,
    level_name      TEXT,
    degree_name     TEXT,
    department_name TEXT,
    total_credits   INTEGER,               -- ผลรวมหน่วยกิตของหมวดระดับบนสุด
    source_url      TEXT    NOT NULL,
    scraped_at      TEXT    NOT NULL
);

-- ── หมวด/กลุ่มวิชา (โครงสร้างต้นไม้) ─────────────────────────────────────────
-- ตรงกับ toggle_row(N) / <table id='TB_ROW_N'> ในหน้า program_info_1.asp
CREATE TABLE IF NOT EXISTS categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id      INTEGER NOT NULL REFERENCES programs(program_id) ON DELETE CASCADE,
    row_id          INTEGER NOT NULL,      -- N ใน toggle_row(N) ใช้ join กับ course list
    parent_row_id   INTEGER,               -- NULL = หมวดระดับบนสุด
    number          TEXT,                  -- '1', '1.1', '2.1' ...
    depth           INTEGER NOT NULL,      -- 0 = บนสุด
    label           TEXT    NOT NULL,      -- 'กลุ่มวิชา บังคับ'
    required_credits INTEGER,              -- หน่วยกิตที่ต้องเก็บในหมวดนี้
    is_leaf         INTEGER NOT NULL DEFAULT 0,
    -- 'required' = เรียนทุกวิชาในลิสต์, 'elective' = เลือกให้ครบหน่วยกิต
    selection_mode  TEXT,
    UNIQUE (program_id, row_id)
);

-- ── รายวิชา ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS courses (
    course_id       INTEGER PRIMARY KEY,   -- courseid ของ Vision Net เช่น 32701
    course_code     TEXT    NOT NULL,      -- '1109901'  (7 หลัก ใช้ค้น class_info_1)
    name_th         TEXT,
    name_en         TEXT,
    credits_text    TEXT,                  -- '3 (2-2-5)' ตามที่แสดงบนเว็บ
    credits         INTEGER,               -- 3  (แยกออกมาเพื่อคำนวณ)
    description_th  TEXT,                  -- คำอธิบายรายวิชา จาก class_info_5.asp
    faculty_text    TEXT,
    source_url      TEXT,
    scraped_at      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(course_code);

-- ── วิชาอยู่ในหมวดไหนของหลักสูตรไหน ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS program_courses (
    program_id      INTEGER NOT NULL REFERENCES programs(program_id) ON DELETE CASCADE,
    category_row_id INTEGER NOT NULL,      -- = categories.row_id
    course_id       INTEGER NOT NULL REFERENCES courses(course_id),
    position        INTEGER,               -- ลำดับที่ปรากฏในลิสต์
    PRIMARY KEY (program_id, category_row_id, course_id)
);

-- ── หมู่เรียนที่เปิดสอนจริง (จาก class_info_1.asp) ───────────────────────────
CREATE TABLE IF NOT EXISTS offerings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id       INTEGER NOT NULL REFERENCES courses(course_id),
    course_code     TEXT    NOT NULL,
    acad_year       INTEGER NOT NULL,      -- 2568
    semester        INTEGER NOT NULL,      -- 1 / 2 / 3
    section         TEXT,                  -- หมู่เรียน
    course_group    TEXT,                  -- คอลัมน์ 'กลุ่มวิชา' เช่น '110'
    schedule_raw    TEXT,                  -- 'TU 08:00-11:20 360305'
    instructors     TEXT,                  -- คั่นด้วย ' | '
    seats_total     INTEGER,               -- จำนวนรับ
    seats_taken     INTEGER,               -- ลงแล้ว
    seats_left      INTEGER,               -- เหลือ
    status          TEXT,                  -- 'ปกติ'
    source_url      TEXT,
    scraped_at      TEXT    NOT NULL,
    UNIQUE (course_id, acad_year, semester, section, schedule_raw)
);

CREATE INDEX IF NOT EXISTS idx_offerings_term ON offerings(acad_year, semester);
CREATE INDEX IF NOT EXISTS idx_offerings_code ON offerings(course_code);

-- ── คาบเรียนที่แยก field แล้ว (ใช้ตรวจตารางชน) ──────────────────────────────
CREATE TABLE IF NOT EXISTS offering_slots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    offering_id     INTEGER NOT NULL REFERENCES offerings(id) ON DELETE CASCADE,
    day_code        TEXT,                  -- MO TU WE TH FR SA SU
    start_min       INTEGER,               -- 08:00 -> 480  (นาทีจากเที่ยงคืน)
    end_min         INTEGER,               -- 11:20 -> 680
    room            TEXT
);

CREATE INDEX IF NOT EXISTS idx_slots_offering ON offering_slots(offering_id);

-- ── สรุปว่าวิชานี้ "มักเปิด" เทอมไหน (derive จาก offerings หลายเทอม) ─────────
CREATE TABLE IF NOT EXISTS offering_patterns (
    course_code     TEXT PRIMARY KEY,
    opens_sem1      INTEGER NOT NULL DEFAULT 0,
    opens_sem2      INTEGER NOT NULL DEFAULT 0,
    opens_sem3      INTEGER NOT NULL DEFAULT 0,
    terms_observed  INTEGER NOT NULL DEFAULT 0,   -- จำนวนเทอมที่สำรวจ
    terms_found     INTEGER NOT NULL DEFAULT 0,   -- จำนวนเทอมที่พบว่าเปิด
    detail          TEXT,                         -- JSON: {"2568/1": 4, ...} = จำนวนหมู่
    computed_at     TEXT NOT NULL
);

-- ── วิชาบังคับก่อน + แผนเทอมมาตรฐาน (กรอกมือจาก มคอ.2) ───────────────────────
-- ระบบทะเบียนไม่มีข้อมูลนี้เลย (ค้น 'บังคับก่อน' ได้ 0 ผลลัพธ์)
-- ต้องมี source เพื่อให้บอทอ้างอิงได้ และตรวจสอบย้อนหลังได้
CREATE TABLE IF NOT EXISTS curriculum_rules (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    program_code    TEXT    NOT NULL,      -- '643170151'
    course_code     TEXT    NOT NULL,      -- '7071204'
    std_year        INTEGER,               -- ชั้นปีตามแผน
    std_semester    INTEGER,               -- ภาคการศึกษาตามแผน
    is_fixed_term   INTEGER NOT NULL DEFAULT 0,  -- 1 = หลักสูตรฟิกซ์เทอมไว้
    note            TEXT,
    source          TEXT    NOT NULL,      -- 'มคอ.2 หลักสูตร 643170151 หน้า 42'
    verified_by     TEXT,
    updated_at      TEXT    NOT NULL,
    UNIQUE (program_code, course_code)
);

CREATE TABLE IF NOT EXISTS prerequisites (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    program_code    TEXT    NOT NULL,
    course_code     TEXT    NOT NULL,      -- วิชาที่จะเรียน
    requires_code   TEXT    NOT NULL,      -- ต้องผ่านวิชานี้ก่อน
    -- 'hard'  = ต้องผ่านก่อนจริง ๆ
    -- 'soft'  = แนะนำให้เรียนก่อน
    -- 'concurrent' = เรียนพร้อมกันได้
    kind            TEXT    NOT NULL DEFAULT 'hard',
    source          TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL,
    UNIQUE (program_code, course_code, requires_code)
);

-- ── อาจารย์ ─────────────────────────────────────────────────────────────────
-- ข้อมูลจาก itrmu.org/academic_staff.php มีแค่ ชื่อ + ตำแหน่ง + email
-- ฟิลด์ phone / building / floor / room / office_hours **เว็บไม่มี**
-- ต้องกรอกมือจากคณะ → ปล่อย NULL ไว้ และบอทต้องตอบว่า "ไม่มีข้อมูล"
-- ห้ามเดา (ดู Requirement ข้อ 7 ที่ขอ 9 ฟิลด์ แต่เว็บให้ได้แค่ 2)
CREATE TABLE IF NOT EXISTS instructors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT    NOT NULL UNIQUE,  -- ชื่อพร้อมคำนำหน้าตามเว็บ
    name_normalized TEXT    NOT NULL,         -- ตัดคำนำหน้า/ยศ ออก ใช้ค้นหา
    title_prefix    TEXT,                     -- ผู้ช่วยศาสตราจารย์ / อาจารย์ / ดร.
    email           TEXT,
    -- ↓ เว็บไม่มี ต้องกรอกมือ
    phone           TEXT,
    building        TEXT,
    floor           TEXT,
    room            TEXT,
    office_hours    TEXT,
    other_contact   TEXT,
    -- แหล่งข้อมูลของฟิลด์ที่กรอกมือ (เพื่อ audit)
    manual_source   TEXT,
    source_url      TEXT,
    scraped_at      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_instructors_norm ON instructors(name_normalized);

-- อาจารย์ 1 คนสังกัดได้หลายสาขา/หลายหลักสูตร (พบจริง เช่น สอนทั้ง MTA และ CTD)
CREATE TABLE IF NOT EXISTS instructor_affiliations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    instructor_id   INTEGER NOT NULL REFERENCES instructors(id) ON DELETE CASCADE,
    group_name      TEXT    NOT NULL,   -- 'สาขาเทคโนโลยีสารสนเทศ (IT)'
    group_code      TEXT,               -- 'IT' / 'MTA' / 'MDI' / 'CTD'
    position        TEXT,               -- 'ประธานหลักสูตร...' / 'อาจารย์ประจำหลักสูตร'
    is_chair        INTEGER NOT NULL DEFAULT 0,
    UNIQUE (instructor_id, group_name, position)
);

-- ── เอกสาร/แบบฟอร์ม/ลิงก์ที่นักศึกษาต้องใช้ ─────────────────────────────────
-- ตอบคำถามแนว "ขอเอกสารเพิ่มวิชาได้ที่ไหน" → ส่ง URL ให้ตรง ๆ
-- ไม่ต้องดาวน์โหลดไฟล์มาเก็บ (เปลืองที่ + ลิขสิทธิ์) เก็บแค่ URL + metadata
CREATE TABLE IF NOT EXISTS documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    category        TEXT    NOT NULL,   -- registration / loan / internship / calendar ...
    title           TEXT    NOT NULL,
    url             TEXT    NOT NULL UNIQUE,
    doc_type        TEXT,               -- pdf / doc / docx / page / drive
    -- 'student' = นักศึกษาใช้ , 'staff' = ของบุคลากร (กรองออกจากคำตอบบอทได้)
    audience        TEXT    NOT NULL DEFAULT 'student',
    keywords        TEXT,               -- คำค้นไทย คั่นด้วย , ใช้ทำ FAQ matching
    note            TEXT,
    source_page     TEXT,               -- หน้าที่พบลิงก์นี้
    -- ผลการตรวจสอบว่าลิงก์ยังใช้ได้
    http_status     INTEGER,
    content_type    TEXT,
    content_length  INTEGER,
    is_available    INTEGER,            -- 1 = เข้าได้จริง
    checked_at      TEXT,
    scraped_at      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_cat ON documents(category, audience);

-- ── log การ scrape (ตรวจสอบว่าข้อมูลเก่าแค่ไหน) ──────────────────────────────
CREATE TABLE IF NOT EXISTS scrape_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task            TEXT    NOT NULL,
    target          TEXT,
    status          TEXT    NOT NULL,      -- ok / partial / error
    rows_written    INTEGER DEFAULT 0,
    message         TEXT,
    started_at      TEXT    NOT NULL,
    finished_at     TEXT
);
"""


def connect(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    """เปิด connection และสร้าง schema ถ้ายังไม่มี"""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


if __name__ == "__main__":
    conn = connect()
    tables = [
        r["name"]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
    ]
    print(f"db: {DEFAULT_DB}")
    print(f"tables ({len(tables)}): {', '.join(tables)}")
    conn.close()
