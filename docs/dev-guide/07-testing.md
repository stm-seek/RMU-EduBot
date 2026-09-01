# 07 — การทดสอบ

## 7.1 ตัวเลขล่าสุด (รันจริงเมื่อ 31 สิงหาคม 2569)

```
unit test        837 ผ่าน   (ไม่ต้องมีอินเทอร์เน็ต ไม่ต้องมี Postgres — 8 วินาที)
doctest           65 ผ่าน   (ตัวอย่างในเอกสารประกอบโค้ดถูกรันจริง)
integration      100 ผ่าน  3 ตก  1 xfail   (ต้องมี Postgres จริง + seed จึงเป็น opt-in)
             ─────────
รวม            1,005 ตัว
```

คำสั่งที่ใช้ (ตัวเลขในเล่มควรรันดูเองอีกครั้งก่อนส่ง):

```powershell
$env:PYTHONUTF8='1'; python -m pytest -q                                   # unit
$env:PYTHONUTF8='1'; python -m pytest --doctest-modules app/ run.py -q     # doctest
$env:PYTHONUTF8='1'; $env:RMU_DB_TESTS='1'; python -m pytest tests/integration -q
```

ถ้าไม่ตั้ง `RMU_DB_TESTS=1` เทส integration จะขึ้น **skipped** ไม่ใช่ failed
(เจตนา: คนที่ไม่มี Postgres ต้องรันเทสได้)

### เทส integration ที่ตกอยู่ 3 ตัว (รู้สาเหตุแล้ว ไม่ใช่บั๊กของระบบ)

| เทส | สาเหตุ | ต้องทำอะไร |
|---|---|---|
| `test_00_smoke.py::test_operational_table_is_empty[faqs]` | ฐานข้อมูลที่ใช้พัฒนามีแถวทดสอบค้างอยู่ในตาราง `faqs` 1 แถว (`is_active = false`) เทสตัวนี้ตรวจว่าตารางที่ยังไม่ใช้งานต้องว่าง | ลบแถวทดสอบทิ้ง หรือรันเทสกับฐานข้อมูลที่ seed ใหม่ |
| `test_10_repository.py::test_every_repository_function_is_covered_by_this_module` | มีฟังก์ชันใหม่ `search_faqs` ใน `app/repository.py` แต่ยังไม่ถูกเพิ่มในรายชื่อ `COVERED_FUNCTIONS` ของไฟล์เทส | เขียนเทสให้ `search_faqs` แล้วเพิ่มชื่อในรายการ |
| `test_30_router.py::test_instructor_group_buttons_survive_postback_round_trip` | คำตอบเรื่องอาจารย์เปลี่ยนเป็น Flex Message แล้ว เทสยังอ่าน `messages[0]["text"]` (ของเดิมเป็นข้อความล้วน) | แก้เทสให้อ่านเนื้อหาจากโครง Flex |

> **ถ้าจะใส่ตัวเลขผลทดสอบในเล่ม** ให้แก้สามข้อนี้ก่อนแล้วรันใหม่ จะได้
> "ผ่านทั้งหมด" ซึ่งอ่านดีกว่า และตรงความจริงกว่าการรายงานเฉพาะตัวที่ผ่าน

## 7.2 unit test แยกตามไฟล์

| ไฟล์ | จำนวน | ทดสอบอะไร |
|---|---|---|
| `test_admin.py` | 226 | หน้า admin: ล็อกอิน, สิทธิ์, allowlist ตาราง, audit log, กฎเสริมของ AI |
| `test_repository.py` | 101 | SQL ทุกคำสั่งของชั้นข้อมูล (ตรวจด้วย `sqlglot` + fake connection) |
| `test_router.py` | 79 | การตัดสินใจของบอทว่าคำถามไหนไปชั้นไหน |
| `test_ai_chat.py` | 66 | โหมดปรึกษา AI: จำนวนตา, หมดเวลา, เข้า/ออกโหมด, การประกอบ system prompt |
| `test_webhook.py` | 39 | ลายเซ็น, ตอบ 200 ทันที, งานเบื้องหลัง |
| `test_progress.py` | 35 | การประกอบคำตอบเรื่องความก้าวหน้า |
| `test_llm.py` | 32 | retry, สลับโมเดลสำรอง, เพดานเวลา, error ที่ไม่ควร retry |
| `test_api.py` | 30 | `/health`, `/api/liff/*` |
| `test_line_client.py` | 28 | เรียก Messaging API (reply/push/link Rich Menu) |
| `test_gpa.py` | 28 | คำนวณเกรด/เป้า GPAX/เกียรตินิยม |
| `test_messages.py` | 25 | รูปแบบข้อความ/Quick Reply ให้ถูกข้อจำกัดของ LINE |
| `test_db.py` | 25 | connection pool |
| `test_rich_menu.py` | 23 | พิกัดปุ่ม + payload ที่ส่งขึ้น LINE |
| `test_config.py` | 19 | อ่าน `.env` + fail fast |
| `test_planner.py` | 18 | ตรรกะเลือกวิชาเทอมถัดไป |
| `test_flex.py` | 17 | Flex Message |
| `test_auth.py` | 14 | ตรวจ LIFF ID token |
| `test_signature.py` | 10 | HMAC-SHA256 ของ `X-Line-Signature` |

## 7.3 integration test (ต้องมี Postgres จริง)

| ไฟล์ | จำนวน | ทดสอบอะไร |
|---|---|---|
| `test_00_smoke.py` | 27 | schema ครบ, extension เปิดอยู่, ข้อมูล seed ครบจำนวน |
| `test_10_repository.py` | 56 | ทุก query ยิง Postgres จริงแล้วได้ผลถูก |
| `test_20_pool.py` | 9 | connection pool กับฐานข้อมูลจริง |
| `test_30_router.py` | 10 | บทสนทนาจริงตั้งแต่ข้อความ → คำตอบ |
| `test_90_restart.py` | 2 | ข้อมูลไม่หายหลังรีสตาร์ต container |

## 7.4 ทดสอบโดยไม่ต้องมีเน็ต/DB ได้อย่างไร (เขียนลงบทที่ 3 ได้)

| สิ่งที่ต้องแทน | แทนด้วย |
|---|---|
| LINE Messaging API, LLM API | `httpx.MockTransport` — ดักที่ชั้น HTTP ตรวจได้ทั้ง URL, header, body ที่ส่งออกจริง |
| ฐานข้อมูล | `FakeDatabase` ที่ implement `Protocol` เดียวกับ pool จริง (`app/db.py`) |
| ความถูกต้องของ SQL | `sqlglot` แปลง SQL ทุกคำสั่งเพื่อตรวจ syntax และนับ placeholder |
| ฟังก์ชันคำนวณ (planner, gpa) | ไม่ต้องแทนอะไร เพราะออกแบบให้ไม่แตะ I/O เลย |

**ประโยชน์ที่ได้จริง:** ชุด unit test รันจบใน ~8 วินาที ทำให้แก้โค้ดแล้วรู้ผลทันที
และรันได้บนเครื่องที่ไม่มี Docker

## 7.5 การทดสอบที่เครื่องทำแทนไม่ได้ (ต้องคนกดบนมือถือ)

1. **Rich Menu** — ไม่แสดงบน LINE for PC ต้องทดสอบบนมือถือเท่านั้น
2. **การสลับ Rich Menu 2 ใบ** — กดปรึกษา AI → เมนูเปลี่ยนเป็น 2 ปุ่ม → พิมพ์ถาม
   → กดจบการปรึกษา → กลับเป็น 6 ช่อง
3. **หน้า LIFF** — ต้องเปิดในแอป LINE จริงจึงจะมี ID token
4. **ปุ่ม Verify ใน LINE Developers Console** — ยืนยันว่า webhook ต่อติด

## 7.6 ข้อควรรู้เรื่องเทสของโปรเจกต์นี้

* `pytest.ini` ตั้ง `asyncio_mode = auto` → เทส async ทำงานได้โดยไม่ต้องใส่
  decorator ทุกตัว (ต้องมีปลั๊กอิน `pytest-asyncio` ตามที่ pin ไว้)
* **doctest ถูกรันจริง** — ตัวอย่างในคำอธิบายฟังก์ชันจึงล้าสมัยไม่ได้
  ถ้าแก้พฤติกรรมแล้วลืมแก้ตัวอย่าง เทสจะแดง
* เคยมีบทเรียน: **เทสบางตัวเคย "ล็อกบั๊กเก่าไว้"** คือเขียนยืนยันพฤติกรรมที่ผิด
  พอแก้บั๊กจริงเทสกลับแดง ทางแก้ที่ถูกคือ **แก้เทส ไม่ใช่ย้อนโค้ดกลับไปผิด**
  (จบไปแล้ว 12 ตัวเมื่อ 21 ส.ค. 2569)
