# ============================================================================
#  LINE AI Academic Assistant — งานที่ใช้บ่อย
#
#  Windows ไม่มี make มาให้ ติดตั้งด้วย:  winget install ezwinports.make
#  หรือคัดลอกคำสั่งในแต่ละ target ไปรันตรง ๆ ก็ได้
# ============================================================================

SHELL := cmd.exe
PY := python
PROGRAM_ID := 59721
TERMS := 2567/1,2567/2,2568/1,2568/2

.PHONY: help install dev dev-reload db-up db-down db-reset db-shell migrate seed \
        scrape scrape-programs scrape-courses scrape-offerings \
        scrape-documents scrape-instructors export check verify test doctest clean

help:
	@echo.
	@echo   install           ติดตั้ง dependency
	@echo.
	@echo   -- รันเซิร์ฟเวอร์ --
	@echo   dev               รันแอป (ใช้ตัวนี้ถ้าต้องต่อฐานข้อมูล)
	@echo   dev-reload        รันแบบ auto-reload (ต่อฐานข้อมูลไม่ได้บน Windows)
	@echo.
	@echo   -- Database (ต้องมี Docker) --
	@echo   db-up             เริ่ม Postgres + pgvector
	@echo   db-down           หยุด (ข้อมูลยังอยู่)
	@echo   db-reset          ลบ volume แล้วสร้างใหม่ (ข้อมูลหาย)
	@echo   db-shell          เข้า psql
	@echo   seed              นำเข้า seed data
	@echo.
	@echo   -- Scraper --
	@echo   scrape            รันทุกตัวตามลำดับ
	@echo   scrape-programs   โครงสร้างหลักสูตร
	@echo   scrape-courses    คำอธิบายรายวิชา
	@echo   scrape-offerings  ตารางสอน + offering_pattern
	@echo   scrape-documents  ลิงก์เอกสาร + ตรวจลิงก์ตาย
	@echo   scrape-instructors ข้อมูลอาจารย์
	@echo.
	@echo   -- ตรวจสอบ --
	@echo   test              รันเทส (pytest)
	@echo   doctest           รัน doctest ในโค้ดของแอป
	@echo   export            SQLite -^> Postgres seed SQL
	@echo   check             ตรวจ SQL syntax + FK/constraint
	@echo   verify            ตรวจความถูกต้องของ knowledge base
	@echo.

# requirements-dev.txt มี -r requirements.txt อยู่ข้างใน → ได้ทั้ง 3 กลุ่มในทีเดียว
# (แอป + scraper/ตรวจ SQL + เทส) ถ้าจะลงเฉพาะตัวรันแอป ใช้ requirements.txt
install:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements-dev.txt

# ── รันเซิร์ฟเวอร์ ──────────────────────────────────────────────────────────

# ต้องผ่าน run.py เพราะ psycopg async ใช้ ProactorEventLoop (default ของ
# Windows) ไม่ได้ — run.py ตั้ง SelectorEventLoop ให้ก่อนสร้าง loop
dev:
	set PYTHONUTF8=1 && $(PY) run.py

# auto-reload สะดวกตอนแก้โค้ด แต่ process ลูกกลับไปใช้ Proactor
# → ต่อฐานข้อมูลไม่ได้ ใช้เฉพาะตอนทำส่วนที่ไม่ต้องใช้ DB
dev-reload:
	set PYTHONUTF8=1 && $(PY) -m uvicorn app.main:app --reload --port 8000

# ── Database ────────────────────────────────────────────────────────────────

db-up:
	docker compose up -d db
	@echo รอ Postgres พร้อม...
	docker compose exec db pg_isready -U rmubot -d rmu_bot

db-down:
	docker compose down

db-reset:
	docker compose down -v
	docker compose up -d db

db-shell:
	docker compose exec db psql -U rmubot -d rmu_bot

# migration รันอัตโนมัติตอนสร้าง volume ครั้งแรก
# target นี้ใช้เมื่ออยากรันซ้ำบน DB ที่มีอยู่แล้ว
migrate:
	docker compose exec -T db psql -U rmubot -d rmu_bot < db/migrations/001_init.sql

seed:
	docker compose exec -T db psql -U rmubot -d rmu_bot -v ON_ERROR_STOP=1 < db/seed/002_seed_data.sql

# ── Scraper ─────────────────────────────────────────────────────────────────

scrape: scrape-programs scrape-courses scrape-offerings scrape-documents scrape-instructors export

scrape-programs:
	$(PY) -m kb.scrape_programs --faculty 70 --program-id $(PROGRAM_ID)

scrape-courses:
	$(PY) -m kb.scrape_courses --program-id $(PROGRAM_ID)

scrape-offerings:
	$(PY) -m kb.scrape_offerings --program-id $(PROGRAM_ID) --terms "$(TERMS)"

scrape-documents:
	$(PY) -m kb.scrape_documents

scrape-instructors:
	$(PY) -m kb.scrape_instructors --cross-check

# ── ตรวจสอบ ─────────────────────────────────────────────────────────────────

# PYTHONUTF8=1 จำเป็นบน Windows ไม่งั้นข้อความไทยใน output เป็น ?????
test:
	set PYTHONUTF8=1 && $(PY) -m pytest

doctest:
	set PYTHONUTF8=1 && $(PY) -m pytest --doctest-modules app/ -q

export:
	$(PY) -m db.export_seed

check:
	$(PY) -m db.validate_sql
	$(PY) -m db.check_integrity

verify:
	$(PY) -m kb.verify $(PROGRAM_ID)

clean:
	@if exist kb\data\raw rmdir /s /q kb\data\raw
	@echo ล้าง HTML cache แล้ว
