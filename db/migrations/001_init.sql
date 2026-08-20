-- ============================================================================
--  LINE AI Academic Assistant — Postgres schema
--  ต้องใช้ Postgres 14+ พร้อม extension: vector (pgvector), pg_trgm
--
--  ต่างจาก kb/schema.py (SQLite) ตรงที่:
--    * เพิ่มตารางฝั่ง application (นักศึกษา, session, chat log, FAQ, RAG chunk)
--    * ใช้ pgvector สำหรับ semantic search — ไม่ต้องรัน Chroma/Qdrant แยก
--    * ใช้ pg_trgm สำหรับ fuzzy search ภาษาไทย เพราะ Postgres ไม่มี
--      ตัวตัดคำไทย ทำ full-text search ไทยตรง ๆ ไม่ได้
--
--  รันด้วย:  psql -f db/migrations/001_init.sql
-- ============================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
--  ส่วนที่ 1: ข้อมูลสาธารณะจาก regis.rmu.ac.th (mirror จาก kb/schema.py)
-- ============================================================================

CREATE TABLE IF NOT EXISTS programs (
    program_id      INTEGER PRIMARY KEY,
    faculty_id      TEXT NOT NULL,
    level_id        TEXT NOT NULL,
    program_code    TEXT,
    program_name    TEXT,
    faculty_name    TEXT,
    level_name      TEXT,
    degree_name     TEXT,
    department_name TEXT,
    total_credits   INTEGER,
    source_url      TEXT NOT NULL,
    scraped_at      TIMESTAMPTZ NOT NULL
);

COMMENT ON TABLE programs IS 'หลักสูตร — ข้อมูลสาธารณะ ไม่มีข้อมูลส่วนบุคคล';

CREATE TABLE IF NOT EXISTS categories (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    program_id       INTEGER NOT NULL REFERENCES programs(program_id) ON DELETE CASCADE,
    row_id           INTEGER NOT NULL,
    parent_row_id    INTEGER,
    number           TEXT,
    depth            INTEGER NOT NULL,
    label            TEXT NOT NULL,
    required_credits INTEGER,
    is_leaf          BOOLEAN NOT NULL DEFAULT FALSE,
    selection_mode   TEXT CHECK (selection_mode IN ('required', 'elective')),
    UNIQUE (program_id, row_id)
);

COMMENT ON COLUMN categories.row_id IS 'N จาก toggle_row(N) ในหน้า program_info_1.asp';
COMMENT ON COLUMN categories.selection_mode IS 'required = เรียนทุกวิชา, elective = เลือกให้ครบหน่วยกิต';

CREATE TABLE IF NOT EXISTS courses (
    course_id       INTEGER PRIMARY KEY,
    course_code     TEXT NOT NULL,
    name_th         TEXT,
    name_en         TEXT,
    credits_text    TEXT,
    credits         INTEGER,
    description_th  TEXT,
    faculty_text    TEXT,
    source_url      TEXT,
    scraped_at      TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_courses_code ON courses (course_code);
-- fuzzy search ชื่อวิชาไทย: "ฐานข้อมูล" ควรเจอ "ระบบฐานข้อมูลเบื้องต้น"
CREATE INDEX IF NOT EXISTS idx_courses_name_trgm
    ON courses USING gin (name_th gin_trgm_ops);

CREATE TABLE IF NOT EXISTS program_courses (
    program_id      INTEGER NOT NULL REFERENCES programs(program_id) ON DELETE CASCADE,
    category_row_id INTEGER NOT NULL,
    course_id       INTEGER NOT NULL REFERENCES courses(course_id),
    position        INTEGER,
    PRIMARY KEY (program_id, category_row_id, course_id)
);

CREATE TABLE IF NOT EXISTS offerings (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id     INTEGER NOT NULL REFERENCES courses(course_id),
    course_code   TEXT NOT NULL,
    acad_year     INTEGER NOT NULL,
    semester      SMALLINT NOT NULL CHECK (semester BETWEEN 1 AND 3),
    section       TEXT,
    course_group  TEXT,
    schedule_raw  TEXT,
    instructors   TEXT,
    seats_total   INTEGER,
    seats_taken   INTEGER,
    seats_left    INTEGER,
    status        TEXT,
    source_url    TEXT,
    scraped_at    TIMESTAMPTZ NOT NULL,
    -- NULLS NOT DISTINCT จำเป็น: schedule_raw เป็น NULL ได้ (45/337 แถวไม่มีตาราง
    -- เรียนในหน้าเว็บ) และ Postgres ถือว่า NULL != NULL ในดัชนี unique ปกติ
    -- → ON CONFLICT ไม่จับ → รัน seed ซ้ำแล้วได้แถวซ้ำ 45 แถวทุกครั้ง
    UNIQUE NULLS NOT DISTINCT (course_id, acad_year, semester, section, schedule_raw)
);

CREATE INDEX IF NOT EXISTS idx_offerings_term ON offerings (acad_year, semester);
CREATE INDEX IF NOT EXISTS idx_offerings_code ON offerings (course_code);

CREATE TABLE IF NOT EXISTS offering_slots (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    offering_id BIGINT NOT NULL REFERENCES offerings(id) ON DELETE CASCADE,
    day_code    TEXT CHECK (day_code IN ('MO','TU','WE','TH','FR','SA','SU')),
    start_min   INTEGER CHECK (start_min BETWEEN 0 AND 1439),
    end_min     INTEGER CHECK (end_min BETWEEN 0 AND 1439),
    room        TEXT
);

CREATE INDEX IF NOT EXISTS idx_slots_offering ON offering_slots (offering_id);
-- ใช้ตรวจตารางชน: หาคาบที่วันเดียวกันแล้วเวลาทับ
CREATE INDEX IF NOT EXISTS idx_slots_day_time ON offering_slots (day_code, start_min, end_min);

CREATE TABLE IF NOT EXISTS offering_patterns (
    course_code    TEXT PRIMARY KEY,
    opens_sem1     BOOLEAN NOT NULL DEFAULT FALSE,
    opens_sem2     BOOLEAN NOT NULL DEFAULT FALSE,
    opens_sem3     BOOLEAN NOT NULL DEFAULT FALSE,
    terms_observed INTEGER NOT NULL DEFAULT 0,
    terms_found    INTEGER NOT NULL DEFAULT 0,
    detail         JSONB,
    computed_at    TIMESTAMPTZ NOT NULL
);

COMMENT ON TABLE offering_patterns IS
    'สรุปว่าวิชาเปิดเทอมไหน — ใช้แทนแผนการเรียนที่ระบบทะเบียนไม่มี';

-- ── ข้อมูลที่ระบบทะเบียนไม่มี ต้องกรอกมือจาก มคอ.2 ──────────────────────────
CREATE TABLE IF NOT EXISTS curriculum_rules (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    program_code  TEXT NOT NULL,
    course_code   TEXT NOT NULL,
    std_year      SMALLINT CHECK (std_year BETWEEN 1 AND 8),
    std_semester  SMALLINT CHECK (std_semester BETWEEN 1 AND 3),
    is_fixed_term BOOLEAN NOT NULL DEFAULT FALSE,
    note          TEXT,
    source        TEXT NOT NULL,
    verified_by   TEXT,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (program_code, course_code)
);

COMMENT ON COLUMN curriculum_rules.source IS
    'บังคับใส่ เช่น "มคอ.2 หลักสูตร 643170151 หน้า 42" เพื่อให้บอทอ้างอิงได้';

CREATE TABLE IF NOT EXISTS prerequisites (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    program_code  TEXT NOT NULL,
    course_code   TEXT NOT NULL,
    requires_code TEXT NOT NULL,
    kind          TEXT NOT NULL DEFAULT 'hard'
                  CHECK (kind IN ('hard', 'soft', 'concurrent')),
    source        TEXT NOT NULL,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (program_code, course_code, requires_code),
    -- กันข้อมูลผิดชัด ๆ: วิชาเป็น prerequisite ของตัวเอง
    CHECK (course_code <> requires_code)
);

COMMENT ON COLUMN prerequisites.kind IS
    'hard = ต้องผ่านก่อนจริง, soft = แนะนำให้เรียนก่อน, concurrent = เรียนพร้อมกันได้';

-- ============================================================================
--  ส่วนที่ 2: เอกสาร + อาจารย์
-- ============================================================================

CREATE TABLE IF NOT EXISTS documents (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category       TEXT NOT NULL,
    title          TEXT NOT NULL,
    url            TEXT NOT NULL UNIQUE,
    doc_type       TEXT,
    audience       TEXT NOT NULL DEFAULT 'student'
                   CHECK (audience IN ('student', 'staff')),
    keywords       TEXT,
    note           TEXT,
    source_page    TEXT,
    http_status    INTEGER,
    content_type   TEXT,
    content_length BIGINT,
    is_available   BOOLEAN,
    checked_at     TIMESTAMPTZ,
    scraped_at     TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_cat ON documents (category, audience);
-- FAQ matching ด้วย keyword ไทย เช่น "ดรอปเรียน" → เจอ "พักการเรียน"
CREATE INDEX IF NOT EXISTS idx_documents_kw_trgm
    ON documents USING gin (keywords gin_trgm_ops);

CREATE TABLE IF NOT EXISTS instructors (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name       TEXT NOT NULL UNIQUE,
    name_normalized TEXT NOT NULL,
    title_prefix    TEXT,
    email           TEXT,
    -- ↓ เว็บคณะไม่มีข้อมูลนี้ (0/28) ต้องกรอกมือ — บอทต้องตอบ "ไม่มีข้อมูล" ห้ามเดา
    phone           TEXT,
    building        TEXT,
    floor           TEXT,
    room            TEXT,
    office_hours    TEXT,
    other_contact   TEXT,
    manual_source   TEXT,
    source_url      TEXT,
    scraped_at      TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_instructors_norm ON instructors (name_normalized);
-- ค้นชื่ออาจารย์แบบพิมพ์ไม่ครบ/พิมพ์ผิด
CREATE INDEX IF NOT EXISTS idx_instructors_name_trgm
    ON instructors USING gin (name_normalized gin_trgm_ops);

CREATE TABLE IF NOT EXISTS instructor_affiliations (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instructor_id BIGINT NOT NULL REFERENCES instructors(id) ON DELETE CASCADE,
    group_name    TEXT NOT NULL,
    group_code    TEXT,
    position      TEXT,
    is_chair      BOOLEAN NOT NULL DEFAULT FALSE,
    -- position เป็น NULL ได้ → ต้อง NULLS NOT DISTINCT ด้วยเหตุผลเดียวกับ offerings
    UNIQUE NULLS NOT DISTINCT (instructor_id, group_name, position)
);

-- ============================================================================
--  ส่วนที่ 3: ข้อมูลผู้ใช้ (แผน B — ไม่เก็บรหัสผ่าน ไม่เก็บชื่อ ไม่เก็บเกรด)
-- ============================================================================

-- ผู้ใช้ LINE 1 คน = 1 แถว
--
-- PDPA / data minimization:
--   * เก็บ line_user_id แบบ hash (SHA-256 + pepper) ไม่เก็บค่าดิบ
--   * ไม่เก็บ: ชื่อ-นามสกุล, รหัสนักศึกษา, เลขบัตรประชาชน, เกรด, รหัสผ่าน
--   * เก็บเฉพาะ program_code + ชั้นปี ที่จำเป็นต่อการคำนวณแผนการเรียน
CREATE TABLE IF NOT EXISTS app_users (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    line_user_hash    TEXT NOT NULL UNIQUE,
    program_code      TEXT,
    study_year        SMALLINT CHECK (study_year BETWEEN 1 AND 8),
    entry_year        SMALLINT,
    -- consent ตาม PDPA — ต้องมีก่อนเก็บข้อมูลการเรียน
    consent_version   TEXT,
    consent_at        TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at      TIMESTAMPTZ
);

COMMENT ON COLUMN app_users.line_user_hash IS
    'SHA-256(line_user_id + pepper) — ห้ามเก็บ line_user_id ดิบ';

-- วิชาที่นักศึกษาแจ้งว่าผ่านแล้ว (แผน B: ติ๊กเองผ่าน LIFF)
--
-- เก็บแค่ "ผ่าน/ไม่ผ่าน" ไม่เก็บเกรด → ยังคำนวณหน่วยกิตและ prereq ได้ครบ
-- แต่ลดความอ่อนไหวของข้อมูลลงมาก
CREATE TABLE IF NOT EXISTS user_completed_courses (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    course_code TEXT NOT NULL,
    -- 'self_report' = ติ๊กเอง, 'upload' = อัปโหลดเอกสารแล้ว OCR
    source      TEXT NOT NULL DEFAULT 'self_report'
                CHECK (source IN ('self_report', 'upload')),
    reported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, course_code)
);

-- LIFF session ชั่วคราว (ไม่ใช่ session ของระบบทะเบียน)
--
-- ใช้ผูก LIFF ID token ที่ verify แล้วกับ request ถัดไป
-- อายุสั้น มี TTL — ลบทิ้งด้วย cron/pg_cron
CREATE TABLE IF NOT EXISTS liff_sessions (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id        BIGINT NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    session_token  TEXT NOT NULL UNIQUE,
    expires_at     TIMESTAMPTZ NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_liff_sessions_exp ON liff_sessions (expires_at);

-- ============================================================================
--  ส่วนที่ 4: FAQ + RAG
-- ============================================================================

-- FAQ ที่คนเขียนคำตอบไว้เอง → ตอบได้เลยไม่ต้องเรียก LLM (ประหยัด + แม่น)
CREATE TABLE IF NOT EXISTS faqs (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    intent_key  TEXT NOT NULL UNIQUE,
    question    TEXT NOT NULL,
    answer      TEXT NOT NULL,
    category    TEXT,
    -- คำพ้อง เช่น ['ดรอปเรียน','พักการเรียน','ลาพัก','ขอพักการศึกษา']
    variants    TEXT[] NOT NULL DEFAULT '{}',
    -- Quick Reply ที่จะเสนอต่อ (Requirement ข้อ 13)
    quick_replies JSONB,
    source_url  TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_faqs_variants ON faqs USING gin (variants);
CREATE INDEX IF NOT EXISTS idx_faqs_q_trgm
    ON faqs USING gin (question gin_trgm_ops);

-- ก้อนข้อความสำหรับ RAG (คำอธิบายรายวิชา, เนื้อ PDF, ระเบียบ ฯลฯ)
--
-- มิติ 768 = Gemini text-embedding-004 (ต้องตรงกับ EMBEDDING_DIM ใน .env)
-- ถ้าเปลี่ยน embedding model ต้องแก้เลขนี้ + ALTER คอลัมน์ + re-index ใหม่ทั้งชุด
-- (BGE-M3 = 1024, OpenAI text-embedding-3-small = 1536)
CREATE TABLE IF NOT EXISTS rag_chunks (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_type  TEXT NOT NULL,   -- course_description / document / faq / regulation
    source_ref   TEXT NOT NULL,   -- course_code / documents.url / faqs.intent_key
    title        TEXT,
    content      TEXT NOT NULL,
    -- ต้องมีเพื่อให้บอทอ้างอิงแหล่งที่มาได้ (Requirement ข้อ 11)
    citation_url TEXT,
    chunk_index  INTEGER NOT NULL DEFAULT 0,
    token_count  INTEGER,
    embedding    vector(768),
    model_name   TEXT,
    indexed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_type, source_ref, chunk_index)
);

-- HNSW เร็วกว่า IVFFlat ตอน query และไม่ต้อง train ก่อน
-- cosine distance เพราะ embedding ส่วนใหญ่ normalize มาแล้ว
CREATE INDEX IF NOT EXISTS idx_rag_embedding
    ON rag_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_rag_content_trgm
    ON rag_chunks USING gin (content gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_rag_source ON rag_chunks (source_type, source_ref);

-- ============================================================================
--  ส่วนที่ 5: log / operations
-- ============================================================================

-- log บทสนทนา เพื่อวัดผลในธีสิส (accuracy, fallback rate, intent distribution)
--
-- ไม่เก็บ line_user_id ดิบ — ใช้ user_id ที่อ้างถึง app_users
CREATE TABLE IF NOT EXISTS chat_logs (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id        BIGINT REFERENCES app_users(id) ON DELETE SET NULL,
    message_text   TEXT,
    -- ชั้นที่ตอบ: rich_menu / faq / planner / rag / fallback
    answered_by    TEXT NOT NULL,
    intent_key     TEXT,
    confidence     REAL,
    response_text  TEXT,
    citations      JSONB,
    latency_ms     INTEGER,
    llm_model      TEXT,
    prompt_tokens  INTEGER,
    output_tokens  INTEGER,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_logs_time ON chat_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_logs_by ON chat_logs (answered_by);

CREATE TABLE IF NOT EXISTS scrape_runs (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    task         TEXT NOT NULL,
    target       TEXT,
    status       TEXT NOT NULL CHECK (status IN ('ok', 'partial', 'error')),
    rows_written INTEGER DEFAULT 0,
    message      TEXT,
    started_at   TIMESTAMPTZ NOT NULL,
    finished_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_scrape_runs_task ON scrape_runs (task, started_at DESC);

COMMIT;
