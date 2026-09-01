"""
FastAPI application — LINE webhook + LIFF API

**จุดสำคัญที่สุดของไฟล์นี้: reply token ของ LINE อายุสั้น**

ถ้ารอ LLM ตอบ (3-10 วินาที) แล้วค่อย reply → token อาจหมดอายุ ตอบไม่ได้
ทางแก้คือ:

1. verify signature (เร็ว)
2. **ตอบ 200 กลับ LINE ทันที**
3. ประมวลผลใน ``BackgroundTasks``
4. ตอบ user ด้วย reply token ถ้าทัน ไม่ทันก็ push

ถ้าไม่ทำแบบนี้ LINE จะ retry webhook ซ้ำ (เพราะคิดว่าเราล่ม) → user ได้ข้อความซ้ำ

รันด้วย::

    uvicorn app.main:app --reload --port 8000

แล้วเปิด tunnel (URL ต้องเป็น HTTPS):

    ngrok http 8000                     # URL เปลี่ยนทุกครั้งที่ restart
    tailscale funnel 8000               # URL คงที่ — สะดวกกว่าตอน dev

ตั้ง Webhook URL ใน LINE Console เป็น ``https://<tunnel>/webhook``
"""

from __future__ import annotations

import contextlib
import json
import logging
import sys
from pathlib import Path
from typing import Annotated, AsyncIterator
from urllib.parse import parse_qsl, unquote, urlencode

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    Response,
)
from pydantic import BaseModel, Field

from . import admin, admin_activities, planner
from . import router as bot_router
from .config import Settings, get_settings
from .db import Database, SupportsExecute, SupportsQuery
from .db import connect as connect_database
from .line import messages as msg
from .line.auth import LiffAuthError, VerifiedUser, hash_user_id, verify_id_token
from .line.client import LineApiError, LineClient
from .line.signature import verify_signature
from .llm import LlmClient
from .repository import CHAT_STATUS_DELIVERED, CHAT_STATUS_SEND_FAILED

log = logging.getLogger("app.main")

# httpx client ตัวเดียวทั้งแอป — reuse connection pool
# สร้างใหม่ทุก request จะช้าและเปลือง file descriptor
_http: httpx.AsyncClient | None = None

# connection pool ของ Postgres — ``None`` ได้ (ยังไม่ตั้ง DATABASE_URL หรือต่อไม่ได้)
# ตั้งใจให้แอปทำงานต่อได้แบบไม่มี DB แล้วให้บอทตอบว่า "ยังไม่มีข้อมูล"
_db: Database | None = None

# LLM client — ``None`` ได้ (ยังไม่ตั้ง LLM_API_KEY) AI Chat จะข้ามตัวเอง
# ใช้ httpx client ตัวเดียวกับทั้งแอป (connection pool เดียว)
_llm: LlmClient | None = None


def _configure_logging(level: str) -> None:
    """
    ตั้ง logging + **บังคับ stream เป็น UTF-8**

    บน Windows stderr default เป็น cp874/cp1252 → ข้อความไทยใน log
    กลายเป็น ``?????`` (เจอจริงตอนรัน uvicorn) ทำให้อ่าน error ไม่ได้เลย
    ตั้ง ``PYTHONUTF8=1`` ช่วยได้ แต่พึ่งพาไม่ได้เพราะคนรันอาจลืม
    (และ ``uvicorn --reload`` spawn process ใหม่) → บังคับในโค้ดชัวร์กว่า
    """
    stream = sys.stderr
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        with contextlib.suppress(Exception):
            reconfigure(encoding="utf-8", errors="replace")

    handler = logging.StreamHandler(stream)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s | %(message)s")
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _http, _db, _llm
    settings = get_settings()
    _configure_logging(settings.log_level)
    _http = httpx.AsyncClient(timeout=30.0)
    log.info("เริ่มทำงาน (env=%s, program=%s)", settings.app_env, settings.default_program_code)

    # เตือนตอนสตาร์ทว่าอะไรยังไม่ตั้ง — ดีกว่าไปพังตอน user ยิงเข้ามา
    for name, label in [
        ("line_channel_secret", "LINE_CHANNEL_SECRET"),
        ("line_channel_access_token", "LINE_CHANNEL_ACCESS_TOKEN"),
        ("line_login_channel_id", "LINE_LOGIN_CHANNEL_ID"),
        ("llm_api_key", "LLM_API_KEY"),
        ("user_id_pepper", "USER_ID_PEPPER"),
        ("database_url", "DATABASE_URL"),
    ]:
        if not getattr(settings, name):
            log.warning("ยังไม่ได้ตั้ง %s — ฟีเจอร์ที่เกี่ยวข้องจะใช้ไม่ได้", label)

    # LLM สร้างก่อนต่อ DB — AI Chat ใช้ DB ด้วย แต่สร้าง client ล่วงหน้าได้
    # (ไม่ยิงเน็ตตอนสร้าง) ถ้าไม่มี key ก็ปล่อยให้ None แล้วข้ามชั้นนี้ไป
    if settings.llm_api_key and _http is not None:
        _llm = LlmClient(settings, _http)
        log.info("LLM พร้อม (model=%s)", settings.llm_model)

    _db = await connect_database(settings)

    try:
        yield
    finally:
        _llm = None
        if _db is not None:
            await _db.close()
            _db = None
        await _http.aclose()
        _http = None
        log.info("ปิดการทำงาน")


app = FastAPI(
    title="LINE AI Academic Assistant",
    description="แชทบอทให้คำปรึกษาด้านการเรียน — มรภ.มหาสารคาม",
    version="0.1.0",
    lifespan=lifespan,
)


def get_http() -> httpx.AsyncClient:
    if _http is None:  # pragma: no cover - เกิดได้เฉพาะเรียกนอก lifespan
        raise RuntimeError("HTTP client ยังไม่พร้อม (แอปยังไม่ start)")
    return _http


def get_db() -> SupportsQuery | None:
    """
    connection pool — **คืน ``None`` ได้** ถ้ายังต่อ DB ไม่ได้

    ตั้งใจไม่ raise เพราะบอทควรตอบว่า "ยังไม่มีข้อมูล" ได้
    ดีกว่าเงียบหรือส่ง 500 กลับ LINE (ซึ่งจะทำให้ LINE retry ซ้ำ)
    """
    return _db


def get_llm() -> LlmClient | None:
    """LLM client — ``None`` ได้เมื่อไม่ได้ตั้ง ``LLM_API_KEY``"""
    return _llm


SettingsDep = Annotated[Settings, Depends(get_settings)]
HttpDep = Annotated[httpx.AsyncClient, Depends(get_http)]


# ── health check ────────────────────────────────────────────────────────────


async def _database_status(settings: Settings) -> str:
    """
    สามสถานะที่ต่างกันจริงและต้องแยกให้ออกตอน debug:

    * ``not_configured`` — ยังไม่ได้ตั้ง ``DATABASE_URL``
    * ``unreachable`` — ตั้งแล้วแต่ต่อไม่ได้ (DB ล่ม / DSN ผิด / firewall)
    * ``ok`` — ต่อได้และ query ผ่าน

    ถ้ารวม ``unreachable`` เข้ากับ ``not_configured`` จะหลงคิดว่าลืมตั้งค่า
    ทั้งที่ปัญหาจริงคือ DB ล่ม
    """
    if _db is None:
        return "unreachable" if settings.database_url else "not_configured"
    return "ok" if await _db.healthy() else "unreachable"


@app.get("/health")
async def health(settings: SettingsDep) -> dict:
    """
    health check — บอกว่าอะไรพร้อม/ไม่พร้อม โดยไม่เปิดเผยค่า secret

    ``configured`` = ตั้งค่าใน .env แล้วหรือยัง
    ``checks`` = ทดสอบจริงแล้วใช้ได้ไหม (ตอนนี้มีแค่ฐานข้อมูล)
    """
    return {
        "status": "ok",
        "env": settings.app_env,
        "program": settings.default_program_code,
        "configured": {
            "line_messaging": bool(
                settings.line_channel_secret and settings.line_channel_access_token
            ),
            "liff": bool(settings.line_login_channel_id and settings.liff_id),
            "llm": bool(settings.llm_api_key),
            "database": bool(settings.database_url),
            "user_hashing": bool(settings.user_id_pepper),
        },
        "checks": {
            "database": await _database_status(settings),
        },
        "llm": {
            "base_url": settings.llm_base_url,
            "model": settings.llm_model,
            "embedding_model": settings.embedding_model,
            "embedding_dim": settings.embedding_dim,
        },
    }


# ── LINE webhook ────────────────────────────────────────────────────────────


async def build_result(
    event: dict,
    db: SupportsQuery | None = None,
    *,
    settings: Settings | None = None,
    llm: LlmClient | None = None,
    user_hash: str | None = None,
) -> bot_router.RouteResult | None:
    """
    ตัดสินใจว่าจะตอบอะไร — **ไม่แตะ LINE API เลย**

    แยกออกจากการส่งเพื่อให้เทสได้โดยไม่ต้องมี access token
    และเพื่อให้ error เรื่อง config ไม่ปนกับ bug ของ router

    ``settings``/``llm``/``user_hash`` ส่งต่อให้ AI Chat (Requirement ข้อ 9)
    ถ้า ``llm`` เป็น ``None`` router จะตอบ fallback แบบเดิม ไม่มีอะไรพัง
    """
    event_type = event.get("type")

    if event_type == "follow":
        return await bot_router.handle_follow(settings=settings)

    if event_type == "postback":
        data = (event.get("postback") or {}).get("data", "")
        return await bot_router.handle_postback(
            data,
            db,
            settings=settings,
            llm=llm,
            user_hash=user_hash,
        )

    if event_type == "message":
        message = event.get("message") or {}
        if message.get("type") != "text":
            # รูป/สติกเกอร์/เสียง — ยังไม่รองรับ บอกตรง ๆ
            return bot_router.RouteResult(
                messages=[
                    msg.text_message(
                        "ตอนนี้ระบบรับได้เฉพาะข้อความตัวอักษรครับ",
                        msg.quick_reply(msg.MAIN_MENU_ACTIONS),
                    )
                ],
                answered_by="fallback",
            )
        return await bot_router.handle_text(
            message.get("text", ""),
            db,
            settings=settings,
            llm=llm,
            user_hash=user_hash,
        )

    log.debug("ข้าม event ประเภท %r", event_type)
    return None


async def process_event(event: dict, settings: Settings) -> None:
    """
    ประมวลผล 1 event — รันใน background หลังตอบ 200 ให้ LINE แล้ว

    ห้ามให้ exception หลุดออกไป เพราะ background task ที่ error
    จะไม่มีใครเห็นถ้าไม่ log
    """
    event_type = event.get("type")
    source = event.get("source") or {}
    user_id = source.get("userId")
    reply_token = event.get("replyToken")

    # hash user id ก่อนทำอะไรทั้งสิ้น — ทุกชั้นที่อยากจำบริบทผู้ใช้ต้องใช้ค่านี้
    # (ไม่ใช่ line_user_id ดิบ — PDPA ดู :func:`app.line.auth.hash_user_id`)
    # ไม่มี pepper → ไม่ hash → AI Chat ไม่จำบริบท แต่บอทยังตอบชั้นอื่นได้
    user_hash = None
    if user_id and settings.user_id_pepper:
        user_hash = hash_user_id(user_id, settings.user_id_pepper)

    try:
        result = await build_result(
            event,
            get_db(),
            settings=settings,
            llm=get_llm(),
            user_hash=user_hash,
        )
        if result is None:
            return

        messages = msg.clamp_messages(result.messages)
        if not messages:
            return

        if not reply_token and not user_id:
            log.warning("event ไม่มีทั้ง replyToken และ userId — ตอบไม่ได้")
            return

        # สร้าง client หลังคิดคำตอบเสร็จ — ถ้ายังไม่ตั้ง token จะได้เห็นว่า
        # router ทำงานถูกแล้ว ติดแค่ config (ไม่ใช่ traceback ที่ทำให้เข้าใจผิด)
        try:
            client = LineClient(settings, get_http())
        except RuntimeError as exc:
            log.warning(
                "ยังส่งข้อความไม่ได้ (%s) — router คิดคำตอบไว้แล้ว: type=%s by=%s intent=%s %d ข้อความ",
                exc,
                event_type,
                result.answered_by,
                result.intent_key,
                len(messages),
            )
            return

        # ส่งกับบันทึกอยู่ใน try เดียวกัน เพราะ **ทุกทางออกต้องเขียน chat_logs
        # หนึ่งแถวเสมอ** ไม่ว่าจะส่งถึงหรือไม่ (ดู ``except LineApiError``)
        try:
            if reply_token and user_id:
                channel = await client.reply_or_push(reply_token, user_id, messages)
            elif reply_token:
                await client.reply(reply_token, messages)
                channel = "reply"
            else:
                await client.push(user_id, messages)
                channel = "push"
        except LineApiError as exc:
            # เดิมตรงนี้ log ทิ้งแล้วจบ → รอบที่ส่งไม่ถึง **ไม่มีแถวใน chat_logs
            # เลย** ทั้งที่ router คิดคำตอบเสร็จแล้ว ธีสิสนับจำนวนรอบที่ตอบได้
            # จากตารางนี้ตรง ๆ ความล้มเหลวจึงหายไปจากข้อมูลและอัตราการตอบสำเร็จ
            # สูงเกินจริงแบบเงียบ ๆ — บันทึกเป็น send_failed แล้วจบ
            #
            # ``reply_or_push`` ลอง push ให้แล้วก่อนจะโยนออกมา (ดู
            # :meth:`app.line.client.LineClient.reply_or_push`) มาถึงนี่คือ
            # ทุกทางพังหมด และเป็น except ตัวเดียวของทั้งการส่ง → เขียนแถวเดียว
            log.error(
                "LINE API ล้มเหลว ส่งคำตอบไม่ถึงผู้ใช้: %s (type=%s by=%s intent=%s)",
                exc,
                event_type,
                result.answered_by,
                result.intent_key,
            )
            await _log_conversation(
                event, result, user_hash, status=CHAT_STATUS_SEND_FAILED
            )
            return

        log.info(
            "ตอบแล้ว: type=%s by=%s intent=%s ผ่าน=%s",
            event_type,
            result.answered_by,
            result.intent_key,
            channel,
        )

        # บันทึกลง chat_logs — วัดผลธีสิส (fallback rate, intent, ต้นทุน LLM)
        # และเก็บบริบทสนทนาให้ AI Chat ในรอบถัดไป (Requirement ข้อ 9)
        await _log_conversation(event, result, user_hash, status=CHAT_STATUS_DELIVERED)

        # สลับ Rich Menu รายผู้ใช้ตามโหมดปรึกษา — ทำหลังส่ง+บันทึกสำเร็จแล้ว
        # เพราะเมนูไม่ขึ้นไม่คุ้มกับการทำให้รอบสนทนาพัง/ข้อมูลวัดผลหาย
        await _switch_rich_menu(client, settings, user_id, result)

    except Exception:
        log.exception("ประมวลผล event ล้มเหลว (type=%s)", event_type)


async def _switch_rich_menu(client, settings: Settings, user_id: str | None, result) -> None:
    """
    ผูก/ถอดใบโหมดปรึกษาให้ผู้ใช้คนนี้ตาม ``result.rich_menu``

    * ``"consult"`` → ผูกใบปรึกษา (กลบเมนูหลักจนกว่าจะถอด)
    * ``"main"``    → ถอด กลับเมนูหลักของบัญชี
    * ``None``      → ไม่สลับ (คำตอบธรรมดา / ในโหมดที่ปุ่มไม่ได้จบโหมด)

    เงื่อนไขที่จะข้ามเงียบ ๆ (ไม่ใช่ข้อผิดพลาด):

    * ไม่มี ``userId`` — group chat ไม่มีเมนูรายผู้ใช้
    * ยังไม่ได้ตั้ง ``RICH_MENU_CONSULT_ID`` — ฟีเจอร์ปิดทั้งระบบ
      (ผู้ใช้ยังเห็นเมนูหลักตลอด ถือว่าเสื่อมอย่างสุภาพ)

    ความล้มเหลวของ LINE API ถูกกลืนแล้วแค่ log warning — เมนูค้างใบเดิม
    ดีกว่าทำให้ผู้ใช้เห็นว่าบอทพัง และคำตอบจริงถูกส่งไปแล้ว
    """
    consult_id = settings.rich_menu_consult_id
    if not result.rich_menu or not user_id or not consult_id:
        return

    try:
        if result.rich_menu == "consult":
            await client.link_rich_menu(user_id, consult_id)
        elif result.rich_menu == "main":
            await client.unlink_rich_menu(user_id)
        else:
            log.warning("ไม่รู้จักค่าสลับเมนู %r — ข้าม", result.rich_menu)
            return
        log.info("สลับ Rich Menu: user=...%s → %s", user_id[-6:], result.rich_menu)
    except LineApiError as exc:
        log.warning("สลับ Rich Menu ไม่สำเร็จ (ไม่กระทบคำตอบ): %s", exc)


async def _log_conversation(
    event: dict,
    result: bot_router.RouteResult,
    user_hash: str | None,
    *,
    status: str = CHAT_STATUS_DELIVERED,
) -> None:
    """
    เขียน 1 รอบสนทนาลง ``chat_logs`` — **ล้มเหลวได้แต่ห้ามพังบทสนทนา**

    ส่งข้อความไปแล้วค่อยบันทึก: ถ้า DB เขียนไม่ได้ นักศึกษาก็ยังได้คำตอบ
    (แค่เสียข้อมูลวัดผล) ซึ่งดีกว่าตอบเงียบเพราะ log ล้ม

    ``status`` แยกรอบที่ส่งถึงผู้ใช้ออกจากรอบที่ส่งไม่ถึง — ห้ามให้ความล้มเหลว
    ของการเขียนตรงนี้บังความล้มเหลวของการส่ง จึงกลืน exception ทุกตัวแล้ว
    log เป็น warning เท่านั้น (ฝ่ายเรียกได้ log error ของการส่งไปก่อนแล้ว)
    """
    from . import repository as repo

    db = get_db()
    if db is None or not isinstance(db, SupportsExecute):
        return

    try:
        # หา/สร้าง app_users ก่อน — chat_logs.user_id อ้างอิงตารางนั้น
        # ถ้า router รู้ user_id อยู่แล้ว (ai_chat) ใช้เลย ไม่ต้อง ensure ซ้ำ
        app_user_id = result.user_id
        if app_user_id is None and user_hash:
            app_user_id = await repo.ensure_user(db, user_hash)

        message_text = (event.get("message") or {}).get("text")
        if event.get("type") == "postback":
            message_text = (event.get("postback") or {}).get("data")

        # flex message ไม่มี ``text`` — ใช้ ``altText`` (ข้อความที่ขึ้นใน
        # รายการแชทแทนการ์ด) แทน เพื่อไม่ให้รอบที่ตอบด้วยการ์ดหายไปจาก
        # ``chat_logs`` (ใช้วัดผลในธีสิส)
        response_parts: list[str] = []
        for message in result.messages:
            if message.get("type") == "flex":
                response_parts.append(message.get("altText", ""))
            elif message.get("text"):
                response_parts.append(message["text"])

        response_text = "\n".join(
            part for part in response_parts if part
        ) or None

        await repo.insert_chat_log(
            db,
            user_id=app_user_id,
            message_text=message_text,
            answered_by=result.answered_by,
            intent_key=result.intent_key,
            confidence=result.confidence,
            response_text=response_text,
            citations=result.citations or None,
            latency_ms=result.latency_ms,
            llm_model=result.llm_model,
            prompt_tokens=result.prompt_tokens,
            output_tokens=result.output_tokens,
            status=status,
        )
    except Exception:
        log.warning("บันทึก chat_logs ไม่สำเร็จ", exc_info=True)


@app.post("/webhook")
async def webhook(
    request: Request,
    background: BackgroundTasks,
    settings: SettingsDep,
    x_line_signature: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    """
    รับ webhook จาก LINE

    ลำดับสำคัญ: verify signature → **ตอบ 200 ทันที** → ประมวลผล background
    """
    body = await request.body()

    if not settings.line_channel_secret:
        log.error("ยังไม่ได้ตั้ง LINE_CHANNEL_SECRET — ปฏิเสธ webhook ทุกตัว")
        return JSONResponse({"message": "server not configured"}, status_code=503)

    if not verify_signature(settings.line_channel_secret, body, x_line_signature):
        # response ไม่บอกรายละเอียดว่าผิดตรงไหน (กัน probe) แต่ **log ต้องแยกให้ออก**
        # เพราะสองกรณีนี้แก้ไม่เหมือนกัน:
        #   ไม่มี header เลย  → ไม่ใช่ LINE ที่ยิงมา (bot สแกนเน็ต / uptime check)
        #                      หรือ tunnel/reverse proxy กิน header ทิ้ง
        #   มี header แต่ไม่ตรง → LINE_CHANNEL_SECRET ผิดช่อง (สลับกับ channel อื่น)
        #                      หรือมีอะไรแก้ body กลางทาง
        # เคยเสียเวลาไล่ผิดทางเพราะ log เดิมเขียนรวมกันเป็นข้อความเดียว
        log.warning(
            "ปฏิเสธ request: %s (body %d ไบต์)",
            "ไม่มี header X-Line-Signature"
            if not x_line_signature
            else "signature ไม่ตรงกับ body",
            len(body),
        )
        return JSONResponse({"message": "invalid signature"}, status_code=403)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse({"message": "invalid json"}, status_code=400)

    events = payload.get("events") or []

    # LINE ส่ง verify request ตอนกดปุ่ม Verify ใน Console — events จะว่าง
    if not events:
        return JSONResponse({"message": "ok"})

    for event in events:
        background.add_task(process_event, event, settings)

    # ตอบทันทีเสมอ ไม่รอ background — ถ้าช้า LINE จะ retry ซ้ำ
    return JSONResponse({"message": "ok"})


# ── LIFF API ────────────────────────────────────────────────────────────────


class LiffLoginRequest(BaseModel):
    """
    ต้องส่ง **ID token** ไม่ใช่ userId

    ``userId`` จาก ``liff.getContext()`` ปลอมได้ (LINE เตือนไว้ในเอกสารเอง)
    ถ้า backend เชื่อค่านั้น ใครก็ดูข้อมูลคนอื่นได้
    """

    id_token: str = Field(min_length=16, description="ค่าจาก liff.getIDToken()")


class LiffLoginResponse(BaseModel):
    success: bool
    user_hash: str = Field(description="SHA-256(line_user_id + pepper)")
    display_name: str | None = None
    is_new_user: bool = False


async def verify_or_401(
    id_token: str, settings: Settings, http: httpx.AsyncClient
) -> VerifiedUser:
    """
    verify ID token กับ LINE แล้วแปลง error เป็น HTTP status ที่ถูกต้อง

    แยกออกมาเป็นฟังก์ชันธรรมดา (ไม่ใช่ dependency) เพราะ endpoint ที่รับ body
    มากกว่า ``id_token`` ต้องประกาศ body model ของตัวเอง — ถ้าใช้ dependency
    ที่ประกาศ body ด้วย FastAPI จะบังคับให้ body ซ้อนเป็นสองก้อน
    (``{"payload": ..., "body": ...}``) ซึ่งฝั่งหน้าเว็บต้องรู้เรื่องภายในของ
    เซิร์ฟเวอร์เพื่อจะยิงให้ถูก
    """
    try:
        return await verify_id_token(id_token, settings, http)
    except LiffAuthError as exc:
        raise _http_error(401, str(exc)) from exc
    except RuntimeError as exc:
        raise _http_error(503, str(exc)) from exc


async def require_verified_user(
    payload: LiffLoginRequest, settings: SettingsDep, http: HttpDep
) -> VerifiedUser:
    """dependency: verify ID token กับ LINE ก่อนเข้าถึง endpoint"""
    return await verify_or_401(payload.id_token, settings, http)


def _http_error(status: int, detail: str):
    from fastapi import HTTPException

    return HTTPException(status_code=status, detail=detail)


@app.post("/api/liff/login", response_model=LiffLoginResponse)
async def liff_login(
    user: Annotated[VerifiedUser, Depends(require_verified_user)],
) -> LiffLoginResponse:
    """
    ยืนยันตัวตนจาก LIFF แล้วสร้าง/อัปเดตผู้ใช้

    ตามแผน B: **ไม่ขอรหัสผ่านระบบทะเบียน** นักศึกษาแจ้งวิชาที่ผ่านเองผ่าน LIFF
    เก็บลง DB แค่ ``user_hash`` + ``program_code`` + รายการรหัสวิชา
    ไม่เก็บชื่อ ไม่เก็บรหัสนักศึกษา ไม่เก็บเกรด

    ``display_name`` ที่คืนกลับไปใช้ทักทายบนหน้าเว็บเท่านั้น — **ไม่ถูกเขียนลง
    ฐานข้อมูล** (มาจาก ID token ที่ผู้ใช้ถืออยู่แล้ว ไม่ใช่ของใหม่ที่เราไปเก็บ)

    ไม่มี DB ก็ยังตอบ 200: หน้า LIFF จะแสดงว่าบันทึกไม่ได้ ดีกว่าค้างที่หน้าขาว
    """
    is_new = True
    db = get_db()
    if db is not None and isinstance(db, SupportsExecute):
        from . import repository as repo

        before = await repo.user_profile(db, user.user_hash)
        is_new = before is None
        await repo.ensure_user(db, user.user_hash)

    log.info("LIFF login สำเร็จ (hash=%s... ผู้ใช้ใหม่=%s)", user.user_hash[:12], is_new)
    return LiffLoginResponse(
        success=True,
        user_hash=user.user_hash,
        display_name=user.display_name,
        is_new_user=is_new,
    )


# หน้า LIFF เสิร์ฟจากแอปเดียวกัน ไม่แยก static host
#
# เหตุผล: LIFF ต้องเป็น HTTPS และต้องเรียก /api/liff/* ได้ อยู่โดเมนเดียวกัน
# แล้วไม่ต้องตั้ง CORS เลย (CORS ที่ตั้งผิดคือช่องให้เว็บอื่นยิง API แทนผู้ใช้)
# Endpoint URL ที่ต้องใส่ใน LINE Developers Console = <PUBLIC_BASE_URL>/liff
LIFF_PAGE = Path(__file__).resolve().parent.parent / "web" / "liff" / "index.html"


@app.get("/liff", response_class=HTMLResponse)
async def liff_page() -> HTMLResponse:
    """หน้าติ๊กวิชาที่ผ่านแล้ว — ไฟล์เดียว ไม่มี asset ภายนอกนอกจาก LIFF SDK"""
    if not LIFF_PAGE.is_file():  # pragma: no cover - ไฟล์หายจาก repo เท่านั้น
        raise _http_error(500, "ไม่พบไฟล์หน้า LIFF ในเซิร์ฟเวอร์")
    return HTMLResponse(LIFF_PAGE.read_text(encoding="utf-8"))


# ── หน้า admin ──────────────────────────────────────────────────────────────
#
# เสิร์ฟจากแอปเดียวกันด้วยเหตุผลเดียวกับหน้า LIFF (โดเมนเดียว = ไม่ต้องตั้ง CORS)
# ตัว router ของ API อยู่ใน :mod:`app.admin` — ไฟล์นี้แค่เสิร์ฟ HTML
#
# **หน้า HTML เปิดได้โดยไม่ต้องล็อกอิน** โดยเจตนา: มันไม่มีข้อมูลอยู่ในตัว
# ต้องยิง ``/api/admin/*`` พร้อม cookie เซสชันที่ ``/api/admin/login`` ออกให้จึงจะ
# ได้ข้อมูล ตัวที่กันคนอยู่ที่ :func:`app.admin.require_admin` ไม่ใช่ที่การซ่อน
# ไฟล์นี้ (ซ่อน HTML ไม่ใช่การป้องกัน และซ่อนแล้วคนจะเข้าไปกรอกฟอร์มล็อกอินไม่ได้)
ADMIN_PAGE = Path(__file__).resolve().parent.parent / "web" / "admin" / "index.html"

app.include_router(admin.router)
app.include_router(admin_activities.router)


@app.get("/admin", response_class=HTMLResponse)
async def admin_page() -> HTMLResponse:
    """หน้าแก้ข้อมูลของ admin — ไฟล์เดียว ไม่มี build step"""
    if not ADMIN_PAGE.is_file():  # pragma: no cover - ไฟล์หายจาก repo เท่านั้น
        raise _http_error(500, "ไม่พบไฟล์หน้า admin ในเซิร์ฟเวอร์")
    return HTMLResponse(ADMIN_PAGE.read_text(encoding="utf-8"))


# ── ทางเข้าจากลิงก์ liff.line.me ────────────────────────────────────────────
#
# LIFF app หนึ่งใบมี Endpoint URL ได้ค่าเดียว แต่เรามีสองหน้า (``/liff`` ของ
# นักศึกษา และ ``/admin``) จึงตั้ง Endpoint URL เป็น **โดเมนเปล่า** แล้วเปิด
# ด้วยลิงก์ ``https://liff.line.me/<liffId>/admin``
#
# กลไกของ LINE: ลิงก์นั้นจะพาไปที่ Endpoint URL **ราก** พร้อม
# ``?liff.state=%2Fadmin`` (บวก ``code``/``state`` ของการล็อกอิน) แล้วคาดว่า
# หน้าที่รากจะโหลด LIFF SDK เพื่อเด้งต่อไปยัง path ใน ``liff.state`` เอง
# ถ้ารากเป็น 404 ทั้งอย่างนี้จะจบลงด้วย ``{"detail":"Not Found"}`` โดยไม่มี
# อะไรบอกว่าเพราะอะไร (เจอมาแล้ว 28 ส.ค. 2026)
#
# แก้ด้วยการ redirect ฝั่งเซิร์ฟเวอร์แทนที่จะฝัง SDK ไว้ที่ราก: สั้นกว่า และ
# ``code``/``state`` ถูกส่งต่อครบให้ ``liff.init()`` ของหน้าปลายทางจัดการเอง
#
# **allowlist ไม่ใช่การกรอง** — ``liff.state`` มาจาก query string ที่ใครก็ใส่
# อะไรก็ได้ ถ้าเอาไป redirect ตรง ๆ จะได้ open redirect (ยิงลิงก์โดเมนเราที่
# พาไปเว็บหลอกลวง) จึงยอมเฉพาะสองหน้าที่มีจริง
LIFF_STATE_TARGETS = frozenset({"/liff", "/admin"})

# หน้าที่ตอบเมื่อมีคนเปิด "โดเมนเปล่า ๆ" เอง (ไม่มี ``liff.state``)
#
# เดิมตอบ 404 เป็น JSON ``{"detail":"Not Found"}`` ด้วยเหตุผลว่าไม่อยากโฆษณา
# ว่ามีหน้า /admin อยู่ — เหตุผลนั้นยังใช้อยู่ (หน้านี้จึง**ไม่มีลิงก์ไป /admin**
# และไม่เอ่ยถึงมัน) แต่ JSON ก้อนนั้นทำให้คนตั้งระบบเข้าใจว่าเซิร์ฟเวอร์พัง
# แล้วไปไล่แก้ tunnel/webhook ทั้งที่ไม่มีอะไรพัง (เกิดจริง 28 ส.ค. 2026 สองรอบ)
# ตอบหน้าสั้น ๆ ที่บอกว่า "ทำงานอยู่" จึงเป็นข้อมูลที่จริงกว่าและหลงน้อยกว่า
ROOT_PAGE = """<!doctype html>
<html lang="th">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>ระบบผู้ช่วยวิชาการ</title>
<style>
  :root { color-scheme: light dark }
  body { margin: 0; min-height: 100vh; display: grid; place-items: center;
         font-family: "Noto Sans Thai", "Leelawadee UI", "Tahoma", sans-serif;
         line-height: 1.7; padding: 24px; text-align: center }
  h1 { font-size: 1.25rem; margin: 0 0 .5rem }
  p { margin: 0; opacity: .7; font-size: .95rem }
</style>
<h1>ระบบผู้ช่วยวิชาการ</h1>
<p>เซิร์ฟเวอร์ทำงานอยู่ — ใช้งานผ่านแอป LINE</p>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def liff_state_entry(request: Request) -> Response:
    """
    รับลิงก์ ``liff.line.me/<liffId>/<path>`` แล้วส่งต่อไปหน้าที่ขอ

    ไม่มี ``liff.state`` = คนเปิดโดเมนเปล่า ๆ เอง → ตอบ :data:`ROOT_PAGE`
    ไม่เดาว่าเขาอยากไปหน้าไหน (เด้งไปหน้า admin เองจะกลายเป็นการโฆษณาว่ามี
    หน้านี้อยู่)
    """
    raw = request.query_params.get("liff.state")
    if raw is None:
        return HTMLResponse(ROOT_PAGE)

    # บางเส้นทาง LINE ส่ง ``liff.state`` มาแบบ encode ซ้อนสองชั้น — เห็นได้จาก
    # ``liffRedirectUri`` ที่มันแนบมาเองว่าเป็น ``liff.state=%252Fadmin``
    # ชั้นนอกถูกถอดตอน parse query string เหลือค่า ``%2Fadmin`` ซึ่งไม่ตรง
    # allowlist แล้วกลายเป็น 404 ทั้งที่ปลายทางถูกต้อง จึงถอดอีกชั้นเฉพาะกรณี
    # ที่ยังไม่ได้ขึ้นต้นด้วย ``/`` — ถอดแล้วยัง**ต้องผ่าน allowlist เหมือนกัน**
    # (การถอด encoding ไม่ใช่การอนุญาต ค่าที่ถอดออกมาชี้ออกนอกเว็บก็ยังถูกปฏิเสธ)
    if not raw.startswith("/"):
        raw = unquote(raw)

    target, _, inner_query = raw.partition("?")
    if target not in LIFF_STATE_TARGETS:
        log.warning("liff.state ชี้ไปที่ %r ซึ่งไม่อยู่ในรายการที่ยอมให้เด้งไป", target)
        raise _http_error(404, "Not Found")

    # ``code``/``state`` ของการล็อกอินอยู่ใน query ชั้นนอก ต้องส่งต่อให้ครบ
    # ไม่งั้นหน้าปลายทางจะเริ่มล็อกอินใหม่ตั้งแต่ต้นเป็นวงไม่จบ
    passthrough = [
        (key, value)
        for key, value in request.query_params.multi_items()
        if key != "liff.state"
    ]
    query = urlencode(
        [*parse_qsl(inner_query, keep_blank_values=True), *passthrough]
    )
    return RedirectResponse(f"{target}?{query}" if query else target)


@app.get("/api/liff/config")
async def liff_config(settings: SettingsDep) -> dict:
    """
    ค่า config ที่หน้า LIFF ต้องใช้

    ปลอดภัยที่จะเปิดเผย: LIFF ID ไม่ใช่ secret (ต้องใส่ใน HTML อยู่แล้ว)
    """
    return {
        "liff_id": settings.liff_id,
        "program_code": settings.default_program_code,
        "max_credits_per_term": settings.planner_max_credits,
    }


# ── LIFF: ติ๊กวิชาที่ผ่านแล้ว (input ของ Planner Engine) ──────────────────────
#
# ทำไมต้องให้ติ๊กเอง: ระบบไม่ได้ต่อกับระบบทะเบียน และ **ไม่ขอรหัสผ่าน**
# ของนักศึกษาโดยเจตนา (เก็บรหัสผ่านระบบราชการไว้ในแอปนักศึกษาคือความเสี่ยง
# ที่ไม่คุ้มกับความสะดวก) จึงแลกด้วยการติ๊กครั้งเดียวแล้วใช้ได้ตลอด
#
# เก็บแค่ "ผ่าน/ไม่ผ่าน" ไม่เก็บเกรด — คำนวณหน่วยกิตกับลำดับวิชาได้ครบ
# โดยข้อมูลอ่อนไหวน้อยลงมาก (ดู PDPA ใน db/migrations/001_init.sql)


class LiffStateRequest(BaseModel):
    id_token: str = Field(min_length=16)


class LiffSaveRequest(BaseModel):
    id_token: str = Field(min_length=16)
    # รหัสวิชา 7 หลักที่ติ๊กว่าผ่านแล้ว — ส่งมาทั้งชุดเสมอ (ไม่ใช่ diff)
    # เพราะ "ชุด" คือสิ่งที่ผู้ใช้เห็นบนหน้าจอ ส่ง diff แล้วพลาดหนึ่งครั้ง
    # สองฝั่งจะไม่ตรงกันอย่างเงียบ ๆ
    course_codes: list[str] = Field(default_factory=list, max_length=400)
    program_code: str | None = Field(default=None, max_length=20)
    study_year: int | None = Field(default=None, ge=1, le=8)
    # หน่วยกิตหมวดเลือกเสรีที่ผู้ใช้กรอกเอง — หลักสูตรไม่ระบุรายวิชาให้ติ๊ก
    #
    # ขอบเขต 0–60 ต้องอยู่ที่ชั้นนี้ ไม่ใช่ปล่อยให้ CHECK constraint ของ
    # ``app_users`` เป็นคนปฏิเสธ: ค่านอกช่วงจะกลายเป็น 500 (ความผิดของเรา)
    # ทั้งที่มันคือ input ที่ผู้ใช้ส่งผิด (422) — และ ``None`` ยังต่างจาก 0
    # เพราะ 0 = "ยังไม่ผ่านเลย" แต่ ``None`` = "ฟอร์มนี้ไม่ได้ถาม"
    free_elective_credits: int | None = Field(default=None, ge=0, le=60)


def _require_writable_db() -> SupportsExecute:
    db = get_db()
    if db is None or not isinstance(db, SupportsExecute):
        raise _http_error(503, "ฐานข้อมูลยังไม่พร้อม — ลองอีกครั้งในอีกสักครู่")
    return db


def _plan_payload(
    plan_rows: list[dict], passed: set[str], group_rows: list[dict] | None = None
) -> list[dict]:
    """
    แผนการเรียนในรูปที่หน้าเว็บ render เป็น checkbox ได้ตรง ๆ

    ต้องแนบ ``group_label`` มาด้วย ไม่ใช่แค่ ``group_code``: วิชาเลือกมี
    ``std_year``/``std_semester`` เป็น NULL (อ่านออกมาเป็น 0) หน้าเว็บจึงจัด
    กลุ่มตามหมวดแทนเทอม และ "ชื่อหมวด" คือหัวข้อที่ผู้ใช้ต้องเห็นแทนคำว่า
    "ปี 0 เทอม 0" ที่ไม่มีอยู่จริงในหลักสูตร — join ที่นี่ทีเดียวเพื่อไม่ให้
    หน้าเว็บต้องถือตารางแปลรหัสหมวดของตัวเอง
    """
    labels = {
        str(row["group_code"]): str(row.get("group_label") or row["group_code"])
        for row in (group_rows or [])
    }
    payload = []
    for row in plan_rows:
        code = row.get("group_code")
        code = str(code) if code else None
        payload.append(
            {
                "course_code": row["course_code"],
                "course_code_full": row.get("course_code_full"),
                "name": row.get("name_th"),
                "credits": row.get("credits"),
                "credits_text": row.get("credits_text"),
                "std_year": row.get("std_year"),
                "std_semester": row.get("std_semester"),
                "note": row.get("note"),
                "passed": row["course_code"] in passed,
                "group_code": code,
                "group_label": labels.get(code) if code else None,
            }
        )
    return payload


def _progress_payload(progress: planner.Progress) -> dict:
    """
    สรุปตัวเลขจาก :class:`app.planner.Progress` ให้หน้าเว็บแสดงหัวข้อสรุป

    ทุกตัวเลขในนี้ **อ่านมาจาก planner ตรง ๆ** ไม่มีการคิดซ้ำที่ชั้นนี้ (เช่น
    ไม่ min() หน่วยกิตเอง) เพราะถ้าคิดสองที่ วันหนึ่งสูตรจะเพี้ยนกันแล้ว
    ตัวเลขที่ผู้ใช้เห็นจะไม่ตรงกับตัวเลขที่บอทตอบใน LINE

    ``groups`` เรียงตามลำดับที่ planner ให้มา (ซึ่งมาจาก ``sort_order`` ใน
    ``curriculum_groups``) — ห้ามเรียงใหม่ที่นี่ ลำดับหมวดคือสิ่งที่ผู้ดูแล
    ตั้งไว้จากหน้า /admin
    """
    return {
        "program_code": progress.program_code,
        "plan_courses": progress.plan_courses,
        "passed_courses": len(progress.passed_statuses),
        "passed_credits": progress.passed_credits,
        "remaining_courses": len(progress.remaining),
        "remaining_plan_credits": progress.remaining_plan_credits,
        "percent_complete": progress.percent_complete,
        "total_credits_required": progress.total_credits_required,
        "credits_left_to_graduate": progress.credits_left_to_graduate,
        # หน้าเว็บต้องบอกผู้ใช้ตรง ๆ ว่ายังไม่มีข้อมูลวิชาบังคับก่อน
        "prereq_known": progress.prereq_known,
        "passed_outside_plan": list(progress.passed_outside_plan),
        "free_elective_credits": progress.free_elective_credits,
        # ต่างจาก passed_credits เมื่อเก็บวิชาเลือกเกินโควตาหมวด
        "counted_credits": progress.counted_credits,
        "groups": [
            {
                "group_code": group.group_code,
                "group_label": group.group_label,
                "required_credits": group.required_credits,
                "passed_credits": group.passed_credits,
                "counted_credits": group.counted_credits,
                "is_choice": group.is_choice,
                "complete": group.complete,
                "percent": group.percent,
                "sort_order": group.sort_order,
            }
            for group in progress.groups
        ],
    }


async def _load_state(db: SupportsExecute, user_hash: str, program_code: str) -> dict:
    """อ่านสถานะทั้งหมดที่หน้า LIFF ต้องใช้ใน 6 คิวรี (ไม่ขึ้นกับจำนวนวิชา)"""
    from . import repository as repo

    user_id = await repo.ensure_user(db, user_hash)
    profile = await repo.user_profile(db, user_hash) or {}
    chosen = profile.get("program_code") or program_code

    plan_rows = await repo.curriculum_plan(db, chosen)
    done_rows = await repo.completed_courses(db, user_id)
    passed = {row["course_code"] for row in done_rows}
    program = await repo.program_info(db, chosen)
    prereq_rows = await repo.prerequisites_for_program(db, chosen)
    # โควตารายหมวด — หลักสูตรที่ยังไม่ได้กรอกจะได้ลิสต์ว่าง แล้ว planner
    # ถอยไปใช้สูตรนับจำนวนวิชาเอง (ไม่พัง แต่ตัวเลขหยาบกว่า)
    group_rows = await repo.curriculum_groups(db, chosen)

    progress = planner.evaluate(
        chosen,
        plan_rows,
        passed,
        prereq_rows=prereq_rows,
        total_credits_required=(program or {}).get("total_credits"),
        group_rows=group_rows,
        free_elective_credits=profile.get("free_elective_credits") or 0,
    )
    return {
        "program_code": chosen,
        "program_name": (program or {}).get("program_name"),
        "study_year": profile.get("study_year"),
        "plan": _plan_payload(plan_rows, passed, group_rows),
        "progress": _progress_payload(progress),
    }


@app.post("/api/liff/state")
async def liff_state(
    payload: LiffStateRequest, settings: SettingsDep, http: HttpDep
) -> dict:
    """
    แผนการเรียน + วิชาที่ติ๊กไว้แล้ว + ตัวเลขความก้าวหน้า — สำหรับ render หน้าเว็บ

    ต้องส่ง ID token มาทุกครั้ง (ไม่มี session cookie): ``userId`` จาก
    ``liff.getContext()`` ปลอมได้ ถ้าเชื่อค่านั้นใครก็อ่านข้อมูลคนอื่นได้
    """
    user = await verify_or_401(payload.id_token, settings, http)
    db = _require_writable_db()
    return await _load_state(db, user.user_hash, settings.default_program_code)


@app.post("/api/liff/completed_courses")
async def liff_save_completed(
    payload: LiffSaveRequest, settings: SettingsDep, http: HttpDep
) -> dict:
    """
    บันทึก "ชุด" วิชาที่ผ่านแล้ว แล้วคืนสถานะใหม่กลับไปทั้งก้อน

    คืนสถานะใหม่ด้วย (ไม่ใช่แค่ ``{"ok": true}``) เพื่อให้หน้าเว็บแสดงตัวเลข
    ที่ **เซิร์ฟเวอร์คำนวณ** ไม่ใช่ตัวเลขที่หน้าเว็บเดาเอง — สองฝั่งคิดเองแล้ว
    ไม่ตรงกันคือบั๊กที่ผู้ใช้เห็นก่อนเราเสมอ
    """
    user = await verify_or_401(payload.id_token, settings, http)
    db = _require_writable_db()

    from . import repository as repo

    user_id = await repo.ensure_user(db, user.user_hash)
    # เทียบ ``is not None`` กับ free_elective_credits ไม่ใช่ truthy: ส่ง 0 มา
    # คือ "แก้ให้เป็น 0" (ผู้ใช้ลบตัวเลขที่เคยกรอกไว้) ต้องบันทึกด้วย
    if (
        payload.program_code
        or payload.study_year
        or payload.free_elective_credits is not None
    ):
        await repo.set_user_program(
            db,
            user.user_hash,
            program_code=payload.program_code,
            study_year=payload.study_year,
            free_elective_credits=payload.free_elective_credits,
        )

    # กันขยะเข้าตาราง: รับเฉพาะรหัส 7 หลักที่อยู่ในหลักสูตรจริง
    program_code = payload.program_code or settings.default_program_code
    plan_rows = await repo.curriculum_plan(db, program_code)
    known = {row["course_code"] for row in plan_rows}
    accepted = sorted({code.strip() for code in payload.course_codes} & known)
    rejected = sorted({code.strip() for code in payload.course_codes} - known)
    if rejected:
        log.info("ติ๊กรหัสที่ไม่อยู่ในแผน %s — ไม่บันทึก %s", program_code, rejected)

    counts = await repo.replace_completed_courses(db, user_id, accepted)
    state = await _load_state(db, user.user_hash, program_code)
    return {
        "success": True,
        "saved": len(accepted),
        "added": counts.get("added", 0),
        "removed": counts.get("removed", 0),
        "rejected": rejected,
        **state,
    }
