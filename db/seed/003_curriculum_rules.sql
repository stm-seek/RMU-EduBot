-- ==========================================================================
--  curriculum_rules — แผนการเรียนมาตรฐาน 643170151 : การจัดการนวัตกรรมดิจิทัล
--
--  ที่มา: https://regis.rmu.ac.th/registrar/Student_Studyplan.asp
--         (แท็บ "แผนการเรียน" ของระบบทะเบียน — ต้อง login)
--         snapshot: snapshot_curriculum_plan.txt, parser: scripts/parse_curriculum_plan.py
--
--  ต้องรัน 001_init.sql ก่อน / รันซ้ำได้ (idempotent ผ่าน ON CONFLICT)
--
--  ต้องรัน 005_planner.sql ก่อน (คอลัมน์ course_code_full)
--
--  ข้อควรรู้ 3 ข้อ (อย่าเข้าใจผิดตอนเอาไปคำนวณ):
--
--  0. course_code = 7 หลัก (ใช้ JOIN courses / ตรงกับที่ router ดึงจากข้อความ)
--     course_code_full = รหัสในแผน เช่น 7071102-3 (เลขท้าย = รุ่นหลักสูตร)
--
--  1. is_fixed_term = FALSE ทุกแถว — แผนนี้เป็น "เทอมที่แนะนำ" ไม่ใช่ข้อบังคับ
--     ระบบทะเบียนไม่ได้บอกว่าวิชาไหนล็อกเทอม จึงไม่เดาแทน
--
--  2. แผนมีช่อง "วิชาเลือกเสรี" (รหัส 500-2) อีก 2 ตัว ปี 2/1 และ ปี 2/2
--     รวม 6 หน่วยกิต — **ไม่ใส่ในตารางนี้** เพราะไม่ใช่รหัสวิชาจริง
--     (UNIQUE (program_code, course_code) ใส่ซ้ำไม่ได้ด้วย) planner ต้องนับ
--     6 หน่วยกิตนี้แยกเป็นโควตาเลือกเสรี ไม่ใช่รายวิชา
--
--  3. หน่วยกิตของ 32 วิชานี้ = 105 (31 วิชา x 3 + ฝึกประสบการณ์ 12)
--     + เลือกเสรี 6 (ข้อ 2) = 111 แต่ programs.total_credits = 120
--     → แผนในระบบยังขาดอีก 9 หน่วยกิตที่ไม่ได้ระบุ ต้องยืนยันกับ มคอ.2
--     planner จึงต้องคิด "หน่วยกิตที่เหลือ" จาก total_credits ไม่ใช่จากผลรวมแผน
-- ==========================================================================

BEGIN;

INSERT INTO curriculum_rules
    (program_code, course_code, course_code_full, std_year, std_semester, is_fixed_term, note, source, updated_at)
VALUES
    -- ปี 1 ภาคเรียนที่ 1 (2564/1) — 6 วิชา 18 นก.
    ('643170151', '1209903', '1209903-1', 1, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '1409905', '1409905-1', 1, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071101', '7071101-3', 1, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071102', '7071102-3', 1, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071103', '7071103-3', 1, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071104', '7071104-3', 1, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    -- ปี 1 ภาคเรียนที่ 2 (2564/2) — 6 วิชา 18 นก.
    ('643170151', '1109902', '1109902-1', 1, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '1309903', '1309903-1', 1, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '1409903', '1409903-1', 1, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071105', '7071105-2', 1, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071106', '7071106-2', 1, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071107', '7071107-1', 1, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    -- ปี 2 ภาคเรียนที่ 1 (2565/1) — 5 วิชา + เลือกเสรี 1 ตัว
    ('643170151', '1109904', '1109904-1', 2, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '1409907', '1409907-1', 2, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071201', '7071201-3', 2, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071202', '7071202-3', 2, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7072203', '7072203-2', 2, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    -- ปี 2 ภาคเรียนที่ 2 (2565/2) — 5 วิชา + เลือกเสรี 1 ตัว
    ('643170151', '1109901', '1109901-1', 2, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '1209901', '1209901-1', 2, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '1309904', '1309904-1', 2, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071203', '7071203-3', 2, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071204', '7071204-3', 2, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    -- ปี 3 ภาคเรียนที่ 1 (2566/1) — 4 วิชา 12 นก.
    ('643170151', '7071301', '7071301-3', 3, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071302', '7071302-3', 3, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7072306', '7072306-3', 3, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7072313', '7072313-1', 3, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    -- ปี 3 ภาคเรียนที่ 2 (2566/2) — 2 วิชา 6 นก.
    ('643170151', '7071303', '7071303-3', 3, 2, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071402', '7071402-3', 3, 2, FALSE, 'โครงงาน 1', 'Student_Studyplan.asp 2026-08-22', now()),
    -- ปี 4 ภาคเรียนที่ 1 (2567/1) — 3 วิชา 9 นก.
    ('643170151', '7071401', '7071401-4', 4, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071403', '7071403-3', 4, 1, FALSE, 'โครงงาน 2 — ตามแผนอยู่หลังโครงงาน 1', 'Student_Studyplan.asp 2026-08-22', now()),
    ('643170151', '7071404', '7071404-1', 4, 1, FALSE, NULL, 'Student_Studyplan.asp 2026-08-22', now()),
    -- ปี 4 ภาคเรียนที่ 2 (2567/2) — 1 วิชา 12 นก.
    ('643170151', '7073401', '7073401-3', 4, 2, FALSE, 'ฝึกประสบการณ์ 12 นก. แผนวางไว้เทอมสุดท้าย', 'Student_Studyplan.asp 2026-08-22', now())
ON CONFLICT (program_code, course_code) DO UPDATE SET
    course_code_full = EXCLUDED.course_code_full,
    std_year      = EXCLUDED.std_year,
    std_semester  = EXCLUDED.std_semester,
    is_fixed_term = EXCLUDED.is_fixed_term,
    note          = EXCLUDED.note,
    source        = EXCLUDED.source,
    updated_at    = now();

COMMIT;
