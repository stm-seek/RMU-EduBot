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
from typing import Annotated, AsyncIterator

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import router as bot_router
from .config import Settings, get_settings
from .db import Database, SupportsExecute, SupportsQuery
from .db import connect as connect_database
from .line import messages as msg
from .line.auth import LiffAuthError, VerifiedUser, hash_user_id, verify_id_token
from .line.client import LineApiError, LineClient
from .line.signature import verify_signature
from .llm import LlmClient

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
        return await bot_router.handle_follow()

    if event_type == "postback":
        data = (event.get("postback") or {}).get("data", "")
        return await bot_router.handle_postback(data, db)

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

        if reply_token and user_id:
            channel = await client.reply_or_push(reply_token, user_id, messages)
        elif reply_token:
            await client.reply(reply_token, messages)
            channel = "reply"
        else:
            await client.push(user_id, messages)
            channel = "push"

        log.info(
            "ตอบแล้ว: type=%s by=%s intent=%s ผ่าน=%s",
            event_type,
            result.answered_by,
            result.intent_key,
            channel,
        )

        # บันทึกลง chat_logs — วัดผลธีสิส (fallback rate, intent, ต้นทุน LLM)
        # และเก็บบริบทสนทนาให้ AI Chat ในรอบถัดไป (Requirement ข้อ 9)
        await _log_conversation(event, result, user_hash)

    except LineApiError as exc:
        log.error("LINE API ล้มเหลว: %s", exc)
    except Exception:
        log.exception("ประมวลผล event ล้มเหลว (type=%s)", event_type)


async def _log_conversation(
    event: dict,
    result: bot_router.RouteResult,
    user_hash: str | None,
) -> None:
    """
    เขียน 1 รอบสนทนาลง ``chat_logs`` — **ล้มเหลวได้แต่ห้ามพังบทสนทนา**

    ส่งข้อความไปแล้วค่อยบันทึก: ถ้า DB เขียนไม่ได้ นักศึกษาก็ยังได้คำตอบ
    (แค่เสียข้อมูลวัดผล) ซึ่งดีกว่าตอบเงียบเพราะ log ล้ม
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

        response_text = "\n".join(
            message.get("text", "") for message in result.messages if message.get("text")
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


async def require_verified_user(
    payload: LiffLoginRequest, settings: SettingsDep, http: HttpDep
) -> VerifiedUser:
    """dependency: verify ID token กับ LINE ก่อนเข้าถึง endpoint"""
    try:
        return await verify_id_token(payload.id_token, settings, http)
    except LiffAuthError as exc:
        raise _http_error(401, str(exc)) from exc
    except RuntimeError as exc:
        raise _http_error(503, str(exc)) from exc


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
    """
    # TODO: upsert app_users เมื่อต่อ DB แล้ว
    log.info("LIFF login สำเร็จ (hash=%s...)", user.user_hash[:12])
    return LiffLoginResponse(
        success=True,
        user_hash=user.user_hash,
        display_name=user.display_name,
        is_new_user=True,
    )


@app.get("/api/liff/config")
async def liff_config(settings: SettingsDep) -> dict:
    """
    ค่า config ที่หน้า LIFF ต้องใช้

    ปลอดภัยที่จะเปิดเผย: LIFF ID ไม่ใช่ secret (ต้องใส่ใน HTML อยู่แล้ว)
    """
    return {
        "liff_id": settings.liff_id,
        "program_code": settings.default_program_code,
    }
