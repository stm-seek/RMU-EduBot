"""
Repository ของหน้า admin — SQL ทั้งหมดที่ :mod:`app.admin` ใช้

แยกไฟล์จาก :mod:`app.repository` เพราะสองไฟล์นี้มีสิทธิ์ไม่เท่ากัน: repository
อ่านอย่างเดียว (เขียนแค่ log/โปรไฟล์ของเจ้าตัว) ส่วนไฟล์นี้ **เขียนทับข้อมูลที่
บอทเอาไปตอบนักศึกษา** อยู่คนละไฟล์แล้วรีวิวง่ายกว่า และ grep คำถามว่า "อะไร
แก้ตาราง ``faqs`` ได้บ้าง" ได้จบในไฟล์เดียว

กฎที่ยกมาจาก :mod:`app.repository` ทั้งดุ้น (เหตุผลเดียวกัน):

* SQL อยู่เป็นค่าคงที่ระดับโมดูล + ลงทะเบียนใน :data:`ALL_QUERIES` เพื่อให้เทส
  parse ด้วย ``sqlglot`` และเทียบชื่อตารางกับ migration ทุกไฟล์ได้
* placeholder ``%s`` ของ psycopg เท่านั้น — **ห้าม f-string ใส่ค่าผู้ใช้ลง SQL**
  ข้อนี้เข้มกว่าที่อื่นเพราะที่นี่รับค่าจากฟอร์มโดยตรง ไม่ใช่จากคลังข้อมูลตัวเอง

สิ่งที่ตั้งใจ **ไม่** ทำ:

* **ไม่มี ``DELETE`` เลยแม้แต่ statement เดียว** — ปิดด้วย ``is_active``
  (scraper เขียนทับตารางเหล่านี้ ลบทิ้งรอบหน้าก็กลับมาเงียบ ๆ)
* ไม่ให้แก้ ``instructors.full_name``/``name_normalized`` — ชื่อเป็นของ scraper
  ช่องที่คนต้องกรอกคือข้อมูลติดต่อ (วัดแล้ว phone/room ว่าง 0/28 แถว) ถ้าแก้ชื่อ
  ได้ รอบ scrape ถัดไป ``ON CONFLICT (full_name)`` จะไม่แมตช์แล้วกลายเป็นคนสองคน
* ไม่ให้แก้ ``faqs.quick_replies`` (JSONB) — พิมพ์ JSON ผิดในกล่องข้อความแล้ว
  บอทพังตอน *ตอบ* ไม่ใช่ตอน *บันทึก* ซึ่งเป็นความพังที่แพงที่สุด
* upsert ทุกตัว **ไม่แตะ ``is_active``** ตอน ``DO UPDATE`` — การเปิด/ปิดเป็นของ
  ปุ่ม toggle ตัวเดียว ไม่งั้นกดบันทึกแก้คำผิดก็ปลุกแถวที่ปิดไว้ขึ้นมาด้วย
"""

from __future__ import annotations

import json
import logging

from .db import SupportsExecute, SupportsQuery

log = logging.getLogger("app.admin_repo")

# เพดานแถวต่อการเรียกหนึ่งครั้ง — หน้า admin โหลดทั้งตารางมาแสดงในไฟล์ HTML
# ไฟล์เดียว ไม่มี pagination ตารางใหญ่สุดตอนนี้ 33 แถว (documents) ค่านี้จึงเผื่อ
# ไว้เยอะแล้ว และกันหน้าเว็บค้างถ้าวันหนึ่ง chat_logs โตเป็นหมื่นแถว
DEFAULT_LIMIT = 500

# ── อ่าน: รายการทั้งตารางสำหรับหน้าแก้ไข ────────────────────────────────────
#
# ทุกตัวเรียง ``is_active DESC`` ขึ้นก่อนโดยเจตนา: ของที่ปิดไว้ควรอยู่ล่างสุด
# เพราะคนเข้ามาแก้ของที่ใช้งานอยู่ แต่ **ยังต้องเห็น** ของที่ปิด ไม่ใช่กรองหาย
# (กรองหายแล้วจะเปิดกลับไม่ได้เลยจากหน้านี้)

SQL_ADMIN_FAQS = """
SELECT intent_key, question, answer, category, variants, source_url,
       is_active, updated_at, updated_by
FROM faqs
ORDER BY is_active DESC, updated_at DESC, intent_key
LIMIT %s
"""

SQL_ADMIN_DOCUMENTS = """
SELECT url, title, category, doc_type, audience, keywords, note,
       is_available, is_active, updated_at, updated_by
FROM documents
ORDER BY is_active DESC, category, title
LIMIT %s
"""

SQL_ADMIN_INSTRUCTORS = """
SELECT full_name, title_prefix, email, phone, building, floor, room,
       office_hours, other_contact, manual_source,
       is_active, updated_at, updated_by
FROM instructors
ORDER BY is_active DESC, full_name
LIMIT %s
"""

SQL_ADMIN_CURRICULUM_RULES = """
SELECT program_code, course_code, course_code_full, std_year, std_semester,
       is_fixed_term, note, source, group_code, is_active, updated_at, updated_by
FROM curriculum_rules
WHERE program_code = %s
ORDER BY is_active DESC, std_year, std_semester, course_code
LIMIT %s
"""

# โควตาหน่วยกิตรายหมวด (010_electives.sql) — เรียง ``sort_order`` ก่อน
# ``group_code`` ด้วยเหตุผลเดียวกับใน :mod:`app.repository`: '1.1.10' เรียงแบบ
# text จะมาก่อน '1.1.2' ซึ่งไม่ใช่ลำดับที่คนอ่านหลักสูตรคุ้น
#
# **ไม่กรอง is_active** ต่างจาก ``repository.SQL_CURRICULUM_GROUPS`` ที่บอทใช้:
# หน้านี้ต้องเห็นหมวดที่ปิดไว้เพื่อเปิดกลับได้ (กรองหายแล้วปิดคือลบจริง)
SQL_ADMIN_CURRICULUM_GROUPS = """
SELECT program_code, group_code, group_label, required_credits, is_choice,
       sort_order, source, verified_by, is_active, updated_at, updated_by
FROM curriculum_groups
WHERE program_code = %s
ORDER BY is_active DESC, sort_order, group_code
LIMIT %s
"""

# คลังวิชาของแต่ละหมวด — "เลือกให้ครบโควตาได้จริงไหม" ตอบได้ต่อเมื่อรู้ว่าหมวด
# นั้นมีวิชาให้เลือกกี่หน่วยกิต ตัวเลขนี้จึงมาจาก ``curriculum_rules`` ที่ชี้มา
# ไม่ใช่จากตัวโควตาเอง (ดูคำเตือนใน :func:`app.admin.curriculum_group_warnings`)
#
# ``LEFT JOIN LATERAL`` ตามแบบ ``repository.SQL_CURRICULUM_PLAN``: ตาราง
# ``courses`` มีรหัสซ้ำได้ (คนละหลักสูตร/คนละปี) join ตรง ๆ แล้วหน่วยกิตจะถูก
# นับหลายรอบต่อวิชาเดียว ซึ่งทำให้คลังดู "พอ" ทั้งที่ไม่พอ
#
# ``unknown_credits`` = วิชาที่ไม่มีหน่วยกิตในคลังข้อมูล — ถ้ามีแถวแบบนี้
# ผลรวมข้างบนต่ำกว่าความจริง จึงต้องรายงานแยกไม่ใช่เตือนว่าคลังไม่พอ
SQL_ADMIN_CURRICULUM_GROUP_STOCK = """
SELECT cr.group_code,
       count(*) AS course_count,
       coalesce(sum(c.credits), 0) AS stock_credits,
       count(*) FILTER (WHERE c.credits IS NULL) AS unknown_credits
FROM curriculum_rules cr
LEFT JOIN LATERAL (
    SELECT credits
    FROM courses
    WHERE course_code = cr.course_code
    ORDER BY (credits IS NULL), course_id
    LIMIT 1
) c ON TRUE
WHERE cr.program_code = %s
  AND cr.is_active
  AND cr.group_code IS NOT NULL
GROUP BY cr.group_code
"""

# ตัวหารของคำเตือน "ผลรวมโควตาไม่เท่าหลักสูตร" — อ่านเองที่นี่ ไม่เรียกข้าม
# ไปที่ :mod:`app.repository` เพราะไฟล์นี้ลงทะเบียน SQL ของตัวเองให้เทสตรวจ
SQL_ADMIN_PROGRAM_TOTAL_CREDITS = """
SELECT program_code, program_name, total_credits
FROM programs
WHERE program_code = %s
ORDER BY program_id
LIMIT 1
"""

SQL_ADMIN_PREREQUISITES = """
SELECT program_code, course_code, requires_code, kind, source,
       is_active, updated_at, updated_by
FROM prerequisites
WHERE program_code = %s
ORDER BY is_active DESC, course_code, requires_code
LIMIT %s
"""

# กฎเสริมของ AI — เรียง ``created_at`` เป็นตัวที่สองโดยเจตนา (ไม่ใช่
# ``updated_at DESC`` เหมือนตารางอื่น) เพราะลำดับที่เห็นในหน้า admin คือลำดับ
# เดียวกับที่ข้อพวกนี้ถูกต่อเข้า prompt — แก้คำผิดข้อหนึ่งแล้วลำดับในหน้าเว็บ
# สลับ จะอ่านไม่ออกว่ากฎที่ AI เห็นเรียงยังไง
SQL_ADMIN_PROMPT_RULES = """
SELECT rule_key, rule_text, note, is_active, created_at, updated_at, updated_by
FROM ai_prompt_rules
ORDER BY is_active DESC, created_at, rule_key
LIMIT %s
"""

# นับข้อที่ "เปิดใช้" อยู่ — ใช้บังคับเพดานจำนวนข้อก่อนเพิ่ม/เปิดข้อใหม่
# (เพดานข้ามแถวทำเป็น CHECK ใน Postgres ไม่ได้ ดู 009_ai_prompt_rules.sql)
SQL_ADMIN_PROMPT_RULES_ACTIVE_COUNT = """
SELECT count(*) AS active FROM ai_prompt_rules WHERE is_active
"""

# ── อ่าน: chat_logs (อ่านอย่างเดียว — คือ input ของการเขียน FAQ) ─────────────
#
# **ไม่ SELECT ``user_id``** ทั้งที่คอลัมน์นั้นเป็น hash แล้ว: หน้านี้มีไว้อ่าน
# ว่า "คำถามแบบไหนที่บอทตอบไม่ได้" ซึ่งไม่ต้องรู้ว่าใครถาม ส่งออกไปหน้าเว็บ
# แล้วมันจะกลายเป็นเครื่องมือไล่ดูว่าใครถามอะไรทันที ซึ่งไม่ใช่หน้าที่ของ
# หน้านี้ (และ hash เดียวกันตามคนได้ข้ามวัน)
#
# ``message_text`` เป็นข้อความที่นักศึกษาพิมพ์เอง อาจมีรหัสนักศึกษา/ชื่อติดมา
# เลี่ยงไม่ได้เพราะเป็นของที่ต้องอ่านเพื่อเขียน FAQ — จำกัดด้วยการที่หน้านี้
# เข้าได้แค่บัญชีใน ``admin_accounts`` (username+password) และไม่มีปุ่ม export

SQL_ADMIN_CHAT_LOGS = """
SELECT message_text, answered_by, intent_key, confidence, response_text,
       latency_ms, status, created_at
FROM chat_logs
ORDER BY created_at DESC
LIMIT %s
"""

# แยกเป็นค่าคงที่ตัวที่สองแทนการต่อ WHERE ด้วยสตริง — เงื่อนไขที่ประกอบใน
# Python คือจุดที่ SQL injection เกิด และ sqlglot ก็ parse ของที่ประกอบทีหลัง
# ไม่ได้ (เท่ากับ query นี้ไม่มีใครตรวจ)
#
# 'fallback' = ตกถังสุดท้าย, 'no_data' = รู้ว่าถามอะไรแต่ในคลังไม่มีข้อมูล
# สองอันนี้คือรายการงานของคนเขียน FAQ ตรง ๆ
SQL_ADMIN_CHAT_LOGS_UNANSWERED = """
SELECT message_text, answered_by, intent_key, confidence, response_text,
       latency_ms, status, created_at
FROM chat_logs
WHERE answered_by IN ('fallback', 'no_data')
ORDER BY created_at DESC
LIMIT %s
"""

# นับให้หน้าแรกบอกได้ว่า "ยังมีที่ต้องทำอีกเท่าไหร่" โดยไม่ต้องโหลดทุกแถว
SQL_ADMIN_COUNTS = """
SELECT
    (SELECT count(*) FROM faqs) AS faqs,
    (SELECT count(*) FROM faqs WHERE is_active) AS faqs_active,
    (SELECT count(*) FROM documents) AS documents,
    (SELECT count(*) FROM documents WHERE is_active) AS documents_active,
    (SELECT count(*) FROM instructors) AS instructors,
    (SELECT count(*) FROM instructors WHERE phone IS NOT NULL) AS with_phone,
    (SELECT count(*) FROM instructors WHERE room IS NOT NULL) AS with_room,
    (SELECT count(*) FROM curriculum_rules) AS curriculum_rules,
    (SELECT count(*) FROM prerequisites) AS prerequisites,
    (SELECT count(*) FROM ai_prompt_rules) AS ai_prompt_rules,
    (SELECT count(*) FROM ai_prompt_rules WHERE is_active) AS ai_prompt_rules_active,
    (SELECT count(*) FROM chat_logs
      WHERE answered_by IN ('fallback', 'no_data')) AS unanswered
"""

# ── อ่าน: แถวเดียว (ใช้ทำ audit diff ก่อนเขียน) ─────────────────────────────
#
# ต้องอ่านค่าเก่าก่อนทับ ไม่ใช่เพราะอยากได้ log สวย ๆ แต่เพราะ ``UPDATE`` ที่นี่
# ทับข้อมูลที่นักศึกษาจะได้เป็นคำตอบ ถ้าวันหนึ่งคำตอบผิดแล้วไม่มีค่าเก่าเก็บไว้
# ก็ย้อนไม่ได้เลย — ไม่มีที่อื่นในระบบที่เก็บ FAQ เวอร์ชันก่อนหน้า

SQL_ADMIN_FAQ_ROW = """
SELECT intent_key, question, answer, category, variants, source_url, is_active
FROM faqs
WHERE intent_key = %s
"""

SQL_ADMIN_DOCUMENT_ROW = """
SELECT url, title, category, doc_type, audience, keywords, note, is_active
FROM documents
WHERE url = %s
"""

SQL_ADMIN_INSTRUCTOR_ROW = """
SELECT full_name, title_prefix, email, phone, building, floor, room,
       office_hours, other_contact, manual_source, is_active
FROM instructors
WHERE full_name = %s
"""

SQL_ADMIN_CURRICULUM_RULE_ROW = """
SELECT program_code, course_code, course_code_full, std_year, std_semester,
       is_fixed_term, note, source, group_code, is_active
FROM curriculum_rules
WHERE program_code = %s AND course_code = %s
"""

SQL_ADMIN_CURRICULUM_GROUP_ROW = """
SELECT program_code, group_code, group_label, required_credits, is_choice,
       sort_order, source, verified_by, is_active
FROM curriculum_groups
WHERE program_code = %s AND group_code = %s
"""

SQL_ADMIN_PREREQUISITE_ROW = """
SELECT program_code, course_code, requires_code, kind, source, is_active
FROM prerequisites
WHERE program_code = %s AND course_code = %s AND requires_code = %s
"""

SQL_ADMIN_PROMPT_RULE_ROW = """
SELECT rule_key, rule_text, note, is_active
FROM ai_prompt_rules
WHERE rule_key = %s
"""

# ── เขียน: upsert (สร้างใหม่หรือแก้ ใช้ statement เดียว) ────────────────────
#
# ใช้ ``ON CONFLICT`` แทนการเช็คก่อนว่ามีแถวอยู่ไหมแล้วเลือก INSERT/UPDATE
# เพราะสองคำสั่งแยกกันแข่งกันได้ (admin สองคนกดพร้อมกัน = ``UniqueViolation``
# โผล่ใส่หน้าเว็บ) และเพราะเราอยากให้ปุ่ม "บันทึก" ปุ่มเดียวใช้ได้ทั้งสองกรณี
#
# ``updated_by`` = username ของ admin ที่กดบันทึก (ดู 008_admin_accounts.sql
# — ก่อนหน้านั้นเป็น 12 ตัวแรกของ line_user_hash)

SQL_ADMIN_UPSERT_FAQ = """
INSERT INTO faqs (intent_key, question, answer, category, variants,
                  source_url, updated_at, updated_by)
VALUES (%s, %s, %s, %s, %s, %s, now(), %s)
ON CONFLICT (intent_key) DO UPDATE SET
    question   = EXCLUDED.question,
    answer     = EXCLUDED.answer,
    category   = EXCLUDED.category,
    variants   = EXCLUDED.variants,
    source_url = EXCLUDED.source_url,
    updated_at = now(),
    updated_by = EXCLUDED.updated_by
"""

# ``scraped_at``/``source_page`` **ไม่อยู่ใน DO UPDATE** โดยเจตนา: แถวที่ scraper
# เจอมาต้องคงร่องรอยว่ามาจากไหนไว้ แม้คนจะมาแก้ชื่อเรื่องทีหลัง ส่วนแถวที่คน
# เพิ่มเองจะได้ ``source_page = 'admin'`` ตอน INSERT ครั้งแรกครั้งเดียว
SQL_ADMIN_UPSERT_DOCUMENT = """
INSERT INTO documents (url, title, category, doc_type, audience, keywords,
                       note, source_page, scraped_at, updated_at, updated_by)
VALUES (%s, %s, %s, %s, %s, %s, %s, 'admin', now(), now(), %s)
ON CONFLICT (url) DO UPDATE SET
    title      = EXCLUDED.title,
    category   = EXCLUDED.category,
    doc_type   = EXCLUDED.doc_type,
    audience   = EXCLUDED.audience,
    keywords   = EXCLUDED.keywords,
    note       = EXCLUDED.note,
    updated_at = now(),
    updated_by = EXCLUDED.updated_by
"""

# UPDATE ล้วน ไม่มี INSERT: อาจารย์ต้องมีในระบบก่อน (มาจาก scraper) เพราะแถวใหม่
# ต้องมี ``name_normalized`` ที่ตัดคำนำหน้าออกแล้ว ซึ่งเป็นตรรกะของ scraper
# ให้คนกรอกเองแล้วสะกดคนละแบบ = ค้นชื่อไม่เจอ ซึ่งดีบักยากกว่าปัญหาที่แก้
SQL_ADMIN_UPDATE_INSTRUCTOR = """
UPDATE instructors SET
    title_prefix  = %s,
    email         = %s,
    phone         = %s,
    building      = %s,
    floor         = %s,
    room          = %s,
    office_hours  = %s,
    other_contact = %s,
    manual_source = %s,
    updated_at    = now(),
    updated_by    = %s
WHERE full_name = %s
"""

# ``source`` เป็น NOT NULL ตั้งแต่ 001 โดยเจตนา — ทุกกฎหลักสูตรต้องบอกได้ว่า
# มาจากไหน (มคอ.2 หน้าไหน / แผนการเรียนในเว็บ) เพราะข้อมูลชุดนี้คือสิ่งที่
# planner เอาไปบอกนักศึกษาว่าลงวิชาได้ไหม เดาแล้วเสียหายจริง
SQL_ADMIN_UPSERT_CURRICULUM_RULE = """
INSERT INTO curriculum_rules (program_code, course_code, course_code_full,
                              std_year, std_semester, is_fixed_term, note,
                              source, group_code, updated_at, updated_by)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), %s)
ON CONFLICT (program_code, course_code) DO UPDATE SET
    course_code_full = EXCLUDED.course_code_full,
    std_year         = EXCLUDED.std_year,
    std_semester     = EXCLUDED.std_semester,
    is_fixed_term    = EXCLUDED.is_fixed_term,
    note             = EXCLUDED.note,
    source           = EXCLUDED.source,
    group_code       = EXCLUDED.group_code,
    updated_at       = now(),
    updated_by       = EXCLUDED.updated_by
"""

# ``group_code`` **ไม่อยู่ใน DO UPDATE** ไม่ได้ — มันคือครึ่งหนึ่งของ PK
# (แก้รหัสหมวดคือสร้างหมวดใหม่ ไม่ใช่เปลี่ยนชื่อ) endpoint จึงกันไว้อีกชั้น
# ก่อนถึงคำสั่งนี้ ดู ``/api/admin/curriculum_group`` ใน :mod:`app.admin`
#
# ``verified_by`` อยู่ใน DO UPDATE เพราะ **นี่คือเหตุผลที่แท็บนี้ต้องมี**:
# โควตาทั้ง 9 หมวดมาจากใบผลการเรียนของนักศึกษาคนเดียว ยังไม่มีใครเทียบกับ
# มคอ.2 คนที่เทียบแล้วต้องกรอกชื่อตัวเองได้จากหน้าเว็บ ไม่ต้องเขียน migration
SQL_ADMIN_UPSERT_CURRICULUM_GROUP = """
INSERT INTO curriculum_groups (program_code, group_code, group_label,
                               required_credits, is_choice, sort_order,
                               source, verified_by, updated_at, updated_by)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), %s)
ON CONFLICT (program_code, group_code) DO UPDATE SET
    group_label      = EXCLUDED.group_label,
    required_credits = EXCLUDED.required_credits,
    is_choice        = EXCLUDED.is_choice,
    sort_order       = EXCLUDED.sort_order,
    source           = EXCLUDED.source,
    verified_by      = EXCLUDED.verified_by,
    updated_at       = now(),
    updated_by       = EXCLUDED.updated_by
"""

SQL_ADMIN_UPSERT_PREREQUISITE = """
INSERT INTO prerequisites (program_code, course_code, requires_code, kind,
                           source, updated_at, updated_by)
VALUES (%s, %s, %s, %s, %s, now(), %s)
ON CONFLICT (program_code, course_code, requires_code) DO UPDATE SET
    kind       = EXCLUDED.kind,
    source     = EXCLUDED.source,
    updated_at = now(),
    updated_by = EXCLUDED.updated_by
"""

# กฎเสริมของ AI — ``created_at`` ไม่อยู่ใน DO UPDATE โดยเจตนา: ลำดับที่กฎถูก
# ต่อเข้า prompt เรียงตามวันที่สร้าง แก้ข้อความแล้วข้อนั้นไม่ควรกระโดดไปท้ายแถว
SQL_ADMIN_UPSERT_PROMPT_RULE = """
INSERT INTO ai_prompt_rules (rule_key, rule_text, note, updated_at, updated_by)
VALUES (%s, %s, %s, now(), %s)
ON CONFLICT (rule_key) DO UPDATE SET
    rule_text  = EXCLUDED.rule_text,
    note       = EXCLUDED.note,
    updated_at = now(),
    updated_by = EXCLUDED.updated_by
"""

# ── เขียน: เปิด/ปิด (แทนการลบ) ──────────────────────────────────────────────
#
# แยกจาก upsert เป็นคนละคำสั่ง เพราะฟอร์มแก้เนื้อหาไม่ควรมีอำนาจเปลี่ยนสถานะ
# เปิด/ปิด: คนกดบันทึกคำผิดหนึ่งตัวไม่ได้ตั้งใจปลุกแถวที่อีกคนปิดไว้เมื่อวาน

SQL_ADMIN_TOGGLE_FAQ = """
UPDATE faqs SET is_active = %s, updated_at = now(), updated_by = %s
WHERE intent_key = %s
"""

SQL_ADMIN_TOGGLE_DOCUMENT = """
UPDATE documents SET is_active = %s, updated_at = now(), updated_by = %s
WHERE url = %s
"""

SQL_ADMIN_TOGGLE_INSTRUCTOR = """
UPDATE instructors SET is_active = %s, updated_at = now(), updated_by = %s
WHERE full_name = %s
"""

SQL_ADMIN_TOGGLE_CURRICULUM_RULE = """
UPDATE curriculum_rules SET is_active = %s, updated_at = now(), updated_by = %s
WHERE program_code = %s AND course_code = %s
"""

# ปิดหมวด ≠ ลบหมวด: ``curriculum_rules`` 68 แถวชี้มาที่ ``group_code`` โดยไม่มี
# FK (ตั้งใจ ดูหัวไฟล์ 010) ถ้าลบหมวด วิชาที่ชี้มาจะกลายเป็นวิชาที่ไม่มีโควตา
# รองรับแบบเงียบ ๆ — ปิดแล้วคำเตือนบนแท็บยังเห็นว่าเคยมีหมวดนี้อยู่
SQL_ADMIN_TOGGLE_CURRICULUM_GROUP = """
UPDATE curriculum_groups SET is_active = %s, updated_at = now(), updated_by = %s
WHERE program_code = %s AND group_code = %s
"""

SQL_ADMIN_TOGGLE_PREREQUISITE = """
UPDATE prerequisites SET is_active = %s, updated_at = now(), updated_by = %s
WHERE program_code = %s AND course_code = %s AND requires_code = %s
"""

SQL_ADMIN_TOGGLE_PROMPT_RULE = """
UPDATE ai_prompt_rules SET is_active = %s, updated_at = now(), updated_by = %s
WHERE rule_key = %s
"""

SQL_ADMIN_INSERT_AUDIT = """
INSERT INTO admin_audit_logs (admin_username, action, table_name, row_key, changes)
VALUES (%s, %s, %s, %s, %s)
"""

# ``admin_short`` คงชื่อเดิมไว้เพราะหน้าเว็บอ่านคอลัมน์นี้ — แต่ค่าที่อยู่ในนั้น
# เปลี่ยนความหมายตั้งแต่ 008: เดิมคือ 12 ตัวแรกของ ``line_user_hash`` (ค่าที่คน
# อ่านไม่ออก) ตอนนี้คือ **username จริง** ของคนที่แก้ ซึ่งเป็นสิ่งที่คนดู audit
# ต้องการอยู่แล้ว
#
# ``coalesce`` เพราะแถวก่อน 008 ไม่มี ``admin_username`` (มีแต่ hash) —
# ประวัติเก่าต้องอ่านต่อได้ ไม่ใช่กลายเป็นช่องว่าง; hash ยังตัดเหลือ 12 ตัว
# เพื่อไม่ให้ค่าเต็มออกจาก DB ไปหน้าเว็บ
SQL_ADMIN_AUDIT_RECENT = """
SELECT action, table_name, row_key, changes, created_at,
       coalesce(admin_username, left(admin_hash, 12)) AS admin_short
FROM admin_audit_logs
ORDER BY created_at DESC
LIMIT %s
"""

# ── บัญชีผู้ดูแล (008_admin_accounts.sql) ────────────────────────────────────
#
# ``lower(username) = lower(%s)`` ทั้งสองข้าง: index ที่ 008 สร้างเป็น
# ``lower(username)`` → เขียนให้ตรงรูปนั้น Postgres จึงใช้ index ได้ และการเทียบ
# ไม่สนตัวพิมพ์เหมือนกับที่ unique index บังคับไว้ (ไม่งั้นจะมีทางที่ล็อกอิน
# ด้วย 'Somchai' ไม่ผ่านแต่สร้างบัญชีชื่อนั้นซ้ำก็ไม่ได้ ซึ่งอธิบายไม่ได้)
#
# **ไม่มี DELETE** — ปิดด้วย ``is_active`` เท่านั้น (ประวัติใน audit อ้าง username)

SQL_ADMIN_ACCOUNT_BY_USERNAME = """
SELECT username, password_hash, is_active
FROM admin_accounts
WHERE lower(username) = lower(%s)
"""

SQL_ADMIN_ACCOUNT_ANY_ACTIVE = """
SELECT count(*) AS active_count
FROM admin_accounts
WHERE is_active
"""

SQL_ADMIN_ACCOUNT_TOUCH_LOGIN = """
UPDATE admin_accounts SET last_login_at = now()
WHERE lower(username) = lower(%s)
"""

SQL_ADMIN_ACCOUNT_UPSERT = """
INSERT INTO admin_accounts (username, password_hash)
VALUES (lower(%s), %s)
ON CONFLICT (lower(username)) DO UPDATE
SET password_hash = EXCLUDED.password_hash,
    is_active = TRUE
"""

SQL_ADMIN_ACCOUNT_DEACTIVATE = """
UPDATE admin_accounts SET is_active = FALSE
WHERE lower(username) = lower(%s)
"""

SQL_ADMIN_ACCOUNT_LIST = """
SELECT username, is_active, created_at, last_login_at
FROM admin_accounts
ORDER BY is_active DESC, lower(username)
"""


# ── ทะเบียนตาราง: กุญแจ + SQL ของแต่ละตาราง ─────────────────────────────────
#
# ทำเป็น dict เพื่อให้ ``toggle_row``/``fetch_row`` ตัวเดียวใช้กับทุกตารางได้
# **โดยที่ SQL ยังเป็นค่าคงที่** — endpoint รับชื่อตารางมาจากหน้าเว็บแล้วใช้
# ชื่อนั้นเป็น *กุญแจของ dict นี้* ไม่ใช่เอาไปต่อเป็นสตริง SQL ชื่อที่ไม่อยู่ใน
# dict คือ 400 ทันที เท่ากับ allowlist ที่บังคับตัวเองจากโครงสร้างข้อมูล
TABLE_KEYS: dict[str, tuple[str, ...]] = {
    "faqs": ("intent_key",),
    "documents": ("url",),
    "instructors": ("full_name",),
    "curriculum_rules": ("program_code", "course_code"),
    "curriculum_groups": ("program_code", "group_code"),
    "prerequisites": ("program_code", "course_code", "requires_code"),
    "ai_prompt_rules": ("rule_key",),
}

TABLE_ROW_SQL: dict[str, str] = {
    "faqs": SQL_ADMIN_FAQ_ROW,
    "documents": SQL_ADMIN_DOCUMENT_ROW,
    "instructors": SQL_ADMIN_INSTRUCTOR_ROW,
    "curriculum_rules": SQL_ADMIN_CURRICULUM_RULE_ROW,
    "curriculum_groups": SQL_ADMIN_CURRICULUM_GROUP_ROW,
    "prerequisites": SQL_ADMIN_PREREQUISITE_ROW,
    "ai_prompt_rules": SQL_ADMIN_PROMPT_RULE_ROW,
}

TABLE_TOGGLE_SQL: dict[str, str] = {
    "faqs": SQL_ADMIN_TOGGLE_FAQ,
    "documents": SQL_ADMIN_TOGGLE_DOCUMENT,
    "instructors": SQL_ADMIN_TOGGLE_INSTRUCTOR,
    "curriculum_rules": SQL_ADMIN_TOGGLE_CURRICULUM_RULE,
    "curriculum_groups": SQL_ADMIN_TOGGLE_CURRICULUM_GROUP,
    "prerequisites": SQL_ADMIN_TOGGLE_PREREQUISITE,
    "ai_prompt_rules": SQL_ADMIN_TOGGLE_PROMPT_RULE,
}


def row_key(table: str, key: tuple) -> str:
    """
    กุญแจของแถวในรูปสตริงเดียว สำหรับคอลัมน์ ``admin_audit_logs.row_key``

    >>> row_key('prerequisites', ('643170151', '7071102', '7071101'))
    '643170151|7071102|7071101'
    >>> row_key('faqs', ('drop_course',))
    'drop_course'
    """
    return "|".join(str(part) for part in key)


def diff(before: dict | None, after: dict) -> dict:
    """
    เทียบค่าเก่ากับค่าใหม่ → ``{"field": {"from": ..., "to": ...}}``

    เก็บเฉพาะ field ที่เปลี่ยนจริง เพราะ audit ที่บันทึกทุก field ทุกครั้งอ่าน
    ไม่ออกว่าคนกดบันทึกนั้น *เปลี่ยนอะไร* (ปัญหาเดียวกับ diff ที่มีแต่ noise)

    ``before`` เป็น ``None`` = แถวใหม่ → คืนแค่ค่าใหม่ทั้งชุด

    >>> diff({'answer': 'ก', 'category': 'x'}, {'answer': 'ข', 'category': 'x'})
    {'answer': {'from': 'ก', 'to': 'ข'}}
    >>> diff(None, {'answer': 'ก'})
    {'answer': {'to': 'ก'}}
    """
    if before is None:
        return {field: {"to": value} for field, value in after.items()}
    changed = {}
    for field, value in after.items():
        old = before.get(field)
        if old != value:
            changed[field] = {"from": old, "to": value}
    return changed


# ── ฟังก์ชันอ่าน ────────────────────────────────────────────────────────────


async def counts(db: SupportsQuery) -> dict:
    """ตัวเลขสรุปหน้าแรกของ admin — ไม่มีข้อมูลก็คืน dict ว่าง ไม่ใช่ระเบิด"""
    return await db.fetch_one(SQL_ADMIN_COUNTS) or {}


async def list_faqs(db: SupportsQuery, limit: int = DEFAULT_LIMIT) -> list[dict]:
    return await db.fetch_all(SQL_ADMIN_FAQS, (limit,))


async def list_documents(db: SupportsQuery, limit: int = DEFAULT_LIMIT) -> list[dict]:
    return await db.fetch_all(SQL_ADMIN_DOCUMENTS, (limit,))


async def list_instructors(db: SupportsQuery, limit: int = DEFAULT_LIMIT) -> list[dict]:
    return await db.fetch_all(SQL_ADMIN_INSTRUCTORS, (limit,))


async def list_curriculum_rules(
    db: SupportsQuery, program_code: str, limit: int = DEFAULT_LIMIT
) -> list[dict]:
    return await db.fetch_all(SQL_ADMIN_CURRICULUM_RULES, (program_code, limit))


async def list_curriculum_groups(
    db: SupportsQuery, program_code: str, limit: int = DEFAULT_LIMIT
) -> list[dict]:
    return await db.fetch_all(SQL_ADMIN_CURRICULUM_GROUPS, (program_code, limit))


async def curriculum_group_stock(db: SupportsQuery, program_code: str) -> dict[str, dict]:
    """
    คลังวิชาต่อหมวด → ``{group_code: {course_count, stock_credits, unknown_credits}}``

    คืนเป็น dict ไม่ใช่ list เพราะผู้ใช้ฝั่งเดียวของมันคือคำเตือนที่ต้องถาม
    "หมวดนี้มีวิชาให้เลือกกี่หน่วยกิต" ทีละหมวด — คืน list แล้วต้องวนหาเองทุกครั้ง
    หมวดที่ไม่มีวิชาชี้มาเลย (เลือกเสรี) **จะไม่มีคีย์ในนี้** ซึ่งเป็นสิ่งที่
    คำเตือนใช้แยกแยะว่า "คลังไม่พอ" กับ "หมวดที่ไม่ได้ระบุรายวิชาโดยเจตนา"
    """
    rows = await db.fetch_all(SQL_ADMIN_CURRICULUM_GROUP_STOCK, (program_code,))
    return {
        row["group_code"]: {
            "course_count": int(row.get("course_count") or 0),
            "stock_credits": int(row.get("stock_credits") or 0),
            "unknown_credits": int(row.get("unknown_credits") or 0),
        }
        for row in rows
        if row.get("group_code")
    }


async def program_total_credits(db: SupportsQuery, program_code: str) -> int | None:
    """
    หน่วยกิตรวมของหลักสูตร — ``None`` เมื่อไม่มีแถว/ไม่ได้กรอกไว้

    คืน ``None`` แทน 0 โดยเจตนา: 0 จะทำให้คำเตือนบอกว่า "โควตาเกินหลักสูตร
    120 นก." ทั้งที่ความจริงคือ *ไม่รู้* ว่าหลักสูตรต้องกี่หน่วยกิต
    """
    row = await db.fetch_one(SQL_ADMIN_PROGRAM_TOTAL_CREDITS, (program_code,))
    if not row or row.get("total_credits") is None:
        return None
    return int(row["total_credits"])


async def list_prerequisites(
    db: SupportsQuery, program_code: str, limit: int = DEFAULT_LIMIT
) -> list[dict]:
    return await db.fetch_all(SQL_ADMIN_PREREQUISITES, (program_code, limit))


async def list_prompt_rules(
    db: SupportsQuery, limit: int = DEFAULT_LIMIT
) -> list[dict]:
    """กฎเสริมของ AI ทุกข้อ (รวมข้อที่ปิดไว้ — ปิดแล้วต้องเปิดกลับได้)"""
    return await db.fetch_all(SQL_ADMIN_PROMPT_RULES, (limit,))


async def active_prompt_rule_count(db: SupportsQuery) -> int:
    """
    จำนวนกฎเสริมที่เปิดใช้อยู่ — ใช้กันไม่ให้บล็อกกฎเสริมบวมเกิน prompt หลัก

    นับที่ DB ไม่ใช่นับจากรายการที่โหลดมาแสดง เพราะสองคนกดเพิ่มพร้อมกันได้
    (ยังไม่ใช่การกันแบบ atomic — เพดานนี้กันความบวมของ prompt ไม่ใช่กันคนร้าย
    และค่าที่เกินไปหนึ่งข้อไม่ทำให้ระบบพัง ตอนประกอบ prompt ตัดให้อีกชั้นแล้ว)
    """
    row = await db.fetch_one(SQL_ADMIN_PROMPT_RULES_ACTIVE_COUNT)
    return int((row or {}).get("active") or 0)


async def list_chat_logs(
    db: SupportsQuery, *, unanswered_only: bool = True, limit: int = 100
) -> list[dict]:
    """
    บทสนทนาล่าสุด — default เอาแต่ที่ตอบไม่ได้

    default เป็น ``True`` เพราะนี่คือเหตุผลที่หน้านี้มีอยู่: อ่านคำถามที่บอท
    ตอบไม่ได้แล้วเอาไปเขียน FAQ ไม่ใช่ไล่ดูว่าใครคุยอะไร
    """
    sql = SQL_ADMIN_CHAT_LOGS_UNANSWERED if unanswered_only else SQL_ADMIN_CHAT_LOGS
    return await db.fetch_all(sql, (limit,))


async def list_audit(db: SupportsQuery, limit: int = 50) -> list[dict]:
    return await db.fetch_all(SQL_ADMIN_AUDIT_RECENT, (limit,))


# ── บัญชีผู้ดูแล: ฝั่งอ่านที่ตอนล็อกอินใช้ ───────────────────────────────────
#
# สามฟังก์ชันนี้แยกจากกันเพราะ ``app.admin.login`` ต้องรู้สองเรื่องที่ต่างกัน:
# "มีบัญชีที่เปิดใช้อยู่ไหมทั้งระบบ" (ตอบ 403 ถ้าไม่มี — ระบบยังตั้งไม่เสร็จ)
# กับ "บัญชีชื่อนี้มีไหม" (ตอบ 401 ข้อความกลาง ๆ ทั้งกรณีไม่มีชื่อและรหัสผิด)


async def find_account(db: SupportsQuery, username: str) -> dict | None:
    """
    หาบัญชีจาก username (ไม่สนตัวพิมพ์) — ``None`` = ไม่มีบัญชีชื่อนี้

    คืน ``is_active`` มาด้วย **ไม่กรองทิ้งใน SQL** โดยเจตนา: ผู้เรียกต้องเสีย
    เวลา verify รหัสผ่านเท่ากันทั้งบัญชีที่ปิดและบัญชีที่เปิด ไม่งั้นเวลาตอบจะ
    บอกได้ว่าบัญชีชื่อนี้มีอยู่แต่ถูกปิด
    """
    return await db.fetch_one(SQL_ADMIN_ACCOUNT_BY_USERNAME, (username,))


async def has_active_account(db: SupportsQuery) -> bool:
    """
    มีบัญชีที่เปิดใช้อยู่ไหม — ``False`` = ยังไม่มีใครเข้าหน้านี้ได้เลย

    ถามก่อนเทียบรหัสผ่านทุกครั้ง เพราะ "ระบบยังไม่มีบัญชี" กับ "รหัสผิด" เป็น
    สองสถานะที่คนตั้งระบบต้องแยกออกจากกันได้จาก log (ส่วนคนนอกไม่ได้เห็นความ
    ต่างนี้ — ดู ``app.admin``)
    """
    row = await db.fetch_one(SQL_ADMIN_ACCOUNT_ANY_ACTIVE)
    return bool(row and row.get("active_count"))


async def touch_last_login(db: SupportsExecute, username: str) -> None:
    """
    ประทับเวลาล็อกอินสำเร็จ — **ห้ามให้ error หลุด** (เหตุผลเดียวกับ audit)

    ล็อกอินสำเร็จแล้วแต่ประทับเวลาไม่ได้ ไม่ควรกลายเป็นล็อกอินไม่ผ่าน
    (คนจะพิมพ์รหัสซ้ำจนติด rate limit ของตัวเอง)
    """
    try:
        await db.execute(SQL_ADMIN_ACCOUNT_TOUCH_LOGIN, (username,))
    except Exception as exc:  # pragma: no cover - ต้องมี DB จริงจะทดสอบได้
        log.error("อัปเดต last_login_at ไม่สำเร็จ: %s", exc)


async def fetch_row(db: SupportsQuery, table: str, key: tuple) -> dict | None:
    """แถวเดียวก่อนถูกทับ — ``None`` ถ้ายังไม่มี (= การบันทึกครั้งนี้คือการสร้าง)"""
    return await db.fetch_one(TABLE_ROW_SQL[table], key)


# ── ฟังก์ชันเขียน ───────────────────────────────────────────────────────────
#
# ทุกตัวรับ ``admin_username`` (ชื่อผู้ใช้ที่ล็อกอินอยู่) แล้วลง ``updated_by``
# ตรง ๆ — ก่อน 008 ช่องนี้เก็บ 12 ตัวแรกของ ``line_user_hash`` ซึ่งคนอ่านไม่ออก
# ว่าเป็นใคร ตอนนี้เก็บชื่อจริงซึ่งเป็นข้อมูลที่คนดูตารางต้องการอยู่แล้ว
#
# ทุกตัว **อ่านค่าเก่า → เขียน → บันทึก audit** เป็นชุด ผู้เรียกลืมเขียน audit
# ไม่ได้เพราะไม่มีทางเรียกเฉพาะการเขียน (SQL upsert ไม่ export ออกไปใช้ที่อื่น)


async def write_audit(
    db: SupportsExecute,
    *,
    admin_username: str,
    action: str,
    table: str,
    key: tuple,
    changes: dict,
) -> None:
    """
    บันทึก audit — **ไม่ให้ error หลุดออกไป**

    การเขียน audit ล้มไม่ควรทำให้การแก้ข้อมูลที่สำเร็จแล้วดูเหมือนล้มเหลว
    (คนจะกดบันทึกซ้ำ) ที่นี่จึงกลืน exception แล้ว log ไว้ที่ระดับ ERROR
    ให้เห็นชัดว่ามีรอยขาดใน audit trail
    """
    try:
        await db.execute(
            SQL_ADMIN_INSERT_AUDIT,
            (
                admin_username,
                action,
                table,
                row_key(table, key),
                json.dumps(changes, ensure_ascii=False, default=str),
            ),
        )
    except Exception as exc:  # pragma: no cover - ต้องมี DB จริงจะทดสอบได้
        log.error("บันทึก audit ไม่สำเร็จ (%s %s): %s", action, table, exc)


async def save_faq(
    db: SupportsExecute,
    *,
    admin_username: str,
    intent_key: str,
    question: str,
    answer: str,
    category: str | None,
    variants: list[str],
    source_url: str | None,
) -> dict:
    """
    เขียน FAQ หนึ่งข้อ (สร้างใหม่ถ้ายังไม่มี) → คืน ``{"action", "changes"}``

    ``variants`` ส่งเป็น list ตรง ๆ — psycopg map list ของ Python เป็น
    ``TEXT[]`` ให้เอง ไม่ต้องประกอบสตริง ``{a,b}`` ด้วยมือ (ประกอบเองแล้วชื่อ
    ที่มีคอมมา/ปีกกาจะทำ array พังเงียบ ๆ)
    """
    key = (intent_key,)
    before = await fetch_row(db, "faqs", key)
    after = {
        "question": question,
        "answer": answer,
        "category": category,
        "variants": variants,
        "source_url": source_url,
    }
    await db.execute(
        SQL_ADMIN_UPSERT_FAQ,
        (
            intent_key,
            question,
            answer,
            category,
            variants,
            source_url,
            admin_username,
        ),
    )
    action = "update" if before else "create"
    changes = diff(before, after)
    await write_audit(
        db, admin_username=admin_username, action=action, table="faqs", key=key,
        changes=changes,
    )
    return {"action": action, "changes": changes}


async def save_document(
    db: SupportsExecute,
    *,
    admin_username: str,
    url: str,
    title: str,
    category: str,
    doc_type: str | None,
    audience: str,
    keywords: str | None,
    note: str | None,
) -> dict:
    """เขียนเอกสารหนึ่งฉบับ (สร้างใหม่ถ้า url ยังไม่มี)"""
    key = (url,)
    before = await fetch_row(db, "documents", key)
    after = {
        "title": title,
        "category": category,
        "doc_type": doc_type,
        "audience": audience,
        "keywords": keywords,
        "note": note,
    }
    await db.execute(
        SQL_ADMIN_UPSERT_DOCUMENT,
        (
            url, title, category, doc_type, audience, keywords, note,
            admin_username,
        ),
    )
    action = "update" if before else "create"
    changes = diff(before, after)
    await write_audit(
        db, admin_username=admin_username, action=action, table="documents", key=key,
        changes=changes,
    )
    return {"action": action, "changes": changes}


async def save_instructor(
    db: SupportsExecute,
    *,
    admin_username: str,
    full_name: str,
    title_prefix: str | None,
    email: str | None,
    phone: str | None,
    building: str | None,
    floor: str | None,
    room: str | None,
    office_hours: str | None,
    other_contact: str | None,
    manual_source: str | None,
) -> dict:
    """
    แก้ข้อมูลติดต่ออาจารย์ — **แถวต้องมีอยู่แล้ว** (ดูเหตุผลบนหัวไฟล์)

    ``manual_source`` = คนกรอกรู้มาจากไหน ("โทรถามธุรการ 27 ส.ค. 69") ไม่ใช่
    ช่องไว้สวย: schema 001 เขียนไว้ว่าเบอร์โทร/ห้องต้องกรอกมือและ **ห้ามเดา**
    ถ้าไม่รู้ว่าค่าที่เห็นมาจากไหน วันหลังก็ตัดสินไม่ได้ว่าควรเชื่อไหม
    """
    key = (full_name,)
    before = await fetch_row(db, "instructors", key)
    if before is None:
        raise LookupError(f"ไม่พบอาจารย์ชื่อ {full_name!r} ในระบบ")
    after = {
        "title_prefix": title_prefix,
        "email": email,
        "phone": phone,
        "building": building,
        "floor": floor,
        "room": room,
        "office_hours": office_hours,
        "other_contact": other_contact,
        "manual_source": manual_source,
    }
    await db.execute(
        SQL_ADMIN_UPDATE_INSTRUCTOR,
        (
            title_prefix, email, phone, building, floor, room, office_hours,
            other_contact, manual_source, admin_username, full_name,
        ),
    )
    changes = diff(before, after)
    await write_audit(
        db, admin_username=admin_username, action="update", table="instructors",
        key=key, changes=changes,
    )
    return {"action": "update", "changes": changes}


async def save_curriculum_rule(
    db: SupportsExecute,
    *,
    admin_username: str,
    program_code: str,
    course_code: str,
    course_code_full: str | None,
    std_year: int,
    std_semester: int,
    is_fixed_term: bool,
    note: str | None,
    source: str,
    group_code: str | None = None,
) -> dict:
    """
    เขียนกฎแผนการเรียนหนึ่งวิชา

    ``course_code`` คือรหัส **7 หลัก** (ใช้ JOIN ตาราง ``courses``) ส่วน
    ``course_code_full`` คือรหัสเต็มที่มีขีดหน่วยกิต ('7071102-3') — สองอันนี้
    แยกกันมาตั้งแต่ 005_planner.sql ใส่รหัสเต็มลงช่อง 7 หลักแล้ว JOIN จะไม่เจอ
    ชื่อวิชา แล้วหน้า LIFF จะขึ้น "(ไม่มีชื่อวิชาในคลังข้อมูล)"
    """
    key = (program_code, course_code)
    before = await fetch_row(db, "curriculum_rules", key)
    after = {
        "course_code_full": course_code_full,
        "std_year": std_year,
        "std_semester": std_semester,
        "is_fixed_term": is_fixed_term,
        "note": note,
        "source": source,
        "group_code": group_code,
    }
    await db.execute(
        SQL_ADMIN_UPSERT_CURRICULUM_RULE,
        (
            program_code, course_code, course_code_full, std_year, std_semester,
            is_fixed_term, note, source, group_code, admin_username,
        ),
    )
    action = "update" if before else "create"
    changes = diff(before, after)
    await write_audit(
        db, admin_username=admin_username, action=action, table="curriculum_rules",
        key=key, changes=changes,
    )
    return {"action": action, "changes": changes}


async def save_curriculum_group(
    db: SupportsExecute,
    *,
    admin_username: str,
    program_code: str,
    group_code: str,
    group_label: str,
    required_credits: int,
    is_choice: bool,
    sort_order: int,
    source: str,
    verified_by: str | None,
) -> dict:
    """
    เขียนโควตาหน่วยกิตของหมวดหนึ่ง

    ``required_credits`` ของทุกหมวดที่เปิดใช้รวมกันต้องเท่ากับ
    ``programs.total_credits`` — ที่นี่ **ไม่บังคับ** เพราะบังคับแล้วจะแก้
    ทีละหมวดไม่ได้เลย (ย้าย 3 นก. จากหมวด ก ไปหมวด ข ต้องผ่านสถานะที่ผลรวมผิด
    หนึ่งจังหวะ) จึงคุมด้วย *คำเตือน* บนแท็บแทน ดู
    :func:`app.admin.curriculum_group_warnings` — คำเตือนนั้นคือกับดักหลักของ
    งานวิชาเลือกทั้งงาน ห้ามเอาออก

    ``is_choice`` = หมวดนี้เป็นคลังให้เลือก (คลังมากกว่าโควตา) ไม่ใช่ "ต้องผ่าน
    ทุกวิชา" — planner ใช้ค่านี้ตัดสินว่าจะแนะนำวิชาในหมวดต่อหรือหยุด
    """
    key = (program_code, group_code)
    before = await fetch_row(db, "curriculum_groups", key)
    after = {
        "group_label": group_label,
        "required_credits": required_credits,
        "is_choice": is_choice,
        "sort_order": sort_order,
        "source": source,
        "verified_by": verified_by,
    }
    await db.execute(
        SQL_ADMIN_UPSERT_CURRICULUM_GROUP,
        (
            program_code, group_code, group_label, required_credits, is_choice,
            sort_order, source, verified_by, admin_username,
        ),
    )
    action = "update" if before else "create"
    changes = diff(before, after)
    await write_audit(
        db, admin_username=admin_username, action=action, table="curriculum_groups",
        key=key, changes=changes,
    )
    return {"action": action, "changes": changes}


async def save_prerequisite(
    db: SupportsExecute,
    *,
    admin_username: str,
    program_code: str,
    course_code: str,
    requires_code: str,
    kind: str,
    source: str,
) -> dict:
    """
    เขียนเงื่อนไขวิชาบังคับก่อนหนึ่งข้อ

    ``kind``: 'hard' = ต้องผ่านก่อนจริง ๆ, 'soft' = แนะนำให้ผ่านก่อน,
    'concurrent' = ลงพร้อมกันได้ (CHECK ใน 001_init.sql บังคับไว้แค่สามค่านี้)
    """
    key = (program_code, course_code, requires_code)
    before = await fetch_row(db, "prerequisites", key)
    after = {"kind": kind, "source": source}
    await db.execute(
        SQL_ADMIN_UPSERT_PREREQUISITE,
        (
            program_code, course_code, requires_code, kind, source,
            admin_username,
        ),
    )
    action = "update" if before else "create"
    changes = diff(before, after)
    await write_audit(
        db, admin_username=admin_username, action=action, table="prerequisites",
        key=key, changes=changes,
    )
    return {"action": action, "changes": changes}


async def save_prompt_rule(
    db: SupportsExecute,
    *,
    admin_username: str,
    rule_key: str,
    rule_text: str,
    note: str | None,
) -> dict:
    """
    เขียนกฎเสริมของ AI หนึ่งข้อ (สร้างใหม่ถ้า ``rule_key`` ยังไม่มี)

    ที่นี่ **ไม่ตรวจเนื้อหา** ให้ตรวจที่ :mod:`app.admin` ที่เดียว (ความยาว
    ตัวอักษรควบคุม จำนวนข้อที่เปิดใช้) เหมือนตารางอื่นในไฟล์นี้ — ชั้นนี้มี
    หน้าที่เดียวคือ "อ่านค่าเก่า → เขียน → บันทึก audit"

    ไม่มีการลบเช่นเดิม: เลิกใช้กฎข้อไหนให้ปิดด้วย ``toggle_row`` ประวัติว่า
    เคยมีกฎอะไรบังคับ AI อยู่ช่วงไหนเป็นข้อมูลที่ต้องตอบให้ได้ย้อนหลัง
    """
    key = (rule_key,)
    before = await fetch_row(db, "ai_prompt_rules", key)
    after = {"rule_text": rule_text, "note": note}
    await db.execute(
        SQL_ADMIN_UPSERT_PROMPT_RULE,
        (rule_key, rule_text, note, admin_username),
    )
    action = "update" if before else "create"
    changes = diff(before, after)
    await write_audit(
        db, admin_username=admin_username, action=action, table="ai_prompt_rules",
        key=key, changes=changes,
    )
    return {"action": action, "changes": changes}


async def toggle_row(
    db: SupportsExecute,
    *,
    admin_username: str,
    table: str,
    key: tuple,
    is_active: bool,
) -> dict:
    """
    เปิด/ปิดแถวหนึ่งแถว — **แทนการลบ** (ดูเหตุผลใน 006_admin.sql)

    ``table`` ต้องเป็นกุญแจของ :data:`TABLE_TOGGLE_SQL` ผู้เรียกที่ส่งชื่ออื่นมา
    จะได้ ``KeyError`` ที่นี่ ไม่ได้ไปโผล่เป็น SQL แปลก ๆ ที่ฐานข้อมูล
    """
    sql = TABLE_TOGGLE_SQL[table]
    before = await fetch_row(db, table, key)
    if before is None:
        raise LookupError(f"ไม่พบแถว {row_key(table, key)!r} ในตาราง {table}")
    affected = await db.execute(sql, (is_active, admin_username, *key))
    changes = {"is_active": {"from": before.get("is_active"), "to": is_active}}
    await write_audit(
        db, admin_username=admin_username, action="toggle", table=table, key=key,
        changes=changes,
    )
    return {"action": "toggle", "affected": affected, "changes": changes}


# ── ทะเบียน SQL (เทสเทียบกับ dir() ของโมดูลนี้ — ลืมลงทะเบียน = เทสแดง) ──────

ALL_QUERIES: dict[str, str] = {
    "SQL_ADMIN_FAQS": SQL_ADMIN_FAQS,
    "SQL_ADMIN_DOCUMENTS": SQL_ADMIN_DOCUMENTS,
    "SQL_ADMIN_INSTRUCTORS": SQL_ADMIN_INSTRUCTORS,
    "SQL_ADMIN_CURRICULUM_RULES": SQL_ADMIN_CURRICULUM_RULES,
    "SQL_ADMIN_CURRICULUM_GROUPS": SQL_ADMIN_CURRICULUM_GROUPS,
    "SQL_ADMIN_CURRICULUM_GROUP_STOCK": SQL_ADMIN_CURRICULUM_GROUP_STOCK,
    "SQL_ADMIN_PROGRAM_TOTAL_CREDITS": SQL_ADMIN_PROGRAM_TOTAL_CREDITS,
    "SQL_ADMIN_PREREQUISITES": SQL_ADMIN_PREREQUISITES,
    "SQL_ADMIN_PROMPT_RULES": SQL_ADMIN_PROMPT_RULES,
    "SQL_ADMIN_PROMPT_RULES_ACTIVE_COUNT": SQL_ADMIN_PROMPT_RULES_ACTIVE_COUNT,
    "SQL_ADMIN_CHAT_LOGS": SQL_ADMIN_CHAT_LOGS,
    "SQL_ADMIN_CHAT_LOGS_UNANSWERED": SQL_ADMIN_CHAT_LOGS_UNANSWERED,
    "SQL_ADMIN_COUNTS": SQL_ADMIN_COUNTS,
    "SQL_ADMIN_FAQ_ROW": SQL_ADMIN_FAQ_ROW,
    "SQL_ADMIN_DOCUMENT_ROW": SQL_ADMIN_DOCUMENT_ROW,
    "SQL_ADMIN_INSTRUCTOR_ROW": SQL_ADMIN_INSTRUCTOR_ROW,
    "SQL_ADMIN_CURRICULUM_RULE_ROW": SQL_ADMIN_CURRICULUM_RULE_ROW,
    "SQL_ADMIN_CURRICULUM_GROUP_ROW": SQL_ADMIN_CURRICULUM_GROUP_ROW,
    "SQL_ADMIN_PREREQUISITE_ROW": SQL_ADMIN_PREREQUISITE_ROW,
    "SQL_ADMIN_PROMPT_RULE_ROW": SQL_ADMIN_PROMPT_RULE_ROW,
    "SQL_ADMIN_UPSERT_FAQ": SQL_ADMIN_UPSERT_FAQ,
    "SQL_ADMIN_UPSERT_DOCUMENT": SQL_ADMIN_UPSERT_DOCUMENT,
    "SQL_ADMIN_UPDATE_INSTRUCTOR": SQL_ADMIN_UPDATE_INSTRUCTOR,
    "SQL_ADMIN_UPSERT_CURRICULUM_RULE": SQL_ADMIN_UPSERT_CURRICULUM_RULE,
    "SQL_ADMIN_UPSERT_CURRICULUM_GROUP": SQL_ADMIN_UPSERT_CURRICULUM_GROUP,
    "SQL_ADMIN_UPSERT_PREREQUISITE": SQL_ADMIN_UPSERT_PREREQUISITE,
    "SQL_ADMIN_UPSERT_PROMPT_RULE": SQL_ADMIN_UPSERT_PROMPT_RULE,
    "SQL_ADMIN_TOGGLE_FAQ": SQL_ADMIN_TOGGLE_FAQ,
    "SQL_ADMIN_TOGGLE_DOCUMENT": SQL_ADMIN_TOGGLE_DOCUMENT,
    "SQL_ADMIN_TOGGLE_INSTRUCTOR": SQL_ADMIN_TOGGLE_INSTRUCTOR,
    "SQL_ADMIN_TOGGLE_CURRICULUM_RULE": SQL_ADMIN_TOGGLE_CURRICULUM_RULE,
    "SQL_ADMIN_TOGGLE_CURRICULUM_GROUP": SQL_ADMIN_TOGGLE_CURRICULUM_GROUP,
    "SQL_ADMIN_TOGGLE_PREREQUISITE": SQL_ADMIN_TOGGLE_PREREQUISITE,
    "SQL_ADMIN_TOGGLE_PROMPT_RULE": SQL_ADMIN_TOGGLE_PROMPT_RULE,
    "SQL_ADMIN_INSERT_AUDIT": SQL_ADMIN_INSERT_AUDIT,
    "SQL_ADMIN_AUDIT_RECENT": SQL_ADMIN_AUDIT_RECENT,
    "SQL_ADMIN_ACCOUNT_BY_USERNAME": SQL_ADMIN_ACCOUNT_BY_USERNAME,
    "SQL_ADMIN_ACCOUNT_ANY_ACTIVE": SQL_ADMIN_ACCOUNT_ANY_ACTIVE,
    "SQL_ADMIN_ACCOUNT_TOUCH_LOGIN": SQL_ADMIN_ACCOUNT_TOUCH_LOGIN,
    "SQL_ADMIN_ACCOUNT_UPSERT": SQL_ADMIN_ACCOUNT_UPSERT,
    "SQL_ADMIN_ACCOUNT_DEACTIVATE": SQL_ADMIN_ACCOUNT_DEACTIVATE,
    "SQL_ADMIN_ACCOUNT_LIST": SQL_ADMIN_ACCOUNT_LIST,
}
