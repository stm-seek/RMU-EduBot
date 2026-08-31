"""
ชั้น planner ที่ต่อกับบทสนทนา — "ความก้าวหน้าตามหลักสูตร" (Requirement 4.1 หมวด 3)

แยกจาก :mod:`app.router` เพราะสองเรื่องนี้ต่างกันจริง:
router เลือกว่าคำถามควรไปทางไหน ส่วนไฟล์นี้ **ประกอบคำตอบจากตัวเลขที่คำนวณ**
โดย :mod:`app.planner` (ซึ่งไม่รู้จัก LINE เลย และเทสได้โดยไม่มี DB)

ทิศทาง import เหมือน :mod:`app.ai_chat`: ไฟล์นี้ import จาก router
ส่วน router import ไฟล์นี้แบบ lazy ในฟังก์ชัน (กัน circular import)

**ไม่มี LLM ในไฟล์นี้** ตัวเลขหน่วยกิตกับลำดับวิชาผิดแล้วนักศึกษาลงทะเบียน
พลาดจริง — LLM เอาไปเรียบเรียงต่อได้ แต่ห้ามเป็นคนคิด
"""

from __future__ import annotations

import logging
import re
from typing import Any

from . import gpa
from . import planner
from . import repository as repo
from .db import SupportsQuery
from .line import flex
from .line import messages as msg
from .router import RouteResult, join_lines

log = logging.getLogger("app.progress")

# ป้ายใน chat_logs — ประกาศไว้ใน db/migrations/005_planner.sql แล้ว
PLANNER_ANSWER = "planner"

# คำถามที่ควรเข้าชั้นนี้ ไม่ใช่ไปค้นเอกสาร
#
# ตั้งใจให้แคบ: จับกว้างไปแล้วคำถามเรื่องเอกสาร ("ขอใบรายงานผลการเรียน")
# จะถูกดูดมาตอบด้วยแผนการเรียน ซึ่งไม่ใช่คำตอบที่ถาม
# ``(?:กี่|เท่าไหร่|เท่าไร)`` เพราะคนถามคำถามเดียวกันสองสำนวน — "เรียนไป
# แล้วกี่วิชา" กับ "เรียนไปได้เท่าไหร่แล้ว" เดิมจับแค่สำนวนแรก อีกสำนวน
# ตกไป fallback (เจอจาก chat_logs ของการทดสอบจริง 23 ส.ค. 2026)
# ไม่ต้องกลัวชนคำถามเรื่องเกรด ("เกรดเท่าไหร่") เพราะ router เช็ค
# GPA_PATTERN ก่อน PROGRESS_PATTERN อยู่แล้ว
PROGRESS_PATTERN = re.compile(
    r"ความก้าวหน้า"
    r"|เรียนไป(?:ได้)?(?:แล้ว)?(?:กี่|เท่าไหร่|เท่าไร)"
    r"|ผ่านไป(?:ได้)?(?:แล้ว)?(?:กี่|เท่าไหร่|เท่าไร)"
    r"|เหลืออีก(?:กี่|เท่าไหร่|เท่าไร)|เหลือกี่วิชา"
    r"|หน่วยกิตที่เหลือ|ครบหลักสูตร|ใกล้จบ|จบได้ไหม|จบทันไหม|เหลือวิชาอะไร"
)

NEXT_TERM_PATTERN = re.compile(
    r"เทอมหน้า|เทอมถัดไป|ภาคหน้า|ลงอะไรดี|ลงวิชาอะไรดี|ลงทะเบียนอะไรดี|เรียนอะไรต่อ"
)

# "ลงวิชา 7071201 ได้เลยไหม" — มีรหัสวิชาอยู่ในข้อความ จึงต้องแยกจาก
# PROGRESS_PATTERN ไม่ให้ไปชนทางตอบรายละเอียดวิชาตามปกติ
ELIGIBILITY_PATTERN = re.compile(
    r"ลงได้|ได้เลยไหม|ได้ไหม|ได้หรือยัง|บังคับก่อน|ต้องผ่านวิชา|prereq"
)


# ── ตัวช่วยประกอบข้อความ ─────────────────────────────────────────────────────


def _menu(*extra: dict) -> dict:
    """ปุ่มพิเศษ + เมนูหลัก — ใช้ตัวเดียวกับ router เพื่อไม่ให้เมนูสองชุดเพี้ยนกัน"""
    return msg.quick_reply([*extra, *msg.MAIN_MENU_ACTIONS])


def liff_button(settings: Any | None, label: str = "ติ๊กวิชาที่ผ่านแล้ว") -> list[dict]:
    """
    ปุ่มเปิดหน้า LIFF — คืนลิสต์ว่างถ้ายังไม่ได้ตั้ง ``LIFF_ID``

    ปุ่มที่กดแล้วไปหน้าเปล่าแย่กว่าไม่มีปุ่ม จึงไม่ส่งปุ่มตายออกไปเลย
    """
    url = getattr(settings, "liff_url", "") if settings is not None else ""
    return [msg.uri_action(label, url)] if url else []


def prereq_caveat(progress: planner.Progress) -> str:
    """
    บอกตรง ๆ ว่าลำดับที่แสดงอ้างอิงอะไร

    ตาราง ``prerequisites`` ยังว่าง (ระบบทะเบียนไม่เผยแพร่ ต้องกรอกจาก มคอ.2)
    ถ้าไม่บอก นักศึกษาจะเข้าใจว่านี่คือเงื่อนไขวิชาบังคับก่อนจริง แล้วไปลง
    วิชาที่ลงไม่ได้ — คำเตือนหนึ่งบรรทัดถูกกว่าการเสียเวลาไปหนึ่งเทอม
    """
    if progress.prereq_known:
        return ""
    return (
        "หมายเหตุ: ลำดับที่แสดงคือ “เทอมที่แผนการเรียนแนะนำ” "
        "ยังไม่ใช่เงื่อนไขวิชาบังคับก่อน (ระบบทะเบียนไม่เผยแพร่ข้อมูลนี้) "
        "ก่อนลงจริงเช็คกับอาจารย์ที่ปรึกษาอีกครั้งครับ"
    )


def course_line(status: planner.CourseStatus, *, with_term: bool = True) -> str:
    """
    หนึ่งบรรทัดของรายวิชา

    >>> c = planner.PlannedCourse('7071201', 2, 1, name='ระบบฐานข้อมูลเบื้องต้น', credits=3)
    >>> course_line(planner.CourseStatus(course=c))
    '  • [ปี 2 เทอม 1] 7071201 ระบบฐานข้อมูลเบื้องต้น 3 นก.'
    >>> course_line(planner.CourseStatus(course=c), with_term=False)
    '  • 7071201 ระบบฐานข้อมูลเบื้องต้น 3 นก.'
    """
    course = status.course
    name = msg.truncate(course.name or "(ยังไม่มีชื่อวิชาในคลังข้อมูล)", 60)
    credits = f" {course.credits} นก." if course.credits else ""
    term = f"[{course.term_label}] " if with_term else ""
    blocked = ""
    if status.blockers:
        codes = ", ".join(req.requires_code for req in status.blockers)
        blocked = f"\n     ต้องผ่าน {codes} ก่อน"
    return f"  • {term}{course.course_code} {name}{credits}{blocked}"


def course_row_data(status: planner.CourseStatus, *, with_term: bool = True) -> dict:
    """
    รายวิชาหนึ่งแถวสำหรับ Flex — ฝาแฝดของ :func:`course_line` ฝั่งการ์ด

    ต้องให้ข้อมูลเท่ากับแบบข้อความทุกช่อง (รหัส/ชื่อ/หน่วยกิต/เทอมที่แผนแนะนำ/
    วิชาที่ต้องผ่านก่อน) ไม่ใช่ตัดทิ้งเพราะการ์ดแคบ

    ``action`` ทำให้แตะแถวแล้วได้รายละเอียดวิชานั้นเลย — เส้นทางเดียวกับที่
    ผู้ใช้พิมพ์รหัส 7 หลักมาเอง (``action=course&code=...`` ใน router)

    >>> c = planner.PlannedCourse('7071201', 2, 1, name='ระบบฐานข้อมูลเบื้องต้น', credits=3)
    >>> row = course_row_data(planner.CourseStatus(course=c))
    >>> row['code'], row['credits'], row['term']
    ('7071201', 3, 'ปี 2 เทอม 1')
    >>> row['action']['data']
    'action=course&code=7071201'
    """
    course = status.course
    row: dict = {
        "code": course.course_code,
        "name": msg.truncate(course.name or "(ยังไม่มีชื่อวิชาในคลังข้อมูล)", 60),
        "credits": course.credits or 0,
        "term": course.term_label if with_term else "",
        "action": msg.postback_action(
            course.course_code, f"action=course&code={course.course_code}"
        ),
    }
    if status.blockers:
        codes = ", ".join(req.requires_code for req in status.blockers)
        row["note"] = f"ต้องผ่าน {codes} ก่อน"
    return row


# ── โหลดข้อมูลที่ planner ต้องใช้ ─────────────────────────────────────────────


def need_completed_courses(
    settings: Any | None, topic: str = "ความก้าวหน้า"
) -> RouteResult:
    """
    ยังไม่รู้ว่าผ่านวิชาอะไร → คำนวณไม่ได้ ต้องบอกวิธีให้ข้อมูล

    **ไม่เดาจากชั้นปี** โดยเจตนา: ชั้นปีบอกว่าเข้ามากี่ปี ไม่ได้บอกว่าผ่านอะไร
    (ติด F / ถอน / เทียบโอน ทำให้ต่างกันมาก) เดาแล้วผิดทั้งคำตอบ และผิดแบบ
    ที่ผู้ใช้จับไม่ได้ เพราะหน้าตาคำตอบเหมือนของจริงเป๊ะ
    """
    buttons = liff_button(settings)
    extra = "\n\nกดปุ่มด้านล่างเพื่อติ๊กวิชาที่ผ่านแล้วครับ" if buttons else ""
    return RouteResult(
        messages=[
            msg.text_message(
                f"ยังคำนวณ{topic}ให้ไม่ได้ครับ เพราะระบบยังไม่รู้ว่าผ่านวิชาอะไรมาแล้ว\n\n"
                "ระบบไม่ได้ต่อกับระบบทะเบียน (ไม่ขอรหัสผ่านของนักศึกษา) "
                "จึงต้องติ๊กวิชาที่ผ่านเองครั้งเดียว หลังจากนั้นถามได้เลยครับ"
                + extra,
                _menu(*buttons),
            )
        ],
        answered_by="no_data",
        intent_key="progress_no_profile",
    )


async def load_progress(
    db: SupportsQuery, user_hash: str
) -> tuple[planner.Progress, dict] | None:
    """
    ดึงทุกอย่างที่ planner ต้องใช้ — คืน ``None`` เมื่อยังคำนวณไม่ได้

    จำนวนคิวรีคงที่ (5 ครั้ง) ไม่ขึ้นกับจำนวนวิชา — ไม่มี N+1
    """
    profile = await repo.user_profile(db, user_hash)
    if not profile or not profile.get("completed_courses"):
        return None

    program_code = profile.get("program_code") or _default_program_code()
    plan_rows = await repo.curriculum_plan(db, program_code)
    if not plan_rows:
        log.info("ไม่มีแผนการเรียนของหลักสูตร %s ในคลังข้อมูล", program_code)
        return None

    prereq_rows = await repo.prerequisites_for_program(db, program_code)
    done = await repo.completed_courses(db, int(profile["id"]))
    program = await repo.program_info(db, program_code)

    progress = planner.evaluate(
        program_code,
        plan_rows,
        [row["course_code"] for row in done],
        prereq_rows=prereq_rows,
        total_credits_required=(program or {}).get("total_credits"),
    )
    return progress, profile


def _default_program_code() -> str:
    """import ในฟังก์ชัน เพื่อไม่ผูกโมดูลนี้กับการโหลด ``.env`` ตอน import"""
    from .config import get_settings

    return get_settings().default_program_code


# ── คำตอบ 1: ภาพรวมความก้าวหน้า ──────────────────────────────────────────────


async def progress_answer(
    db: SupportsQuery | None, user_hash: str | None, settings: Any | None
) -> RouteResult:
    """ผ่านแล้วเท่าไร เหลืออะไร — คำถามหลักของ Requirement 4.1 หมวด 3"""
    if db is None:
        from .router import _no_data

        return _no_data("ความก้าวหน้าตามหลักสูตร", "progress")
    if not user_hash:
        from .router import _fallback

        return _fallback("progress")

    loaded = await load_progress(db, user_hash)
    if loaded is None:
        return need_completed_courses(settings)
    progress, _ = loaded

    # ตัวเลขทั้งชุดไปอยู่บนการ์ด (แถบ % + รายการวิชาที่เหลือ) — ค่าที่เคยอยู่ใน
    # header ข้อความเดิมต้องไปครบทุกตัว ไม่ใช่เหลือแค่ที่การ์ดใส่สวย
    stats: list[str] = []
    if progress.total_credits_required:
        stats.append(
            f"หลักสูตรกำหนด {progress.total_credits_required} หน่วยกิต"
            f" → ยังต้องเก็บอีกไม่เกิน {progress.credits_left_to_graduate} หน่วยกิต"
        )
    if progress.passed_outside_plan:
        stats.append(f"มีวิชานอกแผนที่ติ๊กไว้ {len(progress.passed_outside_plan)} วิชา")

    notes = [prereq_caveat(progress)]
    if not progress.remaining:
        notes = ["เก็บครบทุกวิชาในแผนแล้วครับ 🎉 เหลือตรวจสอบจบกับสำนักส่งเสริมวิชาการฯ"]

    buttons = [
        msg.postback_action("เทอมหน้าลงอะไรดี", "action=progress&next=1"),
        *liff_button(settings, "แก้วิชาที่ผ่าน"),
    ]
    return RouteResult(
        messages=[
            flex.progress_flex_message(
                program_code=progress.program_code,
                percent=progress.percent_complete,
                passed_courses=len(progress.passed_statuses),
                plan_courses=progress.plan_courses,
                passed_credits=progress.passed_credits,
                remaining_headline=(
                    f"เหลือในแผน {len(progress.remaining)} วิชา"
                    f" {progress.remaining_plan_credits} หน่วยกิต"
                ),
                stats=stats,
                course_rows=[course_row_data(s) for s in progress.remaining],
                notes=notes,
                quick_reply=_menu(*buttons),
            )
        ],
        answered_by=PLANNER_ANSWER,
        intent_key="progress",
        confidence=1.0,
    )


# ── คำตอบ 2: เทอมถัดไปลงอะไรดี ───────────────────────────────────────────────


def next_semester(latest_term: dict | None) -> int:
    """
    เทอมถัดไปคือภาคเรียนที่เท่าไร — อ้างจาก **เทอมล่าสุดที่มีตารางสอนในคลัง**

    ไม่ใช้นาฬิกาเครื่อง เพราะคลังข้อมูลอาจตามหลังปีปัจจุบัน แล้วจะไปเสนอ
    เทอมที่ไม่มีข้อมูลการเปิดสอนเลย (คำตอบดูมั่นใจแต่ว่างเปล่า)

    >>> next_semester({'acad_year': 2568, 'semester': 1})
    2
    >>> next_semester({'acad_year': 2568, 'semester': 2})
    1
    >>> next_semester({'acad_year': 2568, 'semester': 3})
    1
    >>> next_semester(None)
    1
    """
    if not latest_term:
        return 1
    return 2 if int(latest_term.get("semester") or 0) == 1 else 1


async def next_term_answer(
    db: SupportsQuery | None, user_hash: str | None, settings: Any | None
) -> RouteResult:
    """ตะกร้าวิชาที่เสนอให้ลงเทอมถัดไป (คำนวณ ไม่ใช่ให้ LLM เดา)"""
    if db is None:
        from .router import _no_data

        return _no_data("แผนเทอมถัดไป", "next_term")
    if not user_hash:
        from .router import _fallback

        return _fallback("next_term")

    loaded = await load_progress(db, user_hash)
    if loaded is None:
        return need_completed_courses(settings)
    progress, profile = loaded

    semester = next_semester(await repo.latest_term(db))
    max_credits = int(
        getattr(settings, "planner_max_credits", planner.DEFAULT_MAX_CREDITS_PER_TERM)
        or planner.DEFAULT_MAX_CREDITS_PER_TERM
    )
    study_year = profile.get("study_year")
    suggestion = planner.suggest_term(
        progress,
        semester,
        max_credits=max_credits,
        up_to_term=(int(study_year), semester) if study_year else None,
    )

    if not suggestion.picks:
        return _nothing_to_take(progress, suggestion, semester, settings)

    # หมายเหตุทุกบรรทัดต้องยังอยู่ — วิชาที่ค้าง/ไม่เปิด/เกินเพดาน คือเหตุผลว่า
    # ทำไมตะกร้าถึงหน้าตาแบบนี้ ตัดออกแล้วนักศึกษาจะคิดว่าระบบลืมวิชาไป
    notes: list[str] = []
    if suggestion.overdue:
        codes = ", ".join(s.course.course_code for s in suggestion.overdue)
        notes.append(f"ค้างจากเทอมก่อนตามแผน (ควรเก็บให้ทัน): {codes}")
    if suggestion.not_offered:
        codes = ", ".join(s.course.course_code for s in suggestion.not_offered)
        notes.append(f"ภาคเรียนนี้ไม่เปิด ต้องรอเทอมถัดไป: {codes}")
    if suggestion.deferred:
        notes.append(f"เกินเพดานหน่วยกิต เลื่อนไปเทอมหลัง {len(suggestion.deferred)} วิชา")
    if suggestion.block_only:
        notes.append("วิชานี้เป็นการฝึกประสบการณ์เต็มเวลา ลงร่วมกับวิชาอื่นไม่ได้")
    if suggestion.unknown_offering:
        codes = ", ".join(suggestion.unknown_offering)
        notes.append(f"ไม่มีข้อมูลว่าเปิดภาคเรียนไหน ต้องเช็คเอง: {codes}")
    notes.append(prereq_caveat(progress))

    return RouteResult(
        messages=[
            flex.next_term_flex_message(
                semester=semester,
                course_count=len(suggestion.picks),
                credits=suggestion.credits,
                max_credits=max_credits,
                course_rows=[course_row_data(s) for s in suggestion.picks],
                notes=notes,
                # ปุ่ม "ความก้าวหน้า" อยู่ใน MAIN_MENU_ACTIONS แล้ว ไม่ใส่ซ้ำ
                quick_reply=_menu(*liff_button(settings, "แก้วิชาที่ผ่าน")),
            )
        ],
        answered_by=PLANNER_ANSWER,
        intent_key="next_term",
        confidence=1.0,
    )


def _nothing_to_take(
    progress: planner.Progress,
    suggestion: planner.TermSuggestion,
    semester: int,
    settings: Any | None,
) -> RouteResult:
    """เสนอไม่ได้เลย — ต้องบอกว่าเพราะอะไร ไม่ใช่ตอบว่า "ไม่มีข้อมูล" ลอย ๆ"""
    lines = []
    if progress.remaining:
        lines.append(f"  • ติดวิชาบังคับก่อน {len(suggestion.blocked)} วิชา")
        lines.append(f"  • ภาคเรียนนี้ไม่เปิดสอน {len(suggestion.not_offered)} วิชา")
    header = (
        "เก็บครบทุกวิชาในแผนแล้วครับ 🎉"
        if not progress.remaining
        else f"ยังเสนอวิชาสำหรับภาคเรียนที่ {semester} ให้ไม่ได้ครับ"
    )
    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(
                    header,
                    lines,
                    prereq_caveat(progress) or "รบกวนปรึกษาอาจารย์ที่ปรึกษาครับ",
                ),
                _menu(*liff_button(settings, "แก้วิชาที่ผ่าน")),
            )
        ],
        answered_by=PLANNER_ANSWER,
        intent_key="next_term",
        confidence=1.0,
    )


# ── คำตอบ 3: ลงวิชานี้ได้เลยไหม ───────────────────────────────────────────────


async def eligibility_answer(
    db: SupportsQuery | None,
    user_hash: str | None,
    settings: Any | None,
    course_code: str,
) -> RouteResult | None:
    """
    "ลงวิชา 7071201 ได้เลยไหม" — ตอบจากสถานะจริงของผู้ใช้

    คืน ``None`` เมื่อตอบแบบนี้ไม่ได้ (ไม่มี DB / ยังไม่ติ๊กวิชา / วิชาไม่อยู่ใน
    แผนหลักสูตรนี้) เพื่อให้ router ถอยไปตอบรายละเอียดวิชาแบบเดิม —
    ดีกว่าตอบว่าไม่รู้ทั้งที่มีข้อมูลรายวิชาอยู่ในมือ
    """
    if db is None or not user_hash:
        return None

    loaded = await load_progress(db, user_hash)
    if loaded is None:
        return None
    progress, _ = loaded

    status = planner.find_status(progress, course_code)
    if status is None:
        return None

    course = status.course
    name = course.name or ""
    if status.passed:
        verdict = f"ผ่านวิชานี้แล้วครับ — {course_code} {name}".rstrip()
        lines = ["  • ไม่ต้องลงซ้ำ (ถ้าติ๊กผิด แก้ได้จากปุ่มด้านล่าง)"]
    elif status.blockers:
        verdict = f"ยังลงไม่ได้ครับ — {course_code} {name}".rstrip()
        lines = [
            f"  • ต้องผ่าน {req.requires_code} {req.name or ''}".rstrip()
            for req in status.blockers
        ]
    else:
        opens = ", ".join(str(sem) for sem in sorted(course.opens))
        verdict = f"ลงได้ครับ — {course_code} {name}".rstrip()
        lines = [
            f"  • แผนการเรียนวางไว้ {course.term_label}",
            f"  • เปิดสอนภาคเรียน: {opens or 'ไม่มีข้อมูลในคลัง'}",
        ]
        if status.co_requisites:
            codes = ", ".join(req.requires_code for req in status.co_requisites)
            lines.append(f"  • ลงพร้อมกันได้กับ {codes}")
        if status.advisories:
            codes = ", ".join(req.requires_code for req in status.advisories)
            lines.append(f"  • แนะนำให้ผ่าน {codes} ก่อน (ไม่บังคับ)")

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(verdict, lines, prereq_caveat(progress)),
                _menu(
                    msg.postback_action("เทอมหน้าลงอะไรดี", "action=progress&next=1"),
                    *liff_button(settings, "แก้วิชาที่ผ่าน"),
                ),
            )
        ],
        answered_by=PLANNER_ANSWER,
        intent_key="eligibility",
        confidence=1.0,
    )


# ── คำตอบ 4: ให้คำปรึกษาด้านผลการเรียน (Requirement ข้อ 4.4) ─────────────────
#
# ต่อกับตัวเลขของ planner โดยตรง — นั่นคือทั้งหมดที่ทำให้คำตอบนี้ต่างจาก
# เว็บคิดเกรดทั่วไป: ผู้ใช้บอก GPAX มาตัวเดียว ส่วน "เหลืออีกกี่หน่วยกิต"
# ระบบรู้อยู่แล้วจากวิชาที่ติ๊กไว้ ไม่ต้องกรอกรายวิชาทีละช่อง

GPA_PATTERN = re.compile(r"gpax?|เกรดเฉลี่ย|เกียรตินิยม|เกรด")

# กันชนคำขอ "เอกสาร" ที่ดันมีคำว่าเกรดอยู่ด้วย
#
# "ขอใบเกรด" / "ขอใบรายงานผลการเรียน" คือคำขอเอกสาร ต้องไปทางหมวดเอกสาร
# ถ้าไม่กัน ชั้นนี้จะดูดไปคำนวณเกรดให้ ซึ่งไม่ใช่คำตอบที่ถามเลย
GPA_NOT_PATTERN = re.compile(
    r"ใบเกรด|ใบรายงานผล|ใบแสดงผล|ใบ รบ|ทรานสคริป|transcript|ขอเอกสาร|ยื่นคำร้อง"
)

# เครื่องคิดเกรดแบบใส่รายวิชาเอง — แนบไว้เป็นทางเลือกสำหรับคนที่อยากกรอก
# ทีละวิชา (ซึ่งโมเดลของเราไม่รับ เพราะไม่เก็บเกรดรายวิชา)
GPA_CALCULATOR_URL = "https://www.stepupth.com/gpa"


def grade_scale_note() -> str:
    """
    บอกสเกลที่ใช้คิด เพราะ **ยังไม่ได้ยืนยันกับเล่มข้อบังคับ RMU**

    ถ้าสเกลจริงต่างจากนี้ ตัวเลขทุกตัวในคำตอบเปลี่ยนหมด ผู้ใช้จึงต้องเห็นว่า
    ระบบคิดด้วยอะไร ไม่ใช่เชื่อตัวเลขลอย ๆ
    """
    scale = " / ".join(
        f"{grade} {point:.2f}" for grade, point in gpa.GRADE_POINTS.items()
    )
    return f"คิดด้วยสเกล {scale}"


def credits_note(overridden: bool) -> str:
    """
    เตือนว่าหน่วยกิตที่ใช้คิดอาจไม่ตรง และบอกวิธีแก้ในประโยคเดียวกัน

    เตือนโดยไม่ให้ทางแก้ = เตือนเปล่า ๆ จึงบอกรูปประโยคที่พิมพ์กลับมาได้เลย
    """
    if overridden:
        return "ใช้จำนวนหน่วยกิตที่คุณบอกมาคิดครับ"
    return (
        "หน่วยกิตที่คิดเกรดใช้จากวิชาที่ติ๊กไว้ — ถ้ามีวิชาติด F / เทียบโอน / "
        "ตัดสินผลเป็น S-U จะไม่ตรง พิมพ์ว่า “เก็บไปแล้ว 72 หน่วยกิต” เพื่อแก้ได้ครับ"
    )


def _target_line(plan: gpa.TargetPlan) -> str:
    """หนึ่งบรรทัดสรุปเป้าหนึ่งเป้า — สี่สถานะที่ต้องไม่พูดปนกัน"""
    head = plan.label or f"เป้า GPAX {plan.target:.2f}"
    if plan.remaining_credits == 0:
        verdict = "ถึงแล้วครับ" if plan.achievable else "ไม่ถึงแล้วครับ"
        return f"• {head}: เก็บครบหลักสูตรแล้ว แก้ไม่ได้อีก — {verdict}"
    if plan.guaranteed:
        return f"• {head}: ถึงแน่นอนแล้ว แม้ได้ F ทุกวิชาที่เหลือก็ไม่หลุด"
    if not plan.achievable:
        return (
            f"• {head}: ไปไม่ถึงแล้วครับ — ได้ A ทุกวิชาที่เหลือ "
            f"GPAX สูงสุดคือ {plan.best_possible:.2f}"
        )
    return (
        f"• {head}: ต้องได้เฉลี่ย {plan.required:.2f} ในอีก "
        f"{plan.remaining_credits} หน่วยกิต (ประมาณ {plan.grade} ทุกวิชา)"
    )


def _scenario_lines(rows: tuple[gpa.Scenario, ...]) -> list[str]:
    lines = []
    for row in rows:
        honors = f" — เกียรตินิยม{row.honors}" if row.honors else ""
        lines.append(f"• ได้ {row.grade} ทุกวิชา → GPAX {row.final_gpax:.2f}{honors}")
    return lines


def ask_for_gpax(settings: Any | None, remaining_credits: int) -> RouteResult:
    """
    ขอเลขตัวเดียวที่ระบบไม่มีทางรู้เอง

    ที่ต้องขอมีแค่ GPAX เพราะ "เหลืออีกกี่หน่วยกิต" planner รู้แล้วจากวิชาที่
    ติ๊กไว้ — จุดนี้คือความต่างจากเว็บคิดเกรดทั่วไปที่ต้องกรอกทุกช่องเอง
    """
    buttons = [
        *liff_button(settings, "แก้วิชาที่ผ่าน"),
        msg.uri_action("เครื่องคิดเกรดรายวิชา", GPA_CALCULATOR_URL),
    ]
    return RouteResult(
        messages=[
            msg.text_message(
                "บอก GPAX ตอนนี้มาได้เลยครับ แล้วผมคำนวณให้ว่าต้องได้เกรดเท่าไร\n\n"
                "พิมพ์แบบนี้ได้เลย:\n"
                "• “เกรดตอนนี้ 2.75 อยากได้ 3.00”\n"
                "• “GPA 3.4 ยังลุ้นเกียรตินิยมได้ไหม”\n\n"
                f"ระบบรู้อยู่แล้วว่าคุณเหลืออีก {remaining_credits} หน่วยกิต "
                "จึงไม่ต้องกรอกรายวิชาเองครับ\n"
                "(ระบบไม่เก็บเกรดที่พิมพ์มา — ใช้คำนวณแล้วทิ้งทันที)",
                _menu(*buttons),
            )
        ],
        answered_by=PLANNER_ANSWER,
        intent_key="gpa_need_gpax",
        confidence=1.0,
    )


async def gpa_answer(
    db: SupportsQuery | None,
    user_hash: str | None,
    settings: Any | None,
    text: str,
) -> RouteResult:
    """
    ให้คำปรึกษาด้านผลการเรียน (Requirement ข้อ 4.4)

    ใช้ตัวเลขจาก planner (หน่วยกิตที่เหลือ/ที่ผ่าน) + GPAX ที่ผู้ใช้พิมพ์บอก
    **GPAX ไม่ถูกเขียนลงตารางใด ๆ** ใช้คำนวณในรอบนี้แล้วทิ้ง — คำเคลมใน
    ``db/migrations/001_init.sql`` และบทที่ 3 ว่า "ไม่เก็บเกรด" จึงยังเป็นจริง
    """
    if db is None:
        from .router import _no_data

        return _no_data("การคำนวณเกรด", "gpa")
    if not user_hash:
        from .router import _fallback

        return _fallback("gpa")

    question = gpa.parse_question(text)
    loaded = await load_progress(db, user_hash)
    if loaded is None:
        return need_completed_courses(settings, "เกรด")
    progress, _ = loaded

    remaining = progress.credits_left_to_graduate
    if remaining is None:
        # ไม่รู้เกณฑ์จบของหลักสูตร → ใช้หน่วยกิตที่เหลือในแผนแทน (ต่ำกว่าความจริง)
        remaining = progress.remaining_plan_credits
    # ``or`` ทำให้ 0 ถูกมองว่า "ไม่ได้บอกมา" ซึ่งถูกต้องในที่นี้: หน่วยกิตที่
    # คิดเกรดแล้วเป็น 0 แปลว่าไม่มีอะไรให้ถ่วง ไม่ใช่ค่าที่ผู้ใช้ตั้งใจส่ง
    credits_counted = question.credits_counted or progress.passed_credits

    if question.gpax is None:
        return ask_for_gpax(settings, remaining)

    current = question.gpax
    blocks: list[str] = []
    intent = "gpa_scenarios"

    if question.target is not None:
        intent = "gpa_target"
        blocks.append(
            _target_line(
                gpa.plan_target(current, credits_counted, remaining, question.target)
            )
        )

    if question.wants_honors:
        intent = "gpa_honors"
        if blocks:
            blocks.append("")
        blocks.append("ลุ้นเกียรตินิยม (คิดเฉพาะเกณฑ์ GPAX):")
        blocks.extend(
            _target_line(plan)
            for plan in gpa.honors_outlook(current, credits_counted, remaining)
        )
        blocks.append(
            "เกณฑ์จริงมีเงื่อนไขอื่นที่ระบบยังไม่รู้ (เช่น ต้องไม่เคยได้ F "
            "และจบในเวลาปกติ) — เช็คกับสำนักส่งเสริมวิชาการฯ ด้วยครับ"
        )

    rows = gpa.scenarios(current, credits_counted, remaining)
    if blocks:
        blocks.append("")
    if rows:
        blocks.append("ถ้าเกรดที่เหลือออกมาเท่ากันหมด:")
        blocks.extend(_scenario_lines(rows))
    else:
        rank = gpa.honors_rank(current)
        blocks.append(
            f"เก็บครบหลักสูตรแล้ว GPAX {current:.2f} คือผลสุดท้าย"
            + (f" (ถึงเกณฑ์เกียรตินิยม{rank})" if rank else "")
        )

    header = (
        f"คำปรึกษาด้านผลการเรียน\n"
        f"คิดจาก GPAX {current:.2f} · คิดเกรดแล้ว {credits_counted} หน่วยกิต"
        f" · เหลืออีก {remaining} หน่วยกิต"
    )
    footer = "\n".join(
        [
            credits_note(question.credits_counted is not None),
            grade_scale_note() + " (ยังไม่ได้ยืนยันกับข้อบังคับ RMU)",
            "ระบบไม่เก็บเกรดที่พิมพ์มา — ใช้คำนวณแล้วทิ้งทันที",
        ]
    )
    buttons = [
        *liff_button(settings, "แก้วิชาที่ผ่าน"),
        msg.uri_action("เครื่องคิดเกรดรายวิชา", GPA_CALCULATOR_URL),
    ]
    return RouteResult(
        messages=[
            msg.text_message(join_lines(header, blocks, footer), _menu(*buttons))
        ],
        answered_by=PLANNER_ANSWER,
        intent_key=intent,
        confidence=1.0,
    )
