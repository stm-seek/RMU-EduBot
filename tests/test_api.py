"""
เทส ``/health`` และ API ของ LIFF

``/api/liff/login`` เป็นจุดที่ข้อมูลส่วนบุคคลเข้าระบบ จึงเทสตามแผน B ไว้ว่า:

* ต้องยืนยัน **ID token** กับ LINE (ห้ามเชื่อ ``userId`` ที่ client ส่งมา)
* คืนออกไปแค่ ``user_hash`` — **ห้ามมี ``line_user_id`` ดิบ** ในคำตอบ
* config ไม่ครบ → 503 (เซิร์ฟเวอร์ยังไม่พร้อม) ไม่ใช่ 401 (คุณไม่มีสิทธิ์)
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import main
from app.config import get_settings
from app.line.auth import hash_user_id

from .helpers import (
    TEST_LOGIN_CHANNEL_ID,
    TEST_PEPPER,
    TEST_USER_ID,
    Recorder,
    make_settings,
)

VALID_TOKEN = "eyJhbGciOiJIUzI1NiJ9.dGhpcy1pcy1hLWZha2UtdG9rZW4.signature"


def liff_settings(**overrides):
    return make_settings(
        liff_id="1234567890-abcdefgh",
        line_login_channel_id=TEST_LOGIN_CHANNEL_ID,
        **overrides,
    )


# ── /health ─────────────────────────────────────────────────────────────────


def test_health_reports_nothing_configured(make_client) -> None:
    """สถานะจริงตอน dev: มี DB + pepper แต่ยังไม่มี token/key ของ LINE และ LLM"""
    client = make_client(make_settings())
    body = client.get("/health").json()

    assert body["status"] == "ok"
    assert body["env"] == "development"
    assert body["program"] == "643170151"
    assert body["configured"] == {
        "line_messaging": False,
        "liff": False,
        "llm": False,
        "database": True,
        "user_hashing": True,
    }


def test_health_reports_everything_configured(make_client) -> None:
    client = make_client(
        liff_settings(
            line_channel_secret="s",
            line_channel_access_token="t",
            llm_api_key="k",
        )
    )
    assert client.get("/health").json()["configured"] == {
        "line_messaging": True,
        "liff": True,
        "llm": True,
        "database": True,
        "user_hashing": True,
    }


def test_health_reports_database_check_separately(make_client) -> None:
    """
    ``configured.database`` = ตั้ง ``DATABASE_URL`` แล้วหรือยัง
    ``checks.database`` = ต่อได้จริงไหม

    แยกกันเพราะสองอย่างนี้ต่างกันจริง: ตั้ง URL ไว้แต่ DB ล่ม ต้องรู้ว่าล่ม
    ไม่ใช่เข้าใจผิดว่าลืมตั้งค่า (เจอจริงตอน dev เพราะ Docker ยังรันไม่ได้)
    """
    client = make_client(make_settings())
    body = client.get("/health").json()

    assert body["configured"]["database"] is True
    assert body["checks"]["database"] == "unreachable"


def test_health_says_not_configured_without_database_url(make_client) -> None:
    client = make_client(make_settings(database_url=""))
    body = client.get("/health").json()

    assert body["configured"]["database"] is False
    assert body["checks"]["database"] == "not_configured"


def test_health_reports_ok_when_database_answers(make_client, monkeypatch) -> None:
    """ต่อได้จริง → ``ok`` (จำลอง pool ที่เปิดอยู่ด้วย fake)"""

    class HealthyDatabase:
        async def healthy(self) -> bool:
            return True

    monkeypatch.setattr(main, "_db", HealthyDatabase())
    client = make_client(make_settings())

    assert client.get("/health").json()["checks"]["database"] == "ok"


def test_health_needs_both_secret_and_token_for_messaging(make_client) -> None:
    """มี secret แต่ไม่มี token = ยังตอบข้อความไม่ได้ → ต้องรายงานว่า False"""
    client = make_client(make_settings(line_channel_secret="s"))
    assert client.get("/health").json()["configured"]["line_messaging"] is False


def test_health_never_leaks_secret_values(make_client) -> None:
    """
    ``/health`` เปิดสาธารณะ (tunnel ก็เข้าถึงได้) — ต้องบอกแค่ "ตั้งแล้ว/ยังไม่ตั้ง"
    ห้ามคืนค่าจริงออกไป
    """
    secrets = {
        "line_channel_secret": "SECRET-VALUE-1",
        "line_channel_access_token": "SECRET-VALUE-2",
        "llm_api_key": "SECRET-VALUE-3",
        "user_id_pepper": "SECRET-VALUE-4-อย่างน้อยสามสิบสองตัวอักษรนะครับ",
        "database_url": "postgresql://user:SECRET-VALUE-5@host/db",
    }
    client = make_client(make_settings(**secrets))
    text = client.get("/health").text

    for value in secrets.values():
        assert value not in text


def test_health_exposes_llm_settings_for_debugging(make_client) -> None:
    """base_url/model ไม่ใช่ความลับ และช่วยตรวจว่าชี้ provider ถูกตัว"""
    client = make_client(make_settings())
    llm = client.get("/health").json()["llm"]

    assert llm["base_url"].startswith("https://")
    assert llm["model"]
    assert isinstance(llm["embedding_dim"], int)


# ── /api/liff/config ────────────────────────────────────────────────────────


def test_liff_config_returns_public_values(make_client) -> None:
    """LIFF ID ไม่ใช่ secret (ต้องใส่ใน HTML อยู่แล้ว) — คืนได้"""
    client = make_client(liff_settings())
    body = client.get("/api/liff/config").json()

    assert body == {"liff_id": "1234567890-abcdefgh", "program_code": "643170151"}


# ── /api/liff/login ─────────────────────────────────────────────────────────


def test_login_rejects_too_short_token(make_client) -> None:
    """
    ``id_token`` สั้นกว่า 16 ตัวไม่ใช่ JWT แน่นอน → 422 โดยไม่ต้องถาม LINE
    """
    client = make_client(liff_settings())
    assert client.post("/api/liff/login", json={"id_token": "สั้น"}).status_code == 422


def test_login_rejects_missing_field(make_client) -> None:
    client = make_client(liff_settings())
    assert client.post("/api/liff/login", json={}).status_code == 422


def test_login_returns_503_when_channel_id_missing(make_client) -> None:
    """
    config ไม่ครบเป็นความผิดของเซิร์ฟเวอร์ ไม่ใช่ของผู้ใช้
    → 503 พร้อมบอกชื่อตัวแปรที่ต้องตั้งใน .env
    """
    client = make_client(make_settings())
    response = client.post("/api/liff/login", json={"id_token": VALID_TOKEN})

    assert response.status_code == 503
    assert "LINE_LOGIN_CHANNEL_ID" in response.json()["detail"]


def test_login_returns_401_when_line_rejects_token(make_client) -> None:
    recorder = Recorder((400, {"error_description": "JWS format error"}))
    client = make_client(liff_settings(), recorder.client())

    response = client.post("/api/liff/login", json={"id_token": VALID_TOKEN})

    assert response.status_code == 401
    assert recorder.count == 1


def test_login_succeeds_and_returns_only_a_hash(make_client) -> None:
    """
    PDPA / data minimization: คืน ``user_hash`` เท่านั้น
    ห้ามมี ``line_user_id`` ดิบหลุดออกไปในคำตอบ
    """
    recorder = Recorder(
        (200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID, "name": "สมชาย"})
    )
    client = make_client(liff_settings(), recorder.client())

    response = client.post("/api/liff/login", json={"id_token": VALID_TOKEN})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["user_hash"] == hash_user_id(TEST_USER_ID, TEST_PEPPER)
    assert TEST_USER_ID not in response.text


def test_login_verifies_token_with_line(make_client) -> None:
    """ยืนยันว่าไปถาม LINE จริง ไม่ได้เชื่อค่าที่ client ส่งมา"""
    recorder = Recorder((200, {"sub": TEST_USER_ID}))
    client = make_client(liff_settings(), recorder.client())

    client.post("/api/liff/login", json={"id_token": VALID_TOKEN})

    assert str(recorder.requests[0].url) == "https://api.line.me/oauth2/v2.1/verify"
    assert VALID_TOKEN in recorder.text_body()


# ── lifespan ────────────────────────────────────────────────────────────────


def test_lifespan_opens_and_closes_http_client(monkeypatch) -> None:
    """
    รัน startup/shutdown จริง — ยืนยันว่า httpx client ถูกสร้างและถูกปิด

    ตัวนี้เป็นเทสเดียวที่เข้า ``with TestClient(...)`` เพราะ lifespan
    เรียก ``_configure_logging()`` ซึ่งเปลี่ยน handler ของ root logger
    (fixture ``restore_root_logging`` ใน conftest คืนค่าให้หลังจบเทส)
    """
    settings = make_settings()
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    main.app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(main.app) as client:
            assert main._http is not None
            assert client.get("/health").status_code == 200
    finally:
        main.app.dependency_overrides.clear()

    assert main._http is None, "ต้องปิด client ตอน shutdown ไม่ปล่อยค้าง"
