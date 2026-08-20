"""
HTTP client สำหรับ regis.rmu.ac.th (Vision Net / Classic ASP)

ข้อควรรู้ที่ยืนยันจากการทดสอบกับเซิร์ฟเวอร์จริง:

1. encoding เป็น ``windows-874`` (cp874) ไม่ใช่ UTF-8
   → ต้อง set ``r.encoding`` เองทุกครั้ง ไม่งั้นข้อความไทยเพี้ยน

2. **ต้อง parse ด้วย ``lxml`` ห้ามใช้ ``html.parser``**
   HTML มี ``</div>`` ที่ไม่มีคู่ ทำให้ ``html.parser`` ตัด ``<td>`` ทิ้งไปหลายช่อง
   (เทียบแล้ว: html.parser ได้ 2/4 แถวที่คอลัมน์ครบ, lxml ได้ 4/4)
   นี่เป็นสาเหตุที่ทำให้ข้อมูลเกรด/เทอมที่ scrape ไว้ก่อนหน้าคลาดคอลัมน์

3. หน้า public ที่ใช้ได้ (ไม่ต้อง login):
   - ``program_info.asp``    POST facultyid=..  → ลิสต์หลักสูตรของคณะ
   - ``program_info_1.asp``  GET  programid=..  → โครงสร้างหลักสูตร
   - ``class_info_5.asp``    GET  courseid=..   → คำอธิบายรายวิชา
   - ``class_info_1.asp``    GET  coursecode=.. → หมู่เรียนที่เปิดสอน

4. ``coursecode`` ต้องเป็น **7 หลักเต็ม** — ใส่ prefix สั้น (เช่น '7071')
   ได้ผลลัพธ์ 0 รายการ ไม่ใช่การค้นแบบ partial match

5. ทุก URL จะแนบ query แปลก ๆ กลับมา เช่น ``avs103281229=2`` (session nonce)
   → ไม่จำเป็นต้องส่ง แต่ต้อง **เพิกเฉย** เวลาเทียบ URL

หมายเหตุ: ``login.asp``/``validate.asp`` (ต้องใช้ ``f_uid``/``f_pwd`` + ``BUILDKEY``
สุ่มต่อ request) **ไม่ถูกใช้ในโมดูลนี้โดยเจตนา** — knowledge base นี้ใช้เฉพาะ
ข้อมูลสาธารณะเพื่อเลี่ยงประเด็น PDPA
"""

from __future__ import annotations

import hashlib
import logging
import random
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://regis.rmu.ac.th/registrar"
ENCODING = "cp874"
PARSER = "lxml"  # ต้องเป็น lxml — ดู docstring ข้อ 2

CACHE_DIR = Path(__file__).resolve().parent / "data" / "raw"

log = logging.getLogger("rmu.client")


class RmuClient:
    """
    Client ที่สุภาพกับเซิร์ฟเวอร์: มี rate limit, retry แบบ backoff และ cache ลงดิสก์

    Parameters
    ----------
    delay:
        หน่วงระหว่าง request (วินาที) เพื่อไม่ให้ยิงถี่เกินไป
    use_cache:
        ถ้า True จะอ่านจาก ``kb/data/raw/`` ถ้ามีไฟล์อยู่แล้ว
        มีประโยชน์มากตอน dev เพราะเว็บนี้ล่มบ่อย (เคยเจอ HTTP 500)
    """

    def __init__(
        self,
        delay: float = 1.0,
        timeout: int = 30,
        retries: int = 3,
        use_cache: bool = True,
        cache_dir: Path = CACHE_DIR,
    ) -> None:
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.use_cache = use_cache
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                ),
                "Accept-Language": "th,en;q=0.8",
            }
        )
        self._last_request = 0.0
        self._warmed = False

    # ── internals ───────────────────────────────────────────────────────────

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request
        wait = self.delay - elapsed
        if wait > 0:
            time.sleep(wait + random.uniform(0, 0.25))
        self._last_request = time.monotonic()

    def _cache_path(self, method: str, path: str, params: dict | None) -> Path:
        key = f"{method}:{path}:{sorted((params or {}).items())}"
        digest = hashlib.sha1(key.encode()).hexdigest()[:16]
        stem = path.replace(".asp", "").replace("/", "_")
        return self.cache_dir / f"{stem}_{digest}.html"

    def warmup(self) -> None:
        """เปิดหน้าแรกก่อนเพื่อรับ ASPSESSIONID cookie (บางหน้าต้องมี)"""
        if self._warmed:
            return
        try:
            self.fetch("class_info.asp", use_cache=False)
        except Exception as exc:  # pragma: no cover - เว็บล่มก็ยังไปต่อได้
            log.warning("warmup failed (ไปต่อได้): %s", exc)
        self._warmed = True

    # ── public API ──────────────────────────────────────────────────────────

    def fetch(
        self,
        path: str,
        params: dict | None = None,
        method: str = "GET",
        use_cache: bool | None = None,
    ) -> str:
        """ดึง HTML (decode cp874 แล้ว) พร้อม retry + cache"""
        use_cache = self.use_cache if use_cache is None else use_cache
        cache_file = self._cache_path(method, path, params)

        if use_cache and cache_file.exists():
            log.debug("cache hit %s", cache_file.name)
            return cache_file.read_text(encoding="utf-8")

        url = f"{BASE_URL}/{path}"
        last_error: Exception | None = None

        for attempt in range(1, self.retries + 1):
            self._throttle()
            try:
                if method == "POST":
                    resp = self.session.post(url, data=params, timeout=self.timeout)
                else:
                    resp = self.session.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                resp.encoding = ENCODING
                html = resp.text

                if use_cache:
                    cache_file.write_text(html, encoding="utf-8")
                return html

            except Exception as exc:
                last_error = exc
                backoff = 2**attempt
                log.warning(
                    "%s %s ล้มเหลว (ครั้งที่ %d/%d): %s — รอ %ds",
                    method,
                    path,
                    attempt,
                    self.retries,
                    exc,
                    backoff,
                )
                if attempt < self.retries:
                    time.sleep(backoff)

        raise RuntimeError(f"ดึง {url} ไม่สำเร็จหลังลอง {self.retries} ครั้ง") from last_error

    def soup(
        self,
        path: str,
        params: dict | None = None,
        method: str = "GET",
        use_cache: bool | None = None,
    ) -> BeautifulSoup:
        """เหมือน :meth:`fetch` แต่คืน BeautifulSoup (parser=lxml)"""
        return BeautifulSoup(
            self.fetch(path, params, method, use_cache), PARSER
        )


# ── helper สำหรับ parse ข้อความจากเว็บ ───────────────────────────────────────

DAY_CODES = {"MO", "TU", "WE", "TH", "FR", "SA", "SU"}


def clean(text: str | None) -> str:
    """normalize ช่องว่าง + nbsp"""
    if not text:
        return ""
    return " ".join(text.replace("\xa0", " ").split())


def parse_credits(credits_text: str) -> int | None:
    """
    ดึงจำนวนหน่วยกิตออกจากข้อความ โดยเอา *เลขตัวแรก* ที่เจอ

    รองรับทั้ง 2 รูปแบบที่เว็บใช้จริง:

    >>> parse_credits('3 (2-2-5)')     # รายวิชา: 3 นก. (บรรยาย-ปฏิบัติ-ศึกษาเอง)
    3
    >>> parse_credits('30 หน่วยกิต')    # หัวข้อหมวด
    30
    >>> parse_credits('') is None
    True
    """
    text = clean(credits_text)
    if not text:
        return None
    match = re.match(r"^\s*(\d+)", text)
    return int(match.group(1)) if match else None


def parse_time_to_minutes(hhmm: str) -> int | None:
    """'08:00' -> 480"""
    try:
        hours, minutes = hhmm.strip().split(":")
        return int(hours) * 60 + int(minutes)
    except (ValueError, AttributeError):
        return None
