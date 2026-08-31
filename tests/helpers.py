"""
เครื่องมือช่วยเทส — ไม่ใช่ fixture (ดู :mod:`tests.conftest` สำหรับ fixture)

หลักการของชุดเทสนี้:

1. **ไม่ยิงเน็ตเวิร์กจริงเลย** — LINE API / LLM API ถูกแทนด้วย
   ``httpx.MockTransport`` (เครื่องนี้ไม่มี ``respx`` และไม่จำเป็นต้องมี)
2. **ไม่อ่าน ``.env`` ของเครื่องที่รันเทส** — ถ้าอ่าน เทสจะผ่านบนเครื่อง dev
   แต่พังบน CI (หรือกลับกัน) เพราะ secret ไม่เหมือนกัน
3. ตรวจ **ข้อจำกัดของ LINE** ทุกครั้งที่ router สร้างข้อความ เพราะถ้าเกิน limit
   LINE จะ reject ทั้ง request ไม่ใช่ตัดให้เอง → user ไม่ได้คำตอบเลย
"""

from __future__ import annotations

import json

import httpx

from app.config import Settings
from app.line import flex
from app.line import messages as msg

# ── ค่าคงที่สำหรับเทส (ห้ามใช้ค่าจริง) ────────────────────────────────────────

TEST_CHANNEL_SECRET = "test_channel_secret"
TEST_ACCESS_TOKEN = "test_access_token"
TEST_LOGIN_CHANNEL_ID = "1234567890"
TEST_PEPPER = "test-pepper-value-long-enough-for-production-check"
TEST_USER_ID = "U4af4980629474f753dfb1d4e58b9c4b1"
TEST_REPLY_TOKEN = "0f3779fba3b349968c5d07db31eab56f"


def make_settings(**overrides) -> Settings:
    """
    สร้าง :class:`Settings` จากค่าคงที่

    ``_env_file=None`` ปิดการอ่าน ``.env`` ส่วนค่าที่ส่งเข้า ``__init__``
    มีลำดับความสำคัญสูงกว่า environment variable อยู่แล้ว → deterministic

    ค่า default ตรงกับสถานะจริงตอน dev: มี channel secret (เทส signature ได้)
    แต่ **ยังไม่มี access token / LLM key** เพื่อให้เทสยืนยันว่าระบบ
    ไม่พังเมื่อ config ไม่ครบ
    """
    values: dict = {
        "app_env": "development",
        "log_level": "DEBUG",
        "database_url": "postgresql://test:test@127.0.0.1:5432/test_db",
        "line_channel_secret": TEST_CHANNEL_SECRET,
        "line_channel_access_token": "",
        "liff_id": "",
        "line_login_channel_id": "",
        "llm_api_key": "",
        "embedding_api_key": "",
        "user_id_pepper": TEST_PEPPER,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


# ── mock HTTP ────────────────────────────────────────────────────────────────


def refuse_all(request: httpx.Request) -> httpx.Response:
    """handler default — เทสที่ไม่ควรยิง HTTP ออกไปจะ fail ทันทีถ้ายิง"""
    raise AssertionError(
        f"เทสนี้ไม่ควรเรียก HTTP ภายนอก แต่เรียก {request.method} {request.url}"
    )


class Recorder:
    """
    บันทึก request ที่ยิงออกไป และตอบตาม response ที่กำหนดไว้ล่วงหน้า

    ตอบตามลำดับ: request ที่ 1 ได้ response ที่ 1, ที่ 2 ได้ที่ 2 ...
    ถ้า request มากกว่า response ที่ให้ไว้ จะใช้ตัวสุดท้ายซ้ำ
    (สะดวกตอนเทส retry ที่ต้องสำเร็จตั้งแต่ครั้งที่ 2 เป็นต้นไป)

    >>> rec = Recorder((200, {'ok': True}))
    >>> rec.requests
    []
    """

    def __init__(self, *responses: tuple[int, dict | str]) -> None:
        self._responses: list[tuple[int, dict | str]] = list(responses) or [(200, {})]
        self.requests: list[httpx.Request] = []

    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=httpx.MockTransport(self._handle))

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        index = min(len(self.requests) - 1, len(self._responses) - 1)
        status, body = self._responses[index]
        if isinstance(body, str):
            return httpx.Response(status, text=body)
        return httpx.Response(status, json=body)

    # ── ตัวช่วยอ่านสิ่งที่ถูกส่งออกไป ───────────────────────────────────────

    @property
    def count(self) -> int:
        return len(self.requests)

    def paths(self) -> list[str]:
        return [request.url.path for request in self.requests]

    def json_body(self, index: int = 0) -> dict:
        return json.loads(self.requests[index].content)

    def text_body(self, index: int = 0) -> str:
        return self.requests[index].content.decode("utf-8")


# ── mock ฐานข้อมูล ───────────────────────────────────────────────────────────


class FakeDatabase:
    """
    ฐานข้อมูลปลอมที่ทำตาม :class:`app.db.SupportsQuery`

    Postgres ยังรันบนเครื่อง dev ไม่ได้ (Docker ติด WSL2) — ตัวนี้ให้เทส
    ชั้น repository/router ได้ครบ โดยแยกสองเรื่องออกจากกัน:

    * **SQL ถูกไหม** → เทสด้วย ``sqlglot`` + เทียบชื่อตารางกับ migration
      (ดู :mod:`tests.test_repository`)
    * **เอาผลลัพธ์ไปแสดงถูกไหม** → เทสด้วยคลาสนี้

    ``rules`` จับคู่ด้วย substring ของ SQL และ **เรียงตามลำดับที่ใส่**
    → ใส่ตัวที่เฉพาะเจาะจงกว่าไว้ก่อน

    >>> db = FakeDatabase({'FROM documents': [{'title': 'ก'}]})
    >>> import asyncio; asyncio.run(db.fetch_all('SELECT * FROM documents'))
    [{'title': 'ก'}]
    >>> asyncio.run(db.fetch_all('SELECT * FROM courses'))
    []
    """

    def __init__(self, rules: dict[str, list[dict] | dict | None] | None = None) -> None:
        self.rules = rules or {}
        self.calls: list[tuple[str, tuple | None]] = []

    async def fetch_all(self, sql: str, params=None) -> list[dict]:
        self.calls.append((sql, params))
        value = self._match(sql)
        if value is None:
            return []
        return list(value) if isinstance(value, list) else [value]

    async def fetch_one(self, sql: str, params=None) -> dict | None:
        self.calls.append((sql, params))
        value = self._match(sql)
        if isinstance(value, list):
            return value[0] if value else None
        return value

    def _match(self, sql: str):
        for needle, value in self.rules.items():
            if needle in sql:
                return value
        return None

    # ── ตัวช่วยตรวจว่าถูกเรียกด้วยอะไร ──────────────────────────────────────

    @property
    def count(self) -> int:
        return len(self.calls)

    def params_for(self, needle: str) -> tuple | None:
        """params ของ query แรกที่มี ``needle`` อยู่ใน SQL"""
        for sql, params in self.calls:
            if needle in sql:
                return params
        raise AssertionError(f"ไม่มี query ที่มี {needle!r} ถูกเรียก")


class FakeWriteDatabase(FakeDatabase):
    """
    :class:`FakeDatabase` ที่รองรับ **ทางเขียน** (``execute``) ด้วย

    ใช้เทส ``chat_logs`` / ``app_users`` โดยไม่ต้องมี Postgres จริง
    บันทึกทุก execute ไว้ให้เทสตรวจว่า SQL/params ถูกต้อง
    """

    def __init__(
        self, rules: dict[str, list[dict] | dict | None] | None = None
    ) -> None:
        super().__init__(rules)
        self.executed: list[tuple[str, tuple | None]] = []

    async def execute(self, sql: str, params=None) -> int:
        self.executed.append((sql, params))
        return 1

    def executed_for(self, needle: str) -> tuple | None:
        """params ของ execute แรกที่มี ``needle`` อยู่ใน SQL"""
        for sql, params in self.executed:
            if needle in sql:
                return params
        raise AssertionError(f"ไม่มี execute ที่มี {needle!r} ถูกเรียก")


# ── ตรวจข้อจำกัดของ LINE ─────────────────────────────────────────────────────


def assert_line_limits(messages: list[dict]) -> None:
    """
    ตรวจว่าชุดข้อความไม่ละเมิด limit ของ LINE

    ใช้กับผลลัพธ์ของ router ทุกทาง — ถ้าวันหนึ่งมีใครเพิ่มปุ่มที่ 14
    หรือเขียน label ยาว 25 ตัว เทสจะจับได้ก่อนขึ้น production
    """
    assert messages, "ต้องมีข้อความอย่างน้อย 1 ข้อความ"
    assert len(messages) <= msg.MAX_MESSAGES_PER_REPLY, (
        f"ส่งได้สูงสุด {msg.MAX_MESSAGES_PER_REPLY} ข้อความ (ได้ {len(messages)})"
    )

    for message in messages:
        assert message.get("type"), f"message ไม่มี field 'type': {message!r}"

        if message["type"] == "text":
            assert message["text"], "text message ว่างไม่ได้"
            assert len(message["text"]) <= msg.MAX_TEXT_LENGTH

        if message["type"] == "flex":
            _assert_flex_limits(message)

        quick = message.get("quickReply")
        if quick is None:
            continue

        items = quick["items"]
        assert len(items) <= msg.MAX_QUICK_REPLY_ITEMS
        for item in items:
            assert item["type"] == "action"
            action = item["action"]
            assert len(action["label"]) <= msg.MAX_LABEL_LENGTH
            if action["type"] == "postback":
                assert len(action["data"]) <= msg.MAX_POSTBACK_DATA_LENGTH


def _assert_flex_limits(message: dict) -> None:
    """
    ข้อจำกัดของ Flex Message ที่ถ้าผิด LINE จะ reject ทั้ง request

    * ``altText`` ต้องมีและยาวไม่เกิน 400 ตัวอักษร
    * ``action`` แบบ ``uri`` — ยาวไม่เกิน 1,000 ตัวอักษร และต้องเป็น ``https``
      (แตะแล้วเปิดไม่ได้ = จุดประสงค์ของแถวเสียทั้งแถว)
    * ``action`` แบบ ``postback`` — ``data`` ยาวไม่เกินเพดานเดียวกับ Quick Reply

    ไม่บังคับว่าทุกฟองต้องมี action เพราะฟองรายชื่ออาจารย์ตั้งใจไม่ให้กดได้
    (ยังไม่มีลิงก์ต่อคน และ ``mailto:`` ไม่อยู่ใน scheme ที่ LINE รับ)
    """
    alt_text = message.get("altText")
    assert alt_text, "flex message ต้องมี altText (ข้อความในรายการแชท)"
    assert len(alt_text) <= flex.MAX_ALT_TEXT_LENGTH

    contents = message.get("contents") or {}
    for action in _iter_actions(contents):
        assert action["type"] in ("uri", "postback"), (
            f"action ชนิด {action['type']!r} ยังไม่ได้ตรวจในเทส"
        )
        assert len(action["label"]) <= msg.MAX_LABEL_LENGTH
        if action["type"] == "uri":
            assert len(action["uri"]) <= flex.MAX_URI_LENGTH
            assert action["uri"].startswith("https://"), (
                f"ลิงก์ในฟองต้องเป็น https: {action['uri'][:60]}"
            )
        else:
            assert len(action["data"]) <= msg.MAX_POSTBACK_DATA_LENGTH


def flex_texts(message: dict) -> list[str]:
    """
    ข้อความทุกชิ้นในฟอง เรียงตามที่ผู้ใช้เห็นจากบนลงล่าง

    เทสของคำตอบที่ย้ายจากข้อความมาเป็น Flex ใช้ตัวนี้แทนการอ่าน
    ``message["text"]`` — เนื้อหาที่ต้องมีก็ยังตรวจได้เหมือนเดิม
    """
    return _iter_texts(message.get("contents") or {})


def flex_body_text(message: dict) -> str:
    """รวมข้อความทั้งฟองเป็นก้อนเดียว — สะดวกกับการเช็ค ``in``"""
    return chr(10).join(flex_texts(message))


def flex_uris(message: dict) -> list[str]:
    """ลิงก์ทุกเส้นในฟอง — URL ย้ายไปอยู่ใน action แล้ว ไม่ได้พิมพ์เป็นข้อความ"""
    return [
        action["uri"]
        for action in _iter_actions(message.get("contents") or {})
        if action["type"] == "uri"
    ]


def _iter_texts(node: dict) -> list[str]:
    texts: list[str] = []
    if node.get("type") == "text" and node.get("text"):
        texts.append(str(node["text"]))
    for child in node.get("contents", []) or []:
        texts.extend(_iter_texts(child))
    for part in ("header", "hero", "body", "footer"):
        if node.get(part):
            texts.extend(_iter_texts(node[part]))
    return texts



def _iter_actions(node: dict) -> list[dict]:
    """เดินโครงสร้างฟองเก็บทุก action — ทั้งปุ่ม (``button``) และกล่องที่มี
    ``action`` ตั้งตรง ๆ (แถวเอกสารแตะเปิดทั้งแถว)"""
    actions: list[dict] = []
    if node.get("action") and node.get("type") in ("button", "icon", "image", "box"):
        actions.append(node["action"])
    for child in node.get("contents", []) or []:
        actions.extend(_iter_actions(child))
    for part in ("header", "hero", "body", "footer"):
        if node.get(part):
            actions.extend(_iter_actions(node[part]))
    return actions
