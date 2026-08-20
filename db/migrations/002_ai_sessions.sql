-- ============================================================================
--  LINE AI Academic Assistant — ตารางโหมดปรึกษา AI (002)
--  รันต่อจาก 001_init.sql:  psql -f db/migrations/002_ai_sessions.sql
--
--  ทำไมต้องมีตารางนี้: AI Chat เดิมยิง LLM ทุกข้อความที่ search ไม่เจอ
--  (เสีย token ฟรีกับเรื่องที่ไม่ควรตอบ + วัดผลไม่ได้ว่า "ตั้งใจปรึกษา" กี่ครั้ง)
--  เลยเปลี่ยนเป็น "โหมดปรึกษา" ที่ user กดปุ่ม/พิมพ์คำเพื่อเข้า และออกได้
--  4 ทาง: กดปุ่มจบ, พิมพ์คำออก, ว่างเกิน 30 นาที, ครบเพดานรอบ
--  (ดู app/ai_chat.py::dispatch — กติกาเหล่านี้เป็นค่าใน config)
--
--  ตารางนี้คือข้อมูลวัดผลธีสิสตรง ๆ: จำนวน session, รอบเฉลี่ยต่อ session,
--  ออกด้วยเหตุผลอะไร (ปุ่ม/คำพูด/หมดเวลา/ครบรอบ) — join กับ chat_logs
--  ได้ผ่าน user_id + ช่วงเวลา started_at
--
--  idempotent ทั้งไฟล์: รันซ้ำได้ ไม่ทำลายข้อมูล (CREATE IF NOT EXISTS,
--  index ก็ IF NOT EXISTS)
-- ============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS ai_sessions (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- อัปเดตทุกครั้งที่ user ส่งข้อความในโหมด — ใช้คำนวณ timeout ว่าง 30 นาที
    last_active_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- จำนวนรอบสนทนาในโหมดนี้ — เปรียบกับเพดาน ai_chat_session_max_turns
    turn_count      INTEGER NOT NULL DEFAULT 0,
    -- NULL = session ยังเปิดอยู่
    ended_at        TIMESTAMPTZ,
    -- เหตุผลที่จบ: button = กดปุ่มจบ, keyword = พิมพ์คำออก,
    -- timeout = ว่างเกินกำหนด, turn_limit = ครบเพดานรอบ
    end_reason      TEXT CHECK (end_reason IN ('button', 'keyword', 'timeout', 'turn_limit'))
);

-- user 1 คนมี session เปิดได้ **แถวเดียว** — dispatch ใช้ WHERE ended_at IS NULL
-- ถ้าไม่มี index นี้ ทุกข้อความในโหมดต้อง scan ทั้งตารางเมื่อข้อมูลโต
CREATE INDEX IF NOT EXISTS idx_ai_sessions_open
    ON ai_sessions (user_id) WHERE ended_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_ai_sessions_started
    ON ai_sessions (started_at DESC);

COMMIT;
