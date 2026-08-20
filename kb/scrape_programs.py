"""
Scraper: ลิสต์หลักสูตร + โครงสร้างหลักสูตร (public, ไม่ต้อง login)

โครงสร้างหน้า ``program_info_1.asp`` ที่ยืนยันจากของจริง (programid=59721 / MDI):

    <span onclick='javascript:toggle_row(0);'>  ...  1 หมวดศึกษาทั่วไป   30 หน่วยกิต
    <table id='TB_ROW_0'>                       ← เนื้อหาของหมวดนั้น (ซ้อนกันได้)
        <span onclick='javascript:toggle_row(1);'> ... 1.1 กลุ่มวิชาภาษา  9 หน่วยกิต
        <table id='TB_ROW_1'>
            <span onclick='...toggle_row(2)'> ... 1.1.1 กลุ่มวิชาภาษา (บังคับ) 6 หน่วยกิต
            <table id='TB_ROW_2'>
                <a href=#current onclick="window.open('class_info_5.asp?courseid=32701...')">
                    1109901</a>  ← รายวิชา

ความสัมพันธ์ parent/child หาได้จากการเช็คว่า ``TB_ROW_N`` ซ้อนอยู่ใน ``TB_ROW_M`` ตัวไหน
ไม่ควรเดาจากเลขข้อ (เช่น 1.1.1) เพราะบางหลักสูตรเว้นเลขไม่ต่อเนื่อง

*สิ่งที่หน้านี้ไม่มี* (ตรวจแล้วได้ 0 ผลลัพธ์ทุกคำ): ``บังคับก่อน``, ``ปีที่``,
``ภาคการศึกษา``, ``แผนการเรียน`` → prerequisite/แผนเทอมต้องกรอกมือจาก มคอ.2
ลงตาราง ``prerequisites`` / ``curriculum_rules``
"""

from __future__ import annotations

import argparse
import logging
import re
from datetime import datetime, timezone

from bs4 import Tag

from .client import BASE_URL, RmuClient, clean, parse_credits
from .schema import connect

log = logging.getLogger("rmu.programs")

TOGGLE_RE = re.compile(r"toggle_row\((\d+)\)")
COURSEID_RE = re.compile(r"courseid=(\d+)")
# 'program_info_1.asp?f_cmd=2&levelid=31&programid=59721&facultyid=70&...'
PROGRAM_LINK_RE = re.compile(r"program_info_1\.asp\?([^\"'>\s]+)")
# ชื่อในลิงก์มาแบบ '643170151-การจัดการนวัตกรรมดิจิทัล'
PROGRAM_NAME_RE = re.compile(r"^(\d+)\s*-\s*(.*)$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── ลิสต์หลักสูตรของคณะ ──────────────────────────────────────────────────────


def list_programs(client: RmuClient, faculty_id: str) -> list[dict]:
    """
    คืนลิสต์หลักสูตรของคณะ โดย POST ``facultyid`` ไปที่ ``program_info.asp``

    ต้องใช้ POST เพราะหน้านี้ใช้ ``<SELECT onchange=submit()>``
    """
    client.warmup()
    soup = client.soup(
        "program_info.asp",
        {"facultyid": faculty_id, "f_cmd": ""},
        method="POST",
        use_cache=False,  # ผลลัพธ์ผูกกับ session ไม่ควร cache
    )

    programs: dict[int, dict] = {}
    for a in soup.find_all("a", href=PROGRAM_LINK_RE):
        href = a.get("href", "")
        params = dict(
            part.split("=", 1)
            for part in href.split("?", 1)[1].split("&")
            if "=" in part
        )
        program_id = params.get("programid")
        if not program_id:
            continue

        raw_name = clean(params.get("programname", "").replace("+", " "))
        match = PROGRAM_NAME_RE.match(raw_name)
        code, name = (match.group(1), match.group(2)) if match else ("", raw_name)

        programs[int(program_id)] = {
            "program_id": int(program_id),
            "faculty_id": faculty_id,
            "level_id": params.get("levelid", ""),
            "program_code": code,
            "program_name": name,
            "degree_name": clean(params.get("degreename", "").replace("+", " ")),
            "department_name": clean(
                params.get("departmentname", "").replace("+", " ")
            ),
            "label": clean(a.get_text()),
        }

    log.info("คณะ %s: พบ %d หลักสูตร", faculty_id, len(programs))
    return sorted(programs.values(), key=lambda p: p["program_id"])


# ── โครงสร้างหลักสูตร ────────────────────────────────────────────────────────


def _header_info(soup) -> dict:
    """ดึง คณะ / ระดับการศึกษา จากตารางหัวเรื่อง (label : value)"""
    info: dict[str, str] = {}
    wanted = {
        "คณะ": "faculty_name",
        "ระดับการศึกษา": "level_name",
        "หลักสูตร": "program_title",
        "ภาควิชา": "department_name",
        "สาขาวิชา": "major_name",
    }
    for td in soup.find_all("td", class_=re.compile("HeaderDetail", re.I)):
        label = clean(td.get_text()).rstrip(":")
        key = wanted.get(label)
        if not key:
            continue
        sibling = td.find_next_sibling("td")
        if sibling:
            info[key] = clean(sibling.get_text()).lstrip(": ").strip()
    return info


def _selection_mode(label: str) -> str | None:
    """เดาว่าหมวดนี้ 'เรียนทุกวิชา' หรือ 'เลือกให้ครบหน่วยกิต' จากชื่อหมวด"""
    if "บังคับ" in label:
        return "required"
    if "เลือก" in label:
        return "elective"
    return None


def parse_program_structure(client: RmuClient, program: dict) -> dict:
    """
    ดึงโครงสร้างหลักสูตร 1 หลักสูตร

    คืน dict: ``{program, categories, courses, links}``
    โดย ``links`` = (category_row_id, course_id, position)
    """
    params = {
        "f_cmd": "2",
        "levelid": program["level_id"],
        "programid": program["program_id"],
        "facultyid": program["faculty_id"],
    }
    soup = client.soup("program_info_1.asp", params)
    source_url = f"{BASE_URL}/program_info_1.asp?" + "&".join(
        f"{k}={v}" for k, v in params.items()
    )

    # ── หมวด: span onclick=toggle_row(N) → label + หน่วยกิต ──────────────────
    categories: dict[int, dict] = {}
    for span in soup.find_all("span", onclick=TOGGLE_RE):
        match = TOGGLE_RE.search(span.get("onclick", ""))
        if not match:
            continue
        row_id = int(match.group(1))

        tr = span.find_parent("tr")
        if tr is None:
            continue
        cells = tr.find_all("td")
        label = clean(cells[0].get_text()) if cells else ""
        credit_text = clean(cells[1].get_text()) if len(cells) > 1 else ""

        number_match = re.match(r"^([\d.]+)\s+(.*)$", label)
        number = number_match.group(1).rstrip(".") if number_match else None
        title = number_match.group(2) if number_match else label

        categories[row_id] = {
            "row_id": row_id,
            "number": number,
            "depth": number.count(".") if number else 0,
            "label": title,
            "required_credits": parse_credits(credit_text),
            "parent_row_id": None,
            "is_leaf": 0,
            "selection_mode": _selection_mode(title),
        }

    # ── parent: TB_ROW_N ที่ซ้อนอยู่ใน TB_ROW_M ตัวที่ใกล้สุด ────────────────
    for row_id in categories:
        table = soup.find("table", id=f"TB_ROW_{row_id}")
        if table is None:
            continue
        for ancestor in table.parents:
            if not isinstance(ancestor, Tag):
                continue
            ancestor_id = ancestor.get("id", "")
            if ancestor.name == "table" and ancestor_id.startswith("TB_ROW_"):
                parent = int(ancestor_id.removeprefix("TB_ROW_"))
                if parent in categories:
                    categories[row_id]["parent_row_id"] = parent
                break

    # ── รายวิชา: ผูกกับหมวดที่ "ลึกสุด" ที่ครอบมันอยู่ ────────────────────────
    courses: dict[int, dict] = {}
    links: list[tuple[int, int, int]] = []
    position_counter: dict[int, int] = {}

    for anchor in soup.find_all("a", onclick=COURSEID_RE):
        match = COURSEID_RE.search(anchor.get("onclick", ""))
        if not match:
            continue
        course_id = int(match.group(1))
        code = clean(anchor.get_text())

        tr = anchor.find_parent("tr")
        cells = tr.find_all("td") if tr else []
        # td[1]=รหัส, td[2]='<EN><br><TH>', td[3]='3 (2-2-5)'
        name_cell = cells[2] if len(cells) > 2 else None
        credits_text = clean(cells[3].get_text()) if len(cells) > 3 else ""

        name_en = name_th = ""
        if name_cell is not None:
            lines = [
                clean(part)
                for part in name_cell.get_text("\n").split("\n")
                if clean(part)
            ]
            if lines:
                name_en = lines[0]
            if len(lines) > 1:
                name_th = lines[1]

        courses.setdefault(
            course_id,
            {
                "course_id": course_id,
                "course_code": code.split("-")[0],
                "name_en": name_en,
                "name_th": name_th,
                "credits_text": credits_text,
                "credits": parse_credits(credits_text),
            },
        )

        # หมวดที่ลึกสุดที่ครอบวิชานี้อยู่
        owner: int | None = None
        for ancestor in anchor.parents:
            if not isinstance(ancestor, Tag):
                continue
            ancestor_id = ancestor.get("id", "")
            if ancestor.name == "table" and ancestor_id.startswith("TB_ROW_"):
                candidate = int(ancestor_id.removeprefix("TB_ROW_"))
                if candidate in categories:
                    owner = candidate
                    break
        if owner is None:
            log.warning("วิชา %s ไม่พบหมวดที่ครอบอยู่ — ข้าม", code)
            continue

        position_counter[owner] = position_counter.get(owner, 0) + 1
        links.append((owner, course_id, position_counter[owner]))
        categories[owner]["is_leaf"] = 1

    header = _header_info(soup)
    total = sum(
        c["required_credits"] or 0 for c in categories.values() if c["depth"] == 0
    )

    program_row = {
        **program,
        "faculty_name": header.get("faculty_name", ""),
        "level_name": header.get("level_name", ""),
        "total_credits": total,
        "source_url": source_url,
    }

    log.info(
        "หลักสูตร %s (%s): %d หมวด, %d วิชา, รวม %d หน่วยกิต",
        program.get("program_code") or program["program_id"],
        program.get("program_name", ""),
        len(categories),
        len(courses),
        total,
    )
    return {
        "program": program_row,
        "categories": list(categories.values()),
        "courses": list(courses.values()),
        "links": links,
    }


# ── บันทึกลง DB ─────────────────────────────────────────────────────────────


def save_program(conn, parsed: dict) -> None:
    now = _now()
    program = parsed["program"]

    conn.execute(
        """
        INSERT INTO programs (program_id, faculty_id, level_id, program_code,
                              program_name, faculty_name, level_name, degree_name,
                              department_name, total_credits, source_url, scraped_at)
        VALUES (:program_id, :faculty_id, :level_id, :program_code,
                :program_name, :faculty_name, :level_name, :degree_name,
                :department_name, :total_credits, :source_url, :scraped_at)
        ON CONFLICT(program_id) DO UPDATE SET
            program_code = excluded.program_code,
            program_name = excluded.program_name,
            faculty_name = excluded.faculty_name,
            level_name = excluded.level_name,
            total_credits = excluded.total_credits,
            source_url = excluded.source_url,
            scraped_at = excluded.scraped_at
        """,
        {
            "faculty_name": "",
            "level_name": "",
            "degree_name": "",
            "department_name": "",
            **program,
            "scraped_at": now,
        },
    )

    program_id = program["program_id"]
    conn.execute("DELETE FROM categories WHERE program_id = ?", (program_id,))
    conn.executemany(
        """
        INSERT INTO categories (program_id, row_id, parent_row_id, number, depth,
                                label, required_credits, is_leaf, selection_mode)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                program_id,
                c["row_id"],
                c["parent_row_id"],
                c["number"],
                c["depth"],
                c["label"],
                c["required_credits"],
                c["is_leaf"],
                c["selection_mode"],
            )
            for c in parsed["categories"]
        ],
    )

    conn.executemany(
        """
        INSERT INTO courses (course_id, course_code, name_th, name_en,
                             credits_text, credits, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(course_id) DO UPDATE SET
            course_code  = excluded.course_code,
            name_th      = COALESCE(NULLIF(excluded.name_th, ''), courses.name_th),
            name_en      = COALESCE(NULLIF(excluded.name_en, ''), courses.name_en),
            credits_text = excluded.credits_text,
            credits      = excluded.credits,
            scraped_at   = excluded.scraped_at
        """,
        [
            (
                c["course_id"],
                c["course_code"],
                c["name_th"],
                c["name_en"],
                c["credits_text"],
                c["credits"],
                now,
            )
            for c in parsed["courses"]
        ],
    )

    conn.execute("DELETE FROM program_courses WHERE program_id = ?", (program_id,))
    conn.executemany(
        """
        INSERT OR REPLACE INTO program_courses
            (program_id, category_row_id, course_id, position)
        VALUES (?, ?, ?, ?)
        """,
        [(program_id, row_id, cid, pos) for row_id, cid, pos in parsed["links"]],
    )
    conn.commit()


# ── CLI ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ดึงโครงสร้างหลักสูตรจาก regis.rmu.ac.th (public)"
    )
    parser.add_argument("--faculty", default="70", help="รหัสคณะ (70 = เทคโนโลยีสารสนเทศ)")
    parser.add_argument(
        "--program-id", type=int, action="append", help="เจาะจง programid (ใส่ซ้ำได้)"
    )
    parser.add_argument("--list-only", action="store_true", help="แสดงลิสต์หลักสูตรแล้วจบ")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)-7s %(name)s | %(message)s"
    )

    client = RmuClient(delay=args.delay, use_cache=not args.no_cache)
    programs = list_programs(client, args.faculty)

    if args.list_only:
        for p in programs:
            print(
                f"  programid={p['program_id']:<6} level={p['level_id']:<3} "
                f"{p['program_code']:<12} {p['program_name']}"
            )
        return

    if args.program_id:
        wanted = set(args.program_id)
        programs = [p for p in programs if p["program_id"] in wanted]
        if not programs:
            raise SystemExit(f"ไม่พบ programid {sorted(wanted)} ในคณะ {args.faculty}")

    conn = connect()
    try:
        for program in programs:
            parsed = parse_program_structure(client, program)
            save_program(conn, parsed)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
