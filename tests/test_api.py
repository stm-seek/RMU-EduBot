"""
เทส ``/health`` และ API ของ LIFF

``/api/liff/login`` เป็นจุดที่ข้อมูลส่วนบุคคลเข้าระบบ จึงเทสตามแผน B ไว้ว่า:

* ต้องยืนยัน **ID token** กับ LINE (ห้ามเชื่อ ``userId`` ที่ client ส่งมา)
* คืนออกไปแค่ ``user_hash`` — **ห้ามมี ``line_user_id`` ดิบ** ในคำตอบ
* config ไม่ครบ → 503 (เซิร์ฟเวอร์ยังไม่พร้อม) ไม่ใช่ 401 (คุณไม่มีสิทธิ์)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import get_settings
from app.line.auth import hash_user_id

from .helpers import (
    TEST_LOGIN_CHANNEL_ID,
    TEST_PEPPER,
    TEST_USER_ID,
    FakeWriteDatabase,
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

    assert body == {
        "liff_id": "1234567890-abcdefgh",
        "program_code": "643170151",
        # หน้าเว็บบอกผู้ใช้ว่าเพดานหน่วยกิตที่ระบบใช้คิดคือเท่าไร
        "max_credits_per_term": 22,
    }


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


# ── LIFF: หน้าเว็บ + ติ๊กวิชาที่ผ่าน ──────────────────────────────────────────


PLAN_ROWS = [
    {
        "course_code": "7071101",
        "course_code_full": "7071101-3",
        "std_year": 1,
        "std_semester": 1,
        "credits": 3,
        "credits_text": "3 (2-2-5)",
        "name_th": "พื้นฐานเทคโนโลยีสารสนเทศ",
        "note": None,
        "group_code": "2.1",
    },
    # วิชาเลือก: ``std_year``/``std_semester`` เป็น NULL ใน DB จริง (นักศึกษา
    # ลงเทอมไหนก็ได้) — ต้องมีในชุดทดสอบ ไม่งั้นเทสจะไม่เจอกรณี "ปี 0 เทอม 0"
    {
        "course_code": "7073312",
        "course_code_full": "7073312-3",
        "std_year": None,
        "std_semester": None,
        "credits": 3,
        "credits_text": "3 (2-2-5)",
        "name_th": "การเขียนโปรแกรมบนอุปกรณ์เคลื่อนที่",
        "note": None,
        "group_code": "2.2",
    },
]

# โควตารายหมวด — เรียงตาม ``sort_order`` เหมือนที่ SQL คืนมาจริง
#
# หมวด 3.1 ไม่มีวิชาใน ``curriculum_rules`` ชี้มาโดยเจตนา (เลือกเสรีลงคณะไหน
# ก็ได้) จึงเป็นหมวดเดียวที่ ``passed_credits`` มาจากตัวเลขที่ผู้ใช้กรอกเอง
GROUP_ROWS = [
    {
        "group_code": "2.1",
        "group_label": "วิชาเฉพาะด้าน (บังคับ)",
        "required_credits": 54,
        "is_choice": False,
        "sort_order": 60,
    },
    {
        "group_code": "2.2",
        "group_label": "วิชาเฉพาะด้าน (เลือก)",
        "required_credits": 18,
        "is_choice": True,
        "sort_order": 70,
    },
    {
        "group_code": "3.1",
        "group_label": "วิชาเลือกเสรี",
        "required_credits": 6,
        "is_choice": True,
        "sort_order": 90,
    },
]


def liff_db(
    passed: list[str] | None = None,
    *,
    free_elective_credits: int = 0,
    plan_rows: list[dict] | None = None,
    group_rows: list[dict] | None = None,
) -> FakeWriteDatabase:
    """FakeWriteDatabase ที่ตอบครบทุกคิวรีของ ``/api/liff/*``"""
    done = passed or []
    return FakeWriteDatabase(
        {
            "INSERT INTO app_users": {"id": 42},
            "FROM app_users u": {
                "id": 42,
                "program_code": "643170151",
                "study_year": 1,
                "entry_year": 2564,
                "completed_courses": len(done),
                "free_elective_credits": free_elective_credits,
            },
            "FROM curriculum_rules cr": (
                PLAN_ROWS if plan_rows is None else plan_rows
            ),
            "FROM curriculum_groups": (
                GROUP_ROWS if group_rows is None else group_rows
            ),
            "FROM prerequisites p": [],
            "FROM user_completed_courses": [{"course_code": c} for c in done],
            "FROM programs": {
                "program_code": "643170151",
                "program_name": "การจัดการนวัตกรรมดิจิทัล",
                "total_credits": 120,
            },
            "WITH incoming": {"removed": 0, "added": len(done)},
        }
    )


def test_liff_page_is_served_without_secrets(make_client) -> None:
    """หน้า LIFF ต้องไม่ฝัง LIFF ID หรือ secret ไว้ในไฟล์ (อ่านจาก API ตอนรัน)"""
    client = make_client(liff_settings())
    response = client.get("/liff")

    assert response.status_code == 200
    assert "static.line-scdn.net/liff/edge/2/sdk.js" in response.text
    assert "1234567890-abcdefgh" not in response.text
    assert "getIDToken" in response.text, "ต้องส่ง ID token ไม่ใช่ userId"


def test_liff_page_keeps_the_elective_contract(make_client) -> None:
    """
    ข้อตกลงของหน้า LIFF ที่ regression ได้ง่ายที่สุด — ล็อกไว้ที่ระดับไฟล์

    * วิชาเลือกอยู่ใน ``<details>`` และ **ไม่มี** ``open`` (หมวดเดียวมีถึง 29
      วิชา เปิดค้างแล้วผู้ใช้เลื่อนหาวิชาบังคับไม่เจอ)
    * ช่องเลือกเสรีต้องคุมช่วง 0–60 ที่ตัว input ด้วย ไม่ใช่รอ 422 จาก backend
    * คำว่า "ปี 0 / เทอม 0" ห้ามโผล่เลย แม้แต่ในคอมเมนต์ (วิชาเลือกไม่มีเทอม)
    * ไลบรารีภายนอกมีได้ตัวเดียวคือ LIFF SDK
    """
    client = make_client(liff_settings())
    page = client.get("/liff").text

    assert 'createElement("details")' in page, "วิชาเลือกต้องอยู่ในกล่องพับได้"
    assert 'createElement("summary")' in page
    # เปิดเฉพาะตอนค้นหาเจอ — ไม่มีบรรทัดไหนตั้ง open = true แบบไม่มีเงื่อนไข
    assert "box.open = query" in page
    assert 'type="search"' in page, "ต้องมีช่องค้นหาวิชาเลือก"
    assert 'type="number" id="free" min="0" max="60"' in page
    assert "ปี 0" not in page and "เทอม 0" not in page
    assert page.count("<script src=") == 1
    # ตัวเลขทุกตัวมาจาก backend — คีย์เหล่านี้คือทางเดียวที่หน้าเว็บได้ตัวเลขมา
    for key in ("counted_credits", "free_elective_credits", "percent_complete"):
        assert key in page
    assert "localStorage.setItem" not in page and "sessionStorage.setItem" not in page


def test_liff_line_me_link_lands_on_the_page_it_asked_for(make_client) -> None:
    """
    ลิงก์ ``liff.line.me/<id>/admin`` มาถึงเราเป็น ``/?liff.state=%2Fadmin``

    ก่อนมีเราท์นี้ รากเป็น 404 → คนกดลิงก์เห็นแค่ ``{"detail":"Not Found"}``
    """
    client = make_client(liff_settings())

    response = client.get(
        "/", params={"liff.state": "/admin"}, follow_redirects=False
    )

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/admin"


def test_login_code_is_carried_over_to_the_target_page(make_client) -> None:
    """``code``/``state`` หายไป = หน้าปลายทางเริ่มล็อกอินใหม่เป็นวงไม่จบ"""
    client = make_client(liff_settings())

    response = client.get(
        "/",
        params={"liff.state": "/liff?tab=done", "code": "abc123", "state": "xyz"},
        follow_redirects=False,
    )

    location = response.headers["location"]
    assert location.startswith("/liff?")
    for expected in ("tab=done", "code=abc123", "state=xyz"):
        assert expected in location


def test_liff_state_cannot_point_off_site(make_client) -> None:
    """
    query string ปลอมได้ ถ้าเด้งตามที่บอกจะได้ open redirect —
    ลิงก์โดเมนเราที่พาไปเว็บหลอกลวง (น่าเชื่อกว่าลิงก์แปลกหน้ามาก)
    """
    client = make_client(liff_settings())

    for evil in ("https://evil.example/steal", "//evil.example", "/../admin"):
        response = client.get(
            "/", params={"liff.state": evil}, follow_redirects=False
        )
        assert response.status_code == 404, evil
        assert "location" not in response.headers


def test_double_encoded_liff_state_still_lands_on_the_page(make_client) -> None:
    """
    บางเส้นทาง LINE ส่ง ``liff.state`` มา encode ซ้อนสองชั้น

    เห็นจาก ``liffRedirectUri`` ที่ LINE แนบมาเองว่าเป็น ``%252Fadmin`` — parse
    query string ถอดให้ชั้นเดียวเหลือ ``%2Fadmin`` ซึ่งเทียบ allowlist ไม่ผ่าน
    แล้วกลายเป็น 404 ทั้งที่ปลายทางถูกต้อง
    """
    client = make_client(liff_settings())

    response = client.get(
        "/", params={"liff.state": "%2Fadmin"}, follow_redirects=False
    )

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/admin"


def test_decoding_liff_state_does_not_allow_going_off_site(make_client) -> None:
    """
    ถอด encoding ไม่ใช่การอนุญาต — ค่าที่ถอดแล้วต้องผ่าน allowlist เหมือนกัน

    ไม่มีเทสตัวนี้ การถอดชั้นที่สองจะกลายเป็นทางอ้อมรอบ allowlist ทันที
    """
    client = make_client(liff_settings())

    for evil in ("%2F%2Fevil.example", "https%3A%2F%2Fevil.example%2Fsteal"):
        response = client.get(
            "/", params={"liff.state": evil}, follow_redirects=False
        )

        assert response.status_code == 404, evil
        assert "location" not in response.headers


def test_opening_the_bare_domain_says_the_server_is_up(make_client) -> None:
    """
    ไม่มี ``liff.state`` = ไม่รู้ว่าอยากไปไหน แต่ต้องไม่ทำให้คนคิดว่าเซิร์ฟเวอร์พัง

    เดิมตอบ 404 เป็น JSON แล้วคนตั้งระบบไปไล่แก้ tunnel/webhook ทั้งที่ไม่มี
    อะไรพัง — และยังต้อง**ไม่บอกว่ามีหน้า /admin อยู่**
    """
    client = make_client(liff_settings())

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 200
    assert "admin" not in response.text.lower()


def test_liff_state_requires_database(make_client) -> None:
    """ไม่มี DB = ยังเก็บ/อ่านข้อมูลไม่ได้ → 503 (ปัญหาของเซิร์ฟเวอร์)"""
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    client = make_client(liff_settings(), recorder.client())

    response = client.post("/api/liff/state", json={"id_token": VALID_TOKEN})

    assert response.status_code == 503


def test_liff_state_returns_plan_and_progress(make_client, monkeypatch) -> None:
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(main, "_db", liff_db(["7071101"]))
    client = make_client(liff_settings(), recorder.client())

    body = client.post("/api/liff/state", json={"id_token": VALID_TOKEN}).json()

    assert body["program_code"] == "643170151"
    assert body["plan"][0]["course_code"] == "7071101"
    assert body["plan"][0]["passed"] is True
    assert body["progress"]["passed_credits"] == 3
    assert body["progress"]["prereq_known"] is False


def test_liff_state_never_returns_raw_line_user_id(make_client, monkeypatch) -> None:
    """PDPA: ข้อมูลที่คืนออกไปห้ามมี ``line_user_id`` ดิบ"""
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(main, "_db", liff_db())
    client = make_client(liff_settings(), recorder.client())

    response = client.post("/api/liff/state", json={"id_token": VALID_TOKEN})

    assert TEST_USER_ID not in response.text


def test_liff_state_rejects_bad_token(make_client, monkeypatch) -> None:
    recorder = Recorder((400, {"error_description": "JWS format error"}))
    monkeypatch.setattr(main, "_db", liff_db())
    client = make_client(liff_settings(), recorder.client())

    response = client.post("/api/liff/state", json={"id_token": VALID_TOKEN})

    assert response.status_code == 401


def test_saving_completed_courses_ignores_codes_outside_the_plan(
    make_client, monkeypatch
) -> None:
    """
    รหัสที่ไม่อยู่ในหลักสูตรต้องไม่เข้าตาราง

    หน้าเว็บส่งอะไรมาก็ได้ (แก้ JS ได้) — ถ้าไม่กรอง ตารางจะมีรหัสมั่ว
    แล้ว planner นับหน่วยกิตจากขยะนั้น
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    database = liff_db(["7071101"])
    monkeypatch.setattr(main, "_db", database)
    client = make_client(liff_settings(), recorder.client())

    body = client.post(
        "/api/liff/completed_courses",
        json={"id_token": VALID_TOKEN, "course_codes": ["7071101", "9999999"]},
    ).json()

    assert body["success"] is True
    assert body["saved"] == 1
    assert body["rejected"] == ["9999999"]
    assert database.params_for("WITH incoming")[0] == ["7071101"]


def test_saving_accepts_an_empty_selection(make_client, monkeypatch) -> None:
    """เอาติ๊กออกหมด = ล้างข้อมูล ต้องทำได้ (ไม่ใช่ error)"""
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(main, "_db", liff_db())
    client = make_client(liff_settings(), recorder.client())

    response = client.post(
        "/api/liff/completed_courses",
        json={"id_token": VALID_TOKEN, "course_codes": []},
    )

    assert response.status_code == 200
    assert response.json()["saved"] == 0


# ── LIFF: หมวดวิชาเลือก + เลือกเสรี ──────────────────────────────────────────
#
# ทำไมต้องเทสเยอะกับ payload ชุดนี้: หน้าเว็บ **ห้ามคิดเลขเอง** ตัวเลขทุกตัว
# ที่ผู้ใช้เห็นจึงมีที่มาเดียวคือคีย์เหล่านี้ ถ้าคีย์หายหรือความหมายเปลี่ยน
# หน้าเว็บจะแสดง ``undefined`` แบบไม่มีใครรู้จนผู้ใช้บ่น


def state_of(client, body_extra: dict | None = None) -> dict:
    return client.post(
        "/api/liff/state", json={"id_token": VALID_TOKEN, **(body_extra or {})}
    ).json()


def test_liff_state_reports_progress_per_group(make_client, monkeypatch) -> None:
    """หมวดต้องมาครบทุกคีย์ และเรียงตาม ``sort_order`` ที่ planner ให้มา"""
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(main, "_db", liff_db(["7071101"]))
    client = make_client(liff_settings(), recorder.client())

    groups = state_of(client)["progress"]["groups"]

    assert [g["group_code"] for g in groups] == ["2.1", "2.2", "3.1"]
    assert [g["sort_order"] for g in groups] == [60, 70, 90]
    assert groups[0] == {
        "group_code": "2.1",
        "group_label": "วิชาเฉพาะด้าน (บังคับ)",
        "required_credits": 54,
        "passed_credits": 3,
        "counted_credits": 3,
        "is_choice": False,
        "complete": False,
        "percent": 5.6,
        "sort_order": 60,
    }


def test_free_elective_group_gets_its_credits_from_the_user(
    make_client, monkeypatch
) -> None:
    """
    หมวดเลือกเสรีไม่มีวิชาให้ติ๊ก — ต้องรับตัวเลขที่ผู้ใช้กรอกเอง

    ถ้าไปนับจากวิชาที่ติ๊กเหมือนหมวดอื่น หมวดนี้จะค้าง 0% ตลอดชีวิตและ
    เปอร์เซ็นต์รวมจะไม่มีวันถึง 100 ทั้งที่นักศึกษาจบได้แล้ว
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(main, "_db", liff_db([], free_elective_credits=6))
    client = make_client(liff_settings(), recorder.client())

    progress = state_of(client)["progress"]
    free = [g for g in progress["groups"] if g["group_code"] == "3.1"][0]

    assert progress["free_elective_credits"] == 6
    assert free["passed_credits"] == 6
    assert free["complete"] is True
    assert free["percent"] == 100.0
    # ไม่ได้ติ๊กวิชาไหนเลย แต่หมวดเลือกเสรีนับให้ 6 → counted ต้องไม่ใช่ 0
    assert progress["passed_credits"] == 0
    assert progress["counted_credits"] == 6


def test_counted_credits_caps_at_the_quota_of_each_group(
    make_client, monkeypatch
) -> None:
    """
    เก็บเกินโควตาไม่ทำให้จบเร็วขึ้น — เพดานต้องมาจาก planner ไม่ใช่หน้าเว็บ

    กรอกเลือกเสรี 60 นก. (สุดขอบที่ฟอร์มยอมรับ) กับโควตา 6 → นับให้ 6
    ``counted_credits`` รวมจึงเป็น 3 (2.1) + 3 (2.2) + 6 (3.1) = 12
    ขณะที่ ``passed_credits`` ดิบยังเป็น 6 ตามวิชาที่ติ๊กจริงสองตัว
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(
        main, "_db", liff_db(["7071101", "7073312"], free_elective_credits=60)
    )
    client = make_client(liff_settings(), recorder.client())

    progress = state_of(client)["progress"]
    free = [g for g in progress["groups"] if g["group_code"] == "3.1"][0]

    assert free["passed_credits"] == 60 and free["counted_credits"] == 6
    assert progress["passed_credits"] == 6
    assert progress["counted_credits"] == 12
    assert progress["percent_complete"] == 10.0
    assert progress["credits_left_to_graduate"] == 108


def test_plan_rows_carry_the_group_label_for_electives(make_client, monkeypatch) -> None:
    """
    วิชาเลือกต้องมีชื่อหมวดติดมาด้วย ไม่ใช่แค่รหัสหมวด

    หน้าเว็บจัดกลุ่มวิชาเลือกตามหมวด (ไม่มีปี/เทอมให้จัด) ถ้าส่งมาแค่ ``'2.2'``
    หน้าเว็บต้องมีตารางแปลรหัสของตัวเอง = ข้อมูลเดียวกันสองที่
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(main, "_db", liff_db())
    client = make_client(liff_settings(), recorder.client())

    plan = state_of(client)["plan"]
    elective = [c for c in plan if c["course_code"] == "7073312"][0]

    assert plan[0]["group_code"] == "2.1"
    assert plan[0]["group_label"] == "วิชาเฉพาะด้าน (บังคับ)"
    assert elective["group_label"] == "วิชาเฉพาะด้าน (เลือก)"
    # NULL ใน DB ต้องมาถึงหน้าเว็บเป็น null เพื่อให้แยก "ไม่มีเทอม" ออกจากปี 0
    assert elective["std_year"] is None and elective["std_semester"] is None


def test_program_without_curriculum_rules_still_answers(make_client, monkeypatch) -> None:
    """
    หลักสูตร 653170011 ยังไม่มีแถวใน ``curriculum_rules`` เลย — ต้องไม่ 500

    เคยเป็นบั๊กแบบคลาสสิก: โค้ดที่สมมติว่ามีหมวดเสมอจะหารด้วยศูนย์หรือ
    index ลิสต์ว่าง แล้วนักศึกษาหลักสูตรนั้นเปิดหน้านี้ไม่ได้เลย
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(main, "_db", liff_db(plan_rows=[], group_rows=[]))
    client = make_client(liff_settings(), recorder.client())

    response = client.post("/api/liff/state", json={"id_token": VALID_TOKEN})
    progress = response.json()["progress"]

    assert response.status_code == 200
    assert progress["groups"] == []
    assert progress["plan_courses"] == 0
    assert progress["counted_credits"] == 0
    assert progress["percent_complete"] == 0.0
    assert progress["credits_left_to_graduate"] == 120


@pytest.mark.parametrize("value", [-1, 61, 999])
def test_free_elective_credits_out_of_range_is_rejected_as_input(
    make_client, monkeypatch, value: int
) -> None:
    """
    ค่านอกช่วงต้องเป็น 422 ไม่ใช่ 500

    ``app_users.free_elective_credits`` มี CHECK 0–60 อยู่แล้ว ถ้าปล่อยให้ DB
    เป็นคนปฏิเสธ ผู้ใช้จะเห็น "เซิร์ฟเวอร์ผิดพลาด" ทั้งที่เขากรอกผิดเอง
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    monkeypatch.setattr(main, "_db", liff_db())
    client = make_client(liff_settings(), recorder.client())

    response = client.post(
        "/api/liff/completed_courses",
        json={
            "id_token": VALID_TOKEN,
            "course_codes": [],
            "free_elective_credits": value,
        },
    )

    assert response.status_code == 422


def test_saving_free_elective_credits_writes_and_recomputes(
    make_client, monkeypatch
) -> None:
    """
    บันทึกเลือกเสรีแล้วต้องคืนสถานะที่ **เซิร์ฟเวอร์คำนวณใหม่** กลับไปด้วย

    ส่ง 0 ก็ต้องบันทึก (ผู้ใช้ลบตัวเลขที่เคยกรอก) — ``None`` เท่านั้นที่แปลว่า
    "ฟอร์มนี้ไม่ได้ถาม" จึงไม่แตะค่าเดิม
    """
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    database = liff_db(["7071101"], free_elective_credits=6)
    monkeypatch.setattr(main, "_db", database)
    client = make_client(liff_settings(), recorder.client())

    body = client.post(
        "/api/liff/completed_courses",
        json={
            "id_token": VALID_TOKEN,
            "course_codes": ["7071101"],
            "free_elective_credits": 0,
        },
    ).json()

    assert body["success"] is True
    # ลำดับ params ของ SQL_SET_USER_PROGRAM: program, study_year, entry, free, hash
    assert database.params_for("UPDATE app_users")[3] == 0
    assert body["progress"]["counted_credits"] == 9
    assert len(body["progress"]["groups"]) == 3


def test_saving_without_free_electives_does_not_touch_the_stored_value(
    make_client, monkeypatch
) -> None:
    """ฟอร์มที่ไม่ส่งฟิลด์นี้มา ต้องไม่เขียนทับค่าที่ผู้ใช้กรอกไว้แล้ว"""
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    database = liff_db([], free_elective_credits=6)
    monkeypatch.setattr(main, "_db", database)
    client = make_client(liff_settings(), recorder.client())

    client.post(
        "/api/liff/completed_courses",
        json={"id_token": VALID_TOKEN, "course_codes": []},
    )

    assert not any("UPDATE app_users" in sql for sql, _ in database.calls)


def test_login_creates_the_user_row(make_client, monkeypatch) -> None:
    """login ต้อง upsert ``app_users`` ไม่ใช่แค่ verify แล้วทิ้ง"""
    recorder = Recorder((200, {"sub": TEST_USER_ID, "aud": TEST_LOGIN_CHANNEL_ID}))
    database = liff_db()
    monkeypatch.setattr(main, "_db", database)
    client = make_client(liff_settings(), recorder.client())

    body = client.post("/api/liff/login", json={"id_token": VALID_TOKEN}).json()

    assert body["success"] is True
    # มีแถวอยู่แล้ว (fake ตอบ profile กลับมา) → ไม่ใช่ผู้ใช้ใหม่
    assert body["is_new_user"] is False
    assert database.params_for("INSERT INTO app_users") == (
        hash_user_id(TEST_USER_ID, TEST_PEPPER),
    )


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
