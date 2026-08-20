"""
Demo script for Registration Advisor Chatbot
Shows example usage without requiring user input
"""
from chatbot_registration_advisor import RegistrationAdvisorBot

def demo():
    """Demonstrate chatbot capabilities"""
    print("=" * 70)
    print("🤖 DEMO: ระบบแนะนำการลงทะเบียน")
    print("=" * 70)

    # Initialize bot
    bot = RegistrationAdvisorBot('complete_student_data.json')

    # Demo 1: Show summary
    print("\n" + "="*70)
    print("📊 DEMO 1: แสดงสรุปข้อมูล")
    print("="*70)
    print(bot.get_summary())

    # Demo 2: Show incomplete courses
    print("\n" + "="*70)
    print("📋 DEMO 2: แสดงวิชาที่ยังไม่ผ่าน")
    print("="*70)
    print(bot.get_incomplete_courses())

    # Demo 3: Search for courses
    print("\n" + "="*70)
    print("🔍 DEMO 3: ค้นหาวิชา 'โครงงาน'")
    print("="*70)
    print(bot.search_course('โครงงาน'))

    # Demo 4: Get course details
    print("\n" + "="*70)
    print("📖 DEMO 4: รายละเอียดวิชา 7071403-3")
    print("="*70)
    print(bot.get_course_details('7071403-3'))

    # Demo 5: Get recommendations
    print("\n" + "="*70)
    print("💡 DEMO 5: คำแนะนำการลงทะเบียน")
    print("="*70)
    print(bot.recommend_registration())

    # Demo 6: Search completed courses
    print("\n" + "="*70)
    print("🔍 DEMO 6: ค้นหาวิชา 'ดิจิทัล'")
    print("="*70)
    print(bot.search_course('ดิจิทัล'))

    print("\n" + "="*70)
    print("✅ DEMO เสร็จสิ้น")
    print("="*70)
    print("\n💡 วิธีใช้งานจริง:")
    print("   python chatbot_registration_advisor.py")
    print("\n   แล้วพิมพ์คำสั่ง เช่น:")
    print("   • สรุป")
    print("   • ยังไม่ผ่าน")
    print("   • ค้นหา โครงงาน")
    print("   • รายละเอียด 7071403-3")
    print("   • แนะนำ")
    print("   • ออก")

if __name__ == "__main__":
    try:
        demo()
    except FileNotFoundError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
