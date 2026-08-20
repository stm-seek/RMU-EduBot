"""
Scraper: ข้อมูลอาจารย์ (``itrmu.org/academic_staff.php``)

โครงสร้างหน้า (Bootstrap 5) ที่ยืนยันจากของจริง::

    <h3 class="text-center mb-4 text-primary">สาขาเทคโนโลยีสารสนเทศ (IT)</h3>
    <div class="row">
      <div class="col-md-5">...รูป...</div>
      <div class="col-md-7">
        <h4 class="mb-3">อาจารย์ ดร.วีระพน ภานุรักษ์</h4>
        <h5 class="mb-3">ประธานหลักสูตรเทคโนโลยีสารสนเทศ</h5>
        <h5 class="mb-3"><span class="text-secondary">Email : panurag2562@gmail.com</span></h5>
      </div>
    </div>

**ข้อจำกัดสำคัญ:** Requirement ข้อ 7 ขอ 9 ฟิลด์ (ชื่อ, ตำแหน่ง, สาขา, email,
เบอร์โทร, อาคาร, ชั้น, ห้องพัก, เวลาติดต่อ) แต่เว็บมีแค่ **4 ฟิลด์แรก**
→ ``phone`` / ``building`` / ``floor`` / ``room`` / ``office_hours`` เป็น NULL
บอทต้องตอบว่า "ยังไม่มีข้อมูลในระบบ" ห้ามเดา

**PDPA:** อีเมลหลายคนเป็น gmail/hotmail ส่วนตัว → มีธง ``is_personal_email``
ในรายงาน เพื่อให้ตัดสินใจได้ว่าจะเผยแพร่ผ่านบอทหรือไม่

อาจารย์ 1 คนอยู่ได้หลายสาขา (เช่น ดร.ธารีชล ดงสงคราม อยู่ 3 กลุ่ม)
จึงแยกตาราง ``instructor_affiliations`` แบบ many-to-many
"""

from __future__ import annotations

import argparse
import logging
import re
import warnings
from datetime import datetime, timezone

import requests
import urllib3
from bs4 import BeautifulSoup

from .schema import connect

warnings.simplefilter("ignore")
urllib3.disable_warnings()

log = logging.getLogger("rmu.instructors")

STAFF_URL = "https://www.itrmu.org/academic_staff.php"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

# คำนำหน้า/ยศ ที่ต้องตัดออกเพื่อ normalize ชื่อ (เรียงจากยาวไปสั้น สำคัญ!)
TITLE_PREFIXES = [
    "ผู้ช่วยศาสตราจารย์",
    "รองศาสตราจารย์",
    "ศาสตราจารย์",
    "อาจารย์",
    "อาจาร",  # พบ typo จริงในเว็บ
    "ผศ.",
    "รศ.",
    "ศ.",
    "ดร.",
    "นาย",
    "นาง",
    "นางสาว",
]

# รหัสสาขาจากวงเล็บท้ายหัวข้อ เช่น 'สาขาเทคโนโลยีสารสนเทศ (IT)'
# ต้องเป็น A-Z ล้วน (2-5 ตัว) เพื่อไม่ให้จับ '(ปร.ด.การจัดการเทคโนโลยี)' ที่เป็นไทย
GROUP_CODE_RE = re.compile(r"\(([A-Z]{2,5})\)\s*$")

PERSONAL_EMAIL_DOMAINS = ("gmail.com", "hotmail.com", "yahoo.com", "outlook.com")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean(text: str | None) -> str:
    return " ".join((text or "").replace("\xa0", " ").split())


def normalize_name(full_name: str) -> str:
    """
    ตัดคำนำหน้า/ยศออก เหลือชื่อ-นามสกุล เพื่อใช้ค้นหาและ match กับ offerings

    >>> normalize_name('ผู้ช่วยศาสตราจารย์ ดร.ธรัช อารีราษฎร์')
    'ธรัช อารีราษฎร์'
    >>> normalize_name('อาจารย์วินัย โกหลำ')
    'วินัย โกหลำ'
    >>> normalize_name('อาจาร ดร.ชนะชัย อวนวัง')
    'ชนะชัย อวนวัง'

    ชื่อจากตารางสอน (``offerings.instructors``) เขียนไม่เหมือนเว็บคณะ
    ต้อง normalize ให้เทียบกันได้:

    >>> normalize_name('ดร .วาริธ ราศรี')       # มีช่องว่างก่อนจุด
    'วาริธ ราศรี'
    >>> normalize_name('อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์')  # มี X แทรก (ข้อมูลสกปรก)
    'นิภาภรณ์ จงวุฒิเวศย์'
    """
    name = clean(full_name)
    # 'ดร .วาริธ' → 'ดร.วาริธ'
    name = re.sub(r"\s+\.", ".", name)

    changed = True
    while changed:
        changed = False
        for prefix in TITLE_PREFIXES:
            if name.startswith(prefix):
                name = name[len(prefix) :].lstrip(" .")
                changed = True
                break

    # ข้อมูลสกปรกจากตารางสอน: อักษรละตินเดี่ยวติดหน้าชื่อไทย ('Xนิภาภรณ์')
    # ทำหลังตัดคำนำหน้า เพราะ X อยู่หลัง 'อาจารย์' ไม่ใช่ต้นสตริง
    name = re.sub(r"^[A-Za-z](?=[\u0E00-\u0E7F])", "", name)
    return clean(name)


def extract_title_prefix(full_name: str) -> str:
    """คืนคำนำหน้าที่ถูกตัดออกไป"""
    name = clean(full_name)
    normalized = normalize_name(name)
    return clean(name[: len(name) - len(normalized)].rstrip(" ."))


def parse_staff_page(html: str) -> list[dict]:
    """
    แยกข้อมูลอาจารย์ออกจากหน้า HTML

    เดินจาก ``h3`` (หัวข้อกลุ่ม) ลงไปเก็บ ``h4`` (ชื่อ) ที่อยู่ถัดจากมัน
    จนกว่าจะเจอ ``h3`` ตัวถัดไป
    """
    soup = BeautifulSoup(html, "lxml")
    records: list[dict] = []
    current_group = ""

    # ไล่ตามลำดับที่ปรากฏในเอกสาร เพื่อรู้ว่า h4 อยู่ใต้ h3 ตัวไหน
    for tag in soup.find_all(["h3", "h4"]):
        if tag.name == "h3":
            current_group = clean(tag.get_text(" "))
            continue

        full_name = clean(tag.get_text(" "))
        if not full_name:
            continue

        # h5 ที่ตามหลัง h4 ตัวนี้ = ตำแหน่ง แล้วต่อด้วย Email
        position = email = ""
        for sibling in tag.find_next_siblings(["h4", "h5"]):
            if sibling.name == "h4":
                break  # เจออาจารย์คนถัดไปแล้ว
            text = clean(sibling.get_text(" "))
            if text.startswith("Email"):
                email = clean(text.split(":", 1)[1]) if ":" in text else ""
            elif not position:
                position = text

        match = GROUP_CODE_RE.search(current_group)
        records.append(
            {
                "full_name": full_name,
                "name_normalized": normalize_name(full_name),
                "title_prefix": extract_title_prefix(full_name),
                "email": email,
                "group_name": current_group,
                "group_code": match.group(1).strip() if match else "",
                "position": position,
                "is_chair": 1 if "ประธาน" in position else 0,
            }
        )

    return records


def save_instructors(conn, records: list[dict]) -> tuple[int, int]:
    """เขียน instructors + instructor_affiliations — คืน (จำนวนคน, จำนวนสังกัด)"""
    now = _now()
    people = 0

    for record in records:
        cursor = conn.execute(
            """
            INSERT INTO instructors (full_name, name_normalized, title_prefix,
                                     email, source_url, scraped_at)
            VALUES (:full_name, :name_normalized, :title_prefix,
                    :email, :source_url, :scraped_at)
            ON CONFLICT(full_name) DO UPDATE SET
                name_normalized = excluded.name_normalized,
                title_prefix    = excluded.title_prefix,
                -- ไม่ให้ค่าว่างจากเว็บไปลบอีเมลที่เคยได้มา
                email           = COALESCE(NULLIF(excluded.email, ''), instructors.email),
                source_url      = excluded.source_url,
                scraped_at      = excluded.scraped_at
            RETURNING id
            """,
            {**record, "source_url": STAFF_URL, "scraped_at": now},
        )
        instructor_id = cursor.fetchone()[0]
        people += 1

        conn.execute(
            """
            INSERT INTO instructor_affiliations (instructor_id, group_name,
                                                 group_code, position, is_chair)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(instructor_id, group_name, position) DO UPDATE SET
                group_code = excluded.group_code,
                is_chair   = excluded.is_chair
            """,
            (
                instructor_id,
                record["group_name"],
                record["group_code"],
                record["position"],
                record["is_chair"],
            ),
        )

    conn.commit()
    n_people = conn.execute("SELECT COUNT(*) FROM instructors").fetchone()[0]
    n_affil = conn.execute("SELECT COUNT(*) FROM instructor_affiliations").fetchone()[0]
    return n_people, n_affil


def cross_check_offerings(conn) -> None:
    """
    เทียบชื่ออาจารย์จาก ``offerings.instructors`` (คนที่ *สอนจริง*)
    กับรายชื่อในเว็บคณะ → หาคนที่สอนแต่ไม่มีในเว็บ (ข้อมูลเว็บไม่ครบ)
    """
    known = {
        r[0] for r in conn.execute("SELECT name_normalized FROM instructors")
    }
    teaching: dict[str, int] = {}

    for row in conn.execute(
        "SELECT instructors FROM offerings WHERE instructors <> ''"
    ):
        for raw in row[0].split(" | "):
            name = normalize_name(raw)
            if name:
                teaching[name] = teaching.get(name, 0) + 1

    missing = {n: c for n, c in teaching.items() if n not in known}
    print(f"\nอาจารย์ที่สอนจริงในตารางสอน: {len(teaching)} คน")
    print(f"  มีในเว็บคณะ IT   : {len(teaching) - len(missing)} คน")
    print(f"  ไม่มีในเว็บคณะ IT : {len(missing)} คน (ส่วนใหญ่คือวิชา GE ของคณะอื่น)")
    if missing:
        print("\n  ตัวอย่างคนที่สอนแต่ไม่มีในเว็บ (เรียงตามจำนวนหมู่ที่สอน)")
        for name, count in sorted(missing.items(), key=lambda kv: -kv[1])[:12]:
            print(f"    {count:>3} หมู่  {name}")


def report(conn) -> None:
    print("\nอาจารย์แยกตามกลุ่ม")
    print("-" * 96)
    for row in conn.execute(
        """
        SELECT a.group_name, COUNT(DISTINCT a.instructor_id) AS n,
               SUM(CASE WHEN i.email IS NULL OR i.email = '' THEN 1 ELSE 0 END) AS no_email
          FROM instructor_affiliations a
          JOIN instructors i ON i.id = a.instructor_id
         GROUP BY a.group_name ORDER BY a.group_name
        """
    ):
        print(f"  {row['group_name'][:62]:<62} {row['n']:>3} คน  ไม่มีอีเมล={row['no_email'] or 0}")

    total = conn.execute("SELECT COUNT(*) FROM instructors").fetchone()[0]
    print(f"\n  รวมอาจารย์ไม่ซ้ำ: {total} คน")

    print("\nอาจารย์ที่สังกัดหลายกลุ่ม")
    print("-" * 96)
    for row in conn.execute(
        """
        SELECT i.full_name, COUNT(*) AS n,
               GROUP_CONCAT(
                   CASE WHEN a.group_code <> '' THEN a.group_code ELSE a.group_name END,
                   ' / '
               ) AS groups
          FROM instructors i
          JOIN instructor_affiliations a ON a.instructor_id = i.id
         GROUP BY i.id HAVING n > 1 ORDER BY n DESC
        """
    ):
        print(f"  {row['full_name'][:44]:<44} {row['n']} กลุ่ม  {row['groups'][:44]}")

    # ── ความครบถ้วนของฟิลด์ที่ Requirement ข้อ 7 ต้องการ ────────────────────
    print("\nความครบถ้วนของข้อมูลติดต่อ (Requirement ข้อ 7)")
    print("-" * 96)
    fields = [
        ("ชื่อ", "full_name"),
        ("ตำแหน่ง", None),
        ("สาขา", None),
        ("Email", "email"),
        ("เบอร์โทรศัพท์", "phone"),
        ("อาคาร", "building"),
        ("ชั้น", "floor"),
        ("ห้องพัก", "room"),
        ("เวลาที่ติดต่อได้", "office_hours"),
    ]
    for label, column in fields:
        if column is None:
            print(f"  {label:<18} มีครบ (จาก instructor_affiliations)")
            continue
        filled = conn.execute(
            f"SELECT COUNT(*) FROM instructors WHERE {column} IS NOT NULL AND {column} <> ''"
        ).fetchone()[0]
        flag = "" if filled else "   <-- เว็บไม่มี ต้องกรอกมือ"
        print(f"  {label:<18} {filled}/{total}{flag}")

    # ── PDPA: อีเมลส่วนตัว ──────────────────────────────────────────────────
    personal = conn.execute(
        "SELECT full_name, email FROM instructors WHERE "
        + " OR ".join(f"email LIKE '%{d}'" for d in PERSONAL_EMAIL_DOMAINS)
    ).fetchall()
    if personal:
        print(f"\nอีเมลส่วนตัว (ไม่ใช่ @rmu.ac.th) — {len(personal)} คน  [ต้องพิจารณา PDPA]")
        print("-" * 96)
        for row in personal:
            print(f"  {row['full_name'][:50]:<50} {row['email']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ดึงข้อมูลอาจารย์จาก itrmu.org (public)"
    )
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument(
        "--cross-check", action="store_true", help="เทียบกับอาจารย์ที่สอนจริงใน offerings"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)-7s %(name)s | %(message)s"
    )

    conn = connect()
    try:
        if not args.report_only:
            resp = requests.get(STAFF_URL, timeout=30, headers=HEADERS, verify=False)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"

            records = parse_staff_page(resp.text)
            log.info("parse ได้ %d รายการ (คน x กลุ่ม)", len(records))

            people, affil = save_instructors(conn, records)
            log.info("บันทึกแล้ว: %d คน, %d สังกัด", people, affil)

        report(conn)
        if args.cross_check:
            cross_check_offerings(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
