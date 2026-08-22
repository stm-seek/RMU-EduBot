"""
Scraper: เอกสาร/แบบฟอร์ม/ลิงก์ที่นักศึกษาต้องใช้

ทำ 2 อย่าง:

1. **seed** ลิงก์ที่คัดมาแล้วด้วยมือ (``SEED_DOCUMENTS``) — คัดจากผล crawl จริง
   แล้วกรองเอาแต่ของที่ *นักศึกษา* ใช้ ทิ้งเอกสารบุคลากรทั้งหมด
   (แผน KM, SAR/CAR, แผนบริหารความเสี่ยง, ข้อตกลงปฏิบัติราชการ ฯลฯ)
   เพราะถ้าโยนเข้าไปหมด บอทจะตอบเอกสารผิดกลุ่มให้นักศึกษา

2. **crawl** หน้าที่กำหนด เพื่อหาลิงก์ใหม่ที่ยังไม่มีใน seed (``--crawl``)

ทุกลิงก์จะถูก **ตรวจสอบว่าเข้าได้จริง** (HEAD/GET) ก่อนบันทึก ``is_available``
เพราะเว็บ RMU ล่มบ่อย และบางลิงก์ในเว็บพิมพ์ผิด เช่น
``http://https://sci.rmu.ac.th/...`` (URL ซ้อน URL — พบจริงในหน้า sci.rmu)
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

log = logging.getLogger("rmu.documents")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "th,en;q=0.8",
}

# ── ลิงก์ที่คัดแล้วว่านักศึกษาใช้จริง ─────────────────────────────────────────
# (category, title, url, doc_type, keywords)
SEED_DOCUMENTS: list[tuple[str, str, str, str, str]] = [
    # ── การลงทะเบียน / คำร้อง ────────────────────────────────────────────────
    (
        "registration",
        "เอกสารขอเพิ่มรายวิชาเรียน",
        "https://sci.rmu.ac.th/wp-content/uploads/2024/08/เอกสารขอเพิ่มรายวิชาเรียน.pdf",
        "pdf",
        "เพิ่มวิชา,เพิ่มรายวิชา,ขอเพิ่มวิชา,ลงวิชาเพิ่ม,แอดวิชา",
    ),
    (
        "registration",
        "เอกสารขอยืนยันลงทะเบียนเรียน (ล่าช้า)",
        "https://sci.rmu.ac.th/wp-content/uploads/2024/08/เอกสารขอยืนยันลงทะเบียนเรียนล่าช้า.pdf",
        "pdf",
        "ลงทะเบียนล่าช้า,ยืนยันลงทะเบียน,ลงทะเบียนช้า,ลืมลงทะเบียน",
    ),
    (
        "registration",
        "เอกสารขอขยายหน่วยกิต",
        "https://sci.rmu.ac.th/wp-content/uploads/2024/08/เอกสารขอขยายหน่วยกิต.pdf",
        "pdf",
        "ขยายหน่วยกิต,ลงเกินหน่วยกิต,หน่วยกิตเกิน,ลงเกิน",
    ),
    (
        "registration",
        "เอกสารขอเปิดรายวิชาเรียน (ปรับปรุง 2568)",
        "https://sci.rmu.ac.th/wp-content/uploads/2025/06/เอกสารขอเปิดรายวิชาเรียน-ปรับปรุง2568.pdf",
        "pdf",
        "ขอเปิดวิชา,เปิดรายวิชา,ขอเปิดรายวิชา,วิชาไม่เปิด",
    ),
    # ── กู้ยืมเงิน กยศ. / กรอ. ───────────────────────────────────────────────
    (
        "loan",
        "101 แบบคำขอกู้ยืมเงิน",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/101-แบบคำขอกู้ยืมเงิน.pdf",
        "pdf",
        "กู้ยืม,กยศ,แบบคำขอกู้,ขอกู้เงิน,กู้เรียน,เงินกู้",
    ),
    (
        "loan",
        "102 หนังสือรับรองรายได้ครอบครัว (กยศ.)",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/102-หนังสือรับรองรายได้ครอบครัว-กยศ.pdf",
        "pdf",
        "รับรองรายได้,กยศ,รายได้ครอบครัว,หนังสือรับรองรายได้",
    ),
    (
        "loan",
        "103 หนังสือรับรองรายได้ครอบครัว (กรอ.)",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/102-หนังสือรับรองรายได้ครอบครัว-กรอ.pdf",
        "pdf",
        "รับรองรายได้,กรอ,รายได้ครอบครัว",
    ),
    (
        "loan",
        "104 หนังสือแสดงความคิดเห็นของอาจารย์ที่ปรึกษา",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/103-หนังสือแสดงความคิดเห็นของอาจารย์ที่ปรึกษา.pdf",
        "pdf",
        "อาจารย์ที่ปรึกษา,ความคิดเห็นอาจารย์,กยศ",
    ),
    (
        "loan",
        "105 บันทึกข้อตกลงต่อท้ายสัญญากู้ยืม",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/104-บันทึกข้อตกลงต่อท้ายสัญญากู้ยืม.doc",
        "doc",
        "สัญญากู้ยืม,บันทึกข้อตกลง,ต่อท้ายสัญญา",
    ),
    (
        "loan",
        "106 แบบรายงานข้อมูลผู้กู้ยืมเงิน",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/108-แบบรายงานข้อมูลผู้กู้ยืมเงิน.pdf",
        "pdf",
        "รายงานข้อมูลผู้กู้,ผู้กู้ยืม,กยศ",
    ),
    (
        "loan",
        "107 แบบฟอร์มบันทึกกิจกรรมจิตอาสา",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/107-แบบฟอร์มบันทึกกิจกรรมจิตอาสา.docx",
        "docx",
        "จิตอาสา,ชั่วโมงจิตอาสา,กิจกรรมจิตอาสา,กยศ ชั่วโมง",
    ),
    (
        "loan",
        "108 กยศ. แบบรายงานสถานภาพการศึกษา",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/กยศ-แบบรายงานสถานภาพการศึกษา.pdf",
        "pdf",
        "สถานภาพการศึกษา,กยศ,รายงานสถานภาพ",
    ),
    (
        "loan",
        "109 กรอ. แบบรายงานสถานภาพการศึกษา",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/กรอ-แบบรายงานสถานภาพการศึกษา.pdf",
        "pdf",
        "สถานภาพการศึกษา,กรอ,รายงานสถานภาพ",
    ),
    (
        "loan",
        "110 ตัวอย่างการทำสัญญา กยศ. กับธนาคารอิสลาม",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/105-ตัวอย่างการทำสัญญา-กยศ-กับธนาคารอิสลาม.pdf",
        "pdf",
        "ทำสัญญา,ธนาคารอิสลาม,กยศ,ตัวอย่างสัญญา",
    ),
    (
        "loan",
        "111 ตัวอย่างการทำสัญญา กรอ. กับธนาคารอิสลาม",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/07/105-ตัวอย่างการทำสัญญา-กรอ-กับธนาคารอิสลาม.pdf",
        "pdf",
        "ทำสัญญา,ธนาคารอิสลาม,กรอ",
    ),
    # ── ฝึกประสบการณ์วิชาชีพ ─────────────────────────────────────────────────
    # URL เป็น percent-encoded ชื่อไทย ต้องใส่แบบนี้เท่านั้น (คัดลอกจาก href จริง)
    # หมายเหตุ: มีไฟล์ชื่อเดียวกันทั้ง .doc (404) และ .docx (200) → ใช้ .docx
    (
        "internship",
        "แบบฟอร์มแจ้งเปลี่ยนระยะเวลาการออกฝึกประสบการณ์วิชาชีพ",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/12/"
        "%E0%B9%81%E0%B8%88%E0%B9%89%E0%B8%87%E0%B9%80%E0%B8%9B%E0%B8%A5%E0%B8%B5"
        "%E0%B9%88%E0%B8%A2%E0%B8%99%E0%B8%A3%E0%B8%B0%E0%B8%A2%E0%B8%B0"
        "%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%B2%E0%B8%81%E0%B8%B2%E0%B8%A3"
        "%E0%B8%AD%E0%B8%AD%E0%B8%81%E0%B8%9D%E0%B8%B6%E0%B8%81%E0%B8%AF1.docx",
        "docx",
        "ฝึกงาน,ฝึกประสบการณ์,เปลี่ยนวันฝึกงาน,เลื่อนฝึกงาน",
    ),
    (
        "internship",
        "แบบฟอร์มประวัตินักศึกษาออกฝึกประสบการณ์วิชาชีพ",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/12/"
        "%E0%B8%9F%E0%B8%AD%E0%B8%A3%E0%B9%8C%E0%B8%A1-"
        "%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%A7%E0%B8%B1%E0%B8%95%E0%B8%B4"
        "%E0%B8%99%E0%B8%B1%E0%B8%81%E0%B8%A8%E0%B8%B6%E0%B8%81%E0%B8%A9%E0%B8%B2.doc",
        "doc",
        "ฝึกงาน,ประวัตินักศึกษา,ฝึกประสบการณ์,ฟอร์มประวัติ",
    ),
    (
        "internship",
        "แบบฟอร์มตอบกลับจากหน่วยงานที่นักศึกษาออกฝึกประสบการณ์",
        "https://sci.rmu.ac.th/wp-content/uploads/2016/12/ฟอร์ม-แบบตอบกลับ.doc",
        "doc",
        "ฝึกงาน,แบบตอบกลับ,หน่วยงานฝึกงาน,ตอบรับฝึกงาน",
    ),
    # ปฏิทินสหกิจศึกษา — คำถาม "สหกิจเริ่มเมื่อไหร่/ส่งเอกสารวันไหน" ถามหากันจริง
    # แต่ในคลังเดิมมีแค่แบบฟอร์ม ไม่มีช่วงเวลา → ใส่หน้าเว็บของศูนย์สหกิจเอง
    # (วันที่จริงอยู่ในหน้านี้ ห้ามสรุปตัวเลขลง seed เพราะเปลี่ยนทุกปีการศึกษา)
    (
        "internship",
        "ปฏิทินสหกิจศึกษา (ศูนย์สหกิจศึกษาฯ)",
        "https://coopcenter.rmu.ac.th/"
        "%E0%B8%9B%E0%B8%8F%E0%B8%B4%E0%B8%97%E0%B8%B4%E0%B8%99"
        "%E0%B8%AA%E0%B8%AB%E0%B8%81%E0%B8%B4%E0%B8%88%E0%B8%A8%E0%B8%B6%E0%B8%81%E0%B8%A9%E0%B8%B2/",
        "page",
        "สหกิจ,ปฏิทินสหกิจ,ฝึกงาน,ออกฝึก,วันส่งเอกสาร,กำหนดการสหกิจ,ฝึกประสบการณ์",
    ),
    # ── บัญชี/อีเมล มหาวิทยาลัย ──────────────────────────────────────────────
    # หมายเหตุ: ลิงก์ไฟล์ PDF เดิม (cc.rmu.ac.th/file/e-mail_std_.pdf,
    # networkRMU_std_.pdf) ตรวจแล้วได้ 404 → ใส่หน้าแรกของสำนักคอมพิวเตอร์แทน
    (
        "it_account",
        "สำนักคอมพิวเตอร์ (อีเมลมหาวิทยาลัย / บัญชีเครือข่าย / WiFi)",
        "https://cc.rmu.ac.th/",
        "page",
        "อีเมลมหาลัย,email,ขออีเมล,wifi,รหัสผ่านเน็ต,internet,เครือข่าย,อินเทอร์เน็ต",
    ),
    # ── หน้าเว็บรวมข้อมูล (ไม่ใช่ไฟล์) ───────────────────────────────────────
    (
        "registration",
        "หน้ารวมเอกสาร/คำร้องทั่วไป คณะวิทยาศาสตร์และเทคโนโลยี",
        "https://sci.rmu.ac.th/?p=6289",
        "page",
        "คำร้อง,เอกสาร,แบบฟอร์ม,ดาวน์โหลดเอกสาร",
    ),
    (
        "loan",
        "หน้ารวมข้อมูลการกู้ยืมเงินเพื่อการศึกษา",
        "https://sci.rmu.ac.th/?page_id=509",
        "page",
        "กู้ยืม,กยศ,กรอ,เงินกู้,กู้เรียน,ทุนกู้ยืม",
    ),
    (
        "calendar",
        "ปฏิทินการศึกษา (ระบบบริการการศึกษา)",
        "https://regis.rmu.ac.th/registrar/calendar.asp",
        "page",
        "ปฏิทินการศึกษา,วันเปิดเทอม,วันลงทะเบียน,วันสอบ,เดดไลน์,ถอนวิชา",
    ),
    (
        "curriculum",
        "โครงสร้างหลักสูตร (ระบบบริการการศึกษา)",
        "https://regis.rmu.ac.th/registrar/program_info.asp",
        "page",
        "หลักสูตร,โครงสร้างหลักสูตร,หน่วยกิต,วิชาบังคับ",
    ),
    (
        "curriculum",
        "ค้นหารายวิชาที่เปิดสอน (ระบบบริการการศึกษา)",
        "https://regis.rmu.ac.th/registrar/class_info.asp",
        "page",
        "วิชาเปิดสอน,ตารางเรียน,ค้นหารายวิชา,หมู่เรียน,ที่นั่ง",
    ),
    (
        "curriculum",
        "ระบบบริหารจัดการหลักสูตร (ข้อมูลหลักสูตรที่เปิดสอน)",
        "https://promo-curriculum.rmu.ac.th",
        "page",
        "หลักสูตรที่เปิดสอน,สมัครเรียน,ข้อมูลหลักสูตร",
    ),
    (
        "staff",
        "ข้อมูลบุคลากรสายวิชาการ คณะเทคโนโลยีสารสนเทศ",
        "https://www.itrmu.org/academic_staff.php",
        "page",
        "อาจารย์,ติดต่ออาจารย์,อีเมลอาจารย์,รายชื่ออาจารย์",
    ),
    (
        "scholarship",
        "ข่าวทุนการศึกษา คณะวิทยาศาสตร์และเทคโนโลยี",
        "https://sci.rmu.ac.th/?cat=6",
        "page",
        "ทุนการศึกษา,ขอทุน,สมัครทุน,ทุนเรียน",
    ),
    # หมายเหตุ: ocsc.go.th/scholarship ตอบ 403 กับ bot (มี WAF) → ตัดออก
    (
        "activity",
        "ระบบกิจกรรมนักศึกษา (e-activity)",
        "https://e-activity.rmu.ac.th",
        "page",
        "กิจกรรม,ชั่วโมงกิจกรรม,เก็บชั่วโมง,กิจกรรมนักศึกษา",
    ),
    # ── เตรียมสอบภาษาอังกฤษ (มหาลัยบังคับสอบก่อนจบบางหลักสูตร) ────────────────
    (
        "exam_prep",
        "เทคนิคการทำข้อสอบ TOEIC",
        "https://sci.rmu.ac.th/wp-content/uploads/2018/06/3-เทคนิคการทำข้อสอบ-toeic.pdf",
        "pdf",
        "toeic,สอบภาษาอังกฤษ,เทคนิคสอบ,ข้อสอบอังกฤษ",
    ),
    (
        "exam_prep",
        "แนวข้อสอบ IELTS",
        "https://sci.rmu.ac.th/wp-content/uploads/2018/06/2-ข้อสอบ-ielts.pdf",
        "pdf",
        "ielts,สอบภาษาอังกฤษ,แนวข้อสอบ",
    ),
    # ── ระเบียบ/กฎหมายที่นักศึกษาควรรู้ ──────────────────────────────────────
    (
        "regulation",
        "พ.ร.บ. คอมพิวเตอร์ ฉบับที่ 1 พ.ศ. 2550",
        "https://sci.rmu.ac.th/wp-content/uploads/2022/03/"
        "พรบ.-ว่าด้วยการกระทำความผิดทางคอมพิวเตอร์-พ.ศ.-2550.pdf",
        "pdf",
        "พรบคอมพิวเตอร์,กฎหมายคอมพิวเตอร์,พรบ 2550",
    ),
    (
        "regulation",
        "พ.ร.บ. คอมพิวเตอร์ ฉบับที่ 2 พ.ศ. 2560 (แก้ไขเพิ่มเติม)",
        "https://sci.rmu.ac.th/wp-content/uploads/2022/03/พรบ-คอมพิวเตอร์-ฉบับที่-2-2560.pdf",
        "pdf",
        "พรบคอมพิวเตอร์,กฎหมายคอมพิวเตอร์,พรบ 2560",
    ),
]

# ── หน้าที่จะ crawl หาลิงก์ใหม่ ──────────────────────────────────────────────
CRAWL_PAGES = [
    "https://sci.rmu.ac.th/?p=6289",
    "https://sci.rmu.ac.th/?page_id=509",
    "https://sci.rmu.ac.th/?page_id=443",
    "https://www.rmu.ac.th/download",
]

# กรองเอกสารบุคลากรออก — ถ้าชื่อไฟล์/label เข้าเงื่อนไขนี้ ถือว่าไม่ใช่ของนักศึกษา
STAFF_PATTERNS = re.compile(
    r"KM|SAR|CAR|แผนบริหาร|แผนปฏิบัติราชการ|แผนกลยุทธ|แผนพัฒนาคุณภาพ|"
    r"ข้อตกลง|ประกันคุณภาพ|ทวนสอบ|กลุ่มวิจัย|ตีพิมพ์|Plagiarism|Open.Access|"
    r"ขายทอดตลาด|ขายพัสดุ|เสนอขออนุมัติโครงการ|รายงานผลการดำเนินโครงการ|"
    r"กำหนดตำแหน่ง|บริการวิชาการ|มคอ\.3",
    re.I,
)

DOC_EXT_RE = re.compile(r"\.(pdf|docx?|xlsx?)(\?|$)", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def check_url(url: str, timeout: int = 20) -> dict:
    """
    ตรวจว่าลิงก์ยังเข้าได้ ใช้ GET แบบ stream (ไม่โหลดทั้งไฟล์)

    ไม่ใช้ HEAD เพราะเซิร์ฟเวอร์ RMU หลายตัวตอบ 405/500 กับ HEAD
    แต่ตอบ 200 กับ GET
    """
    result = {
        "http_status": None,
        "content_type": None,
        "content_length": None,
        "is_available": 0,
        "checked_at": _now(),
    }
    # ดัก URL พิมพ์ผิดแบบ 'http://https://...' ที่พบจริงในเว็บ sci.rmu
    if re.match(r"^https?://https?://", url):
        result["content_type"] = "INVALID_URL (ซ้อน scheme)"
        return result

    try:
        resp = requests.get(
            url, timeout=timeout, headers=HEADERS, verify=False, stream=True
        )
        result["http_status"] = resp.status_code
        result["content_type"] = resp.headers.get("Content-Type", "")[:120]
        length = resp.headers.get("Content-Length")
        result["content_length"] = int(length) if length and length.isdigit() else None
        result["is_available"] = 1 if resp.status_code == 200 else 0
        resp.close()
    except Exception as exc:
        result["content_type"] = f"ERROR: {type(exc).__name__}"
    return result


def upsert_document(conn, doc: dict, verify: bool) -> None:
    row = {
        "category": doc["category"],
        "title": doc["title"],
        "url": doc["url"],
        "doc_type": doc.get("doc_type", ""),
        "audience": doc.get("audience", "student"),
        "keywords": doc.get("keywords", ""),
        "note": doc.get("note", ""),
        "source_page": doc.get("source_page", ""),
        "http_status": None,
        "content_type": None,
        "content_length": None,
        "is_available": None,
        "checked_at": None,
        "scraped_at": _now(),
    }
    if verify:
        row.update(check_url(doc["url"]))

    conn.execute(
        """
        INSERT INTO documents (category, title, url, doc_type, audience, keywords,
                               note, source_page, http_status, content_type,
                               content_length, is_available, checked_at, scraped_at)
        VALUES (:category, :title, :url, :doc_type, :audience, :keywords,
                :note, :source_page, :http_status, :content_type,
                :content_length, :is_available, :checked_at, :scraped_at)
        ON CONFLICT(url) DO UPDATE SET
            category       = excluded.category,
            title          = excluded.title,
            doc_type       = excluded.doc_type,
            audience       = excluded.audience,
            keywords       = COALESCE(NULLIF(excluded.keywords, ''), documents.keywords),
            source_page    = excluded.source_page,
            http_status    = COALESCE(excluded.http_status, documents.http_status),
            content_type   = COALESCE(excluded.content_type, documents.content_type),
            content_length = COALESCE(excluded.content_length, documents.content_length),
            is_available   = COALESCE(excluded.is_available, documents.is_available),
            checked_at     = COALESCE(excluded.checked_at, documents.checked_at),
            scraped_at     = excluded.scraped_at
        """,
        row,
    )


def seed(conn, verify: bool) -> int:
    for category, title, url, doc_type, keywords in SEED_DOCUMENTS:
        upsert_document(
            conn,
            {
                "category": category,
                "title": title,
                "url": url,
                "doc_type": doc_type,
                "keywords": keywords,
                "audience": "student",
                "source_page": "seed (คัดด้วยมือ)",
            },
            verify,
        )
        if verify:
            log.info("  ตรวจแล้ว: %s", title[:56])
    conn.commit()
    return len(SEED_DOCUMENTS)


def crawl(conn, verify: bool) -> int:
    """หาลิงก์เอกสารใหม่ที่ยังไม่มีใน DB"""
    known = {r[0] for r in conn.execute("SELECT url FROM documents")}
    found = 0

    for page in CRAWL_PAGES:
        try:
            resp = requests.get(page, timeout=25, headers=HEADERS, verify=False)
            resp.encoding = resp.apparent_encoding or "utf-8"
        except Exception as exc:
            log.error("crawl %s ล้มเหลว: %s", page, exc)
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        for anchor in soup.find_all("a", href=True):
            url = requests.compat.urljoin(page, anchor["href"].strip())
            label = " ".join(anchor.get_text().split())
            if not DOC_EXT_RE.search(url) or url in known:
                continue
            if STAFF_PATTERNS.search(label) or STAFF_PATTERNS.search(url):
                continue

            known.add(url)
            found += 1
            upsert_document(
                conn,
                {
                    "category": "uncategorized",
                    "title": label or url.rsplit("/", 1)[-1],
                    "url": url,
                    "doc_type": DOC_EXT_RE.search(url).group(1).lower(),
                    "keywords": "",
                    "audience": "student",
                    "note": "พบจาก crawl — ต้องตรวจ category ด้วยมือ",
                    "source_page": page,
                },
                verify,
            )
            log.info("  พบใหม่: %s", (label or url)[:70])

    conn.commit()
    return found


def report(conn) -> None:
    print("\nเอกสารในฐานข้อมูล")
    print("-" * 104)
    for row in conn.execute(
        """
        SELECT category, COUNT(*) AS n,
               SUM(CASE WHEN is_available = 1 THEN 1 ELSE 0 END) AS ok,
               SUM(CASE WHEN is_available = 0 THEN 1 ELSE 0 END) AS bad
          FROM documents WHERE audience = 'student'
         GROUP BY category ORDER BY category
        """
    ):
        print(
            f"  {row['category']:<16} ทั้งหมด={row['n']:<3} "
            f"เข้าได้={row['ok'] or 0:<3} เข้าไม่ได้={row['bad'] or 0}"
        )

    broken = conn.execute(
        """
        SELECT title, url, http_status, content_type FROM documents
         WHERE is_available = 0 ORDER BY category
        """
    ).fetchall()
    if broken:
        print(f"\nลิงก์ที่เข้าไม่ได้ ({len(broken)}) — ต้องหา URL ใหม่")
        print("-" * 104)
        for row in broken:
            status = row["http_status"] or row["content_type"] or "?"
            print(f"  [{status}] {row['title'][:52]:<52} {row['url'][:56]}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="เก็บลิงก์เอกสาร/แบบฟอร์มที่นักศึกษาต้องใช้"
    )
    parser.add_argument("--crawl", action="store_true", help="crawl หาลิงก์ใหม่ด้วย")
    parser.add_argument(
        "--no-verify", action="store_true", help="ไม่ต้องตรวจว่าลิงก์เข้าได้จริง (เร็วกว่า)"
    )
    parser.add_argument("--report-only", action="store_true", help="แสดงรายงานแล้วจบ")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)-7s %(name)s | %(message)s"
    )

    conn = connect()
    try:
        if not args.report_only:
            verify = not args.no_verify
            log.info("seed เอกสารที่คัดไว้ %d รายการ (verify=%s)", len(SEED_DOCUMENTS), verify)
            n_seed = seed(conn, verify)
            log.info("seed เสร็จ: %d รายการ", n_seed)

            if args.crawl:
                log.info("crawl %d หน้า", len(CRAWL_PAGES))
                n_new = crawl(conn, verify)
                log.info("crawl เสร็จ: พบใหม่ %d รายการ", n_new)

        report(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
