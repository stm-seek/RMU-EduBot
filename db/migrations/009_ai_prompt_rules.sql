-- ============================================================================
--  LINE AI Academic Assistant — กฎเสริมของ AI ที่ผู้ดูแลเพิ่มได้ (009)
--  รันต่อจาก 008:  psql -f db/migrations/009_ai_prompt_rules.sql
--
--  ทำไมต้องมีไฟล์นี้:
--
--  ระบบให้คำปรึกษาด้วย AI (app/ai_chat.py) มี system prompt อยู่ในโค้ด และ
--  **ต้องอยู่ในโค้ดต่อไป** — prompt นั้นคือสิ่งที่บอกว่าบอทเป็นใคร ตอบด้วย
--  ข้อมูลอะไร และห้ามเดาอะไร แก้จากหน้าเว็บได้เท่ากับเปิดให้ใครที่เข้าหน้า
--  /admin ได้ เปลี่ยนบอทให้ตอบอะไรก็ได้ในคลิกเดียว (รวมทั้งลบข้อห้ามทั้งหมด)
--
--  แต่ข้อห้ามที่ "งอกขึ้นตามหน้างาน" มีจริงและเจ้าหน้าที่ต้องเพิ่มได้เอง เช่น
--  "ห้ามให้คำแนะนำเรื่องยา" / "ห้ามสอนวิธีทุจริตการสอบ" / "ห้ามตอบเรื่อง
--  การเมือง" — ข้อพวกนี้ไม่ควรต้องรอคนเขียนโค้ด deploy ใหม่
--
--  ตารางนี้จึงเก็บ **เฉพาะข้อห้าม/ข้อจำกัด "ที่ต่อท้าย"** กฎหลักเท่านั้น
--  ฝั่ง Python ต่อท้าย SYSTEM_PROMPT เป็นบล็อกที่มีหัวเรื่องกำกับชัดว่าเป็น
--  ข้อจำกัด *เพิ่มเติม* และห้ามลบล้างกฎด้านบน (กันคนพิมพ์ว่า "ไม่ต้องสนใจ
--  กฎข้อ 1") — ตัวตารางไม่มีทางแทนที่ prompt หลักได้เลยไม่ว่าจะเขียนอะไรลงไป
--
--  ── ทำไมมี rule_key ทั้งที่มี id แล้ว ──────────────────────────────────────
--
--  หน้า /admin ทั้งหน้าทำงานด้วย "กุญแจที่เป็นข้อความ" (faqs.intent_key,
--  documents.url, instructors.full_name) ปุ่มเปิด/ปิดของหน้านั้นส่งกุญแจนั้น
--  กลับมาเป็น text (ดู admin_repo.TABLE_KEYS) ถ้าตารางนี้ใช้ id ตัวเลขเป็น
--  กุญแจ ต้องเพิ่มทางโค้ดเส้นใหม่ให้กลไก toggle/row ทั้งชุด — และคนกรอกจะ
--  แก้ข้อเดิมไม่ได้เลยเพราะไม่รู้ว่า id ของข้อนั้นคือเลขอะไร
--
--  ``rule_key`` จึงเป็นชื่อสั้น ๆ ที่คนตั้งเอง (เช่น no_medical_advice) ใส่ค่า
--  เดิมคือแก้ ใส่ค่าใหม่คือเพิ่ม เหมือน intent_key ของ faqs เป๊ะ ๆ ส่วน ``id``
--  ยังมีไว้เป็น surrogate key ตามแบบตารางอื่นในสคีมานี้
--
--  ── ทำไม updated_by ไม่ใช่ created_by ──────────────────────────────────────
--
--  ทุกตารางที่หน้า /admin เขียนใช้ ``updated_at``/``updated_by`` (ค่าคือ
--  username ของ admin ที่กดบันทึกครั้งล่าสุด) หน้า admin แสดงคอลัมน์ "คนแก้"
--  จากช่องนี้ และ ``admin_audit_logs`` เก็บ "ใครสร้างครั้งแรก" ไว้ให้แล้ว
--  (action = create) การเพิ่ม created_by จะได้ข้อมูลที่ซ้ำกับ audit trail
--  แต่ไม่เข้ากับตารางอื่น
--
--  ── ทำไมมี CHECK ความยาว ───────────────────────────────────────────────────
--
--  ข้อความในตารางนี้ถูกต่อเข้า prompt ทุกครั้งที่มีคนคุยกับ AI กฎยาว ๆ ข้อเดียว
--  กินโทเคนของประวัติการสนทนา และกฎเสริมที่ยาวกว่ากฎหลักจะกลบกฎหลักในทางปฏิบัติ
--  ฝั่ง API จำกัดไว้แล้ว (app/admin.py) แต่ DB ต้องกันด้วย เพราะ psql/สคริปต์
--  เขียนลงตารางนี้ได้โดยไม่ผ่าน API
--
--  จำนวนข้อที่ *เปิดใช้* จำกัดที่ชั้น API ไม่ใช่ที่นี่ (CHECK ข้ามแถวทำใน
--  Postgres ไม่ได้ตรง ๆ ต้องใช้ trigger ซึ่งแพงกว่าประโยชน์ที่ได้ — ค่าเพดาน
--  อยู่ที่ ai_chat.PROMPT_RULE_LIMIT และถูกบังคับซ้ำตอนประกอบ prompt)
--
--  idempotent: รันซ้ำได้ทั้งไฟล์
-- ============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS ai_prompt_rules (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- ชื่อสั้น ๆ ที่คนตั้ง = กุญแจของแถว (ดูเหตุผลด้านบน)
    rule_key    TEXT NOT NULL,
    -- ข้อความที่จะไปโผล่ใน prompt จริง — หนึ่งบรรทัดหนึ่งข้อห้าม
    rule_text   TEXT NOT NULL,
    -- บันทึกภายในสำหรับคนดูแล (ไม่ถูกส่งให้ AI)
    note        TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by  TEXT,
    CONSTRAINT ai_prompt_rules_text_len
        CHECK (char_length(btrim(rule_text)) BETWEEN 2 AND 300),
    CONSTRAINT ai_prompt_rules_key_len
        CHECK (char_length(btrim(rule_key)) BETWEEN 2 AND 80)
);

-- กุญแจของแถว: unique index แยกจาก inline UNIQUE เพื่อให้รันไฟล์ซ้ำได้
-- (ALTER TABLE ADD CONSTRAINT ไม่มี IF NOT EXISTS)
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_prompt_rules_key
    ON ai_prompt_rules (rule_key);

-- ไม่มี index สำหรับทาง SELECT ของบอทโดยเจตนา: ตารางนี้ถูกจำกัดให้เล็ก
-- (ข้อที่เปิดใช้ไม่เกิน ai_chat.PROMPT_RULE_LIMIT ข้อ) seq scan เร็วกว่า
-- index scan ที่ขนาดนี้ และผลลัพธ์ยัง cache ไว้ฝั่งแอปอีกชั้น

COMMENT ON TABLE ai_prompt_rules IS
    'ข้อห้าม/ข้อจำกัดเพิ่มเติมที่ต่อท้าย system prompt ของ AI — prompt หลักอยู่ในโค้ด (app/ai_chat.py) และแก้จากหน้าเว็บไม่ได้';
COMMENT ON COLUMN ai_prompt_rules.rule_key IS
    'กุญแจของแถว ตั้งเอง เช่น no_medical_advice — ใส่ค่าเดิมคือแก้ ใส่ค่าใหม่คือเพิ่ม';
COMMENT ON COLUMN ai_prompt_rules.rule_text IS
    'ข้อความที่ต่อเข้า prompt (2-300 ตัวอักษร) — เป็นข้อจำกัดเพิ่มเติมเท่านั้น ลบล้างกฎหลักไม่ได้';
COMMENT ON COLUMN ai_prompt_rules.note IS
    'บันทึกภายในของผู้ดูแล — ไม่ถูกส่งให้ AI';
COMMENT ON COLUMN ai_prompt_rules.is_active IS
    'ปิด = ไม่ต่อเข้า prompt (ระบบนี้ไม่ลบแถว ดูเหตุผลใน 006_admin.sql)';
COMMENT ON COLUMN ai_prompt_rules.updated_by IS
    'username ของ admin ที่แก้ผ่านหน้า /admin (ใครสร้างครั้งแรก ดูที่ admin_audit_logs action=create)';

COMMIT;
