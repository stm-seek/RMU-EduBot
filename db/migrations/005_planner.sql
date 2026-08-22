-- ============================================================================
--  LINE AI Academic Assistant — Planner Engine (005)
--  รันต่อจาก 004:  psql -f db/migrations/005_planner.sql
--
--  ไฟล์นี้เตรียมทางให้ชั้น planner (ตอบ "ความก้าวหน้าตามหลักสูตร" แบบคำนวณ
--  ไม่ใช่ให้ LLM เดา) มี 3 เรื่อง:
--
--  1. curriculum_rules.course_code_full — รหัสวิชาแบบเต็มที่แผนการเรียน
--     ในระบบทะเบียนใช้ เช่น '7071102-3'
--
--     ทำไมต้องแยกคอลัมน์: ตาราง courses เก็บรหัส **7 หลัก** ('7071102')
--     และ app/router.py ก็ดึงรหัสจากข้อความผู้ใช้ด้วย 7 หลักเหมือนกัน
--     (COURSE_CODE_PATTERN) ตอนนำเข้าครั้งแรกเผลอเก็บรหัสเต็มลง course_code
--     → JOIN courses ได้ 0 แถวทั้ง 32 วิชา ชื่อวิชาหายหมดแบบไม่มี error
--     ให้ course_code เป็น 7 หลักเสมอ (ใช้ JOIN) และเก็บ '-N' ซึ่งเป็นเลข
--     รุ่นหลักสูตรไว้ที่นี่ เพื่อ diff กับแผนตอน re-scrape ได้
--
--  2. index (program_code, std_year, std_semester) — ทุก query ของ planner
--     เรียงตามลำดับเทอมของแผน
--
--  3. answered_by += 'planner' — ชั้นใหม่ต้องประกาศใน CHECK ก่อน ไม่งั้น
--     เขียน chat_logs ไม่ผ่าน (ดูเจตนาใน 003)
--
--  idempotent: รันซ้ำได้ทั้งไฟล์
-- ============================================================================

BEGIN;

ALTER TABLE curriculum_rules
    ADD COLUMN IF NOT EXISTS course_code_full TEXT;

COMMENT ON COLUMN curriculum_rules.course_code_full IS
    'รหัสเต็มตามแผนการเรียน เช่น 7071102-3 (เลขหลังขีด = รุ่นหลักสูตร) — course_code เก็บ 7 หลักไว้ JOIN courses';

CREATE INDEX IF NOT EXISTS idx_curriculum_rules_term
    ON curriculum_rules (program_code, std_year, std_semester);

CREATE INDEX IF NOT EXISTS idx_prerequisites_course
    ON prerequisites (program_code, course_code);

ALTER TABLE chat_logs
    DROP CONSTRAINT IF EXISTS chat_logs_answered_by_check;

ALTER TABLE chat_logs
    ADD CONSTRAINT chat_logs_answered_by_check
    CHECK (answered_by IN (
        'rich_menu',    -- กดปุ่มบน Rich Menu (postback มี src=rich)
        'quick_reply',  -- กดปุ่มในบทสนทนา
        'course',       -- พิมพ์รหัสวิชา 7 หลักมาเอง
        'follow',       -- ข้อความต้อนรับตอนเพิ่มเพื่อน
        'search',       -- พิมพ์คำแล้วค้นจาก DB (pg_trgm)
        'planner',      -- คำนวณความก้าวหน้า/แผนเทอมถัดไปจาก curriculum_rules
        'ai_chat',      -- โหมดปรึกษา AI (LLM)
        'no_data',      -- เข้าใจคำถามแต่ไม่มีข้อมูลในคลัง
        'db_error',     -- ถามฐานข้อมูลไม่สำเร็จ
        'fallback'      -- ไม่เข้าใจคำถาม / เงื่อนไขไม่ครบ
    ));

COMMENT ON COLUMN chat_logs.answered_by IS
    'พื้นผิว/ชั้นที่ตอบ: rich_menu, quick_reply, course, follow, search, planner, ai_chat, no_data, db_error, fallback — ดู CHECK constraint และ app/router.py (ยังไม่มี faq/rag)';

COMMIT;
