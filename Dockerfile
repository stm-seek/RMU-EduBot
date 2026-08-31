# ============================================================================
#  image ของแอป (FastAPI + LINE webhook)
#
#  มีไว้เพื่อสองอย่าง:
#  1. ให้ `docker compose up -d` สตาร์ตทั้ง DB และแอปพร้อมกัน — ไม่ต้องรัน
#     `python run.py` แยกอีก
#  2. เตรียมทางขึ้นโฮสต์จริง (Railway/Render อ่าน Dockerfile นี้ได้ตรง ๆ)
#
#  **ในคอนเทนเนอร์ไม่ต้องใช้ run.py** เพราะ run.py มีไว้แก้ปัญหาเฉพาะของ
#  Windows (uvicorn บังคับ ProactorEventLoop ซึ่ง psycopg async ใช้ไม่ได้)
#  ข้างในนี้เป็น Linux — default เป็น SelectorEventLoop อยู่แล้ว จึงเรียก
#  `uvicorn app.main:app` ตรง ๆ ได้
# ============================================================================

FROM python:3.13-slim

# PYTHONUNBUFFERED — ให้ log ไทยออกทันทีไม่ค้างใน buffer ตอน docker logs
# PYTHONDONTWRITEBYTECODE — ไม่ต้องมี __pycache__ ใน image
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1 \
    TZ=Asia/Bangkok

WORKDIR /app

# คัดลอก requirements ก่อนโค้ด — แก้โค้ดแล้ว layer นี้ไม่ต้อง build ใหม่
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir -r requirements.txt

# ไม่ใส่ทั้งโปรเจกต์ — เอาเฉพาะที่ runtime ใช้ (เทส/scraper/เอกสารไม่ต้องอยู่ใน image)
COPY app/ ./app/
COPY web/ ./web/

# ไม่รันด้วย root — ถ้าโค้ดมีช่องโหว่ ผู้บุกรุกก็ยังไม่ได้ root ในคอนเทนเนอร์
RUN useradd --create-home --uid 10001 appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# ต้อง 0.0.0.0 ไม่ใช่ 127.0.0.1 — ผูกกับ loopback แล้วคนนอกคอนเทนเนอร์
# เข้าไม่ถึง (พอร์ตที่ map ไว้จะตอบ connection refused)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
