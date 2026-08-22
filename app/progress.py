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

from . import planner
from . import repository as repo
from .db import SupportsQuery
from .line import messages as msg
from .router import RouteResult, join_lines

log = logging.getLogger("app.progress")

# ป้ายใน chat_logs — ประกาศไว้ใน db/migrations/005_planner.sql แล้ว
PLANNER_ANSWER = "planner"

# คำถามที่ควรเข้าชั้นนี้ ไม่ใช่ไปค้นเอกสาร
#
# ตั้งใจให้แคบ: จับกว้างไปแล้วคำถามเรื่องเอกสาร ("ขอใบรายงานผลการเรียน")
# จะถูกดูดมาตอบด้วยแผนการเรียน ซึ่งไม่ใช่คำตอบที่ถาม
PROGRESS_PATTERN = re.compile(
    r"ความก้าวหน้า|เรียนไปแล้วกี่|ผ่านไปแล้วกี่|เหลืออีกกี่|เหลือกี่วิชา"
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


# ── โหลดข้อมูลที่ planner ต้องใช้ ─────────────────────────────────────────────


def need_completed_courses(settings: Any | None) -> RouteResult:
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
                "ยังคำนวณความก้าวหน้าให้ไม่ได้ครับ เพราะระบบยังไม่รู้ว่าผ่านวิชาอะไรมาแล้ว\n\n"
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

    header = (
        f"ความก้าวหน้าตามหลักสูตร {progress.program_code}\n"
        f"ผ่านแล้ว {len(progress.passed_statuses)}/{progress.plan_courses} วิชา"
        f" ({progress.percent_complete}%) รวม {progress.passed_credits} หน่วยกิต\n"
        f"เหลือในแผน {len(progress.remaining)} วิชา"
        f" {progress.remaining_plan_credits} หน่วยกิต"
    )
    if progress.total_credits_required:
        header += (
            f"\nหลักสูตรกำหนด {progress.total_credits_required} หน่วยกิต"
            f" → ยังต้องเก็บอีกไม่เกิน {progress.credits_left_to_graduate} หน่วยกิต"
        )
    if progress.passed_outside_plan:
        header += f"\n(มีวิชานอกแผนที่ติ๊กไว้ {len(progress.passed_outside_plan)} วิชา)"

    lines = [course_line(status) for status in progress.remaining]
    footer = prereq_caveat(progress)
    if not lines:
        footer = "เก็บครบทุกวิชาในแผนแล้วครับ 🎉 เหลือตรวจสอบจบกับสำนักส่งเสริมวิชาการฯ"

    buttons = [
        msg.postback_action("เทอมหน้าลงอะไรดี", "action=progress&next=1"),
        *liff_button(settings, "แก้วิชาที่ผ่าน"),
    ]
    return RouteResult(
        messages=[msg.text_message(join_lines(header, lines, footer), _menu(*buttons))],
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

    header = (
        f"วิชาที่แนะนำให้ลงภาคเรียนที่ {semester}\n"
        f"{len(suggestion.picks)} วิชา {suggestion.credits} หน่วยกิต"
        f" (เพดานที่ใช้คิด {max_credits} หน่วยกิต)"
    )
    lines = [course_line(status) for status in suggestion.picks]
    if suggestion.overdue:
        codes = ", ".join(s.course.course_code for s in suggestion.overdue)
        lines.append(f"\nค้างจากเทอมก่อนตามแผน (ควรเก็บให้ทัน): {codes}")
    if suggestion.not_offered:
        codes = ", ".join(s.course.course_code for s in suggestion.not_offered)
        lines.append(f"ภาคเรียนนี้ไม่เปิด ต้องรอเทอมถัดไป: {codes}")
    if suggestion.deferred:
        lines.append(f"เกินเพดานหน่วยกิต เลื่อนไปเทอมหลัง {len(suggestion.deferred)} วิชา")
    if suggestion.block_only:
        lines.append("วิชานี้เป็นการฝึกประสบการณ์เต็มเวลา ลงร่วมกับวิชาอื่นไม่ได้")
    if suggestion.unknown_offering:
        codes = ", ".join(suggestion.unknown_offering)
        lines.append(f"ไม่มีข้อมูลว่าเปิดภาคเรียนไหน ต้องเช็คเอง: {codes}")

    return RouteResult(
        messages=[
            msg.text_message(
                join_lines(header, lines, prereq_caveat(progress)),
                # ปุ่ม "ความก้าวหน้า" อยู่ใน MAIN_MENU_ACTIONS แล้ว ไม่ใส่ซ้ำ
                _menu(*liff_button(settings, "แก้วิชาที่ผ่าน")),
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
