"""
เทส config — fail fast ก่อนขึ้น production

``Settings`` เป็นจุดเดียวที่รู้ว่าอะไรจำเป็น เทสนี้จึงเน้น 2 เรื่อง:

1. **dev รันได้โดยไม่มี key ครบ** (จะได้ dev ส่วนที่ไม่ใช้ LINE ต่อได้)
2. **production รันไม่ได้ถ้า secret ไม่ครบ** — ไม่ใช่ค่อยไปพังตอน user ยิงเข้ามา

ทุกเทสสร้าง ``Settings`` ด้วย ``_env_file=None`` เพื่อไม่ให้ ``.env`` ของเครื่อง
ที่รันเทสมาเปลี่ยนผลลัพธ์
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.config import REPO_ROOT, Settings, get_settings

from .helpers import TEST_PEPPER, make_settings

PRODUCTION_SECRETS = {
    "database_url": "postgresql://u:p@db.example.com:5432/rmu_bot?sslmode=require",
    "line_channel_secret": "real_secret",
    "line_channel_access_token": "real_token",
    "line_login_channel_id": "1234567890",
    "llm_api_key": "real_key",
    "user_id_pepper": TEST_PEPPER,
}


def production_settings(**overrides) -> Settings:
    values = dict(PRODUCTION_SECRETS, app_env="production")
    values.update(overrides)
    return Settings(_env_file=None, **values)


# ── ค่า default ─────────────────────────────────────────────────────────────


def test_scope_defaults_match_mdi_program() -> None:
    """
    scope ของโปรเจกต์คือหลักสูตร MDI เท่านั้น (643170151 / programid 59721)
    ถ้าค่านี้เพี้ยน scraper กับ query จะไปดึงหลักสูตรอื่นมาตอบ
    """
    settings = make_settings()
    assert settings.default_program_code == "643170151"
    assert settings.default_program_id == 59721


def test_llm_defaults_point_to_openai_compatible_endpoint() -> None:
    settings = make_settings()
    assert settings.llm_base_url.endswith("/v1beta/openai")
    assert settings.embedding_base_url.endswith("/v1beta/openai")


def test_base_url_trailing_slash_is_stripped() -> None:
    """กัน ``//chat/completions`` ตอนต่อ path (บาง provider ตอบ 404)"""
    settings = make_settings(
        llm_base_url="https://api.openai.com/v1/",
        embedding_base_url="http://127.0.0.1:11434/v1///",
    )
    assert settings.llm_base_url == "https://api.openai.com/v1"
    assert settings.embedding_base_url == "http://127.0.0.1:11434/v1"


def test_embedding_key_falls_back_to_llm_key() -> None:
    assert make_settings(llm_api_key="k").embedding_key == "k"
    assert make_settings(llm_api_key="k", embedding_api_key="e").embedding_key == "e"


def test_is_production_flag() -> None:
    assert make_settings().is_production is False
    assert production_settings().is_production is True


# ── validation ──────────────────────────────────────────────────────────────


def test_unknown_app_env_is_rejected() -> None:
    """
    พิมพ์ ``prod`` แทน ``production`` แล้วผ่านไปได้ = การตรวจ secret
    ของ production ถูกข้ามทั้งหมดโดยไม่มีใครรู้
    """
    with pytest.raises(ValueError, match="app_env"):
        Settings(_env_file=None, app_env="prod")


def test_development_allows_missing_secrets() -> None:
    """dev ต้องรันได้เพื่อทำงานส่วนที่ไม่ต้องใช้ LINE/LLM"""
    settings = Settings(
        _env_file=None,
        app_env="development",
        line_channel_secret="",
        line_channel_access_token="",
        llm_api_key="",
        user_id_pepper="",
    )
    assert settings.line_channel_access_token == ""


def test_production_lists_every_missing_secret() -> None:
    """error ต้องบอกครบทุกตัวที่ขาด ไม่ใช่ทีละตัว (แก้รอบเดียวจบ)"""
    with pytest.raises(ValueError) as info:
        production_settings(line_channel_access_token="", llm_api_key="")

    message = str(info.value)
    assert "LINE_CHANNEL_ACCESS_TOKEN" in message
    assert "LLM_API_KEY" in message
    assert "LINE_CHANNEL_SECRET" not in message, "ตัวที่ตั้งแล้วไม่ควรถูกรายงาน"


def test_production_rejects_short_pepper() -> None:
    """
    pepper สั้น = brute-force หา line_user_id ย้อนกลับได้
    (line_user_id มีรูปแบบคาดเดาได้)
    """
    with pytest.raises(ValueError, match="USER_ID_PEPPER"):
        production_settings(user_id_pepper="สั้นเกิน")


def test_production_accepts_complete_config() -> None:
    settings = production_settings()
    assert settings.is_production is True
    assert len(settings.user_id_pepper) >= 32


def test_threshold_bounds_are_enforced() -> None:
    """
    threshold นอกช่วง 0-1 ทำให้ตรรกะ "มั่นใจพอจะตอบไหม" พังเงียบ ๆ
    (เช่น 82 แทน 0.82 → จะ fallback ทุกคำถาม)
    """
    for field in ("faq_match_threshold", "rag_similarity_threshold"):
        with pytest.raises(ValueError):
            make_settings(**{field: 1.5})
        with pytest.raises(ValueError):
            make_settings(**{field: -0.1})

    with pytest.raises(ValueError):
        make_settings(rag_top_k=0)


# ── require() ───────────────────────────────────────────────────────────────


def test_require_passes_when_set() -> None:
    make_settings(line_channel_access_token="t").require("line_channel_access_token")


def test_require_reports_env_variable_names() -> None:
    """
    ข้อความต้องเป็นชื่อ **ตัวแปรใน .env** (ตัวใหญ่) ไม่ใช่ชื่อ attribute
    เพราะคนอ่าน error ต้องเอาไปแก้ไฟล์ .env ได้ทันที
    """
    with pytest.raises(RuntimeError) as info:
        make_settings().require("line_channel_access_token", "llm_api_key")

    message = str(info.value)
    assert ".env" in message
    assert "LINE_CHANNEL_ACCESS_TOKEN" in message
    assert "LLM_API_KEY" in message


def test_require_ignores_fields_that_are_set() -> None:
    with pytest.raises(RuntimeError) as info:
        make_settings(llm_api_key="k").require("llm_api_key", "line_channel_access_token")

    assert "LLM_API_KEY" not in str(info.value)


# ── get_settings ────────────────────────────────────────────────────────────


def test_get_settings_is_cached() -> None:
    """cache ไว้ตัวเดียว — ไม่โหลด .env ใหม่ทุก request"""
    assert get_settings() is get_settings()


# ── ความสอดคล้องกับ schema ──────────────────────────────────────────────────


def _sql_vector_dimension() -> int:
    sql = Path(REPO_ROOT, "db", "migrations", "001_init.sql").read_text(
        encoding="utf-8"
    )
    match = re.search(r"vector\((\d+)\)", sql)
    assert match, "ไม่พบคอลัมน์ vector(N) ใน 001_init.sql"
    return int(match.group(1))


def test_embedding_dim_matches_sql_schema() -> None:
    """
    ``EMBEDDING_DIM`` ต้องเท่ากับ ``vector(N)`` ใน migration

    ใช้ Gemini ``gemini-embedding-2`` ซึ่ง default เป็น 3072 มิติ แต่ ``app/llm.py``
    ส่ง ``dimensions`` ไปขอตัดเหลือ **768** ให้ตรงกับ schema
    ถ้าไม่ตรง: insert embedding ลง Postgres จะ error ทุกครั้ง และรู้ตัวตอน
    index ข้อมูลจริงแล้ว (เสียเวลา re-embed ใหม่ทั้งชุด)

    เปลี่ยน model ในอนาคตต้องแก้ **ทั้งสองที่** พร้อม re-index — เทสนี้กันลืม
    """
    assert Settings(_env_file=None).embedding_dim == _sql_vector_dimension() == 768
