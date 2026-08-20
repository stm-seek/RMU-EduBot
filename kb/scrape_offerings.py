"""
Scraper: หมู่เรียนที่เปิดสอนจริง (``class_info_1.asp``) + สรุป offering pattern

เป็นส่วนที่ให้ข้อมูลซึ่ง *ไม่มี* ที่อื่นเลย:

* วิชานี้เปิดสอนเทอมไหน (ใช้แทนแผนการเรียนที่ระบบไม่มี)
* วัน-เวลา-ห้อง → ตรวจตารางชนได้
* จำนวนรับ / ลงแล้ว / เหลือ → เตือนที่นั่งใกล้เต็ม
* ชื่ออาจารย์ผู้สอน

คอลัมน์ที่ยืนยันจากของจริง (coursecode=1109901, 2568/1) — 12 ช่อง::

    td[0]  (spacer)
    td[1]  รหัสวิชา       '1109901-1'
    td[2]  ชื่อวิชา + อาจารย์ (อาจารย์อยู่ใน <LI>)
    td[3]  หน่วยกิต       '3 (2-2-5)'
    td[4]  กลุ่มวิชา      '110'
    td[5]  เวลา          'TU 08:00-11:20 360305'
    td[6]  หมู่เรียน       '1'
    td[7]  จำนวนรับ      '50'
    td[8]  ลงแล้ว        '49'
    td[9]  เหลือ         '1'
    td[10] สถานะ        'ปกติ'
    td[11] (spacer)

**ข้อควรระวังที่เจอจากการทดสอบ:**

1. ต้อง parse ด้วย ``lxml`` — ``html.parser`` คืนแถวแรก ๆ เป็น 3 ช่อง
   (คอลัมน์หาย) เพราะ ``</div>`` ที่ไม่มีคู่ในหน้านี้
2. ``coursecode`` ต้องเป็น 7 หลักเต็ม — ใส่ '7071' ได้ 0 ผลลัพธ์
3. ถ้าไม่เปิดสอน หน้าจะขึ้นข้อความ 'ไม่พบรายวิชา ที่ตรงกับเงื่อนไขการค้นหา!'
   ซึ่งเป็นผลลัพธ์ที่ถูกต้อง ไม่ใช่ error
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime, timezone

from .client import (
    BASE_URL,
    DAY_CODES,
    RmuClient,
    clean,
    parse_credits,
    parse_time_to_minutes,
)
from .schema import connect

log = logging.getLogger("rmu.offerings")

NOT_FOUND = "ไม่พบรายวิชา"
COURSEID_RE = re.compile(r"courseid=(\d+)")
# 'TU 08:00-11:20 360305' / 'TU 08:00-11:20 360305 WE 13:00-16:20 360306'
# room ต้องไม่ใช่ day code ของคาบถัดไป (negative lookahead) ไม่งั้นคาบที่ 2 หาย
SLOT_RE = re.compile(
    r"(?P<day>MO|TU|WE|TH|FR|SA|SU)\s*"
    r"(?P<start>\d{1,2}:\d{2})\s*-\s*(?P<end>\d{1,2}:\d{2})\s*"
    r"(?P<room>(?!(?:MO|TU|WE|TH|FR|SA|SU)\b)\S+)?"
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _to_int(text: str) -> int | None:
    match = re.search(r"-?\d+", clean(text))
    return int(match.group()) if match else None


def parse_slots(schedule_raw: str) -> list[dict]:
    """
    'TU 08:00-11:20 360305' → [{'day_code': 'TU', 'start_min': 480,
                                'end_min': 680, 'room': '360305'}]

    รองรับหลายคาบในช่องเดียว และข้ามคาบที่เวลาผิดรูปแบบ
    """
    slots: list[dict] = []
    for match in SLOT_RE.finditer(schedule_raw or ""):
        start = parse_time_to_minutes(match.group("start"))
        end = parse_time_to_minutes(match.group("end"))
        if start is None or end is None:
            continue
        room = match.group("room") or ""
        # กันกรณี regex กิน day code ของคาบถัดไปมาเป็นห้อง
        if room.upper() in DAY_CODES:
            room = ""
        slots.append(
            {
                "day_code": match.group("day"),
                "start_min": start,
                "end_min": end,
                "room": room,
            }
        )
    return slots


def fetch_offerings(
    client: RmuClient, course_code: str, acad_year: int, semester: int
) -> list[dict]:
    """ดึงหมู่เรียนของ 1 วิชา ใน 1 เทอม — คืน ``[]`` ถ้าไม่เปิดสอน"""
    client.warmup()
    params = {
        "cmd": "2",
        "facultyid": "all",
        "acadyear": str(acad_year),
        "semester": str(semester),
        "CAMPUSID": "",
        "LEVELID": "",
        "CLASSSET": "",
        "coursecode": course_code,
        "coursename": "",
    }
    soup = client.soup("class_info_1.asp", params)

    if NOT_FOUND in soup.get_text():
        return []

    source_url = f"{BASE_URL}/class_info_1.asp?" + "&".join(
        f"{k}={v}" for k, v in params.items()
    )
    rows: list[dict] = []

    for anchor in soup.find_all(
        "a", href=lambda h: h and "class_info_2.asp" in h and "courseid=" in h
    ):
        match = COURSEID_RE.search(anchor.get("href", ""))
        if not match:
            continue

        tr = anchor.find_parent("tr")
        if tr is None:
            continue
        cells = tr.find_all("td")
        if len(cells) < 11:
            # ถ้าเจอบ่อย = parser ตัดคอลัมน์ (แปลว่าไม่ได้ใช้ lxml)
            log.warning(
                "%s %s/%s: แถวมี %d ช่อง (คาด >=11) — ข้าม",
                course_code,
                acad_year,
                semester,
                len(cells),
            )
            continue

        name_cell = cells[2]
        instructors = " | ".join(
            clean(li.get_text()) for li in name_cell.find_all("li")
        )
        schedule_raw = clean(cells[5].get_text())

        rows.append(
            {
                "course_id": int(match.group(1)),
                "course_code": course_code,
                "acad_year": acad_year,
                "semester": semester,
                "section": clean(cells[6].get_text()),
                "course_group": clean(cells[4].get_text()),
                "schedule_raw": schedule_raw,
                "instructors": instructors,
                "seats_total": _to_int(cells[7].get_text()),
                "seats_taken": _to_int(cells[8].get_text()),
                "seats_left": _to_int(cells[9].get_text()),
                "status": clean(cells[10].get_text()),
                "credits_text": clean(cells[3].get_text()),
                "source_url": source_url,
                "slots": parse_slots(schedule_raw),
            }
        )

    return rows


def save_offerings(conn, rows: list[dict]) -> int:
    """เขียน offerings + offering_slots (idempotent ผ่าน UNIQUE constraint)"""
    now = _now()
    written = 0

    for row in rows:
        # ให้ courses มีแถวนี้ก่อน (บางวิชาเปิดสอนแต่ไม่อยู่ในหลักสูตรที่ scrape)
        conn.execute(
            """
            INSERT INTO courses (course_id, course_code, credits_text,
                                 credits, scraped_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(course_id) DO NOTHING
            """,
            (
                row["course_id"],
                row["course_code"],
                row["credits_text"],
                parse_credits(row["credits_text"]),
                now,
            ),
        )

        cursor = conn.execute(
            """
            INSERT INTO offerings (course_id, course_code, acad_year, semester,
                                   section, course_group, schedule_raw, instructors,
                                   seats_total, seats_taken, seats_left, status,
                                   source_url, scraped_at)
            VALUES (:course_id, :course_code, :acad_year, :semester,
                    :section, :course_group, :schedule_raw, :instructors,
                    :seats_total, :seats_taken, :seats_left, :status,
                    :source_url, :scraped_at)
            ON CONFLICT(course_id, acad_year, semester, section, schedule_raw)
            DO UPDATE SET
                seats_total = excluded.seats_total,
                seats_taken = excluded.seats_taken,
                seats_left  = excluded.seats_left,
                status      = excluded.status,
                instructors = excluded.instructors,
                scraped_at  = excluded.scraped_at
            RETURNING id
            """,
            {**row, "scraped_at": now},
        )
        offering_id = cursor.fetchone()[0]
        written += 1

        conn.execute(
            "DELETE FROM offering_slots WHERE offering_id = ?", (offering_id,)
        )
        conn.executemany(
            """
            INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    offering_id,
                    s["day_code"],
                    s["start_min"],
                    s["end_min"],
                    s["room"],
                )
                for s in row["slots"]
            ],
        )

    return written


def compute_patterns(conn, terms: list[tuple[int, int]]) -> int:
    """
    สรุปว่าแต่ละวิชา "มักเปิด" เทอมไหน จาก offerings ที่เก็บมา

    ``terms`` คือเทอมที่สำรวจไปทั้งหมด ใช้บอกว่า "ไม่พบ" เพราะไม่เปิด
    หรือเพราะยังไม่ได้สำรวจ
    """
    now = _now()
    observed_sems = {sem for _, sem in terms}
    codes = [
        r[0] for r in conn.execute("SELECT DISTINCT course_code FROM courses")
    ]
    updated = 0

    for code in codes:
        detail: dict[str, int] = {}
        opens = {1: 0, 2: 0, 3: 0}

        for year, sem in terms:
            count = conn.execute(
                """
                SELECT COUNT(*) FROM offerings
                 WHERE course_code = ? AND acad_year = ? AND semester = ?
                """,
                (code, year, sem),
            ).fetchone()[0]
            detail[f"{year}/{sem}"] = count
            if count:
                opens[sem] = 1

        terms_found = sum(1 for v in detail.values() if v)
        if terms_found == 0 and not any(opens.values()):
            # ไม่เคยพบเลย: ข้ามไป ไม่ต้องเขียนแถวเปล่า
            continue

        conn.execute(
            """
            INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2,
                                           opens_sem3, terms_observed, terms_found,
                                           detail, computed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(course_code) DO UPDATE SET
                opens_sem1     = excluded.opens_sem1,
                opens_sem2     = excluded.opens_sem2,
                opens_sem3     = excluded.opens_sem3,
                terms_observed = excluded.terms_observed,
                terms_found    = excluded.terms_found,
                detail         = excluded.detail,
                computed_at    = excluded.computed_at
            """,
            (
                code,
                opens[1] if 1 in observed_sems else 0,
                opens[2] if 2 in observed_sems else 0,
                opens[3] if 3 in observed_sems else 0,
                len(terms),
                terms_found,
                json.dumps(detail, ensure_ascii=False),
                now,
            ),
        )
        updated += 1

    conn.commit()
    return updated


def parse_terms(spec: str) -> list[tuple[int, int]]:
    """'2568/1,2568/2' → [(2568, 1), (2568, 2)]"""
    terms: list[tuple[int, int]] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        year, _, sem = part.partition("/")
        terms.append((int(year), int(sem)))
    return terms


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ดึงหมู่เรียนที่เปิดสอน + สรุป offering pattern"
    )
    parser.add_argument("--program-id", type=int, help="จำกัดเฉพาะวิชาในหลักสูตรนี้")
    parser.add_argument(
        "--terms",
        default="2567/1,2567/2,2568/1,2568/2",
        help="เทอมที่จะสำรวจ คั่นด้วย , เช่น '2568/1,2568/2'",
    )
    parser.add_argument("--limit", type=int, help="จำกัดจำนวนวิชา (ใช้ตอนทดสอบ)")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)-7s %(name)s | %(message)s"
    )

    terms = parse_terms(args.terms)
    client = RmuClient(delay=args.delay, use_cache=not args.no_cache)
    conn = connect()

    try:
        if args.program_id:
            query = """
                SELECT DISTINCT c.course_code
                  FROM courses c
                  JOIN program_courses pc ON pc.course_id = c.course_id
                 WHERE pc.program_id = ?
                 ORDER BY c.course_code
            """
            codes = [r[0] for r in conn.execute(query, (args.program_id,))]
        else:
            codes = [
                r[0]
                for r in conn.execute(
                    "SELECT DISTINCT course_code FROM courses ORDER BY course_code"
                )
            ]

        if args.limit:
            codes = codes[: args.limit]

        log.info("สำรวจ %d วิชา x %d เทอม = %d request", len(codes), len(terms), len(codes) * len(terms))

        total_rows = 0
        for index, code in enumerate(codes, 1):
            for year, sem in terms:
                try:
                    rows = fetch_offerings(client, code, year, sem)
                except Exception as exc:
                    log.error("%s %s/%s ล้มเหลว: %s", code, year, sem, exc)
                    continue
                if rows:
                    total_rows += save_offerings(conn, rows)

            if index % 10 == 0:
                conn.commit()
                log.info("  ...%d/%d วิชา (offerings=%d)", index, len(codes), total_rows)

        conn.commit()
        patterns = compute_patterns(conn, terms)
        log.info("เสร็จ: offerings=%d แถว, offering_patterns=%d วิชา", total_rows, patterns)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
