"""
Client สำหรับเรียก LINE Messaging API

จุดสำคัญที่ออกแบบไว้:

1. **reply token ใช้ได้ครั้งเดียวและอายุสั้น** → ถ้า reply ล้มเหลวเพราะ token
   หมดอายุ ต้อง fallback ไปใช้ push แทน (มี :meth:`reply_or_push`)

2. **push message กินโควตาฟรีรายเดือน** ส่วน reply ไม่กิน → พยายาม reply ก่อนเสมอ

3. มี :meth:`show_loading` เพื่อแสดง "กำลังพิมพ์" ระหว่างรอ LLM
   (LINE จำกัดให้เป็นช่วง 5-60 วินาที และหารด้วย 5 ลงตัว)
"""

from __future__ import annotations

import logging

import httpx

from ..config import Settings

log = logging.getLogger("app.line.client")

API_BASE = "https://api.line.me/v2/bot"

# LINE บังคับว่า loadingSeconds ต้องอยู่ในช่วง 5-60 และหารด้วย 5 ลงตัว
LOADING_MIN = 5
LOADING_MAX = 60
LOADING_STEP = 5


def normalize_loading_seconds(seconds: int) -> int:
    """
    ปรับค่าให้เข้าเงื่อนไขของ LINE (5-60 และหารด้วย 5 ลงตัว)

    >>> normalize_loading_seconds(1)
    5
    >>> normalize_loading_seconds(12)
    10
    >>> normalize_loading_seconds(999)
    60
    """
    clamped = max(LOADING_MIN, min(LOADING_MAX, seconds))
    return (clamped // LOADING_STEP) * LOADING_STEP


class LineApiError(RuntimeError):
    """LINE API ตอบกลับด้วย error — เก็บ status/body ไว้ให้ debug ได้"""

    def __init__(self, status_code: int, body: str) -> None:
        super().__init__(f"LINE API {status_code}: {body[:400]}")
        self.status_code = status_code
        self.body = body


class LineClient:
    """
    ห่อ Messaging API เท่าที่โปรเจกต์ใช้

    รับ ``httpx.AsyncClient`` จากภายนอกเพื่อให้ reuse connection pool ได้
    (สร้างใหม่ทุก request จะช้าและเปลือง fd)
    """

    def __init__(self, settings: Settings, http: httpx.AsyncClient) -> None:
        settings.require("line_channel_access_token")
        self._settings = settings
        self._http = http
        self._headers = {
            "Authorization": f"Bearer {settings.line_channel_access_token}",
            "Content-Type": "application/json",
        }

    async def _post(self, path: str, payload: dict | None) -> dict:
        # payload=None = POST ตัวเปล่า (เช่น link rich menu ที่ไม่ต้องมี body)
        body_kwargs = {} if payload is None else {"json": payload}
        response = await self._http.post(
            f"{API_BASE}{path}", headers=self._headers, **body_kwargs
        )
        if response.status_code >= 400:
            raise LineApiError(response.status_code, response.text)
        return response.json() if response.content else {}

    async def _delete(self, path: str) -> None:
        """DELETE ไม่มี body — ใช้แค่ ``_post`` ไม่ได้เพราะบังคับส่ง json"""
        response = await self._http.delete(
            f"{API_BASE}{path}", headers=self._headers
        )
        if response.status_code >= 400:
            raise LineApiError(response.status_code, response.text)

    # ── ส่งข้อความ ──────────────────────────────────────────────────────────

    async def reply(self, reply_token: str, messages: list[dict]) -> None:
        """
        ตอบกลับด้วย reply token (ไม่กินโควตาฟรี)

        ใช้ได้ครั้งเดียวต่อ token และหมดอายุเร็ว
        """
        await self._post(
            "/message/reply", {"replyToken": reply_token, "messages": messages}
        )

    async def push(self, to: str, messages: list[dict]) -> None:
        """ส่งข้อความหา user ได้ทุกเวลา — **กินโควตาฟรีรายเดือน**"""
        await self._post("/message/push", {"to": to, "messages": messages})

    async def reply_or_push(
        self, reply_token: str, user_id: str, messages: list[dict]
    ) -> str:
        """
        ลอง reply ก่อน ถ้าล้มเหลว (token หมดอายุ/ถูกใช้แล้ว) ค่อย push

        คืน ``'reply'`` หรือ ``'push'`` เพื่อให้ caller log ได้ว่าใช้ทางไหน
        — ตัวเลขนี้มีประโยชน์ตอนวัดผลว่าระบบตอบช้าจนต้อง push บ่อยแค่ไหน
        """
        try:
            await self.reply(reply_token, messages)
            return "reply"
        except LineApiError as exc:
            log.warning(
                "reply ล้มเหลว (%s) — เปลี่ยนไปใช้ push: %s",
                exc.status_code,
                exc.body[:200],
            )
            await self.push(user_id, messages)
            return "push"

    # ── UX ระหว่างรอ ────────────────────────────────────────────────────────

    async def show_loading(self, user_id: str, seconds: int = 20) -> None:
        """
        แสดงอนิเมชัน "กำลังพิมพ์" ในแชท 1-1

        เรียกก่อนงานที่ใช้เวลานาน (LLM / RAG) เพื่อไม่ให้ user คิดว่าบอทค้าง
        ล้มเหลวได้โดยไม่กระทบงานหลัก → จับ error แล้วปล่อยผ่าน
        """
        try:
            await self._post(
                "/chat/loading/start",
                {
                    "chatId": user_id,
                    "loadingSeconds": normalize_loading_seconds(seconds),
                },
            )
        except LineApiError as exc:
            log.debug("แสดง loading ไม่สำเร็จ (ไม่กระทบงานหลัก): %s", exc)

    # ── Rich Menu เฉพาะผู้ใช้ (สลับใบตามโหมดปรึกษา) ─────────────────────────

    async def link_rich_menu(self, user_id: str, menu_id: str) -> None:
        """
        ผูก rich menu ให้ผู้ใช้คนเดียว — **กลบเมนู default** ของบัญชีจนกว่า
        จะ :meth:`unlink_rich_menu`

        ใช้สลับเป็นใบโหมดปรึกษาเฉพาะคนที่อยู่ในโหมด (เรียกจาก
        ``app/main.py`` หลังส่งคำตอบสำเร็จ) ไม่ใช้ ``richmenuswitch`` action
        เพราะทางนั้นไม่ส่ง postback กลับ webhook = บันทึก ``chat_logs`` ไม่ได้

        พังแล้วยิง :class:`LineApiError` ออกไป — ผู้เรียกตัดสินใจเองว่าจะกลืน
        หรือปล่อย (เมนูไม่ขึ้นไม่ควรทำให้งานหลักพัง → ``app/main.py``
        ห่อ try/except ให้)
        """
        await self._post(f"/user/{user_id}/richmenu/{menu_id}", None)

    async def unlink_rich_menu(self, user_id: str) -> None:
        """
        เอาเมนูเฉพาะผู้ใช้ออก → ผู้ใช้กลับไปเห็นเมนู default ของบัญชี

        เรียกเมื่อออกจากโหมดปรึกษา (ปิด/timeout/ครบรอบ) — ถ้าผู้ใช้ไม่ได้
        link อยู่แล้ว การเรียกซ้ำก็ไม่เป็นไร (ฝั่งเราห่อ try/except ไว้)
        """
        await self._delete(f"/user/{user_id}/richmenu")

    # ── ข้อมูลบอท ───────────────────────────────────────────────────────────

    async def get_bot_info(self) -> dict:
        """
        ดึงข้อมูล LINE Official Account — ใช้ตรวจว่า access token ใช้ได้จริง

        เหมาะกับ health check ตอนสตาร์ท
        """
        response = await self._http.get(f"{API_BASE}/info", headers=self._headers)
        if response.status_code >= 400:
            raise LineApiError(response.status_code, response.text)
        return response.json()
