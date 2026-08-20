"""
สคริปต์ดึงข้อมูลจากระบบทะเบียน RMU โดย login ด้วยรหัสผ่านของนักศึกษา

หมายเหตุ: ไฟล์นี้เป็นของแนวทางเดิม (ให้นักศึกษากรอกรหัสผ่านระบบทะเบียน)
ซึ่งโปรเจกต์เลิกใช้ไปแล้ว และเปลี่ยนไปใช้ Plan B (ไม่ขอรหัสผ่านจากนักศึกษา)
เก็บไฟล์นี้ไว้เพื่ออ้างอิงเท่านั้น ไม่ได้ใช้งานจริง

credential ของจริงถูกถอดออกแล้วตาม PDPA ถ้าจะทดลองรันต้องส่งค่าผ่าน
environment variable RMU_STUDENT_ID / RMU_PASSWORD เอง
"""
import os
import requests
from bs4 import BeautifulSoup
import json
import re

class RMUScraper:
    def __init__(self, student_id, password):
        self.student_id = student_id
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://regis.rmu.ac.th/registrar"
        self.student_data = {
            'student_id': student_id,
            'student_name': '',
            'program': '',
            'grades': [],
            'curriculum': [],
            'graduation_status': {}
        }

    def login(self):
        """Login to RMU registrar system"""
        login_url = f"{self.base_url}/login.asp"

        # Get initial page
        response = self.session.get(login_url)

        # Post login credentials
        login_data = {
            'txtUsername': self.student_id,
            'txtPassword': self.password,
            'Submit': 'เข้าสู่ระบบ'
        }

        response = self.session.post(login_url, data=login_data)

        if 'student.asp' in response.url or response.status_code == 200:
            print(f"[+] Login successful for {self.student_id}")
            return True
        else:
            print(f"[-] Login failed")
            return False

    def get_grades(self):
        """Scrape grade data"""
        grades_url = f"{self.base_url}/grade.asp"
        response = self.session.get(grades_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all tables
        tables = soup.find_all('table')
        grades = []

        for table in tables:
            rows = table.find_all('tr')
            current_semester = ''

            for row in rows:
                cells = row.find_all('td')
                text = row.get_text(strip=True)

                # Check if semester header
                if 'ภาคการศึกษา' in text or 'ปีการศึกษา' in text:
                    current_semester = text

                # Check if course row
                if len(cells) >= 5:
                    course_code = cells[0].get_text(strip=True)

                    # Validate course code format
                    if re.match(r'^\d{7}-\d', course_code):
                        course_name = cells[1].get_text(strip=True)
                        credits = cells[2].get_text(strip=True)
                        grade = cells[3].get_text(strip=True)

                        grades.append({
                            'semester': current_semester,
                            'course_code': course_code,
                            'course_name': course_name,
                            'credits': credits,
                            'grade': grade
                        })

        self.student_data['grades'] = grades
        print(f"[+] Found {len(grades)} course grades")
        return grades

    def get_curriculum(self):
        """Scrape curriculum/study plan"""
        curriculum_url = f"{self.base_url}/Student_Studyplan.asp"
        response = self.session.get(curriculum_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        tables = soup.find_all('table')
        curriculum = []

        for table in tables:
            rows = table.find_all('tr')
            current_year = ''

            for row in rows:
                cells = row.find_all('td')
                text = row.get_text(strip=True)

                # Check if year header
                if 'ปีการศึกษา' in text:
                    current_year = re.sub(r'ปีการศึกษา\s*', '', text).strip()

                # Check if course row
                if len(cells) >= 3:
                    course_code = cells[0].get_text(strip=True)

                    if re.match(r'^\d{7}-\d', course_code):
                        course_name_full = cells[1].get_text(separator='\n', strip=True)
                        course_name_parts = course_name_full.split('\n')
                        course_name_th = course_name_parts[0] if len(course_name_parts) > 0 else ''
                        course_name_en = course_name_parts[1] if len(course_name_parts) > 1 else ''
                        credits = cells[2].get_text(strip=True)

                        curriculum.append({
                            'year': current_year,
                            'course_code': course_code,
                            'course_name_th': course_name_th,
                            'course_name_en': course_name_en,
                            'credits': credits
                        })

        self.student_data['curriculum'] = curriculum
        print(f"[+] Found {len(curriculum)} courses in curriculum")
        return curriculum

    def get_graduation_check(self):
        """Scrape graduation requirements check"""
        grad_url = f"{self.base_url}/graduate_check.asp"
        response = self.session.get(grad_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract summary data
        text_content = soup.get_text()

        graduation_status = {}

        # Try to extract total credits
        credits_match = re.search(r'หน่วยกิตสะสม[^\d]*(\d+\.?\d*)', text_content)
        if credits_match:
            graduation_status['total_credits'] = float(credits_match.group(1))

        # Try to extract GPA
        gpa_match = re.search(r'เกรดเฉลี่ย[^\d]*(\d+\.?\d*)', text_content)
        if gpa_match:
            graduation_status['gpa'] = float(gpa_match.group(1))

        self.student_data['graduation_status'] = graduation_status
        print(f"[+] Graduation status extracted")
        return graduation_status

    def get_student_info(self):
        """Extract student name and program from main page"""
        main_url = f"{self.base_url}/student.asp"
        response = self.session.get(main_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        text = soup.get_text()

        # Extract student name
        name_match = re.search(r'\d{12}\s*:\s*(.+?)(?:\n|$)', text)
        if name_match:
            self.student_data['student_name'] = name_match.group(1).strip()
            print(f"[+] Student: {self.student_data['student_name']}")

    def scrape_all(self):
        """Main scraping function"""
        print("[*] Starting RMU Registrar scraper...")

        if not self.login():
            return None

        self.get_student_info()
        self.get_grades()
        self.get_curriculum()
        self.get_graduation_check()

        print("[+] Scraping completed!")
        return self.student_data

    def save_to_json(self, filename='student_data.json'):
        """Save scraped data to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.student_data, f, ensure_ascii=False, indent=2)
        print(f"[+] Data saved to {filename}")


if __name__ == "__main__":
    # credential ของจริงถูกถอดออกแล้ว (PDPA) ให้อ่านจาก environment variable เท่านั้น
    # ตัวอย่าง: RMU_STUDENT_ID=xxxx RMU_PASSWORD=yyyy python rmu_scraper.py
    STUDENT_ID = os.environ.get('RMU_STUDENT_ID', 'REPLACE_WITH_STUDENT_ID')
    PASSWORD = os.environ.get('RMU_PASSWORD', 'REPLACE_WITH_PASSWORD')

    if STUDENT_ID.startswith('REPLACE_WITH') or PASSWORD.startswith('REPLACE_WITH'):
        print("[-] ยังไม่ได้ตั้งค่า RMU_STUDENT_ID / RMU_PASSWORD ใน environment variable")
        print("[-] สคริปต์นี้เป็นโค้ดเก่าที่เลิกใช้แล้ว เก็บไว้เพื่ออ้างอิงเท่านั้น")
        raise SystemExit(1)

    scraper = RMUScraper(STUDENT_ID, PASSWORD)
    data = scraper.scrape_all()

    if data:
        scraper.save_to_json('rmu_student_data.json')

        # Print summary
        print("\n=== SUMMARY ===")
        print(f"Student: {data['student_name']}")
        print(f"Courses taken: {len(data['grades'])}")
        print(f"Curriculum courses: {len(data['curriculum'])}")
        if 'total_credits' in data['graduation_status']:
            print(f"Total credits: {data['graduation_status']['total_credits']}")
