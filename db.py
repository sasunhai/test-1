import os
import uuid
import datetime
import gspread
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# Google Sheets API Connection
# ============================================================
def get_gspread_client():
    """
    Connects to Google Sheets using Streamlit Secrets (for Streamlit Cloud) 
    or falls back to a local service_account.json file.
    """
    try:
        import streamlit as st
        # 1. Try reading from Streamlit Secrets
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            credentials_dict = dict(st.secrets["gcp_service_account"])
            return gspread.service_account_from_dict(credentials_dict)
    except Exception:
        pass

    # 2. Fallback to local service_account.json
    json_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "service_account.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"ไม่พบไฟล์ Credentials: '{json_path}' กรุณาตรวจสอบว่ามีไฟล์ service_account.json ในโฟลเดอร์โปรเจกต์"
        )
    return gspread.service_account(filename=json_path)


def get_spreadsheet():
    """
    Opens the target spreadsheet using URL or Sheet Name 
    from Streamlit Secrets or Environment Variables.
    """
    gc = get_gspread_client()
    sheet_url = ""
    sheet_name = "SchoolDatabase"

    # Try reading configuration from Streamlit Secrets first
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            sheet_url = st.secrets.get("GOOGLE_SHEETS_URL", "")
            sheet_name = st.secrets.get("GOOGLE_SHEETS_NAME", sheet_name)
    except Exception:
        pass

    # Fallback to .env values if missing in st.secrets
    if not sheet_url:
        sheet_url = os.getenv("GOOGLE_SHEETS_URL", "").strip()
    if not sheet_name:
        sheet_name = os.getenv("GOOGLE_SHEETS_NAME", "SchoolDatabase").strip()

    if sheet_url:
        return gc.open_by_url(sheet_url)
    
    return gc.open(sheet_name)


# ============================================================
# Operations บน Google Sheets
# ============================================================
def get_user_by_username(username: str):
    """
    ดึงข้อมูลผู้ใช้จาก Google Sheets โดยทำการตัดช่องว่างและเทียบเคียงแบบ Case-insensitive
    """
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("users")
        records = ws.get_all_records()

        target_username = str(username).strip().lower()

        for user in records:
            db_username = str(user.get("username", "")).strip().lower()

            if db_username and db_username == target_username:
                user["is_active"] = str(user.get("is_active")).upper() in ["TRUE", "1", "YES"]
                
                grade = user.get("grade_level")
                if grade is not None and str(grade).isdigit():
                    user["grade_level"] = int(grade)
                else:
                    user["grade_level"] = None
                    
                return user
        return None
    except Exception as e:
        print(f"[DEBUG] เกิดข้อผิดพลาดใน get_user_by_username: {e}")
        return None


def touch_last_login(username: str):
    """
    อัปเดตเวลาเข้าใช้งานล่าสุดของผู้ใช้ในคอลัมน์ H (last_login)
    """
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("users")
        cell = ws.find(username.strip(), in_column=2)  # คอลัมน์ B คือ username
        if cell:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.update_cell(cell.row, 8, now_str)  # คอลัมน์ H คือ last_login
    except Exception as e:
        print(f"[DEBUG] Error updating last login: {e}")


def write_login_log(username: str, success: bool):
    """
    บันทึกประวัติการเข้าสู่ระบบลงใน Worksheet 'login_logs'
    """
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("login_logs")
        log_id = str(uuid.uuid4())[:8]
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        ws.append_row([log_id, username, "TRUE" if success else "FALSE", now_str])
    except Exception as e:
        print(f"[DEBUG] Error writing login log: {e}")


def authenticate(username: str, password: str):
    """
    ตรวจสอบชื่อผู้ใช้และรหัสผ่านแบบ Plain text (ตรงๆ)
    """
    user = get_user_by_username(username)

    if user is None:
        write_login_log(username, False)
        return None, "ไม่พบชื่อผู้ใช้นี้ในระบบ"

    if not user["is_active"]:
        write_login_log(username, False)
        return None, "บัญชีนี้ถูกระงับการใช้งาน"

    # เปรียบเทียบรหัสผ่านตรงๆ (Plain Text)
    stored_password = str(user.get("password_hash", "")).strip()
    if password.strip() != stored_password:
        write_login_log(username, False)
        return None, "รหัสผ่านไม่ถูกต้อง"

    touch_last_login(username)
    write_login_log(username, True)
    
    # ลบข้อมูลรหัสผ่านออกก่อนส่งกลับ Session เพื่อความสะอาดของวัตถุ
    user.pop("password_hash", None)
    return user, None


def create_user(username, password, full_name, role="student", grade_level=None):
    """
    สร้างผู้ใช้งานโดยบันทึกรหัสผ่านเป็น Plain text ลงคอลัมน์ C
    """
    try:
        sh = get_spreadsheet()
        
        try:
            ws = sh.worksheet("users")
        except gspread.exceptions.WorksheetNotFound:
            print("❌ ข้อผิดพลาด: ไม่พบ WorkSheet (แท็บ) ชื่อ 'users' ใน Google Sheet")
            return None
        
        if get_user_by_username(username) is not None:
            print(f"❌ ข้อผิดพลาด: ชื่อผู้ใช้ '{username}' มีอยู่ในระบบแล้ว")
            return None

        user_id = str(uuid.uuid4())
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_row = [
            user_id,
            username.strip(),
            password.strip(),  # บันทึกรหัสผ่าน Plain text ตรงๆ
            full_name.strip(),
            role,
            grade_level if grade_level else "",
            "TRUE",
            now_str
        ]
        
        ws.append_row(new_row)
        return user_id

    except gspread.exceptions.SpreadsheetNotFound:
        print("❌ ข้อผิดพลาด: ไม่พบ Google Sheet ตามชื่อหรือ URL ที่ระบุในไฟล์ .env")
        return None
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดแบบไม่คาดคิด ({type(e).__name__}): {e}")
        return None