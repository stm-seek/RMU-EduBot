"""
ตัวรันเซิร์ฟเวอร์ — **บน Windows ต้องรันด้วยไฟล์นี้ ไม่ใช่ ``uvicorn`` ตรง ๆ**

    python run.py

เหตุผล: ``psycopg`` แบบ async ต้องใช้ event loop ที่มี ``add_reader`` /
``add_writer`` (คือ ``SelectorEventLoop``) แต่ uvicorn **บังคับ**
``ProactorEventLoop`` บน Windows อย่างชัดเจนใน ``uvicorn/loops/asyncio.py``::

    if sys.platform == "win32" and not use_subprocess:
        return asyncio.ProactorEventLoop

ผลคือเปิด connection pool ไม่ได้เลย ขึ้น error ว่า::

    Psycopg cannot use the 'ProactorEventLoop' to run in async mode

เพราะ uvicorn ส่ง *loop factory* ให้ ``asyncio.Runner`` โดยตรง การตั้ง
``asyncio.set_event_loop_policy()`` จึงไม่ช่วยอะไร (ทดลองแล้ว — ยังได้ Proactor)
ทางแก้คือสร้าง loop เองแล้วเรียก ``Server.serve()`` ในนั้น ซึ่งเป็นสิ่งที่
ไฟล์นี้ทำ

ข้อจำกัดที่ยอมรับไว้: **ไม่รองรับ ``--reload``** เพราะ uvicorn จะ spawn
process ลูกที่สร้าง loop ใหม่เองอีกครั้ง ตอน dev ที่แก้โค้ดบ่อยและไม่ต้องใช้ DB
ใช้คำสั่งนี้ได้ (``make dev-reload``)::

    uvicorn app.main:app --reload --port 8000

บน Linux/macOS ไม่มีปัญหานี้ (default เป็น Selector อยู่แล้ว) — deploy จริง
ใช้ ``uvicorn app.main:app`` ตรง ๆ ได้
"""

from __future__ import annotations

import asyncio
import sys
from typing import Callable


def loop_factory(
    platform: str = sys.platform,
) -> Callable[[], asyncio.AbstractEventLoop] | None:
    """
    factory ของ event loop ที่ psycopg async ใช้ได้ (``None`` = ใช้ค่า default)

    >>> loop_factory('linux') is None
    True
    >>> loop_factory('darwin') is None
    True
    >>> loop_factory('win32') is asyncio.SelectorEventLoop
    True
    """
    if platform.startswith("win"):
        return asyncio.SelectorEventLoop
    return None


def main() -> None:
    import uvicorn

    from app.config import get_settings

    settings = get_settings()
    factory = loop_factory()
    if factory is not None:
        print(f"ใช้ {factory.__name__} — จำเป็นสำหรับ psycopg async บน Windows")

    server = uvicorn.Server(
        uvicorn.Config(
            "app.main:app",
            host="127.0.0.1",
            port=settings.port,
            log_level=settings.log_level.lower(),
        )
    )

    # ไม่เรียก server.run() เพราะข้างในจะไปเอา loop factory ของ uvicorn มาใช้
    with asyncio.Runner(loop_factory=factory) as runner:
        runner.run(server.serve())


if __name__ == "__main__":
    main()
