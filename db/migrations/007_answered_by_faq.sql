-- ============================================================================
--  LINE AI Academic Assistant — เพิ่ม 'faq' ใน chat_logs.answered_by (007)
--  รันต่อจาก 006:  psql -f db/migrations/007_answered_by_faq.sql
--
--  ทำไมต้องมีไฟล์นี้:
--
--  ชั้นที่ 2 (FAQ) ทำงานจริงแล้ว — ``app/router.py::_faq_answer`` อ่านตาราง
--  ``faqs`` ที่หน้า /admin เขียนเข้ามา แล้วตอบด้วย ``answered_by='faq'``
--  แต่ CHECK constraint จาก 003 (แก้ครั้งล่าสุดใน 005 ตอนเพิ่ม 'planner')
--  ยังไม่มีค่านี้ → **การเขียน chat_logs จะล้มทุกครั้งที่ FAQ ตอบสำเร็จ**
--  (คำตอบถึงนักศึกษาแล้วแต่วัดผลในธีสิสไม่ได้ และ log ขึ้น error เงียบ ๆ)
--
--  เจตนาเดิมของ 003 คือ "เพิ่มชั้นใหม่เมื่อไรต้องมาแก้ CHECK ด้วย" เพื่อบังคับ
--  ให้คิดก่อนว่าค่าใหม่หมายถึงอะไร — ไฟล์นี้คือการทำตามนั้น ไม่ใช่การหลบ
--
--  ค่าที่โค้ดผลิตได้จริง ณ วันที่เขียน (ต้องตรงกับบล็อกคอมเมนต์บนหัว
--  app/router.py และ RouteResult.answered_by — ตอนนี้ 11 ค่า):
--
--    พื้นผิวที่ผู้ใช้ใช้     rich_menu, quick_reply, course, follow
--    ชั้นที่ตอบ             search, faq, planner, ai_chat
--    ตอบไม่ได้              no_data (ไม่มีข้อมูล), db_error (ถาม DB ไม่สำเร็จ),
--                          fallback (ไม่เข้าใจคำถาม)
--
--  **ยังไม่มี rag** — ตาราง rag_chunks ยังว่าง ห้ามใส่ไว้ล่วงหน้าเพราะจะกลาย
--  เป็นคำเคลมในเอกสารที่ไม่มีของจริงรองรับ (เหตุผลเดียวกับที่ 003 ไม่ใส่ faq)
--
--  ไม่มี UPDATE ข้อมูลเก่าในไฟล์นี้: แถวเดิมไม่มีแถวไหนที่ "จริง ๆ คือ faq"
--  เพราะก่อนวันนี้ไม่มีโค้ดฝั่งตอบไหนอ่านตาราง faqs เลย
--
--  idempotent: รันซ้ำได้ (DROP ... IF EXISTS ก่อน ADD)
-- ============================================================================

BEGIN;

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
        'faq',          -- คำตอบที่คนเขียนไว้ในตาราง faqs (ชั้นที่ 2)
        'planner',      -- คำนวณความก้าวหน้า/แผนเทอมถัดไปจาก curriculum_rules
        'ai_chat',      -- โหมดปรึกษา AI (LLM)
        'no_data',      -- เข้าใจคำถามแต่ไม่มีข้อมูลในคลัง
        'db_error',     -- ถามฐานข้อมูลไม่สำเร็จ
        'fallback'      -- ไม่เข้าใจคำถาม / เงื่อนไขไม่ครบ
    ));

COMMENT ON COLUMN chat_logs.answered_by IS
    'พื้นผิว/ชั้นที่ตอบ: rich_menu, quick_reply, course, follow, search, faq, planner, ai_chat, no_data, db_error, fallback — ดู CHECK constraint และ app/router.py (ยังไม่มี rag)';

COMMIT;
