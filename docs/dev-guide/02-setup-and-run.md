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

ครั้งแรกสุด (ยังไม่มี container เลย) ใช้ `docker compose up -d db` ครั้งเดียว —
migration **และ** seed รันเองตอนสร้าง volume (ตัวเรียก seed คือ
`db/migrations/009z_seed.sh` ดู §4.3) ไม่ต้อง `make seed` ตามหลัง

แต่ต้องตรวจทุกครั้งที่สร้าง volume ใหม่ เพราะ init ที่ล้มกลางทางจะถูก
`restart: unless-stopped` ปลุกกลับมาเป็น `healthy` ทั้งที่ schema ไม่ครบ
(PGDATA ไม่ว่างแล้ว Postgres จึงข้าม init ทั้งชุด ไม่มี error ค้างให้เห็น):

```powershell
docker compose logs db | Select-String -Pattern "ERROR|FATAL"
docker compose exec db psql -U rmubot -d rmu_bot -At -c "select count(*) from information_schema.tables where table_schema='public'"
# ต้องได้ 26 ตาราง — ไม่ครบให้ down -v แล้ว up -d db ใหม่ (ข้อมูลผู้ใช้หาย)
```

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
| `make seed` | นำเข้าข้อมูล 1,066 แถว + แผนการเรียน (idempotent) — **ใช้เฉพาะกับ DB ที่มีอยู่แล้ว** volume ใหม่ seed เองอยู่แล้ว |
| `make test` / `make doctest` | รันชุดทดสอบ |
| `make check` / `make verify` | ตรวจ SQL ด้วย sqlglot + ตรวจ FK/ลำดับ INSERT |
| `make scrape` | ดึงข้อมูลจากเว็บทะเบียนใหม่ทั้งชุด |
| `make rich-menu-dry` / `rich-menu-apply` | ตรวจ/อัปโหลด Rich Menu ขึ้น LINE (ขั้นตอนเต็มอยู่ §2.6) |
| `python scripts/admin_user.py --username <ชื่อ>` | สร้าง/รีเซ็ตรหัสผู้ดูแลหน้า `/admin` |

> ⚠️ **`make migrate` ล้าสมัย** — รัน migration ถึงแค่ `005_planner.sql`
> ยังไม่รวม `006_admin.sql`, `007_answered_by_faq.sql`, `008_admin_accounts.sql`
> ถ้าตั้งเครื่องใหม่ต้องรันสามไฟล์นั้นเองต่อ (หรือใช้ `make db-reset` ซึ่ง
> Postgres จะรันทุกไฟล์ใน `db/migrations/` ให้ตอนสร้าง volume ใหม่)

## 2.6 ติดตั้ง Rich Menu ให้ channel ใหม่ (ทำครั้งเดียวต่อ channel)

**Rich Menu ไม่ได้อยู่ในโค้ดและไม่ได้อยู่ใน DB — มันอยู่บนเซิร์ฟเวอร์ของ LINE
ผูกกับ channel** ใครเอาโปรเจกต์นี้ไปต่อกับ channel ของตัวเอง (เพื่อน เครื่องใหม่
channel ทดสอบอีกใบ) ต้องสั่งสร้างเมนูของ channel นั้นเอง `git pull` ไม่ได้เมนูมาด้วย
อาการเวลายังไม่ได้ทำ: บอทตอบข้อความได้ปกติ แต่ในแชทไม่มีแถบเมนูให้กดเลย

ต้องมีก่อนอย่างเดียวคือ `.env` ที่มี `LINE_CHANNEL_ACCESS_TOKEN` (long-lived)
ของ channel นั้น — ปุ่มทุกช่องเป็น `postback` ล้วน **ไม่มี URL/LIFF ฝังในเมนู**
จึงไม่ต้องรอ tunnel, `PUBLIC_BASE_URL` หรือ LIFF ID ให้พร้อมก่อน ทำก่อนหรือหลัง
ตั้ง webhook ก็ได้ ส่วนภาพ `assets/rich_menu.png` (1200x810) กับ
`assets/rich_menu_consult.png` อยู่ใน repo แล้ว ไม่ต้องทำภาพใหม่

### เครื่องที่ลง Docker ล้วน (ไม่มี python/httpx บน host)

```powershell
docker compose run --rm tools scripts/rich_menu.py --dry-run   # ตรวจภาพ + ดู JSON ไม่ยิง API
docker compose run --rm tools scripts/rich_menu.py             # create -> upload -> set default
docker compose run --rm tools scripts/rich_menu.py --list      # ดูใบที่อยู่บน channel
```

จบแค่นี้ — เปิดแชทบอทบน**มือถือ** จะเห็นเมนู 6 ช่อง ไม่ต้องรีสตาร์ตแอปเพราะ
เมนูหลักอยู่ฝั่ง LINE ทั้งหมด แอปไม่ได้ถือ id ของมันไว้

`tools` เป็น service ใน `docker-compose.yml` ที่ mount โปรเจกต์ทั้งก้อนทับ `/app`
แล้วใช้ `python` ในคอนเทนเนอร์รันให้ — จำเป็นเพราะ image ของแอปคัดลอกเข้าไปแค่
`app/` กับ `web/` ไม่มี `scripts/` กับ `assets/` และเพราะอยู่ใน
`profiles: ["tools"]` มันจึงไม่ขึ้นมาตอน `up -d` ใช้กับสคริปต์อื่นได้เหมือนกัน เช่น
`docker compose run --rm tools scripts/admin_user.py --username admin`
(ตัวนั้นต้องมี `db` ขึ้นอยู่ก่อน ไม่งั้น psycopg ฟ้อง connection refused)

### เครื่องที่ลง python + `requirements.txt` แล้ว

| คำสั่ง | ทำอะไร |
|---|---|
| `make rich-menu-dry` | ตรวจภาพ + พิมพ์ JSON ไม่ยิง API |
| `make rich-menu-apply` | สร้าง + อัปโหลดภาพ + ตั้ง default |
| `make rich-menu-list` | ดู id / ขนาด / จำนวนปุ่มของทุกใบบน channel |
| `make rich-menu-delete RICHMENU_ID=<id>` | ลบใบเก่า |
| `make rich-menu-apply-consult` | ใบโหมดปรึกษา (ไม่ตั้ง default) |

### ใบที่สอง — โหมดปรึกษา AI (ทำหรือไม่ทำก็ได้)

ตอนผู้ใช้เข้าโหมดปรึกษา AI แอปจะสลับเมนูของ *คนนั้นคนเดียว* ไปเป็นใบ 2 ปุ่ม
(จบการปรึกษา · เมนูหลัก) แล้วสลับกลับเมื่อจบ — ทำผ่าน `link_rich_menu` /
`unlink_rich_menu` ใน `app/main.py` ถ้าไม่ตั้งค่านี้ ระบบยังทำงานปกติทุกอย่าง
แค่ไม่สลับเมนู

```powershell
docker compose run --rm tools scripts/rich_menu.py --variant consult --no-default
# ได้ richmenu-xxxx -> ใส่ RICH_MENU_CONSULT_ID=richmenu-xxxx ใน .env
docker compose up -d app        # ค่านี้อ่านตอนเริ่มโปรเซส ต้องรีสตาร์ตแอป
```

สคริปต์**ปฏิเสธ**ถ้าลืม `--no-default` เพราะใบนี้ถ้าตั้งเป็น default ทั้งบัญชี
ผู้ใช้ทุกคนจะเหลือ 2 ปุ่มทันที

### กับดักที่เสียเวลามาแล้ว

* **ไม่ขึ้นบน LINE for PC เลย** ต้องทดสอบบนมือถือ และเห็นตอนเปิดห้องแชทรอบถัดไป
  (ช้าได้ถึง ~1 นาที) — ปิดแล้วเปิดห้องแชทใหม่ช่วยให้มาไวขึ้น
* **แก้ภาพของใบที่อัปโหลดไปแล้วไม่ได้** ต้องสร้างใบใหม่แล้ว `--delete` ใบเก่า
  และ API create/delete จำกัด **100 ครั้ง/ชั่วโมง** ต่อ channel
* ภาพต้องเป็น **1200x810 เท่านั้น** เพราะพิกัดปุ่มใน `app/line/rich_menu.py`
  (`COLUMN_EDGES` / `ROW_EDGES`) วัดมาจากไฟล์นั้น ไม่ใช่หาร 3 หาร 2 เอา —
  สคริปต์ตรวจขนาด/ชนิดไฟล์/ไม่เกิน 1 MB ให้ก่อนยิง API เปลี่ยนภาพ = ต้องวัด
  พิกัดใหม่ แล้วรัน `pytest tests/test_rich_menu.py` (คุมว่าช่องไม่ทับกันและ
  ไม่ล้นขอบภาพ แต่ไม่รู้ว่าตรงกับภาพใหม่จริงไหม — ต้องดูด้วยตาบนมือถือ)
* เมนูผูกกับ **channel** ไม่ใช่กับ token — ออก token ใหม่เมนูยังอยู่ แต่ย้ายไป
  channel อื่นต้องสร้างใหม่ และ `--list` ตอบตาม token ที่อยู่ใน `.env` ตอนนั้น
* ปุ่มส่ง `postback` เป็น `action=<x>&src=rich` → ใน `chat_logs` แยกได้ว่ามาจาก
  Rich Menu ไม่ใช่ผู้ใช้พิมพ์เอง เพิ่ม/ย้ายปุ่มต้องแก้ทั้ง `SLOTS` และ router
