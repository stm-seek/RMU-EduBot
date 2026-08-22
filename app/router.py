"""
Router 3 ชั้น: postback → FAQ → RAG → fallback

**หลักการที่ยึด** (ตาม Requirement ข้อ 4.4 และ 14):

* เรื่องที่คำนวณได้แน่นอน (prerequisite, หน่วยกิต, ตารางชน) ใช้ **code**
  ไม่ให้ LLM คิด — LLM ผิดเรื่องตัวเลข/วันที่ได้ และถ้าตอบผิดนักศึกษาเสียหายจริง
* ไม่มีข้อมูลอ้างอิง → **ตอบว่าไม่มี ไม่เดา**

ชั้นที่ 1 ตอบจาก DB ตรง ๆ: เร็ว ฟรี แม่น 100%  ← **ทำแล้ว** ครอบคลุม
postback จากปุ่ม, รหัสวิชา 7 หลัก, และ **ค้นด้วยคำที่พิมพ์มา** (``pg_trgm``)
ชั้นที่ 2 (FAQ) ใช้คำตอบที่คนเขียนไว้ ไม่เรียก LLM → ประหยัดและคุมคำตอบได้
ชั้นที่ 3 (RAG/AI Chat) generate ด้วย LLM — ตอนนี้ **AI Chat ทำแล้ว**
(คำแนะนำการเรียนทั่วไป ตอบจาก ``app/ai_chat.py``) ส่วน RAG/FAQ ยังไม่มี
เพราะตาราง ``rag_chunks``/``faqs`` ยังว่าง (บล็อกที่เนื้อหาทางการ)

**ค่า ``answered_by`` ที่ไฟล์นี้ผลิตได้จริงตอนนี้มี 9 ค่า**: ``rich_menu``
(กดปุ่มบน Rich Menu — postback มี ``src=rich``), ``quick_reply`` (กดปุ่มใน
บทสนทนา), ``course`` (พิมพ์รหัสวิชา 7 หลัก), ``follow`` (ทักครั้งแรก),
``search`` (พิมพ์คำแล้วค้นจาก DB), ``no_data`` (เข้าใจคำถามแต่ไม่มีข้อมูล),
``db_error`` (ถามฐานข้อมูลไม่สำเร็จ), ``fallback`` (ไม่เข้าใจคำถาม),
``ai_chat`` (LLM ตอบคำถามทั่วไป) — ยังไม่มี ``faq`` / ``planner`` / ``rag``

**เดิมทุกทางข้างบนถูกป้ายว่า ``rich_menu`` หมด** รวมทั้งการพิมพ์รหัสวิชาและ
ข้อความต้อนรับ ซึ่งทำให้วัดในธีสิสไม่ได้ว่า Rich Menu รับภาระเท่าไหร่จริง
(ดู :func:`_answer_surface`) — ระวังว่า ``no_data``/``db_error``/``fallback``
ทับป้ายพื้นผิวโดยเจตนา จึงนับ ``rich_menu`` ได้เป็น **ขั้นต่ำ** ไม่ใช่ยอดกด

``db`` ที่ทุก handler รับเป็น ``None`` ได้ (ยังไม่ตั้ง ``DATABASE_URL`` หรือ
ต่อไม่ได้ตอนสตาร์ท) → ตอบว่า "ยังไม่มีข้อมูล" ไม่ใช่ 500 และไม่ใช่เงียบหาย
ส่วน DB ที่ล่ม *ระหว่าง* บทสนทนา :func:`_guard` ดักไว้แล้วตอบ ``db_error``
"""

from __future__ import annotations

import logging
import re
from collections.abc import Awaitable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl

from . import repository as repo
from .db import SupportsQuery
from .line import messages as msg

log = logging.getLogger("app.router")

# กันข้อความทะลุ 5,000 ตัวอักษรของ LINE — เผื่อที่ให้ header/footer ด้วย
TEXT_BUDGET = 4_200

# รหัสวิชาของ regis.rmu.ac.th เป็นเลข 7 หลักเต็มเสมอ
COURSE_CODE_PATTERN = re.compile(r"(?<!\d)(\d{7})(?!\d)")

TERM_LABELS = {1: "เทอม 1", 2: "เทอม 2", 3: "ภาคฤดูร้อน"}

# จำนวนผลค้นหาต่อครั้ง — 5 พออ่านจบในหน้าจอมือถือโดยไม่ต้องเลื่อนยาว
SEARCH_RESULT_LIMIT = 5

# วิชาตัวอย่างบนปุ่ม "ค้นรายวิชา" — 3 พอให้เห็นว่าใช้งานยังไง ไม่บังปุ่มเมนูหลัก
SAMPLE_COURSE_COUNT = 3

# เพดานเอกสารต่อหมวด **ต้องมากกว่าหมวดที่ใหญ่สุด** (ตอนนี้ loan = 12 ฉบับ)
#
# ``repo.documents_in_category`` ตั้ง default ไว้ 10 เป็นกันชนของชั้นข้อมูล
# ตรงนี้เคยเรียกโดยไม่ส่ง limit → เมนูบอก "12 ฉบับ" แต่กดเข้าไปเห็น 10
# และเอกสาร 2 ฉบับสุดท้ายเข้าถึงไม่ได้เลยจากบอท (เจอกับข้อมูลจริง)
# ถ้าโตเกินงบตัวอักษร :func:`join_lines` จะตัดให้แล้วบอก "แสดง N จาก M รายการ"
DOCUMENTS_PER_CATEGORY = 30


@dataclass
class RouteResult:
    """
    ผลการตอบ 1 ครั้ง — เก็บข้อมูลพอสำหรับ log ลง ``chat_logs``

    ``answered_by`` ใช้วัดผลในธีสิสได้ว่าแต่ละชั้นรับภาระเท่าไหร่
    และ fallback rate เป็นเท่าไหร่
    """

    messages: list[dict]
    # ค่าที่ผลิตได้จริงตอนนี้: rich_menu / quick_reply / course / follow / search
    # / no_data / db_error / fallback / ai_chat
    # (faq / planner / rag ยังไม่มีชั้นที่ผลิตค่าเหล่านี้ — อย่าเคลมในเอกสาร)
    answered_by: str
    intent_key: str | None = None
    confidence: float | None = None
    citations: list[dict] = field(default_factory=list)
    llm_model: str | None = None
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    # id ใน ``app_users`` ถ้า router รู้แล้ว (เช่น ai_chat ที่ต้อง ensure_user
    # อยู่แล้ว) — ``app.main`` จะได้ไม่ต้อง ensure ซ้ำตอนเขียน ``chat_logs``
    user_id: int | None = None
    # สัญญาณสลับ Rich Menu ของผู้ใช้นี้: ``"consult"`` = ผูกใบโหมดปรึกษา
    # ``"main"`` = ถอดกลับเมนูหลัก ``None`` = ไม่สลับ — ``app.main``
    # อ่านค่านี้หลังส่งคำตอบสำเร็จแล้วเรียก ``link_rich_menu``/
    # ``unlink_rich_menu`` (ไม่เดาจาก ``intent_key`` เพราะบางค่าเช่น
    # ``ai_chat`` ต้องดูบริบทเพิ่มว่าเปิด session ในรอบนี้หรือไม่)
    rich_menu: str | None = None


def parse_postback_data(data: str) -> dict[str, str]:
    """
    แปลง postback data (querystring) เป็น dict

    >>> parse_postback_data('action=plan&term=1')
    {'action': 'plan', 'term': '1'}
    >>> parse_postback_data('')
    {}
    >>> parse_postback_data('action=documents&cat=loan')['cat']
    'loan'
    """
    return dict(parse_qsl(data or ""))


# ── ตัวช่วยจัดรูปข้อความ ─────────────────────────────────────────────────────


def join_lines(header: str, lines: list[str], footer: str = "") -> str:
    """
    ต่อบรรทัดโดยไม่ให้ทะลุ limit — ตัด **ทั้งบรรทัด** ไม่ตัดกลาง URL

    ตัดกลาง URL แล้วนักศึกษากดลิงก์ไม่ได้ ซึ่งแย่กว่าแสดงน้อยกว่าแล้วบอกว่ามีต่อ

    >>> join_lines('หัวข้อ', ['ก', 'ข'])
    'หัวข้อ\\n\\nก\\nข'
    >>> 'แสดง 1 จาก 2' in join_lines('ห', ['x' * 4000, 'y' * 400])
    True
    >>> join_lines('เฉย ๆ', [])
    'เฉย ๆ'
    """
    body: list[str] = []
    used = len(header) + len(footer)

    for line in lines:
        if used + len(line) + 1 > TEXT_BUDGET:
            break
        body.append(line)
        used += len(line) + 1

    parts = [header]
    if body:
        parts.append("\n".join(body))
    if len(body) < len(lines):
        parts.append(f"(แสดง {len(body)} จาก {len(lines)} รายการ)")
    if footer:
        parts.append(footer)
    return "\n\n".join(parts)


def _no_data(topic: str, intent_key: str | None = None) -> RouteResult:
    """
    ตอบว่าไม่มีข้อมูล

    แยก ``answered_by='no_data'`` ออกจาก ``'fallback'`` เพราะสองอย่างนี้
    ต่างกันตอนวัดผล: no_data = เข้าใจคำถามแต่ไม่มีข้อมูล,
    fallback = ไม่เข้าใจคำถาม
    """
    return RouteResult(
        messages=[msg.no_data_message(topic)],
        answered_by="no_data",
        intent_key=intent_key,
    )


def _fallback(intent_key: str | None = None) -> RouteResult:
    return RouteResult(
        messages=[msg.fallback_message()], answered_by="fallback", intent_key=intent_key
    )


def _db_error(topic: str, intent_key: str | None = None) -> RouteResult:
    """
    ตอบเมื่อ **ถามฐานข้อมูลไม่สำเร็จ** — ไม่ใช่ "ไม่มีข้อมูล"

    ต้องแยกออกจาก :func:`_no_data` ทั้งข้อความและ ``answered_by``:
    ถ้าใช้ข้อความเดียวกัน นักศึกษาจะเลิกถามเพราะคิดว่าไม่มีข้อมูลจริง
    และตัวเลขวัดผลในธีสิสจะนับ "DB ล่ม" เป็น "คลังข้อมูลไม่ครบ"
    """
    return RouteResult(
        messages=[
            msg.text_message(
                f"ขออภัยครับ ตอนนี้ระบบฐานข้อมูลขัดข้อง ยังดึงข้อมูล{topic}ให้ไม่ได้\n"
                "รบกวนลองอีกครั้งในอีกสักครู่ครับ",
                _menu_quick_reply(),
            )
        ],
        answered_by="db_error",
        intent_key=intent_key,
    )


async def _guard(
    answer: Awaitable[RouteResult], topic: str, intent_key: str | None = None
) -> RouteResult:
    """
    ดัก exception จากชั้นฐานข้อมูลไม่ให้บทสนทนา **เงียบหาย**

    ก่อนมีตัวนี้: DB ล่มกลางบทสนทนา → exception ทะลุขึ้นไปถึง
    ``app.main.process_event`` ที่ ``except Exception: log.exception(...)``
    → นักศึกษาไม่ได้ข้อความอะไรกลับเลย ซึ่งแย่กว่าได้คำตอบว่าระบบขัดข้อง

    ดักไว้ที่ทางเข้า (``handle_postback`` / ``handle_text``) ไม่ใช่ทุก handler
    เพราะทุกเส้นทางผ่านสองจุดนี้อยู่แล้ว — เพิ่มที่เดียวคุมได้ทั้งไฟล์
    และ ``app.db`` ยังไม่ต้องกลืน error (ถ้ากลืนที่นั้นจะแยกไม่ออกว่า
    "ไม่มีข้อมูล" กับ "ถามไม่ได้")
    """
    try:
        return await answer
    except Exception:
        log.exception("ตอบไม่ได้เพราะถามฐานข้อมูลไม่สำเร็จ (intent=%s)", intent_key)
        return _db_error(topic, intent_key)


# ป้ายชั่วคราวที่ handler ของปุ่มใช้ก่อน :func:`handle_postback` จะแทนด้วย
# พื้นผิวจริง — ไม่ควรหลุดออกไปถึง ``chat_logs`` (ถ้าหลุด = มี handler ที่
# ถูกเรียกโดยไม่ผ่าน handle_postback)
BUTTON_ANSWER = "button"

# postback ที่ยิงจาก Rich Menu ต้องมี ``src=rich`` ติดมา — ปุ่มใน Quick Reply
# ไม่มี ทำให้แยกสองพื้นผิวออกจากกันได้ใน ``chat_logs``
RICH_MENU_SOURCE = "rich"


def _answer_surface(params: dict[str, str]) -> str:
    """
    postback นี้มาจากพื้นผิวไหน

    ปุ่มบน Rich Menu กับปุ่มใน Quick Reply ยิง postback event **หน้าตาเหมือนกัน
    ทุกอย่าง** LINE ไม่บอกว่ามาจากไหน → ต้องฝังที่มาไว้ใน data เอง
    ปุ่มเก่าในเครื่องผู้ใช้ที่ยังไม่มี ``src`` จะถูกนับเป็น ``quick_reply``
    (ยอมพลาดฝั่งนี้ดีกว่าเคลมเกินว่าเป็นยอดกด Rich Menu)

    >>> _answer_surface({'action': 'documents', 'src': 'rich'})
    'rich_menu'
    >>> _answer_surface({'action': 'documents'})
    'quick_reply'
    """
    if params.get("src") == RICH_MENU_SOURCE:
        return "rich_menu"
    return "quick_reply"


def _menu_quick_reply(*extra: dict) -> dict:
    """ปุ่มพิเศษ + เมนูหลัก (รวมกันไม่เกิน 13 อยู่แล้ว)"""
    return msg.quick_reply([*extra, *msg.MAIN_MENU_ACTIONS])


def _list_quick_reply(buttons: list[dict]) -> dict:
    """
    ปุ่มรายการยาว ๆ + ปุ่มกลับเมนู 1 ปุ่ม

    เว้นที่ให้ปุ่ม "เมนูหลัก" เสมอ ไม่ให้ถูก clamp หายไปเมื่อรายการเยอะ
    (ถ้าไม่มีทางกลับเมนู user จะติดอยู่ในหน้านั้น)
    """
    room = msg.MAX_QUICK_REPLY_ITEMS - 1
    return msg.quick_reply(
        [*buttons[:room], msg.postback_action("เมนูหลัก", "action=menu")]
    )


# ── ชั้นที่ 1: postback จาก Rich Menu / Quick Reply ──────────────────────────
#
# ใช้ postback ไม่ใช่ข้อความ เพราะรู้ intent แน่นอน ไม่ต้องเดา
# → ไม่มีทางตอบผิดหมวด และไม่เสียค่า LLM

POSTBACK_HANDLERS: dict[str, str] = {
    "plan": "แผนการเรียน",
    # ความก้าวหน้าตามหลักสูตร — ``action=progress`` = ภาพรวม,
    # ``action=progress&next=1`` = เสนอวิชาเทอมถัดไป (ดู app/progress.py)
    "progress": "ความก้าวหน้าตามหลักสูตร",
    "calendar": "ปฏิทินการศึกษา",
    "documents": "เอกสาร/คำร้อง",
    "instructors": "ติดต่ออาจารย์",
    "loan": "ทุน/กู้ยืม",
    "menu": "เมนูหลัก",
    # ค้นรายวิชา — ``action=course`` เปล่า ๆ = อธิบายวิธีใช้ + ปุ่มวิชาตัวอย่าง,
    # ``action=course&code=1109901`` = ตอบรายวิชานั้นตรง ๆ (เส้นทางเดียวกับ
    # ที่ผู้ใช้พิมพ์รหัส 7 หลักมาเอง)
    "course": "ค้นรายวิชา",
    # โหมดปรึกษา AI — เข้า/ออกชัด ๆ เพื่อกันเสีย token ฟรีกับทุก search miss
    # (เงื่อนไข+กติกาทั้งหมดอยู่ที่ app/ai_chat.py::dispatch)
    "ai_session": "ปรึกษา AI",
    "ai_end": "จบการปรึกษา",
}

# ชื่อหมวดเอกสารเป็นภาษาไทย — ต้องไม่เกิน 20 ตัวอักษรเพราะใช้เป็น label ของปุ่ม
DOCUMENT_CATEGORY_LABELS: dict[str, str] = {
    "registration": "ลงทะเบียน/เพิ่ม-ถอน",
    "loan": "กู้ยืม กยศ.",
    "scholarship": "ทุนการศึกษา",
    "internship": "ฝึกงาน/สหกิจ",
    "calendar": "ปฏิทินการศึกษา",
    "curriculum": "หลักสูตร",
    "regulation": "ระเบียบ/ข้อบังคับ",
    "exam_prep": "เตรียมสอบ",
    "activity": "กิจกรรมนักศึกษา",
    "it_account": "บัญชีไอที/อีเมล",
    "staff": "เจ้าหน้าที่/บุคลากร",
}

# ปุ่มในเมนูหลักที่แมปตรงเข้าหมวดเอกสาร
MENU_CATEGORY_SHORTCUTS: dict[str, str] = {
    "loan": "loan",
    "calendar": "calendar",
}


def category_label(category: str) -> str:
    """
    ชื่อไทยของหมวดเอกสาร

    >>> category_label('loan')
    'กู้ยืม กยศ.'
    >>> category_label('หมวดที่ยังไม่ได้แปล')
    'หมวดที่ยังไม่ได้แปล'
    """
    return DOCUMENT_CATEGORY_LABELS.get(category, category)


async def handle_postback(
    data: str,
    db: SupportsQuery | None = None,
    *,
    settings: Any | None = None,
    llm: Any | None = None,
    user_hash: str | None = None,
) -> RouteResult:
    """
    จัดการ postback event — ชั้นที่ 1

    handler ที่ต้องใช้ DB จะเช็ค ``db is None`` ก่อนเสมอ แล้วตอบว่าไม่มีข้อมูล
    ส่วนกรณี DB ล่ม *ระหว่าง* ใช้งาน :func:`_guard` จะดักให้

    ``settings``/``llm``/``user_hash`` ใช้เฉพาะปุ่มโหมดปรึกษา (``ai_session``
    / ``ai_end``) — ปุ่มอื่นไม่แตะ LLM เลย (keyword-only + ``None`` ได้
    เหมือน :func:`handle_text` เทสเดิมเรียกแบบเก่าได้เหมือนเดิม)
    """
    params = parse_postback_data(data)
    action = params.get("action", "")
    result = await _guard(
        _dispatch_postback(
            data, action, params, db,
            settings=settings, llm=llm, user_hash=user_hash,
        ),
        topic="ที่ขอ",
        intent_key=action or None,
    )
    # ตอบสำเร็จด้วยปุ่ม → เปลี่ยนป้ายกลาง ๆ เป็นพื้นผิวจริงที่กดมา
    # ทำที่นี่ที่เดียวเพราะ "มาจากพื้นผิวไหน" เป็นคุณสมบัติของ *event*
    # ไม่ใช่ของ handler — handler แต่ละตัวไม่ต้องรู้เรื่องนี้เลย
    # ส่วน no_data / db_error / fallback ทับป้ายพื้นผิวไว้แล้วโดยเจตนา
    if result.answered_by == BUTTON_ANSWER:
        result.answered_by = _answer_surface(params)
    return result


async def _dispatch_postback(
    data: str,
    action: str,
    params: dict[str, str],
    db: SupportsQuery | None,
    *,
    settings: Any | None = None,
    llm: Any | None = None,
    user_hash: str | None = None,
) -> RouteResult:
    """``data`` ดิบส่งมาด้วยเพื่อให้ log บอกได้ว่า postback ที่ไม่รู้จักหน้าตาแบบไหน"""
    if action not in POSTBACK_HANDLERS:
        log.warning("postback ที่ไม่รู้จัก: %r", data)
        return _fallback()

    if action in ("ai_session", "ai_end"):
        from . import ai_chat

        result = await ai_chat.dispatch(
            settings, llm, db, user_hash, "",
            is_session_postback=(action == "ai_session"),
            is_end_postback=(action == "ai_end"),
        )
        # เงื่อนไขไม่ครบ (ปิดสวิตช์/ไม่มี key/ไม่มี DB) → ตอบ fallback
        # ดีกว่าเงียบหาย (user กดปุ่มของเราแล้วต้องได้คำตอบเสมอ)
        return result or _fallback(action)

    if action == "menu":
        return await handle_follow(intent_key="menu")

    if action == "documents":
        category = params.get("cat", "")
        if category:
            return await _documents_answer(db, category)
        return await _document_categories_answer(db)

    if action in MENU_CATEGORY_SHORTCUTS:
        return await _documents_answer(db, MENU_CATEGORY_SHORTCUTS[action], action)

    if action == "instructors":
        group = params.get("g", "")
        if group:
            return await _instructors_answer(db, group)
        return await _instructor_groups_answer(db)

    if action == "plan":
        return await _plan_answer(db)

    if action == "progress":
        from . import progress as prog

        if params.get("next"):
            return await prog.next_term_answer(db, user_hash, settings)
        return await prog.progress_answer(db, user_hash, settings)

    if action == "course":
        code = params.get("code", "")
        if code:
            return await _course_answer(db, code)
        return await _course_help_answer(db)

    # มาถึงนี่ = เพิ่ม action ใน POSTBACK_HANDLERS แล้วลืมเขียน handler
    log.error("action %r อยู่ใน POSTBACK_HANDLERS แต่ยังไม่มี handler", action)
    return _fallback(action)


# ── เอกสาร / คำร้อง ──────────────────────────────────────────────────────────


async def _document_categories_answer(db: SupportsQuery | None) -> RouteResult:
    if db is None:
        return _no_data("เอกสาร", "documents")

    rows = await repo.document_categories(db)
    if not rows:
        return _no_data("เอกสาร", "documents")

    lines = [
        f"  • {category_label(row['category'])} ({row['total']} ฉบับ)" for row in rows
    ]
    buttons = [
        msg.postback_action(
            category_label(row["category"]), f"action=documents&cat={row['category']}"
        )
        for row in rows
    ]

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(
                    "เอกสารและแบบฟอร์มคำร้องที่มีในระบบ",
                    lines,
                    "เลือกหมวดจากปุ่มด้านล่างได้เลยครับ",
                ),
                _list_quick_reply(buttons),
            )
        ],
        answered_by=BUTTON_ANSWER,
        intent_key="documents",
        confidence=1.0,
    )


async def _documents_answer(
    db: SupportsQuery | None, category: str, intent_key: str | None = None
) -> RouteResult:
    intent = intent_key or f"documents:{category}"
    label = category_label(category)

    if db is None:
        return _no_data(f"เอกสารหมวด{label}", intent)

    rows = await repo.documents_in_category(
        db, category, limit=DOCUMENTS_PER_CATEGORY
    )
    if not rows:
        return _no_data(f"เอกสารหมวด{label}", intent)

    lines: list[str] = []
    for index, row in enumerate(rows, start=1):
        lines.append(f"{index}. {row['title']}")
        lines.append(f"   {row['url']}")
        if row.get("note"):
            lines.append(f"   หมายเหตุ: {row['note']}")

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(
                    f"เอกสารหมวด{label} ({len(rows)} ฉบับ)",
                    lines,
                    "กดลิงก์เพื่อดาวน์โหลดได้เลยครับ",
                ),
                _menu_quick_reply(msg.postback_action("หมวดอื่น", "action=documents")),
            )
        ],
        answered_by=BUTTON_ANSWER,
        intent_key=intent,
        confidence=1.0,
        citations=[{"title": row["title"], "url": row["url"]} for row in rows],
    )


# ── อาจารย์ ─────────────────────────────────────────────────────────────────


def _contact_caveat(coverage: dict) -> str:
    """
    บอกตรง ๆ ว่าข้อมูลติดต่อมีแค่ไหน

    เว็บคณะไม่เผยแพร่เบอร์โทร (0/28 คน) — ถ้าไม่บอก ผู้ใช้จะคิดว่าระบบพัง
    หรือแย่กว่านั้นคือคาดหวังให้บอทเดาเบอร์ให้
    """
    total = coverage.get("total") or 0
    if not total:
        return ""

    with_email = coverage.get("with_email") or 0
    with_phone = coverage.get("with_phone") or 0

    parts = [f"ข้อมูลที่มี: อีเมล {with_email}/{total} คน"]
    if with_phone:
        parts.append(f"เบอร์โทร {with_phone}/{total} คน")
    else:
        parts.append(
            "ยังไม่มีเบอร์โทรในระบบ (เว็บคณะไม่ได้เผยแพร่) — ต้องติดต่อสำนักงานคณะ"
        )
    return "\n".join(parts)


async def _instructor_groups_answer(db: SupportsQuery | None) -> RouteResult:
    if db is None:
        return _no_data("อาจารย์", "instructors")

    rows = await repo.instructor_groups(db)
    if not rows:
        return _no_data("อาจารย์", "instructors")

    coverage = await repo.instructor_contact_coverage(db)
    lines = [f"  • {row['group_name']} ({row['total']} คน)" for row in rows]
    buttons = [
        msg.postback_action(
            row["group_name"], f"action=instructors&g={row['group_name']}"
        )
        for row in rows
    ]

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(
                    "สาขา/กลุ่มวิชาที่มีข้อมูลอาจารย์", lines, _contact_caveat(coverage)
                ),
                _list_quick_reply(buttons),
            )
        ],
        answered_by=BUTTON_ANSWER,
        intent_key="instructors",
        confidence=1.0,
    )


def _instructor_name(row: dict) -> str:
    """
    ชื่ออาจารย์พร้อมคำนำหน้า — **ห้ามเอา ``title_prefix`` มาต่อหน้า ``full_name``**

    ตรวจกับข้อมูลจริงแล้ว ``full_name`` ทั้ง 28 แถว **มีคำนำหน้าอยู่ในตัวแล้ว**
    (``title_prefix`` = "ผู้ช่วยศาสตราจารย์ ดร" และ ``full_name`` =
    "ผู้ช่วยศาสตราจารย์ ดร.ธรัช อารีราษฎร์") การต่อกันจึงได้คำนำหน้าซ้ำสองรอบ
    ซึ่งเป็นสิ่งที่โค้ดเดิมทำ — mock จับไม่ได้เพราะใส่ค่าที่ไม่ซ้ำกันเอง

    เก็บ ``title_prefix`` ไว้ในฐานข้อมูลต่อ เผื่อวันหลัง scraper แยกสองฟิลด์จริง
    """
    return (row.get("full_name") or "").strip()


async def _instructors_answer(db: SupportsQuery | None, group: str) -> RouteResult:
    intent = f"instructors:{group}"
    if db is None:
        return _no_data(f"อาจารย์กลุ่ม{group}", intent)

    rows = await repo.instructors_in_group(db, group)
    if not rows:
        return _no_data(f"อาจารย์กลุ่ม{group}", intent)

    lines: list[str] = []
    for index, row in enumerate(rows, start=1):
        lines.append(f"{index}. {_instructor_name(row)}")
        if row.get("position"):
            lines.append(f"   ตำแหน่ง: {row['position']}")
        # บอกตรง ๆ เมื่อไม่มีอีเมล ห้ามเว้นว่างให้เข้าใจผิดว่าระบบโหลดไม่ครบ
        lines.append(f"   อีเมล: {row.get('email') or 'ไม่มีข้อมูลในระบบ'}")
        if row.get("room"):
            lines.append(f"   ห้อง: {row['room']}")
        if row.get("office_hours"):
            lines.append(f"   เวลาเข้าพบ: {row['office_hours']}")

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(f"อาจารย์กลุ่ม{group} ({len(rows)} คน)", lines),
                _menu_quick_reply(msg.postback_action("กลุ่มอื่น", "action=instructors")),
            )
        ],
        answered_by=BUTTON_ANSWER,
        intent_key=intent,
        confidence=1.0,
    )


# ── แผนการเรียน ─────────────────────────────────────────────────────────────


async def _plan_answer(db: SupportsQuery | None) -> RouteResult:
    """
    ตอบเรื่องแผนการเรียนอย่างซื่อสัตย์

    ระบบทะเบียนไม่เผยแพร่ prerequisite และแผนปี/เทอม → ต้องกรอกมือจาก มคอ.2
    ซึ่งยังไม่มีเล่ม จึง **ห้ามเดา** ตอนนี้ตอบได้แค่ "วิชาไหนเปิดเทอมไหน"
    จาก ``offering_patterns`` ที่สรุปจากตารางสอนย้อนหลัง
    """
    if db is None:
        return _no_data("แผนการเรียน", "plan")

    coverage = await repo.planning_coverage(db, _program_code())
    rules = coverage.get("curriculum_rules") or 0
    prerequisites = coverage.get("prerequisites") or 0
    patterns = coverage.get("patterns") or 0

    if not patterns and not rules:
        return _no_data("แผนการเรียน", "plan")

    lines = [
        f"  • รายวิชาในหลักสูตร {coverage.get('program_courses') or 0} วิชา",
        f"  • รู้ว่าเปิดเทอมไหน {patterns} วิชา"
        f" (เทอม 1: {coverage.get('opens_sem1') or 0},"
        f" เทอม 2: {coverage.get('opens_sem2') or 0},"
        f" ฤดูร้อน: {coverage.get('opens_sem3') or 0})",
    ]

    if rules:
        lines.insert(
            0, f"  • แผนการเรียนมาตรฐาน {rules} วิชา (รู้ว่าวิชาไหนอยู่ปี/เทอมไหน)"
        )

    if prerequisites and rules:
        footer = "ถามได้เลยครับ เช่น “ลงวิชา 7071201 ได้เลยไหม”"
    elif rules:
        # สถานะตอนนี้: มีแผนปี/เทอมแล้ว แต่ prerequisites ยังว่าง
        # → คำนวณได้จริง แต่ต้องไม่เคลมว่ารู้เงื่อนไขวิชาบังคับก่อน
        footer = (
            "คำนวณให้ได้แล้วครับว่าผ่านไปเท่าไร เหลืออะไร และเทอมหน้าควรลงอะไร\n"
            "(กดปุ่ม “ความก้าวหน้า” — ครั้งแรกต้องติ๊กวิชาที่ผ่านมาก่อน)\n\n"
            "ยังไม่มีข้อมูลวิชาบังคับก่อน (prerequisite) ที่ระบบทะเบียนไม่เผยแพร่\n"
            "ลำดับที่ได้จึงเป็นเทอมที่แผนแนะนำ ไม่ใช่เงื่อนไขบังคับครับ"
        )
    else:
        footer = (
            "ยังจัดแผนรายเทอมให้ไม่ได้ครับ เพราะยังไม่มีแผนปี/เทอมของหลักสูตรนี้\n\n"
            "ระหว่างนี้พิมพ์รหัสวิชา 7 หลักมาได้ครับ จะบอกว่าวิชานั้นเปิดเทอมไหน"
        )

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines("ข้อมูลแผนการเรียนที่ระบบมีตอนนี้", lines, footer),
                _menu_quick_reply(),
            )
        ],
        answered_by=BUTTON_ANSWER,
        intent_key="plan",
        confidence=1.0,
    )


def _program_code() -> str:
    """
    รหัสหลักสูตรใน scope — อ่านจาก settings แบบ lazy

    import ในฟังก์ชันเพื่อไม่ให้ router ผูกกับการโหลด ``.env`` ตอน import
    """
    from .config import get_settings

    return get_settings().default_program_code


# ── ชั้นที่ 2 + 3: ข้อความพิมพ์อิสระ ─────────────────────────────────────────


async def handle_text(
    text: str,
    db: SupportsQuery | None = None,
    *,
    settings: Any | None = None,
    llm: Any | None = None,
    user_hash: str | None = None,
) -> RouteResult:
    """
    จัดการข้อความที่ user พิมพ์เอง

    ทำแล้ว: **รหัสวิชา 7 หลัก** → ตอบจาก DB ตรง ๆ, **ความก้าวหน้าตามหลักสูตร**
    (ชั้น planner — คำนวณ ไม่ใช่ค้น ดู :mod:`app.progress`), **โหมดปรึกษา AI**
    (ดักก่อน search — ดู :mod:`app.ai_chat`), และ **ค้นด้วยคำที่พิมพ์มา**
    (``pg_trgm`` word_similarity) → เอกสาร/อาจารย์ ทั้งสองทางยังเป็นชั้นที่ 1
    คือตอบจากฐานข้อมูลตรง ๆ
    search ไม่เจอ → ตอบ fallback พร้อม **ปุ่ม "ปรึกษา AI"** (ไม่ยิง LLM
    ทันทีทุกข้อความ กันเสีย token ฟรีกับพิมพ์ผิด/คำทักทาย)
    ยังไม่ทำ: FAQ ที่คนเขียนคำตอบไว้ (ชั้น 2) และ RAG (ตาราง ``rag_chunks`` ว่าง)

    ``settings``/``llm``/``user_hash`` เป็น keyword-only และ ``None`` ได้ —
    เทสเดิมที่เรียก ``handle_text(text, db)`` ยังทำงานเหมือนเดิมทุกประการ
    (ไม่มี LLM ก็ตอบ fallback แบบเก่า)
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return _fallback()

    return await _guard(
        _dispatch_text(cleaned, db, settings=settings, llm=llm, user_hash=user_hash),
        topic="ที่ถาม",
        intent_key="text",
    )


async def _dispatch_text(
    cleaned: str,
    db: SupportsQuery | None,
    *,
    settings: Any | None = None,
    llm: Any | None = None,
    user_hash: str | None = None,
) -> RouteResult:
    # ── ชั้น planner: คำนวณจากข้อมูลจริง มาก่อน LLM เสมอ ────────────────────
    # เหตุผลเดียวกับที่รหัสวิชา 7 หลักถูกดักก่อนโหมดปรึกษาอยู่แล้ว: เรื่องที่
    # คำนวณได้แน่นอน (หน่วยกิต ลำดับวิชา) ห้ามให้ LLM เดา ต่อให้ผู้ใช้กำลัง
    # อยู่ในโหมดปรึกษาก็ตาม
    from . import progress as prog

    match = COURSE_CODE_PATTERN.search(cleaned)
    if match:
        code = match.group(1)
        # "ลงวิชา 7071201 ได้เลยไหม" ถามเงื่อนไขการลง ไม่ได้ถามรายละเอียดวิชา
        # ตอบไม่ได้ (ยังไม่ติ๊กวิชา / วิชาไม่อยู่ในแผน) → ถอยไปทางเดิม
        if prog.ELIGIBILITY_PATTERN.search(cleaned):
            eligibility = await prog.eligibility_answer(db, user_hash, settings, code)
            if eligibility is not None:
                return eligibility
        return await _course_answer(db, code, answered_by="course")

    if prog.NEXT_TERM_PATTERN.search(cleaned):
        return await prog.next_term_answer(db, user_hash, settings)

    if prog.PROGRESS_PATTERN.search(cleaned):
        return await prog.progress_answer(db, user_hash, settings)

    # ── ชั้นที่ 3: โหมดปรึกษา AI — ตรวจก่อน search ─────────────────────────
    # ข้อความระหว่างอยู่ในโหมดต้องตอบด้วย LLM (คนในโหมดต้องการคำตอบ
    # ไม่ใช่ลิงก์เอกสาร) และคำออก/คำเข้าโหมดต้องถูกดักก่อน search เช่นกัน
    # ถ้าไม่มี session เปิดอยู่และไม่ได้เข้าโหมด dispatch คืน ``None``
    # แล้วไหลไป search ตามปกติ
    # import ตรงนี้ไม่ใช่บนไฟล์ เพราะ ``ai_chat`` import RouteResult จากไฟล์นี้
    # กลับไป (circular import)
    from . import ai_chat
    from .llm import LlmError

    try:
        result = await ai_chat.dispatch(settings, llm, db, user_hash, cleaned)
    except LlmError:
        # LLM timeout/429/ตอบว่าง — บอกตรง ๆ ว่าระบบ AI ขัดข้อง
        # แย่กว่าตอบว่าไม่มีข้อมูลนิดเดียว แต่ดีกว่าเงียบหายแน่นอน
        log.warning("AI Chat ไม่สำเร็จ — ตอบขัดข้องแทน", exc_info=True)
        return RouteResult(
            messages=[
                msg.text_message(
                    "ขออภัยครับ ตอนนี้ระบบตอบด้วย AI ขัดข้องชั่วคราว\n"
                    "รบกวนลองอีกครั้งในอีกสักครู่ หรือเลือกหัวข้อจากปุ่มด้านล่างครับ",
                    _menu_quick_reply(),
                )
            ],
            answered_by="fallback",
            intent_key="ai_chat_error",
        )
    if result is not None:
        return result

    if db is not None:
        found = await _search_answer(db, cleaned)
        if found is not None:
            return found

    # search ไม่เจอ — เสนอทางเข้าโหมดปรึกษา AI (ถ้าชั้นนั้นพร้อม) แทนการยิง
    # LLM ทันทีทุกข้อความ: กันเสีย token ฟรีกับพิมพ์ผิด/คำทักทาย/คำถามที่
    # LLM ก็ต้องตอบว่าไม่มีข้อมูลอยู่ดี
    extra = (
        [msg.CONSULT_AI_ACTION]
        if settings is not None and llm is not None and settings.ai_chat_enabled
        else []
    )
    return RouteResult(
        messages=[
            msg.text_message(
                "ยังไม่พบข้อมูลที่ตรงกับคำที่พิมพ์มาครับ\n\n"
                f"“{msg.truncate(cleaned, 120)}”\n\n"
                "ตอนนี้ค้นได้: ชื่อเอกสาร/แบบฟอร์มคำร้อง, ชื่ออาจารย์,\n"
                "และรหัสวิชา 7 หลัก\n"
                "หรือเลือกหัวข้อจากปุ่มด้านล่างครับ",
                _menu_quick_reply(*extra),
            )
        ],
        answered_by="fallback",
        intent_key="text",
    )


# ── ค้นด้วยคำที่พิมพ์มา ────────────────────────────────────────────────────────


async def _search_answer(db: SupportsQuery, keyword: str) -> RouteResult | None:
    """
    ค้นจากคำที่พิมพ์มา — คืน ``None`` เมื่อไม่เจอ เพื่อให้ผู้เรียกไปต่อชั้นถัดไป

    **ลำดับ: อาจารย์ก่อน แล้วค่อยเอกสาร** และ *ไม่* เรียงด้วย ``score`` ข้ามตาราง
    เหตุผลมาจากการวัดกับข้อมูลจริง 16 คำถาม:

    * การค้นอาจารย์คืน **0 แถวสำหรับคำถามเรื่องเอกสารทุกข้อ** (12/12) เพราะ
      ต้องมีชื่อคนอยู่ในข้อความถึงจะแมตช์ → เอาขึ้นก่อนแล้วไม่แย่งงานกัน
    * ส่วนการค้นเอกสาร **แย่งคำถามที่ถามถึงตัวบุคคลได้** เพราะเอกสาร
      "ข้อมูลบุคลากรสายวิชาการ" มี keyword ว่า "อาจารย์" / "อีเมลอาจารย์"
      → "อาจารย์ธรัชสอนวิชาอะไร" ได้เอกสาร 1.000 แต่ได้ตัวอาจารย์ 0.800
      ถ้าเรียงด้วยคะแนนจะตอบเป็นลิงก์รายชื่อบุคลากรแทนอีเมลของคนที่ถามถึง

    กล่าวคือชื่อคนเป็นสัญญาณที่เฉพาะเจาะจงกว่าคำเชิงหัวข้อ คะแนนดิบเทียบข้ามตาราง
    ไม่ได้ ยิง query ที่สองเฉพาะตอนที่อันแรกไม่เจอ และสองตารางรวมกันไม่ถึง 60 แถว
    """
    instructors = await repo.search_instructors(db, keyword, limit=SEARCH_RESULT_LIMIT)
    if instructors:
        return _instructor_search_result(keyword, instructors)

    documents = await repo.search_documents(db, keyword, limit=SEARCH_RESULT_LIMIT)
    if documents:
        return _document_search_result(keyword, documents)

    return None


def _document_search_result(keyword: str, rows: list[dict]) -> RouteResult:
    """
    ผลค้นเอกสาร — แนบ URL ทุกฉบับ และให้ปุ่มไปดูทั้งหมดในหมวดที่เจอ

    ``confidence`` ใช้คะแนน ``word_similarity`` ของแถวแรกตรง ๆ เพื่อให้
    ``chat_logs`` วัดได้ภายหลังว่าคำถามที่ตอบด้วยชั้นนี้มั่นใจแค่ไหนจริง
    (1.0 = คำค้นอยู่ใน ``keywords``/``title`` แบบตรงตัว)
    """
    lines: list[str] = []
    for index, row in enumerate(rows, start=1):
        lines.append(f"{index}. {row['title']}")
        lines.append(f"   {row['url']}")
        lines.append(f"   หมวด: {category_label(row['category'])}")

    # dict.fromkeys = unique แบบรักษาลำดับ (เรียงตามคะแนนที่ SQL จัดมาให้แล้ว)
    buttons = [
        msg.postback_action(category_label(category), f"action=documents&cat={category}")
        for category in dict.fromkeys(row["category"] for row in rows)
    ]

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(
                    f"ค้น “{msg.truncate(keyword, 40)}” เจอเอกสาร {len(rows)} ฉบับ",
                    lines,
                    "กดลิงก์เพื่อดาวน์โหลด หรือกดปุ่มเพื่อดูทั้งหมดในหมวดนั้นครับ",
                ),
                _list_quick_reply(buttons),
            )
        ],
        answered_by="search",
        intent_key="search:documents",
        confidence=float(rows[0]["score"]),
        citations=[{"title": row["title"], "url": row["url"]} for row in rows],
    )


def _instructor_search_result(keyword: str, rows: list[dict]) -> RouteResult:
    """
    ผลค้นอาจารย์ — ไม่มี ``citations`` เพราะตาราง ``instructors`` ไม่มี URL ต่อคน

    ไม่ใส่เบอร์โทรเพราะทั้ง 28 แถวไม่มีข้อมูลเบอร์เลย (ห้ามเว้นบรรทัดว่างไว้
    ให้เข้าใจผิดว่าระบบโหลดไม่ครบ — ดู :func:`_contact_caveat`)
    """
    lines: list[str] = []
    for index, row in enumerate(rows, start=1):
        lines.append(f"{index}. {_instructor_name(row)}")
        lines.append(f"   อีเมล: {row.get('email') or 'ไม่มีข้อมูลในระบบ'}")
        if row.get("room"):
            lines.append(f"   ห้อง: {row['room']}")
        if row.get("office_hours"):
            lines.append(f"   เวลาเข้าพบ: {row['office_hours']}")

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(
                    f"ค้น “{msg.truncate(keyword, 40)}” เจออาจารย์ {len(rows)} คน",
                    lines,
                    "ดูรายชื่อทั้งกลุ่มได้จากปุ่มด้านล่างครับ",
                ),
                _menu_quick_reply(
                    msg.postback_action("อาจารย์ทั้งหมด", "action=instructors")
                ),
            )
        ],
        answered_by="search",
        intent_key="search:instructors",
        confidence=float(rows[0]["score"]),
    )


async def _course_answer(
    db: SupportsQuery | None, course_code: str, answered_by: str = BUTTON_ANSWER
) -> RouteResult:
    """
    ตอบรายละเอียดรายวิชา — เข้าได้ 2 ทาง

    ผู้ใช้ **พิมพ์รหัส 7 หลัก** มาเอง → ``answered_by='course'``
    (เดิมป้ายว่า ``rich_menu`` ซึ่งผิด: ไม่ได้กดปุ่มอะไรเลย)
    กด **ปุ่มวิชาตัวอย่าง** → ป้ายกลาง ๆ แล้วให้ :func:`handle_postback`
    แทนด้วยพื้นผิวจริง
    """
    intent = f"course:{course_code}"
    if db is None:
        return _no_data(f"รายวิชา {course_code}", intent)

    course = await repo.course_by_code(db, course_code)
    if not course:
        return _no_data(f"รายวิชา {course_code}", intent)

    lines = [f"  • ชื่อวิชา: {course.get('name_th') or '-'}"]
    if course.get("name_en"):
        lines.append(f"  • ชื่ออังกฤษ: {course['name_en']}")
    if course.get("credits_text"):
        lines.append(f"  • หน่วยกิต: {course['credits_text']}")

    terms = [
        TERM_LABELS[number]
        for number, opens in (
            (1, course.get("opens_sem1")),
            (2, course.get("opens_sem2")),
            (3, course.get("opens_sem3")),
        )
        if opens
    ]
    if terms:
        observed = course.get("terms_observed") or 0
        lines.append(
            f"  • เคยเปิด: {', '.join(terms)} (จาก {observed} เทอมที่เก็บข้อมูลไว้)"
        )
    else:
        lines.append("  • ยังไม่พบว่าเปิดสอนในเทอมที่เก็บข้อมูลไว้")

    description = (course.get("description_th") or "").strip()
    footer = (
        f"คำอธิบายรายวิชา:\n{msg.truncate(description, 800)}" if description else ""
    )

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(f"รายวิชา {course_code}", lines, footer), _menu_quick_reply()
            )
        ],
        answered_by=answered_by,
        intent_key=intent,
        confidence=1.0,
        citations=(
            [
                {
                    "title": course.get("name_th") or course_code,
                    "url": course["source_url"],
                }
            ]
            if course.get("source_url")
            else []
        ),
    )


async def _course_help_answer(db: SupportsQuery | None) -> RouteResult:
    """
    ปุ่ม *ค้นรายวิชา* บน Rich Menu — บอกวิธีใช้ **พร้อมของให้กดต่อทันที**

    Rich Menu ไม่มี action ที่สั่งให้ผู้ใช้พิมพ์ต่อได้ ถ้าตอบแค่ "พิมพ์รหัสวิชา
    7 หลักมา" ผู้ใช้ที่ไม่รู้รหัสวิชาจะตันอยู่ตรงนั้น จึงแนบวิชาตัวอย่างจริง
    จากฐานข้อมูลมาเป็นปุ่ม (``action=course&code=...``) ให้กดเห็นผลลัพธ์ก่อน
    แล้วค่อยพิมพ์รหัสของตัวเอง

    **ห้าม hardcode รหัสตัวอย่าง** — ถ้า re-scrape แล้วรหัสนั้นหายไป
    บอทจะแนะนำวิชาที่ตัวเองตอบไม่ได้
    """
    intent = "course"
    if db is None:
        return _no_data("รายวิชา", intent)

    program = _program_code()
    coverage = await repo.planning_coverage(db, program)
    samples = await repo.sample_courses(db, program, limit=SAMPLE_COURSE_COUNT)

    total = coverage.get("program_courses") or 0
    patterns = coverage.get("patterns") or 0
    if not total and not samples:
        return _no_data("รายวิชา", intent)

    lines = [f"  • รายวิชาในหลักสูตร {total} วิชา"]
    if patterns:
        lines.append(f"  • รู้ว่าเคยเปิดเทอมไหน {patterns} วิชา")

    example = samples[0]["course_code"] if samples else None
    footer = (
        f"พิมพ์รหัสวิชา 7 หลักมาได้เลยครับ เช่น {example}"
        if example
        else "พิมพ์รหัสวิชา 7 หลักมาได้เลยครับ"
    )
    if samples:
        footer += "\nหรือกดวิชาตัวอย่างจากปุ่มด้านล่างก็ได้ครับ"

    # label ปุ่มยาวได้ 20 ตัวอักษร: รหัส 7 + เว้นวรรค 1 = 8 → เหลือชื่อ 12
    buttons = [
        msg.postback_action(
            f"{row['course_code']} {msg.truncate(row.get('name_th') or '', 12)}".strip(),
            f"action=course&code={row['course_code']}",
        )
        for row in samples
    ]

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines("ค้นรายละเอียดรายวิชา", lines, footer),
                _list_quick_reply(buttons),
            )
        ],
        answered_by=BUTTON_ANSWER,
        intent_key=intent,
        confidence=1.0,
    )


async def handle_follow(intent_key: str = "follow") -> RouteResult:
    """
    ข้อความต้อนรับ — ใช้ทั้งตอน follow และตอนกดปุ่ม "เมนูหลัก"

    ``intent_key`` แยกสองกรณีเพื่อให้สถิติใน ``chat_logs`` ไม่ปนกัน
    และ ``answered_by`` ก็ต้องแยกด้วย: การ **เพิ่มเพื่อน** ไม่ใช่การกดปุ่ม
    (เดิมนับเป็น ``rich_menu`` ทั้งคู่ ทำให้ยอดกดเมนูเกินความจริงทุกครั้ง
    ที่มีคนเพิ่มเพื่อนใหม่)
    """
    return RouteResult(
        messages=[
            msg.text_message(
                "สวัสดีครับ ผมเป็นผู้ช่วยให้คำปรึกษาด้านการเรียน\n\n"
                "ตอนนี้ทำได้\n"
                "  • หาเอกสาร/แบบฟอร์มคำร้อง 31 ฉบับ 10 หมวด\n"
                "  • ดูข้อมูลติดต่ออาจารย์ (อีเมล — ยังไม่มีเบอร์โทรในระบบ)\n"
                "  • พิมพ์รหัสวิชา 7 หลัก เพื่อดูรายละเอียดรายวิชา\n"
                "  • พิมพ์คำที่อยากค้นมาได้เลย เช่น ชื่อเอกสารหรือชื่ออาจารย์\n"
                "  • กด “ปรึกษา AI” บนเมนู หรือพิมพ์ “ปรึกษา” ตามด้วยคำถาม\n\n"
                "ยังทำไม่ได้: จัดแผนรายเทอมและตรวจวิชาบังคับก่อน\n"
                "(ระบบทะเบียนไม่ได้เผยแพร่ข้อมูลส่วนนี้)\n\n"
                "เลือกจากปุ่มด้านล่างได้เลยครับ",
                _menu_quick_reply(),
            )
        ],
        answered_by=BUTTON_ANSWER if intent_key == "menu" else "follow",
        intent_key=intent_key,
        confidence=1.0,
    )
