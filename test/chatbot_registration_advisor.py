import json
import os
import re
from typing import List, Dict

# ไฟล์ complete_student_data.json ของจริงถูกลบออกจาก repo แล้วตาม PDPA
# (มีชื่อ-นามสกุลจริงและเกรดจริงของนักศึกษา) ถ้าจะทดลองรันต้องเตรียมไฟล์ของตัวเอง
DATA_FILE_MISSING_MSG = """ไม่พบไฟล์ข้อมูลนักศึกษา: {path}
ไฟล์ข้อมูลจริงถูกลบออกจาก repo แล้วตาม PDPA (มีชื่อจริงและเกรดจริงของนักศึกษา)
ถ้าต้องการทดลองรัน ให้สร้างไฟล์ JSON โครงสร้างเดิมขึ้นมาเอง
(studentId, studentName, program, enrolledCourses[...])"""

class RegistrationAdvisorBot:
    def __init__(self, data_file: str):
        """Initialize chatbot with student data"""
        if not os.path.exists(data_file):
            raise FileNotFoundError(DATA_FILE_MISSING_MSG.format(path=data_file))

        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.student_id = self.data['studentId']
        self.student_name = self.data['studentName']
        self.program = self.data['program']
        self.courses = self.data['enrolledCourses']

        # Separate completed and incomplete courses
        self.completed = [c for c in self.courses if c['completed']]
        self.incomplete = [c for c in self.courses if not c['completed']]

    def get_summary(self) -> str:
        """Get student summary"""
        total = len(self.courses)
        completed = len(self.completed)
        remaining = len(self.incomplete)

        summary = f"""
📊 สรุปข้อมูลการเรียน
---------------------------------
👤 รหัสนักศึกษา: {self.student_id}
📝 ชื่อ: {self.student_name}
🎓 สาขา: {self.program}

📚 สถานะการลงทะเบียน:
   • วิชาทั้งหมด: {total} วิชา
   • ผ่านแล้ว: {completed} วิชา
   • ยังไม่ผ่าน/ยังไม่ได้ลง: {remaining} วิชา
"""
        return summary

    def get_incomplete_courses(self) -> str:
        """List incomplete courses"""
        if not self.incomplete:
            return "✅ คุณผ่านทุกวิชาแล้ว!"

        result = "\n📋 วิชาที่ยังต้องลง/ยังไม่ผ่าน:\n"
        result += "-" * 50 + "\n"

        for i, course in enumerate(self.incomplete, 1):
            result += f"{i}. {course['courseCode']} - {course['courseName']}\n"
            result += f"   หน่วยกิต: {course['credits']}\n\n"

        return result

    def search_course(self, keyword: str) -> str:
        """Search for courses by keyword"""
        keyword = keyword.lower()
        matches = []

        for course in self.courses:
            if (keyword in course['courseCode'].lower() or
                keyword in course['courseName'].lower()):
                matches.append(course)

        if not matches:
            return f"❌ ไม่พบวิชาที่ตรงกับ '{keyword}'"

        result = f"\n🔍 ผลการค้นหา '{keyword}':\n"
        result += "-" * 50 + "\n"

        for course in matches:
            status = "✅ ผ่านแล้ว" if course['completed'] else "❌ ยังไม่ผ่าน"
            result += f"• {course['courseCode']} - {course['courseName']}\n"
            result += f"  หน่วยกิต: {course['credits']}\n"
            result += f"  สถานะ: {status}\n"
            if course['completed']:
                result += f"  เกรด: {course['grade']}\n"
            result += "\n"

        return result

    def get_course_details(self, course_code: str) -> str:
        """Get details of a specific course"""
        course_code = course_code.strip()

        for course in self.courses:
            if course['courseCode'] == course_code:
                status = "✅ ผ่านแล้ว" if course['completed'] else "❌ ยังไม่ผ่าน"

                details = f"\n📖 รายละเอียดวิชา\n"
                details += "-" * 50 + "\n"
                details += f"รหัสวิชา: {course['courseCode']}\n"
                details += f"ชื่อวิชา: {course['courseName']}\n"
                details += f"หน่วยกิต: {course['credits']}\n"
                details += f"สถานะ: {status}\n"

                if course['completed']:
                    details += f"เกรด: {course['grade']}\n"
                    details += f"ภาคการศึกษา: {course['semester']}\n"
                else:
                    details += f"⚠️ วิชานี้ยังไม่ได้ลงหรือยังไม่ผ่าน\n"

                return details

        return f"❌ ไม่พบวิชา {course_code} ในระบบ"

    def recommend_registration(self) -> str:
        """Recommend courses for next registration"""
        if not self.incomplete:
            return "✅ คุณผ่านทุกวิชาแล้ว ไม่มีวิชาที่ต้องลงเพิ่ม"

        result = "\n💡 แนะนำการลงทะเบียนภาคต่อไป:\n"
        result += "-" * 50 + "\n"
        result += f"คุณมีวิชาที่ยังไม่ผ่าน {len(self.incomplete)} วิชา\n\n"
        result += "📌 วิชาที่แนะนำให้ลงในภาคต่อไป:\n\n"

        # Prioritize based on course code patterns
        # 7071xxx = core courses
        # 7072xxx = elective courses

        core_courses = [c for c in self.incomplete if c['courseCode'].startswith('7071')]
        elective_courses = [c for c in self.incomplete if c['courseCode'].startswith('7072')]
        gen_ed = [c for c in self.incomplete if not (c['courseCode'].startswith('707'))]

        if core_courses:
            result += "🔴 วิชาหลัก (ควรลงก่อน):\n"
            for course in core_courses:
                result += f"   • {course['courseCode']} - {course['courseName']}\n"
            result += "\n"

        if elective_courses:
            result += "🟡 วิชาเลือก:\n"
            for course in elective_courses:
                result += f"   • {course['courseCode']} - {course['courseName']}\n"
            result += "\n"

        if gen_ed:
            result += "🟢 วิชาศึกษาทั่วไป:\n"
            for course in gen_ed:
                result += f"   • {course['courseCode']} - {course['courseName']}\n"

        return result

    def chat(self):
        """Main chat loop"""
        print("=" * 60)
        print("🤖 ระบบแนะนำการลงทะเบียน - มหาวิทยาลัยราชมงคล")
        print("=" * 60)
        print(self.get_summary())
        print("\n💬 พิมพ์คำสั่ง:")
        print("   • 'สรุป' - ดูสรุปข้อมูลการเรียน")
        print("   • 'ยังไม่ผ่าน' - ดูวิชาที่ยังไม่ผ่าน")
        print("   • 'ค้นหา <คำค้น>' - ค้นหาวิชา")
        print("   • 'รายละเอียด <รหัสวิชา>' - ดูรายละเอียดวิชา")
        print("   • 'แนะนำ' - รับคำแนะนำการลงทะเบียน")
        print("   • 'ออก' - ออกจากระบบ")
        print("-" * 60)

        while True:
            user_input = input("\n👤 คุณ: ").strip()

            if not user_input:
                continue

            # Exit commands
            if user_input.lower() in ['ออก', 'exit', 'quit', 'bye']:
                print("\n👋 ขอบคุณที่ใช้บริการ สวัสดีครับ!")
                break

            # Summary
            elif 'สรุป' in user_input or 'summary' in user_input.lower():
                print(self.get_summary())

            # Incomplete courses
            elif 'ยังไม่ผ่าน' in user_input or 'incomplete' in user_input.lower():
                print(self.get_incomplete_courses())

            # Search
            elif user_input.startswith('ค้นหา') or user_input.lower().startswith('search'):
                keyword = user_input.replace('ค้นหา', '').replace('search', '').strip()
                if keyword:
                    print(self.search_course(keyword))
                else:
                    print("❌ กรุณาระบุคำค้นหา เช่น 'ค้นหา โครงงาน'")

            # Course details
            elif user_input.startswith('รายละเอียด') or user_input.lower().startswith('details'):
                course_code = user_input.replace('รายละเอียด', '').replace('details', '').strip()
                if course_code:
                    print(self.get_course_details(course_code))
                else:
                    print("❌ กรุณาระบุรหัสวิชา เช่น 'รายละเอียด 7071101-3'")

            # Recommendations
            elif 'แนะนำ' in user_input or 'recommend' in user_input.lower():
                print(self.recommend_registration())

            # Help
            elif 'help' in user_input.lower() or 'ช่วย' in user_input:
                print("\n📚 คำสั่งที่ใช้ได้:")
                print("   • สรุป - ดูสรุปข้อมูล")
                print("   • ยังไม่ผ่าน - ดูวิชาที่ยังไม่ผ่าน")
                print("   • ค้นหา <คำค้น> - ค้นหาวิชา")
                print("   • รายละเอียด <รหัสวิชา> - ดูรายละเอียดวิชา")
                print("   • แนะนำ - รับคำแนะนำการลงทะเบียน")
                print("   • ออก - ออกจากระบบ")

            else:
                print("❓ ไม่เข้าใจคำสั่ง พิมพ์ 'help' เพื่อดูคำสั่งที่ใช้ได้")


if __name__ == "__main__":
    try:
        bot = RegistrationAdvisorBot('complete_student_data.json')
        bot.chat()
    except FileNotFoundError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
