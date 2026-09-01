"""ดึงและจัดรูปกิจกรรมนักศึกษา โดยไม่แตะข้อมูลผู้สมัครที่เป็น PII"""
from __future__ import annotations

import asyncio, hashlib, logging, re
from datetime import date, datetime, timezone
from typing import Any, Iterable
from urllib.parse import urljoin

import httpx

log = logging.getLogger("app.activities")
LIST_URL = "https://e-activity.rmu.ac.th/home/ActivityRegisterAll"
BASE_URL = "https://e-activity.rmu.ac.th"
MONTHS = {m: i for i, m in enumerate(("ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."), 1)}
EXPECTED_HEADERS = ("กิจกรรม/โครงการ", "วันที่จัดกิจกรรม", "การรับสมัคร", "สมัคร", "รับ")

def thai_date(value: str | None) -> date | None:
    if not value: return None
    text = re.sub(r"\s+", " ", value.strip())
    month_pattern = "|".join(re.escape(m) for m in MONTHS)
    m = re.search(rf"(\d{{1,2}})\s*({month_pattern})\s*(\d{{4}})", text)
    if not m or m.group(2) not in MONTHS: return None
    return date(int(m.group(3)) - 543, MONTHS[m.group(2)], int(m.group(1)))

buddhist_to_gregorian = thai_date

def thai_date_range(value: str | None) -> tuple[date | None, date | None]:
    if not value: return None, None
    month_pattern = "|".join(re.escape(m) for m in MONTHS)
    vals = re.findall(rf"\d{{1,2}}\s*(?:{month_pattern})\s*\d{{4}}", value)
    if not vals: return None, None
    return thai_date(vals[0]), thai_date(vals[1] if len(vals) > 1 else vals[0])

def normalize_status(text: str | None) -> str:
    t = (text or "").strip()
    if "อีกไม่นาน" in t or "เร็ว ๆ นี้" in t or "เร็วๆนี้" in t: return "upcoming"
    if "ปิด" in t or "หมด" in t or "สิ้นสุด" in t: return "closed"
    return "open"

def _num(value: str | None) -> int | None:
    m = re.search(r"[\d,]+", value or "")
    return int(m.group(0).replace(",", "")) if m else None

def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", value.get_text(" ", strip=True) if hasattr(value, "get_text") else str(value or "")).strip()

def parse_list(html: str) -> list[dict[str, Any]]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    rows: list[dict[str, Any]] = []
    for table in soup.find_all("table"):
        trs = table.find_all("tr")
        if not trs: continue
        headers = tuple(_clean(x) for x in trs[0].find_all(["th", "td"]))
        if headers[:5] != EXPECTED_HEADERS: continue
        for tr in trs[1:]:
            cells = tr.find_all("td")
            if len(cells) < 5: continue
            link = cells[0].find("a", href=True)
            href = urljoin(BASE_URL, link["href"]) if link else ""
            ref = (re.search(r"ViewActivity/(\d+)", href) or [None, href])[1]
            status_text = _clean(cells[2]); dates = _clean(cells[1])
            row = {"source_ref": ref, "title": _clean(cells[0]), "event_dates_text": dates,
                   "register_dates_text": status_text, "status_text": status_text,
                   "register_status": normalize_status(status_text), "applied": _num(_clean(cells[3])), "capacity": _num(_clean(cells[4])),
                   "detail_url": href}
            row["row_hash"] = hashlib.sha256("|".join(_clean(c) for c in cells[:5]).encode()).hexdigest()
            rows.append(row)
        if rows: return [r for r in rows if r["register_status"] in {"open", "upcoming"}]
    raise ValueError("invalid activity table header")

parse_activity_list = parse_list

def parse_detail(html: str, base: dict[str, Any] | None = None) -> dict[str, Any]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True)
    # หน้า detail มีรายชื่อผู้สมัครต่อท้าย ซึ่งเป็น PII และไม่เกี่ยวกับการค้นกิจกรรม
    for marker in ("รายชื่อผู้สมัคร", "รายชื่อผู้เข้าร่วม"):
        if marker in text:
            text = text.split(marker, 1)[0]
    labels = ("รหัสกิจกรรม", "ชื่อกิจกรรม", "ประเภทและลักษณะของกิจกรรม", "ลักษณะกิจกรรมการเรียนรู้แบบบูรณาการ", "สังกัด", "จัดขึ้นสำหรับ", "ค่าชั่วโมง", "ช่วงรับสมัคร", "ประเภทการรับสมัคร", "สถานะ", "ปีการศึกษา", "วันจัด", "เวลา", "สถานที่", "โดย", "โทร", "รายละเอียดเพิ่มเติม")
    out = dict(base or {})
    for label in labels:
        m = re.search(re.escape(label) + r"\s*[:：]?\s*(.*?)(?=\s+(?:" + "|".join(map(re.escape, labels)) + r")\s*[:：]?|$)", text)
        if not m: continue
        val = m.group(1).strip()
        key = {"รหัสกิจกรรม":"activity_code","ชื่อกิจกรรม":"title","สังกัด":"affiliation","จัดขึ้นสำหรับ":"target_audience","ค่าชั่วโมง":"hours_text","ช่วงรับสมัคร":"register_dates_text","ประเภทการรับสมัคร":"register_method","สถานะ":"status_text","ปีการศึกษา":"academic_year","วันจัด":"event_dates_text","เวลา":"event_time","สถานที่":"venue","โดย":"organizer","โทร":"phone","รายละเอียดเพิ่มเติม":"description"}.get(label)
        if key: out[key] = val
    out["event_start"], out["event_end"] = thai_date_range(out.get("event_dates_text"))
    out["register_start"], out["register_end"] = thai_date_range(out.get("register_dates_text"))
    out["register_status"] = normalize_status(out.get("status_text"))
    h = re.search(r"\d+(?:\.\d+)?", out.get("hours_text", "")); out["hours"] = float(h.group()) if h else None
    return out

parse_activity_detail = parse_detail

WEB_COLUMNS = ("activity_code","title","organizer","affiliation","activity_type","learning_dimension","target_audience","academic_year","event_start","event_end","event_dates_text","event_time","venue","hours","hours_text","register_start","register_end","register_dates_text","register_method","register_status","status_text","capacity","applied","phone","description","detail_url","row_hash")

async def fetch_url(client: httpx.AsyncClient, url: str, *, attempts: int = 3, delay: float = 1.0) -> httpx.Response:
    """หน่วงและ retry เฉพาะความล้มเหลวชั่วคราว เพื่อไม่รบกวนเว็บเจ้าของ"""
    last: Exception | None = None
    for attempt in range(attempts):
        if attempt: await asyncio.sleep(delay * (2 ** (attempt - 1)))
        try:
            response = await client.get(url, timeout=20.0)
            if response.status_code == 429 or response.status_code >= 500:
                raise httpx.HTTPStatusError("temporary upstream failure", request=response.request, response=response)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            last = exc
    raise last or RuntimeError("request failed")

async def upsert_activity(db: Any, row: dict[str, Any]) -> int:
    cols = ("source", "source_ref", *WEB_COLUMNS)
    vals = [row.get("source", "e-activity"), row["source_ref"], *(row.get(c) for c in WEB_COLUMNS)]
    placeholders = ",".join(["%s"] * len(cols))
    updates = ",".join(f"{c}=EXCLUDED.{c}" for c in WEB_COLUMNS) + ",last_seen_at=now(),scraped_at=now()"
    sql = f"INSERT INTO activities ({','.join(cols)}) VALUES ({placeholders}) ON CONFLICT (source,source_ref) DO UPDATE SET {updates} WHERE activities.source <> 'manual'"
    return await db.execute(sql, vals)

async def list_open_activities(db: Any, limit: int = 12) -> list[dict]:
    return await db.fetch_all("SELECT * FROM activities WHERE is_active AND register_status IN ('open','upcoming') ORDER BY is_pinned DESC, register_end ASC NULLS LAST LIMIT %s", (limit,))

async def scrape_activities(db: Any, client: httpx.AsyncClient, *, triggered_by: str = "cli") -> dict:
    """scrape แบบ atomic ระดับรอบ: ตรวจ list ก่อน แล้วค่อยดึง detail เฉพาะแถวใหม่/เปลี่ยน"""
    response = await fetch_url(client, LIST_URL)
    rows = parse_list(response.text)
    old = {str(r["source_ref"]): r for r in await db.fetch_all("SELECT source_ref,row_hash FROM activities WHERE source='e-activity'")}
    fetched = 0
    for row in rows:
        if row["source_ref"] not in old or old[row["source_ref"]].get("row_hash") != row.get("row_hash"):
            await asyncio.sleep(1)
            detail = await fetch_url(client, row["detail_url"])
            row = parse_detail(detail.text, row)
            fetched += 1
        await upsert_activity(db, row)
    return {"rows_found": len(rows), "details_fetched": fetched, "http_status": response.status_code, "bytes": len(response.content), "triggered_by": triggered_by}

def activities_flex_message(rows: list[dict], fetched_at: datetime | None = None) -> dict:
    if not rows: return {"type":"text","text":"ขณะนี้ไม่มีกิจกรรมที่เปิดรับสมัครครับ"}
    shown = rows[:12]; when = (fetched_at or datetime.now(timezone.utc)).astimezone().strftime("%d/%m/%Y %H:%M")
    bubbles = []
    for r in shown:
        title = str(r.get("title") or "กิจกรรม")[:120]
        body = "\n".join(x for x in (f"จัดโดย {r.get('organizer') or '-'}", f"วันจัด {r.get('event_dates_text') or '-'}", f"รับสมัคร {r.get('register_dates_text') or '-'}", f"{r.get('hours_text') or '-'} · สมัคร {r.get('applied') or 0}/{r.get('capacity') or '-'}") if x)
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","contents":[{"type":"text","text":title,"weight":"bold","wrap":True},{"type":"text","text":body,"wrap":True,"size":"sm","margin":"md"},{"type":"text","text":f"ข้อมูล ณ {when}","size":"xs","color":"#667085","margin":"md"}]},"footer":{"type":"box","layout":"vertical","contents":[{"type":"button","style":"primary","action":{"type":"uri","label":"ดูรายละเอียด","uri":r.get("detail_url") or BASE_URL}}]}}
        bubbles.append(bubble)
    return {"type":"flex","altText":f"กิจกรรมที่เปิดรับสมัคร {len(rows)} รายการ","contents":{"type":"carousel","contents":bubbles},"quickReply":None}

open_activities_flex_message = activities_flex_message
