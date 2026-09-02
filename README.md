# LINE AI Academic Assistant

ระบบแชทบอท LINE ให้คำปรึกษาด้านการเรียนด้วย AI สำหรับ มรภ.มหาสารคาม

**สถานะ: Knowledge Base + LINE webhook + ชั้นที่ 1 (ตอบจาก DB) +
Planner Engine (ความก้าวหน้าตามหลักสูตร) เสร็จแล้ว — ยังไม่มี FAQ matching / RAG**

---

## สิ่งที่ทำเสร็จแล้ว

### Knowledge Base (ดึงจากข้อมูลสาธารณะ ไม่มีการ login)

```
หลักสูตร MDI 643170151    15 หมวด, 68 วิชา, 120 หน่วยกิต  (ตรวจแล้วหน่วยกิตตรงทุกหมวด)
คำอธิบายรายวิชา           68/68 วิชา
ตารางสอน                  337 หมู่เรียน, 292 คาบ, 4 เทอม (2567/1 - 2568/2)
เอกสาร/แบบฟอร์ม           33 รายการ  (ตรวจลิงก์ 22 ส.ค. 2026 เข้าได้ครบ)
อาจารย์                   28 คน, 33 สังกัด
                          รวม 1,066 แถว
```

รายละเอียด + ข้อจำกัดที่พบ ดู [`kb/README.md`](kb/README.md)

### Database

```
db/migrations/001_init.sql   19 ตาราง, 19 index, pgvector + pg_trgm
db/seed/002_seed_data.sql    1,066 INSERT (idempotent ผ่าน ON CONFLICT)
docker-compose.yml           Postgres 17 + pgvector
```

ตรวจแล้ว: syntax ผ่าน (sqlglot), FK/constraint/ลำดับ INSERT ผ่าน
**ยังไม่ได้รันบน Postgres จริง** (ดู [ถ้า Docker ใช้ไม่ได้](#ถ้า-docker-ใช้ไม่ได้))

### แอป (FastAPI)

```
POST /webhook            รับ event จาก LINE — verify HMAC → ตอบ 200 ทันที → BackgroundTask
GET  /health             บอกว่าอะไรตั้งค่าแล้ว + ต่อ DB ได้จริงไหม
POST /api/liff/login     verify ID token กับ LINE แล้วคืน user_hash (ไม่คืน userId ดิบ)
GET  /api/liff/config    LIFF ID + program_code + เพดานหน่วยกิต สำหรับหน้า LIFF
GET  /liff               หน้าติ๊กวิชาที่ผ่านแล้ว (web/liff/index.html)
POST /api/liff/state     แผนการเรียน + วิชาที่ติ๊กไว้ + ตัวเลขความก้าวหน้า
POST /api/liff/completed_courses   บันทึกชุดวิชาที่ผ่าน แล้วคืนสถานะใหม่ทั้งก้อน
```

ชั้นที่ 1 ตอบจากฐานข้อมูลแล้ว: เอกสาร/คำร้อง (11 หมวด), ติดต่ออาจารย์
(แยกตามสาขา), รายละเอียดรายวิชาจากรหัส 7 หลัก, สรุปว่าวิชาไหนเปิดเทอมไหน

**Rich Menu 6 ช่อง** ลงกับ LINE แล้ว (ปรึกษา AI · กู้ยืม กยศ. · ติดต่ออาจารย์ ·
ค้นรายวิชา · เอกสาร/คำร้อง · ทำอะไรได้บ้าง) ภาพต้นฉบับอยู่ที่
`assets/rich_menu.png` (1200x810) และ**พิกัดปุ่มใน `app/line/rich_menu.py`
วัดมาจากไฟล์ภาพนั้น** ไม่ใช่หาร 3 หาร 2 เอา — เปลี่ยนภาพต้องวัดใหม่

```powershell
make rich-menu-dry        # ตรวจภาพ + ดู JSON ไม่ยิง API
make rich-menu-apply      # create -> upload -> set default
make rich-menu-list       # ดูเมนูที่มีบน LINE (แล้ว rich-menu-delete เก็บกวาด)
```

**Rich Menu ไม่แสดงบน LINE for PC** ต้องทดสอบบนมือถือ และ**แก้ภาพของเมนูที่
อัปโหลดไปแล้วไม่ได้** ต้องสร้างใบใหม่แล้วลบใบเก่าทิ้ง

เทส: **512 unit + 46 doctests** — ไม่แตะเน็ตเวิร์กจริงและไม่ต้องมี Postgres
(mock ด้วย `httpx.MockTransport` + fake connection, ตรวจ SQL ด้วย `sqlglot`)
อีก **101 integration** ต้องมี Postgres จริงจึงเป็น opt-in ด้วย `RMU_DB_TESTS=1`

```powershell
$env:PYTHONUTF8="1"; python -m pytest -q
$env:PYTHONUTF8="1"; python -m pytest --doctest-modules app/ run.py -q
$env:PYTHONUTF8="1"; $env:RMU_DB_TESTS="1"; python -m pytest tests/integration -q
```

---

## Quick start

```powershell
# 1) ติดตั้ง (เวอร์ชัน pin ไว้ใน requirements*.txt แล้ว)
pip install -r requirements.txt              # รันแอป
pip install -r requirements-dev.txt          # + scraper, ตรวจ SQL, เทส

# 2) ตั้งค่า
Copy-Item .env.example .env
# แก้ .env ใส่ LINE_CHANNEL_SECRET, LLM_API_KEY, USER_ID_PEPPER

# 3) เริ่ม database + นำเข้าข้อมูล — คำสั่งเดียวจบ ไม่ต้อง psql เอง
docker compose up -d db
# migration ใน db/migrations/ + seed ใน db/seed/ รันอัตโนมัติตอนสร้าง volume ครั้งแรก
# (ตัวเรียก seed คือ db/migrations/009z_seed.sh — ต้องรันก่อน 010_electives.sql)

# 4) ตรวจ — init ที่ล้มกลางทางจะถูก restart กลับมาเป็น healthy ทั้งที่ schema ไม่ครบ
docker compose logs db | Select-String -Pattern "ERROR|FATAL"
docker compose exec db psql -U rmubot -d rmu_bot -At -c "select count(*) from information_schema.tables where table_schema='public'"
# ต้องได้ 26 ตาราง / ถ้าไม่ครบ: docker compose down -v แล้ว up -d db ใหม่

# 5) รันแอป
python run.py                       # → http://127.0.0.1:8000/health
# หรือให้แอปอยู่ใน Docker ด้วย: docker compose up -d --build → http://127.0.0.1:8001/health
```

> **Windows: ต้องรันด้วย `python run.py` ไม่ใช่ `uvicorn app.main:app`**
>
> uvicorn บังคับ `ProactorEventLoop` บน Windows ซึ่ง **psycopg แบบ async ใช้ไม่ได้**
> (`Psycopg cannot use the 'ProactorEventLoop' to run in async mode`)
> `run.py` สร้าง `SelectorEventLoop` ให้ก่อน — ตั้ง event loop *policy* ไม่ช่วย
> เพราะ uvicorn ส่ง loop factory ให้ `asyncio.Runner` โดยตรง
>
> ผลข้างเคียง: **`--reload` ใช้กับฐานข้อมูลไม่ได้** (process ลูกสร้าง loop ใหม่เอง)
> ตอนแก้โค้ดส่วนที่ไม่ต้องใช้ DB ใช้ `make dev-reload` ได้
>
> บน Linux/macOS ไม่มีปัญหานี้ — `uvicorn app.main:app` ตรง ๆ ได้เลย

เปิดให้ LINE เรียกเข้ามาได้ (ต้องเป็น HTTPS) แล้วตั้ง Webhook URL ใน LINE
Console เป็น `https://<tunnel>/webhook`:

```powershell
ngrok http 8000              # URL เปลี่ยนทุกครั้งที่ restart
tailscale funnel 8000        # URL คงที่ — สะดวกกว่าตอน dev
```

> **Windows:** ตั้ง `$env:PYTHONUTF8="1"` ก่อนรัน Python ไม่งั้น console แสดงไทยเป็น `?????`

มี `Makefile` ให้ด้วย — `make help` ดูคำสั่งทั้งหมด

### ถ้า Docker ใช้ไม่ได้

Docker Desktop บน Windows ต้องมี **WSL2** ซึ่งต้องเปิด "Virtual Machine
Platform" + virtualization ใน BIOS:

```powershell
# รันใน PowerShell แบบ Administrator แล้ว reboot
wsl.exe --install --no-distribution
```

ทางเลือกที่ไม่ต้อง Docker:
- ติดตั้ง Postgres ตรง ๆ (`winget install PostgreSQL.PostgreSQL.17`)
  แล้วติดตั้ง pgvector เพิ่ม
- ใช้ Supabase / Neon free tier (มี pgvector มาให้แล้ว) แล้วชี้ `DATABASE_URL` ไปที่นั่น

---

## สถาปัตยกรรม

```
LINE
  ├── Rich Menu ──── postback ──┐
  ├── Quick Reply ──────────────┤
  └── ข้อความพิมพ์ ─── webhook ──┤
                                ↓
                     FastAPI (verify X-Line-Signature)
                                │
                    ตอบ 200 ทันที + BackgroundTask
                                │
        ┌───────────────────────┼───────────────────────┐
        ↓                       ↓                       ↓
   ชั้น 1: postback        ชั้น 2: FAQ match      ชั้น 3: RAG
   ตอบจาก DB ตรง          keyword + embedding    pgvector + LLM
   0 บาท / แม่น 100%      คำตอบที่คนเขียนไว้      + แนบแหล่งอ้างอิง
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ↓
                    ไม่มั่นใจ → Fallback (ไม่เดา)
```

**หลักการที่ยึด:** การคำนวณ prerequisite / หน่วยกิต / ตารางชน เป็น
**deterministic code ห้ามให้ LLM คิด** — LLM ทำหน้าที่เรียบเรียงคำอธิบายจากผล
planner เท่านั้น (ตาม Requirement ข้อ 4.4)

### Tech stack

| ส่วน | เลือกใช้ | เหตุผล |
|---|---|---|
| Backend | FastAPI | reply token หมดอายุเร็ว ต้องตอบ 200 ทันที + `BackgroundTasks` มีในตัว |
| Database | Postgres 17 | production-ready, JSONB, array |
| Vector | **pgvector** | ไม่ต้องรัน Chroma/Qdrant แยก → ลด service ลด cost |
| Fuzzy search | **pg_trgm** | ไทยไม่มีตัวตัดคำใน Postgres → full-text search ไทยตรง ๆ ไม่ได้ |
| LLM | OpenAI-compatible | สลับ provider ได้ด้วย `base_url` + `api_key` เท่านั้น |
| Scraper | requests + bs4 + **lxml** | `html.parser` ตัด `<td>` ทิ้ง (ดู kb/README ข้อ 2) |

**LLM แบบ pluggable** — ตั้งใน `.env` อย่างเดียว:

```
Gemini    LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
OpenAI    LLM_BASE_URL=https://api.openai.com/v1
OpenRouter LLM_BASE_URL=https://openrouter.ai/api/v1
Ollama    LLM_BASE_URL=http://127.0.0.1:11434/v1
```

ยืนยันแล้วว่า Gemini รองรับทั้ง `/chat/completions` และ `/embeddings`
แบบ OpenAI-compatible

**ทนต่อ 503 "high demand" ของ free tier** — วัดจริง 21 ส.ค. 2026: ยิง LLM 7 ครั้ง
ได้ 503 ในการยิงครั้งแรก **ทั้ง 7 ครั้ง** และผู้ใช้เห็นข้อความ "ระบบขัดข้อง"
4 ใน 7 ครั้ง (57%) โดยไม่เกี่ยวกับเนื้อหาคำถาม `app/llm.py` จึงมีสองชั้น:

1. **retry รอสั้น ๆ หลายครั้ง** — 0.5 → 1 → 2 วินาที (+ jitter 25%) 4 ครั้งต่อโมเดล
   แทนของเดิมที่รอ 2 → 4 วินาทีแล้วยอมแพ้ (ช้ากว่าและพลาดบ่อยกว่า)
2. **สลับโมเดลเมื่อโมเดลนั้นล่มยาว** — `LLM_FALLBACK_MODELS` (ค่าเริ่มต้น
   `gemini-3.1-flash-lite,gemini-3-flash-preview` ยืนยันกับ API จริงแล้ว)
   เพราะวัดแล้วว่า 503 เกิดแยกกันต่อโมเดล นาทีเดียวกันที่โมเดลหลัก 503
   โมเดลสำรองตอบได้ปกติ — 400/401/403 (key/payload ผิด) ไม่ retry ไม่สลับ

ทั้งสองชั้นอยู่ใต้เพดานเวลารวม `LLM_RETRY_BUDGET_SECONDS` (28 วิ) ที่คุม
**ทั้งเชน** เพราะ reply token ของ LINE อายุสั้น — เลยงบแล้วเลิกทันทีเพื่อให้
ยังตอบผ่าน reply ได้ ไม่ต้องไปเสียโควตา push

**ที่ตั้งใจไม่ใช้:** LangChain (abstraction เยอะเกินจำเป็น เขียน RAG เองตรง ๆ
debug ง่ายกว่า), Celery (BackgroundTasks พอสำหรับ scale นี้), vector DB แยก

---

## PDPA / ความปลอดภัย (แผน B — ไม่ใช้รหัสผ่านนักศึกษา)

**ไม่ขอรหัสผ่านระบบทะเบียน** เพราะ 90% ของข้อมูลที่ planner ต้องใช้เป็นข้อมูล
สาธารณะที่ scrape มาแล้ว การ login ให้ข้อมูลเพิ่มแค่ *"วิชาที่ผ่านแล้ว"*
ซึ่งถามจากนักศึกษาผ่าน LIFF ได้ตรง ๆ

| เก็บ | ไม่เก็บ |
|---|---|
| `line_user_hash` (SHA-256 + pepper) | `line_user_id` ดิบ |
| `program_code`, `study_year` | ชื่อ-นามสกุล, รหัสนักศึกษา |
| รายการรหัสวิชาที่ผ่าน | **เกรด**, เลขบัตรประชาชน, รหัสผ่าน |

**LIFF ต้อง verify ID token ฝั่ง server** ที่ `POST /oauth2/v2.1/verify`
แล้วใช้ `sub` เป็น user id — **ห้ามเชื่อ `userId` ที่ client ส่งมา**
(LINE เตือนไว้ในเอกสารเอง: *"Don't send the details of the user profile ...
to the server from the LIFF app"*) ไม่ทำ = ใครก็ยิง API ดูข้อมูลคนอื่นได้

---

## ยังไม่ได้ทำ / รอข้อมูล

| เรื่อง | สถานะ |
|---|---|
| `prerequisites` (วิชาบังคับก่อน) | **ว่าง** — ระบบทะเบียนไม่มีข้อมูลนี้ (ค้น `บังคับก่อน` ได้ 0 ผลลัพธ์) และไม่มี มคอ.2 เผยแพร่ออนไลน์ → ต้องขอเล่มจากคณะ ระหว่างนี้ planner ใช้ลำดับจากแผนการเรียนและบอกผู้ใช้ตรง ๆ ว่ายังไม่ใช่เงื่อนไขบังคับ |
| `curriculum_rules` หลักสูตรอื่น | มีแค่ 643170151 (32 วิชา) — คณะ IT มีอีก 6 หลักสูตรในระบบทะเบียน ต้องดึงเพิ่ม |
| ข้อมูลกิจกรรม | `e-activity.rmu.ac.th` คืน **HTTP 500 ทุก path** → รอสอบถามเจ้าหน้าที่ |
| เบอร์โทร/ห้องพัก/เวลาติดต่ออาจารย์ | เว็บคณะไม่มี (0/28) → ต้องกรอกมือ |
| อาจารย์วิชา GE | สอนจริง 111 คน แต่มีในเว็บคณะ IT แค่ 8 คน |
| Planner engine | **เขียนแล้ว** (`app/planner.py` + `app/progress.py`) — ตอบความก้าวหน้า/วิชาเทอมถัดไป/ลงวิชานี้ได้ไหม โดยไม่ใช้ LLM ยังขาด prerequisite จริงเท่านั้น |
| FAQ matching (ชั้น 2) | ยังไม่เขียน — ตาราง `faqs` ยังว่าง |
| RAG (ชั้น 3) | ยังไม่เขียน — ตาราง `rag_chunks` ยังว่าง, ยังไม่ได้ index |
| GPA calculator (ข้อ 4.4) | **เขียนแล้ว** (`app/gpa.py`) — ผู้ใช้พิมพ์ GPAX มาตัวเดียว หน่วยกิตที่เหลือระบบรู้จาก planner แล้ว ยังต้องยืนยัน **สเกลแต้มเกรดและเกณฑ์เกียรตินิยม** กับเล่มข้อบังคับ RMU (ไม่มีในคลังเอกสาร) และยังไม่รองรับการลงเรียนซ้ำแก้เกรด |
| Flex Message | ยังใช้ text + Quick Reply ก่อน |

---

## โครงสร้าง

```
app/
  main.py                 FastAPI — /webhook, /health, /liff, /api/liff/*
  config.py               Settings (pydantic-settings) + fail fast บน production
  router.py               router 3 ชั้น (ชั้น 1 เสร็จ, ชั้น 2/3 ยังไม่ทำ)
  db.py                   psycopg async pool + Protocol ให้เทสใช้ fake ได้
  repository.py           SQL ทั้งหมดของชั้นที่ 1
  llm.py                  LLM client แบบ OpenAI-compatible (chat + embed)
  planner.py              คำนวณความก้าวหน้า/วิชาเทอมถัดไป (ไม่มี LLM ไม่มี I/O)
  progress.py             ประกอบคำตอบของชั้น planner ให้บทสนทนา LINE
  gpa.py                  คำนวณเกรด/เป้า GPAX/เกียรตินิยม (ไม่มี LLM ไม่มี I/O)
  line/                   signature, message builder, Messaging API client, LIFF auth
run.py                   ตัวรันเซิร์ฟเวอร์ (จำเป็นบน Windows — ดู Quick start)
web/liff/index.html      หน้า LIFF ติ๊กวิชาที่ผ่านแล้ว (ไฟล์เดียว ไม่มี build step)
tests/                   512 tests (+101 integration ที่ต้องมี Postgres จริง)
kb/                      scraper + SQLite knowledge base  (ดู kb/README.md)
db/
  migrations/001_init.sql   Postgres schema (005_planner.sql = คอลัมน์/ป้ายของ planner)
  seed/002_seed_data.sql    ข้อมูลจริง 1,065 แถว (generated — ห้ามแก้มือ)
  seed/003_curriculum_rules.sql  แผนการเรียน 643170151 (32 วิชา)
  export_seed.py            SQLite → Postgres SQL
  validate_sql.py           ตรวจ syntax ด้วย sqlglot
  check_integrity.py        ตรวจ FK / constraint / ลำดับ INSERT
test/                    โค้ดทดลองเดิม (แผน A) — ล้าง credential/PII แล้ว เก็บไว้อ้างอิง
docker-compose.yml
.env.example
pytest.ini
Makefile
```

> **ล้าง PII แล้ว** `test/rmu_scraper.py` ถอด credential ออก เปลี่ยนไปอ่านจาก
> env `RMU_STUDENT_ID` / `RMU_PASSWORD` (default เป็น placeholder ปลอม)
> `test/complete_student_data.json` (ชื่อจริง + เกรด) ถูกลบออกจาก repo แล้ว
> โค้ดที่เคยอ่านไฟล์นี้จะแจ้งเป็นภาษาไทยแทนการ crash
>
> **ข้อมูลอาจารย์ — ตัดสินใจแล้ว 19 ส.ค. 2026 ว่าเก็บไว้ทั้งหมด**
> `db/seed/002_seed_data.sql` มีชื่อจริงอาจารย์ 28 คน + อีเมลจริง 26 รายการ
> (`@rmu.ac.th` 16, gmail 7, hotmail 3) และ `kb/scrape_instructors.py` มีตัวอย่าง
> HTML ที่ติดชื่อ + อีเมลจริงมาด้วย ทั้งสองไฟล์ `.gitignore` **ไม่ได้กัน**
>
> เก็บไว้ได้เพราะ **repo นี้จะเป็น private** และข้อมูลชุดนี้เว็บคณะเผยแพร่สาธารณะ
> อยู่แล้ว (`itrmu.org/academic_staff.php`) — ต่างจากข้อมูลนักศึกษาในตาราง PDPA
> ข้างบนซึ่งเป็นของส่วนตัวแท้ ๆ
>
> ⚠️ **ถ้าวันใดจะเปลี่ยน repo เป็น public ต้อง mask อีเมลโดเมนส่วนตัว 10 รายการ
> ก่อน commit** — แก้ที่ `db/export_seed.py` แล้ว re-export ห้ามแก้
> `002_seed_data.sql` ด้วยมือ (เป็นไฟล์ generated)
