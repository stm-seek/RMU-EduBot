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
  แย่กว่าไม่ส่งเลย (จาก 32 ฉบับ เข้าได้จริง 31)
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
GROUP BY category
ORDER BY count(*) DESC, category
"""

SQL_DOCUMENTS_IN_CATEGORY = """
SELECT title, url, doc_type, note
FROM documents
WHERE category = %s
  AND audience = 'student'
  AND coalesce(is_available, TRUE)
ORDER BY title
LIMIT %s
"""

# เกณฑ์คะแนนขั้นต่ำของการค้นแบบใกล้เคียง — วัดกับข้อมูลจริงแล้วเลือก 0.6
#
# ทำไมต้องส่งเกณฑ์เป็น parameter ไม่ใช้ตัวดำเนินการ ``<%`` เฉย ๆ: ``<%`` อ่านเกณฑ์
# จาก GUC ``pg_trgm.word_similarity_threshold`` ซึ่งเป็นค่า **ต่อ session**
# → กับ connection pool ต้อง ``SET`` ใหม่ทุกครั้งที่หยิบ connection ไม่งั้น
# พฤติกรรมเปลี่ยนเงียบ ๆ ตามว่าไปได้ connection ตัวไหน เขียนเป็นเงื่อนไขตรง ๆ
# ตรวจสอบได้และเทสได้ (ตารางมี 31 แถว การไม่ได้ใช้ index จึงไม่มีผล)
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
SELECT group_name, count(DISTINCT instructor_id) AS total
FROM instructor_affiliations
GROUP BY group_name
ORDER BY count(DISTINCT instructor_id) DESC, group_name
"""

SQL_INSTRUCTORS_IN_GROUP = """
SELECT i.full_name, i.title_prefix, i.email, i.room, i.office_hours,
       a.position, a.is_chair
FROM instructors i
JOIN instructor_affiliations a ON a.instructor_id = i.id
WHERE a.group_name = %s
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


# ── แผนการเรียน / วิชาที่เปิด ────────────────────────────────────────────────

# นับทีเดียวหลายอย่างในหนึ่ง round-trip — ใช้บอกผู้ใช้ว่า "ตอบอะไรได้บ้าง"
# ตอนนี้ prerequisites/curriculum_rules ยังว่าง (รอ มคอ.2) → ต้องบอกตรง ๆ
SQL_PLANNING_COVERAGE = """
SELECT
    (SELECT count(*) FROM curriculum_rules WHERE program_code = %s) AS curriculum_rules,
    (SELECT count(*) FROM prerequisites WHERE program_code = %s) AS prerequisites,
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
    response_text, citations, latency_ms, llm_model, prompt_tokens, output_tokens
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


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
) -> int:
    """
    บันทึก 1 รอบสนทนาลง ``chat_logs``

    ``user_id`` เป็น ``None`` ได้ — webhook บาง event ไม่มี userId
    (เช่นใน group) ก็ยังเก็บข้อความ+ชั้นที่ตอบไว้ใช้วัดผลได้
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


# ── ทะเบียนรวมของ SQL ทั้งไฟล์ (ใช้ในเทส) ───────────────────────────────────

ALL_QUERIES: dict[str, str] = {
    "SQL_DOCUMENT_CATEGORIES": SQL_DOCUMENT_CATEGORIES,
    "SQL_DOCUMENTS_IN_CATEGORY": SQL_DOCUMENTS_IN_CATEGORY,
    "SQL_SEARCH_DOCUMENTS": SQL_SEARCH_DOCUMENTS,
    "SQL_INSTRUCTOR_GROUPS": SQL_INSTRUCTOR_GROUPS,
    "SQL_INSTRUCTORS_IN_GROUP": SQL_INSTRUCTORS_IN_GROUP,
    "SQL_SEARCH_INSTRUCTORS": SQL_SEARCH_INSTRUCTORS,
    "SQL_INSTRUCTOR_CONTACT_COVERAGE": SQL_INSTRUCTOR_CONTACT_COVERAGE,
    "SQL_PLANNING_COVERAGE": SQL_PLANNING_COVERAGE,
    "SQL_COURSE_BY_CODE": SQL_COURSE_BY_CODE,
    "SQL_OFFERINGS_FOR_COURSE": SQL_OFFERINGS_FOR_COURSE,
    "SQL_LATEST_TERM": SQL_LATEST_TERM,
    "SQL_RECENT_CHAT": SQL_RECENT_CHAT,
    "SQL_INSERT_CHAT_LOG": SQL_INSERT_CHAT_LOG,
    "SQL_TOUCH_APP_USER": SQL_TOUCH_APP_USER,
}
