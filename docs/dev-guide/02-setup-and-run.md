# 02 — ติดตั้งและรัน

เครื่องที่พัฒนาอยู่: **Windows 11 + PowerShell + Python 3.13** โปรเจกต์อยู่ที่
`D:\repo\line-bot-jang` และเซิร์ฟเวอร์รันที่ **พอร์ต 8001** (พอร์ต 8000 ถูก
โปรเจกต์อื่นในเครื่องยึดไว้ ถ้าเห็น 404 แปลก ๆ ให้เช็คก่อนว่าเรียกถูกพอร์ตไหม)

## 2.1 ติดตั้งครั้งแรก

```powershell
cd D:\repo\line-bot-jang
pip install -r requirements.txt          # รันแอปเท่านั้น
pip install -r requirements-dev.txt      # + scraper, ตรวจ SQL, รันเทส
Copy-Item .env.example .env              # แล้วแก้ค่าในไฟล์ .env
```

ค่าใน `.env` ที่ **ต้องมีจริง** ไม่งั้นระบบไม่ทำงาน:

| ตัวแปร | เอามาจากไหน |
|---|---|
| `LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN` | LINE Developers Console → Messaging API channel |
| `LIFF_ID`, `LINE_LOGIN_CHANNEL_ID` | **LINE Login channel (คนละใบกับ Messaging API)** |
| `LLM_API_KEY` | Google AI Studio (ใช้ Gemini ผ่าน endpoint แบบ OpenAI-compatible) |
| `USER_ID_PEPPER` | สุ่มเอง ยาว ๆ — ใช้ hash LINE user id เปลี่ยนค่าแล้วผู้ใช้เก่าจะกลายเป็นคนใหม่ |
| `ADMIN_SESSION_SECRET` | สุ่มเอง — ว่างไว้ = ล็อกอิน `/admin` ไม่ได้เลย |
| `DATABASE_URL` | ตรงกับ `docker-compose.yml` (ผู้ใช้ `rmubot` ฐาน `rmu_bot`) |
| `PUBLIC_BASE_URL` | URL ของ tunnel รอบปัจจุบัน (เปลี่ยนทุกครั้งที่รีสตาร์ต tunnel) |

`.env.example` มีคำอธิบายทุกตัวแปรอยู่ในไฟล์แล้ว (ยาวกว่าปกติโดยเจตนา — ใช้แทน
เอกสารตั้งค่า) และ `app/config.py` มี **fail fast**: ถ้า `APP_ENV=production`
แล้วค่าจำเป็นหาย ระบบจะไม่ยอมสตาร์ต ไม่ใช่รันแล้วพังตอนมีคนใช้

## 2.2 สตาร์ตระบบ 4 ขั้น (ลำดับนี้เท่านั้น)

### 1) ฐานข้อมูล — ต้องขึ้นก่อนเซิร์ฟเวอร์ ไม่งั้น connection pool ต่อไม่ติด

```powershell
docker start rmu_bot_db
docker ps --filter name=rmu_bot_db --format "{{.Status}} {{.Ports}}"
# ต้องเห็น (healthy) 127.0.0.1:5432
```

ครั้งแรกสุด (ยังไม่มี container เลย) ใช้ `make db-up` แล้ว `make seed`

### 2) เซิร์ฟเวอร์

```powershell
$env:PYTHONUTF8 = '1'
python run.py
```

แบบรันเบื้องหลัง (ต้องตั้ง `PYTHONUTF8` **ก่อน** เพราะ process ลูกรับค่าไปตอนสร้าง):

```powershell
$env:PYTHONUTF8 = '1'
$p = Start-Process python -ArgumentList 'run.py' -WorkingDirectory D:\repo\line-bot-jang `
     -RedirectStandardOutput .server.out.log -RedirectStandardError .server.err.log `
     -PassThru -WindowStyle Hidden
"SERVER PID=$($p.Id)"
```

พร้อมใช้เมื่อ `curl.exe -s http://127.0.0.1:8001/health` คืน `"database":"ok"` (~1 วินาที)

> **ห้ามรัน `uvicorn app.main:app` ตรง ๆ บน Windows** — uvicorn บังคับใช้
> `ProactorEventLoop` ซึ่ง psycopg แบบ async ใช้ไม่ได้ `run.py` สร้าง
> `SelectorEventLoop` ให้ก่อน ผลข้างเคียงคือ `--reload` ใช้กับฐานข้อมูลไม่ได้
> (บน Linux/macOS ไม่มีปัญหานี้)

### ทางเลือก: รวบขั้น 1+2 ด้วย docker compose (ไม่ต้องรัน `run.py`)

โปรเจกต์มี `Dockerfile` ของแอปแล้ว ทำให้สั่งครั้งเดียวขึ้นทั้งฐานข้อมูลและ
เซิร์ฟเวอร์ได้ (compose รอ DB `healthy` ก่อนค่อยสตาร์ตแอปให้เอง):

```powershell
docker compose up -d --build
docker compose ps
# ต้องเห็นทั้ง rmu_bot_db และ rmu_bot_app เป็น Up (healthy)
docker compose logs -f app     # log ของแอป (แทนไฟล์ .server.*.log)
```

จากนั้นข้ามไปทำขั้น 3 ต่อได้เลย พอร์ตบนเครื่องยังเป็น **8001** เหมือนเดิม
(ตั้งได้ที่ `APP_PORT` ใน `.env`) ปิดด้วย `docker compose down`

สิ่งที่ต้องรู้เมื่อใช้ทางนี้:

* **แก้โค้ดแล้วต้อง build ใหม่** — `docker compose up -d --build app`
  ไม่มี `--reload` ให้ (image คัดลอกโค้ดเข้าไปตอน build)
* ในคอนเทนเนอร์**ไม่ได้ใช้ `run.py`** เพราะข้างในเป็น Linux ซึ่งไม่มีปัญหา
  `ProactorEventLoop` ของ Windows — เรียก `uvicorn app.main:app` ตรง ๆ ได้
* `DATABASE_URL` ถูกเขียนทับใน `docker-compose.yml` ให้ชี้ host `db`
  (ชื่อ service) ไม่ใช่ `127.0.0.1` — ค่าใน `.env` ไม่ต้องแก้
* ค่าอื่นทั้งหมด (LINE token, LLM key, pepper) อ่านจาก `.env` ผ่าน `env_file`
  ดังนั้น `.env` ยังเป็นแหล่งเดียวเหมือนเดิม
* รันสองทางพร้อมกันไม่ได้ ถ้า `python run.py` ยังค้างอยู่ compose จะขึ้น
  `ports are not available ... 8001` — ปิดตัวเดิมก่อน

### 3) tunnel — LINE ต้องเรียกเข้ามาทาง HTTPS

```powershell
Start-Process 'C:\Program Files (x86)\cloudflared\cloudflared.exe' `
  -ArgumentList 'tunnel','--url','http://localhost:8001' -WorkingDirectory D:\repo\line-bot-jang `
  -RedirectStandardError .cf.log -RedirectStandardOutput .cf.out.log -PassThru -WindowStyle Hidden

(Select-String -Path .cf.log -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com').Matches[0].Value
```

`cloudflared` **ไม่อยู่ใน PATH** ต้องเรียกด้วย path เต็ม และ **URL สุ่มใหม่ทุกครั้ง**

### 4) ตั้ง Webhook URL ที่ LINE — ต้องทำใหม่ทุกครั้งที่ tunnel เปลี่ยน

แก้ `PUBLIC_BASE_URL` ใน `.env` เป็น URL ที่ได้ แล้ว

```powershell
$env:PYTHONUTF8 = '1'; python scripts/set_webhook_endpoint.py
```

สคริปต์นี้ตั้ง endpoint ตาม `PUBLIC_BASE_URL` แล้วยิงทดสอบให้ในคำสั่งเดียว
ต้องได้ `{"success":true, ... "statusCode":200,"reason":"OK"}` = ต่อติดแล้ว

ถ้า Verify ไม่ผ่าน **ดูค่า `reason` ก่อนแก้อะไร**:
`COULD_NOT_CONNECT` = tunnel ไม่ทำงาน · `ERROR_STATUS_CODE` = ถึงเซิร์ฟเวอร์แล้ว
แต่ตอบไม่ใช่ 200 (ดู log) — **อย่าไปแก้เรื่อง signature** เพราะปุ่ม Verify ของ
LINE ส่ง signature มาถูกต้องอยู่แล้ว

ถ้าใช้หน้า LIFF ด้วย ต้องไปตั้ง **LIFF Endpoint URL** ใน LINE Console เป็น
`<PUBLIC_BASE_URL>/liff` ด้วย (คนละที่กับ webhook)

## 2.3 ดู log

log แยกสองไฟล์ **ต้องดูทั้งคู่** — access log ของ uvicorn ออก stdout
ส่วน log ของแอปออก stderr (อ่านผิดไฟล์แล้วจะคิดว่า request ไม่เข้ามา)

```bash
tail -F .server.err.log .server.out.log | grep -aE 'ตอบแล้ว|ปฏิเสธ|ล้มเหลว|POST /webhook'
```

## 2.4 ปิดระบบ / เข้า DB ตรง ๆ

```powershell
Stop-Process -Id <pid> -Force                       # หรือ
Get-Process cloudflared,python | Stop-Process -Force
```

```bash
docker exec -i rmu_bot_db psql -U rmubot -d rmu_bot   # user คือ rmubot ไม่ใช่ postgres
```

## 2.5 คำสั่งอื่นที่มีให้ (`make help` ดูทั้งหมด)

| คำสั่ง | ทำอะไร |
|---|---|
| `make db-up` / `db-down` / `db-reset` / `db-shell` | คุม Postgres ผ่าน docker compose |
| `make seed` | นำเข้าข้อมูล 1,066 แถว + แผนการเรียน (idempotent รันซ้ำได้) |
| `make test` / `make doctest` | รันชุดทดสอบ |
| `make check` / `make verify` | ตรวจ SQL ด้วย sqlglot + ตรวจ FK/ลำดับ INSERT |
| `make scrape` | ดึงข้อมูลจากเว็บทะเบียนใหม่ทั้งชุด |
| `make rich-menu-dry` / `rich-menu-apply` | ตรวจ/อัปโหลด Rich Menu ขึ้น LINE |
| `python scripts/admin_user.py --username <ชื่อ>` | สร้าง/รีเซ็ตรหัสผู้ดูแลหน้า `/admin` |

> ⚠️ **`make migrate` ล้าสมัย** — รัน migration ถึงแค่ `005_planner.sql`
> ยังไม่รวม `006_admin.sql`, `007_answered_by_faq.sql`, `008_admin_accounts.sql`
> ถ้าตั้งเครื่องใหม่ต้องรันสามไฟล์นั้นเองต่อ (หรือใช้ `make db-reset` ซึ่ง
> Postgres จะรันทุกไฟล์ใน `db/migrations/` ให้ตอนสร้าง volume ใหม่)
