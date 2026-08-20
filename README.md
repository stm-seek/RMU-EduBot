# LINE AI Academic Assistant

ระบบแชทบอท LINE ให้คำปรึกษาด้านการเรียนด้วย AI สำหรับ มรภ.มหาสารคาม

**สถานะ: Knowledge Base + LINE webhook + ชั้นที่ 1 (ตอบจาก DB) เสร็จแล้ว —
ยังไม่มี FAQ matching / RAG / planner**

---

## สิ่งที่ทำเสร็จแล้ว

### Knowledge Base (ดึงจากข้อมูลสาธารณะ ไม่มีการ login)

```
หลักสูตร MDI 643170151    15 หมวด, 68 วิชา, 120 หน่วยกิต  (ตรวจแล้วหน่วยกิตตรงทุกหมวด)
คำอธิบายรายวิชา           68/68 วิชา
ตารางสอน                  337 หมู่เรียน, 292 คาบ, 4 เทอม (2567/1 - 2568/2)
เอกสาร/แบบฟอร์ม           32 รายการ  (ตรวจลิงก์แล้วเข้าได้ 31)
อาจารย์                   28 คน, 33 สังกัด
                          รวม 1,065 แถว
```

รายละเอียด + ข้อจำกัดที่พบ ดู [`kb/README.md`](kb/README.md)

### Database

```
db/migrations/001_init.sql   19 ตาราง, 19 index, pgvector + pg_trgm
db/seed/002_seed_data.sql    1,065 INSERT (idempotent ผ่าน ON CONFLICT)
docker-compose.yml           Postgres 17 + pgvector
```

ตรวจแล้ว: syntax ผ่าน (sqlglot), FK/constraint/ลำดับ INSERT ผ่าน
**ยังไม่ได้รันบน Postgres จริง** (ดู [ถ้า Docker ใช้ไม่ได้](#ถ้า-docker-ใช้ไม่ได้))

### แอป (FastAPI)

```
POST /webhook            รับ event จาก LINE — verify HMAC → ตอบ 200 ทันที → BackgroundTask
GET  /health             บอกว่าอะไรตั้งค่าแล้ว + ต่อ DB ได้จริงไหม
POST /api/liff/login     verify ID token กับ LINE แล้วคืน user_hash (ไม่คืน userId ดิบ)
GET  /api/liff/config    LIFF ID + program_code สำหรับหน้า LIFF
```

ชั้นที่ 1 ตอบจากฐานข้อมูลแล้ว: เอกสาร/คำร้อง (11 หมวด), ติดต่ออาจารย์
(แยกตามสาขา), รายละเอียดรายวิชาจากรหัส 7 หลัก, สรุปว่าวิชาไหนเปิดเทอมไหน

เทส: **244 tests + 17 doctests** — ไม่แตะเน็ตเวิร์กจริงและไม่ต้องมี Postgres
(mock ด้วย `httpx.MockTransport` + fake connection, ตรวจ SQL ด้วย `sqlglot`)

```powershell
$env:PYTHONUTF8="1"; python -m pytest -q
$env:PYTHONUTF8="1"; python -m pytest --doctest-modules app/ run.py -q
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

# 3) เริ่ม database
docker compose up -d db
# migration ใน db/migrations/ รันอัตโนมัติตอนสร้าง volume ครั้งแรก

# 4) นำเข้าข้อมูล
docker compose exec -T db psql -U rmubot -d rmu_bot -v ON_ERROR_STOP=1 < db/seed/002_seed_data.sql

# 5) ตรวจ
docker compose exec db psql -U rmubot -d rmu_bot -c "SELECT program_code, program_name, total_credits FROM programs;"

# 6) รันแอป
python run.py                       # → http://127.0.0.1:8000/health
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
| `prerequisites` + `curriculum_rules` | **ว่าง** — ระบบทะเบียนไม่มีข้อมูลนี้ (ค้น `บังคับก่อน` ได้ 0 ผลลัพธ์) และไม่มี มคอ.2 เผยแพร่ออนไลน์ → ต้องขอเล่มจากคณะ |
| ข้อมูลกิจกรรม | `e-activity.rmu.ac.th` คืน **HTTP 500 ทุก path** → รอสอบถามเจ้าหน้าที่ |
| เบอร์โทร/ห้องพัก/เวลาติดต่ออาจารย์ | เว็บคณะไม่มี (0/28) → ต้องกรอกมือ |
| อาจารย์วิชา GE | สอนจริง 111 คน แต่มีในเว็บคณะ IT แค่ 8 คน |
| Planner engine | ยังไม่เขียน (รอ prerequisite) |
| FAQ matching (ชั้น 2) | ยังไม่เขียน — ตาราง `faqs` ยังว่าง |
| RAG (ชั้น 3) | ยังไม่เขียน — ตาราง `rag_chunks` ยังว่าง, ยังไม่ได้ index |
| หน้า LIFF (ติ๊กวิชาที่ผ่าน) | ยังไม่เขียน — มีแต่ API ฝั่ง server |
| บันทึก `chat_logs` / `app_users` | ยังไม่เขียน (รอ Postgres จริง) |
| Rich Menu | ยังไม่ได้สร้างใน LINE Console (ตอนนี้ใช้ Quick Reply) |
| Flex Message | ยังใช้ text + Quick Reply ก่อน |

---

## โครงสร้าง

```
app/
  main.py                 FastAPI — /webhook, /health, /api/liff/*
  config.py               Settings (pydantic-settings) + fail fast บน production
  router.py               router 3 ชั้น (ชั้น 1 เสร็จ, ชั้น 2/3 ยังไม่ทำ)
  db.py                   psycopg async pool + Protocol ให้เทสใช้ fake ได้
  repository.py           SQL ทั้งหมดของชั้นที่ 1
  llm.py                  LLM client แบบ OpenAI-compatible (chat + embed)
  line/                   signature, message builder, Messaging API client, LIFF auth
run.py                   ตัวรันเซิร์ฟเวอร์ (จำเป็นบน Windows — ดู Quick start)
tests/                   244 tests — ไม่ต้องมีเน็ตหรือ Postgres
kb/                      scraper + SQLite knowledge base  (ดู kb/README.md)
db/
  migrations/001_init.sql   Postgres schema
  seed/002_seed_data.sql    ข้อมูลจริง 1,065 แถว (generated — ห้ามแก้มือ)
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
