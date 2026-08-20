"""
Scraper: คำอธิบายรายวิชา (``class_info_5.asp?courseid=NNNNN``)

โครงสร้างหน้านี้เรียบง่ายและคงที่ (ยืนยันจาก courseid=32701):

    <TR class='headerDetail'><TD>1109901</TD><TD>English for Daily Life</TD></TR>
    <TR class='headerDetail'><TD></TD><TD>ภาษาอังกฤษสำหรับชีวิตประจำวัน</TD></TR>
    <TR><TD></TD><TD>คณะ</TD><TD>หมวดวิชาศึกษาทั่วไป</TD></TR>
    <TR><TD></TD><TD>หน่วยกิต</TD><TD>3 (2-2-5)</TD></TR>
    ...
    <b>คำอธิบายรายวิชา</b><br><FONT Size=3>การสื่อสารในสถานการณ์ต่าง ๆ ...

บางวิชาไม่มีคำอธิบาย → หน้าจะสั้นมาก (~15 ตัวอักษร) ถือว่าปกติ ไม่ใช่ error

คำอธิบายรายวิชานี้เป็นวัตถุดิบหลักของ RAG (embedding + retrieval)
เพราะเป็นข้อความอิสระเพียงส่วนเดียวในฐานข้อมูล
"""

from __future__ import annotations

import argparse
import logging
import re
from datetime import datetime, timezone

from .client import BASE_URL, RmuClient, clean
from .schema import connect

log = logging.getLogger("rmu.courses")

DESC_HEADING = "คำอธิบายรายวิชา"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_course_detail(client: RmuClient, course_id: int) -> dict:
    """
    ดึงคำอธิบาย + ข้อมูลประกอบของรายวิชา 1 วิชา

    คืน ``{}`` ถ้าหน้าว่าง (วิชาไม่มีคำอธิบายในระบบ) เพื่อให้ caller ข้ามได้
    """
    soup = client.soup("class_info_5.asp", {"courseid": course_id})
    text = clean(soup.get_text(" "))
    if len(text) < 40:
        log.debug("courseid=%s: หน้าว่าง (ไม่มีคำอธิบายในระบบ)", course_id)
        return {}

    # ── คำอธิบายรายวิชา: ข้อความหลังหัวข้อ 'คำอธิบายรายวิชา' ────��─────────────
    description = ""
    heading = soup.find(string=re.compile(DESC_HEADING))
    if heading is not None:
        container = heading.find_parent("td") or heading.find_parent("table")
        if container is not None:
            body = clean(container.get_text(" "))
            _, _, tail = body.partition(DESC_HEADING)
            description = clean(tail)

    # ── ตาราง label/value: 'คณะ', 'หน่วยกิต', 'หลักสูตร' ─────────────────────
    fields: dict[str, str] = {}
    for tr in soup.find_all("tr"):
        cells = [clean(td.get_text(" ")) for td in tr.find_all("td")]
        cells = [c for c in cells if c]
        if len(cells) >= 2:
            fields.setdefault(cells[0], cells[1])

    # ── รหัส/ชื่อ จาก 2 แถวแรก (class='headerDetail') ────────────────────────
    header_rows = [
        [clean(td.get_text(" ")) for td in tr.find_all("td")]
        for tr in soup.find_all("tr", class_=re.compile("headerDetail", re.I))
    ]
    code = name_en = name_th = ""
    if header_rows:
        first = [c for c in header_rows[0] if c]
        if first:
            code = first[0]
        if len(first) > 1:
            name_en = first[1]
    if len(header_rows) > 1:
        second = [c for c in header_rows[1] if c]
        if second:
            name_th = second[-1]

    return {
        "course_id": course_id,
        "course_code": code,
        "name_en": name_en,
        "name_th": name_th,
        "credits_text": fields.get("หน่วยกิต", ""),
        "faculty_text": fields.get("คณะ", ""),
        "description_th": description,
        "source_url": f"{BASE_URL}/class_info_5.asp?courseid={course_id}",
    }


def save_course_detail(conn, detail: dict) -> None:
    """
    อัปเดตเฉพาะฟิลด์ที่ได้มาใหม่ — ใช้ ``COALESCE(NULLIF(...))``
    เพื่อไม่ให้ค่าว่างจากหน้านี้ไปลบข้อมูลดี ๆ ที่ได้จาก scrape_programs
    """
    conn.execute(
        """
        UPDATE courses
           SET name_th        = COALESCE(NULLIF(:name_th, ''), name_th),
               name_en        = COALESCE(NULLIF(:name_en, ''), name_en),
               credits_text   = COALESCE(NULLIF(:credits_text, ''), credits_text),
               faculty_text   = COALESCE(NULLIF(:faculty_text, ''), faculty_text),
               description_th = COALESCE(NULLIF(:description_th, ''), description_th),
               source_url     = :source_url,
               scraped_at     = :scraped_at
         WHERE course_id = :course_id
        """,
        {**detail, "scraped_at": _now()},
    )


def pending_course_ids(conn, program_id: int | None, refresh: bool) -> list[int]:
    """รายการ course_id ที่ต้องดึง (ยังไม่มีคำอธิบาย หรือสั่ง refresh)"""
    where = [] if refresh else ["(description_th IS NULL OR description_th = '')"]
    params: list = []

    if program_id is not None:
        where.append(
            "course_id IN (SELECT course_id FROM program_courses WHERE program_id = ?)"
        )
        params.append(program_id)

    clause = f"WHERE {' AND '.join(where)}" if where else ""
    rows = conn.execute(
        f"SELECT course_id FROM courses {clause} ORDER BY course_code", params
    ).fetchall()
    return [r[0] for r in rows]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ดึงคำอธิบายรายวิชาจาก regis.rmu.ac.th (public)"
    )
    parser.add_argument("--program-id", type=int, help="จำกัดเฉพาะวิชาในหลักสูตรนี้")
    parser.add_argument("--refresh", action="store_true", help="ดึงใหม่ทั้งหมด")
    parser.add_argument("--limit", type=int, help="จำกัดจำนวนวิชา (ใช้ตอนทดสอบ)")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)-7s %(name)s | %(message)s"
    )

    client = RmuClient(delay=args.delay, use_cache=not args.no_cache)
    conn = connect()
    try:
        course_ids = pending_course_ids(conn, args.program_id, args.refresh)
        if args.limit:
            course_ids = course_ids[: args.limit]

        log.info("ต้องดึง %d วิชา", len(course_ids))
        filled = empty = failed = 0

        for index, course_id in enumerate(course_ids, 1):
            try:
                detail = parse_course_detail(client, course_id)
            except Exception as exc:
                failed += 1
                log.error("courseid=%s ล้มเหลว: %s", course_id, exc)
                continue

            if not detail:
                empty += 1
                continue

            save_course_detail(conn, detail)
            if detail["description_th"]:
                filled += 1
            else:
                empty += 1

            if index % 20 == 0:
                conn.commit()
                log.info("  ...%d/%d", index, len(course_ids))

        conn.commit()
        log.info(
            "เสร็จ: มีคำอธิบาย=%d  ไม่มีคำอธิบาย=%d  ล้มเหลว=%d",
            filled,
            empty,
            failed,
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
