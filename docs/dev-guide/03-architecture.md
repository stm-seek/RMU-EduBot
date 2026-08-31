# 03 — สถาปัตยกรรมระบบ

## 3.1 ภาพรวม

> ผังนี้มีเวอร์ชันภาพพร้อมใช้แล้วที่ `screenshots/c01-architecture.png`
> และลำดับเหตุการณ์แบบ sequence diagram ที่ `screenshots/c04-sequence.png`

```
        นักศึกษา (แอป LINE บนมือถือ)
                    │
     ┌──────────────┼──────────────┐
     │              │              │
 Rich Menu     พิมพ์ข้อความ     หน้า LIFF
 (postback)     (webhook)      (เว็บในแอป)
     └──────────────┼──────────────┘
                    ↓ HTTPS
          cloudflared tunnel
                    ↓
   ┌────────────────────────────────────────┐
   │  FastAPI  (app/main.py)                │
   │  1. ตรวจลายเซ็น X-Line-Signature       │
   │  2. ตอบ HTTP 200 ให้ LINE ทันที        │
   │  3. ทำงานต่อใน BackgroundTasks         │
   └────────────────────────────────────────┘
                    ↓
          Router (app/router.py)
     ┌──────────────┼──────────────┬─────────────┐
     ↓              ↓              ↓             ↓
  ชั้นที่ 1       ชั้นที่ 2       ชั้นที่ 3     Fallback
 ตอบจาก DB       FAQ ที่คน      AI / RAG      "ยังตอบ
 ตรง ๆ           เขียนไว้       (LLM)         ไม่ได้"
 เร็ว/ฟรี/       ไม่เรียก LLM   มีค่าเรียก    ไม่เดา
 แม่น 100%                      API
     └──────────────┴──────────────┴─────────────┘
                    ↓
        Postgres 17 + pgvector + pg_trgm
        (+ บันทึกทุกครั้งลง chat_logs)
```

**ทำไมต้องตอบ 200 ทันทีแล้วค่อยทำงาน:** reply token ของ LINE อายุสั้นมาก ถ้ารอ
LLM ตอบ (3–10 วินาที) ก่อนแล้วค่อยตอบ LINE จะคิดว่าเราล่มแล้วส่ง webhook ซ้ำ
ผู้ใช้จะได้ข้อความซ้ำ — นี่คือเหตุผลตรงที่เลือก FastAPI (มี `BackgroundTasks` ในตัว)

## 3.2 สามชั้นทำงานยังไง (ของจริง ณ วันนี้)

| ชั้น | ทำงานเมื่อ | กลไก | สถานะ |
|---|---|---|---|
| 1 | กดปุ่ม Rich Menu / Quick Reply, พิมพ์รหัสวิชา 7 หลัก, พิมพ์คำค้น | SQL ตรง + `pg_trgm` (`word_similarity`) | เสร็จ |
| 2 | พิมพ์คำถามที่ตรงกับ FAQ ในตาราง `faqs` | `word_similarity` สองทิศทางกับ `question` และ `variants` เทียบเกณฑ์ `FAQ_MATCH_THRESHOLD` | เสร็จ (ตารางยังไม่มีเนื้อหาจริง) |
| 3 | คำถามทั่วไป / กดปุ่ม "ปรึกษา AI" | เรียก LLM ผ่าน endpoint แบบ OpenAI-compatible | AI Chat เสร็จ / RAG ยังไม่มี |
| – | ไม่เข้าเงื่อนไขไหนเลย | ตอบว่ายังตอบไม่ได้ + เสนอปุ่มที่ทำได้ | เสร็จ |

**ลำดับสำคัญ:** FAQ (ชั้น 2) ถูกเช็ค**ก่อน**การค้นเอกสารอัตโนมัติ เพราะคำตอบที่คน
เขียนเองต้องชนะผลค้นของเครื่อง และถ้าคะแนนความคล้ายไม่ถึงเกณฑ์ → ตกไปชั้นถัดไป
ไม่ใช่ตอบมั่ว

## 3.3 ไฟล์ไหนทำอะไร

```
app/
  main.py         FastAPI — /webhook, /health, /liff, /admin, /api/*  (925 บรรทัด)
  config.py       อ่าน .env ด้วย pydantic-settings + fail fast ตอนสตาร์ต
  router.py       สมองของบอท — ตัดสินใจว่าคำถามนี้ตอบด้วยชั้นไหน (1,267 บรรทัด)
  repository.py   SQL ทั้งหมดของชั้นข้อมูล (ไม่มี SQL กระจายที่อื่น)
  db.py           connection pool ของ psycopg + Protocol ให้เทสใส่ของปลอมแทนได้
  planner.py      คำนวณความก้าวหน้า/วิชาเทอมถัดไป — ไม่เรียก LLM ไม่แตะ I/O เลย
  progress.py     แปลผลจาก planner ให้เป็นบทสนทนา LINE
  gpa.py          คำนวณเกรด/เป้า GPAX/เกียรตินิยม — ไม่เรียก LLM ไม่แตะ I/O
  ai_chat.py      โหมดปรึกษา AI (คุมจำนวนตา + หมดเวลา + สลับ Rich Menu)
  llm.py          ตัวเรียก LLM: retry + สลับโมเดลสำรอง + เพดานเวลารวม
  admin.py        API หน้า /admin + ล็อกอิน username/password (scrypt)
  admin_repo.py   SQL ของหน้า admin (มี allowlist ตารางที่แก้ได้)
  line/
    signature.py  ตรวจ HMAC-SHA256 ของ X-Line-Signature
    messages.py   ประกอบข้อความ/Quick Reply ให้ถูกรูปแบบของ LINE
    flex.py       Flex Message (การ์ด)
    client.py     เรียก Messaging API (reply / push / link Rich Menu)
    auth.py       ตรวจ LIFF ID token กับเซิร์ฟเวอร์ LINE
    rich_menu.py  สร้าง/อัปโหลด Rich Menu + พิกัดปุ่ม
run.py            ตัวรันเซิร์ฟเวอร์ (จำเป็นบน Windows)
web/liff/index.html    หน้าติ๊กวิชาที่ผ่าน (ไฟล์เดียว ไม่มี build step)
web/admin/index.html   หน้าเจ้าหน้าที่แก้ข้อมูล (ไฟล์เดียว ไม่มี build step)
kb/               scraper ดึงข้อมูลจากเว็บทะเบียน → SQLite
db/               migration, seed, สคริปต์ตรวจความถูกต้องของ SQL
scripts/          งานปฏิบัติการ: Rich Menu, ตั้ง webhook, นำเข้าแผนเรียน, สร้าง admin
tests/            ชุดทดสอบ (unit ไม่ต้องมีเน็ต/DB, integration ต้องมี Postgres จริง)
```

## 3.4 เทคโนโลยีที่เลือกและเหตุผล

| ส่วน | เลือกใช้ | เหตุผลที่เลือก (ไม่ใช่เพราะนิยม) |
|---|---|---|
| Backend | FastAPI 0.115 | ต้องตอบ 200 ทันทีแล้วทำงานต่อ — `BackgroundTasks` มีในตัว |
| Server | Uvicorn 0.42 (ผ่าน `run.py`) | ASGI; ต้องผ่าน `run.py` เพราะปัญหา event loop บน Windows |
| Database | PostgreSQL 17 | JSONB + array + ระดับ production |
| Vector | **pgvector** | ไม่ต้องรัน vector DB แยก (Chroma/Qdrant) → ลด service ลดต้นทุน |
| ค้นข้อความไทย | **pg_trgm** | Postgres ไม่มีตัวตัดคำไทย ทำ full-text search ไทยตรง ๆ ไม่ได้ จึงใช้ความคล้ายของตัวอักษรแทน |
| LLM | Gemini ผ่าน endpoint แบบ OpenAI-compatible | สลับผู้ให้บริการได้ด้วยการแก้ `LLM_BASE_URL` + `LLM_API_KEY` เท่านั้น |
| Scraper | requests + BeautifulSoup + **lxml** | `html.parser` ตัด `<td>` ของเว็บทะเบียนทิ้ง ต้องใช้ lxml |
| ตรวจ SQL | sqlglot | ตรวจไฟล์ migration/seed ได้โดยไม่ต้องมี Postgres |
| เก็บรหัสผ่าน admin | `hashlib.scrypt` (stdlib) | ไม่เพิ่ม dependency ให้เรื่องความปลอดภัย |

**ที่ตั้งใจไม่ใช้:** LangChain (ชั้นห่อเยอะเกินจำเป็น เขียนเองแล้ว debug ง่ายกว่า),
Celery (BackgroundTasks พอกับขนาดงานนี้), vector database แยก, ORM
(เขียน SQL ตรง ๆ ในไฟล์เดียวคุมได้กว่า)

## 3.5 ความทนทานต่อ AI ล่ม (ของจริงที่วัดมา)

วัดเมื่อ 21 ส.ค. 2569: ยิง LLM 7 ครั้ง ได้ HTTP 503 "high demand" **ในการยิงครั้ง
แรกทั้ง 7 ครั้ง** และผู้ใช้เห็นข้อความ "ระบบขัดข้อง" 4 ใน 7 ครั้ง (57%)
โดยไม่เกี่ยวกับเนื้อหาคำถาม `app/llm.py` จึงมี 2 ชั้น:

1. **retry รอสั้น ๆ** 0.5 → 1 → 2 วินาที (+ สุ่ม 25%) 4 ครั้งต่อโมเดล
2. **สลับโมเดลสำรอง** ตาม `LLM_FALLBACK_MODELS` เพราะวัดแล้วว่า 503 เกิดแยกกัน
   ต่อโมเดล — นาทีเดียวกันที่โมเดลหลัก 503 โมเดลสำรองตอบได้ปกติ

ทั้งสองชั้นอยู่ใต้เพดานเวลารวม `LLM_RETRY_BUDGET_SECONDS` (28 วินาที) ที่คุม
**ทั้งเชน** เพราะ reply token อายุสั้น — เลยงบแล้วเลิกทันที เพื่อให้ยังตอบผ่าน
reply ได้ ไม่ต้องเสียโควตา push · error 400/401/403 (คีย์/payload ผิด)
**ไม่ retry ไม่สลับ** เพราะลองใหม่ก็ผิดเหมือนเดิม

## 3.6 การวัดผลที่ฝังไว้ในระบบแล้ว

ทุกบทสนทนาถูกบันทึกลง `chat_logs` พร้อมป้าย `answered_by` **11 ค่า**:
`rich_menu`, `quick_reply`, `course`, `follow`, `search`, `faq`, `ai_chat`,
`planner`, `no_data`, `db_error`, `fallback` (ยังไม่มีค่า `rag`)

ป้ายชุดนี้ทำให้ตอบคำถามในบทที่ 4-5 ได้ด้วยข้อมูลจริงว่า แต่ละชั้นรับภาระเท่าไร
อัตราตอบไม่ได้ (`fallback` + `no_data`) เท่าไร และมีคำถามอะไรที่ระบบยังไม่รู้

> ข้อควรระวังในการตีความ: `no_data` / `db_error` / `fallback` **ทับป้ายพื้นผิว**
> ที่ผู้ใช้กดมา ดังนั้นจำนวน `rich_menu` ที่นับได้เป็น **ค่าต่ำสุด** ไม่ใช่จำนวน
> การกดปุ่มจริงทั้งหมด
