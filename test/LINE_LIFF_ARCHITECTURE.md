# LINE LIFF Architecture for RMU Registration Advisor

## Overview
ใช้ LINE Rich Menu + LIFF (LINE Frontend Framework) ให้ user login เอง แล้ว backend เก็บ session และดึงข้อมูลจาก RMU registrar มาวิเคราะห์

---

## Architecture Flow

```
[User] 
  ↓ กด Rich Menu "เข้าสู่ระบบ"
[LINE LIFF Web Page]
  ↓ แสดง login form (ID + Password)
  ↓ User กรอก credentials
[Your Backend API]
  ↓ รับ ID + password
  ↓ Login ไปที่ RMU registrar
  ↓ ได้ session cookie/token
  ↓ ดึงข้อมูล (grades, curriculum)
  ↓ เก็บ session + data ใน database
  ↓ Return success to LIFF
[LIFF]
  ↓ แสดง "เข้าสู่ระบบสำเร็จ"
  ↓ Close LIFF
[User]
  ↓ พิมพ์ใน LINE chat "แนะนำการลงทะเบียน"
[Your Backend]
  ↓ เช็ค session ยังใช้ได้มั้ย
  ↓ ถ้าใช้ได้ → ดึง cached data
  ↓ ถ้าหมดอายุ → บอกให้ login ใหม่
  ↓ ส่งข้อมูลไป AI วิเคราะห์
  ↓ ตอบกลับใน LINE chat
```

---

## Tech Stack

### Required Components
1. **Frontend**: LIFF (LINE Frontend Framework)
2. **Backend**: Python Flask/FastAPI
3. **Cache/Session Store**: Redis
4. **LINE Bot**: LINE Messaging API
5. **AI**: Claude API / OpenAI

---

## Implementation

### 1. Frontend (LIFF)

**File**: `liff-login.html`

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เข้าสู่ระบบ RMU</title>
    <script src="https://static.line-scdn.net/liff/edge/2/sdk.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h2 {
            text-align: center;
            color: #333;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #06c755;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background: #05b34a;
        }
        .error {
            color: red;
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>เข้าสู่ระบบ RMU</h2>
        <form id="loginForm">
            <input type="text" id="studentId" placeholder="รหัสนักศึกษา" required>
            <input type="password" id="password" placeholder="รหัสผ่าน" required>
            <button type="submit">เข้าสู่ระบบ</button>
        </form>
        <div id="error" class="error"></div>
    </div>

    <script>
        liff.init({ liffId: 'YOUR_LIFF_ID' }).then(() => {
            document.getElementById('loginForm').onsubmit = async (e) => {
                e.preventDefault();
                
                const studentId = document.getElementById('studentId').value;
                const password = document.getElementById('password').value;
                const userId = liff.getContext().userId; // LINE user ID
                
                document.getElementById('error').textContent = 'กำลังเข้าสู่ระบบ...';
                
                try {
                    // ส่งไป backend
                    const response = await fetch('https://your-backend.com/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ userId, studentId, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok && data.success) {
                        alert('เข้าสู่ระบบสำเร็จ!');
                        liff.closeWindow();
                    } else {
                        document.getElementById('error').textContent = 
                            data.message || 'เข้าสู่ระบบไม่สำเร็จ กรุณาตรวจสอบรหัสผ่าน';
                    }
                } catch (error) {
                    document.getElementById('error').textContent = 
                        'เกิดข้อผิดพลาด: ' + error.message;
                }
            };
        }).catch(error => {
            console.error('LIFF initialization failed', error);
            document.getElementById('error').textContent = 'ไม่สามารถเริ่มต้น LIFF ได้';
        });
    </script>
</body>
</html>
```

---

### 2. Backend API (Python Flask)

**File**: `app.py`

```python
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import redis
import json
from datetime import timedelta

app = Flask(__name__)

# Redis client for session storage
redis_client = redis.Redis(
    host='localhost', 
    port=6379, 
    decode_responses=True,
    password='your-redis-password'  # ใส่ password ด้วย
)

SESSION_EXPIRE = 3600  # 1 hour

class RMUSession:
    """Handle RMU registrar session"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://regis.rmu.ac.th/registrar"
    
    def login(self, student_id, password):
        """Login and return session cookies"""
        try:
            response = self.session.post(
                f"{self.base_url}/login.asp",
                data={
                    'txtUsername': student_id,
                    'txtPassword': password,
                    'Submit': 'เข้าสู่ระบบ'
                },
                timeout=10
            )
            
            # Check if login successful
            if response.status_code == 200 and 'student.asp' in response.url:
                cookies = self.session.cookies.get_dict()
                return cookies
            
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    def restore_session(self, cookies):
        """Restore session from cookies"""
        self.session.cookies.update(cookies)
    
    def get_grades(self):
        """Fetch grades data"""
        try:
            response = self.session.get(f"{self.base_url}/grade.asp", timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse grade table
            grades = []
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        course_code = cells[0].get_text(strip=True)
                        if course_code and course_code[0].isdigit():
                            grades.append({
                                'code': course_code,
                                'name': cells[1].get_text(strip=True),
                                'credits': cells[2].get_text(strip=True),
                                'grade': cells[3].get_text(strip=True)
                            })
            
            return grades
        except Exception as e:
            print(f"Get grades error: {e}")
            return []
    
    def get_curriculum(self):
        """Fetch curriculum data"""
        try:
            response = self.session.get(
                f"{self.base_url}/Student_Studyplan.asp", 
                timeout=10
            )
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse curriculum
            curriculum = []
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        course_code = cells[0].get_text(strip=True)
                        if course_code and course_code[0].isdigit():
                            curriculum.append({
                                'code': course_code,
                                'name': cells[1].get_text(strip=True),
                                'credits': cells[2].get_text(strip=True)
                            })
            
            return curriculum
        except Exception as e:
            print(f"Get curriculum error: {e}")
            return []
    
    def get_student_data(self):
        """Fetch all student data"""
        return {
            'grades': self.get_grades(),
            'curriculum': self.get_curriculum()
        }

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle LIFF login request"""
    try:
        data = request.json
        line_user_id = data.get('userId')
        student_id = data.get('studentId')
        password = data.get('password')
        
        if not all([line_user_id, student_id, password]):
            return jsonify({
                'success': False,
                'message': 'ข้อมูลไม่ครบถ้วน'
            }), 400
        
        # Login to RMU
        rmu = RMUSession()
        cookies = rmu.login(student_id, password)
        
        if not cookies:
            return jsonify({
                'success': False,
                'message': 'รหัสผ่านไม่ถูกต้อง'
            }), 401
        
        # Store session in Redis
        redis_client.setex(
            f"session:{line_user_id}",
            SESSION_EXPIRE,
            json.dumps(cookies)
        )
        
        # Fetch and cache student data
        student_data = rmu.get_student_data()
        redis_client.setex(
            f"data:{line_user_id}",
            SESSION_EXPIRE,
            json.dumps(student_data)
        )
        
        # Store student ID
        redis_client.setex(
            f"studentid:{line_user_id}",
            SESSION_EXPIRE,
            student_id
        )
        
        return jsonify({
            'success': True,
            'message': 'เข้าสู่ระบบสำเร็จ'
        })
    
    except Exception as e:
        print(f"API login error: {e}")
        return jsonify({
            'success': False,
            'message': 'เกิดข้อผิดพลาดในระบบ'
        }), 500

@app.route('/api/get-advice', methods=['POST'])
def get_advice():
    """Get registration advice for user"""
    try:
        data = request.json
        line_user_id = data.get('userId')
        
        if not line_user_id:
            return jsonify({'error': 'ไม่พบ User ID'}), 400
        
        # Check if session exists
        student_data_json = redis_client.get(f"data:{line_user_id}")
        
        if not student_data_json:
            return jsonify({
                'error': 'session_expired',
                'message': 'กรุณาเข้าสู่ระบบใหม่ผ่าน Rich Menu'
            }), 401
        
        student_data = json.loads(student_data_json)
        
        # Analyze with AI
        advice = analyze_with_ai(student_data)
        
        return jsonify({
            'success': True,
            'advice': advice
        })
    
    except Exception as e:
        print(f"Get advice error: {e}")
        return jsonify({
            'error': 'internal_error',
            'message': 'เกิดข้อผิดพลาดในการวิเคราะห์'
        }), 500

@app.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """Refresh student data from RMU"""
    try:
        data = request.json
        line_user_id = data.get('userId')
        
        # Get stored session
        cookies_json = redis_client.get(f"session:{line_user_id}")
        
        if not cookies_json:
            return jsonify({
                'error': 'session_expired',
                'message': 'กรุณาเข้าสู่ระบบใหม่'
            }), 401
        
        cookies = json.loads(cookies_json)
        
        # Restore session and fetch new data
        rmu = RMUSession()
        rmu.restore_session(cookies)
        student_data = rmu.get_student_data()
        
        # Update cache
        redis_client.setex(
            f"data:{line_user_id}",
            SESSION_EXPIRE,
            json.dumps(student_data)
        )
        
        return jsonify({
            'success': True,
            'message': 'อัพเดทข้อมูลสำเร็จ'
        })
    
    except Exception as e:
        print(f"Refresh data error: {e}")
        return jsonify({
            'error': 'refresh_failed',
            'message': 'ไม่สามารถอัพเดทข้อมูลได้'
        }), 500

def analyze_with_ai(student_data):
    """
    Use AI to analyze student data and provide advice
    TODO: Integrate with Claude API or OpenAI
    """
    grades = student_data.get('grades', [])
    curriculum = student_data.get('curriculum', [])
    
    # Find completed courses
    completed_codes = {g['code'] for g in grades if g['grade'] not in ['-', '', 'W', 'F']}
    
    # Find remaining courses
    remaining = [c for c in curriculum if c['code'] not in completed_codes]
    
    if not remaining:
        return "🎉 ยินดีด้วย! คุณเรียนครบทุกวิชาในหลักสูตรแล้ว"
    
    # Simple recommendation
    advice = f"📚 คุณเรียนไปแล้ว {len(completed_codes)}/{len(curriculum)} วิชา\n\n"
    advice += f"📋 วิชาที่ยังต้องเรียน ({len(remaining)} วิชา):\n\n"
    
    for i, course in enumerate(remaining[:5], 1):
        advice += f"{i}. {course['code']} - {course['name']}\n"
        advice += f"   หน่วยกิต: {course['credits']}\n\n"
    
    if len(remaining) > 5:
        advice += f"...และอีก {len(remaining) - 5} วิชา\n\n"
    
    advice += "💡 แนะนำ: ควรลงวิชาหลักก่อน แล้วค่อยลงวิชาเลือก"
    
    return advice

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

### 3. LINE Bot Webhook

**File**: `line_bot.py`

```python
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

app = Flask(__name__)

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

BACKEND_API = 'https://your-backend.com/api'

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    line_user_id = event.source.user_id
    
    # Command: แนะนำการลงทะเบียน
    if 'แนะนำ' in text or 'ลงทะเบียน' in text:
        try:
            response = requests.post(
                f'{BACKEND_API}/get-advice',
                json={'userId': line_user_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                advice = data['advice']
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=advice)
                )
            elif response.status_code == 401:
                # Session expired
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="⚠️ Session หมดอายุ\nกรุณาเข้าสู่ระบบใหม่ผ่าน Rich Menu"
                    )
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง")
                )
        except Exception as e:
            print(f"Error: {e}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="เกิดข้อผิดพลาดในระบบ")
            )
    
    # Command: อัพเดทข้อมูล
    elif 'อัพเดท' in text or 'refresh' in text.lower():
        try:
            response = requests.post(
                f'{BACKEND_API}/refresh-data',
                json={'userId': line_user_id},
                timeout=30
            )
            
            if response.status_code == 200:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="✅ อัพเดทข้อมูลสำเร็จ")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="⚠️ ไม่สามารถอัพเดทได้\nกรุณาเข้าสู่ระบบใหม่"
                    )
                )
        except Exception as e:
            print(f"Error: {e}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="เกิดข้อผิดพลาด")
            )
    
    # Help
    elif 'help' in text.lower() or 'ช่วย' in text:
        help_text = """
📚 คำสั่งที่ใช้ได้:

• แนะนำการลงทะเบียน - รับคำแนะนำ
• อัพเดทข้อมูล - อัพเดทข้อมูลล่าสุด
• help - แสดงคำสั่งทั้งหมด

💡 หากยังไม่ได้เข้าสู่ระบบ
กรุณากดปุ่ม "เข้าสู่ระบบ" ใน Rich Menu ด้านล่าง
"""
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=help_text)
        )

if __name__ == "__main__":
    app.run(port=8000)
```

---

### 4. Rich Menu Setup

**File**: `setup_richmenu.py`

```python
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction, MessageAction
import requests

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')

# Create Rich Menu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="Registration Advisor Menu",
    chat_bar_text="เมนู",
    areas=[
        # Area 1: เข้าสู่ระบบ (LIFF)
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
            action=URIAction(
                label='เข้าสู่ระบบ',
                uri='https://liff.line.me/YOUR_LIFF_ID'
            )
        ),
        # Area 2: แนะนำการลงทะเบียน
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
            action=MessageAction(
                label='แนะนำการลงทะเบียน',
                text='แนะนำการลงทะเบียน'
            )
        ),
        # Area 3: อัพเดทข้อมูล
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=843, width=1250, height=843),
            action=MessageAction(
                label='อัพเดทข้อมูล',
                text='อัพเดทข้อมูล'
            )
        ),
        # Area 4: ช่วยเหลือ
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=843, width=1250, height=843),
            action=MessageAction(
                label='ช่วยเหลือ',
                text='help'
            )
        )
    ]
)

# Create rich menu
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
print(f"Rich Menu ID: {rich_menu_id}")

# Upload rich menu image
with open('richmenu.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

# Set as default
line_bot_api.set_default_rich_menu(rich_menu_id)
print("Rich Menu set as default!")
```

---

## Deployment Checklist

### 1. **LINE Developer Console**
- [ ] สร้าง Messaging API channel
- [ ] สร้าง LIFF app
- [ ] เปิด webhook
- [ ] ได้ Channel Access Token
- [ ] ได้ Channel Secret
- [ ] ได้ LIFF ID

### 2. **Backend Setup**
- [ ] Deploy Flask app (Heroku/Railway/AWS)
- [ ] Setup Redis (Redis Cloud/AWS ElastiCache)
- [ ] Configure HTTPS (Let's Encrypt)
- [ ] Set environment variables
- [ ] Test API endpoints

### 3. **LIFF Setup**
- [ ] Host LIFF HTML (GitHub Pages/Netlify/S3)
- [ ] Update LIFF endpoint URL in LINE Console
- [ ] Update backend API URL in LIFF HTML
- [ ] Test LIFF flow

### 4. **Rich Menu**
- [ ] Design rich menu image (2500x1686px)
- [ ] Run setup_richmenu.py
- [ ] Test each button

---

## Security Considerations

### ⚠️ Important Security Measures

1. **Password Handling**
   - ❌ ห้ามเก็บ password แบบ plaintext
   - ✅ ใช้ HTTPS เสมอ
   - ✅ Password ผ่าน LIFF เท่านั้น

2. **Session Management**
   - ✅ ใช้ Redis เก็บ session (ไม่ใช่ database)
   - ✅ ตั้ง expiration time (1 hour)
   - ✅ Clear session เมื่อ logout

3. **API Security**
   - ✅ Validate LINE signature
   - ✅ Rate limiting
   - ✅ Input validation
   - ✅ Error handling

4. **Redis Security**
   - ✅ ใช้ password
   - ✅ Bind to localhost
   - ✅ ใช้ TLS ถ้า remote

5. **PDPA Compliance**
   - ✅ แจ้ง user ว่าเก็บข้อมูลอะไร
   - ✅ ลบ session หลังหมดอายุ
   - ✅ ไม่ log password

---

## Advantages

✅ **Security**: User login เอง, password ไม่ผ่าน chat
✅ **Session Reuse**: ไม่ต้อง login ทุกครั้ง
✅ **Scalable**: ใช้ Redis cache, support หลาย user
✅ **Better UX**: LIFF UI สวยกว่า text command
✅ **PDPA Compliant**: เก็บแค่ session, ไม่เก็บ password
✅ **Maintainable**: แยก component ชัดเจน

---

## Potential Issues & Solutions

| ปัญหา | วิธีแก้ |
|------|--------|
| **Session หมดอายุ** | ตรวจสอบก่อนใช้ทุกครั้ง, มีปุ่ม "login ใหม่" |
| **RMU server down** | Implement retry logic, แสดง error ที่เข้าใจได้ |
| **Network timeout** | ตั้ง timeout ที่เหมาะสม (10-30 วินาที) |
| **Redis connection fail** | Implement fallback, health check |
| **Rate limiting จาก RMU** | เพิ่ม delay, cache ข้อมูล |
| **LIFF ไม่เปิด** | ตรวจสอบ LIFF ID, HTTPS requirement |

---

## Testing

### Manual Testing Checklist

- [ ] LIFF เปิดได้จาก Rich Menu
- [ ] Login สำเร็จด้วย credentials ที่ถูกต้อง
- [ ] Login ไม่สำเร็จด้วย credentials ผิด
- [ ] ดึงข้อมูลได้หลัง login
- [ ] ตอบคำแนะนำได้ใน chat
- [ ] Session expire แล้วบอก login ใหม่
- [ ] Refresh data ได้
- [ ] Rich Menu ทุกปุ่มทำงาน

---

## Next Steps

1. **Implement AI Analysis**
   - Integrate Claude API / OpenAI
   - Create better prompts
   - Handle edge cases

2. **Add More Features**
   - แสดง GPA
   - แจ้งเตือนเมื่อเปิดลงทะเบียน
   - Export transcript เป็น PDF
   - แนะนำตารางเรียน

3. **Improve UX**
   - Add loading states
   - Better error messages
   - Quick reply buttons
   - Flex messages สำหรับแสดงผล

4. **Monitoring**
   - Log user actions
   - Track errors
   - Monitor Redis usage
   - Set up alerts

---

## Resources

- [LINE LIFF Documentation](https://developers.line.biz/en/docs/liff/)
- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/)
- [Rich Menu Guide](https://developers.line.biz/en/docs/messaging-api/using-rich-menus/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Redis Documentation](https://redis.io/documentation)
