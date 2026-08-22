"""
ตั้ง Webhook endpoint ของ LINE ให้ชี้มาที่ ``PUBLIC_BASE_URL`` ใน ``.env``

ใช้ตอนเปลี่ยนอุโมงค์ (cloudflared quick tunnel ให้ URL ใหม่ทุกครั้ง) แทนการ
พิมพ์ curl เอง::

    set PYTHONUTF8=1
    python scripts/set_webhook_endpoint.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402

from app.config import get_settings  # noqa: E402


def main() -> None:
    settings = get_settings()
    token = settings.line_channel_access_token
    if not token:
        raise SystemExit("ยังไม่ได้ตั้ง LINE_CHANNEL_ACCESS_TOKEN ใน .env")
    if not settings.public_base_url:
        raise SystemExit("ยังไม่ได้ตั้ง PUBLIC_BASE_URL ใน .env")

    endpoint = settings.public_base_url.rstrip("/") + "/webhook"
    headers = {"Authorization": f"Bearer {token}"}
    api = "https://api.line.me/v2/bot/channel/webhook/endpoint"

    response = httpx.put(api, headers=headers, json={"endpoint": endpoint}, timeout=30)
    print(f"PUT {response.status_code} → {endpoint}")
    if response.status_code != 200:
        raise SystemExit(response.text[:400])

    current = httpx.get(api, headers=headers, timeout=30).json()
    print("LINE เก็บไว้:", current.get("endpoint"))

    # ยิงทดสอบจากฝั่ง LINE ว่ายิงทะลุอุโมงค์จริง (คนละ path กับตัวตั้ง
    # — ``/channel/webhook/test`` ไม่ใช่ ``/endpoint/test``)
    test = httpx.post("https://api.line.me/v2/bot/channel/webhook/test",
                      headers=headers, timeout=30)
    result = test.json()
    print("test:", result)
    if not result.get("success"):
        raise SystemExit("LINE ยิงทดสอบกลับมาไม่สำเร็จ — ตรวจอุโมงค์/เซิร์ฟเวอร์")


if __name__ == "__main__":
    main()
