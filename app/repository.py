"""
Repository — SQL ทั้งหมดของชั้นที่ 1 (ตอบจากฐานข้อมูลตรง ๆ)

ชั้นนี้ **ไม่เรียก LLM เลย**: เร็ว ฟรี และแม่น 100% ตาม Requirement ข้อ 4.4
เรื่องที่คำนวณได้แน่นอน (มีเอกสารกี่ฉบับ, วิชาเปิดเทอมไหน, ใครสอนกลุ่มไหน)
ห้ามให้ LLM เดา เพราะถ้าตอบผิดนักศึกษาเสียหายจริง

หลักการเขียน SQL ในไฟล์นี้:

* **SQL อยู่เป็นค่าคงที่ระดับโมดูล** เพื่อให้เทสหยิบไป parse ด้วย ``sqlglot``
  และเทียบชื่อตารางกับ ``001_init.sql`` ได้ (ดู :mod:`tests.test_repository`)
* ใช้ placeholder ``%s`` ของ psycopg เท่านั้น — **ห้าม f-string ใส่ค่าผู้ใช้**
  ลง SQL (SQL injection)
* กรองเอกสารที่ลิงก์ตายออก (``is_available``) เพราะส่งลิงก์เสียให้นักศึกษา
  แย่กว่าไม่ส่งเลย — รอบตรวจ 22 ส.ค. 2026 ทั้ง 33 ฉบับเข้าได้ครบ ถ้าลิงก์
  ตายอีกครั้งตัวกรองจะตัดออกเองเหมือนเดิม
* **ทุก query ที่อ่านข้อมูลไปตอบผู้ใช้ต้องกรอง ``is_active``** (เพิ่มใน
  ``006_admin.sql``) — ปุ่ม "ปิดใช้" ในหน้า admin ไม่ได้ลบแถว มันตั้ง flag
  ตัวนี้ ถ้ามี query ไหนลืมกรอง ปุ่มนั้นจะไม่มีผลอะไรเลยและไม่มีใครรู้
  จนกว่านักศึกษาจะได้คำตอบที่ตั้งใจซ่อนไปแล้ว
  (``is_active`` = คนตั้ง, ``is_available`` = ตัวตรวจลิงก์ตั้ง — คนละเรื่อง)
"""

from __future__ import annotations

import json
import logging

from .db import SupportsExecute, SupportsQuery

log = logging.getLogger("app.repository")

# ── เอกสาร / คำร้อง ──────────────────────────────────────────────────────────

SQL_DOCUMENT_CATEGORIES = """
SELECT category, count(*) AS total
FROM documents
WHERE audience = 'student'
  AND coalesce(is_available, TRUE)
  AND is_active
GROUP BY category
ORDER BY count(*) DESC, category
"""

SQL_DOCUMENTS_IN_CATEGORY = """
SELECT title, url, doc_type, note
FROM documents
WHERE category = %s
  AND audience = 'student'
  AND coalesce(is_available, TRUE)
  AND is_active
ORDER BY title
LIMIT %s
"""

# เกณฑ์คะแนนขั้นต่ำของการค้นแบบใกล้เคียง — วัดกับข้อมูลจริงแล้วเลือก 0.6
#
# ทำไมต้องส่งเกณฑ์เป็น parameter ไม่ใช้ตัวดำเนินการ ``<%`` เฉย ๆ: ``<%`` อ่านเกณฑ์
# จาก GUC ``pg_trgm.word_similarity_threshold`` ซึ่งเป็นค่า **ต่อ session**
# → กับ connection pool ต้อง ``SET`` ใหม่ทุกครั้งที่หยิบ connection ไม่งั้น
# พฤติกรรมเปลี่ยนเงียบ ๆ ตามว่าไปได้ connection ตัวไหน เขียนเป็นเงื่อนไขตรง ๆ
# ตรวจสอบได้และเทสได้ (ตารางมี 33 แถว การไม่ได้ใช้ index จึงไม่มีผล)
#
# ค่าที่วัดได้จริง: 0.6 ให้ผลเท่ากับการค้น substring พอดีทุกคำที่ทดสอบ
# ส่วน 0.4 ดึงขยะเข้ามา (คำว่า "ขอจบ" ได้ 5 ฉบับที่ไม่เกี่ยวเลย เพราะไปตรงกับ "ขอ")
SEARCH_MIN_SCORE = 0.6

# pg_trgm: ไทยไม่มีเว้นวรรค ทำ full-text search ตรง ๆ ไม่ได้
#
# **ต้องใช้ word_similarity ไม่ใช่ similarity**: ``similarity()`` คิดจากเซต
# trigram ของ *ทั้งสตริง* → คำค้นสั้น ๆ เทียบกับ ``keywords`` ที่เอาหลายคำมาต่อ
# ด้วย ``,`` ได้คะแนนต่ำตลอด วัดกับข้อมูลจริงแล้ว "กยศ" / "กู้ยืม" / "ฝึกงาน" /
# "ปฏิทิน" คืน **0 แถวทั้งหมด** ทั้งที่ ``keywords`` มีคำนั้นตรง ๆ
#
# **และต้องเทียบสองทิศทาง** เพราะ ``word_similarity(a, b)`` ไม่สมมาตร:
#
# 1. ``word_similarity(คำค้น, keywords)`` — คนพิมพ์คำเดียวสั้น ๆ ("ปฏิทิน")
#    แล้วไปตรงกับส่วนหนึ่งของ keyword ที่ยาวกว่า ("ปฏิทินการศึกษา") → 0.857
# 2. ``max(word_similarity(keyword ทีละคำ, คำค้น))`` — คนพิมพ์เป็นประโยค
#    ("อยากรู้เรื่องฝึกงาน") แล้ว keyword โผล่อยู่ข้างในประโยคนั้น → 1.0
#
# ทิศทางที่ 2 จำเป็นจริง ไม่ใช่เผื่อไว้: วัดแล้วประโยคแบบที่นักศึกษาพิมพ์จริง
# ("อยากรู้เรื่องฝึกงาน", "ขอกู้ยืม กยศ ทำยังไง", "อยากได้แบบฟอร์มเพิ่มวิชา")
# ได้ **0 แถวทั้งหมด** ถ้ามีแต่ทิศทางที่ 1 และได้ 3 / 7 / 2 แถวเมื่อเพิ่มทิศทางที่ 2
# ส่วนข้อความที่ไม่เกี่ยว ("สวัสดีครับ", "วันนี้กินอะไรดี") ยังได้ 0 แถวทั้งสองทิศทาง
#
# ``length(btrim(token)) >= 3`` กันคำสั้นกว่า 1 trigram ไปแมตช์กับอะไรก็ได้
SQL_SEARCH_DOCUMENTS = """
SELECT title, url, category, keywords, score
FROM (
    SELECT d.title, d.url, d.category, d.keywords,
           greatest(
               word_similarity(%s, coalesce(d.keywords, '')),
               word_similarity(%s, d.title),
               (
                   SELECT coalesce(max(word_similarity(token, %s)), 0)
                   FROM unnest(
                       string_to_array(
                           coalesce(d.keywords, '') || ',' || d.title, ','
                       )
                   ) AS token
                   WHERE length(btrim(token)) >= 3
               )
           ) AS score
    FROM documents d
    WHERE d.audience = 'student'
      AND coalesce(d.is_available, TRUE)
      AND d.is_active
) AS scored
WHERE score >= %s
ORDER BY score DESC, title
LIMIT %s
"""


async def document_categories(db: SupportsQuery) -> list[dict]:
    """หมวดเอกสารที่มีข้อมูลจริง + จำนวนในแต่ละหมวด"""
    return await db.fetch_all(SQL_DOCUMENT_CATEGORIES)


async def documents_in_category(
    db: SupportsQuery, category: str, limit: int = 10
) -> list[dict]:
    return await db.fetch_all(SQL_DOCUMENTS_IN_CATEGORY, (category, limit))


async def search_documents(
    db: SupportsQuery,
    keyword: str,
    limit: int = 5,
    min_score: float = SEARCH_MIN_SCORE,
) -> list[dict]:
    """
    ค้นเอกสารด้วยคำใกล้เคียง — คืนแถวที่คะแนน ``word_similarity`` ถึงเกณฑ์

    ``min_score`` เปิดให้ปรับได้เพื่อให้เทสพิสูจน์ได้ว่าเกณฑ์คือตัวกำหนดผล
    ไม่ใช่ตัว query พัง แต่**ค่า default ควรใช้ตามที่วัดไว้** (ดู
    :data:`SEARCH_MIN_SCORE`)

    คำที่ไม่มีในคลังจะได้ 0 แถวจริง ๆ (เช่น "ดรอป" / "ลาออก" / "ย้ายสาขา"
    ไม่มีเอกสารรองรับเลยแม้แต่ฉบับเดียว) — นั่นคือปัญหาที่ข้อมูล ไม่ใช่ที่ query
    """
    return await db.fetch_all(
        SQL_SEARCH_DOCUMENTS, (keyword, keyword, keyword, min_score, limit)
    )


# ── อาจารย์ ─────────────────────────────────────────────────────────────────

SQL_INSTRUCTOR_GROUPS = """
SELECT a.group_name, count(DISTINCT a.instructor_id) AS total
FROM instructor_affiliations a
JOIN instructors i ON i.id = a.instructor_id
WHERE i.is_active
GROUP BY a.group_name
ORDER BY count(DISTINCT a.instructor_id) DESC, a.group_name
"""

SQL_INSTRUCTORS_IN_GROUP = """
SELECT i.full_name, i.title_prefix, i.email, i.room, i.office_hours,
       a.position, a.is_chair
FROM instructors i
JOIN instructor_affiliations a ON a.instructor_id = i.id
WHERE a.group_name = %s
  AND i.is_active
ORDER BY a.is_chair DESC, i.full_name
LIMIT %s
"""

# ใช้ word_similarity เหมือน SQL_SEARCH_DOCUMENTS ด้วยเหตุผลเดียวกัน
# ที่นี่ผลที่ได้ดีขึ้นชัด: พิมพ์ "วีระพล" (จริงคือ "วีระพน") เดิมได้ 0.2778
# ไม่ถึงเกณฑ์ 0.3 → หาไม่เจอ ตอนนี้ได้ 0.7143 → เจอ
# และวัดแล้วว่าคำที่ไม่ใช่ชื่อคน ("กยศ", "เอกสาร", "ปฏิทิน") ยังได้ 0 แถว
# ซึ่งจำเป็นตอนเอาไปใช้กับข้อความพิมพ์อิสระ ไม่งั้นถามเรื่องเอกสารแล้วได้ชื่ออาจารย์
SQL_SEARCH_INSTRUCTORS = """
SELECT full_name, title_prefix, email, room, office_hours, score
FROM (
    SELECT i.full_name, i.title_prefix, i.email, i.room, i.office_hours,
           greatest(
               word_similarity(%s, i.name_normalized),
               (
                   SELECT coalesce(max(word_similarity(token, %s)), 0)
                   FROM unnest(string_to_array(i.name_normalized, ' ')) AS token
                   WHERE length(btrim(token)) >= 3
               )
           ) AS score
    FROM instructors i
    WHERE i.is_active
) AS scored
WHERE score >= %s
ORDER BY score DESC, full_name
LIMIT %s
"""

# ใช้บอกผู้ใช้ตรง ๆ ว่าข้อมูลติดต่อมีแค่ไหน — ห้ามเดาเบอร์โทร
SQL_INSTRUCTOR_CONTACT_COVERAGE = """
SELECT count(*)      AS total,
       count(email)  AS with_email,
       count(phone)  AS with_phone,
       count(room)   AS with_room
FROM instructors
WHERE is_active
"""


async def instructor_groups(db: SupportsQuery) -> list[dict]:
    return await db.fetch_all(SQL_INSTRUCTOR_GROUPS)


async def instructors_in_group(
    db: SupportsQuery, group_name: str, limit: int = 12
) -> list[dict]:
    return await db.fetch_all(SQL_INSTRUCTORS_IN_GROUP, (group_name, limit))


async def search_instructors(
    db: SupportsQuery,
    name: str,
    limit: int = 5,
    min_score: float = SEARCH_MIN_SCORE,
) -> list[dict]:
    return await db.fetch_all(
        SQL_SEARCH_INSTRUCTORS, (name, name, min_score, limit)
    )


async def instructor_contact_coverage(db: SupportsQuery) -> dict:
    row = await db.fetch_one(SQL_INSTRUCTOR_CONTACT_COVERAGE)
    return row or {"total": 0, "with_email": 0, "with_phone": 0, "with_room": 0}


# ── FAQ ที่คนเขียนคำตอบไว้ (ชั้นที่ 2) ───────────────────────────────────────

# เกณฑ์ขั้นต่ำของการแมตช์ FAQ — **สูงกว่าเกณฑ์การค้นเอกสาร (0.6) โดยเจตนา**
#
# FAQ ตอบเป็น "คำตอบสำเร็จ" ไม่ใช่รายการลิงก์ให้เลือกเอง → แมตช์ผิดแล้ว
# นักศึกษาได้คำตอบผิดเต็ม ๆ ไม่มีสัญญาณว่าไม่เกี่ยว (ต่างจากผลค้นเอกสาร
# ที่ผู้ใช้เห็นชื่อไฟล์แล้วรู้ทันทีว่าไม่ใช่เรื่องที่ถาม) จึงต้องมั่นใจกว่า
#
# ค่านี้เป็นแค่ default ของชั้นข้อมูล — ของจริง router ส่ง
# ``settings.faq_match_threshold`` (``FAQ_MATCH_THRESHOLD`` ใน ``.env``) มาให้
# ทั้งสองที่ตั้ง 0.82 ตรงกัน ห้ามให้ต่างกันเพราะจะ debug ไม่ออกว่าใช้ค่าไหน
FAQ_MIN_SCORE = 0.82

# ใช้ ``word_similarity`` **สองทิศทาง** ด้วยเหตุผลเดียวกับ SQL_SEARCH_DOCUMENTS
# (ไทยไม่มีเว้นวรรค → full-text ไม่ได้ และ ``word_similarity`` ไม่สมมาตร):
#
# 1. ``word_similarity(คำถามผู้ใช้, question)`` และกับ ``variants`` ทีละคำ —
#    คนพิมพ์คำเดียวสั้น ๆ ("ดรอปเรียน") แล้วไปตรงกับส่วนหนึ่งของประโยคที่ยาวกว่า
# 2. ``max(word_similarity(variant/token, คำถามผู้ใช้))`` — คนพิมพ์เป็นประโยค
#    ("อยากดรอปเรียนต้องทำยังไง") แล้วคำพ้องโผล่อยู่ข้างในประโยคนั้น
#
# ``variants`` เป็น ``TEXT[]`` จึงต้อง ``unnest`` ออกมาเทียบทีละคำ เทียบกับ
# ทั้ง array ต่อกันเป็นสตริงไม่ได้ (คะแนนจะเจือจางตามจำนวนคำพ้องที่ใส่ไว้ —
# ยิ่งเขียน FAQ ดีขึ้นยิ่งแมตช์แย่ลง ซึ่งกลับหัวกลับหาง)
#
# ``length(btrim(...)) >= 3`` กันคำสั้นกว่า 1 trigram ไปแมตช์กับอะไรก็ได้
#
# ``WHERE f.is_active`` จำเป็น: ปุ่ม "ปิดใช้" ในหน้า admin ไม่ได้ลบแถว
# ถ้าลืมกรอง คำตอบที่ตั้งใจซ่อนจะยังถูกส่งให้นักศึกษาต่อไปเงียบ ๆ
SQL_SEARCH_FAQS = """
SELECT intent_key, question, answer, category, quick_replies, source_url, score
FROM (
    SELECT f.intent_key, f.question, f.answer, f.category, f.quick_replies,
           f.source_url,
           greatest(
               word_similarity(%s, f.question),
               (
                   SELECT coalesce(max(word_similarity(%s, variant)), 0)
                   FROM unnest(f.variants) AS variant
                   WHERE length(btrim(variant)) >= 3
               ),
               (
                   SELECT coalesce(max(word_similarity(variant, %s)), 0)
                   FROM unnest(f.variants) AS variant
                   WHERE length(btrim(variant)) >= 3
               ),
               (
                   SELECT coalesce(max(word_similarity(token, %s)), 0)
                   FROM unnest(string_to_array(f.question, ' ')) AS token
                   WHERE length(btrim(token)) >= 3
               )
           ) AS score
    FROM faqs f
    WHERE f.is_active
) AS scored
WHERE score >= %s
ORDER BY score DESC, intent_key
LIMIT %s
"""


async def search_faqs(
    db: SupportsQuery,
    question: str,
    limit: int = 3,
    min_score: float = FAQ_MIN_SCORE,
) -> list[dict]:
    """
    ค้น FAQ ที่คนเขียนคำตอบไว้ — คืนแถวที่คะแนนถึงเกณฑ์ เรียงคะแนนมากไปน้อย

    คืน ``score`` ออกมาด้วยเพื่อให้ router เอาไปเป็น ``confidence`` ใน
    ``chat_logs`` ได้ (วัดในธีสิสภายหลังว่าคำตอบชั้นนี้มั่นใจแค่ไหนจริง)

    ``limit`` default 3 ไม่ใช่ 5 เพราะชั้นนี้ใช้แถวแรกตอบเสมอ ที่เหลือมีไว้
    ให้ log/debug เห็นว่ามี FAQ ใบอื่นสูสีไหม (สัญญาณว่า FAQ เขียนซ้ำซ้อน)

    ``min_score`` เปิดให้ปรับได้เพื่อให้เทสพิสูจน์ได้ว่าเกณฑ์เป็นตัวกำหนดผล
    แต่**ค่าที่ใช้จริงมาจาก ``settings.faq_match_threshold``** (ดู
    :data:`FAQ_MIN_SCORE`)
    """
    return await db.fetch_all(
        SQL_SEARCH_FAQS, (question, question, question, question, min_score, limit)
    )


# ── แผนการเรียน / วิชาที่เปิด ────────────────────────────────────────────────

# นับทีเดียวหลายอย่างในหนึ่ง round-trip — ใช้บอกผู้ใช้ว่า "ตอบอะไรได้บ้าง"
# ตอนนี้ prerequisites/curriculum_rules ยังว่าง (รอ มคอ.2) → ต้องบอกตรง ๆ
SQL_PLANNING_COVERAGE = """
SELECT
    (SELECT count(*) FROM curriculum_rules
      WHERE program_code = %s AND is_active) AS curriculum_rules,
    (SELECT count(*) FROM prerequisites
      WHERE program_code = %s AND is_active) AS prerequisites,
    (SELECT count(*) FROM offering_patterns) AS patterns,
    (SELECT count(*) FROM offering_patterns WHERE opens_sem1) AS opens_sem1,
    (SELECT count(*) FROM offering_patterns WHERE opens_sem2) AS opens_sem2,
    (SELECT count(*) FROM offering_patterns WHERE opens_sem3) AS opens_sem3,
    (SELECT count(*)
       FROM program_courses pc
       JOIN programs p ON p.program_id = pc.program_id
      WHERE p.program_code = %s) AS program_courses
"""

SQL_COURSE_BY_CODE = """
SELECT c.course_code, c.name_th, c.name_en, c.credits, c.credits_text,
       c.description_th, c.source_url,
       p.opens_sem1, p.opens_sem2, p.opens_sem3, p.terms_observed, p.terms_found
FROM courses c
LEFT JOIN offering_patterns p ON p.course_code = c.course_code
WHERE c.course_code = %s
"""

# วิชาตัวอย่างที่ "กดแล้วได้คำตอบสวย" — INNER JOIN offering_patterns โดยเจตนา
# เพราะวิชาที่ไม่มี pattern จะตอบว่า "ยังไม่พบว่าเปิดสอน" ซึ่งเป็นตัวอย่างที่แย่
# เรียงด้วย terms_found = เปิดบ่อยสุดก่อน (วิชาที่นักศึกษาทุกคนต้องเจอ)
SQL_SAMPLE_COURSES = """
SELECT c.course_code, c.name_th
FROM program_courses pc
JOIN programs p ON p.program_id = pc.program_id
JOIN courses c ON c.course_id = pc.course_id
JOIN offering_patterns op ON op.course_code = c.course_code
WHERE p.program_code = %s
ORDER BY op.terms_found DESC, c.course_code
LIMIT %s
"""

SQL_OFFERINGS_FOR_COURSE = """
SELECT o.acad_year, o.semester, o.section, o.schedule_raw, o.instructors,
       o.seats_total, o.seats_left, o.status
FROM offerings o
WHERE o.course_code = %s
ORDER BY o.acad_year DESC, o.semester DESC, o.section
LIMIT %s
"""

SQL_LATEST_TERM = """
SELECT acad_year, semester, count(*) AS offerings
FROM offerings
GROUP BY acad_year, semester
ORDER BY acad_year DESC, semester DESC
LIMIT 1
"""


async def planning_coverage(db: SupportsQuery, program_code: str) -> dict:
    """
    สรุปว่าตอบเรื่องแผนการเรียนได้แค่ไหน

    ใช้ตอบอย่างซื่อสัตย์: มี ``offering_patterns`` (วิชาเปิดเทอมไหน)
    แต่ยังไม่มี ``prerequisites`` / ``curriculum_rules`` (แผนปี-เทอม)
    ซึ่งต้องกรอกมือจาก มคอ.2
    """
    row = await db.fetch_one(
        SQL_PLANNING_COVERAGE, (program_code, program_code, program_code)
    )
    return row or {}


async def course_by_code(db: SupportsQuery, course_code: str) -> dict | None:
    return await db.fetch_one(SQL_COURSE_BY_CODE, (course_code,))


async def sample_courses(
    db: SupportsQuery, program_code: str, limit: int = 3
) -> list[dict]:
    """
    รายวิชาตัวอย่างสำหรับโชว์เป็นปุ่ม "กดดูได้เลย"

    ใช้กับปุ่ม *ค้นรายวิชา* บน Rich Menu ซึ่งกดแล้วต้องมีอะไรให้กดต่อทันที
    (Rich Menu ไม่มี action แบบ "ให้ผู้ใช้พิมพ์ต่อ" — ถ้าตอบแค่ข้อความว่า
    "พิมพ์รหัสมา" ผู้ใช้จำนวนมากจะเลิกกลางทาง)
    """
    return await db.fetch_all(SQL_SAMPLE_COURSES, (program_code, limit))


async def offerings_for_course(
    db: SupportsQuery, course_code: str, limit: int = 6
) -> list[dict]:
    return await db.fetch_all(SQL_OFFERINGS_FOR_COURSE, (course_code, limit))


async def latest_term(db: SupportsQuery) -> dict | None:
    return await db.fetch_one(SQL_LATEST_TERM)


# ── บทสนทนา: ประวัติ + log (ชั้นที่ 3 — AI Chat) ───────────────────────────
#
# สองตารางนี้ต่างจากข้างบนตรงที่เป็น **ทางเขียน** → ต้องใช้ SupportsExecute
# (ดู :class:`app.db.SupportsExecute`) แยก Protocol ไว้เพื่อให้ชั้นอ่าน
# ไม่มีสิทธิ์เขียนโดยบังเอิญ

SQL_RECENT_CHAT = """
SELECT message_text, response_text
FROM chat_logs
WHERE user_id = %s
  AND answered_by = 'ai_chat'
  AND message_text IS NOT NULL
  AND response_text IS NOT NULL
ORDER BY created_at DESC, id DESC
LIMIT %s
"""


async def recent_chat(db: SupportsQuery, user_id: int, turns: int) -> list[dict]:
    """
    ดึงบทสนทนา AI Chat ล่าสุดของ user คนนี้ (เก่า → ใหม่)

    ``user_id`` คือ id ใน ``app_users`` (ผูกกับ ``line_user_hash``) ดังนั้น
    ประวัติ **แยกกันตามผู้ใช้โดยอัตโนมัติ** — ไม่มีทางที่คนหนึ่งเห็นบริบท
    ของอีกคน และดึงเฉพาะแถว ``answered_by='ai_chat'`` ที่เก็บ ``response_text``
    ไว้ ไม่ปนกับคำตอบจากปุ่ม/ค้นหา (พวกนั้นไม่มีบทสนทนาให้จำ)

    ``ORDER BY ... DESC`` แล้วกลับลำดับใน Python — ให้รอบล่าสุดอยู่ท้าย
    เพื่อส่งเข้า LLM ตามลำดับจริง
    """
    rows = await db.fetch_all(SQL_RECENT_CHAT, (user_id, turns))
    return list(reversed(rows))


SQL_INSERT_CHAT_LOG = """
INSERT INTO chat_logs (
    user_id, message_text, answered_by, intent_key, confidence,
    response_text, citations, latency_ms, llm_model, prompt_tokens, output_tokens,
    status
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# ค่าที่ ``chat_logs.status`` รับได้ — **ต้องตรงกับ CHECK ใน
# db/migrations/004_chat_log_status.sql** (ถ้าเพิ่มค่าใหม่ต้องแก้ทั้งสองที่)
#
# แยกจาก ``answered_by`` โดยเจตนา: answered_by บอกว่าชั้น/พื้นผิวไหนคิดคำตอบ
# ส่วนคอลัมน์นี้บอกว่าคำตอบนั้น **ถึงผู้ใช้จริงไหม** ถ้ายุบรวมกันจะเสียข้อมูล
# ไปหนึ่งด้าน (รอบที่ ai_chat ตอบแล้วส่งไม่ถึง จะนับภาระของชั้น AI ไม่ได้อีก)
CHAT_STATUS_DELIVERED = "delivered"
CHAT_STATUS_SEND_FAILED = "send_failed"


async def insert_chat_log(
    db: SupportsExecute,
    *,
    user_id: int | None,
    message_text: str | None,
    answered_by: str,
    intent_key: str | None,
    confidence: float | None,
    response_text: str | None,
    citations: list[dict] | None,
    latency_ms: int | None,
    llm_model: str | None,
    prompt_tokens: int | None,
    output_tokens: int | None,
    status: str = CHAT_STATUS_DELIVERED,
) -> int:
    """
    บันทึก 1 รอบสนทนาลง ``chat_logs``

    ``user_id`` เป็น ``None`` ได้ — webhook บาง event ไม่มี userId
    (เช่นใน group) ก็ยังเก็บข้อความ+ชั้นที่ตอบไว้ใช้วัดผลได้

    ``status`` default เป็น :data:`CHAT_STATUS_DELIVERED` เพราะเส้นทางปกติคือ
    ส่งสำเร็จแล้วค่อยบันทึก — ผู้เรียกที่รู้ว่า **ส่งไม่ถึง** ต้องส่ง
    :data:`CHAT_STATUS_SEND_FAILED` มาเอง ไม่งั้นข้อมูลวัดผลจะบอกว่าตอบสำเร็จ
    ทั้งที่นักศึกษาไม่ได้เห็นคำตอบ (ดู :func:`app.main.process_event`)
    """
    return await db.execute(
        SQL_INSERT_CHAT_LOG,
        (
            user_id,
            message_text,
            answered_by,
            intent_key,
            confidence,
            response_text,
            json.dumps(citations, ensure_ascii=False) if citations is not None else None,
            latency_ms,
            llm_model,
            prompt_tokens,
            output_tokens,
            status,
        ),
    )


SQL_TOUCH_APP_USER = """
INSERT INTO app_users (line_user_hash, last_seen_at)
VALUES (%s, now())
ON CONFLICT (line_user_hash) DO UPDATE
SET last_seen_at = now()
RETURNING id
"""


async def ensure_user(db: SupportsQuery, line_user_hash: str) -> int:
    """
    หา/สร้างแถว ``app_users`` แล้วคืน ``id``

    ใช้ ``ON CONFLICT ... DO UPDATE SET last_seen_at`` เพราะ ``INSERT ...
    ON CONFLICT DO NOTHING RETURNING id`` **ไม่คืนแถว** เมื่อชน (id เป็น
    ``None``) ส่วน ``DO UPDATE`` คืนแถวเสมอ และได้ ``last_seen_at`` ฟรีด้วย
    (PDPA: เก็บแค่ hash + เวลา ไม่เก็บชื่อ ไม่เก็บข้อความส่วนตัวตรงนี้)
    """
    row = await db.fetch_one(SQL_TOUCH_APP_USER, (line_user_hash,))
    return int(row["id"])


# ── โหมดปรึกษา AI (ai_sessions) ─────────────────────────────────────────────
#
# user "เข้าโหมด" ก่อนถึงเสีย token กับ LLM — สถานะโหมดอยู่ในตารางนี้
# (ไม่ใช่ใน process memory) เพราะ restart แล้วโหมดต้องไม่หาย และตารางคือ
# ข้อมูลวัดผลธีสิสตรง ๆ: จำนวน session, รอบเฉลี่ย, ออกด้วยเหตุผลอะไร


SQL_OPEN_AI_SESSION = """
INSERT INTO ai_sessions (user_id)
SELECT u.id
FROM app_users u
WHERE u.line_user_hash = %s
  AND NOT EXISTS (
      SELECT 1 FROM ai_sessions s
      WHERE s.user_id = u.id AND s.ended_at IS NULL
  )
RETURNING id, started_at
"""


async def open_ai_session(db: SupportsExecute, line_user_hash: str) -> int:
    """
    เปิด session โหมดปรึกษา — **ไม่สร้างแถวซ้ำ** ถ้ามี session เปิดอยู่

    ``INSERT ... SELECT ... WHERE NOT EXISTS`` + ``RETURNING`` ทำ atomically
    ใน statement เดียว (ไม่ต้อง ensure_user แยก — join ``app_users`` จาก hash
    ตรง ๆ และแถว user ต้องมีอยู่แล้วเพราะ webhook สร้างให้ตอนแรก)
    ถ้ามี session เปิดอยู่แล้ว RETURNING ไม่คืนแถว → ผู้เรียกต้องไปหา
    session เดิมเองด้วย :func:`active_ai_session_by_hash`
    """
    row = await db.fetch_one(SQL_OPEN_AI_SESSION, (line_user_hash,))
    return int(row["id"])


SQL_ACTIVE_AI_SESSION = """
SELECT id, started_at, last_active_at, turn_count
FROM ai_sessions
WHERE user_id = %s
  AND ended_at IS NULL
ORDER BY id DESC
LIMIT 1
"""


async def active_ai_session(db: SupportsQuery, user_id: int) -> dict | None:
    """คืน session ที่ยังเปิดอยู่ของ user (แถวเดียวเสมอ — ดู ``open_ai_session``)"""
    return await db.fetch_one(SQL_ACTIVE_AI_SESSION, (user_id,))


SQL_ACTIVE_SESSION_BY_HASH = """
SELECT s.id, s.last_active_at, s.turn_count
FROM ai_sessions s
JOIN app_users u ON u.id = s.user_id
WHERE u.line_user_hash = %s
  AND s.ended_at IS NULL
ORDER BY s.id DESC
LIMIT 1
"""


async def active_ai_session_by_hash(db: SupportsQuery, line_user_hash: str) -> dict | None:
    """
    ตรวจว่ามี session เปิดอยู่ไหม **จาก hash ตรง ๆ** — ทางอ่านล้วน

    ใช้กับข้อความธรรมดาทุกตัวที่เข้ามา (ยังไม่รู้ว่าจะเข้าโหมดไหม) เพื่อไม่ให้
    ทุกข้อความกลายเป็นการเขียน (``ensure_user`` upsert) — เขียนเฉพาะเมื่อ
    จะเข้า/ออก/ตอบในโหมดจริง ๆ
    """
    return await db.fetch_one(SQL_ACTIVE_SESSION_BY_HASH, (line_user_hash,))


SQL_TOUCH_AI_SESSION = """
UPDATE ai_sessions
SET last_active_at = now(), turn_count = turn_count + 1
WHERE id = %s
"""


async def touch_ai_session(db: SupportsExecute, session_id: int) -> int:
    """ขยับเวลา + นับรอบหลังตอบสำเร็จ — ใช้ตรวจ timeout/เพดานรอบในรอบถัดไป"""
    return await db.execute(SQL_TOUCH_AI_SESSION, (session_id,))


SQL_END_AI_SESSION = """
UPDATE ai_sessions
SET ended_at = now(), end_reason = %s
WHERE id = %s
"""


async def end_ai_session(db: SupportsExecute, session_id: int, reason: str) -> int:
    """
    ปิด session — ``reason`` ต้องเป็นหนึ่งใน ``button`` / ``keyword`` /
    ``timeout`` / ``turn_limit`` (ตารางมี CHECK constraint บังคับ)
    """
    return await db.execute(SQL_END_AI_SESSION, (reason, session_id))


# ── Planner: แผนการเรียน + วิชาที่ผ่านแล้วของผู้ใช้ ──────────────────────────
#
# สามคิวรีนี้เป็น input ทั้งหมดของ :mod:`app.planner` (ที่เหลือเป็นการคำนวณล้วน)

# LEFT JOIN LATERAL ไม่ใช่ LEFT JOIN เฉย ๆ โดยจำเป็น:
# ``courses`` มี PK เป็น course_id และ **course_code ซ้ำได้** (วัดจริง:
# 7071102 มี 3 แถว, 7071103 มี 3 แถว — ต่างรุ่นหลักสูตร/ต่างที่มา) JOIN ตรง ๆ
# จะได้ 32 วิชากลายเป็น 50 กว่าแถว แล้วหน่วยกิตรวมบวมทันที
# เลือกแถวเดียวด้วย ``(name_th IS NULL), course_id`` = เอาแถวที่มีชื่อวิชาก่อน
# (แถวซ้ำที่เหลือ name_th เป็น NULL) แล้วตัดสินด้วย id ให้ผลคงที่ทุกครั้ง
SQL_CURRICULUM_PLAN = """
SELECT cr.course_code, cr.course_code_full, cr.std_year, cr.std_semester,
       cr.is_fixed_term, cr.note,
       c.name_th, c.credits, c.credits_text,
       op.opens_sem1, op.opens_sem2, op.opens_sem3
FROM curriculum_rules cr
LEFT JOIN LATERAL (
    SELECT name_th, credits, credits_text
    FROM courses
    WHERE course_code = cr.course_code
    ORDER BY (name_th IS NULL), course_id
    LIMIT 1
) c ON TRUE
LEFT JOIN offering_patterns op ON op.course_code = cr.course_code
WHERE cr.program_code = %s
  AND cr.is_active
ORDER BY cr.std_year, cr.std_semester, cr.course_code
"""

SQL_PREREQUISITES_FOR_PROGRAM = """
SELECT p.course_code, p.requires_code, p.kind,
       r.name_th AS requires_name
FROM prerequisites p
LEFT JOIN LATERAL (
    SELECT name_th FROM courses
    WHERE course_code = p.requires_code
    ORDER BY (name_th IS NULL), course_id
    LIMIT 1
) r ON TRUE
WHERE p.program_code = %s
  AND p.is_active
ORDER BY p.course_code, p.requires_code
"""

SQL_PROGRAM_TOTAL_CREDITS = """
SELECT program_code, program_name, total_credits
FROM programs
WHERE program_code = %s
ORDER BY program_id
LIMIT 1
"""

SQL_USER_PROFILE = """
SELECT u.id, u.program_code, u.study_year, u.entry_year,
       u.consent_version, u.consent_at,
       (SELECT count(*) FROM user_completed_courses uc WHERE uc.user_id = u.id)
           AS completed_courses
FROM app_users u
WHERE u.line_user_hash = %s
"""

SQL_COMPLETED_COURSES = """
SELECT course_code, source, reported_at
FROM user_completed_courses
WHERE user_id = %s
ORDER BY course_code
"""


async def curriculum_plan(db: SupportsQuery, program_code: str) -> list[dict]:
    """แผนการเรียนมาตรฐาน + ชื่อวิชา + เปิดเทอมไหน (input หลักของ planner)"""
    return await db.fetch_all(SQL_CURRICULUM_PLAN, (program_code,))


async def prerequisites_for_program(db: SupportsQuery, program_code: str) -> list[dict]:
    """
    วิชาบังคับก่อนทั้งหลักสูตร

    ตอนนี้คืน **ลิสต์ว่าง** เพราะตารางยังไม่มีข้อมูล (ระบบทะเบียนไม่เผยแพร่)
    planner รับมือได้: ``Progress.prereq_known`` จะเป็น False แล้วคำตอบจะบอก
    ผู้ใช้ตรง ๆ ว่าลำดับที่เห็นคือ "เทอมที่แผนแนะนำ" ไม่ใช่เงื่อนไขบังคับ
    """
    return await db.fetch_all(SQL_PREREQUISITES_FOR_PROGRAM, (program_code,))


async def program_info(db: SupportsQuery, program_code: str) -> dict | None:
    return await db.fetch_one(SQL_PROGRAM_TOTAL_CREDITS, (program_code,))


async def user_profile(db: SupportsQuery, line_user_hash: str) -> dict | None:
    """โปรไฟล์ที่ใช้คำนวณแผน — ไม่มีชื่อ ไม่มีรหัสนักศึกษา (ดู PDPA ใน 001_init)"""
    return await db.fetch_one(SQL_USER_PROFILE, (line_user_hash,))


async def completed_courses(db: SupportsQuery, user_id: int) -> list[dict]:
    return await db.fetch_all(SQL_COMPLETED_COURSES, (user_id,))


# ── Planner: ทางเขียน (LIFF ติ๊กวิชาที่ผ่าน) ─────────────────────────────────

SQL_SET_USER_PROGRAM = """
UPDATE app_users
SET program_code = coalesce(%s, program_code),
    study_year   = coalesce(%s, study_year),
    entry_year   = coalesce(%s, entry_year),
    updated_at   = now(),
    last_seen_at = now()
WHERE line_user_hash = %s
RETURNING id, program_code, study_year, entry_year
"""

# แทนที่ "ชุด" วิชาที่ผ่านทั้งก้อนใน **statement เดียว**
#
# ทำไมต้องเดียว: ``Database.execute`` เปิด-ปิด connection แล้ว commit ต่อการ
# เรียกหนึ่งครั้ง ถ้าแยกเป็น DELETE แล้ว INSERT จะมีช่วงหนึ่งที่ผู้ใช้
# "ไม่ผ่านวิชาอะไรเลย" ค้างอยู่ใน DB ถ้า INSERT พังต่อจากนั้น ข้อมูลที่ติ๊ก
# มาทั้งหมดหายจริง — CTE เดียวจึงเป็นทั้ง atomicity และความง่ายในการอ่าน
#
# แตะเฉพาะ ``source = 'self_report'``: แถวที่มาจากการอัปโหลดเอกสาร (ถ้ามีวันหน้า)
# น่าเชื่อถือกว่าการติ๊กเอง ห้ามให้การติ๊กครั้งใหม่ลบทิ้ง
SQL_REPLACE_COMPLETED_COURSES = """
WITH incoming AS (
    SELECT DISTINCT code
    FROM unnest(%s::text[]) AS code
    WHERE code IS NOT NULL AND btrim(code) <> ''
), removed AS (
    DELETE FROM user_completed_courses uc
    WHERE uc.user_id = %s
      AND uc.source = 'self_report'
      AND NOT EXISTS (SELECT 1 FROM incoming i WHERE i.code = uc.course_code)
    RETURNING 1
), added AS (
    INSERT INTO user_completed_courses (user_id, course_code, source)
    SELECT %s, i.code, 'self_report' FROM incoming i
    ON CONFLICT (user_id, course_code) DO NOTHING
    RETURNING 1
)
SELECT (SELECT count(*) FROM removed) AS removed,
       (SELECT count(*) FROM added) AS added
"""


async def set_user_program(
    db: SupportsExecute,
    line_user_hash: str,
    program_code: str | None = None,
    study_year: int | None = None,
    entry_year: int | None = None,
) -> dict | None:
    """
    ตั้งหลักสูตร/ชั้นปีของผู้ใช้ — ``None`` = ไม่แก้ค่าเดิม (coalesce ใน SQL)

    ต้องมีแถว ``app_users`` อยู่ก่อน (เรียก :func:`ensure_user` ให้แล้ว)
    """
    return await db.fetch_one(
        SQL_SET_USER_PROGRAM, (program_code, study_year, entry_year, line_user_hash)
    )


async def replace_completed_courses(
    db: SupportsExecute, user_id: int, course_codes: list[str]
) -> dict:
    """
    ตั้ง "ชุด" วิชาที่ผ่านให้ตรงกับที่ติ๊กมา แล้วคืนจำนวนที่ลบ/เพิ่ม

    ส่งลิสต์ว่างมาได้ = ล้างทั้งหมด (ผู้ใช้เอาติ๊กออกหมด)
    """
    row = await db.fetch_one(
        SQL_REPLACE_COMPLETED_COURSES, (list(course_codes), user_id, user_id)
    )
    return row or {"removed": 0, "added": 0}


# ── กฎเสริมของ AI (ผู้ดูแลเพิ่มจากหน้า /admin) ──────────────────────────────
#
# ทางอ่านของ **บอท** อยู่ที่นี่ ไม่ใช่ใน admin_repo: ไฟล์นี้คือชั้นที่บอทใช้
# ตอนตอบ ส่วน admin_repo คือชั้นที่หน้าเว็บใช้ตอนแก้ (คนละสิทธิ์กัน)
#
# เรียงตาม ``created_at`` = ลำดับที่กฎถูกต่อเข้า prompt และเป็นลำดับเดียวกับ
# ที่หน้า /admin แสดง — คนที่อ่านหน้าเว็บจะเห็นสิ่งเดียวกับที่ AI เห็น
#
# ``LIMIT %s`` ไม่ใช่ของประดับ: ข้อความทุกข้อในผลลัพธ์ถูกต่อเข้า prompt ทุกครั้ง
# ที่มีคนคุยกับ AI ตารางนี้บวมเท่ากับค่า token ต่อข้อความบวมตามไปด้วย

SQL_ACTIVE_PROMPT_RULES = """
SELECT rule_key, rule_text
FROM ai_prompt_rules
WHERE is_active
ORDER BY created_at, rule_key
LIMIT %s
"""


async def active_prompt_rules(db: SupportsQuery, limit: int) -> list[dict]:
    """กฎเสริมที่เปิดใช้อยู่ เรียงตามลำดับที่จะต่อเข้า prompt"""
    return await db.fetch_all(SQL_ACTIVE_PROMPT_RULES, (limit,))


# ── ทะเบียนรวมของ SQL ทั้งไฟล์ (ใช้ในเทส) ───────────────────────────────────

ALL_QUERIES: dict[str, str] = {
    "SQL_DOCUMENT_CATEGORIES": SQL_DOCUMENT_CATEGORIES,
    "SQL_DOCUMENTS_IN_CATEGORY": SQL_DOCUMENTS_IN_CATEGORY,
    "SQL_SEARCH_DOCUMENTS": SQL_SEARCH_DOCUMENTS,
    "SQL_INSTRUCTOR_GROUPS": SQL_INSTRUCTOR_GROUPS,
    "SQL_INSTRUCTORS_IN_GROUP": SQL_INSTRUCTORS_IN_GROUP,
    "SQL_SEARCH_INSTRUCTORS": SQL_SEARCH_INSTRUCTORS,
    "SQL_SEARCH_FAQS": SQL_SEARCH_FAQS,
    "SQL_INSTRUCTOR_CONTACT_COVERAGE": SQL_INSTRUCTOR_CONTACT_COVERAGE,
    "SQL_PLANNING_COVERAGE": SQL_PLANNING_COVERAGE,
    "SQL_COURSE_BY_CODE": SQL_COURSE_BY_CODE,
    "SQL_SAMPLE_COURSES": SQL_SAMPLE_COURSES,
    "SQL_OFFERINGS_FOR_COURSE": SQL_OFFERINGS_FOR_COURSE,
    "SQL_LATEST_TERM": SQL_LATEST_TERM,
    "SQL_RECENT_CHAT": SQL_RECENT_CHAT,
    "SQL_INSERT_CHAT_LOG": SQL_INSERT_CHAT_LOG,
    "SQL_TOUCH_APP_USER": SQL_TOUCH_APP_USER,
    "SQL_OPEN_AI_SESSION": SQL_OPEN_AI_SESSION,
    "SQL_ACTIVE_AI_SESSION": SQL_ACTIVE_AI_SESSION,
    "SQL_ACTIVE_SESSION_BY_HASH": SQL_ACTIVE_SESSION_BY_HASH,
    "SQL_TOUCH_AI_SESSION": SQL_TOUCH_AI_SESSION,
    "SQL_END_AI_SESSION": SQL_END_AI_SESSION,
    "SQL_CURRICULUM_PLAN": SQL_CURRICULUM_PLAN,
    "SQL_PREREQUISITES_FOR_PROGRAM": SQL_PREREQUISITES_FOR_PROGRAM,
    "SQL_PROGRAM_TOTAL_CREDITS": SQL_PROGRAM_TOTAL_CREDITS,
    "SQL_USER_PROFILE": SQL_USER_PROFILE,
    "SQL_COMPLETED_COURSES": SQL_COMPLETED_COURSES,
    "SQL_SET_USER_PROGRAM": SQL_SET_USER_PROGRAM,
    "SQL_REPLACE_COMPLETED_COURSES": SQL_REPLACE_COMPLETED_COURSES,
    "SQL_ACTIVE_PROMPT_RULES": SQL_ACTIVE_PROMPT_RULES,
}
