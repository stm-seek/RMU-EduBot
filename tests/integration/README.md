# เทสที่ต้องใช้ Postgres จริง (integration)

เทสในโฟลเดอร์นี้ยิงฐานข้อมูล **ของจริง** ที่มีข้อมูล seed ครบ ต่างจากเทส 244 ตัว
ที่ `tests/` ชั้นบนซึ่งใช้ `FakeDatabase` / `httpx.MockTransport` / `sqlglot`
และรันได้โดยไม่มี DB เลย

## ต้องเตรียมอะไรก่อน

1. ฐานข้อมูลขึ้นอยู่และ healthy

   ```
   docker compose up -d db
   docker compose ps            # ต้องเห็น rmu_bot_db เป็น healthy
   ```

2. โหลด seed แล้ว (1,065 แถว) — เช็คเร็ว ๆ ด้วย

   ```
   docker compose exec -T db psql -U rmubot -d rmu_bot -Atc "SELECT count(*) FROM offerings"
   ```

   ต้องได้ `337` ถ้าได้ `0` แปลว่ายังไม่ได้รัน `db/seed/002_seed_data.sql`

3. `DATABASE_URL` ใน `.env` ชี้ไปที่ฐานข้อมูลนั้น (เทสอ่านผ่าน
   `app.config.get_settings()` ไม่มีการ hardcode รหัสผ่านในเทส)

## วิธีรัน

```
set PYTHONUTF8=1                     # PowerShell: $env:PYTHONUTF8=1
python -m pytest -m integration -q
```

หรือถ้าจะระบุโฟลเดอร์ตรง ๆ ต้องบอกให้รันด้วย env var:

```
RMU_DB_TESTS=1 python -m pytest tests/integration -q
```

ข้าม (สำคัญตอนรีบ) เทสที่รีสตาร์ต container:

```
python -m pytest -m "integration and not restart" -q
```

`pytest` เปล่า ๆ จะ **skip ทั้งชุดนี้** โดยตั้งใจ เพื่อให้เลข baseline ของเทสเดิม
อ่านได้เหมือนเดิม (`244 passed, ... skipped`) และเครื่องที่ไม่มี Docker ก็ไม่พัง
ถ้า `DATABASE_URL` ว่างหรือต่อ DB ไม่ได้ ก็ skip พร้อมบอกเหตุผลเป็นภาษาไทย
(ดูด้วย `-rs`)

**ต้องตั้ง `PYTHONUTF8=1`** ไม่งั้นข้อความไทยใน output กลายเป็น `?????`
บน Windows (stderr เป็น cp874)

## กับดักที่ทำให้เทสพังทั้งชุด: SelectorEventLoop

`psycopg` แบบ async ใช้ `ProactorEventLoop` (ค่า default ของ Python บน Windows)
**ไม่ได้** จะขึ้น

```
Psycopg cannot use the 'ProactorEventLoop' to run in async mode
```

`pytest-asyncio` สร้าง event loop จาก policy ของระบบ = Proactor → ถ้าเขียนเทส
เป็น `async def` ธรรมดา **จะพังทุกตัว** ด้วย error ที่ไม่เกี่ยวกับโค้ดที่กำลังเทสเลย
(เป็นเหตุผลเดียวกับที่รากโปรเจกต์ต้องมี `run.py` แทนการเรียก `uvicorn` ตรง ๆ
และการตั้ง `asyncio.set_event_loop_policy()` ก็ไม่พอ)

ทางแก้ในโฟลเดอร์นี้: เทสทุกตัวเป็นฟังก์ชัน **`def` ธรรมดา** แล้วรัน coroutine
ผ่าน fixture `run` ที่ถือ `SelectorEventLoop` ของตัวเองไว้ทั้ง session

```python
def test_something(live_db, run):
    rows = run(repo.document_categories(live_db))
    assert rows
```

ห้ามเปลี่ยนไปเป็น `async def` — และ pool ต้องอยู่บน loop เดียวทั้ง session
เพราะ connection ลงทะเบียน reader/writer ไว้กับ loop ที่สร้างมัน

## กฎเรื่องข้อมูล

* **read-only** กับ 10 ตารางที่ seed มา — ห้าม INSERT/UPDATE/DELETE
* เขียนได้แค่ตารางปฏิบัติการที่ยังว่าง (`app_users`, `chat_logs`,
  `liff_sessions`, `user_completed_courses`) และต้องลบทิ้งใน teardown
  (`line_user_hash` ต้องขึ้นต้นด้วย `itest-` ให้ตัวกวาดหาเจอ)
* fixture `row_count_guard` นับแถวทั้ง 19 ตารางก่อน/หลัง session ถ้าไม่เท่ากัน
  จะ error ตอน teardown
* ห้าม `docker compose down` / `down -v` — volume หายแล้ว re-seed ใหม่หลายนาที
  (fixture `docker_compose` บล็อกคำสั่ง `down`/`rm`/`kill`/`stop` ไว้แล้ว)
* `test_90_restart.py` ใช้ `docker compose restart db` ซึ่งปลอดภัย (volume อยู่ครบ)
  ไฟล์นี้ตั้งชื่อขึ้นต้นด้วย `90` เพื่อให้รันท้ายสุด เพราะมันทำให้ connection
  ทั้ง pool ตาย

## ไฟล์ในชุดนี้

| ไฟล์ | ตรวจอะไร |
|---|---|
| `test_00_smoke.py` | ต่อติด, extension, 19 ตาราง, จำนวนแถว seed, ไทยไม่เพี้ยน |
| `test_10_repository.py` | `app/repository.py` ทั้ง 11 ฟังก์ชันกับข้อมูลจริง |
| `test_20_pool.py` | pool รับงานพร้อมกัน, `max_size`, commit, error ไม่ทำ pool เสีย |
| `test_30_router.py` | ปุ่มที่สร้างจากข้อมูลจริง กดแล้วได้คำตอบจริง |
| `test_90_restart.py` | pool ฟื้นเองหลัง `docker compose restart db` |

## เทสที่ติด `xfail` = บั๊กที่บันทึกไว้ แต่ยังไม่แก้

มี 2 ตัว (ทั้งคู่ `strict=True` → ถ้าใครแก้บั๊กแล้วเทสจะ **XPASS แล้วนับเป็น fail**
เป็นสัญญาณให้มาลบ marker ออก)

1. `test_default_limit_should_cover_whole_category` — `limit` default = 10 แต่หมวด
   `loan` มีเอกสารจริง 12 ฉบับ → เมนูบอก 12 กดเข้าไปเห็น 10
2. `test_search_documents_should_find_documents_containing_the_keyword` —
   `SQL_SEARCH_DOCUMENTS` ใช้ `similarity()`/`%` กับ `keywords` ที่เป็นสตริงยาว
   ทำให้คำค้นสั้นอย่าง `กยศ` / `กู้ยืม` / `ดรอป` หาไม่เจอเลย
