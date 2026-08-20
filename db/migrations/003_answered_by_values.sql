-- ============================================================================
--  LINE AI Academic Assistant — ล็อกค่า chat_logs.answered_by (003)
--  รันต่อจาก 002:  psql -f db/migrations/003_answered_by_values.sql
--
--  ทำไมต้องมีไฟล์นี้:
--
--  1. เดิม **ทุกทางที่ตอบสำเร็จถูกป้ายว่า rich_menu** — ทั้งการกดปุ่มใน
--     Quick Reply, การพิมพ์รหัสวิชา 7 หลัก และข้อความต้อนรับตอนเพิ่มเพื่อน
--     ทำให้เคลมในธีสิสว่า "Rich Menu รับภาระ X%" ไม่ได้เลย
--     (แก้ที่ app/router.py::_answer_surface — Rich Menu ฝัง src=rich
--      ไว้ใน postback data, Quick Reply ไม่มี)
--
--  2. คอลัมน์นี้เป็น TEXT เปล่า ๆ ไม่มี CHECK → พิมพ์ผิดครั้งเดียวก็เข้าไป
--     เงียบ ๆ และเจอตอนสรุปผลซึ่งสายเกินแก้ ตารางพี่น้องในสกีมานี้
--     (chat_logs.status, ai_sessions.end_reason) ใช้ CHECK อยู่แล้ว
--
--  ค่าที่โค้ดผลิตได้จริง ณ วันที่เขียน — ต้องตรงกับ docstring บนหัว
--  app/router.py และ RouteResult.answered_by:
--
--    พื้นผิวที่ผู้ใช้ใช้     rich_menu, quick_reply, course, follow
--    ชั้นที่ตอบ             search, ai_chat
--    ตอบไม่ได้              no_data (ไม่มีข้อมูล), db_error (ถาม DB ไม่สำเร็จ),
--                          fallback (ไม่เข้าใจคำถาม)
--
--  **ยังไม่มี faq / planner / rag** — ตาราง faqs/rag_chunks ว่าง ห้ามใส่ไว้
--  ล่วงหน้าเพราะจะกลายเป็นคำเคลมในเอกสารที่ไม่มีของจริงรองรับ
--  เพิ่มชั้นใหม่เมื่อไร → ต้องมาแก้ CHECK นี้ด้วย (เจตนา: บังคับให้คิดก่อน)
--
--  หมายเหตุการวัดผล: no_data/db_error/fallback **ทับ** ป้ายพื้นผิวโดยเจตนา
--  (กดปุ่มแล้วไม่มีข้อมูล = no_data ไม่ใช่ rich_menu) → นับ rich_menu ได้เป็น
--  ขั้นต่ำของยอดกด ไม่ใช่ยอดกดจริง ถ้าต้องการยอดกดแท้ ๆ ให้นับจาก
--  intent_key ร่วมด้วย
--
--  idempotent: รันซ้ำได้ (DROP ... IF EXISTS ก่อน ADD)
-- ============================================================================

BEGIN;

-- แถวเก่าที่เก็บไว้ก่อนแยกพื้นผิว (21 แถว ณ 21 ส.ค. 2026): ตอนนั้น rich_menu
-- หมายถึง "ตอบด้วยปุ่ม" ซึ่งของจริงคือ Quick Reply ทั้งหมด เพราะ Rich Menu
-- ยังไม่ถูกสร้างบน LINE เลย → ค่าที่เก็บไว้จึงเป็น "ยอดกด Rich Menu" ที่ไม่มีจริง
--
-- **ไม่รันให้อัตโนมัติ** เพราะเป็นการเขียนทับข้อมูลที่เก็บมาแล้ว (ย้อนไม่ได้)
-- ถ้าจะสรุปผลธีสิสรวมข้อมูลช่วงก่อนหน้า ให้ปลด comment แล้วรันเอง
-- ทางเลือกที่ปลอดภัยกว่า: ตัดข้อมูลก่อนวันนี้ออกจากการสรุปด้วย created_at
--
-- UPDATE chat_logs
--    SET answered_by = 'quick_reply'
--  WHERE answered_by = 'rich_menu';

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
        'ai_chat',      -- โหมดปรึกษา AI (LLM)
        'no_data',      -- เข้าใจคำถามแต่ไม่มีข้อมูลในคลัง
        'db_error',     -- ถามฐานข้อมูลไม่สำเร็จ
        'fallback'      -- ไม่เข้าใจคำถาม / เงื่อนไขไม่ครบ
    ));

COMMENT ON COLUMN chat_logs.answered_by IS
    'พื้นผิว/ชั้นที่ตอบ: rich_menu, quick_reply, course, follow, search, ai_chat, no_data, db_error, fallback — ดู CHECK constraint และ app/router.py (ยังไม่มี faq/planner/rag)';

COMMIT;
