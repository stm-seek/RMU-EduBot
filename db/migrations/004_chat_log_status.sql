-- ============================================================================
--  LINE AI Academic Assistant — chat_logs.status: ผลการส่งคำตอบ (004)
--  รันต่อจาก 003:  psql -f db/migrations/004_chat_log_status.sql
--
--  ทำไมต้องมีไฟล์นี้:
--
--  1. เดิม app/main.py::process_event เขียน chat_logs **หลังส่งสำเร็จเท่านั้น**
--     ถ้า LINE API ล้มเหลว เช่น reply token หมดอายุแล้ว push พังตามไปด้วย,
--     ติด rate limit 429, access token ผิดช่อง, เน็ตหลุด — โค้ดจะไหลเข้าทาง
--     except LineApiError แล้ว log ทิ้งไปเฉย ๆ → รอบสนทนานั้น
--     **ไม่มีแถวใน chat_logs เลย**
--     ธีสิสนับจำนวนรอบที่ตอบได้จาก chat_logs ตรง ๆ ทุกครั้งที่ส่งไม่ถึงจึงหาย
--     ออกจากข้อมูลทั้งรอบ และอัตราการตอบสำเร็จสูงเกินความจริงแบบเงียบ ๆ
--     กลายเป็นว่าความล้มเหลวที่ต้องเห็นที่สุด เป็นความล้มเหลวที่วัดไม่ได้
--
--  2. ป้ายนี้ต้องอยู่คนละคอลัมน์กับ answered_by เพราะตอบคนละคำถาม:
--     answered_by = พื้นผิว/ชั้นไหนคิดคำตอบ, status = คำตอบนั้นถึงผู้ใช้ไหม
--     ถ้ายุบรวมกันจะเสียข้อมูลไปหนึ่งด้านทันที เช่น รอบที่ ai_chat ตอบแล้ว
--     ส่งไม่ถึง ถ้าป้ายเป็น send_failed ก็นับภาระของชั้น AI ไม่ได้อีก
--     จึงไม่เพิ่มค่าที่ 10 ใน CHECK ของ answered_by — ดู 003
--
--  ค่าที่โค้ดผลิตได้จริง มีสองค่าเท่านั้น:
--
--    delivered    ส่งถึงผู้ใช้แล้ว ผ่าน reply หรือ push
--    send_failed  router คิดคำตอบได้ แต่ LINE API ปฏิเสธทุกทางที่ลอง
--
--  DEFAULT เป็น delivered โดยตั้งใจ และตรงกับข้อมูลเก่าจริง: แถวที่มีอยู่ก่อน
--  ไฟล์นี้ถูกเขียนหลังส่งสำเร็จเสมอ จึงไม่มีแถว send_failed ที่ตกหล่นอยู่
--  ให้ต้องเดาย้อนหลัง
--
--  idempotent: รันซ้ำได้ ทั้ง ADD COLUMN IF NOT EXISTS และ DROP CONSTRAINT
--  IF EXISTS ก่อน ADD CONSTRAINT
-- ============================================================================

BEGIN;

ALTER TABLE chat_logs
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'delivered';

ALTER TABLE chat_logs
    DROP CONSTRAINT IF EXISTS chat_logs_status_check;

ALTER TABLE chat_logs
    ADD CONSTRAINT chat_logs_status_check
    CHECK (status IN (
        'delivered',    -- ส่งถึงผู้ใช้แล้ว ผ่าน reply หรือ push
        'send_failed'   -- คิดคำตอบได้ แต่ LINE API ปฏิเสธทุกทางที่ลอง
    ));

COMMENT ON COLUMN chat_logs.status IS
    'ผลการส่งคำตอบ: delivered = ถึงผู้ใช้แล้ว, send_failed = คิดคำตอบได้แต่ส่งไม่ถึง — นับรอบที่ตอบได้ในธีสิสจาก delivered เท่านั้น';

COMMIT;
