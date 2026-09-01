from datetime import date
from app.activities import thai_date, thai_date_range, normalize_status, activities_flex_message

def test_thai_months_and_cross_year():
    assert thai_date("01 ม.ค. 2569") == date(2026, 1, 1)
    assert thai_date("01 ก.พ. 2569") == date(2026, 2, 1)
    assert thai_date("01 มี.ค. 2569") == date(2026, 3, 1)
    assert thai_date("01 เม.ย. 2569") == date(2026, 4, 1)
    assert thai_date("01 พ.ค. 2569") == date(2026, 5, 1)
    assert thai_date("วันที่04 มิ.ย. 2569") == date(2026, 6, 4)
    assert thai_date("01 ก.ค. 2569") == date(2026, 7, 1)
    assert thai_date("01 ส.ค. 2569") == date(2026, 8, 1)
    assert thai_date("01 ก.ย. 2569") == date(2026, 9, 1)
    assert thai_date("01 ต.ค. 2569") == date(2026, 10, 1)
    assert thai_date("01 พ.ย. 2569") == date(2026, 11, 1)
    assert thai_date("01 ธ.ค. 2569") == date(2026, 12, 1)
    assert thai_date_range("วันที่04 มิ.ย. 2569 - 28 ก.พ. 2570") == (date(2026, 6, 4), date(2027, 2, 28))

def test_status_and_empty_flex():
    assert normalize_status("กำลังรับสมัคร") == "open"
    assert normalize_status("รับสมัครในอีกไม่นาน") == "upcoming"
    assert normalize_status("ปิดรับสมัครแล้ว") == "closed"
    assert activities_flex_message({})["type"] == "text"

def test_flex_caps_carousel_at_12():
    rows = [{"title": str(i), "detail_url": "https://example.test"} for i in range(20)]
    msg = activities_flex_message(rows)
    assert len(msg["contents"]["contents"]) == 12
