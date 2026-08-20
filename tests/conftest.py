"""
fixture กลางของชุดเทส

จุดที่ต้องระวังเป็นพิเศษ 2 เรื่อง:

1. **ไม่ใช้ ``with TestClient(app)``** ในเทสส่วนใหญ่ เพราะ lifespan จะสร้าง
   ``httpx.AsyncClient`` ตัวจริง (ยิงเน็ตออกได้) — เราฉีด mock client เองแทน
   (มีเทสแยกไว้ตัวหนึ่งที่รัน lifespan จริงเพื่อยืนยันว่า start/stop ทำงาน)

2. ``app.main._configure_logging()`` ตั้ง ``root.handlers = [handler]`` ใหม่ทั้งชุด
   (จำเป็นเพราะ stderr บน Windows เป็น cp874 ทำให้ข้อความไทยเป็น ``?????``)
   → ถ้าปล่อยไว้ handler ของ pytest จะหลุด ทำให้ ``caplog`` ของเทสตัวถัด ๆ ไป
   จับ log ไม่ได้ จึงมี fixture คืนค่าเดิมให้ทุกครั้ง
"""

from __future__ import annotations

import logging
from typing import Callable, Iterator

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import Settings, get_settings

from .helpers import Recorder, make_settings, refuse_all


@pytest.fixture(autouse=True)
def restore_root_logging() -> Iterator[None]:
    """คืน handler/level ของ root logger หลังจบเทสแต่ละตัว"""
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    try:
        yield
    finally:
        root.handlers = handlers
        root.setLevel(level)


@pytest.fixture
def settings() -> Settings:
    """Settings สำหรับ dev: มี channel secret แต่ยังไม่มี access token"""
    return make_settings()


@pytest.fixture
def make_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[..., TestClient]]:
    """
    factory สร้าง ``TestClient`` ที่ override settings + httpx client

    ``http`` ที่ส่งเข้ามาจะถูกใส่ใน ``app.main._http`` โดยตรง เพราะ
    ``process_event`` เรียก ``get_http()`` เอง (ไม่ผ่าน dependency injection)
    ส่วน endpoint ที่ใช้ ``Depends(get_http)`` ก็อ่านตัวแปรเดียวกัน
    """
    def _make(
        settings: Settings | None = None,
        http: httpx.AsyncClient | None = None,
    ) -> TestClient:
        resolved = settings or make_settings()
        client = http or httpx.AsyncClient(transport=httpx.MockTransport(refuse_all))

        monkeypatch.setattr(main, "_http", client)
        # lifespan เรียก get_settings() ตรง ๆ — patch ไว้กัน .env จริงหลุดเข้ามา
        monkeypatch.setattr(main, "get_settings", lambda: resolved)
        # ส่วน endpoint ผูกกับ object เดิมตอน import → ต้อง override ทาง FastAPI
        main.app.dependency_overrides[get_settings] = lambda: resolved
        return TestClient(main.app)

    try:
        yield _make
    finally:
        main.app.dependency_overrides.clear()


@pytest.fixture
def recorder() -> Recorder:
    """Recorder ที่ตอบ 200 ว่างเปล่า — พอสำหรับ LINE reply/push API"""
    return Recorder((200, {}))
