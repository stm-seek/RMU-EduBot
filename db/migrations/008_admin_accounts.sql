-- ============================================================================
--  LINE AI Academic Assistant — บัญชีผู้ดูแลของระบบเราเอง (008)
--  รันต่อจาก 007:  psql -f db/migrations/008_admin_accounts.sql
--
--  ทำไมต้องมีไฟล์นี้:
--
--  เดิมหน้า /admin ยืนยันตัวตนด้วย **LINE Login (LIFF ID token)** แล้วเทียบ
--  ``line_user_hash`` กับรายชื่อใน ``ADMIN_USER_HASHES`` (.env) วิธีนั้นใช้ได้
--  แต่มีต้นทุนที่จ่ายทุกครั้งที่เพิ่ม/ถอนคน: ต้องแก้ไฟล์ .env บนเครื่องจริง
--  แล้ว **รีสตาร์ตเซิร์ฟเวอร์** และคนที่จะเป็น admin ต้องหา hash ของตัวเอง
--  จาก log ก่อน (ขั้นตอน bootstrap ที่อธิบายให้อาจารย์ทำเองไม่ได้จริง)
--
--  ตารางนี้ย้ายรายชื่อผู้ดูแลจาก .env มาอยู่ใน DB เป็น **username + password
--  ของระบบเราเอง** เพิ่ม/ถอน/รีเซ็ตรหัสได้โดยไม่ต้องรีสตาร์ต
--
--  ── เก็บรหัสผ่านอย่างไร ────────────────────────────────────────────────────
--
--  ``password_hash`` เป็น **สตริงเดียว** รูปแบบ::
--
--      scrypt$<n>$<r>$<p>$<salt_b64>$<hash_b64>
--
--  พารามิเตอร์ (n/r/p) ฝังอยู่ในสตริงโดยเจตนา ไม่ได้ hardcode ไว้ในโค้ด:
--  วันหนึ่งเครื่องเร็วขึ้นแล้วต้องขึ้นค่าความหนัก (n) จะขึ้นได้ทันทีสำหรับรหัส
--  ที่ตั้งใหม่ ในขณะที่รหัสเก่ายัง verify ผ่านด้วยค่าเดิมของตัวเอง — ถ้าเก็บแค่
--  hash เปล่า ๆ การขึ้นค่าความหนักจะเท่ากับบังคับล้างรหัสผ่านของทุกคน
--
--  salt สุ่มต่อแถว (ไม่ใช่ pepper รวมแบบ ``app_users.user_id``) เพราะที่นี่
--  **ไม่ต้อง lookup ด้วยค่าที่ hash** — lookup ด้วย username แล้วค่อยเทียบรหัส
--
--  ``scrypt`` มาจาก ``hashlib`` ของ stdlib — โปรเจกต์นี้ตั้งใจไม่เพิ่ม
--  dependency (ไม่มี bcrypt/passlib) และ scrypt เป็น KDF ที่หนักพอสำหรับ
--  หน้าที่มีผู้ใช้ไม่กี่คนและถูกกันการเดาด้วย rate limit อีกชั้น
--
--  **ไม่มีบัญชีเริ่มต้นในไฟล์นี้** — บัญชี/รหัส default คือช่องโหว่ที่ไม่มีใคร
--  ไปลบทิ้ง สร้างบัญชีแรกด้วย::
--
--      python scripts/admin_user.py --username <ชื่อ>
--
--  ตารางว่าง = ไม่มีใครเข้าหน้า /admin ได้ (fail closed) ซึ่งเป็นสถานะที่ถูก
--  สำหรับระบบที่เพิ่งติดตั้งและเปิดออกอินเทอร์เน็ตผ่าน cloudflared
--
--  ── ปิดบัญชี ไม่ลบ ─────────────────────────────────────────────────────────
--
--  ``is_active`` เท่านั้น ไม่มี DELETE ที่ไหนในระบบนี้ (เหตุผลเดียวกับ 006):
--  ประวัติใน ``admin_audit_logs`` อ้างถึง username ของคนที่แก้ข้อมูล ลบแถว
--  บัญชีทิ้งแล้วประวัติจะชี้ไปที่ชื่อที่ไม่มีเจ้าของ แล้วไล่ไม่ได้ว่าใครแก้
--
--  ── audit: จาก hash เป็น username ──────────────────────────────────────────
--
--  ``admin_audit_logs.admin_hash`` เดิมเก็บ ``line_user_hash`` ซึ่งระบบใหม่ไม่มี
--  แล้ว → เพิ่มคอลัมน์ ``admin_username`` และทำ ``admin_hash`` เป็น nullable
--  **ห้ามลบคอลัมน์เก่า** เพราะประวัติที่บันทึกไว้แล้วต้องอ่านต่อได้ (แถวเก่ามี
--  hash ไม่มี username / แถวใหม่มี username ไม่มี hash — อ่านทั้งสองแบบได้)
--
--  idempotent: รันซ้ำได้ทั้งไฟล์
-- ============================================================================

BEGIN;

-- ── 1. ตารางบัญชีผู้ดูแล ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS admin_accounts (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- เก็บเป็นตัวพิมพ์เล็กเสมอ (โค้ดฝั่ง Python lower() ก่อนเขียน/ก่อนค้น)
    -- ส่วน unique index ข้างล่างบังคับซ้ำอีกชั้นด้วย lower() เพื่อไม่ให้เกิด
    -- 'Somchai' กับ 'somchai' เป็นสองบัญชี — คนจะเข้าใจว่าเป็นบัญชีเดียวกัน
    -- แล้วรีเซ็ตรหัสผิดใบโดยไม่รู้ตัว
    username       TEXT NOT NULL,
    password_hash  TEXT NOT NULL,
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login_at  TIMESTAMPTZ
);

-- ไม่ใช้ extension ``citext`` โดยเจตนา: 001_init.sql เปิดไว้แค่ vector กับ
-- pg_trgm — เพิ่ม extension ใหม่ต้องมีสิทธิ์ระดับ superuser บน managed DB
-- บางเจ้า ซึ่งเป็นต้นทุนที่ unique index ตัวนี้แทนได้ทั้งหมด
CREATE UNIQUE INDEX IF NOT EXISTS idx_admin_accounts_username
    ON admin_accounts (lower(username));

COMMENT ON TABLE admin_accounts IS
    'บัญชีผู้ดูแลหน้า /admin — ตารางว่าง = ไม่มีใครเข้าได้ (fail closed)';
COMMENT ON COLUMN admin_accounts.username IS
    'ชื่อผู้ใช้ (เทียบแบบไม่สนตัวพิมพ์ผ่าน unique index บน lower(username))';
COMMENT ON COLUMN admin_accounts.password_hash IS
    'scrypt$<n>$<r>$<p>$<salt_b64>$<hash_b64> — พารามิเตอร์ฝังในสตริงเพื่อขึ้นค่าความหนักได้ทีหลังโดยไม่ต้องล้างรหัสทุกคน';
COMMENT ON COLUMN admin_accounts.is_active IS
    'FALSE = ปิดการใช้งาน (ไม่มี DELETE — ประวัติใน admin_audit_logs อ้าง username นี้)';
COMMENT ON COLUMN admin_accounts.last_login_at IS
    'ล็อกอินสำเร็จครั้งล่าสุด — NULL = สร้างบัญชีแล้วยังไม่เคยเข้า';

-- ── 2. audit: บันทึกคนทำเป็น username ───────────────────────────────────────

ALTER TABLE admin_audit_logs
    ADD COLUMN IF NOT EXISTS admin_username TEXT;

-- แถวเก่าเก็บ line_user_hash ไว้ (NOT NULL) แถวใหม่ไม่มี hash ให้เก็บแล้ว
ALTER TABLE admin_audit_logs
    ALTER COLUMN admin_hash DROP NOT NULL;

CREATE INDEX IF NOT EXISTS idx_admin_audit_username
    ON admin_audit_logs (admin_username, created_at DESC);

COMMENT ON COLUMN admin_audit_logs.admin_username IS
    'username ของ admin ที่แก้ (ระบบใหม่) — แถวก่อน 008 ใช้ admin_hash แทน';
COMMENT ON COLUMN admin_audit_logs.admin_hash IS
    'line_user_hash ของ admin สมัยที่ยังล็อกอินด้วย LINE — nullable ตั้งแต่ 008 แถวใหม่ใช้ admin_username';

-- ── 3. แก้คอมเมนต์ที่ 006 เขียนไว้ตามระบบเดิม ────────────────────────────────
--
-- ``updated_by`` ทุกตารางเคยเก็บ "12 ตัวแรกของ line_user_hash" ตอนนี้เก็บ
-- **username** ของคนที่กดบันทึก คอมเมนต์ที่โกหกอันตรายกว่าไม่มีคอมเมนต์
-- (คนอ่านจะพยายามแปลงค่าที่เห็นกลับเป็น hash แล้วสรุปว่าข้อมูลเสีย)

COMMENT ON COLUMN documents.updated_by IS
    'username ของ admin ที่แก้ผ่านหน้า /admin (ก่อน 008: 12 ตัวแรกของ line_user_hash)';
COMMENT ON COLUMN instructors.updated_by IS
    'username ของ admin ที่แก้ผ่านหน้า /admin (ก่อน 008: 12 ตัวแรกของ line_user_hash)';
COMMENT ON COLUMN faqs.updated_by IS
    'username ของ admin ที่แก้ผ่านหน้า /admin (ก่อน 008: 12 ตัวแรกของ line_user_hash)';
COMMENT ON COLUMN curriculum_rules.updated_by IS
    'username ของ admin ที่แก้ผ่านหน้า /admin (ก่อน 008: 12 ตัวแรกของ line_user_hash)';
COMMENT ON COLUMN prerequisites.updated_by IS
    'username ของ admin ที่แก้ผ่านหน้า /admin (ก่อน 008: 12 ตัวแรกของ line_user_hash)';

COMMIT;
