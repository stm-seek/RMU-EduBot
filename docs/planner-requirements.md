# Prerequisites และ Planner Engine — ข้อมูลที่ต้องการ

> **อัปเดต 23 ส.ค. 2026 — Planner Engine เขียนเสร็จและใช้งานได้แล้ว**
>
> * `curriculum_rules` = **32 แถว** (แผนการเรียน 643170151 จาก
>   `Student_Studyplan.asp` → `db/seed/003_curriculum_rules.sql`)
> * `prerequisites` = **ยัง 0 แถว** — ยังต้องขอเล่ม มคอ.2 จากคณะ
> * โค้ด: `app/planner.py` (คำนวณล้วน) + `app/progress.py` (ประกอบคำตอบ)
>   + `web/liff/index.html` (ให้นักศึกษาติ๊กวิชาที่ผ่าน)
> * ระหว่างที่ยังไม่มี prerequisite: planner ใช้ **ลำดับเทอมจากแผนการเรียน**
>   บวก `offering_patterns` (วิชานี้เปิดเทอมไหน) แล้วแจ้งผู้ใช้ทุกคำตอบว่า
>   ลำดับที่เห็นเป็นเพียง "เทอมที่แผนแนะนำ" ไม่ใช่เงื่อนไขบังคับ
>   (`app/progress.py::prereq_caveat` — ลบคำเตือนนี้ได้เมื่อกรอก prereq ครบ)
>
> ส่วนที่เหลือของเอกสารนี้คือสเปกเดิม เก็บไว้เป็นข้อมูลอ้างอิงตอนกรอก มคอ.2

## สถานะปัจจุบัน

### ข้อมูลที่มีแล้ว ✅
```
หลักสูตร MDI 643170151:
├── โครงสร้าง: 15 หมวด, 68 วิชา, 120 หน่วยกิต
├── คำอธิบายรายวิชา: 68/68 วิชา
├── ตารางสอน: 337 หมู่เรียน (4 เทอม)
├── offering_patterns: วิชาเปิดเทอมไหน
│   ├── เปิดทั้ง 2 เทอม: 25 วิชา
│   ├── เปิดเทอม 1 เท่านั้น: 12 วิชา
│   ├── เปิดเทอม 2 เท่านั้น: 8 วิชา
│   └── ไม่พบว่าเปิดเลย: 23 วิชา
└── categories: แยกหมวดบังคับ/เลือก
```

### ข้อมูลที่ยังว่างเปล่า ❌
```sql
SELECT COUNT(*) FROM prerequisites;      -- 0 แถว
SELECT COUNT(*) FROM curriculum_rules;   -- 0 แถว
```

---

## 1. ตาราง `prerequisites` — วิชาบังคับก่อน

### โครงสร้าง
```sql
CREATE TABLE prerequisites (
    id            BIGINT PRIMARY KEY,
    program_code  TEXT NOT NULL,           -- '643170151'
    course_code   TEXT NOT NULL,           -- วิชาที่จะลง
    requires_code TEXT NOT NULL,           -- วิชาที่ต้องผ่านก่อน
    kind          TEXT NOT NULL            -- 'hard' / 'soft' / 'concurrent'
                  CHECK (kind IN ('hard', 'soft', 'concurrent')),
    source        TEXT NOT NULL,           -- 'มคอ.2 หลักสูตร 643170151 หน้า 42'
    updated_at    TIMESTAMPTZ NOT NULL,
    UNIQUE (program_code, course_code, requires_code),
    CHECK (course_code <> requires_code)  -- ห้ามวิชาเป็น prereq ของตัวเอง
);
```

### ความหมายของ `kind`
- **`hard`** = ต้องผ่านก่อนจริง ๆ (ระบบทะเบียนบล็อกถ้าไม่ผ่าน)
  - ตอบนักศึกษา: "ต้องเรียนผ่าน X ก่อนถึงจะลง Y ได้"
  
- **`soft`** = แนะนำให้เรียนก่อน แต่ไม่บังคับ
  - ตอบนักศึกษา: "แนะนำให้เรียน X ก่อน แต่ลง Y ก่อนก็ได้"
  
- **`concurrent`** = เรียนพร้อมกันได้ (co-requisite)
  - ตอบนักศึกษา: "ลงพร้อมกับ X ได้"

### ตัวอย่างข้อมูลที่ต้องกรอก (สมมติ)
```sql
-- ตัวอย่างข้อมูลวิชาบังคับ (ต้องอ่านจาก มคอ.2 จริง)
INSERT INTO prerequisites (program_code, course_code, requires_code, kind, source) VALUES
('643170151', '7070102', '7070101', 'hard', 'มคอ.2 หลักสูตร 643170151 หน้า X'),
-- คณิตศาสตร์ 2 ต้องผ่านคณิต 1 ก่อน

('643170151', '7071203', '7071202', 'hard', 'มคอ.2 หลักสูตร 643170151 หน้า Y'),
-- โครงสร้างข้อมูล ต้องผ่านโปรแกรมมิ่ง 2 ก่อน

('643170151', '7071305', '7071204', 'soft', 'มคอ.2 หลักสูตร 643170151 หน้า Z'),
-- ฐานข้อมูลขั้นสูง แนะนำให้ผ่านฐานข้อมูลเบื้องต้นก่อน

('643170151', '7071401', '7071400', 'concurrent', 'มคอ.2 หลักสูตร 643170151 หน้า W');
-- โปรเจกต์ 1 ลงพร้อมกับสัมมนา 1 ได้
```

### วิธีใช้ใน Planner
```python
def can_take_course(student, course_code):
    """ตรวจสอบว่าเรียนวิชานี้ได้หรือยัง"""
    prereqs = db.query(
        "SELECT requires_code, kind FROM prerequisites "
        "WHERE program_code = ? AND course_code = ?",
        (student.program_code, course_code)
    )
    
    for req_code, kind in prereqs:
        if kind == 'hard':
            if req_code not in student.completed_courses:
                return False, f"ต้องเรียนผ่าน {req_code} ก่อน"
        elif kind == 'soft':
            if req_code not in student.completed_courses:
                # เตือนแต่ไม่บล็อก
                warnings.append(f"แนะนำให้เรียน {req_code} ก่อน")
        # concurrent ไม่ต้องเช็ค
    
    return True, None
```

---

## 2. ตาราง `curriculum_rules` — แผนการเรียน

### โครงสร้าง
```sql
CREATE TABLE curriculum_rules (
    id            BIGINT PRIMARY KEY,
    program_code  TEXT NOT NULL,           -- '643170151'
    course_code   TEXT NOT NULL,           -- รหัสวิชา
    std_year      SMALLINT,                -- ปีที่แนะนำให้เรียน (1-4)
    std_semester  SMALLINT,                -- เทอมที่แนะนำ (1-3)
    is_fixed_term BOOLEAN NOT NULL,        -- บังคับเทอมนี้เท่านั้น?
    note          TEXT,                    -- หมายเหตุ
    source        TEXT NOT NULL,           -- อ้างอิงแหล่งที่มา
    verified_by   TEXT,                    -- ใครตรวจสอบ
    updated_at    TIMESTAMPTZ NOT NULL,
    UNIQUE (program_code, course_code)
);
```

### ความหมาย
- **`std_year` + `std_semester`** = แผนการเรียนมาตรฐาน (ตาม มคอ.2)
  - ปี 1 เทอม 1, ปี 1 เทอม 2, ปี 2 เทอม 1, ...
  
- **`is_fixed_term`** = วิชานี้เปิดเทอมเดียว ห้ามเลื่อน
  - `TRUE` = ต้องเรียนเทอมนี้ พลาดแล้วรอปีหน้า
  - `FALSE` = ยืดหยุ่น เลื่อนได้ (เปิดหลายเทอม)

### ตัวอย่างข้อมูลที่ต้องกรอก
```sql
-- วิชาบังคับปี 1 เทอม 1
INSERT INTO curriculum_rules VALUES
(DEFAULT, '643170151', '7070101', 1, 1, FALSE, 'คณิตศาสตร์ 1 (เปิดทุกเทอม)', 'มคอ.2 หน้า 15', NULL, now()),
(DEFAULT, '643170151', '7071201', 1, 1, FALSE, 'โปรแกรมมิ่ง 1', 'มคอ.2 หน้า 15', NULL, now()),

-- วิชาที่เปิดเทอมเดียว (พลาดต้องรอปีหน้า)
(DEFAULT, '643170151', '7071499', 4, 1, TRUE, 'โปรเจกต์วิจัย (เปิดเทอม 1 เท่านั้น)', 'มคอ.2 หน้า 18', NULL, now()),

-- ฝึกงาน (ปี 4 เทอม 2 และภาคฤดูร้อน)
(DEFAULT, '643170151', '7071498', 4, 2, FALSE, 'สหกิจศึกษา', 'มคอ.2 หน้า 18', NULL, now());
```

### วิธีใช้ใน Planner
```python
def suggest_courses_for_term(student, target_year, target_semester):
    """แนะนำวิชาที่ควรลงในเทอมนี้"""
    
    # 1. ดึงวิชาที่แผนแนะนำให้เรียนเทอมนี้
    planned = db.query(
        "SELECT course_code FROM curriculum_rules "
        "WHERE program_code = ? AND std_year = ? AND std_semester = ?",
        (student.program_code, target_year, target_semester)
    )
    
    # 2. กรองเฉพาะวิชาที่ยังไม่เรียน + ผ่าน prereq
    available = []
    for course_code in planned:
        if course_code in student.completed_courses:
            continue
        can_take, reason = check_prerequisites(student, course_code)
        if can_take:
            available.append(course_code)
    
    return available
```

---

## 3. Planner Engine ต้องทำอะไร

### Input (ที่ต้องรู้)
1. **ข้อมูลนักศึกษา:**
   - `program_code` (หลักสูตรที่เรียน)
   - `study_year` (ชั้นปีปัจจุบัน)
   - `completed_courses[]` (วิชาที่ผ่านแล้ว) — จาก LIFF

2. **ข้อมูลหลักสูตร:**
   - `courses` — รายวิชาทั้งหมด
   - `categories` — หมวดบังคับ/เลือก, หน่วยกิตที่ต้องเรียน
   - **`prerequisites`** — วิชาบังคับก่อน ⚠️ **ยังว่าง**
   - **`curriculum_rules`** — แผนการเรียนมาตรฐาน ⚠️ **ยังว่าง**
   - `offering_patterns` — วิชาเปิดเทอมไหน

### Output (ที่ต้องคำนวณ)
```python
# ตัวอย่าง output ของ planner
{
    "credits_completed": 60,         # เรียนไปแล้ว
    "credits_remaining": 60,         # เหลืออีกเท่าไหร่
    "required_courses": [            # วิชาบังคับที่ยังขาด
        {"code": "7071203", "name": "โครงสร้างข้อมูล", "credits": 3},
        {"code": "7071305", "name": "ฐานข้อมูล", "credits": 3}
    ],
    "elective_credits_needed": {     # วิชาเลือกยังต้องเรียนอีก
        "หมวดเลือก IT": 6,
        "หมวดเลือกเสรี": 6
    },
    "suggested_next_term": [         # แนะนำวิชาเทอมหน้า
        {
            "code": "7071203",
            "name": "โครงสร้างข้อมูล",
            "credits": 3,
            "reason": "วิชาบังคับปี 2 เทอม 1",
            "can_take": True,
            "warnings": []
        },
        {
            "code": "7071305",
            "name": "ฐานข้อมูล",
            "credits": 3,
            "reason": "วิชาบังคับปี 2 เทอม 2",
            "can_take": False,
            "warnings": ["ต้องผ่าน 7071204 ก่อน"]
        }
    ],
    "graduation_check": {
        "can_graduate": False,
        "missing_requirements": [
            "ขาดวิชาบังคับ 5 วิชา (15 หน่วยกิต)",
            "ขาดวิชาเลือก 2 หน่วยกิต"
        ]
    }
}
```

### อัลกอริทึมหลัก

#### 3.1 ตรวจสอบ Prerequisites (Topological Sort)
```python
def check_prerequisites(student, course_code):
    """ตรวจว่าเรียนวิชานี้ได้หรือยัง"""
    prereqs = db.query(
        "SELECT requires_code, kind FROM prerequisites "
        "WHERE course_code = ?", (course_code,)
    )
    
    blocked = []
    warnings = []
    
    for req_code, kind in prereqs:
        if req_code not in student.completed_courses:
            if kind == 'hard':
                blocked.append(req_code)
            elif kind == 'soft':
                warnings.append(f"แนะนำให้เรียน {req_code} ก่อน")
    
    return len(blocked) == 0, blocked, warnings
```

#### 3.2 คำนวณหน่วยกิตที่เหลือ
```python
def calculate_remaining_credits(student):
    """คำนวณว่าเหลือต้องเรียนอีกกี่หน่วยกิต แยกตามหมวด"""
    
    # 1. ดึงหน่วยกิตที่ได้แล้ว
    completed = {}
    for course_code in student.completed_courses:
        course = db.get_course(course_code)
        category = db.get_category(student.program_code, course_code)
        completed[category.label] = completed.get(category.label, 0) + course.credits
    
    # 2. ดึงหน่วยกิตที่ต้องเรียน
    required = db.query(
        "SELECT label, required_credits FROM categories "
        "WHERE program_code = ? AND is_leaf = TRUE",
        (student.program_code,)
    )
    
    # 3. คำนวณที่เหลือ
    remaining = {}
    for label, req_credits in required:
        remaining[label] = max(0, req_credits - completed.get(label, 0))
    
    return remaining
```

#### 3.3 แนะนำวิชาเทอมหน้า
```python
def suggest_next_term(student, target_year, target_semester):
    """แนะนำวิชาที่ควรลงเทอมหน้า"""
    
    suggestions = []
    
    # 1. วิชาตามแผนการเรียน
    planned = db.query(
        "SELECT course_code FROM curriculum_rules "
        "WHERE program_code = ? AND std_year = ? AND std_semester = ?",
        (student.program_code, target_year, target_semester)
    )
    
    for course_code in planned:
        if course_code in student.completed_courses:
            continue
            
        can_take, blocked, warnings = check_prerequisites(student, course_code)
        
        # ตรวจว่าวิชาเปิดเทอมนี้หรือไม่
        pattern = db.get_offering_pattern(course_code)
        is_offered = pattern[f"opens_sem{target_semester}"]
        
        suggestions.append({
            "course_code": course_code,
            "can_take": can_take and is_offered,
            "blocked_by": blocked,
            "warnings": warnings,
            "not_offered": not is_offered
        })
    
    # 2. วิชาบังคับที่พลาดมาจากเทอมก่อน
    # ... (เพิ่มลอจิก)
    
    # 3. วิชาเลือกที่ยังต้องเรียน
    # ... (เพิ่มลอจิก)
    
    return suggestions
```

---

## 4. ข้อมูลที่ต้องกรอกจาก มคอ.2

### สิ่งที่ต้องหา
- [ ] **แผนการเรียน** (4 ปี × 2 เทอม = 8 เทอม)
  - วิชาใดเรียนปีไหน เทอมไหน
  - วิชาใดเปิดเทอมเดียว (is_fixed_term = TRUE)

- [ ] **วิชาบังคับก่อน** (Prerequisites)
  - ต้องผ่านวิชา X ก่อนถึงจะลง Y ได้
  - แยก hard / soft / concurrent

### ประมาณการ
- หลักสูตร MDI มีวิชาบังคับ **18 วิชา + ฝึกงาน 1**
- ถ้าโดยเฉลี่ย 1 วิชามี prereq 1-2 วิชา = **~30-40 แถวใน prerequisites**
- แผนการเรียน 8 เทอม × 5-6 วิชา/เทอม = **~45 แถวใน curriculum_rules**

**เวลากรอก: ประมาณ 1-2 ชั่วโมง**

---

## 5. การทำงานของ Planner (ภาพรวม)

```
User → LIFF: กรอกวิชาที่ผ่านแล้ว
  ↓
Planner Engine (deterministic code):
  1. ดึง completed_courses จาก user_completed_courses
  2. คำนวณหน่วยกิตที่ได้ (แยกตามหมวด)
  3. ตรวจสอบ prerequisites (topological sort)
  4. ดึง curriculum_rules (แผนการเรียนมาตรฐาน)
  5. ดึง offering_patterns (วิชาเปิดเทอมไหน)
  6. คำนวณวิชาที่ควรลงเทอมหน้า
  7. ตรวจสอบเงื่อนไขจบ
  ↓
Structured Output → LLM: เรียบเรียงคำอธิบาย
  ↓
LINE Chatbot → แนะนำแผนการเรียน
```

### หลักการสำคัญ
- **Planner = Deterministic Code** (Python)
  - คำนวณ prerequisite ด้วย graph algorithm
  - คำนวณหน่วยกิตด้วย arithmetic
  - **ห้ามให้ LLM คิด** (LLM คิดผิดเรื่องตัวเลข/graph ได้)

- **LLM = Natural Language Generator**
  - รับ output จาก planner (JSON)
  - เรียบเรียงเป็นประโยคไทยที่เข้าใจง่าย
  - อธิบายเหตุผล + ให้คำแนะนำ

---

## 6. ขั้นตอนถัดไป

### ลำดับการทำ
1. ✅ Database schema พร้อมแล้ว
2. ✅ Knowledge base มีข้อมูลครบ (ยกเว้น prerequisites/curriculum_rules)
3. ⚠️ **ขอ มคอ.2 จากคณะ** (ไฟล์ PDF หรือเล่มจริง)
4. ⚠️ **กรอก prerequisites** (~30-40 แถว, 30-60 นาที)
5. ⚠️ **กรอก curriculum_rules** (~45 แถว, 30-60 นาที)
6. ⚠️ **เขียน planner engine** (Python, ~500-1000 บรรทัด)
7. ⚠️ **เขียน LIFF** (หน้าติ๊กวิชาที่ผ่าน)
8. ⚠️ **ทดสอบ** (unit test + integration test)

### ทางลัด (ถ้าไม่มี มคอ.2)
- ใช้ `offering_patterns` แทน `curriculum_rules` ชั่วคราว
  - ข้อดี: มีข้อมูลแล้ว (วิชาเปิดเทอมไหน)
  - ข้อเสีย: ไม่รู้แผนปี/เทอมมาตรฐาน แนะนำไม่แม่น

- ไม่มี `prerequisites` = ตอบไม่ได้เลยว่า "ต้องเรียนวิชาอะไรก่อน"
  - **ไม่มีทางลัด ต้องมีข้อมูลนี้**

---

## สรุป

| ข้อมูล | สถานะ | จำเป็นต่อ Planner |
|--------|-------|-------------------|
| courses | ✅ มี 68 วิชา | ✅ จำเป็น |
| categories | ✅ มี 15 หมวด | ✅ จำเป็น |
| offering_patterns | ✅ มี | ⚠️ ใช้ได้ชั่วคราว |
| **prerequisites** | ❌ **ว่าง** | ⚠️ **บล็อกหลัก** |
| **curriculum_rules** | ❌ **ว่าง** | ⚠️ **บล็อกหลัก** |
| user_completed_courses | ⚠️ รอ LIFF | ✅ จำเป็น |

**ข้อสรุป: ต้องกรอก prerequisites และ curriculum_rules จาก มคอ.2 ก่อน ถึงจะเขียน planner ได้**
