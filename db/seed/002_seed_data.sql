-- ==========================================================================
--  Seed data — สร้างอัตโนมัติจาก kb/data/rmu_kb.db
--  ห้ามแก้ไฟล์นี้ด้วยมือ ให้แก้ที่ scraper แล้ว export ใหม่
--  สร้างเมื่อ: 2026-08-17T09:32:24+00:00
--
--  ต้องรัน 001_init.sql ก่อน
--  รันซ้ำได้ (idempotent ผ่าน ON CONFLICT)
-- ==========================================================================

BEGIN;

-- ── programs (2 แถว) ──────────────────────────────────────────────────
INSERT INTO programs (program_id, faculty_id, level_id, program_code, program_name, faculty_name, level_name, degree_name, department_name, total_credits, source_url, scraped_at)
VALUES (59721, '70', '31', '643170151', 'การจัดการนวัตกรรมดิจิทัล', 'เทคโนโลยีสารสนเทศ', 'ปริญญาตรี 4 ปี ภาคปกติ', 'วิทยาศาสตรบัณฑิต', 'การจัดการนวัตกรรมดิจิทัล', 120, 'https://regis.rmu.ac.th/registrar/program_info_1.asp?f_cmd=2&levelid=31&programid=59721&facultyid=70', '2026-08-17T05:50:11+00:00')
ON CONFLICT (program_id) DO UPDATE SET
    faculty_id = EXCLUDED.faculty_id,
    level_id = EXCLUDED.level_id,
    program_code = EXCLUDED.program_code,
    program_name = EXCLUDED.program_name,
    faculty_name = EXCLUDED.faculty_name,
    level_name = EXCLUDED.level_name,
    degree_name = EXCLUDED.degree_name,
    department_name = EXCLUDED.department_name,
    total_credits = EXCLUDED.total_credits,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO programs (program_id, faculty_id, level_id, program_code, program_name, faculty_name, level_name, degree_name, department_name, total_credits, source_url, scraped_at)
VALUES (60188, '70', '31', '653170011', 'เทคโนโลยีสารสนเทศ', 'เทคโนโลยีสารสนเทศ', 'ปริญญาตรี 4 ปี ภาคปกติ', 'วิทยาศาสตรบัณฑิต', 'เทคโนโลยีสารสนเทศ', 0, 'https://regis.rmu.ac.th/registrar/program_info_1.asp?f_cmd=2&levelid=31&programid=60188&facultyid=70', '2026-08-17T05:30:07+00:00')
ON CONFLICT (program_id) DO UPDATE SET
    faculty_id = EXCLUDED.faculty_id,
    level_id = EXCLUDED.level_id,
    program_code = EXCLUDED.program_code,
    program_name = EXCLUDED.program_name,
    faculty_name = EXCLUDED.faculty_name,
    level_name = EXCLUDED.level_name,
    degree_name = EXCLUDED.degree_name,
    department_name = EXCLUDED.department_name,
    total_credits = EXCLUDED.total_credits,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;

-- ── categories (26 แถว) ────────────────────────────────────────────────
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 0, NULL, '1', 0, 'หมวดศึกษาทั่วไป', NULL, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 1, 0, '1.1', 1, 'ชุดวิชาภาษาและการสื่อสาร', NULL, TRUE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 5, 0, '1.2', 1, 'ชุดวิชาคุณค่าและทักษะชีวิต', NULL, TRUE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 8, 0, '1.3', 1, 'ชุดวิชาสหวิทยาการสังคมศาสตร์เพื่อพัฒนาท้องถิ่น', NULL, TRUE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 11, 0, '1.4', 1, 'ชุดวิชาคุณภาพชีวิตในยุคดิจิทัล', NULL, TRUE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 15, NULL, '2', 0, 'กลุ่มวิชาเฉพาะ', NULL, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 16, 15, '2.1', 1, 'กลุ่มวิชาแกน', NULL, TRUE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 21, 15, '2.2', 1, 'กลุ่มวิชาเฉพาะด้าน', NULL, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 22, 21, '2.2.1', 2, 'กลุ่มวิชาบังคับ', NULL, TRUE, 'required')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 45, 21, '2.2.2', 2, 'กลุ่มวิชาเลือก', NULL, TRUE, 'elective')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (60188, 67, NULL, '3', 0, 'หมวดวิชาเลือกเสรี', NULL, FALSE, 'elective')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 0, NULL, '1', 0, 'หมวดศึกษาทั่วไป', 30, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 1, 0, '1.1', 1, 'กลุ่มวิชาภาษา', 9, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 2, 1, '1.1.1', 2, 'กลุ่มวิชาภาษา (บังคับ)', 6, TRUE, 'required')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 5, 1, '1.1.2', 2, 'กลุ่มวิชาภาษา (เลือก)', 3, TRUE, 'elective')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 10, 0, '1.2', 1, 'กลุ่มวิชามนุษย์ศาสตร์', 6, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 11, 10, '1.2.1', 2, 'กลุ่มวิชามนุษย์ศาสตร์ (เลือก)', 6, TRUE, 'elective')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 15, 0, '1.3', 1, 'กลุ่มวิชาสังคมศาสตร์', 6, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 16, 15, '1.3.1', 2, 'กลุ่มวิชาสังคมศาสตร์ (เลือก)', 6, TRUE, 'elective')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 21, 0, '1.4', 1, 'กลุ่มวิชาวิทยาศาสตร์ เทคโนโลยีและคณิศาสตร์', 9, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 22, 21, '1.4.1', 2, 'กลุ่มวิชาวิทยาศาสตร์ เทคโนโลยีและคณิศาสตร์ (เลือก)', 9, TRUE, 'elective')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 30, NULL, '2', 0, 'กลุ่มวิชาเฉพาะด้าน', 84, FALSE, NULL)
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 31, 30, '2.1', 1, 'กลุ่มวิชา บังคับ', 54, TRUE, 'required')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 50, 30, '2.2', 1, 'กลุ่มวิชา เลือก', 18, TRUE, 'elective')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 80, 30, '2.3', 1, 'กลุ่มวิชาปฏิบัติการและการฝึกประสบการณ์วิชาชีพบังคับ', 12, TRUE, 'required')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;
INSERT INTO categories (program_id, row_id, parent_row_id, number, depth, label, required_credits, is_leaf, selection_mode)
VALUES (59721, 82, NULL, '3', 0, 'หมวดวิชาเลือกเสรี', 6, FALSE, 'elective')
ON CONFLICT (program_id, row_id) DO UPDATE SET
    parent_row_id = EXCLUDED.parent_row_id,
    number = EXCLUDED.number,
    depth = EXCLUDED.depth,
    label = EXCLUDED.label,
    required_credits = EXCLUDED.required_credits,
    is_leaf = EXCLUDED.is_leaf,
    selection_mode = EXCLUDED.selection_mode;

-- ── courses (145 แถว) ───────────────────────────────────────────────────
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (22956, '7072403', 'การจัดการสารสนเทศแหล่งท่องเที่ยว', 'Tourist Information Management', '3 (2-2-5)', 3, 'ความหมายแนวคิดและประเภทของทรัพยากรแหล่งท่องเที่ยว คุณค่าของแหล่งท่องเที่ยว การกระจายของแหล่งท่องเที่ยวตามธรรมชาติ แหล่งท่องเที่ยวทางวัฒนธรรม แหล่งท่องเที่ยวทางประวัติศาสตร์สิ่งอำนวยความสะดวกต่าง ๆ เพื่อการท่องเที่ยว ปัญหาและการจัดการทรัพยากรแหล่งท่องเที่ยวรวมทั้งการ ฝึกปฏิบัติการวางแผนการพัฒนาการท่องเที่ยวอย่างยั่งยืนโดยอาศัยระบบสารสนเทศและออกภาคสนาม', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=22956', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (27936, '7012473', 'การพาณิชย์อิเล็กทรอนิกส์', 'Electronic Commerce', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (27937, '7011206', 'การออกแบบและการจัดการฐานข้อมูล', 'Database Design and Management', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (27938, '7011301', 'ปฏิสัมพันธ์ระหว่างมนุษย์กับคอมพิวเตอร์', 'Human Computer Interaction', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (27939, '7011205', 'การวิเคราะห์และออกแบบเชิงวัตถุ', 'Object-Oriented Analysis and Design', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (27940, '7012468', 'การบริหารโครงงานเทคโลยีสารสนเทศ', 'Information Technology Project Management', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28341, '7011102', 'เทคโนโลยีเว็บ', 'Web Technology', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28342, '7011204', 'การโปรแกรมในระบบเว็บ', 'Web Programming', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28343, '7011304', 'ปฏิบัติการพัฒนาโปรแกรมประยุกต์ฐานข้อมูลบนเว็บ', 'Web Database Application Development Workshop', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28352, '7011202', 'กระบวนการพัฒนาซอฟต์แวร์', 'Software Development Process II', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28358, '7012462', 'ระบบสารสนเทศเพื่อการจัดการ', 'Management Information Systems', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28359, '7012463', 'การออกแบบกราฟิกบนคอมพิวเตอร์', 'Computer Graphic Design', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28360, '7012464', 'การสร้างสื่อดิจิทัล', 'Digital Media Production', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28361, '7012465', 'กรรมวิธีเชิงอ็อบเจกต์ขั้นสูง', 'Advanced Object Oriented Methodology', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28362, '7012466', 'ปฏิบัติการโปรแกรมจาวาฝั่งแม่ข่าย', 'Java Server Side Programming Workshop', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28364, '7012470', 'ปฏิบัติการระบบวางแผนทรัพยากรวิสาหกิจ', 'Enterprise Resource Planning Workshop', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28365, '7012471', 'ปฏิบัติการบริหารเครือข่ายผู้ผลิต', 'Supply Chain Management Workshop', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28366, '7012472', 'ปฏิบัติการเครือข่ายระดับวิสาหกิจ', 'Enterprise Networking Workshop', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28367, '7012474', 'ระบบสนับสนุนการตัดสินใจ', 'Decision Support System', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28368, '7012475', 'การประกันคุณภาพระบบสารสนเทศ', 'Quality Assurance for Information System', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28369, '7012476', 'เทคโนโลยีอินเทอร์เน็ต', 'Internet Technology', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (28370, '7012477', 'ปัญญาประดิษฐ์', 'Artificial Intelligence', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (31665, '7012481', 'เทคโนโลยีการประมวลผลแบบกลุ่มเมฆ', 'Cloud Computing Technology', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32701, '1109901', 'ภาษาอังกฤษสำหรับชีวิตประจำวัน', 'English for Daily Life', '3 (2-2-5)', 3, 'การสื่อสารในสถานการณ์ต่าง ๆ ในชีวิตประจำวัน การทักทายและการแนะนำตัว การบรรยายลักษณะบุคคล สิ่งของ สถานที่ การสอบถามเส้นทางและบอกทิศทาง การแสดงความรู้สึก การอ่านข่าว ประกาศ โฆษณา และบทความสั้นๆ', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32701', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32702, '1109902', 'ภาษาไทยเพื่อการสื่อสาร', 'Thai Language for Communication', '3 (2-2-5)', 3, 'พัฒนาทักษะการฟัง การพูด การดู การอ่าน และการเขียน สามารถสรุปความ ขยายความ ตีความ คิดวิเคราะห์ คิดสังเคราะห์ และประเมินค่าได้ ค้นคว้าและนำเสนอในรูปแบบและสื่อต่าง ๆ', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32702', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32703, '1109903', 'ภาษาอังกฤษเพื่อเตรียมความพร้อมในการประกอบอาชีพ', 'English for Career Preparation', '3 (2-2-5)', 3, 'ทักษะการฟัง การพูด การอ่าน และการเขียนภาษาอังกฤษ การอ่านโฆษณาจัดหางาน การกรอกแบบฟอร์มใบสมัคร การเขียนจดหมายสมัครงาน การเขียนประวัติส่วนตัว การเตรียมตัวเพื่อสัมภาษณ์', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32703', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32704, '1109904', 'ศิลปะการพูดให้สัมฤทธิผล', 'Art of Effective Speech', '3 (2-2-5)', 3, 'ความมุ่งหมายของการพูด หลักการพูดแบบต่าง ๆ การสร้างบุคลิกภาพในการพูด มารยาทใน การพูด การเตรียมการพูด การประเมินผลและการปรับปรุงการพูด หลักการฝึกพูดในชีวิตประจำวันและ การพูดในที่ชุมชนให้สัมฤทธิ์ผลอย่างสร้างสรรค์', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32704', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32705, '1109905', 'ภาษาจีนเพื่อการสื่อสาร', 'Chinese for Communication', '3 (2-2-5)', 3, 'สัทอักษร (Pinyin) คำศัพท์และโครงสร้างประโยคภาษาจีนพื้นฐาน เน้นทักษะด้านการสนทนา ในวงคำศัพท์ที่ใช้ในชีวิตประจำวัน ได้แก่ การทักทาย การแนะนำตนเอง การบอกเวลา คำเรียกเครือญาติ ส่วนต่าง ๆ ของร่างกาย สถานที่ สี และสิ่งของ ความรู้อักษรจีน 150 ตัว', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32705', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32706, '1109906', 'ภาษาฝรั่งเศสเพื่อการสื่อสาร', 'French for Communication', '3 (2-2-5)', 3, 'คำศัพท์และโครงสร้างประโยคภาษาฝรั่งเศสพื้นฐาน เน้นทักษะด้านการสนทนาในวงคำศัพท์ที่ใช้ในชีวิตประจำวัน ได้แก่ การทักทาย การแนะนำตนเอง การบอกเวลา คำเรียกเครือญาติ ส่วนต่างๆ ของร่างกาย สถานที่ สี และสิ่งของ ความรู้คำศัพท์ภาษาฝรั่งเศส 150 คำ', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32706', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32707, '1209901', 'การพัฒนาตนเพื่อความสุขของชีวิต', 'Self-Development for a Happy Life', '3 (2-2-5)', 3, 'ความหมาย และองค์ประกอบของเป้าหมายในชีวิต หลักการพัฒนาตน แนวทางปฏิบัติใน การพัฒนาตนเพื่อความสุขในชีวิตตามหลักปรัชญาและจิตวิทยา', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32707', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32708, '1209902', 'สุนทรียภาพของชีวิต', 'Aesthetics Appreciation', '3 (2-2-5)', 3, 'ความหมาย ความเป็นมา ความสำคัญของสุนทรียศาสตร์ แนวคิด รูปแบบที่มีผลต่อการรับรู้ ทางความงามและซาบซึ้งในศิลปะ ดนตรี นาฏศิลป์และการแสดง การพัฒนาและฝึกประสบการณ์ การรับรู้เพื่อปลูกฝังสุนทรียภาพให้เจริญงอกงาม นำไปสู่คุณค่าในการดำเนินชีวิตของมนุษย์ในสังคม', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32708', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32709, '1209903', 'ทักษะการเรียนรู้สารสนเทศเพื่อการคิดและค้นคว้า', 'Information Literacy Skills for Thinking and Searching', '3 (2-2-5)', 3, 'แนวคิดเกี่ยวกับการรู้สารสนเทศ วิธีการสืบค้นสารสนเทศและเครื่องมือ กระบวนการและ การคิดเชิงสร้างสรรค์เพื่อสังคม การวิเคราะห์และประเมินสารสนเทศ การอ้างอิงและการเขียนรายงาน ทางวิชาการ', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32709', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32710, '1309901', 'สังคมและทรัพยากรธรรมชาติ', 'Society and Natural Resources', '3 (2-2-5)', 3, 'ทรัพยากรธรรมชาติและสิ่งแวดล้อม ความสัมพันธ์ระหว่างระบบนิเวศน์กับมนุษย์ ภูมิศาสตร์การตั้งถิ่นฐาน ประชากรและเศรษฐกิจ ภูมิปัญญากับทรัพยากรธรรมชาติ ผลกระทบจากกิจกรรมมนุษย์ต่อสิ่งแวดล้อม ตลอดจนการส่งเสริมการมีส่วนร่วมในการจัดการสิ่งแวดล้อมเพื่อการพัฒนาที่ยั่งยืน', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32710', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32711, '1309902', 'พลวัตทางสังคม', 'Social Dynamics', '3 (2-2-5)', 3, 'ความเป็นมา พัฒนาการ และหลักการทางด้านสังคม วัฒนธรรม เศรษฐกิจ การเมือง สิ่งแวดล้อม และการเกษตรที่สอดคล้องกับชีวิตประจำวัน', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32711', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32712, '1309903', 'ศาสตร์พระราชา', 'Local Development from King’s Philosophy', '3 (2-2-5)', 3, 'ศาสตร์พระราชาในประวัติศาสตร์กับการพัฒนาชาติไทยตั้งแต่สมัยสุโขทัย อยุธยา ธนบุรี และ รัตนโกสินทร์ตอนต้นพอสังเขป ศาสตร์พระราชาตามโครงการตามแนวพระราชดำริในพระบาทสมเด็จ พระปรมินทรมหาภูมิพลอดุลยเดช (รัชกาลที่ 9) กับการพัฒนาอย่างยั่งยืน', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32712', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32713, '1309904', 'กฎหมายกับสังคม', 'Law and Society', '3 (2-2-5)', 3, 'ความรู้ทั่วไปเกี่ยวกับกฎหมายที่มีความสัมพันธ์และจำเป็นต้องใช้ในชีวิตประจำวันตามปรากฏการณ์ทางสังคมที่เปลี่ยนแปลงในสถานการณ์ปัจจุบัน หลักกฎหมายและนิติสัมพันธ์ของกฎหมายมหาชนและกฎหมายเอกชน หลักสิทธิและเสรีภาพขั้นพื้นฐานตามกฎหมายรัฐธรรมนูญ ความรู้เบื้องต้นเกี่ยวกับกฎหมายแพ่งและพาณิชย์ กฎหมายอาญา การประยุกต์และบูรณาการการใช้กฎหมายให้ได้เป็น ผลจริงในชีวิตประจำวัน', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32713', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32714, '1409901', 'วิทยาศาสตร์และเทคโนโลยีเพื่อคุณภาพชีวิต', 'Science and Technology for Quality of Life', '3 (2-2-5)', 3, 'การประยุกต์ใช้ความรู้ทางวิทยาศาสตร์และเทคโนโลยีมาพัฒนาคุณภาพชีวิต การพัฒนาตนเองตามวิถีเกษตร ความปลอดภัยและการตรวจสอบคุณภาพ ผลิตภัณฑ์ที่ใช้อุปโภคและบริโภค เพื่อพัฒนาคุณภาพชีวิตอย่างยั่งยืน', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32714', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32715, '1409902', 'เทคโนโลยีและนวัตกรรมเพื่อท้องถิ่น', 'Technology and Innovation for Local Community', '3 (2-2-5)', 3, 'พื้นฐานเทคโนโลยีทางด้านช่าง การบำรุงรักษาวัสดุอุปกรณ์ การนำไปใช้และการใช้งาน อย่างปลอดภัยในชีวิตประจำวัน กระบวนการพัฒนานวัตกรรมเพื่อท้องถิ่นโดยการใช้วิทยาศาสตร์ เทคโนโลยี และสตาร์ทอัพที่ทันสมัย เพื่อเพิ่มผลผลิตภาคการเกษตรที่มีคุณภาพและปลอดภัย การเลือกใช้พลังงานทดแทนที่เป็นมิตรกับสิ่งแวดล้อม', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32715', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32716, '1409903', 'มลพิษและมหันตภัยโลกร้อน', 'Pollution and Global Warming Disaster', '3 (3-0-6)', 3, 'ความหมาย แหล่งกำเนิด ประเภทของมลพิษสิ่งแวดล้อมที่สำคัญ การควบคุมและแนวทางการจัดการมลพิษ ความหมายของสภาวะโลกร้อน สาเหตุและปัจจัยที่ทำให้เกิดสภาวะโลกร้อน มหันตภัยโลกร้อน การป้องกันและแก้ไขมหันตภัยโลกร้อน', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32716', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32717, '1409904', 'การส่งเสริมสุขภาพ', 'Health Promotion', '3 (2-2-5)', 3, 'ความหมาย ขอบเขตของสุขภาพ สุขภาพส่วนบุคคล สุขภาพส่วนชุมชน อาหารและภาวะโภชนาการ สุขภาพผู้บริโภค ยาและสารเสพติด การปฐมพยาบาล กิจกรรมทางกาย การออกกำลังกายและกีฬา สมรรถภาพทางกายและกิจกรรม นันทนาการ', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32717', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32718, '1409905', 'การเรียนรู้สังคมดิจิทัลด้วยไอซีที', 'Learning in Digital Society with ICT', '3 (2-2-5)', 3, 'เทคโนโลยีสารสนเทศและการสื่อสารสำหรับสังคมดิจิทัล การประยุกต์เทคโนโลยีสารสนเทศและการสื่อสาร การเข้าถึงและการใช้ข้อมูล การสื่อสารข้อมูลและระบบเครือข่าย โปรแกรมประยุกต์และ การบริการบนเครือข่ายอินเทอร์เน็ต ภัยคุกคามและความปลอดภัยในการใช้อินเทอร์เน็ต กฎหมายและจริยธรรมเกี่ยวกับเทคโนโลยีสารสนเทศ แนวโน้มของเทคโนโลยีสารสนเทศและการสื่อสารในอนาคต', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32718', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32719, '1409906', 'ความคิดสร้างสรรค์และการแก้ปัญหาในชีวิตประจำวัน', 'Creative Thinking and Problems Solving in Daily Life', '3 (2-2-5)', 3, 'หลักการและกระบวนการคิดของมนุษย์ ความคิดสร้างสรรค์ ความรู้ทางคณิตศาสตร์และ การวิเคราะห์ข้อมูลทางสถิติเบื้องต้นเพื่อการตัดสินใจ นำมาประยุกต์ใช้ในการแก้ปัญหาในชีวิตประจำวัน', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32719', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (32720, '1409907', 'ชีวิตกับการอนุรักษ์พลังงานอย่างยั่งยืน', 'Life and Sustainable Energy Conservation', '3 (2-2-5)', 3, 'พลังงาน พลังงานทดแทน (พลังงานหมุนเวียน พลังงานทางเลือก) การใช้พลังงานเพื่อให้ก้าวทันสู่โลกในยุคปัจจุบัน เป็นมิตรกับสิ่งแวดล้อม การนำโครงการในพระราชดำริด้านพลังงานมาประยุกต์ใช้ การใช้กฎหมายมาตรฐานพลังงานที่เกี่ยวข้องในการดำเนินชีวิตประจำวัน และสามารถสร้างสื่อ เพื่อถ่ายทอดเผยแพร่สู่ท้องถิ่นและชุมชนอย่างยั่งยืน ในการแสวงหาความรู้อย่างมีส่วนร่วมตลอดชีวิต', 'หมวดวิชาศึกษาทั่วไป', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=32720', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (36022, '7011303', 'การทำเหมืองข้อมูล', 'Data Mining', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (36024, '7012480', 'การประมวลผลข้อมูลขนาดใหญ่', 'Big Data Processing', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38921, '2109901', 'ภาษาอังกฤษเพื่อการสื่อสาร', 'English for Communication', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38922, '2109902', 'การใช้ภาษาไทยกับการสื่อสาร', 'Usage Thai Language with Communication', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38923, '2109903', 'ภาษากับวัฒนธรรมทางภาษาเพื่อการสื่อสาร', 'Languages and Language Culture for Communication', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38924, '2209901', 'ศาสตร์และศิลป์ในการสร้างความสุข', 'Sciences and Arts in Creating Happiness', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38925, '2209902', 'ทักษะชีวิตในศตวรรษที่ 21', '21st Century Life Skills', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38926, '2309901', 'ภูมิสังคมกับการพัฒนาท้องถิ่น', 'Social Geography and Local Development', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38927, '2309902', 'ความเป็นพลเมืองและกฎหมายในชีวิตประจำวัน', 'Citizenship and Law in Daily Life', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38928, '2409901', 'วิทยาศาสตร์และเทคโนโลยีเพื่อคุณภาพชีวิต', 'Science and Technology for Quality of Life', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38929, '2409902', 'ชีวิตในยุคเทคโนโลยีดิจิทัล', 'Life in the Digital and Technology Era', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (38930, '2409903', 'การเรียนรู้กับการแก้ปัญหาแบบบูรณาการ', 'Learning and Integrated Problem Solving', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39105, '7071101', 'พื้นฐานเทคโนโลยีสารสนเทศ', 'Fundamental of Information Technology', '3 (2-2-5)', 3, 'ความรู้ในภาพรวมของเทคโนโลยีสารสนเทศ ประวัติเทคโนโลยีสารสนเทศ องค์ประกอบของระบบเทคโนโลยีสารสนเทศ ความสำคัญของข้อมูลและสารสนเทศ ระบบสารสนเทศ นักเทคโนโลยีสารสนเทศ องค์ประกอบของระบบคอมพิวเตอร์ ซอฟต์แวร์ ฮาร์ดแวร์ เทคโนโลยีคอมพิวเตอร์ การปฏิสัมพันธ์กับผู้ใช้ อินเทอร์เน็ต เวิร์ดไวด์เว็บ โซลเชียลเน็ตเวิร์ค ผลกระทบของเทคโนโลยีสารสนเทศที่เกิดต่อสังคม การประยุกต์เทคโนโลยีสารสนเทศในด้านต่างๆ จริยธรรมและกฎหมายทางเทคโนโลยีสารสนเทศ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39105', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39106, '7071102', 'ความคิดสร้างสรรค์ด้านเทคโนโลยีและนวัตกรรม', 'Creativity Thinking of Innovation and Technology', '3 (2-2-5)', 3, 'การพัฒนาความคิดสร้างสรรค์ประเภทต่าง ๆ ความหมายและลักษณะของความคิด สร้างสรรค์ ทฤษฎีที่เกี่ยวข้องกับความคิดสร้างสรรค์ วิธีการจัดการกับปัญหาหรือสถานการณ์ที่คลุมเครือ ซับซ้อน โดยใช้ความคิดสร้างสรรค์ในการจัดการ ฝึกทักษะการใช้ความคิดสร้างสรรค์กับสถานการณ์ปัญหาหรือการพัฒนาในประเด็นต่างๆ ที่สนใจ ศึกษาแนวความคิด กระบวนการ รูปแบบ และนวัตกรรมของเทคโนโลยีสารสนเทศ กลยุทธ์การพัฒนาการนวัตกรรมเทคโนโลยีสารสนเทศที่เป็นระบบ การบริหารจัดการทรัพยากรให้เกิดมูลค่าเพิ่ม การสร้างตราสินค้าที่สัมพันธ์กับนวัตกรรม การวิจัยตลาด การรักษาเทคโนโลยีสารสนเทศและนวัตกรรมในองค์กรให้เกิดความยั่งยืน การรักษาทรัพย์สินทางปัญญา ฝึกทักษะการออกแบบและการพัฒนาเทคโนโลยีสารสนเทศและนวัตกรรมทางด้านสิ่งประดิษฐ์ กระบวนการ การจัดการ อย่างเป็นระบบ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39106', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39107, '7071103', 'การเป็นพลเมือง', 'Citizenship', '3 (2-2-5)', 3, 'ความหมายของสังคม โครงสร้างสังคมไทย ปัญหาของสังคมไทย การสร้างสำนึกทางสังคมและหน้าที่ความรับผิดชอบของการเป็นสมาชิกที่ดีของสังคมในฐานะพลเมืองโลก การปลูกฝังมโนสำนึกทางจริยธรรม หลักธรรมาภิบาล การบูรณาการพุทธจริยธรรมกับสังคม แนวทางการป้องกันและแก้ไขปัญหาทุจริต', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39107', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39108, '7071104', 'กฏหมายแลพจริยธรรมทางการจัดการนวัตกรรมดิจิทัล', 'Law and Ethics in Digital Innovation Management', '3 (2-2-5)', 3, 'ศึกษากฎหมายของประเทศไทยที่เกี่ยวข้องกับสารสนเทศและเทคโนโลยีสารสนเทศ กฎหมายทางด้านการสื่อสารและโทรคมนาคม กฎหมายทางด้านการควบคุมและส่งเสริมการใช้อินเทอร์เน็ต กฎหมายทางด้านการค้าอิเล็กทรอนิกส์ กฎหมายทางด้านการคุ้มครองทรัพย์สินทางปัญญา และกฏหมายทางด้านการคุ้มครองความเป็นส่วนตัวและปลอดภัยในข้อมูล ความรับผิดชอบของผู้ที่เกี่ยวข้องกับการจัดการสารสนเทศและเทคโนโลยีสารสนเทศ อาชญากรรมทางคอมพิวเตอร์ ปัญหาเกี่ยวกับจริยธรรมที่เกี่ยวข้องกับเทคโนโลยีสารสนเทศ การละเมิดลิขสิทธิ์ซอฟต์แวร์', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39108', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39186, '7071101', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:31+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39187, '7071102', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:35+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39188, '7071103', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:38+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39189, '7071104', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:41+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39204, '7072201', 'ระบบสารสนเทศและการจัดการความรู้', 'Information and Knowledge Management', '3 (2-2-5)', 3, 'หลักการ ความหมาย วิวัฒนาการ และบทบาทของระบบสารสนเทศในองค์การ ประเภทของระบบสารสนเทศที่ใช้ในธุรกิจ การกำหนดนโยบาย การวางแผน การวิเคราะห์ และการควบคุม การประยุกต์ใช้ระบบสารสนเทศธุรกิจและระบบสารสนเทศเชิงกลยุทธ์การประเมินความคุ้มค่าของระบบสารสนเทศ กรณีศึกษาเกี่ยวกับระบบสารสนเทศทางธุรกิจและระบบสารสนเทศเชิงกลยุทธ์ แนวคิดทั่วไปเกี่ยวกับความรู้ประเภทของความรู้กระบวนการจัดการความรู้ การวิเคราะห์การออกแบบและพัฒนาระบบจัดการความรู้ การสร้างองค์การแห่งการเรียนรู้ การประยุกต์ใช้หรือกรณีศึกษาเกี่ยวกับการจัดการความรู้', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39204', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39214, '7072402', 'สื่อสังคมเครือข่ายออนไลน์', 'Networking Social Media', '3 (2-2-5)', 3, 'ความหมายและประเภทของเครือข่าย สังคมออนไลน์ (Social Network) วิวัฒนาการของสังคมออนไลน์ การสร้างและวิธีการใช้งาน เครื่องมือ และเทคนิคในแง่มุมต่าง ๆ แนวปฏิบัติในการใช้สื่อสังคมออนไลน์ การสืบค้นข้อมูล การสื่อสารและการแลกเปลี่ยนเรียนรู้กับผู้อื่น การแก้ปัญหา เพื่อให้เกิดความรู้ความเข้าใจ เครือข่ายสังคมออนไลน์ การเลือกใช้เทคโนโลยีในทางสร้างสรรค์ต่อชีวิต สังคม สิ่งแวดล้อม เพื่อพัฒนาอาชีพมีทักษะการค้นหาข้อมูล และการติดต่อสื่อสารผ่านเครือข่ายคอมพิวเตอร์อย่างมีคุณธรรมและจริยธรรม', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39214', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39221, '7071105', 'ระบบปฏิบัติการและเทคโนโลยีคอมพิวเตอร์', 'Operating Systems and Computer Technology', '3 (2-2-5)', 3, 'โครงสร้างคอมพิวเตอร์และองค์ประกอบระบบคอมพิวเตอร์ ระบบหน่วยความจำ ระบบการนำข้อมูลเข้าและระบบแสดงผล ระบบการเชื่อมต่อ สถาปัตยกรรมของไมโครโปรเซสเซอร์ เทคโนโลยีคอมพิวเตอร์สมัยใหม่ ระบบปฏิบัติการต่าง ๆ การทำงานร่วมกันระหว่างฮาร์ดแวร์และซอฟต์แวร์ ปฏิบัติการการติดตั้ง แก้ไขปัญหา ระบบปฏิบัติการลงบนเครื่องคอมพิวเตอร์ประเภทต่าง ๆ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39221', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39222, '7071106', 'เทคโนโลยีในสำนักงาน', 'Office Technology', '3 (2-2-5)', 3, 'ศึกษาและปฏิบัติเกี่ยวกับรูปแบบสำนักงานสมัยใหม่ การปฏิบัติงานในสำนักงานสมัยใหม่ บทบาทของเทคโนโลยีสารสนเทศในสำนักงาน ปฏิบัติงานการใช้เทคโนโลยีที่เกี่ยวกับงานสำนักงาน การรับ-ส่งข้อมูล การจัดเก็บข้อมูลระบบดิจิตอล การประมวลผลข้อมูล', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39222', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39223, '7071107', 'การเขียนโปรแกรมเบื้องต้น', 'Fundamental Programming', '3 (2-2-5)', 3, 'การพัฒนาขั้นตอนวิธีทั่วไป เทคนิคในการแก้ปัญหา การเขียนผังงาน การเขียนโปรแกรมโดยใช้ภาษาคอมพิวเตอร์ภาษาใดภาษาหนึ่ง ศึกษาชนิดของข้อมูล ค่าคงที่ ตัวแปร นิพจน์ คำสั่งรับข้อมูลเข้าและแสดงผลลัพธ์ คำสั่งในการกำหนดค่า คำสั่งควบคุม การประมวลผลข้อความ แถวลำดับ โปรแกรมย่อย การเรียงลำดับข้อมูลและการค้นหาข้อมูล การฝึกปฏิบัติการใช้เครื่องมือในการพัฒนาโปรแกรม การเขียนโปรแกรมเบื้องต้นใน ภาษาใดภาษาหนึ่ง การตรวจสอบ ทดสอบและแก้ไขโปรแกรม', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39223', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39224, '7071201', 'ระบบฐานข้อมูลเบื้องต้น', 'Fundamental Database Systems', '3 (2-2-5)', 3, 'ความรู้เบื้องต้นเกี่ยวกับระบบฐานข้อมูล สถาปัตยกรรมของระบบฐานข้อมูล ฐานข้อมูลเชิงสัมพันธ์ โมเดลจำลองความสัมพันธ์ระหว่างข้อมูล รูปแบบที่เป็นบรรทัดฐาน การออกแบบฐานข้อมูลเชิงสัมพันธ์ การประยุกต์ใช้ฐานข้อมูล กระบวนการสอบถามข้อมูล โครงสร้างการจัดเก็บข้อมูลเชิงกายภาพ การคงสภาพของข้อมูล การฟื้นสภาพและการควบคุมภาวะความพร้อมกัน ความปลอดภัยของฐานข้อมูล คำสั่งภาษาเอสคิวแอล ระบบฐานข้อมูลแบบกระจาย', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39224', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39225, '7071202', 'ระบบเครือข่ายคอมพิวเตอร์เบื้องต้น', 'Fundamental Computer Network Systems', '3 (2-2-5)', 3, 'เครือข่ายการสื่อสารข้อมูลและมาตรฐานระบบเปิด สื่อนำสัญญาณ การส่งข้อมูลในชั้นกายภาพ การควบคุมในระดับเชื่อมโยงข้อมูล เทคโนโลยีของเครือข่ายคอมพิวเตอร์บริเวณเฉพาะที่ เครือข่ายบริเวณกว้าง เครือข่ายอินเทอร์เน็ต การทำงานแบบแม่ข่าย-ลูกข่าย สถาปัตยกรรมและโพรโทคอลการสื่อสาร', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39225', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39226, '7071203', 'การออกแบบและพัฒนาระบบงานสารสนเทศ', 'Design and Development of Information Systems', '3 (2-2-5)', 3, 'ทฤษฎีการวิเคราะห์วงจรชีวิตของการพัฒนาระบบสารสนเทศ กระบวนการ กลยุทธ์ในการวิเคราะห์ความต้องการของระบบ เครื่องมือต่าง ๆ ในการออกแบบและวิเคราะห์ระบบ ออกแบบฐานข้อมูล รวมทั้งคอมพิวเตอร์ช่วยด้านวิศวกรรมซอฟต์แวร์ การติดต่อกับผู้ใช้งาน การศึกษาความเป็นไปได้ของโครงการและจรรยาบรรณนักสารสนเทศ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39226', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39227, '7071204', 'การจัดการเทคโนโลยีสารสนเทศด้านการบริการ', 'Management of Information Technology in Services', '3 (2-2-5)', 3, 'แนวคิดใหม่ในการจัดการและการบริการสารสนเทศ กระบวนการและเครื่องมือที่ใช้ในการออกแบบและการพัฒนาเพื่อเพิ่มคุณค่าการจัดการและการบริการ นวัตกรรมการจัดการและการบริการที่เหมาะสมต่อบริบทขององค์กรประเภทต่าง ๆ การประยุกต์นวัตกรรมในกระบวนการดําเนินขององค์กรการส่งเสริมและการประเมินผลการริเริ่มนวัตกรรมในองค์กร ฝึกปฏิบัติการการประยุกต์ใช้เทคโนโลยีสารสนเทศทางด้านการบริการ เช่น โปรแกรมประยุกต์เพื่อการบริการการเดินทาง การท่องเที่ยว เป็นต้น', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39227', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39228, '7071301', 'จิตวิทยาการบริการ', 'Service Psychology', '3 (2-2-5)', 3, 'แนวทางวิเคราะห์พฤติกรรมมนุษย์ในด้านความต้องการ ศึกษาความแตกต่างระหว่างบุคคล มนุษยสัมพันธ์ การเรียนรู้ การปรับตัว แรงจูงใจ พฤติกรรมของผู้ใช้บริการสารสนเทศ ตลอดจนจิตวิทยาในการให้บริการสารสนเทศ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39228', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39229, '7071302', 'การบริหารโครงการทางเทคโนโลยีสารสนเทศ', 'Project Management in Information Technology', '3 (2-2-5)', 3, 'ลักษณะของโครงการเทคโนโลยีสารสนเทศ การกำหนดแนวความคิดและการริเริ่มโครงการเทคโนโลยีสารสนเทศ โครงรูปการวางแผนโครงการ การบริหารโครงการด้านบุคคล การบริหารโครงการ การบริหารความเสี่ยงในโครงการ การติดตามและรายงานโครงการ การบริหารคุณภาพโครงการ การบริหารการเปลี่ยนแปลงในองค์การ และนำโครงการไปสู่การปฎิบัติและการประเมินผล', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39229', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39230, '7071303', 'การจัดการคุณภาพในงานระบบสารสนเทศ', 'Quality Management for Information Systems', '3 (2-2-5)', 3, 'แนวทางการจัดการคุณภาพโดยรวม วงจรพีดีซีเอ วิธีปรับปรุงประสิทธิภาพของระบบสารสนเทศเพื่อสร้างความพึงพอใจแก่ลูกค้ามากที่สุด เพื่อเพิ่มผลผลิตและตอบสนองความต่อการเปลี่ยนแปลงอย่างรวดเร็ว การออกแบบ การติดตาม การปรับปรุงต่อเนื่อง การเปรียบเทียบ วิธีการและเครื่องมือในการแก้ปัญหา', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39230', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39231, '7071401', 'การบริหารความเสี่ยงทางด้านเทคโนโลยีสารสนเทศ', 'Information Technology Risk Management', '3 (2-2-5)', 3, 'หลักการบริหารจัดการความเสี่ยงด้านเทคโนโลยีสารสนเทศ ความหมายและความสำคัญของการจัดการความเสี่ยง ปัจจัยเสี่ยง ประเมินความเสี่ยง บริหารและควบคุมความเสี่ยง หลักการวิเคราะห์ และจัดทำความเสี่ยงอย่างเหมาะสม ตามมาตรฐานกระบวนการบริหารความเสี่ยง การวิเคราะห์และการประเมิน เพื่อวางแผน กำหนดนโยบายความเสี่ยงด้านเทคโนโลยีสารสนเทศ ด้านภายภาพ ทรัพยากรบุคคล โปรแกรมประยุกต์ และการออกรายงาน', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39231', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39232, '7071402', 'โครงงาน 1', 'Project 1', '3 (2-2-5)', 3, 'การศึกษาความรู้ในขอบข่ายที่อยู่ในความสนใจของการวิจัยค้นคว้าใหม่ ๆ ทางด้านการจัดการเทคโนโลยีสารสนเทศในปัจจุบันเพื่อนำมาเขียนเป็นข้อเสนองานวิจัย การค้นคว้าเอกสารและงานวิจัยที่เกี่ยวข้อง และวิธีการดำเนินงานวิจัยโครงงานการจัดการเทคโนโลยีสารสนเทศ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39232', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39233, '7071403', 'โครงงาน 2', 'Project 2', '3 (2-2-5)', 3, 'วิเคราะห์และออกแบบระบบสารสนเทศที่เกี่ยวกับการจัดการเทคโนโลยีสารสนเทศ พัฒนาระบบงาน ผลการดำเนินงาน สรุปผล จัดทำเอกสารรูปเล่มประกอบโครงงาน การนำเสนอผลงานในรูปแบบของงานวิจัยทางด้านการจัดการเทคโนโลยีสารสนเทศ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39233', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39234, '7071404', 'นวัตกรรมทางด้านดิจิทัล', 'Digital Innovation', '3 (2-2-5)', 3, 'ศึกษานวัตกรรมหรือเทคโนโลยีที่มีอยู่ในปัจจุบันและแนวโน้มของเทคโนโลยีในอนาคต การประยุกต์ใช้นวัตกรรมให้เหมาะสมกับองค์กรในภาครัฐและภาคเอกชน รวมถึงการวางแผนการนำเทคโนโลยีต่าง ๆ มาเป็นเครื่องมือเพื่อเพิ่มประสิทธิภาพในการบริหารจัดการ การดำเนินงานทั้งภาครัฐและภาคเอกชน ฝึกปฏิบัติเกี่ยวกับการวางแผน การประยุกต์ใช้นวัตกรรม เทคโนโลยี', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39234', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39235, '7072101', 'ระบบสารสนเทศเพื่อการจัดการ', 'Management Information Systems', '3 (2-2-5)', 3, 'การจัดการระบบสารสนเทศ การทำธุรกรรมทางอิเล็กทรอนิกส์ การจัดการห่วงโซ่อุปทาน การจัดการลูกค้าสัมพันธ์ การวางแผนทรัพยากรองค์กร การจัดการฐานข้อมูล ผลกระทบและแนวโน้มของเทคโนโลยีในองค์กร จริยธรรมและความมั่นคงปลอดภัยในการทำธุรกรรมทางอิเล็กทรอนิกส์ ฝึกปฏิบัติการการวางแผน การจัดการระบบสารสนเทศในองค์กร', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39235', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39236, '7072102', 'ระบบธุรกิจในยุคดิจิทัล', 'Business System in the Digital Age', '3 (2-2-5)', 3, 'แนวคิด นวัตกรรมของอุตสาหกรรมรวมถึงโอกาสทางธุรกิจใหม่ ๆ องค์ประกอบของระบบธุรกิจในยุคดิจิทัลในมุมมองต่าง ๆ อาทิ โครงสร้างพื้นฐานด้านฮาร์ดแวร์ โครงสร้างพื้นฐานด้านซอฟต์แวร์โครงสร้างพื้นฐานด้านบริการ การส่งเสริมเศรษฐกิจดิจิทัล สังคมยุคดิจิทัล ทักษะในอนาคต ฐานความรู้เครื่องมือสำคัญ การปฏิรูปและการเปลี่ยนถ่ายสู่ยุคดิจิทัล โดยมุมมองการพัฒนาเพื่อความยั่งยืนทางธุรกิจ ปฏิบัติการโดยการฝึกทำธุรกิจบนสื่อออนไลน์ เช่น สื่อสังคมออนไลน์ โปรแกรมประยุกต์ทางด้านการค้าขายออนไลน์ที่ เป็นต้น', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39236', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39237, '7072202', 'เศรษฐศาสตร์ดิจิทัล', 'Digital Economy', '3 (2-2-5)', 3, 'ศึกษาเศรษฐศาสตร์ในอุตสาหกรรมดิจิทัล ที่เกี่ยวกับโครงสร้างตลาด อุปสงค์และอุปทาน วัฏจักรธุรกิจ การลงทุนและกลยุทธ์การลงทุน การศึกษาผลกระทบ การประมาณต้นทุนต่อความเสี่ยงและความไม่แน่นอน มุมมองด้านการจัดการ ประสิทธิภาพ การเปลี่ยนแปลงทางเทคโนโลยีและนโยบาย โดยเน้นเชิงปริมาณและการพยากรณ์ ปฏิบัติการโดยการศึกษาองค์กรระดับชาติหรือในท้องถิ่นในประเด็นทางด้านเศรษฐศาสตร์ นโยบายที่เกี่ยวข้องกับทางด้านเศรษศาสตร์ และอื่นๆ ที่เกี่ยวข้อง เป็นต้น', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39237', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39238, '7072203', 'การตลาดเชิงสร้างสรรค์ในยุคดิจิทัล', 'Creative Marketing in the Digital Age', '3 (2-2-5)', 3, 'แนวคิดและความสำคัญของการตลาดดิจิทัล สภาพแวดล้อมสำหรับตลาดดิจิทัล การกำหนดส่วนแบ่งตลาด ปฏิบัติการทางการตลาดดิจิทัล เช่น การเลือกตลาดเป้าหมายและกำหนดตำแหน่งสำหรับตลาดดิจิทัล การวิเคราะห์ลูกค้า การสร้างสาระหลักและการมีส่วนร่วมเพื่อการสื่อสารผ่านสื่อดิจิทัล การจัดการชื่อเสียงในสังคมเครือข่ายเพื่อสร้างความยั่งยืนของตราสินค้า', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39238', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39239, '7072204', 'เทคโนโลยีสมองกลฝังตัว', 'Embedded Technology', '3 (2-2-5)', 3, 'การออกแบบระบบสมองกลฝังตัวโดยใช้ไมโครคอนโทรลเลอร์ และอุปกรณ์เชื่อมต่อที่มีมาตรฐานการประเมินและเลือกอุปกรณ์ที่เหมาะสมต่อการนำไปใช้งานและคุ้มค่าต่อการลงทุน เพื่อให้ทำงานได้บนระบบสมองกลฝังตัวตามที่ออกแบบ ศึกษาหลักการและวิธีการในการออกแบบซอฟต์แวร์บนระบบสมองกลฝังตัวและการเชื่อมต่อกับอุปกรณ์ภายนอกและตัวอย่างการใช้งานต่าง ๆ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39239', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39240, '7072205', 'การประยุกต์ใช้เทคโนโลยีก้อนเมฆ', 'Cloud Technology Applications', '3 (2-2-5)', 3, 'หลักการ ความหมาย ความรู้เบื้องต้นของเทคโนโลยีคลาวด์ สถาปัตยกรรมคลาวด์ คุณลักษณะการให้บริการผู้ใช้หลายคนพร้อมกัน หลักการพัฒนาแอปพลิเคชันสำหรับองค์กรในคลาวด์ ความต้องการหรือความสามารถในการเลือกรูปแบบเทคโนโลยีก้อนเมฆเพื่อการประยุกต์ใช้ที่เหมาะสมกับงานต่าง ๆ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39240', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39241, '7072301', 'ระบบสารสนเทศอัตโนมัติในงานอุตสาหกรรม', 'Automated Information Systems in Industry', '3 (2-2-5)', 3, 'โครงสร้างและการจัดการระบบสารสนเทศทางอุตสาหกรรม เครื่องมือและโปรแกรมใน การพัฒนาระบบสารสนเทศ การวิเคราะห์ข้อมูลขนาดใหญ่ในระบบการผลิต ระบบความปลอดภัย และ การบำรุงรักษาระบบสารสนเทศ ภาพรวมของระบบอัตโนมัติ เทคโนโลยีการควบคุมอัตโนมัติทางอุตสาหกรรม เทคโนโลยีปัญญาประดิษฐ์ เทคโนโลยีความจริงเสมือน ความรู้เบื้องต้นการประยุกต์ใช้งาน การประยุกต์ใช้ไมโครคอมพิวเตอร์ในการควบคุมกระบวนการผลิตตัวควบคุมแบบโปรแกรมได้และการเขียนโปรแกรมควบคุมพื้นฐานและการประยุกต์ใช้หุ่นยนต์อุตสาหกรรม', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39241', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39242, '7072302', 'การจัดการเทคโนโลยีสารสนเทศด้านการศึกษา', 'Management of Information Technology in Education', '3 (2-2-5)', 3, 'หลักการ แนวคิด การออกแบบ การสร้าง การประยุกต์ใช้ การประเมิน และการปรับปรุงสื่อ นวัตกรรมและเทคโนโลยีสารสนเทศ หาข้อมูลจากแหล่งความรู้และฐานข้อมูลความรู้ วิเคราะห์ปัญหาที่เกิดจากการใช้สื่อนวัตกรรมและเทคโนโลยีสารสนเทศ ฝึกปฏิบัติการออกแบบ ผลิต พัฒนา ประยุกต์ใช้และประเมินสื่อ นวัตกรรมและเทคโนโลยีสารสนเทศเพื่อพัฒนาคุณภาพการเรียนรู้ให้เหมาะสม', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39242', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39243, '7072303', 'การจัดการเทคโนโลยีสารสนเทศด้านการเกษตร', 'Management of Information Technology in Agriculture', '3 (2-2-5)', 3, 'บทบาทและความสำคัญของเทคโนโลยีสารสนเทศและการสื่อสารในระบบเกษตร กรอบงานของเทคโนโลยีสารสนเทศและการสื่อสารในระบบเกษตร โครงข่ายทางการเกษตร การควบคุมและการสื่อสารทางไกลโครงข่ายคอมพิวเตอร์ฐานข้อมูลทางการเกษตร ฝึกปฏิบัติการต่าง ๆ เช่น การตรวจวัดสิ่งต่าง ๆ ทางการเกษตร การควบคุมอุปกรณ์ทางการเกษตรจากระยะไกล', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39243', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39244, '7072304', 'การจัดการเทคโนโลยีสารสนเทศด้านพาณิชย์', 'Management of Information Technology in Commercial', '3 (2-2-5)', 3, 'ความรู้พื้นฐานเกี่ยวกับธุรกิจสารสนเทศ บทบาทของธุรกิจสารสนเทศ ลักษณะและประเภท บทบาทของผู้ให้บริการ การนำโปรแกรมคอมพิวเตอร์ ไปใช้ในการวิเคราะห์ธุรกิจ โดยเน้นข้อมูลที่ใช้ในการทำการตลาด เช่น ราคาผลิตภัณฑ์การสำรวจความต้องการของลูกค้า การแบ่งกลุ่มตลาด การทำนายยอดขายผลิตภัณฑ์ การค้าปลีก การโฆษณาสินค้า ปฏิบัติการการจัดการเทคโนโลยีสารสนเทศเพื่อนำมาในการทำธุรกิจและการพาณิชย์', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39244', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39245, '7072305', 'การจัดการเทคโนโลยีสารสนเทศด้านการเงิน', 'Management of Information Technology in Financial', '3 (2-2-5)', 3, 'หลักการและเครื่องมือทางการเงิน การวางแผนและควบคุมทางการเงินของธุรกิจ การบริหารสินทรัพย์หมุนเวียน งบลงทุน การจัดหาเงินทุนจากแหล่งเงินทุนระยะสั้น ปานกลาง และระยะยาว การจัดโครงสร้างเงินทุน ต้นทุนของเงินทุน ค่าของเงินตามเวลา และนโยบายเงินปันผล การควบคุมกิจการและการแยกกิจการ ฝึกปฏิบัติการการประยุกต์ใช้เทคโนโลยีสารสนเทศทางการเงิน เช่น การใช้โปรแกรมประยุกต์ทางธนาคาร การใช้โปรแกรมประยุกต์เพื่อการวางแผนและควบคุมทางการเงิน เป็นต้น', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39245', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39246, '7072306', 'การตลาดบนอุปกรณ์เคลื่อนที่', 'Mobile Marketing', '3 (2-2-5)', 3, 'หลักการและแนวคิดของการตลาดบนอุปกรณ์เคลื่อนที่ การโฆษณาบนอุปกรณ์เคลื่อนที่ การส่งเสริมการขายบนอุปกรณ์เคลื่อนที่ การเพิ่มประสิทธิภาพของเครื่องมือค้นหาบนอุปกรณ์เคลื่อนที่ พาณิชย์อิเล็กทรอนิกส์บนอุปกรณ์เคลื่อนที่ ปัจจัยแห่งความสำเร็จของการตลาดบนอุปกรณ์เคลื่อนที่ เทคโนโลยีสำหรับการตลาดบนอุปกรณ์เคลื่อนที่ การบริหารลูกค้าสัมพันธ์บนอุปกรณ์เคลื่อนที่ ฝึกปฏิบัติโดยการทำการตลาดบนอุปกรณ์เคลื่อนที่ เพื่อส่งเสริมการขาย', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39246', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39247, '7072307', 'การออกแบบและพัฒนาเว็บเพื่องานธุรกิจยุคใหม่', 'Web Design and Development for New Business', '3 (2-2-5)', 3, 'ทฤษฎีองค์ประกอบของธุรกิจยุคใหม่ สถาปัตยกรรมของการสื่อสารข้อมูลระหว่างเว็บเซิร์ฟเวอร์และเว็บเบราเซอร์ เทคโนโลยีฮาร์ดแวร์และซอฟต์แวร์ที่เหมาะสมในปัจจุบัน การให้บริการของเว็บเซิร์ฟเวอร์ในปัจจุบัน ปฏิบัติการการติดตั้งระบบเว็บเซิร์ฟเวอร์และฐานข้อมูลบนเว็บโดยประยุกต์ใช้ซอฟท์แวร์ที่ให้บริการในปัจจุบัน การออกแบบโครงสร้างเว็บไซต์ การออกแบบหน้าเว็บให้รองรับ การแสดงผลที่หลากหลายอุปกรณ์เพื่อการพัฒนาและออกแบบเว็บไซต์ในงานธุรกิจ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39247', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39248, '7072308', 'การประยุกต์ใช้โปรแกรมคอมพิวเตอร์แบบเปิด', 'Application of Open Source Computer Programs', '3 (2-2-5)', 3, 'บทบาท ความสําคัญ ประเภท มาตรฐานและกฎหมายที่เกี่ยวข้องกับโปรแกรมคอมพิวเตอร์แบบเปิด การประเมินและการเลือกใช้โปรแกรมคอมพิวเตอร์แบบเปิด การนําโปรแกรมคอมพิวเตอร์แบบเปิดไปใช้ในการดําเนินงานขององค์กรและการพัฒนาต่อเนื่อง', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39248', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39249, '7072309', 'การบริหารจัดการระบบเครือข่ายคอมพิวเตอร์', 'Computer Network Management System', '3 (2-2-5)', 3, 'หลักการการจัดการเครือข่ายและโครงสร้างพื้นฐานระบบเครือข่าย การจัดการเครือข่ายด้านต่าง ๆ ได้แก่ การจัดการด้านการปรับตั้งค่าด้านความผิดพลาด ด้านประสิทธิภาพด้านบัญชีและด้านความมั่นคงปลอดภัย ผลิตภัณฑ์การจัดการเครือข่ายการจัดการโครงสร้างพื้นฐานระบบปฏิบัติการระบบเครือข่ายและสภาพแวดล้อมทางกายภาพรวมทั้งการพิจารณาด้านความมั่นคงปลอดภัยระบบสำหรับให้บริการในโครงสร้างพื้นฐาน โดยมีการฝึกปฏิบัติการด้านการจัดการเครือข่าย', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39249', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39250, '7072310', 'เมืองอัจฉริยะ', 'Smart City', '3 (2-2-5)', 3, 'ศึกษาการพัฒนา เมืองอัจฉริยะ และการใช้เทคโนโลยีอัจฉริยะที่เกิดขึ้นใหม่เชื่อมโยงกับแนวคิดของข้อมูลขนาดใหญ่และการเปลี่ยนแปลงของสภาพแวดล้อมในเมือง กลยุทธ์นวัตกรรมและกระบวนการนวัตกรรมเทคโนโลยี การจัดหาเงินทุนของเทคโนโลยีใหม่ กระบวนการเชิงพาณิชย์ของเทคโนโลยี', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39250', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39251, '7072311', 'การตรวจสอบและความมั่นคงของสารสนเทศดิจิทัล', 'Auditing and Digital Information Security', '3 (2-2-5)', 3, 'แนวคิดพื้นฐานด้านความปลอดภัยของข้อมูล เทคนิคและวิธีการในการรักษาความปลอดภัยของข้อมูล การจัดการความเสี่ยง มาตรฐานทางด้านความมั่นคงและความปลอดภัยของระบบ นโยบายการรักษาความเป็นส่วนตัวและความปลอดภัยของข้อมูล การควบคุมการเข้าถึงข้อมูล ประเด็นทางด้านกฎหมายและจริยธรรมที่เกี่ยวข้องกับความเป็นส่วนตัวและความปลอดภัยของข้อมูลที่เกี่ยวกับเศรษฐกิจในยุคปัจจุบัน ฝึกปฏิบัติโดยการวิเคราะห์ภัยคุกคาม ความเสี่ยง การป้องกันความปลอดภัยของข้อมูล โปรแกรมการป้องกันต่าง ๆ เป็นต้น', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39251', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39252, '7072312', 'สารสนเทศเพื่อการจัดการโลจิสติกส์', 'Information for Logistics Management', '3 (2-2-5)', 3, 'ศึกษาค้นคว้าในหัวข้อเกี่ยวกับทฤษฎีและการประยุกต์ใช้คอมพิวเตอร์ในการจัดการกิจกรรม ทั้งหมด ตั้งแต่ขั้นตอนจัดหาวัตถุดิบจนถึงการส่งมอบผลิตภัณฑ์ให้ลูกค้า การจัดการความสัมพันธ์ของลูกค้าการปรับปรุงกระบวนการธุรกิจเพื่อการจัดการคุณภาพ ฝึกปฏิบัติการการประยุกต์ใช้เทคโนโลยีสารสนเทศทางด้านการโลจิสติกส์ เช่น โปรแกรมประยุกต์ในการติดตามการส่งสินค้า เป็นต้น', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39252', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39253, '7072313', 'การออกแบบสื่อดิจิทัล', 'Digital Media Design', '3 (2-2-5)', 3, 'องค์ประกอบพื้นฐานของการจัดสร้างมัลติมีเดีย ความรู้เบื้องต้นในการผลิตสื่อภาพ เสียง และแอนิเมชัน การประสานสื่อเข้ากันด้วยเครื่องมือที่เหมาะสม ฝึกปฏิบัติการการสร้างมัลติมีเดียบนคอมพิวเตอร์ การนำข้อมูลหรือความรู้มาสรุปเป็นสารสนเทศ ในลักษณะของกราฟิกที่ออกแบบเป็นภาพนิ่งหรือภาพเคลื่อนไหว และแนวคิดเกี่ยวกับมัลติมีเดีย เพื่อนำมาสนับสนุนการทำธุรกิจ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39253', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39254, '7072314', 'การวิเคราะห์ข้อมูลขนาดใหญ่', 'Big Data Analytics', '3 (2-2-5)', 3, 'ความหมาย องค์ประกอบและคุณลักษณะของข้อมูลใหญ่ ประเภทของข้อมูล การจัดการข้อมูลขนาดใหญ่ เครื่องมือต่าง ๆ ที่ใช้ในการจัดเก็บข้อมูล การวิเคราะห์ข้อมูล การประยุกต์ใช้สถิติและซอฟต์แวร์เครื่องมือเพื่อการวิเคราะห์ข้อมูล และการนำเสนอข้อมูลขนาดใหญ่ การฝึกปฏิบัติการจัดการข้อมูลขนาดใหญ่ด้วยซอฟต์แวร์เครื่องมือ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39254', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39255, '7072315', 'ระบบธุรกิจอัจฉริยะ', 'Business Intelligence', '3 (2-2-5)', 3, 'ความหมายและแนวคิดเกี่ยวกับธุรกิจอัจฉริยะ ประเภทและกระบวนธุรกิจอัจฉริยะ ลักษณะสารสนเทศสำหรับธุรกิจอัจฉริยะ แบบจำลองการจัดการและแบบจำลองการวิเคราะห์ข้อมูลจำนวนมากที่มาจากแหล่งข้อมูลหลายแหล่งที่มีทั้งรูปแบบ โครงสร้างข้อมูลที่มีความแตกต่างกัน เพื่อให้เป็นสารสนเทศในรูปแบบที่ผู้ใช้ต้องการประยุกต์ใช้ข้อมูลเพื่อเป็นแนวทางการประกอบธุรกิจ ฝึกปฏิบัติโดย การเลือกใช้เครื่องมือและการวิเคราะห์ข้อมูล การประยุกต์ใช้ข้อมูลในเชิงธุรกิจและกรณีศึกษา', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39255', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39256, '7072316', 'เทคโนโลยีอินเทอร์เน็ตสรรพสิ่ง', 'Internet of Things', '3 (2-2-5)', 3, 'ความรู้พื้นฐานเกี่ยวกับเทคโนโลยีสมองกลฝังตัวและอินเทอร์เน็ตของสรรพสิ่ง อุปกรณ์อิเล็กทรอนิกส์ระบบสมองกลฝังตัว การเขียนโปรแกรมควบคุมการทำงานของอุปกรณ์อิเล็กทรอนิกส์รวมถึงการเชื่อมโยงอุปกรณ์กับอินเทอร์เน็ตของสรรพสิ่งในระบบสมองกลฝังตัว การประยุกต์ใช้เทคโนโลยีสมองกลฝังตัวและอินเทอร์เน็ตของสรรพสิ่งและกรณีศึกษา', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39256', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39257, '7072317', 'การจัดการเทคโนโลยีปัญญาประดิษฐ์เพื่องานธุรกิจ', 'Management of Artificial Intelligence Technology for Business', '3 (2-2-5)', 3, 'แนวคิดเกี่ยวกับปัญญาประดิษฐ์ เทคนิคการค้นหาแบบต่าง ๆ การใช้คอมพิวเตอร์แก้ปัญหา ภาษาธรรมชาติ การตอบคำถามและตัวประสาน การรับรู้ทางภาพและการเรียนรู้ รูปแบบการจำได้ กระบวนการเรียนรู้โดยการสืบค้น ระบบผู้เชี่ยวชาญ และปฏิบัติการนำมาประยุกต์ใช้งานธุรกิจแบบต่าง ๆ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39257', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39258, '7072401', 'สัมมนาด้านการจัดการเทคโนโลยีสารสนเทศ', 'Information Technology Management Seminar', '3 (2-2-5)', 3, 'การศึกษาค้นคว้าปัญหาหรือหัวข้อที่สนใจทางด้านการจัดการเทคโนโลยีสารสนเทศทั้งในประเทศและต่างประเทศ เป็นรายบุคคล หรือเป็นกลุ่ม รวบรวม เรียบเรียงและสรุปข้อคิดเห็นเพื่อนำเสนอต่อที่ประชุมกลุ่มสัมมนา หลักการด้านการสัมมนา รูปแบบการจัดสัมมนา ฝึกปฏิบัติการวิธีการจัดสัมมนา การทำโครงการและการดำเนินโครงการด้านการจัดสัมมนา รวมถึงการสรุปผลและการรายงานผลการจัดโครงการสัมมนา', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39258', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39259, '7072404', 'ผู้ประกอบการทางด้านดิจิทัล', 'Digital Entrepreneur', '3 (2-2-5)', 3, 'กระบวนการในการนำนวัตกรรมสู่การปฏิบัติและการใช้เชิงพาณิชย์ เทคนิคและเครื่องมือในการถ่ายทอดนวัตกรรม กลยุทธ์การบริหารจัดการนวัตกรรมและเทคโนโลยีอย่างเป็นระบบ เพื่อสร้างนวัตกรรมและเทคโนโลยีเพื่อความได้เปรียบเชิงการแข่งขัน ผลกระทบของนวัตกรรมและเทคโนโลยีที่มีต่อเศรษฐกิจและสังคม คุณลักษณะและทักษะที่จำเป็นสำหรับผู้ประกอบการในยุคเศรษฐกิจดิจิทัล การแสวงหาโอกาสทางธุรกิจ จริยธรรมของการเป็นผู้ประกอบการ ปัญหาและอุปสรรคของการทำธุรกิจดิจิทัล ปฏิบัติการประยุกต์ใช้เทคโนโลยีสมัยใหม่กับการประกอบธุรกิจในยุคดิจิทัล การใช้นวัตกรรมเพื่อการบริการ การใช้ระบบจัดการข้อมูลสำหรับการประกอบธุรกิจ การวางแผนกลยุทธ์ทางธุรกิจ', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39259', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39260, '7072405', 'การศึกษาเฉพาะทาง', 'Selected Topics', '3 (2-2-5)', 3, 'ศึกษาในหัวข้อที่แตกต่างจากวิชาที่เปิดสอนตามปกติ เพื่อให้ทันต่อการเปลี่ยนแปลงของเทคโนโลยีสารสนเทศในขณะนั้น ซึ่งจะกำหนดรายละเอียดวิชาขึ้นตามความเหมาะสม', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39260', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39261, '7073401', 'ฝึกประสบการณ์การจัดการนวัตกรรมดิจิทัล', 'Experience in Digital Innovation Management', '12 (0-0-640)', 12, 'ฝึกงานตามความต้องการของสถานประกอบการเพื่อมีความพร้อมในการทำงานสำหรับพนักงานใหม่ โดยสถานประกอบการต้องกำหนดแผนงาน ภาระงานทั้งงานประจำ (work-based learning) หรืองานโครงงาน (project based learning) หรืองานที่ได้รับมอบหมาย โดยได้รับความเห็นชอบจากสาขาวิชา จัดพี่เลี้ยงกับกับ ติดตาม ดูแลและประเมินผลการปฏิบัติงานของนักศึกษา', 'เทคโนโลยีสารสนเทศ', 'https://regis.rmu.ac.th/registrar/class_info_5.asp?courseid=39261', '2026-08-17T05:50:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39858, '7000101', 'เทคโนโลยีดิจิทัลเพื่อการพัฒนาเศรษฐกิจและสังคม', 'Digital Technology For Economic And Social Development', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39859, '7000102', 'วิศวกรสังคมเพื่อการพัฒนานวัตกรรมชุมชน', 'Social Engineer for Community Innovation Development', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39860, '7011101', 'การเขียนโปรแกรมเบื้องต้น', 'Fundamentals Programming', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (39881, '7071102', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:34+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40148, '7000103', 'ผู้ประกอบการชุมชนในยุคดิจิทัล', 'Community Entrepreneurs In The Digital Age', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40149, '7000104', 'ภาษาอังกฤษในยุคดิจิทัล', 'English for Digital', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40154, '7071103', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:38+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40155, '7071104', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:41+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40156, '7071105', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:45+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40301, '7011103', 'การซ่อมบำรุงรักษาระบบคอมพิวเตอร์', 'Computer System Maintenance', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40302, '7011105', 'มิติทางสังคมและจริยธรรมสำหรับนักเทคโนโลยีสารสนเทศ', 'Social Issues and Ethics for IT Professional', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40401, '7011104', 'การเขียนโปรแกรมเชิงวัตถุ', 'Object Oriented Programming', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (40710, '7011306', 'ผู้ประกอบการเทคโนโลยีสารสนเทศ', 'Information Technology Entrepreneurship', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41047, '7011106', 'ปฏิบัติการเครือข่ายในสำนักงาน', 'Office Networking workshop', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41048, '7011201', 'การพัฒนาโปรแกรมประยุกต์สำหรับอุปกรณ์เคลื่อนที่เบื้องต้น', 'Fundamentals Application Development for Mobile Devices', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41049, '7011203', 'ระบบฐานข้อมูลเบื้องต้น', 'Fundamental Database Systems', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41050, '7011305', 'การพัฒนาโปรแกรมประยุกต์สำหรับอุปกรณ์เคลื่อนที่ขั้นสูง', 'Application Development for Mobile Devices', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41051, '7011401', 'โครงงานเทคโนโลยีสารสนเทศ 1', 'Information Technology Project 1', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41052, '7011402', 'โครงงานเทคโนโลยีสารสนเทศ 2', 'Information Technology Project 2', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41053, '7013403', 'การเตรียมความพร้อมสหกิจศึกษา', 'Preparation for Co-operative Education Internship', '2 (0-0-90)', 2, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41054, '7013404', 'สหกิจศึกษา', 'Co-operative Education Internship', '6 (0-0-640)', 6, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41055, '7012461', 'การบริหารโครงสร้างพื้นฐานเทคโนโลยีสารสนเทศ', 'Information Technology Infrastructure Management', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41056, '7012478', 'เครือข่ายคอมพิวเตอร์', 'Computer Network', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41057, '7012479', 'เทคโนโลยีแพลตฟอร์มคอมพิวเตอร์', 'Computing Platform Technology', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41058, '7012482', 'ปฏิบัติการการโปรแกรมภาษาจาวา', 'Java Programming Workshop', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41181, '7071203', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:44:02+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41202, '7071202', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:43:57+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41203, '7071204', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:44:05+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41204, '7071301', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:44:08+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41205, '7071302', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:44:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41206, '7071303', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:44:15+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41209, '7071402', NULL, NULL, '3 (1-6-5)', 3, NULL, NULL, NULL, '2026-08-17T05:44:21+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41210, '7071403', NULL, NULL, '3 (1-6-5)', 3, NULL, NULL, NULL, '2026-08-17T05:44:25+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41211, '7073401', NULL, NULL, '6 (0-0-640)', 6, NULL, NULL, NULL, '2026-08-17T05:46:06+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41216, '7072304', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:45:03+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41218, '7072306', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:45:11+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41222, '7072309', NULL, NULL, '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:45:20+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41461, '7011302', 'สัมมนาเทคโนโลยีสารสนเทศ', 'Information Technology Seminar', '2 (1-2-3)', 2, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO courses (course_id, course_code, name_th, name_en, credits_text, credits, description_th, faculty_text, source_url, scraped_at)
VALUES (41462, '7012469', 'การประกันและความมั่นคงสารสนเทศ', 'Information Assurance and Security', '3 (2-2-5)', 3, NULL, NULL, NULL, '2026-08-17T05:30:07+00:00')
ON CONFLICT (course_id) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    credits_text = EXCLUDED.credits_text,
    credits = EXCLUDED.credits,
    description_th = EXCLUDED.description_th,
    faculty_text = EXCLUDED.faculty_text,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;

-- ── program_courses (125 แถว) ───────────────────────────────────────────
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 1, 38922, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 1, 38923, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 1, 38921, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 5, 38924, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 5, 38925, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 8, 38926, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 8, 38927, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 11, 38929, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 11, 38928, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 11, 38930, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 16, 40148, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 16, 39859, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 16, 39858, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 16, 40149, 4)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 27937, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 28341, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 39860, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 27939, 4)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41047, 5)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 28343, 6)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 36022, 7)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 40710, 8)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41461, 9)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 28352, 10)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 40302, 11)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 40401, 12)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41048, 13)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41051, 14)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41054, 15)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 27938, 16)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 28342, 17)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41049, 18)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41050, 19)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41052, 20)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 41053, 21)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 22, 40301, 22)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 41057, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 41058, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28361, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28367, 4)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 27940, 5)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28359, 6)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 41055, 7)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 41056, 8)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28366, 9)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 31665, 10)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28362, 11)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28364, 12)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28369, 13)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 41462, 14)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 27936, 15)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28358, 16)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28365, 17)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28368, 18)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 36024, 19)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28360, 20)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (60188, 45, 28370, 21)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 2, 32701, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 2, 32702, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 5, 32703, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 5, 32704, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 5, 32706, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 5, 32705, 4)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 11, 32708, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 11, 32709, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 11, 32707, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 16, 32710, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 16, 32711, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 16, 32712, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 16, 32713, 4)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 22, 32717, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 22, 32715, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 22, 32714, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 22, 32720, 4)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 22, 32716, 5)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 22, 32719, 6)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 22, 32718, 7)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39226, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39228, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39222, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39105, 4)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39233, 5)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39227, 6)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39224, 7)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39234, 8)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39229, 9)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39106, 10)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39225, 11)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39108, 12)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39230, 13)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39232, 14)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39107, 15)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39223, 16)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39231, 17)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 31, 39221, 18)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39236, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39244, 2)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39246, 3)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39237, 4)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39240, 5)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39255, 6)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39259, 7)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39257, 8)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39238, 9)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39214, 10)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39250, 11)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39249, 12)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39248, 13)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39204, 14)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39256, 15)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39253, 16)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39245, 17)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 22956, 18)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39258, 19)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39252, 20)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39251, 21)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39243, 22)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39235, 23)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39260, 24)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39247, 25)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39242, 26)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39254, 27)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39241, 28)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 50, 39239, 29)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;
INSERT INTO program_courses (program_id, category_row_id, course_id, position)
VALUES (59721, 80, 39261, 1)
ON CONFLICT (program_id, category_row_id, course_id) DO UPDATE SET
    position = EXCLUDED.position;

-- ── offerings (337 แถว) ─────────────────────────────────────────────────
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2568, 1, '1', '110', 'TU08:00-11:20 360305', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2568, 1, '2', '110', 'TU13:00-16:20 360305', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 52, 49, 3, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2568, 1, '3', '110', 'WE08:00-11:20 360305', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 48, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2568, 1, '4', '110', 'WE13:00-16:20 360305', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 34, 16, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '1', '110', 'TU08:00-11:20 350804', 'อาจารย์จำรัส สุขแป', 50, 25, 25, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '10', '110', NULL, NULL, 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '2', '110', 'TU08:00-11:20 350804', 'อาจารย์จำรัส สุขแป', 50, 23, 27, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '3', '110', 'TU08:00-11:20 350804', 'อาจารย์จำรัส สุขแป', 50, 21, 29, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '4', '110', NULL, NULL, 50, 0, 50, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '5', '110', 'TU13:00-16:20 38-IT0503', 'อาจารย์จำรัส สุขแป', 50, 39, 11, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '6', '110', 'TU13:00-16:20 38-IT0503', 'อาจารย์จำรัส สุขแป', 50, 32, 18, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '7', '110', 'TU13:00-16:20 38-IT0503', 'อาจารย์จำรัส สุขแป', 50, 17, 33, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '8', '110', 'TU13:00-16:20 38-IT0503', 'อาจารย์จำรัส สุขแป', 50, 24, 26, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 1, '9', '110', 'SA08:00-11:20 360407', 'อาจารย์นัฐพงษ์ ภูภักดี', 50, 8, 42, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2568, 1, '1', '110', NULL, 'อาจารย์ภิญญดา วิริยะ', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:34+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2568, 1, '2', '110', NULL, NULL, 60, 0, 60, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:34+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 1, '1', '110', 'TU08:00-11:20 260401', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 1, '2', '110', 'TU08:00-11:20 260401', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 1, '3', '110', 'TU08:00-11:20 260401', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 51, 49, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 1, '4', '110', 'TU13:00-16:20 040301', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 1, '5', '110', 'TU13:00-16:20 040303', 'อาจารย์ธีระ ตันบุญต่อ', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 1, '6', '110', 'TU13:00-16:20 040304', 'ดร.ฉัฐพร ศรีประเสริฐ', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 1, '7', '110', NULL, NULL, 0, 0, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 2, '1', '110', 'TU08:00-11:20 38-IT0509', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 42, 8, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 2, '2', '110', 'TU08:00-11:20 38-IT0509', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 30, 20, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 2, '3', '110', 'TU08:00-11:20 38-IT0509', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 17, 33, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 2, '4', '110', 'TU13:00-16:20 38-IT0509', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 45, 5, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 2, '5', '110', 'TU13:00-16:20 38-IT0509', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 11, 39, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 2, '6', '110', 'SU08:00-11:20 150801', 'ผู้ช่วยศาสตราจารย์ ดร.แสงระวี ดอนแก้วบัว', 50, 35, 15, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2567, 2, '7', '110', NULL, 'อาจารย์ภิญญดา วิริยะ', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2568, 2, '1', '110', NULL, 'ผู้ช่วยศาสตราจารย์สุวิชชาน อุ่นอุดม', 12, 9, 3, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32701, '1109901', 2568, 2, '2', NULL, NULL, 'ผู้ช่วยศาสตราจารย์สุวิชชาน อุ่นอุดม', 1, 0, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109901&coursename=', '2026-08-17T05:42:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '1', '110', 'TU13:00-16:20 38-IT0208', 'อาจารย์สุดารัตน์ มาศวรรณา', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '10', '110', 'TU08:00-11:20 37-EN5007', 'อาจารย์จำรัส สุขแป', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '11', '110', 'SA08:00-11:20 360303', 'อาจารย์นัฐพงษ์ ภูภักดี', 50, 9, 41, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '2', '110', 'TU13:00-16:20 38-IT0208', 'อาจารย์สุดารัตน์ มาศวรรณา', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '3', '110', 'TU13:00-16:20 38-IT0208', 'อาจารย์สุดารัตน์ มาศวรรณา', 52, 48, 4, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '4', '110', 'TU08:00-11:20 38-IT0509', 'อาจารย์นัฐพงษ์ ภูภักดี', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '5', '110', 'TU08:00-11:20 38-IT0509', 'อาจารย์นัฐพงษ์ ภูภักดี', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '6', '110', 'TU08:00-11:20 38-IT0509', 'อาจารย์นัฐพงษ์ ภูภักดี', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '7', '110', 'TU13:00-16:20 360306', 'อาจารย์วินัย แสงกล้า', 50, 41, 9, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '8', '110', 'TU13:00-16:20 360305', 'อาจารย์ ดร .สุมาลี พลขุนทรัพย์', 52, 51, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 1, '9', '110', 'TU08:00-11:20 37-EN5007', 'อาจารย์จำรัส สุขแป', 50, 47, 3, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '1', '110', 'TU08:00-11:20 350305', 'อาจารย์จำรัส สุขแป', 50, 31, 19, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '10', '110', 'TU13:00-16:20 360304', 'ผู้ช่วยศาสตราจารย์กฤต โสดาลี', 50, 18, 32, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '11', '110', 'SU08:00-11:20 360304', 'อาจารย์นัฐพงษ์ ภูภักดี', 50, 26, 24, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '2', '110', 'TU08:00-11:20 350305', 'อาจารย์จำรัส สุขแป', 50, 17, 33, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '3', '110', 'TU08:00-11:20 350305', 'อาจารย์จำรัส สุขแป', 50, 4, 46, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '4', '110', 'TU08:00-11:20 350305', 'อาจารย์จำรัส สุขแป', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '5', '110', 'TU13:00-16:20 350305', 'อาจารย์จำรัส สุขแป', 50, 36, 14, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '6', '110', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '7', '110', 'TU13:00-16:20 350305', 'อาจารย์จำรัส สุขแป', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '8', '110', 'TU13:00-16:20 350305', 'อาจารย์จำรัส สุขแป', 50, 10, 40, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '8888', NULL, NULL, NULL, 2, 2, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2567, 2, '9', '110', 'TU13:00-16:20 360304', 'ผู้ช่วยศาสตราจารย์กฤต โสดาลี', 50, 11, 39, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 2, '1', '110', 'TU13:00-16:20 350804', 'อาจารย์จำรัส สุขแป', 50, 22, 28, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:32+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 2, '2', '110', 'TU13:00-16:20 350804', 'อาจารย์จำรัส สุขแป', 50, 11, 39, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:32+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32702, '1109902', 2568, 2, '3', '110', 'SA08:00-11:20 360304', 'อาจารย์นัฐพงษ์ ภูภักดี', 50, 4, 46, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109902&coursename=', '2026-08-17T05:42:32+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2567, 1, '1', '110', 'TU08:00-11:20 360303', 'ดร.ฉัฐพร ศรีประเสริฐ', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:33+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2567, 1, '2', '110', 'TU13:00-16:20 360304', 'อาจารย์เศวตชาติ สิงหเลิศ', 50, 48, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:33+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2567, 1, '3', '110', 'TU13:00-16:20 37-EN5005', 'อาจารย์มนัสนันท์ สมดี', 50, 29, 21, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:33+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2567, 1, '4', '110', NULL, 'อาจารย์มนัสนันท์ สมดี', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:33+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2568, 2, '1', '110', 'TU08:00-11:20 360304', 'อาจารย์ภัทรภร บุญศรี', 51, 51, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:34+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2568, 2, '2', '110', 'TU16:20-19:40 360302', 'อาจารย์ภัทรภร บุญศรี', 50, 4, 46, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:34+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32703, '1109903', 2568, 2, '3', NULL, 'SA08:00-11:20 260304', 'อาจารย์ภัทรภร บุญศรี', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109903&coursename=', '2026-08-17T05:42:34+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 1, '1', '110', 'TU08:00-11:20 360304', 'อาจารย์วินัย แสงกล้า', 50, 37, 13, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 1, '2', '110', 'TU08:00-11:20 360304', 'อาจารย์วินัย แสงกล้า', 50, 22, 28, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 1, '3', '110', 'TU13:00-16:20 360408', 'อาจารย์อัษฎาวุธ ไสยรส', 50, 40, 10, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 1, '4', '110', 'TU13:00-16:20 360408', 'อาจารย์อัษฎาวุธ ไสยรส', 50, 15, 35, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 1, '5', '110', 'TU13:00-16:20 360408', 'อาจารย์อัษฎาวุธ ไสยรส', 50, 12, 38, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 1, '6', '110', 'SA08:00-11:20 360401', 'อาจารย์วินัย แสงกล้า', 18, 11, 7, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 1, '8', '110', 'SU08:00-11:20 360304', 'อาจารย์อัษฎาวุธ ไสยรส', 50, 11, 39, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 2, '1', '110', 'TU08:00-11:20 360304', 'อาจารย์วินัย แสงกล้า', 50, 17, 33, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:36+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 2, '2', '110', 'TU08:00-11:20 360304', 'อาจารย์วินัย แสงกล้า', 50, 12, 38, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:36+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 2, '3', '110', 'TU08:00-11:20 360304', 'อาจารย์วินัย แสงกล้า', 50, 2, 48, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:36+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 2, '4', '110', 'TU13:00-16:20 360305', 'อาจารย์วินัย แสงกล้า', 50, 39, 11, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:36+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 2, '5', '110', 'TU13:00-16:20 360305', 'อาจารย์วินัย แสงกล้า', 50, 3, 47, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:36+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 2, '6', '110', 'SA08:00-11:20 360305', 'อาจารย์อัษฎาวุธ ไสยรส', 50, 11, 39, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:36+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2567, 2, '7', '110', NULL, 'อาจารย์อัษฎาวุธ ไสยรส', 3, 3, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:36+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 1, '1', '110', 'TU08:00-11:20 38-IT0503', 'อาจารย์วินัย แสงกล้า', 50, 46, 4, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:37+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 1, '2', '110', 'TU08:00-11:20 38-IT0503', 'อาจารย์วินัย แสงกล้า', 50, 18, 32, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:37+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 1, '3', '110', 'TU08:00-11:20 38-IT0503', 'อาจารย์วินัย แสงกล้า', 50, 33, 17, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:37+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 1, '4', '110', 'TU08:00-11:20 38-IT0503', 'อาจารย์วินัย แสงกล้า', 50, 11, 39, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:37+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 1, '5', '110', 'SU08:00-11:20 360302', 'อาจารย์อัษฎาวุธ ไสยรส', 50, 27, 23, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:37+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 1, '6', '110', 'SU11:20-14:40 151006', 'อาจารย์อัษฎาวุธ ไสยรส', 50, 27, 23, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:37+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 2, '1', '110', 'TU08:00-11:20 37-EN4009', 'อาจารย์วินัย แสงกล้า', 55, 52, 3, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:38+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 2, '2', '110', 'TU08:00-11:20 37-EN4009', 'อาจารย์วินัย แสงกล้า', 50, 46, 4, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:38+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 2, '3', '110', 'SU08:00-11:20 360402', 'อาจารย์อัษฎาวุธ ไสยรส', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:38+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32704, '1109904', 2568, 2, '4', '110', NULL, 'อาจารย์อัษฎาวุธ ไสยรส', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1109904&coursename=', '2026-08-17T05:42:38+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 1, '1', '120', 'TU13:00-16:20 260401', 'ผู้ช่วยศาสตราจารย์วิชัย วัชรเวคะวิชญ์ | อาจารย์สุทิน เจียมประโคน', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:45+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 1, '2', '120', 'TU13:00-16:20 260401', 'ผู้ช่วยศาสตราจารย์วิชัย วัชรเวคะวิชญ์ | อาจารย์สุทิน เจียมประโคน', 50, 48, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:45+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 1, '3', '120', 'TU13:00-16:20 260401', 'ผู้ช่วยศาสตราจารย์วิชัย วัชรเวคะวิชญ์ | อาจารย์สุทิน เจียมประโคน', 56, 56, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:45+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 1, '4', '120', 'TU08:00-11:20 070205', 'รองศาสตราจารย์จันทร์เพ็ญ ภูโสภา | ผู้ช่วยศาสตราจารย์ ดร.สิบปีย์ ชยานุสาสนี จันทร์ดอน', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:45+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 1, '5', '120', 'SA08:00-11:20 070205', 'ผู้ช่วยศาสตราจารย์บุญส่ง เทียมภักดี', 50, 5, 45, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:45+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 2, '1', '120', 'TU08:00-11:20 38-IT0503', 'อาจารย์สุทิน เจียมประโคน', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:46+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 2, '2', '120', 'TU08:00-11:20 38-IT0503', 'อาจารย์สุทิน เจียมประโคน', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:46+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 2, '3', '120', 'TU08:00-11:20 38-IT0503', 'อาจารย์สุทิน เจียมประโคน', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:46+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 2, '4', '120', 'TU13:00-16:20 070304', 'รองศาสตราจารย์จันทร์เพ็ญ ภูโสภา | ผู้ช่วยศาสตราจารย์ ดร.สิบปีย์ ชยานุสาสนี จันทร์ดอน', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:46+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2567, 2, '5', '120', 'SA08:00-11:20 150801', 'ผู้ช่วยศาสตราจารย์บุญส่ง เทียมภักดี', 50, 32, 18, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:46+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2568, 1, '1', '120', 'TU08:00-11:20 070205', 'รองศาสตราจารย์จันทร์เพ็ญ ภูโสภา | ผู้ช่วยศาสตราจารย์ ดร.สิบปีย์ ชยานุสาสนี จันทร์ดอน', 59, 58, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:47+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2568, 2, '1', '120', 'TU08:00-11:20 37-EN4007', 'รองศาสตราจารย์จันทร์เพ็ญ ภูโสภา | อาจารย์สุทิน เจียมประโคน', 64, 60, 4, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:47+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32707, '1209901', 2568, 2, '2', '120', NULL, 'อาจารย์สุทิน เจียมประโคน', 3, 2, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209901&coursename=', '2026-08-17T05:42:47+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 1, '1', '120', 'TU08:00-11:20 350305', 'อาจารย์ระพีพันธ์ ศิริสัมพันธ์ | ผู้ช่วยศาสตราจารย์นัฐณรงค์ กวีพงศธร | อาจารย์พิราภรณ์ พันธุ์มณี', 50, 45, 5, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:48+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 1, '2', '120', 'TU08:00-11:20 350305', 'อาจารย์ระพีพันธ์ ศิริสัมพันธ์ | ผู้ช่วยศาสตราจารย์นัฐณรงค์ กวีพงศธร | อาจารย์พิราภรณ์ พันธุ์มณี', 50, 29, 21, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:48+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 1, '3', '120', 'TU08:00-11:20 38-IT0503', 'อาจารย์สกุณา พันธุระ | รองศาสตราจารย์ ดร .กิตติกรณ์ บำรุงบุญ | อาจารย์สุนิศา โพธิแสนสุข', 50, 23, 27, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:48+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 1, '4', '120', 'TU08:00-11:20 38-IT0503', 'อาจารย์สกุณา พันธุระ | รองศาสตราจารย์ ดร .กิตติกรณ์ บำรุงบุญ | อาจารย์สุนิศา โพธิแสนสุข', 50, 10, 40, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:48+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 2, '1', '120', 'TU08:00-11:20 37-EN4008', 'อาจารย์ระพีพันธ์ ศิริสัมพันธ์ | อาจารย์รัตน ไวยะราบุตร | อาจารย์พิราภรณ์ พันธุ์มณี', 50, 24, 26, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:49+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 2, '2', '120', 'TU08:00-11:20 37-EN4008', 'อาจารย์ระพีพันธ์ ศิริสัมพันธ์ | อาจารย์รัตน ไวยะราบุตร | อาจารย์พิราภรณ์ พันธุ์มณี', 50, 4, 46, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:49+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 2, '3', '120', 'TU13:00-16:20 37-EN4009', 'อาจารย์สกุณา พันธุระ | รองศาสตราจารย์ ดร .กิตติกรณ์ บำรุงบุญ | อาจารย์สุนิศา โพธิแสนสุข', 50, 38, 12, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:49+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 2, '4', '120', 'TU13:00-16:20 37-EN4009', 'อาจารย์สกุณา พันธุระ | รองศาสตราจารย์ ดร .กิตติกรณ์ บำรุงบุญ | อาจารย์สุนิศา โพธิแสนสุข', 50, 3, 47, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:49+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2567, 2, '5', '120', 'SU08:00-11:20 360408', 'อาจารย์สิรินภา ขจรโมทย์ | อาจารย์วิกรณ์กิจ อินทร์จันทร์ | อาจารย์สุนิศา โพธิแสนสุข', 20, 10, 10, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:49+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2568, 1, '1', '120', 'WE08:00-11:20 150410', 'อาจารย์ระพีพันธ์ ศิริสัมพันธ์ | รองศาสตราจารย์ ดร .กิตติกรณ์ บำรุงบุญ | อาจารย์พิมพ์วลัญช์ พลหงษ์', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:50+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2568, 1, '2', '120', 'WE08:00-11:20 150410', 'อาจารย์ระพีพันธ์ ศิริสัมพันธ์ | รองศาสตราจารย์ ดร .กิตติกรณ์ บำรุงบุญ | อาจารย์พิมพ์วลัญช์ พลหงษ์', 55, 23, 32, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:50+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2568, 1, '3', '120', 'WE13:00-16:20 360001', 'ผู้ช่วยศาสตราจารย์ ดร.สุธีระพงษ์ พินิจพล | รองศาสตราจารย์ ดร .กิตติกรณ์ บำรุงบุญ | อาจารย์ภานุวัฒน์ เหล่าพิลัย', 50, 39, 11, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:50+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2568, 1, '4', '120', 'WE13:00-16:20 360001', 'ผู้ช่วยศาสตราจารย์ ดร.สุธีระพงษ์ พินิจพล | รองศาสตราจารย์ ดร .กิตติกรณ์ บำรุงบุญ | อาจารย์ภานุวัฒน์ เหล่าพิลัย', 50, 12, 38, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:50+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2568, 1, '5', '120', NULL, 'ผู้ช่วยศาสตราจารย์ ดร.อำพร แสงไชยา', 1, 0, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:50+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2568, 2, '1', '120', 'SU08:00-11:20 360306', 'อาจารย์วิกรณ์กิจ อินทร์จันทร์ | อาจารย์รัตน ไวยะราบุตร | อาจารย์พิราภรณ์ พันธุ์มณี', 50, 15, 35, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:51+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32708, '1209902', 2568, 2, '2', '120', 'TU16:20-18:50 360101', 'อาจารย์สกุณา พันธุระ | อาจารย์สุนิศา โพธิแสนสุข | อาจารย์สิรินภา ขจรโมทย์', 50, 31, 19, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209902&coursename=', '2026-08-17T05:42:51+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 1, '1', '120', 'TU13:00-16:20 350803', 'อาจารย์ศิรินนา วอนเก่าน้อย | ดร.ชุมแพร บุญยืน', 50, 29, 21, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:52+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 1, '2', '120', 'TU13:00-16:20 350803', 'อาจารย์ศิรินนา วอนเก่าน้อย | ดร.ชุมแพร บุญยืน', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:52+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 1, '3', '120', 'TU08:00-11:20 360402', 'อาจารย์ณุกานดา ศุภวัฒน์ | อาจารย์สิทธานต์ ดีล้น', 50, 8, 42, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:52+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 1, '4', '120', 'TU08:00-11:20 360408', 'ดร.ชุมแพร บุญยืน | ผู้ช่วยศาสตราจารย์ ดร.วัชรินทร์ สุทธิศัย', 50, 34, 16, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:52+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 1, '5', '120', 'SU08:00-11:20 360301', 'ผู้ช่วยศาสตราจารย์นวรัตน์ เดชพิมล | รองศาสตราจารย์ ดร .ประภัสสร ฤทธิสุทธิ์', 50, 2, 48, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:52+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 1, '6', '120', NULL, 'อาจารย์ณุกานดา ศุภวัฒน์', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:52+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 1, '7', '120', 'SA08:00-11:20 151303', 'ผู้ช่วยศาสตราจารย์นัยนา ประทุมรัตน์ | ผู้ช่วยศาสตราจารย์ ดร.วัชรินทร์ สุทธิศัย', 60, 35, 25, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:52+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 1, '8', '120', NULL, 'ดร.ชัยวัฒน์ สุภัควรกุล', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:52+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 2, '1', '120', 'TU13:00-16:20 350804', 'อาจารย์ศิรินนา วอนเก่าน้อย | ผู้ช่วยศาสตราจารย์ ดร.วัชรินทร์ สุทธิศัย', 50, 38, 12, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 2, '2', '120', 'TU13:00-16:20 350804', 'อาจารย์ศิรินนา วอนเก่าน้อย | ผู้ช่วยศาสตราจารย์ ดร.วัชรินทร์ สุทธิศัย', 50, 27, 23, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 2, '3', '120', 'TU08:00-11:20 350804', 'ดร.ชุมแพร บุญยืน | รองศาสตราจารย์ ดร .ประภัสสร ฤทธิสุทธิ์', 50, 41, 9, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 2, '4', '120', 'TU08:00-11:20 350804', 'ดร.ชุมแพร บุญยืน | รองศาสตราจารย์ ดร .ประภัสสร ฤทธิสุทธิ์', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2567, 2, '5', '120', 'SU08:00-11:20 360302', 'ผู้ช่วยศาสตราจารย์นวรัตน์ เดชพิมล | รองศาสตราจารย์ ดร .ประภัสสร ฤทธิสุทธิ์', 50, 15, 35, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2568, 1, '1', '120', 'TU13:00-16:20 360303', 'ดร.ชุมแพร บุญยืน | รองศาสตราจารย์ ดร .ประภัสสร ฤทธิสุทธิ์', 53, 51, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2568, 1, '2', '120', 'TU13:00-16:20 360303', 'ดร.ชุมแพร บุญยืน | รองศาสตราจารย์ ดร .ประภัสสร ฤทธิสุทธิ์', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2568, 1, '3', '120', NULL, 'ผู้ช่วยศาสตราจารย์นัยนา ประทุมรัตน์', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2568, 2, '1', '120', 'TU13:00-16:20 160601', 'ผู้ช่วยศาสตราจารย์ไปรมา เฮียงราช | ผู้ช่วยศาสตราจารย์ ดร.วัชรินทร์ สุทธิศัย', 73, 58, 15, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:54+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2568, 2, '2', '120', 'TU13:00-16:20 160601', 'ผู้ช่วยศาสตราจารย์ไปรมา เฮียงราช', 52, 50, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:54+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2568, 2, '3', '120', 'SA16:20-19:40 150410', 'อาจารย์ณุกานดา ศุภวัฒน์', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:54+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32709, '1209903', 2568, 2, '4', '120', NULL, 'ผู้ช่วยศาสตราจารย์นวรัตน์ เดชพิมล | ผู้ช่วยศาสตราจารย์ ดร.วัชรินทร์ สุทธิศัย', 2, 2, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1209903&coursename=', '2026-08-17T05:42:54+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2567, 1, '1', '130', 'TU13:00-16:20 040101', 'อาจารย์ปวีนา ภูมิแดนดิน', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:55+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2567, 1, '2', '130', 'TU13:00-16:20 030204', 'อาจารย์ผุสดี กิจบุญ', 50, 26, 24, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:55+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2567, 1, '3', '130', 'TU08:00-11:20 350803', 'ผู้ช่วยศาสตราจารย์ทนงศักดิ์ ปัดสินธุ์ | อาจารย์ดิษยพงศ์ หกสุวรรณ', 50, 35, 15, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:55+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2567, 1, '4', '130', 'TU08:00-11:20 350803', 'ผู้ช่วยศาสตราจารย์ทนงศักดิ์ ปัดสินธุ์ | อาจารย์ดิษยพงศ์ หกสุวรรณ', 50, 30, 20, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:55+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2567, 2, '1', '130', 'TU13:00-16:20 040101', 'อาจารย์ปวีนา ภูมิแดนดิน', 50, 47, 3, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:56+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2567, 2, '2', '130', 'TU08:00-11:20 030204', 'อาจารย์ผุสดี กิจบุญ', 50, 20, 30, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:56+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2567, 2, '3', '130', 'TU08:00-11:20 260401', 'ผู้ช่วยศาสตราจารย์ทนงศักดิ์ ปัดสินธุ์ | อาจารย์ดิษยพงศ์ หกสุวรรณ', 50, 37, 13, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:56+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2567, 2, '4', '130', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:56+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2568, 1, '1', '130', 'TU08:00-11:20 030204', 'อาจารย์ปวีนา ภูมิแดนดิน', 50, 43, 7, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:57+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32710, '1309901', 2568, 1, '2', '130', 'TU13:00-16:20 030202', 'ผู้ช่วยศาสตราจารย์ทนงศักดิ์ ปัดสินธุ์ | อาจารย์ดิษยพงศ์ หกสุวรรณ', 51, 50, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309901&coursename=', '2026-08-17T05:42:57+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 1, '1', '130', 'TU08:00-11:20 030202', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 48, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:58+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 1, '2', '130', 'TU08:00-11:20 030202', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 47, 3, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:58+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 1, '3', '130', 'TU13:00-16:20 030202', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 38, 12, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:58+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 1, '4', '130', 'TU13:00-16:20 030202', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 29, 21, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:58+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 1, '5', '130', 'SU08:00-11:20 360305', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช', 50, 2, 48, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:58+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 2, '1', '130', 'TU13:00-16:20 030200', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 40, 10, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:59+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 2, '2', '130', 'TU13:00-16:20 030200', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 9, 41, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:59+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 2, '3', '130', 'TU13:00-16:20 030200', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 24, 26, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:59+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2567, 2, '4', '130', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:42:59+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2568, 1, '1', '130', 'TU08:00-11:20 030200', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 13, 37, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:43:00+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2568, 1, '2', '130', 'TU08:00-11:20 030200', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช | ผู้ช่วยศาสตราจารย์ ดร.นภาพร เวชกามา | อาจารย์Xนิภาภรณ์ จงวุฒิเวศย์ | รองศาสตราจารย์ ดร .วาริธ ราศรี', 50, 26, 24, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:43:00+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32711, '1309902', 2568, 1, '3', '130', 'SU14:40-18:00 340601', 'ผู้ช่วยศาสตราจารย์ ดร.กมลทิพย์ ตรีเดช', 7, 6, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309902&coursename=', '2026-08-17T05:43:00+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2567, 1, '1', '130', 'TU08:00-11:20 37-EN4005', 'รองศาสตราจารย์ ดร .ชูชาติ ผาระนัด', 50, 29, 21, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2567, 1, '2', '130', 'TU13:00-16:20 37-EN4005', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด', 50, 32, 18, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2567, 1, '3', '130', 'TU08:00-11:20 37-EN4006', 'อาจารย์ปกเกศ จันทะกล', 50, 35, 15, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2567, 1, '4', '130', 'TU13:00-16:20 37-EN4006', 'อาจารย์มุณี จันทะรัง', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2567, 2, '1', '130', 'TU08:00-11:20 37-EN4005', 'ผู้ช่วยศาสตราจารย์วรพันธุ์ สมบัติธีระ', 50, 21, 29, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2567, 2, '2', '130', 'TU13:00-16:20 37-EN4005', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด', 50, 18, 32, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2567, 2, '3', '130', 'TU08:00-11:20 37-EN4006', 'อาจารย์มุณี จันทะรัง', 50, 0, 50, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2567, 2, '4', '130', 'TU13:00-16:20 37-EN4006', 'อาจารย์มุณี จันทะรัง', 50, 15, 35, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2568, 1, '1', '130', 'TU08:00-11:20 37-EN4006', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด', 50, 48, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:03+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2568, 1, '2', '130', 'TU13:00-16:20 37-EN4006', 'อาจารย์มุณี จันทะรัง', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:03+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2568, 2, '1', '130', 'TU13:00-16:20 37-EN4007', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด', 52, 52, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:04+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2568, 2, '2', '130', 'SA08:00-11:20 37-EN4007', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด', 50, 19, 31, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:04+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32712, '1309903', 2568, 2, '8888', NULL, NULL, NULL, 2, 2, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309903&coursename=', '2026-08-17T05:43:04+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 1, '1', NULL, NULL, 'อาจารย์ธงชัย ผลรุ่ง', 60, 8, 52, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:05+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 1, '1', '130', 'TU08:00-11:20 330402', 'ผู้ช่วยศาสตราจารย์จิรสุดา ไชยทุม', 50, 28, 22, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:05+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 1, '2', '130', 'TU08:00-11:20 330403', 'ดร.นภธร ศิวารัตน์', 50, 7, 43, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:05+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 1, '3', '130', 'TU13:00-16:20 330402', 'อาจารย์ธงชัย ผลรุ่ง', 50, 25, 25, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:05+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 1, '4', '130', 'TU13:00-16:20 330403', 'อาจารย์วิษณุ บาคาล', 50, 8, 42, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:05+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 1, '5', '130', 'SA08:00-11:20 330403', 'อาจารย์ธงชัย ผลรุ่ง', 50, 10, 40, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:05+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 1, '6', '130', 'SA11:20-14:40 151302', 'อาจารย์วิษณุ บาคาล', 60, 19, 41, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:05+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 2, '1', '130', 'TU08:00-11:20 330201', 'ผู้ช่วยศาสตราจารย์จิรสุดา ไชยทุม', 50, 18, 32, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:06+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 2, '2', '130', 'TU08:00-11:20 330302', 'ดร.นภธร ศิวารัตน์', 50, 19, 31, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:06+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 2, '3', '130', 'TU13:00-16:20 330201', 'อาจารย์ธงชัย ผลรุ่ง', 50, 38, 12, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:06+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 2, '4', '130', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:06+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2567, 2, '5', '130', 'SA08:00-11:20 330201', 'ผู้ช่วยศาสตราจารย์จิรสุดา ไชยทุม', 50, 5, 45, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:06+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2568, 1, '1', '130', 'TU08:00-11:20 330304', 'ผู้ช่วยศาสตราจารย์จิรสุดา ไชยทุม', 50, 22, 28, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:07+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2568, 1, '2', '130', 'TU13:00-16:20 330302', 'ผู้ช่วยศาสตราจารย์จิรสุดา ไชยทุม', 50, 28, 22, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:07+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2568, 1, '3', '130', 'SU08:00-11:20 330304', 'ผู้ช่วยศาสตราจารย์จิรสุดา ไชยทุม', 50, 4, 46, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:07+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2568, 1, '4', '130', 'SU14:40-18:00 151004', 'อาจารย์วิษณุ บาคาล', 50, 26, 24, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:07+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2568, 2, '1', '130', 'TU08:00-11:20 330304', 'ผู้ช่วยศาสตราจารย์จิรสุดา ไชยทุม', 57, 55, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:07+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32713, '1309904', 2568, 2, '2', '130', 'SA08:00-11:20 330304', 'ผู้ช่วยศาสตราจารย์จิรสุดา ไชยทุม', 50, 15, 35, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1309904&coursename=', '2026-08-17T05:43:07+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2567, 1, '1', '140', 'SA14:40-18:00 390601', 'อาจารย์ ดร.ภิรมย์ สุวรรณสม', 50, 15, 35, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:08+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2567, 1, '2', '140', 'TU13:00-16:20 390502', 'ผู้ช่วยศาสตราจารย์ ดร.ผกามาศ จุลศรี | อาจารย์ธนิษฐ์นันท์ ชะยาสินธุ์ | ผู้ช่วยศาสตราจารย์ ดร.ดรรชนีย์ พลหาญ', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:08+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2567, 1, '3', '140', NULL, 'อาจารย์ ดร.ภิรมย์ สุวรรณสม', 10, 3, 7, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:08+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2567, 1, '4', '140', 'WE13:00-16:20 390509', 'ผู้ช่วยศาสตราจารย์กุสุมาวดี ฐานเจริญ | ผู้ช่วยศาสตราจารย์ ดร.ปิยรัตน์ นามเสนา | อาจารย์บุษยมาส รัตนดอน | อาจารย์ธนิษฐ์นันท์ ชะยาสินธุ์', 6, 6, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:08+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2567, 2, '1', '140', 'TU08:00-11:20 390502', 'ผู้ช่วยศาสตราจารย์ ดร.ผกามาศ จุลศรี | อาจารย์ธนิษฐ์นันท์ ชะยาสินธุ์ | ผู้ช่วยศาสตราจารย์ ดร.ดรรชนีย์ พลหาญ', 50, 43, 7, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:09+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2567, 2, '2', '140', 'SA08:00-11:20 390622', 'อาจารย์ ดร.ภิรมย์ สุวรรณสม', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:09+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2567, 2, '8888', NULL, NULL, NULL, 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:09+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2568, 1, '1', '140', 'TU08:00-11:20 390502', 'ผู้ช่วยศาสตราจารย์ ดร.ผกามาศ จุลศรี | อาจารย์ธนิษฐ์นันท์ ชะยาสินธุ์ | ผู้ช่วยศาสตราจารย์ ดร.ดรรชนีย์ พลหาญ', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:10+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2568, 1, '2', '140', 'SA08:00-11:20 390617', 'อาจารย์ ดร.ภิรมย์ สุวรรณสม', 50, 10, 40, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:10+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2568, 2, '1', '140', 'TU08:00-11:20 390502', 'ผู้ช่วยศาสตราจารย์ ดร.ผกามาศ จุลศรี | อาจารย์ธนิษฐ์นันท์ ชะยาสินธุ์ | ผู้ช่วยศาสตราจารย์ ดร.ดรรชนีย์ พลหาญ', 57, 57, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:10+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32714, '1409901', 2568, 2, '2', '140', 'SU08:00-11:20 100308', 'อาจารย์ ดร.ภิรมย์ สุวรรณสม', 50, 17, 33, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409901&coursename=', '2026-08-17T05:43:10+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 1, '1', NULL, NULL, 'อาจารย์นพดล ใหม่คามิ | ผู้ช่วยศาสตราจารย์พิชญ์นันท์ รักษาวงศ์', 60, 9, 51, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:11+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 1, '1', '140', 'TU08:00-11:20 37-EN6009', 'อาจารย์นพดล ใหม่คามิ', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:11+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 1, '2', '140', 'TU13:00-16:20 37-EN5008', 'อาจารย์นพดล ใหม่คามิ | อาจารย์สุอารีย์ นครพันธุ์', 50, 48, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:11+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 1, '3', '140', 'TU08:00-11:20 37-EN6007', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด | ผู้ช่วยศาสตราจารย์ชลดา ยอดยิ่ง', 50, 45, 5, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:11+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 1, '4', '140', 'TU13:00-16:20 37-EN6007', 'ผู้ช่วยศาสตราจารย์ชาติวิรุทธ์ ภัทรสุเมธี | อาจารย์ศนันธร พิชัย', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:11+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 2, '1', '140', 'TU08:00-11:20 37-EN6009', 'อาจารย์เปรมประชา ดรชัย', 50, 2, 48, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:12+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 2, '2', '140', 'TU13:00-16:20 37-EN6009', 'อาจารย์นพดล ใหม่คามิ | อาจารย์สุอารีย์ นครพันธุ์', 50, 37, 13, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:12+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 2, '3', '140', 'TU08:00-11:20 37-EN6010', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด | ผู้ช่วยศาสตราจารย์ชลดา ยอดยิ่ง', 50, 24, 26, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:12+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2567, 2, '4', '140', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:12+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2568, 1, '1', '140', 'TU08:00-11:20 37-EN4008', 'อาจารย์นพดล ใหม่คามิ', 51, 44, 7, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:13+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2568, 1, '2', '140', 'TU13:00-16:20 37-EN5005', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:13+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2568, 1, '3', '140', 'SA08:00-11:20 37-EN4010', 'ผู้ช่วยศาสตราจารย์พิชญ์นันท์ รักษาวงศ์', 50, 43, 7, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:13+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2568, 2, '1', '140', 'TU08:00-11:20 37-EN4008', 'ผู้ช่วยศาสตราจารย์สุจิตรา ผาระนัด', 56, 56, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:14+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2568, 2, '2', '140', 'TU13:00-16:20 37-EN4008', 'อาจารย์นพดล ใหม่คามิ', 69, 68, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:14+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2568, 2, '3', '140', NULL, 'อาจารย์ติดต่อเจ้าหน้าที่ทะเบียน แจ้งชื่อผู้สอน', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:14+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32715, '1409902', 2568, 2, '4', NULL, 'SU08:00-11:20 150705', 'อาจารย์นพดล ใหม่คามิ', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409902&coursename=', '2026-08-17T05:43:14+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 1, '1', NULL, NULL, 'อาจารย์ชมภู่ เหนือศรี', 60, 9, 51, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 1, '1', '140', 'TU08:00-11:20 090201', 'อาจารย์ชมภู่ เหนือศรี', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 1, '2', '140', 'TU13:00-16:20 090201', 'ผู้ช่วยศาสตราจารย์เชิดชัย สมบัติโยธา', 50, 25, 25, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 1, '3', '140', 'TU08:00-11:20 090201', 'อาจารย์ชมภู่ เหนือศรี', 50, 4, 46, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 1, '4', '140', 'TU13:00-16:20 090201', 'ผู้ช่วยศาสตราจารย์เชิดชัย สมบัติโยธา', 50, 0, 50, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 2, '1', '140', 'TU08:00-10:30 090305', 'ผู้ช่วยศาสตราจารย์เชิดชัย สมบัติโยธา', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 2, '2', '140', 'TU08:00-10:30 090305', 'ผู้ช่วยศาสตราจารย์เชิดชัย สมบัติโยธา', 50, 14, 36, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 2, '3', '140', 'TU13:00-15:30 090201', 'อาจารย์รติกร แสงห้าว', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 2, '4', '140', 'TU13:00-15:30 090203', 'ผู้ช่วยศาสตราจารย์ ดร.วุฒิกร สายแก้ว', 50, 34, 16, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2567, 2, '5', '140', NULL, 'อาจารย์ชมภู่ เหนือศรี', 3, 3, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2568, 1, '1', '140', 'TU08:00-10:30 090201', 'อาจารย์ชมภู่ เหนือศรี', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:16+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32716, '1409903', 2568, 1, '2', '140', 'TU13:00-16:20 090201', 'ผู้ช่วยศาสตราจารย์เชิดชัย สมบัติโยธา', 53, 50, 3, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409903&coursename=', '2026-08-17T05:43:16+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32717, '1409904', 2567, 1, '1', '140', 'TU08:00-11:20 230101', 'อาจารย์ ดร.อรนุช วงศ์วัฒนาเสถียร | อาจารย์อภิภวัส ปาลวัฒน์', 52, 49, 3, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409904&coursename=', '2026-08-17T05:43:18+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32717, '1409904', 2567, 1, '2', '140', 'TU13:00-16:20 150701', 'อาจารย์อภิภวัส ปาลวัฒน์ | อาจารย์ ดร.อรนุช วงศ์วัฒนาเสถียร', 51, 51, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409904&coursename=', '2026-08-17T05:43:18+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32717, '1409904', 2567, 2, '1', '140', 'TU08:00-11:20 120107', 'อาจารย์มณฑิรา จันทวารีย์ | อาจารย์อภิภวัส ปาลวัฒน์', 50, 48, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409904&coursename=', '2026-08-17T05:43:19+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32717, '1409904', 2567, 2, '2', '140', 'TU13:00-16:20 120107', 'อาจารย์มณฑิรา จันทวารีย์ | อาจารย์อภิภวัส ปาลวัฒน์', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409904&coursename=', '2026-08-17T05:43:19+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32717, '1409904', 2568, 2, '1', '140', 'FR08:00-11:20 120107', 'อาจารย์มณฑิรา จันทวารีย์', 51, 29, 22, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409904&coursename=', '2026-08-17T05:43:20+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 1, '1', '140', 'TU13:00-16:20 622', 'อาจารย์จักรพันธ์ ศรีวงษา', 50, 33, 17, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:21+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 1, '2', '140', 'TU08:00-11:20 390409', 'ผู้ช่วยศาสตราจารย์ณัฐพงษ์ พันธุ์มณี', 50, 28, 22, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:21+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 1, '3', '140', 'TU08:00-11:20 632', 'ผู้ช่วยศาสตราจารย์ ดร.ไชยยันต์ สกุลไทย', 50, 6, 44, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:21+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 1, '4', '140', 'TU13:00-16:20 632', 'อาจารย์ปรัชญา ไชยเมือง', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:21+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 1, '5', '140', 'TU13:00-16:20 612', 'รองศาสตราจารย์ ดร .สิทธิชัย บุษหมั่น', 50, 1, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:21+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 1, '6', '140', 'WE08:00-11:20 612', 'อาจารย์พวงผกา คุณาสิทธิ์', 50, 32, 18, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:21+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 1, '7', '140', 'SU08:00-11:20 151302', 'ผู้ช่วยศาสตราจารย์ ดร.ไชยยันต์ สกุลไทย', 60, 19, 41, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:21+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 2, '1', '140', 'TU08:00-11:20 390409', 'ผู้ช่วยศาสตราจารย์ณัฐพงษ์ พันธุ์มณี', 50, 16, 34, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:22+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 2, '2', '140', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:22+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 2, '3', '140', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:22+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 2, '4', '140', 'TU13:00-16:20 636', 'รองศาสตราจารย์ ดร .สิทธิชัย บุษหมั่น', 50, 7, 43, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:22+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 2, '5', '140', 'WE13:00-16:20 622', 'อาจารย์จักรพันธ์ ศรีวงษา', 30, 30, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:22+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2567, 2, '6', '140', 'SU13:00-16:20 627', 'อาจารย์จักรพันธ์ ศรีวงษา', 50, 13, 37, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:22+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2568, 1, '1', '140', 'TU08:00-11:20 390409', 'ผู้ช่วยศาสตราจารย์ณัฐพงษ์ พันธุ์มณี', 50, 26, 24, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:23+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2568, 1, '2', '140', 'TU13:00-16:20 627', 'รองศาสตราจารย์ ดร .สิทธิชัย บุษหมั่น', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:23+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2568, 1, '3', '140', 'WE13:00-16:20 622', 'อาจารย์จักรพันธ์ ศรีวงษา', 35, 29, 6, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:23+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2568, 1, '4', '140', 'SU08:00-11:20 622', 'อาจารย์จักรพันธ์ ศรีวงษา', 30, 8, 22, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:23+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32718, '1409905', 2568, 2, '1', '140', NULL, 'อาจารย์ปรัชญา ไชยเมือง', 3, 3, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409905&coursename=', '2026-08-17T05:43:24+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32719, '1409906', 2567, 1, '1', '140', NULL, NULL, 60, 0, 60, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409906&coursename=', '2026-08-17T05:43:25+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32719, '1409906', 2567, 1, '2', '140', NULL, 'ผู้ช่วยศาสตราจารย์ ดร.รามนรี นนทภา', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409906&coursename=', '2026-08-17T05:43:25+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32719, '1409906', 2567, 2, '1', '140', 'TU08:00-11:20 150801', 'อาจารย์พิชญ์ทิพา สุวรรณศรี', 50, 13, 37, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409906&coursename=', '2026-08-17T05:43:25+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32719, '1409906', 2567, 2, '2', '140', 'TU13:00-16:20 150901-150903', 'อาจารย์ปิยนันท์ เกตุแสง', 50, 7, 43, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409906&coursename=', '2026-08-17T05:43:25+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32719, '1409906', 2567, 2, '3', '140', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409906&coursename=', '2026-08-17T05:43:25+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32719, '1409906', 2567, 2, '4', '140', 'TU13:00-16:20 150803', 'อาจารย์วริดา พลาศรี', 50, 29, 21, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409906&coursename=', '2026-08-17T05:43:25+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 1, '1', '140', 'TU08:00-11:20 37-EN4008', 'ดร.มลฤดี บุญยะศรี | ผู้ช่วยศาสตราจารย์วีรยุทธ เติมสวัสดิ์ | อาจารย์สิรินภา ขจรโมทย์', 60, 14, 46, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 1, '2', '140', 'TU13:00-16:20 360407', 'อาจารย์เกศดาพร วงษ์ซิ้ม | ผู้ช่วยศาสตราจารย์ ดร.ทวีทรัพย์ ไชยรักษ์ | อาจารย์ ดร.ชนะชัย อวนวัง', 60, 0, 60, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 1, '3', '140', 'TU13:00-16:20 350701', 'ดร.กัญชลิกา รัตนเชิดฉาย | ดร.ธนนชาติ อิ่มสมบัติ | อาจารย์สิรินภา ขจรโมทย์', 60, 30, 30, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 1, '4', '140', 'TU08:00-11:20 350701', 'ผู้ช่วยศาสตราจารย์ชวิศร ปูคะภาค | อาจารย์ศรินนา ศิริมาตย์ | อาจารย์มารุดิศ วชิรโกเมน', 60, 3, 57, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 1, '5', '140', 'SA08:00-11:20 151302', 'อาจารย์เกศดาพร วงษ์ซิ้ม', 60, 19, 41, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:28+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 2, '1', '140', 'TU08:00-11:20 37-EN6007', 'ดร.กัญชลิกา รัตนเชิดฉาย | ดร.ธนนชาติ อิ่มสมบัติ | อาจารย์สิรินภา ขจรโมทย์', 50, 40, 10, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 2, '2', '140', NULL, NULL, 50, 0, 50, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 2, '3', '140', 'TU13:00-16:20 37-EN6007', 'ดร.มลฤดี บุญยะศรี | ผู้ช่วยศาสตราจารย์วีรยุทธ เติมสวัสดิ์ | อาจารย์ ดร.ชนะชัย อวนวัง', 50, 28, 22, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 2, '4', '140', 'TU13:00-16:20 37-EN6008', 'อาจารย์ศรินนา ศิริมาตย์ | ผู้ช่วยศาสตราจารย์ชวิศร ปูคะภาค | อาจารย์มารุดิศ วชิรโกเมน', 50, 11, 39, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2567, 2, '5', '140', 'SA14:40-18:00 150801', 'อาจารย์เกศดาพร วงษ์ซิ้ม | ดร.ธนนชาติ อิ่มสมบัติ | อาจารย์สิรินภา ขจรโมทย์', 50, 37, 13, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2568, 1, '1', '140', 'TU08:00-11:20 37-EN5007', 'ผู้ช่วยศาสตราจารย์วีรยุทธ เติมสวัสดิ์ | ดร.มลฤดี บุญยะศรี | อาจารย์ ดร.ชนะชัย อวนวัง', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2568, 1, '2', '140', 'TU08:00-11:20 090202', 'อาจารย์ศรินนา ศิริมาตย์ | อาจารย์มารุดิศ วชิรโกเมน | อาจารย์รังสรรค์ พงษ์พัฒนอำไพ', 50, 24, 26, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2568, 1, '3', '140', 'TU13:00-16:20 150701', 'ผู้ช่วยศาสตราจารย์ ดร.ทวีทรัพย์ ไชยรักษ์ | อาจารย์เกศดาพร วงษ์ซิ้ม | อาจารย์มารุดิศ วชิรโกเมน', 50, 48, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2568, 1, '4', '140', 'TU13:00-16:20 150703', 'ดร.กัญชลิกา รัตนเชิดฉาย | ดร.ธนนชาติ อิ่มสมบัติ | อาจารย์ ดร.ชนะชัย อวนวัง', 50, 49, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (32720, '1409907', 2568, 2, '1', NULL, 'SU16:20-19:40 37-EN3003', 'ดร.ธนนชาติ อิ่มสมบัติ', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=1409907&coursename=', '2026-08-17T05:43:30+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39105, '7071101', 2567, 1, '2', NULL, 'MO08:50-12:10 38-IT0310', 'ดร.กฤษดา หินเธาว์', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071101&coursename=', '2026-08-17T05:43:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39186, '7071101', 2567, 1, '1', NULL, 'MO13:00-16:20 38-IT0204', 'รองศาสตราจารย์ ดร .วรปภา อารีราษฎร์', 60, 0, 60, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071101&coursename=', '2026-08-17T05:43:31+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39186, '7071101', 2567, 2, '1', NULL, 'SA08:00-11:20 38-IT0110', 'ดร.ธารีชล ดงสงคราม', 60, 2, 58, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071101&coursename=', '2026-08-17T05:43:32+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39105, '7071101', 2568, 1, '1', NULL, 'MO08:50-12:10 38-IT0311', 'ดร.กฤษดา หินเธาว์', 60, 6, 54, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071101&coursename=', '2026-08-17T05:43:33+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39881, '7071102', 2567, 1, '1', NULL, 'MO13:00-16:20 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071102&coursename=', '2026-08-17T05:43:34+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39187, '7071102', 2567, 2, '1', NULL, 'SA11:20-14:40 38-IT0110', 'ดร.อภิชาติ เหล็กดี', 60, 2, 58, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071102&coursename=', '2026-08-17T05:43:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39881, '7071102', 2568, 1, '1', NULL, 'MO13:00-16:20 38-IT0309', 'อาจารย์วรรณพร สารภักดิ์', 60, 6, 54, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071102&coursename=', '2026-08-17T05:43:36+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39188, '7071103', 2567, 2, '2', NULL, 'SU08:00-11:20 38-IT0110', 'ดร.ธารีชล ดงสงคราม', 60, 2, 58, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071103&coursename=', '2026-08-17T05:43:38+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (40154, '7071103', 2567, 2, '1', NULL, 'FR08:50-12:10 38-IT0311', 'ดร.กฤษดา หินเธาว์', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071103&coursename=', '2026-08-17T05:43:38+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (40154, '7071103', 2568, 2, '1', NULL, 'TH08:50-12:10 38-IT0311', 'ดร.กฤษดา หินเธาว์', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071103&coursename=', '2026-08-17T05:43:40+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39189, '7071104', 2567, 2, '2', NULL, 'SU11:20-14:40 38-IT0110', 'ดร.อภิชาติ เหล็กดี', 60, 2, 58, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071104&coursename=', '2026-08-17T05:43:41+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (40155, '7071104', 2567, 2, '1', NULL, 'FR13:00-16:20 38-IT0311', 'ดร.กฤษดา หินเธาว์', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071104&coursename=', '2026-08-17T05:43:41+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (40155, '7071104', 2568, 2, '1', NULL, 'TH13:00-16:20 38-IT0311', 'ดร.กฤษดา หินเธาว์', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071104&coursename=', '2026-08-17T05:43:43+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (40156, '7071105', 2567, 2, '1', NULL, 'MO08:50-12:10 38-IT0311', 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071105&coursename=', '2026-08-17T05:43:45+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (40156, '7071105', 2568, 2, '1', NULL, 'MO13:00-16:20 38-IT0311', 'อาจารย์กีรติ ทองเนตร', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071105&coursename=', '2026-08-17T05:43:47+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39224, '7071201', 2567, 1, '1', NULL, 'TH08:50-12:10 38-IT0309', 'อาจารย์วรรณพร สารภักดิ์', 60, 11, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071201&coursename=', '2026-08-17T05:43:54+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39224, '7071201', 2568, 1, '1', NULL, 'MO13:00-16:20 38-IT0311', 'ดร.กฤษดา หินเธาว์', 60, 6, 54, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071201&coursename=', '2026-08-17T05:43:56+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41202, '7071202', 2567, 1, '1', NULL, 'MO13:00-16:20 38-IT0313', 'อาจารย์ธเนศ ยืนสุข', 60, 11, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071202&coursename=', '2026-08-17T05:43:57+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41202, '7071202', 2568, 1, '1', NULL, 'FR13:00-16:20 38-IT0309', 'อาจารย์กีรติ ทองเนตร', 60, 6, 54, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071202&coursename=', '2026-08-17T05:43:59+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41202, '7071202', 2568, 2, '1', NULL, NULL, 'ดร.กฤษดา หินเธาว์', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071202&coursename=', '2026-08-17T05:44:00+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41181, '7071203', 2567, 2, '1', NULL, 'MO08:50-12:10 38-IT0313', 'อาจารย์กีรติ ทองเนตร', 60, 11, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071203&coursename=', '2026-08-17T05:44:02+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41181, '7071203', 2568, 2, '1', NULL, 'TH13:00-16:20 38-IT0313', 'อาจารย์กีรติ ทองเนตร', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071203&coursename=', '2026-08-17T05:44:03+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41203, '7071204', 2567, 2, '1', NULL, 'TH08:50-12:10 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 11, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071204&coursename=', '2026-08-17T05:44:05+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41203, '7071204', 2568, 2, '1', NULL, 'MO13:00-16:20 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071204&coursename=', '2026-08-17T05:44:07+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41204, '7071301', 2567, 1, '1', NULL, 'MO13:00-16:20 38-IT0309', 'อาจารย์กีรติ ทองเนตร', 60, 7, 53, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071301&coursename=', '2026-08-17T05:44:08+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41204, '7071301', 2568, 1, '1', NULL, 'FR08:50-12:10 38-IT0309', 'อาจารย์กีรติ ทองเนตร', 60, 10, 50, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071301&coursename=', '2026-08-17T05:44:09+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41205, '7071302', 2567, 1, '1', NULL, 'FR13:00-16:20 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 7, 53, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071302&coursename=', '2026-08-17T05:44:11+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41205, '7071302', 2568, 1, '1', NULL, 'TH08:50-12:10 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 11, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071302&coursename=', '2026-08-17T05:44:12+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41206, '7071303', 2567, 2, '1', NULL, 'MO08:50-12:10 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 7, 53, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071303&coursename=', '2026-08-17T05:44:15+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41206, '7071303', 2568, 2, '1', NULL, 'TH08:50-12:10 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 9, 51, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071303&coursename=', '2026-08-17T05:44:16+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39231, '7071401', 2567, 1, '1', NULL, 'WE08:50-12:10 38-IT0313', 'อาจารย์วรรณพร สารภักดิ์', 60, 1, 59, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071401&coursename=', '2026-08-17T05:44:17+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39231, '7071401', 2568, 1, '1', NULL, 'MO08:50-12:10 38-IT0310', 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 60, 8, 52, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071401&coursename=', '2026-08-17T05:44:19+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41209, '7071402', 2567, 2, '1', NULL, 'TH12:10-17:10 38-IT0311', 'อาจารย์กีรติ ทองเนตร', 60, 7, 53, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071402&coursename=', '2026-08-17T05:44:21+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41209, '7071402', 2568, 2, '1', NULL, 'MO12:10-17:10 38-IT0309', 'อาจารย์ธเนศ ยืนสุข', 60, 9, 51, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071402&coursename=', '2026-08-17T05:44:23+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39233, '7071403', 2567, 1, '1', NULL, 'FR13:00-16:20 38-IT0311', 'อาจารย์กีรติ ทองเนตร', 60, 1, 59, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071403&coursename=', '2026-08-17T05:44:23+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41210, '7071403', 2568, 1, '1', NULL, 'MO13:00-18:50 38-IT0310', 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 60, 8, 52, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071403&coursename=', '2026-08-17T05:44:25+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39234, '7071404', 2567, 1, '1', NULL, 'MO08:50-12:10 38-IT0311', 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 60, 1, 59, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071404&coursename=', '2026-08-17T05:44:27+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39234, '7071404', 2568, 1, '1', NULL, NULL, 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7071404&coursename=', '2026-08-17T05:44:29+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39236, '7072102', 2567, 1, '1', NULL, 'FR08:50-12:10 38-IT0313', 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 60, 11, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072102&coursename=', '2026-08-17T05:44:34+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39236, '7072102', 2568, 1, '1', NULL, 'WE08:00-11:20 38-IT0310', 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 60, 5, 55, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072102&coursename=', '2026-08-17T05:44:35+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39239, '7072204', 2567, 2, '1', NULL, 'TH13:00-16:20 38-IT0310', 'อาจารย์ธเนศ ยืนสุข', 60, 11, 49, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072204&coursename=', '2026-08-17T05:44:48+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41216, '7072304', 2567, 1, '1', NULL, 'FR08:50-12:10 38-IT0311', 'อาจารย์วรรณพร สารภักดิ์', 60, 7, 53, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072304&coursename=', '2026-08-17T05:45:03+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41218, '7072306', 2567, 2, '1', NULL, 'MO13:00-16:20 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 7, 53, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072306&coursename=', '2026-08-17T05:45:11+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41218, '7072306', 2568, 1, '1', NULL, 'TH13:00-16:20 38-IT0310', 'อาจารย์วรรณพร สารภักดิ์', 60, 9, 51, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072306&coursename=', '2026-08-17T05:45:11+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39248, '7072308', 2567, 1, '1', NULL, 'TH08:50-12:10 38-IT0313', 'ดร.กฤษดา หินเธาว์', 60, 7, 53, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072308&coursename=', '2026-08-17T05:45:16+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41222, '7072309', 2567, 1, '1', NULL, 'TH13:00-16:20 38-IT0309', 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 60, 7, 53, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072309&coursename=', '2026-08-17T05:45:20+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39253, '7072313', 2567, 1, '1', '500', 'WE13:00-16:20 38-IT0502', 'อาจารย์อุดมศักดิ์ พิมพ์พาศรี', 50, 21, 29, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072313&coursename=', '2026-08-17T05:45:33+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39214, '7072402', 2567, 1, '1', '500', 'WE13:00-16:20 38-IT0313', 'อาจารย์กีรติ ทองเนตร', 50, 36, 14, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072402&coursename=', '2026-08-17T05:45:53+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39214, '7072402', 2567, 2, '1', '500', 'WE13:00-16:20 38-IT0313', 'อาจารย์กีรติ ทองเนตร', 30, 30, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072402&coursename=', '2026-08-17T05:45:54+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39214, '7072402', 2568, 1, '1', '500', 'WE13:00-16:20 38-IT0313', 'อาจารย์กีรติ ทองเนตร', 30, 28, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072402&coursename=', '2026-08-17T05:45:55+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39214, '7072402', 2568, 2, '1', '500', 'WE13:00-16:20 38-IT0313', 'อาจารย์กีรติ ทองเนตร', 30, 28, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072402&coursename=', '2026-08-17T05:45:56+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (22956, '7072403', 2567, 1, '1', '500', 'WE13:00-16:20 38-IT0310', 'อาจารย์ธเนศ ยืนสุข', 50, 50, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072403&coursename=', '2026-08-17T05:45:56+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (22956, '7072403', 2567, 1, '2', '500', 'WE13:00-16:20 38-IT0310', 'ดร.กฤษดา หินเธาว์', 50, 42, 8, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072403&coursename=', '2026-08-17T05:45:56+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (22956, '7072403', 2567, 2, '1', '500', 'WE13:00-16:20 38-IT0310', 'อาจารย์ธเนศ ยืนสุข', 30, 29, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072403&coursename=', '2026-08-17T05:45:57+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (22956, '7072403', 2567, 2, '2', '500', 'WE13:00-16:20 38-IT0310', 'ดร.กฤษดา หินเธาว์', 30, 30, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072403&coursename=', '2026-08-17T05:45:57+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (22956, '7072403', 2567, 2, '3', '500', NULL, 'อาจารย์ธเนศ ยืนสุข', 5, 3, 2, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072403&coursename=', '2026-08-17T05:45:57+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (22956, '7072403', 2568, 1, '1', '500', NULL, NULL, 0, 0, 0, 'ปิด', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072403&coursename=', '2026-08-17T05:45:58+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (22956, '7072403', 2568, 1, '2', '500', 'WE13:00-16:20 38-IT0310', 'ดร.กฤษดา หินเธาว์', 30, 21, 9, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072403&coursename=', '2026-08-17T05:45:58+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (22956, '7072403', 2568, 2, '1', '500', 'WE13:00-16:20 38-IT0310', 'ดร.กฤษดา หินเธาว์', 32, 31, 1, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072403&coursename=', '2026-08-17T05:45:59+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39260, '7072405', 2567, 1, '1', NULL, 'TH13:00-16:20 38-IT0310', 'ดร.กฤษดา หินเธาว์', 60, 1, 59, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7072405&coursename=', '2026-08-17T05:46:03+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41211, '7073401', 2567, 1, '1', NULL, NULL, 'ดร.กฤษดา หินเธาว์', 1, 1, 0, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=1&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7073401&coursename=', '2026-08-17T05:46:06+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (39261, '7073401', 2567, 2, '1', NULL, NULL, 'ดร.กฤษดา หินเธาว์', 60, 0, 60, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2567&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7073401&coursename=', '2026-08-17T05:46:07+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO offerings (course_id, course_code, acad_year, semester, section, course_group, schedule_raw, instructors, seats_total, seats_taken, seats_left, status, source_url, scraped_at)
VALUES (41211, '7073401', 2568, 2, '1', NULL, NULL, 'ดร.กฤษดา หินเธาว์', 60, 6, 54, 'ปกติ', 'https://regis.rmu.ac.th/registrar/class_info_1.asp?cmd=2&facultyid=all&acadyear=2568&semester=2&CAMPUSID=&LEVELID=&CLASSSET=&coursecode=7073401&coursename=', '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_id, acad_year, semester, section, schedule_raw) DO UPDATE SET
    course_code = EXCLUDED.course_code,
    course_group = EXCLUDED.course_group,
    instructors = EXCLUDED.instructors,
    seats_total = EXCLUDED.seats_total,
    seats_taken = EXCLUDED.seats_taken,
    seats_left = EXCLUDED.seats_left,
    status = EXCLUDED.status,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;

-- ── offering_patterns (45 แถว) ─────────────────────────────────────────
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1109901', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 7, "2567/2": 7, "2568/1": 4, "2568/2": 2}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1109902', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 11, "2567/2": 12, "2568/1": 10, "2568/2": 3}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1109903', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 4, "2567/2": 0, "2568/1": 2, "2568/2": 3}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1109904', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 7, "2567/2": 7, "2568/1": 6, "2568/2": 4}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1209901', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 5, "2567/2": 5, "2568/1": 1, "2568/2": 2}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1209902', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 4, "2567/2": 5, "2568/1": 5, "2568/2": 2}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1209903', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 8, "2567/2": 5, "2568/1": 3, "2568/2": 4}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1309901', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 4, "2567/2": 4, "2568/1": 2, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1309902', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 5, "2567/2": 4, "2568/1": 3, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1309903', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 4, "2567/2": 4, "2568/1": 2, "2568/2": 3}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1309904', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 7, "2567/2": 5, "2568/1": 4, "2568/2": 2}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1409901', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 4, "2567/2": 3, "2568/1": 2, "2568/2": 2}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1409902', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 5, "2567/2": 4, "2568/1": 3, "2568/2": 4}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1409903', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 5, "2567/2": 5, "2568/1": 2, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1409904', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 2, "2567/2": 2, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1409905', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 7, "2567/2": 6, "2568/1": 4, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1409906', TRUE, TRUE, FALSE, 4, 2, '{"2567/1": 2, "2567/2": 4, "2568/1": 0, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('1409907', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 5, "2567/2": 5, "2568/1": 4, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071101', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 2, "2567/2": 1, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071102', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 1, "2567/2": 1, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071103', FALSE, TRUE, FALSE, 4, 2, '{"2567/1": 0, "2567/2": 2, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071104', FALSE, TRUE, FALSE, 4, 2, '{"2567/1": 0, "2567/2": 2, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071105', FALSE, TRUE, FALSE, 4, 2, '{"2567/1": 0, "2567/2": 1, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071201', TRUE, FALSE, FALSE, 4, 2, '{"2567/1": 1, "2567/2": 0, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071202', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 1, "2567/2": 0, "2568/1": 1, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071203', FALSE, TRUE, FALSE, 4, 2, '{"2567/1": 0, "2567/2": 1, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071204', FALSE, TRUE, FALSE, 4, 2, '{"2567/1": 0, "2567/2": 1, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071301', TRUE, FALSE, FALSE, 4, 2, '{"2567/1": 1, "2567/2": 0, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071302', TRUE, FALSE, FALSE, 4, 2, '{"2567/1": 1, "2567/2": 0, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071303', FALSE, TRUE, FALSE, 4, 2, '{"2567/1": 0, "2567/2": 1, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071401', TRUE, FALSE, FALSE, 4, 2, '{"2567/1": 1, "2567/2": 0, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071402', FALSE, TRUE, FALSE, 4, 2, '{"2567/1": 0, "2567/2": 1, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071403', TRUE, FALSE, FALSE, 4, 2, '{"2567/1": 1, "2567/2": 0, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7071404', TRUE, FALSE, FALSE, 4, 2, '{"2567/1": 1, "2567/2": 0, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072102', TRUE, FALSE, FALSE, 4, 2, '{"2567/1": 1, "2567/2": 0, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072204', FALSE, TRUE, FALSE, 4, 1, '{"2567/1": 0, "2567/2": 1, "2568/1": 0, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072304', TRUE, FALSE, FALSE, 4, 1, '{"2567/1": 1, "2567/2": 0, "2568/1": 0, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072306', TRUE, TRUE, FALSE, 4, 2, '{"2567/1": 0, "2567/2": 1, "2568/1": 1, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072308', TRUE, FALSE, FALSE, 4, 1, '{"2567/1": 1, "2567/2": 0, "2568/1": 0, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072309', TRUE, FALSE, FALSE, 4, 1, '{"2567/1": 1, "2567/2": 0, "2568/1": 0, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072313', TRUE, FALSE, FALSE, 4, 1, '{"2567/1": 1, "2567/2": 0, "2568/1": 0, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072402', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 1, "2567/2": 1, "2568/1": 1, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072403', TRUE, TRUE, FALSE, 4, 4, '{"2567/1": 2, "2567/2": 3, "2568/1": 2, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7072405', TRUE, FALSE, FALSE, 4, 1, '{"2567/1": 1, "2567/2": 0, "2568/1": 0, "2568/2": 0}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;
INSERT INTO offering_patterns (course_code, opens_sem1, opens_sem2, opens_sem3, terms_observed, terms_found, detail, computed_at)
VALUES ('7073401', TRUE, TRUE, FALSE, 4, 3, '{"2567/1": 1, "2567/2": 1, "2568/1": 0, "2568/2": 1}'::jsonb, '2026-08-17T05:46:09+00:00')
ON CONFLICT (course_code) DO UPDATE SET
    opens_sem1 = EXCLUDED.opens_sem1,
    opens_sem2 = EXCLUDED.opens_sem2,
    opens_sem3 = EXCLUDED.opens_sem3,
    terms_observed = EXCLUDED.terms_observed,
    terms_found = EXCLUDED.terms_found,
    detail = EXCLUDED.detail,
    computed_at = EXCLUDED.computed_at;

-- ── documents (32 แถว) ─────────────────────────────────────────────────
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('registration', 'เอกสารขอเพิ่มรายวิชาเรียน', 'https://sci.rmu.ac.th/wp-content/uploads/2024/08/เอกสารขอเพิ่มรายวิชาเรียน.pdf', 'pdf', 'student', 'เพิ่มวิชา,เพิ่มรายวิชา,ขอเพิ่มวิชา,ลงวิชาเพิ่ม,แอดวิชา', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 124683, TRUE, '2026-08-17T07:08:00+00:00', '2026-08-17T07:08:00+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('registration', 'เอกสารขอยืนยันลงทะเบียนเรียน (ล่าช้า)', 'https://sci.rmu.ac.th/wp-content/uploads/2024/08/เอกสารขอยืนยันลงทะเบียนเรียนล่าช้า.pdf', 'pdf', 'student', 'ลงทะเบียนล่าช้า,ยืนยันลงทะเบียน,ลงทะเบียนช้า,ลืมลงทะเบียน', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 123257, TRUE, '2026-08-17T07:08:00+00:00', '2026-08-17T07:08:00+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('registration', 'เอกสารขอขยายหน่วยกิต', 'https://sci.rmu.ac.th/wp-content/uploads/2024/08/เอกสารขอขยายหน่วยกิต.pdf', 'pdf', 'student', 'ขยายหน่วยกิต,ลงเกินหน่วยกิต,หน่วยกิตเกิน,ลงเกิน', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 93509, TRUE, '2026-08-17T07:08:00+00:00', '2026-08-17T07:08:00+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('registration', 'เอกสารขอเปิดรายวิชาเรียน (ปรับปรุง 2568)', 'https://sci.rmu.ac.th/wp-content/uploads/2025/06/เอกสารขอเปิดรายวิชาเรียน-ปรับปรุง2568.pdf', 'pdf', 'student', 'ขอเปิดวิชา,เปิดรายวิชา,ขอเปิดรายวิชา,วิชาไม่เปิด', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 354778, TRUE, '2026-08-17T07:08:00+00:00', '2026-08-17T07:08:00+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '101 แบบคำขอกู้ยืมเงิน', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/101-แบบคำขอกู้ยืมเงิน.pdf', 'pdf', 'student', 'กู้ยืม,กยศ,แบบคำขอกู้,ขอกู้เงิน,กู้เรียน,เงินกู้', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 1889597, TRUE, '2026-08-17T07:08:01+00:00', '2026-08-17T07:08:01+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '102 หนังสือรับรองรายได้ครอบครัว (กยศ.)', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/102-หนังสือรับรองรายได้ครอบครัว-กยศ.pdf', 'pdf', 'student', 'รับรองรายได้,กยศ,รายได้ครอบครัว,หนังสือรับรองรายได้', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 254396, TRUE, '2026-08-17T07:08:01+00:00', '2026-08-17T07:08:01+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '103 หนังสือรับรองรายได้ครอบครัว (กรอ.)', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/102-หนังสือรับรองรายได้ครอบครัว-กรอ.pdf', 'pdf', 'student', 'รับรองรายได้,กรอ,รายได้ครอบครัว', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 32939, TRUE, '2026-08-17T07:08:01+00:00', '2026-08-17T07:08:01+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '104 หนังสือแสดงความคิดเห็นของอาจารย์ที่ปรึกษา', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/103-หนังสือแสดงความคิดเห็นของอาจารย์ที่ปรึกษา.pdf', 'pdf', 'student', 'อาจารย์ที่ปรึกษา,ความคิดเห็นอาจารย์,กยศ', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 460625, TRUE, '2026-08-17T07:08:01+00:00', '2026-08-17T07:08:01+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '105 บันทึกข้อตกลงต่อท้ายสัญญากู้ยืม', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/104-บันทึกข้อตกลงต่อท้ายสัญญากู้ยืม.doc', 'doc', 'student', 'สัญญากู้ยืม,บันทึกข้อตกลง,ต่อท้ายสัญญา', NULL, 'seed (คัดด้วยมือ)', 200, 'application/msword', 34304, TRUE, '2026-08-17T07:08:01+00:00', '2026-08-17T07:08:01+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '106 แบบรายงานข้อมูลผู้กู้ยืมเงิน', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/108-แบบรายงานข้อมูลผู้กู้ยืมเงิน.pdf', 'pdf', 'student', 'รายงานข้อมูลผู้กู้,ผู้กู้ยืม,กยศ', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 809870, TRUE, '2026-08-17T07:08:01+00:00', '2026-08-17T07:08:01+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '107 แบบฟอร์มบันทึกกิจกรรมจิตอาสา', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/107-แบบฟอร์มบันทึกกิจกรรมจิตอาสา.docx', 'docx', 'student', 'จิตอาสา,ชั่วโมงจิตอาสา,กิจกรรมจิตอาสา,กยศ ชั่วโมง', NULL, 'seed (คัดด้วยมือ)', 200, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 33038, TRUE, '2026-08-17T07:08:02+00:00', '2026-08-17T07:08:02+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '108 กยศ. แบบรายงานสถานภาพการศึกษา', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/กยศ-แบบรายงานสถานภาพการศึกษา.pdf', 'pdf', 'student', 'สถานภาพการศึกษา,กยศ,รายงานสถานภาพ', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 522117, TRUE, '2026-08-17T07:08:02+00:00', '2026-08-17T07:08:02+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '109 กรอ. แบบรายงานสถานภาพการศึกษา', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/กรอ-แบบรายงานสถานภาพการศึกษา.pdf', 'pdf', 'student', 'สถานภาพการศึกษา,กรอ,รายงานสถานภาพ', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 553911, TRUE, '2026-08-17T07:08:02+00:00', '2026-08-17T07:08:02+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '110 ตัวอย่างการทำสัญญา กยศ. กับธนาคารอิสลาม', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/105-ตัวอย่างการทำสัญญา-กยศ-กับธนาคารอิสลาม.pdf', 'pdf', 'student', 'ทำสัญญา,ธนาคารอิสลาม,กยศ,ตัวอย่างสัญญา', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 253069, TRUE, '2026-08-17T07:08:02+00:00', '2026-08-17T07:08:02+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', '111 ตัวอย่างการทำสัญญา กรอ. กับธนาคารอิสลาม', 'https://sci.rmu.ac.th/wp-content/uploads/2016/07/105-ตัวอย่างการทำสัญญา-กรอ-กับธนาคารอิสลาม.pdf', 'pdf', 'student', 'ทำสัญญา,ธนาคารอิสลาม,กรอ', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 104923, TRUE, '2026-08-17T07:08:02+00:00', '2026-08-17T07:08:02+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('internship', 'แบบฟอร์มตอบกลับจากหน่วยงานที่นักศึกษาออกฝึกประสบการณ์', 'https://sci.rmu.ac.th/wp-content/uploads/2016/12/ฟอร์ม-แบบตอบกลับ.doc', 'doc', 'student', 'ฝึกงาน,แบบตอบกลับ,หน่วยงานฝึกงาน,ตอบรับฝึกงาน', NULL, 'seed (คัดด้วยมือ)', 200, 'application/msword', 26112, TRUE, '2026-08-17T07:08:03+00:00', '2026-08-17T07:08:03+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('registration', 'หน้ารวมเอกสาร/คำร้องทั่วไป คณะวิทยาศาสตร์และเทคโนโลยี', 'https://sci.rmu.ac.th/?p=6289', 'page', 'student', 'คำร้อง,เอกสาร,แบบฟอร์ม,ดาวน์โหลดเอกสาร', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html; charset=UTF-8', NULL, TRUE, '2026-08-17T07:08:04+00:00', '2026-08-17T07:08:04+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('loan', 'หน้ารวมข้อมูลการกู้ยืมเงินเพื่อการศึกษา', 'https://sci.rmu.ac.th/?page_id=509', 'page', 'student', 'กู้ยืม,กยศ,กรอ,เงินกู้,กู้เรียน,ทุนกู้ยืม', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html; charset=UTF-8', NULL, TRUE, '2026-08-17T07:08:04+00:00', '2026-08-17T07:08:04+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('calendar', 'ปฏิทินการศึกษา (ระบบบริการการศึกษา)', 'https://regis.rmu.ac.th/registrar/calendar.asp', 'page', 'student', 'ปฏิทินการศึกษา,วันเปิดเทอม,วันลงทะเบียน,วันสอบ,เดดไลน์,ถอนวิชา', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html', NULL, TRUE, '2026-08-17T07:08:05+00:00', '2026-08-17T07:08:05+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('curriculum', 'โครงสร้างหลักสูตร (ระบบบริการการศึกษา)', 'https://regis.rmu.ac.th/registrar/program_info.asp', 'page', 'student', 'หลักสูตร,โครงสร้างหลักสูตร,หน่วยกิต,วิชาบังคับ', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html', NULL, TRUE, '2026-08-17T07:08:05+00:00', '2026-08-17T07:08:05+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('curriculum', 'ค้นหารายวิชาที่เปิดสอน (ระบบบริการการศึกษา)', 'https://regis.rmu.ac.th/registrar/class_info.asp', 'page', 'student', 'วิชาเปิดสอน,ตารางเรียน,ค้นหารายวิชา,หมู่เรียน,ที่นั่ง', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html', NULL, TRUE, '2026-08-17T07:08:05+00:00', '2026-08-17T07:08:05+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('curriculum', 'ระบบบริหารจัดการหลักสูตร (ข้อมูลหลักสูตรที่เปิดสอน)', 'https://promo-curriculum.rmu.ac.th', 'page', 'student', 'หลักสูตรที่เปิดสอน,สมัครเรียน,ข้อมูลหลักสูตร', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html; charset=UTF-8', 2727, TRUE, '2026-08-17T07:08:05+00:00', '2026-08-17T07:08:05+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('staff', 'ข้อมูลบุคลากรสายวิชาการ คณะเทคโนโลยีสารสนเทศ', 'https://www.itrmu.org/academic_staff.php', 'page', 'student', 'อาจารย์,ติดต่ออาจารย์,อีเมลอาจารย์,รายชื่ออาจารย์', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html; charset=UTF-8', 3474, TRUE, '2026-08-17T07:08:05+00:00', '2026-08-17T07:08:05+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('scholarship', 'ข่าวทุนการศึกษา คณะวิทยาศาสตร์และเทคโนโลยี', 'https://sci.rmu.ac.th/?cat=6', 'page', 'student', 'ทุนการศึกษา,ขอทุน,สมัครทุน,ทุนเรียน', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html; charset=UTF-8', NULL, TRUE, '2026-08-17T07:08:06+00:00', '2026-08-17T07:08:06+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('it_account', 'สำนักคอมพิวเตอร์ (อีเมลมหาวิทยาลัย / บัญชีเครือข่าย / WiFi)', 'https://cc.rmu.ac.th/', 'page', 'student', 'อีเมลมหาลัย,email,ขออีเมล,wifi,รหัสผ่านเน็ต,internet,เครือข่าย,อินเทอร์เน็ต', NULL, 'seed (คัดด้วยมือ)', 200, 'text/html; charset=UTF-8', 45160, TRUE, '2026-08-17T07:08:03+00:00', '2026-08-17T07:08:03+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('internship', 'แบบฟอร์มประวัตินักศึกษาออกฝึกประสบการณ์วิชาชีพ', 'https://sci.rmu.ac.th/wp-content/uploads/2016/12/%E0%B8%9F%E0%B8%AD%E0%B8%A3%E0%B9%8C%E0%B8%A1-%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%A7%E0%B8%B1%E0%B8%95%E0%B8%B4%E0%B8%99%E0%B8%B1%E0%B8%81%E0%B8%A8%E0%B8%B6%E0%B8%81%E0%B8%A9%E0%B8%B2.doc', 'doc', 'student', 'ฝึกงาน,ประวัตินักศึกษา,ฝึกประสบการณ์,ฟอร์มประวัติ', NULL, 'seed (คัดด้วยมือ)', 200, 'application/msword', 27648, TRUE, '2026-08-17T07:08:03+00:00', '2026-08-17T07:08:03+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('activity', 'ระบบกิจกรรมนักศึกษา (e-activity)', 'https://e-activity.rmu.ac.th', 'page', 'student', 'กิจกรรม,ชั่วโมงกิจกรรม,เก็บชั่วโมง,กิจกรรมนักศึกษา', NULL, 'seed (คัดด้วยมือ)', 500, 'text/html; charset=UTF-8', 2077, FALSE, '2026-08-17T07:08:06+00:00', '2026-08-17T07:08:06+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('exam_prep', 'เทคนิคการทำข้อสอบ TOEIC', 'https://sci.rmu.ac.th/wp-content/uploads/2018/06/3-เทคนิคการทำข้อสอบ-toeic.pdf', 'pdf', 'student', 'toeic,สอบภาษาอังกฤษ,เทคนิคสอบ,ข้อสอบอังกฤษ', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 483623, TRUE, '2026-08-17T07:08:06+00:00', '2026-08-17T07:08:06+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('exam_prep', 'แนวข้อสอบ IELTS', 'https://sci.rmu.ac.th/wp-content/uploads/2018/06/2-ข้อสอบ-ielts.pdf', 'pdf', 'student', 'ielts,สอบภาษาอังกฤษ,แนวข้อสอบ', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 1208715, TRUE, '2026-08-17T07:08:06+00:00', '2026-08-17T07:08:06+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('regulation', 'พ.ร.บ. คอมพิวเตอร์ ฉบับที่ 1 พ.ศ. 2550', 'https://sci.rmu.ac.th/wp-content/uploads/2022/03/พรบ.-ว่าด้วยการกระทำความผิดทางคอมพิวเตอร์-พ.ศ.-2550.pdf', 'pdf', 'student', 'พรบคอมพิวเตอร์,กฎหมายคอมพิวเตอร์,พรบ 2550', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 118710, TRUE, '2026-08-17T07:08:07+00:00', '2026-08-17T07:08:07+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('regulation', 'พ.ร.บ. คอมพิวเตอร์ ฉบับที่ 2 พ.ศ. 2560 (แก้ไขเพิ่มเติม)', 'https://sci.rmu.ac.th/wp-content/uploads/2022/03/พรบ-คอมพิวเตอร์-ฉบับที่-2-2560.pdf', 'pdf', 'student', 'พรบคอมพิวเตอร์,กฎหมายคอมพิวเตอร์,พรบ 2560', NULL, 'seed (คัดด้วยมือ)', 200, 'application/pdf', 116631, TRUE, '2026-08-17T07:08:07+00:00', '2026-08-17T07:08:07+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO documents (category, title, url, doc_type, audience, keywords, note, source_page, http_status, content_type, content_length, is_available, checked_at, scraped_at)
VALUES ('internship', 'แบบฟอร์มแจ้งเปลี่ยนระยะเวลาการออกฝึกประสบการณ์วิชาชีพ', 'https://sci.rmu.ac.th/wp-content/uploads/2016/12/%E0%B9%81%E0%B8%88%E0%B9%89%E0%B8%87%E0%B9%80%E0%B8%9B%E0%B8%A5%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%99%E0%B8%A3%E0%B8%B0%E0%B8%A2%E0%B8%B0%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%B2%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%AD%E0%B8%AD%E0%B8%81%E0%B8%9D%E0%B8%B6%E0%B8%81%E0%B8%AF1.docx', 'docx', 'student', 'ฝึกงาน,ฝึกประสบการณ์,เปลี่ยนวันฝึกงาน,เลื่อนฝึกงาน', NULL, 'seed (คัดด้วยมือ)', 200, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 92027, TRUE, '2026-08-17T07:08:03+00:00', '2026-08-17T07:08:03+00:00')
ON CONFLICT (url) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    doc_type = EXCLUDED.doc_type,
    audience = EXCLUDED.audience,
    keywords = EXCLUDED.keywords,
    note = EXCLUDED.note,
    source_page = EXCLUDED.source_page,
    http_status = EXCLUDED.http_status,
    content_type = EXCLUDED.content_type,
    content_length = EXCLUDED.content_length,
    is_available = EXCLUDED.is_available,
    checked_at = EXCLUDED.checked_at,
    scraped_at = EXCLUDED.scraped_at;

-- ── instructors (28 แถว) ───────────────────────────────────────────────
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('ผู้ช่วยศาสตราจารย์ ดร.ธรัช อารีราษฎร์', 'ธรัช อารีราษฎร์', 'ผู้ช่วยศาสตราจารย์ ดร', 'dr.tharach@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.อภิชาติ เหล็กดี', 'อภิชาติ เหล็กดี', 'อาจารย์ ดร', 'apichart.la@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.ธารีชล ดงสงคราม', 'ธารีชล ดงสงคราม', 'อาจารย์ ดร', 'kanjana.do@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.วีระพน ภานุรักษ์', 'วีระพน ภานุรักษ์', 'อาจารย์ ดร', 'panurag2562@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.เดือนเพ็ญ ภานุรักษ์', 'เดือนเพ็ญ ภานุรักษ์', 'อาจารย์ ดร', 'keroiloveu@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์บัณฑิต สุวรรณโท', 'บัณฑิต สุวรรณโท', 'อาจารย์', 'bundit_s@hotmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์วินัย โกหลำ', 'วินัย โกหลำ', 'อาจารย์', 'winaiko@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ภาสกร ธนศิระธรรม', 'ภาสกร ธนศิระธรรม', 'อาจารย์', 'passakorn.ta@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์มณีรัตน์ ผลประเสริฐ', 'มณีรัตน์ ผลประเสริฐ', 'อาจารย์', 'phonprasert@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ชเนตตี อินธิสิทธิ์', 'ชเนตตี อินธิสิทธิ์', 'อาจารย์', 'chanettee2011@hotmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์อิสรา ชื่นตา', 'อิสรา ชื่นตา', 'อาจารย์', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์สมร เหล็กกล้า', 'สมร เหล็กกล้า', 'อาจารย์', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('ผู้ช่วยศาสตราจารย์ ดร.ปิยะศักดิ์ ถีอาสนา', 'ปิยะศักดิ์ ถีอาสนา', 'ผู้ช่วยศาสตราจารย์ ดร', 'piyasakbadboy@hotmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('ผู้ช่วยศาสตราจารย์ ดร.ณัฐพงษ์ พระลับรักษา', 'ณัฐพงษ์ พระลับรักษา', 'ผู้ช่วยศาสตราจารย์ ดร', 'nuttapong.pr@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('ผู้ช่วยศาสตราจารย์ ดร.อภิดา รุณวาทย์', 'อภิดา รุณวาทย์', 'ผู้ช่วยศาสตราจารย์ ดร', 'apida.ru@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('ผู้ช่วยศาสตราจารย์พจน์ศิรินทร์ ลิมปินันทน์', 'พจน์ศิรินทร์ ลิมปินันทน์', 'ผู้ช่วยศาสตราจารย์', 'potsirin.li@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('ผู้ช่วยศาสตราจารย์นฤมล สธนเสาวภาคย์', 'นฤมล สธนเสาวภาคย์', 'ผู้ช่วยศาสตราจารย์', 'narumonintirak@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.ธวัชชัย สหพงษ์', 'ธวัชชัย สหพงษ์', 'อาจารย์ ดร', 'thawatchai.sa@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.กฤษดา หินเธาว์', 'กฤษดา หินเธาว์', 'อาจารย์ ดร', 'kritsada.hi@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.อุดมศักดิ์ พิมพ์พาศรี', 'อุดมศักดิ์ พิมพ์พาศรี', 'อาจารย์ ดร', 'udomsak.pi@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ธเนศ ยืนสุข', 'ธเนศ ยืนสุข', 'อาจารย์', 'thanet.y@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์กีรติ ทองเนตร', 'กีรติ ทองเนตร', 'อาจารย์', 'keerati.to@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์วรรณพร สารภักดิ์', 'วรรณพร สารภักดิ์', 'อาจารย์', 'ice.wannaporn@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('ผู้ช่วยศาสตราจารย์ ดร.ทิพวิมล ชมภูคำ', 'ทิพวิมล ชมภูคำ', 'ผู้ช่วยศาสตราจารย์ ดร', 'thipwimon.ch@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.ณพรรธนนท์ ทองปาน', 'ณพรรธนนท์ ทองปาน', 'อาจารย์ ดร', 'naphattanon.th@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจาร ดร.ณัฐพงศ์ ผลสยม', 'ณัฐพงศ์ ผลสยม', 'อาจาร ดร', 'nuttapong.po@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจาร ดร.ชนะชัย อวนวัง', 'ชนะชัย อวนวัง', 'อาจาร ดร', 'chanachai.eo@rmu.ac.th', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;
INSERT INTO instructors (full_name, name_normalized, title_prefix, email, phone, building, floor, room, office_hours, other_contact, manual_source, source_url, scraped_at)
VALUES ('อาจารย์ ดร.พัชรี ศรีพุทธา', 'พัชรี ศรีพุทธา', 'อาจารย์ ดร', 'sriputta29@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'https://www.itrmu.org/academic_staff.php', '2026-08-17T08:52:41+00:00')
ON CONFLICT (full_name) DO UPDATE SET
    name_normalized = EXCLUDED.name_normalized,
    title_prefix = EXCLUDED.title_prefix,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    building = EXCLUDED.building,
    floor = EXCLUDED.floor,
    room = EXCLUDED.room,
    office_hours = EXCLUDED.office_hours,
    other_contact = EXCLUDED.other_contact,
    manual_source = EXCLUDED.manual_source,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at;

-- prerequisites: ไม่มีข้อมูล (ข้าม)

-- curriculum_rules: ไม่มีข้อมูล (ข้าม)

-- ── instructor_affiliations (33 แถว) ──────────────────────────────
-- ใช้ SELECT id FROM instructors WHERE full_name = ...
-- เพราะ instructor_id เป็น IDENTITY ค่าจึงไม่ตรงกับฝั่ง SQLite
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน (MTA)', 'MTA', 'อาจารย์สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน', FALSE
  FROM instructors i WHERE i.full_name = 'ผู้ช่วยศาสตราจารย์ ดร.ณัฐพงษ์ พระลับรักษา'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล (CTD)', 'CTD', 'ประธานหลักสูตรเทคโนโลยีคอมพิวเตอร์และดิจิทัล', TRUE
  FROM instructors i WHERE i.full_name = 'ผู้ช่วยศาสตราจารย์ ดร.ทิพวิมล ชมภูคำ'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'ระดับปรัชญาดุษฎีบัณฑิต (ปร.ด.การจัดการเทคโนโลยี)', NULL, 'ประธานหลักสูตรระดับปรัชญาดุษฎีบัณฑิต', TRUE
  FROM instructors i WHERE i.full_name = 'ผู้ช่วยศาสตราจารย์ ดร.ธรัช อารีราษฎร์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'ระดับปริญญามหาบัณฑิต (วท.ม.การจัดการเทคโนโลยี)', NULL, 'อาจารย์ประจำหลักสูตร', FALSE
  FROM instructors i WHERE i.full_name = 'ผู้ช่วยศาสตราจารย์ ดร.ธรัช อารีราษฎร์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน (MTA)', 'MTA', 'ประธานหลักสูตรเทคโนโลยีมัลติมีเดียและแอนิเมชัน', TRUE
  FROM instructors i WHERE i.full_name = 'ผู้ช่วยศาสตราจารย์ ดร.ปิยะศักดิ์ ถีอาสนา'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน (MTA)', 'MTA', 'อาจารย์สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน', FALSE
  FROM instructors i WHERE i.full_name = 'ผู้ช่วยศาสตราจารย์ ดร.อภิดา รุณวาทย์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน (MTA)', 'MTA', 'อาจารย์สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน', FALSE
  FROM instructors i WHERE i.full_name = 'ผู้ช่วยศาสตราจารย์นฤมล สธนเสาวภาคย์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน (MTA)', 'MTA', 'อาจารย์สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน', FALSE
  FROM instructors i WHERE i.full_name = 'ผู้ช่วยศาสตราจารย์พจน์ศิรินทร์ ลิมปินันทน์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล (CTD)', 'CTD', 'อาจารย์สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจาร ดร.ชนะชัย อวนวัง'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล (CTD)', 'CTD', 'อาจารย์สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจาร ดร.ณัฐพงศ์ ผลสยม'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาการจัดการนวัตกรรมดิจิทัล (MDI)', 'MDI', 'ประธานหลักสูตรการจัดการโนโลยีดิจิทัล', TRUE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.กฤษดา หินเธาว์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล (CTD)', 'CTD', 'อาจารย์สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.ณพรรธนนท์ ทองปาน'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน (MTA)', 'MTA', 'อาจารย์สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.ธวัชชัย สหพงษ์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'ระดับปรัชญาดุษฎีบัณฑิต (ปร.ด.การจัดการเทคโนโลยี)', NULL, 'อาจารย์ประจำหลักสูตร', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.ธารีชล ดงสงคราม'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'ระดับปริญญามหาบัณฑิต (วท.ม.การจัดการเทคโนโลยี)', NULL, 'ประธานหลักสูตรระดับปริญญามหาบัณฑิต', TRUE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.ธารีชล ดงสงคราม'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน (MTA)', 'MTA', 'อาจารย์สาขาเทคโนโลยีมัลติมีเดียและแอนิเมชัน', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.ธารีชล ดงสงคราม'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล (CTD)', 'CTD', 'อาจารย์สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.พัชรี ศรีพุทธา'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'ประธานหลักสูตรเทคโนโลยีสารสนเทศ', TRUE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.วีระพน ภานุรักษ์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'ระดับปรัชญาดุษฎีบัณฑิต (ปร.ด.การจัดการเทคโนโลยี)', NULL, 'อาจารย์ประจำหลักสูตร', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.อภิชาติ เหล็กดี'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'ระดับปริญญามหาบัณฑิต (วท.ม.การจัดการเทคโนโลยี)', NULL, 'อาจารย์ประจำหลักสูตร', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.อภิชาติ เหล็กดี'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล (CTD)', 'CTD', 'อาจารย์สาขาเทคโนโลยีคอมพิวเตอร์และดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.อภิชาติ เหล็กดี'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาการจัดการนวัตกรรมดิจิทัล (MDI)', 'MDI', 'อาจารย์สาขาการจัดการโนโลยีดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.อุดมศักดิ์ พิมพ์พาศรี'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'อาจารย์สาขาเทคโนโลยีสารสนเทศ', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ ดร.เดือนเพ็ญ ภานุรักษ์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาการจัดการนวัตกรรมดิจิทัล (MDI)', 'MDI', 'อาจารย์สาขาการจัดการโนโลยีดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์กีรติ ทองเนตร'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'อาจารย์สาขาเทคโนโลยีสารสนเทศ', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ชเนตตี อินธิสิทธิ์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาการจัดการนวัตกรรมดิจิทัล (MDI)', 'MDI', 'อาจารย์สาขาการจัดการโนโลยีดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ธเนศ ยืนสุข'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'อาจารย์สาขาเทคโนโลยีสารสนเทศ', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์บัณฑิต สุวรรณโท'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'อาจารย์สาขาเทคโนโลยีสารสนเทศ', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์ภาสกร ธนศิระธรรม'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'อาจารย์สาขาเทคโนโลยีสารสนเทศ', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์มณีรัตน์ ผลประเสริฐ'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาการจัดการนวัตกรรมดิจิทัล (MDI)', 'MDI', 'อาจารย์สาขาการจัดการโนโลยีดิจิทัล', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์วรรณพร สารภักดิ์'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'อาจารย์สาขาเทคโนโลยีสารสนเทศ', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์วินัย โกหลำ'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'อาจารย์สาขาเทคโนโลยีสารสนเทศ', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์สมร เหล็กกล้า'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;
INSERT INTO instructor_affiliations (instructor_id, group_name, group_code, position, is_chair)
SELECT i.id, 'สาขาเทคโนโลยีสารสนเทศ (IT)', 'IT', 'อาจารย์สาขาเทคโนโลยีสารสนเทศ', FALSE
  FROM instructors i WHERE i.full_name = 'อาจารย์อิสรา ชื่นตา'
ON CONFLICT (instructor_id, group_name, position) DO UPDATE SET
    group_code = EXCLUDED.group_code,
    is_chair   = EXCLUDED.is_chair;

-- ── offering_slots (292 แถว) ────────────────────────────────────
-- lookup offering_id จาก natural key (course_id, ปี, เทอม, หมู่, ตาราง)
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '260401'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 260401'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0509'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360305'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '260401'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 260401'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0509'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360305'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '260401'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 260401'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0509'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 480, 680, '360305'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'WE08:00-11:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '040301'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 040301'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0509'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '360305'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'WE13:00-16:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '040303'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'TU13:00-16:20 040303'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0509'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '150801'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '6'
   AND o.schedule_raw = 'SU08:00-11:20 150801'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '040304'
  FROM offerings o
 WHERE o.course_id = 32701
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '6'
   AND o.schedule_raw = 'TU13:00-16:20 040304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350305'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350804'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0208'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0208'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350804'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN5007'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '10'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN5007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360304'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '10'
   AND o.schedule_raw = 'TU13:00-16:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '360303'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '11'
   AND o.schedule_raw = 'SA08:00-11:20 360303'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '11'
   AND o.schedule_raw = 'SU08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350305'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350804'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0208'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0208'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350804'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'SA08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350305'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350804'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0208'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0208'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0509'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350305'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0509'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350305'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'TU13:00-16:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0509'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '6'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '6'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360306'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '7'
   AND o.schedule_raw = 'TU13:00-16:20 360306'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350305'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '7'
   AND o.schedule_raw = 'TU13:00-16:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '7'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360305'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '8'
   AND o.schedule_raw = 'TU13:00-16:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350305'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '8'
   AND o.schedule_raw = 'TU13:00-16:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '8'
   AND o.schedule_raw = 'TU13:00-16:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '360407'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '9'
   AND o.schedule_raw = 'SA08:00-11:20 360407'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN5007'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '9'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN5007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360304'
  FROM offerings o
 WHERE o.course_id = 32702
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '9'
   AND o.schedule_raw = 'TU13:00-16:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360303'
  FROM offerings o
 WHERE o.course_id = 32703
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 360303'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32703
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360304'
  FROM offerings o
 WHERE o.course_id = 32703
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 980, 1180, '360302'
  FROM offerings o
 WHERE o.course_id = 32703
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU16:20-19:40 360302'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 980
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '260304'
  FROM offerings o
 WHERE o.course_id = 32703
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'SA08:00-11:20 260304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN5005'
  FROM offerings o
 WHERE o.course_id = 32703
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN5005'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4009'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4009'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4009'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4009'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360402'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'SU08:00-11:20 360402'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360408'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 360408'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360408'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 360408'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360305'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360302'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'SU08:00-11:20 360302'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360408'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'TU13:00-16:20 360408'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360305'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'TU13:00-16:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '360401'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '6'
   AND o.schedule_raw = 'SA08:00-11:20 360401'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '360305'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '6'
   AND o.schedule_raw = 'SA08:00-11:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 680, 880, '151006'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '6'
   AND o.schedule_raw = 'SU11:20-14:40 151006'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 680
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360304'
  FROM offerings o
 WHERE o.course_id = 32704
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '8'
   AND o.schedule_raw = 'SU08:00-11:20 360304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '070205'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 070205'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4007'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '260401'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 260401'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '260401'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 260401'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '260401'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 260401'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '070205'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 070205'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '070304'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 070304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '070205'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'SA08:00-11:20 070205'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '150801'
  FROM offerings o
 WHERE o.course_id = 32707
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'SA08:00-11:20 150801'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360306'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'SU08:00-11:20 360306'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350305'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4008'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4008'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 480, 680, '150410'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'WE08:00-11:20 150410'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350305'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 350305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4008'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4008'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 980, 1130, '360101'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU16:20-18:50 360101'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 980
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 480, 680, '150410'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'WE08:00-11:20 150410'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4009'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4009'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '360001'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'WE13:00-16:20 360001'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '38-IT0503'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 38-IT0503'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4009'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4009'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '360001'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'WE13:00-16:20 360001'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360408'
  FROM offerings o
 WHERE o.course_id = 32708
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'SU08:00-11:20 360408'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350803'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 350803'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350804'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360303'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 360303'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '160601'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 160601'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350803'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 350803'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350804'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360303'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 360303'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '160601'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 160601'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 980, 1180, '150410'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'SA16:20-19:40 150410'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 980
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360402'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 360402'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350804'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '360408'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 360408'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350804'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 350804'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360301'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'SU08:00-11:20 360301'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360302'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'SU08:00-11:20 360302'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '151303'
  FROM offerings o
 WHERE o.course_id = 32709
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '7'
   AND o.schedule_raw = 'SA08:00-11:20 151303'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '030204'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 030204'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '040101'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 040101'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '040101'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 040101'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '030204'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 030204'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '030204'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 030204'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '030202'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 030202'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350803'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 350803'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '260401'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 260401'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350803'
  FROM offerings o
 WHERE o.course_id = 32710
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 350803'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '030202'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 030202'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '030200'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 030200'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '030200'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 030200'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '030202'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 030202'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '030200'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 030200'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '030200'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 030200'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 880, 1080, '340601'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'SU14:40-18:00 340601'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 880
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '030202'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 030202'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '030200'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 030200'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '030202'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 030202'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '360305'
  FROM offerings o
 WHERE o.course_id = 32711
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'SU08:00-11:20 360305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4005'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4005'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4005'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4005'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4006'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4006'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4007'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '37-EN4007'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'SA08:00-11:20 37-EN4007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4005'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4005'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4005'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4005'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4006'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4006'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4006'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4006'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4006'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4006'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4006'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4006'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4006'
  FROM offerings o
 WHERE o.course_id = 32712
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4006'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '330402'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 330402'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '330201'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 330201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '330304'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 330304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '330304'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 330304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '330304'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'SA08:00-11:20 330304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '330403'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 330403'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '330302'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 330302'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '330302'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 330302'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '330304'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'SU08:00-11:20 330304'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '330402'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 330402'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '330201'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 330201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 880, 1080, '151004'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'SU14:40-18:00 151004'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 880
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '330403'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 330403'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '330403'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'SA08:00-11:20 330403'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '330201'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'SA08:00-11:20 330201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 680, 880, '151302'
  FROM offerings o
 WHERE o.course_id = 32713
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '6'
   AND o.schedule_raw = 'SA11:20-14:40 151302'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 680
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 880, 1080, '390601'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'SA14:40-18:00 390601'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 880
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '390502'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 390502'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '390502'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 390502'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '390502'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 390502'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '390622'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'SA08:00-11:20 390622'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '390617'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'SA08:00-11:20 390617'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '100308'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'SU08:00-11:20 100308'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '390502'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 390502'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '390509'
  FROM offerings o
 WHERE o.course_id = 32714
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'WE13:00-16:20 390509'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN6009'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN6009'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN6009'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN6009'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4008'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4008'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4008'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4008'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN5008'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN5008'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN6009'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN6009'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN5005'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN5005'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN4008'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN4008'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '37-EN4010'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'SA08:00-11:20 37-EN4010'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN6007'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN6007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN6010'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN6010'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '150705'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'SU08:00-11:20 150705'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN6007'
  FROM offerings o
 WHERE o.course_id = 32715
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN6007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '090201'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 090201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 630, '090305'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-10:30 090305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 630, '090201'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-10:30 090201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 630, '090305'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-10:30 090305'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '090201'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 090201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '090201'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 090201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '090201'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 090201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 930, '090201'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-15:30 090201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '090201'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 090201'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 930, '090203'
  FROM offerings o
 WHERE o.course_id = 32716
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-15:30 090203'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 480, 680, '120107'
  FROM offerings o
 WHERE o.course_id = 32717
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'FR08:00-11:20 120107'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '230101'
  FROM offerings o
 WHERE o.course_id = 32717
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 230101'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '120107'
  FROM offerings o
 WHERE o.course_id = 32717
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 120107'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '150701'
  FROM offerings o
 WHERE o.course_id = 32717
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 150701'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '120107'
  FROM offerings o
 WHERE o.course_id = 32717
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 120107'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '390409'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 390409'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '390409'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 390409'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '622'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU13:00-16:20 622'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '390409'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 390409'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '627'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 627'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '632'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU08:00-11:20 632'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '622'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'WE13:00-16:20 622'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '622'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'SU08:00-11:20 622'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '632'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 632'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '636'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 636'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '612'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'TU13:00-16:20 612'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '622'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'WE13:00-16:20 622'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 780, 980, '627'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '6'
   AND o.schedule_raw = 'SU13:00-16:20 627'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 480, 680, '612'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '6'
   AND o.schedule_raw = 'WE08:00-11:20 612'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '151302'
  FROM offerings o
 WHERE o.course_id = 32718
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '7'
   AND o.schedule_raw = 'SU08:00-11:20 151302'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '150801'
  FROM offerings o
 WHERE o.course_id = 32719
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 150801'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '150901-150903'
  FROM offerings o
 WHERE o.course_id = 32719
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 150901-150903'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '150803'
  FROM offerings o
 WHERE o.course_id = 32719
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 150803'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 980, 1180, '37-EN3003'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'SU16:20-19:40 37-EN3003'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 980
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN4008'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN4008'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN6007'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN6007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '37-EN5007'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TU08:00-11:20 37-EN5007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '090202'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU08:00-11:20 090202'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '360407'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'TU13:00-16:20 360407'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '350701'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 350701'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN6007'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN6007'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '150701'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '3'
   AND o.schedule_raw = 'TU13:00-16:20 150701'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 480, 680, '350701'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU08:00-11:20 350701'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '37-EN6008'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 37-EN6008'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TU', 780, 980, '150703'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '4'
   AND o.schedule_raw = 'TU13:00-16:20 150703'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TU'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '151302'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '5'
   AND o.schedule_raw = 'SA08:00-11:20 151302'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 880, 1080, '150801'
  FROM offerings o
 WHERE o.course_id = 32720
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '5'
   AND o.schedule_raw = 'SA14:40-18:00 150801'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 880
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 530, 730, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 39105
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO08:50-12:10 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0204'
  FROM offerings o
 WHERE o.course_id = 39186
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0204'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 480, 680, '38-IT0110'
  FROM offerings o
 WHERE o.course_id = 39186
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'SA08:00-11:20 38-IT0110'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 530, 730, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 39105
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'MO08:50-12:10 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 39881
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0309'
  FROM offerings o
 WHERE o.course_id = 39881
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0309'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SA', 680, 880, '38-IT0110'
  FROM offerings o
 WHERE o.course_id = 39187
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'SA11:20-14:40 38-IT0110'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SA'
         AND x.start_min = 680
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 530, 730, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 40154
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'FR08:50-12:10 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 530, 730, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 40154
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TH08:50-12:10 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 480, 680, '38-IT0110'
  FROM offerings o
 WHERE o.course_id = 39188
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'SU08:00-11:20 38-IT0110'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 780, 980, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 40155
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'FR13:00-16:20 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 780, 980, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 40155
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TH13:00-16:20 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'SU', 680, 880, '38-IT0110'
  FROM offerings o
 WHERE o.course_id = 39189
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'SU11:20-14:40 38-IT0110'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'SU'
         AND x.start_min = 680
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 530, 730, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 40156
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'MO08:50-12:10 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 40156
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 39224
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 530, 730, '38-IT0309'
  FROM offerings o
 WHERE o.course_id = 39224
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TH08:50-12:10 38-IT0309'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 780, 980, '38-IT0309'
  FROM offerings o
 WHERE o.course_id = 41202
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'FR13:00-16:20 38-IT0309'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 41202
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 530, 730, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 41181
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'MO08:50-12:10 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 780, 980, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 41181
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TH13:00-16:20 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41203
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 530, 730, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41203
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TH08:50-12:10 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 530, 730, '38-IT0309'
  FROM offerings o
 WHERE o.course_id = 41204
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'FR08:50-12:10 38-IT0309'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0309'
  FROM offerings o
 WHERE o.course_id = 41204
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0309'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41205
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'FR13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 530, 730, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41205
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TH08:50-12:10 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 530, 730, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41206
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'MO08:50-12:10 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 530, 730, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41206
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TH08:50-12:10 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 530, 730, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 39231
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO08:50-12:10 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 530, 730, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 39231
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'WE08:50-12:10 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 730, 1030, '38-IT0309'
  FROM offerings o
 WHERE o.course_id = 41209
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'MO12:10-17:10 38-IT0309'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 730
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 730, 1030, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 41209
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TH12:10-17:10 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 730
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 780, 980, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 39233
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'FR13:00-16:20 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 1130, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41210
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-18:50 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 530, 730, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 39234
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'MO08:50-12:10 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 530, 730, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 39236
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'FR08:50-12:10 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 480, 680, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 39236
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'WE08:00-11:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 480
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 39239
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'TH13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'FR', 530, 730, '38-IT0311'
  FROM offerings o
 WHERE o.course_id = 41216
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'FR08:50-12:10 38-IT0311'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'FR'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'MO', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41218
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'MO13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'MO'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 41218
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TH13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 530, 730, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 39248
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TH08:50-12:10 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 530
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 780, 980, '38-IT0309'
  FROM offerings o
 WHERE o.course_id = 41222
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TH13:00-16:20 38-IT0309'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0502'
  FROM offerings o
 WHERE o.course_id = 39253
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0502'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 39214
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 39214
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 39214
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0313'
  FROM offerings o
 WHERE o.course_id = 39214
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0313'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 22956
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 22956
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 22956
   AND o.acad_year = 2568
   AND o.semester = 2
   AND o.section = '1'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 22956
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 22956
   AND o.acad_year = 2567
   AND o.semester = 2
   AND o.section = '2'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'WE', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 22956
   AND o.acad_year = 2568
   AND o.semester = 1
   AND o.section = '2'
   AND o.schedule_raw = 'WE13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'WE'
         AND x.start_min = 780
  );
INSERT INTO offering_slots (offering_id, day_code, start_min, end_min, room)
SELECT o.id, 'TH', 780, 980, '38-IT0310'
  FROM offerings o
 WHERE o.course_id = 39260
   AND o.acad_year = 2567
   AND o.semester = 1
   AND o.section = '1'
   AND o.schedule_raw = 'TH13:00-16:20 38-IT0310'
  AND NOT EXISTS (
      SELECT 1 FROM offering_slots x
       WHERE x.offering_id = o.id
         AND x.day_code = 'TH'
         AND x.start_min = 780
  );

COMMIT;
