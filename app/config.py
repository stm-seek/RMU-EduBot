"""
Config ของแอป — อ่านจาก environment / ``.env``

ตั้งใจให้ **สลับ LLM provider ได้ด้วย ``base_url`` + ``api_key`` เท่านั้น**
ไม่ผูกกับ SDK ของเจ้าไหน (ยืนยันแล้วว่า Gemini มี OpenAI-compatible endpoint
ทั้ง ``/chat/completions`` และ ``/embeddings``)

ค่าที่จำเป็นจะถูกตรวจตอนสตาร์ท (fail fast) ไม่ปล่อยให้พังตอน user ยิงเข้ามา
"""

from __future__ import annotations

import functools
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── App ─────────────────────────────────────────────────────────────────
    app_env: str = "development"
    log_level: str = "INFO"
    port: int = 8000
    public_base_url: str = ""

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = ""
    # เวลารอตอนสตาร์ทให้ connection pool พร้อม — ถ้าเกินนี้แอปจะทำงานต่อ
    # แบบไม่มี DB (บอทตอบว่า "ยังไม่มีข้อมูล") ไม่ใช่สตาร์ทไม่ขึ้น
    #
    # ตั้งสูงไว้เผื่อ Neon/Supabase free tier ที่ต้อง cold start
    # ตอน dev ที่ยังไม่มี DB ลดค่านี้ลงจะสตาร์ทเร็วขึ้น (psycopg บวกอีก 5 วินาที
    # ตอนปิด pool ที่ timeout เอง ซึ่งคุมไม่ได้)
    db_connect_timeout_seconds: float = Field(default=10.0, gt=0.0, le=120.0)

    # ── LINE Messaging API ──────────────────────────────────────────────────
    line_channel_secret: str = ""
    line_channel_access_token: str = ""

    # ── LIFF / LINE Login ───────────────────────────────────────────────────
    liff_id: str = ""
    line_login_channel_id: str = ""

    # ── LLM (OpenAI-compatible) ─────────────────────────────────────────────
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    llm_api_key: str = ""
    # เลือก flash-lite เพราะวัดแล้วเร็วกว่า gemini-3.6-flash ราว 20 เท่า
    # (1.0 วิ vs 20.5 วิ) โดยคุณภาพคำตอบเท่ากันในงานนี้ — flash ตัวเต็มเป็น
    # thinking model เผา token ไปกับการคิด ~500 tokens ซึ่งงานนี้ไม่ต้องการ
    # เพราะ LLM แค่เรียบเรียงข้อมูลที่ retrieve มาแล้ว ไม่ได้คิดเลขหรือวางแผน
    llm_model: str = "gemini-3.5-flash-lite"
    # 30 วิ ตึงเกินจริง — วัด 19 ส.ค. 2026 ได้ chat 19.7 วิ (thinking model)
    # และ embed ครั้งแรก timeout ที่ 30 วิ ต้องให้ retry ช่วย
    llm_timeout_seconds: float = 60.0
    # โมเดลตระกูล thinking (gemini-3.x flash) กิน token ไปกับการคิดก่อนตอบ
    # ซึ่งไม่ถูกนับใน completion_tokens — วัดจริงพบว่าคำตอบไทยสั้น ๆ 48 token
    # ใช้ total ไป 417 จึงต้องเผื่อไว้ ถ้าตั้งน้อยเกินจะได้คำตอบเปล่า
    llm_max_output_tokens: int = 2048
    llm_temperature: float = 0.3

    # ── Embedding ───────────────────────────────────────────────────────────
    embedding_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    embedding_api_key: str = ""
    # text-embedding-004 ถูกปลดจาก API แล้ว (404) — gemini-embedding-2 คือตัวแทน
    # ที่ยืนยันแล้วว่าคืนเวกเตอร์ normalize มาแล้วเมื่อขอ 768 มิติ
    embedding_model: str = "gemini-embedding-2"
    embedding_dim: int = 768

    # ── Security ────────────────────────────────────────────────────────────
    user_id_pepper: str = ""

    # ── Retrieval ───────────────────────────────────────────────────────────
    faq_match_threshold: float = Field(default=0.82, ge=0.0, le=1.0)
    rag_similarity_threshold: float = Field(default=0.55, ge=0.0, le=1.0)
    rag_top_k: int = Field(default=5, ge=1, le=50)

    # ── AI Chat (Requirement ข้อ 9) ─────────────────────────────────────────
    # ปิดทั้งชั้นได้ด้วยตัวเดียว (เช่น key หมดกะทันหัน) — router จะถอยกลับไป
    # ตอบ fallback แบบเดิม ไม่ใช่พัง
    ai_chat_enabled: bool = True
    # จำนวนรอบสนทนาเก่าที่ดึงจาก chat_logs มาต่อเป็น context
    # 4 รอบ = 8 message ≈ ไม่กี่ร้อย token — พอสำหรับ "แล้วต้องทำยังไงอีก"
    # โดยไม่ทำให้ prompt บวม (ทุกข้อความถูกตัดเพดานด้วยค่าข้างล่างอีกที)
    ai_chat_history_turns: int = Field(default=4, ge=0, le=10)
    # เพดานตัวอักษรรวมของประวัติ — กันข้อความยาวพิเศษทำ prompt บวม
    # นับจากรอบล่าสุดย้อนหลัง เกินเมื่อไหร่หยุดดึงเพิ่ม
    ai_chat_max_history_chars: int = Field(default=2_000, ge=0)

    # ── Scope ───────────────────────────────────────────────────────────────
    default_program_id: int = 59721
    default_program_code: str = "643170151"

    # ── validators ──────────────────────────────────────────────────────────

    @field_validator("llm_base_url", "embedding_base_url")
    @classmethod
    def _strip_trailing_slash(cls, value: str) -> str:
        """กัน ``//chat/completions`` ตอนต่อ path"""
        return value.rstrip("/")

    @field_validator("app_env")
    @classmethod
    def _known_env(cls, value: str) -> str:
        allowed = {"development", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"app_env ต้องเป็นหนึ่งใน {sorted(allowed)} (ได้ {value!r})")
        return value

    @model_validator(mode="after")
    def _check_production_secrets(self) -> "Settings":
        """
        บน production ต้องมี secret ครบ — ห้ามรันด้วยค่าว่าง

        ตอน development ปล่อยว่างได้ เพื่อให้ dev ส่วนที่ไม่ต้องใช้ LINE ได้
        แต่ endpoint ที่ต้องใช้จะโยน error เองเมื่อถูกเรียก
        """
        if self.app_env != "production":
            return self

        required = {
            "DATABASE_URL": self.database_url,
            "LINE_CHANNEL_SECRET": self.line_channel_secret,
            "LINE_CHANNEL_ACCESS_TOKEN": self.line_channel_access_token,
            "LINE_LOGIN_CHANNEL_ID": self.line_login_channel_id,
            "LLM_API_KEY": self.llm_api_key,
            "USER_ID_PEPPER": self.user_id_pepper,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(
                "APP_ENV=production แต่ยังไม่ได้ตั้งค่า: " + ", ".join(missing)
            )

        if len(self.user_id_pepper) < 32:
            raise ValueError(
                "USER_ID_PEPPER สั้นเกินไป (ต้อง >= 32 ตัว) "
                'สร้างด้วย: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        return self

    # ── helpers ─────────────────────────────────────────────────────────────

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def embedding_key(self) -> str:
        """ถ้าไม่ตั้ง EMBEDDING_API_KEY ให้ใช้ตัวเดียวกับ LLM"""
        return self.embedding_api_key or self.llm_api_key

    def require(self, *names: str) -> None:
        """
        เช็คว่าค่าที่จำเป็นถูกตั้งแล้ว — เรียกก่อนใช้ feature นั้น

        ใช้แทนการ raise ตอน import เพื่อให้ dev feature อื่นได้
        โดยไม่ต้องมี key ครบทุกตัว
        """
        missing = [name for name in names if not getattr(self, name, None)]
        if missing:
            env_names = ", ".join(name.upper() for name in missing)
            raise RuntimeError(f"ยังไม่ได้ตั้งค่าใน .env: {env_names}")


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """cache ไว้ตัวเดียว — เรียกซ้ำได้ไม่โหลด .env ใหม่"""
    return Settings()
