"""
ชั้นที่ 3: AI Chat — เชื่อม ``LlmClient`` เข้าบทสนทนาจริง (Requirement ข้อ 9)

**ช่องว่างที่ไฟล์นี้ปิด**: ก่อนหน้านี้ ``app/llm.py`` ไม่มีใครเรียกนอกจากเทส
(ยืนยันด้วย grep ทั้งทรี) ทั้งที่ชื่อโครงงานคือ "**AI** Academic Assistant"

**ขอบเขตของชั้นนี้** (ซื่อสัตย์กับข้อมูลที่มี):

* ตอบคำถามทั่วไปด้านการเรียน/ชีวิตมหาวิทยาลัย เช่น "เพิ่งเข้ามหาลัยควร
  ปรับตัวยังไง" "อ่านหนังสือก่อนสอบยังไง" — ไม่ได้บล็อกที่ข้อมูลทางการ
* **ไม่ตอบ**เรื่องกฎระเบียบ/กำหนดการ/ตัวเลข — ไม่มี ``rag_chunks``/``faqs``
  ให้ retrieve (ตารางยังว่าง บล็อกที่เนื้อหาทางการ) LLM จึงไม่มีแหล่งอ้างอิง
  ซึ่ง Requirement ข้อ 11 บอกชัดว่าห้ามเดา → system prompt บังคับให้บอกว่า
  ไม่มีข้อมูลแทน

**บริบทบทสนทนาแยกตามผู้ใช้**: ประวัติไม่ได้เก็บใน memory ของ process
แต่ดึงจาก ``chat_logs`` โดยกรอง ``user_id`` (ผูกกับ ``line_user_hash``)
→ ผู้ใช้แต่ละคนเห็นแต่บทสนทนาของตัวเอง และบอท restart ก็ไม่ลืม
เพราะบทสนทนาอยู่ใน DB ไม่ใช่ในตัว process

**กัน context บวม**: ดึงไม่กี่รอบล่าสุด + เพดานตัวอักษรรวม
(``ai_chat_history_turns`` / ``ai_chat_max_history_chars``) ข้อความยาวพิเศษ
รอบเดียวจึงไม่ทำให้ prompt พองจนค่า token บานหรือคำตอบช้า

**ทุกความล้มเหลวถอยกลับเป็น fallback** — LLM timeout/429/ตอบว่าง ต้องไม่ทำ
ให้บทสนทนาเงียบหาย นักศึกษาควรได้คำตอบว่าระบบขัดข้อง ไม่ใช่การรอเก้อ
"""

from __future__ import annotations

import logging

from . import repository as repo
from .config import Settings
from .db import SupportsQuery
from .line import messages as msg
from .llm import ChatResult, LlmClient, LlmError
from .router import RouteResult

log = logging.getLogger("app.ai_chat")

# ข้อความถาม/ตอบหนึ่งข้างยาวเกินนี้ในประวัติ = ตัดก่อนส่งเข้า LLM
# กันข้อความพิเศษ (เช่น copy ยาว ๆ มาวาง) กินงบบริบททั้งก้อน
HISTORY_ENTRY_LIMIT = 1_000

# system prompt — เขียนเป็นกฎที่ "ห้าม" ชัด เพราะผลของการเดาข้อมูลราชการ
# คือนักศึกษาเสียหายจริง (Requirement ข้อ 11 และ 14)
SYSTEM_PROMPT = """\
คุณเป็นผู้ช่วยให้คำปรึกษาด้านการเรียนและชีวิตมหาวิทยาลัย \
ของนักศึกษามหาวิทยาลัยราชภัฏมหาสารคาม ตอบเป็นภาษาไทย สุภาพ ลงท้ายครับ

คุณให้คำแนะนำทั่วไปได้ เช่น การปรับตัวในมหาวิทยาลัย การจัดการเวลา \
เทคนิคการอ่านหนังสือ/จดสรุป การเตรียมสอบ การจัดลำดับความสำคัญ

กฎที่ต้องทำตามเสมอ:
1. ห้ามแต่งข้อมูลทางการของมหาวิทยาลัย: วัน-กำหนดการ ระเบียบ ข้อบังคับ \
ค่าธรรมเนียม ขั้นตอนเอกสาร ชื่อเจ้าหน้าที่ ถ้าไม่แน่ใจให้ตอบว่าไม่มีข้อมูล \
และแนะนำให้ถามเจ้าหน้าที่หรือใช้ปุ่มเมนูของบอท
2. ห้ามขอข้อมูลส่วนตัว เช่น รหัสนักศึกษา เลขบัตรประชาชน รหัสผ่าน
3. ถ้าคำถามไม่เกี่ยวกับการเรียนหรือชีวิตนักศึกษา ให้ปฏิเสธอย่างสุภาพ
4. ตอบกระชับ ไม่เกินราว 250 คำ ใช้หัวข้อสั้น ๆ เมื่อช่วยให้อ่านง่ายขึ้น
5. ห้ามใช้ markdown ที่แชท LINE แสดงไม่ได้ เช่น ## ตัวหนา ** หรือตาราง

บริบท: นักศึกษาพิมพ์มาจากแอป LINE ข้อความตอบของคุณจะแสดงเป็นฟองแชทตรง ๆ\
"""


def build_history_messages(rows: list[dict], max_chars: int) -> list[dict]:
    """
    แปลงแถว ``chat_logs`` เป็น message list สำหรับ LLM (เก่า → ใหม่)

    งบตัวอักษรนับจาก **รอบล่าสุดย้อนหลัง** — ถ้ารอบเก่าที่สุดถูกตัดทิ้ง
    ไม่เสียหายมากเท่าตัดรอบล่าสุด และคู่อื่น ๆ ยังอยู่ครบ

    แต่ละข้อความถูกตัดที่ :data:`HISTORY_ENTRY_LIMIT` ก่อนนับงบ

    ระวัง: ต้อง **กลับลำดับแถวก่อน** แล้วค่อยต่อ user/assistant — ถ้าต่อคู่
    แล้วกลับทั้งก้อน จะได้ ``assistant`` นำหน้า ``user`` ในแต่ละรอบ
    ซึ่งสลับบทบาทผิด
    """
    kept: list[dict] = []
    used = 0

    for row in reversed(rows):  # ใหม่สุดก่อน — ตัดจากรอบเก่าที่สุด
        question = msg.truncate(row.get("message_text") or "", HISTORY_ENTRY_LIMIT)
        answer = msg.truncate(row.get("response_text") or "", HISTORY_ENTRY_LIMIT)
        cost = len(question) + len(answer)
        if used + cost > max_chars and kept:
            break
        kept.append(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ]
        )
        used += cost

    kept.reverse()
    return [message for turn in kept for message in turn]


def build_messages(history: list[dict], question: str) -> list[dict]:
    """system + ประวัติ + คำถามปัจจุบัน — ลำดับที่ chat API ทุกรายการต้องการ"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": question},
    ]


async def answer(
    settings: Settings,
    llm: LlmClient,
    db: SupportsQuery | None,
    user_hash: str | None,
    text: str,
) -> RouteResult | None:
    """
    ตอบคำถามทั่วไปด้วย LLM — คืน ``None`` เมื่อเงื่อนไขไม่ครบ ผู้เรียก
    (router) จะถอยกลับไปตอบ fallback แบบเดิม

    เงื่อนไขที่ต้องครบ **ทั้งหมด**:

    * ``ai_chat_enabled`` ใน settings (สวิตช์ปิดทั้งชั้นได้)
    * ตั้ง ``LLM_API_KEY`` แล้ว
    * มี DB + ``user_hash`` — เพราะบริบทสนทนาแยกตามผู้ใช้ ถ้าแยกไม่ได้
      (เช่นคุยในกลุ่มที่ไม่มี userId) ยอมไม่ตอบ LLM ดีกว่าจำบริบทปนกัน

    โยน :class:`LlmError` ออกมาเมื่อ LLM พังจริง ๆ — ผู้เรียกต้อง catch
    แล้ว fallback (ไม่ให้ ``_guard`` กลืน เพราะนั่นจะตอบว่า "ฐานข้อมูล
    ขัดข้อง" ซึ่งไม่ตรงสาเหตุ)

    ``db`` ใช้แค่ทางอ่าน/``RETURNING`` (``ensure_user`` ใช้ ``fetch_one``,
    ``recent_chat`` ใช้ ``fetch_all``) ไม่ต้องการ ``execute``
    """
    if not settings.ai_chat_enabled:
        return None
    if not settings.llm_api_key:
        log.debug("ข้าม AI Chat — ยังไม่ได้ตั้ง LLM_API_KEY")
        return None
    if db is None or not user_hash:
        log.debug("ข้าม AI Chat — ไม่มี DB หรือ user_hash (แยกบริบทไม่ได้)")
        return None

    # DB error ตรงนี้ให้ _guard ของ router ดักเป็น db_error — ถูกต้องแล้ว
    # เพราะการดึงประวัติ/หาตัวผู้ใช้คือ "ถามฐานข้อมูล" จริง ๆ
    user_id = await repo.ensure_user(db, user_hash)
    history_rows = await repo.recent_chat(
        db, user_id, settings.ai_chat_history_turns
    )
    history = build_history_messages(history_rows, settings.ai_chat_max_history_chars)

    result: ChatResult = await llm.chat(
        build_messages(history, text),
        temperature=settings.llm_temperature,
    )

    if not result.text:
        # โมเดลตอบว่าง (เช่น safety filter) — ให้ผู้เรียก fallback
        raise LlmError(None, "LLM ตอบกลับมาว่างเปล่า")

    log.info(
        "AI Chat ตอบแล้ว: user=%s... model=%s prompt=%s output=%s tokens",
        user_hash[:12],
        result.model,
        result.prompt_tokens,
        result.output_tokens,
    )

    return RouteResult(
        messages=[msg.ai_chat_message(result.text)],
        answered_by="ai_chat",
        intent_key="ai_chat",
        llm_model=result.model,
        prompt_tokens=result.prompt_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        # บอก app.main ว่าตัว user ถูก ensure แล้ว — จะได้ไม่ ensure ซ้ำ
        # ตอนเขียน chat_logs
        user_id=user_id,
    )
