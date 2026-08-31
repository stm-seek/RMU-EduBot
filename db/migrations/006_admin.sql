-- ============================================================================
--  LINE AI Academic Assistant — หน้า admin แก้ข้อมูล (006)
--  รันต่อจาก 005:  psql -f db/migrations/006_admin.sql
--
--  ไฟล์นี้เตรียมทางให้ ``app/admin.py`` แก้ข้อมูลที่ scraper เอามาให้ไม่ได้
--  (FAQ ที่คนต้องเขียนเอง, เบอร์โทร/ห้องอาจารย์, วิชาบังคับก่อนจาก มคอ.2)
--  มี 3 เรื่อง:
--
--  1. ``is_active`` — **ปิดใช้ ไม่ลบ**
--
--     ตารางเหล่านี้เป็นข้อมูลที่ scraper เขียนทับได้ (``ON CONFLICT DO UPDATE``)
--     ถ้า admin ลบแถวทิ้งจริง ๆ รอบ scrape ถัดไปจะเอากลับมาใหม่เงียบ ๆ
--     แล้วคนที่ลบจะไม่รู้เลยว่าของที่ตั้งใจซ่อนกลับมาแล้ว การปิดด้วย flag
--     ทำให้ scraper อัปเดตเนื้อหาต่อได้ โดยไม่ปลุกแถวที่คนตัดสินใจปิดไว้
--
--     ``faqs`` มี ``is_active`` อยู่แล้วตั้งแต่ 001 — ไม่ต้องเพิ่ม
--
--     **ต้องแก้ query ฝั่งอ่านให้กรองด้วย** ไม่งั้นปุ่มปิดจะไม่มีผลอะไรเลย
--     (ทำแล้วใน ``app/repository.py`` — ถ้ารันไฟล์นี้ช้ากว่าโค้ด query จะพัง
--     ด้วย ``column "is_active" does not exist``)
--
--  2. ``updated_at`` / ``updated_by`` — แยก "คนแก้" ออกจาก "scraper เขียน"
--
--     ``documents``/``instructors`` มีแต่ ``scraped_at`` ซึ่ง scraper ทับทุกรอบ
--     ถ้าไม่มีคอลัมน์ของฝั่งคน จะดูไม่ออกว่าเบอร์โทรที่เห็นมาจากการกรอกมือ
--     หรือ scraper ไปเจอมา — ซึ่งเป็นข้อมูลที่ต้องใช้ตัดสินว่าเชื่อได้แค่ไหน
--
--     ``updated_by`` เก็บ **12 ตัวแรกของ line_user_hash** ไม่ใช่ค่าเต็ม:
--     พอสำหรับไล่ว่าใครแก้ (admin มีไม่กี่คน) และไม่สร้างที่เก็บ hash เต็ม
--     ขึ้นมาอีกจุดนอก ``app_users``
--
--  3. ``admin_audit_logs`` — ใครแก้อะไรเมื่อไหร่
--
--     หน้า admin แก้คำตอบที่บอทเอาไปตอบนักศึกษาได้ตรง ๆ ถ้าวันหนึ่งคำตอบผิด
--     ต้องย้อนได้ว่าใครเปลี่ยนและเปลี่ยนจากอะไร — ``changes`` เก็บทั้งค่าเก่า
--     และค่าใหม่เพื่อให้ย้อนกลับได้ด้วยมือ (ไม่ได้ทำปุ่ม undo)
--
--  idempotent: รันซ้ำได้ทั้งไฟล์
-- ============================================================================

BEGIN;

-- ── 1. is_active: ปิดใช้ ไม่ลบ ───────────────────────────────────────────────

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE instructors
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE curriculum_rules
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE prerequisites
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- ``is_available`` (documents) กับ ``is_active`` ต่างกันและต้องอยู่แยกกัน:
--   is_available = ตัวตรวจลิงก์บอกว่า URL ยังเข้าได้ไหม (เครื่องตั้ง)
--   is_active    = คนตัดสินใจว่าจะให้บอทใช้ไหม (คนตั้ง)
-- ยุบรวมกันแล้วรอบตรวจลิงก์ถัดไปจะลบการตัดสินใจของคนทิ้ง
COMMENT ON COLUMN documents.is_active IS
    'คนปิดเอกสารนี้ไว้ไหม — คนละเรื่องกับ is_available ที่ตัวตรวจลิงก์ตั้ง';
COMMENT ON COLUMN instructors.is_active IS
    'FALSE = ไม่ให้บอทเอาไปตอบ (ย้าย/เกษียณ) แต่ยังเก็บแถวไว้ให้ scraper ทับได้';
COMMENT ON COLUMN curriculum_rules.is_active IS
    'FALSE = ไม่นับวิชานี้ในแผน (ยกเลิกวิชา/หลักสูตรปรับ) — planner ข้ามไปเลย';
COMMENT ON COLUMN prerequisites.is_active IS
    'FALSE = ไม่บังคับเงื่อนไขนี้แล้ว';

-- ── 2. ร่องรอยการแก้ด้วยมือ ─────────────────────────────────────────────────

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS updated_by TEXT;
ALTER TABLE instructors
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS updated_by TEXT;
ALTER TABLE faqs
    ADD COLUMN IF NOT EXISTS updated_by TEXT;
ALTER TABLE curriculum_rules
    ADD COLUMN IF NOT EXISTS updated_by TEXT;
ALTER TABLE prerequisites
    ADD COLUMN IF NOT EXISTS updated_by TEXT;

-- NULL = ยังไม่มีคนแตะ (ข้อมูลมาจาก scraper/seed ล้วน ๆ) ซึ่งเป็นค่าที่ถูก
-- สำหรับแถวเดิมทุกแถว — ห้ามใส่ DEFAULT now() เพราะจะกลายเป็นว่าทุกแถว
-- ถูกคนแก้ตอนรัน migration
COMMENT ON COLUMN documents.updated_at IS
    'ครั้งล่าสุดที่คนแก้ผ่านหน้า admin — NULL = ยังไม่มีคนแตะ (ต่างจาก scraped_at)';
COMMENT ON COLUMN documents.updated_by IS '12 ตัวแรกของ line_user_hash ของ admin';

-- ── 3. audit ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    admin_hash  TEXT NOT NULL,
    action      TEXT NOT NULL CHECK (action IN ('create', 'update', 'toggle')),
    table_name  TEXT NOT NULL,
    row_key     TEXT,
    changes     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_admin_audit_time
    ON admin_audit_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_admin_audit_row
    ON admin_audit_logs (table_name, row_key);

COMMENT ON TABLE admin_audit_logs IS
    'ใครแก้อะไรผ่านหน้า admin — ไม่มี delete เพราะหน้า admin ปิดใช้ ไม่ลบ';
COMMENT ON COLUMN admin_audit_logs.admin_hash IS
    'line_user_hash เต็มของ admin — ตารางนี้ไม่ให้หน้าเว็บอ่าน';
COMMENT ON COLUMN admin_audit_logs.changes IS
    'ค่าเก่า+ค่าใหม่ของ field ที่เปลี่ยน: {"field": {"from": ..., "to": ...}}';

-- ── 4. index ที่หน้า admin ต้องใช้ ──────────────────────────────────────────

-- หน้า admin เรียงตามการแก้ล่าสุดขึ้นก่อน (คนแก้อยากเห็นของที่เพิ่งแตะ)
CREATE INDEX IF NOT EXISTS idx_faqs_updated ON faqs (updated_at DESC);
-- หน้าดู chat_logs กรอง "คำถามที่ตอบไม่ได้" — ตัวนี้คือ input ของการเขียน FAQ
CREATE INDEX IF NOT EXISTS idx_chat_logs_unanswered
    ON chat_logs (created_at DESC)
    WHERE answered_by IN ('fallback', 'no_data');

COMMIT;
