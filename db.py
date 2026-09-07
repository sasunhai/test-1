import os
import uuid
import datetime
import gspread
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# Google Sheets API Connection (Using API Key / User Token)
# ============================================================
def get_gspread_client():
    """
    Initializes gspread using a Google Cloud API Key / Token.
    Checks Streamlit Secrets first, then falls back to environment variables (.env).
    """
    api_key = None

    # 1. Try reading from Streamlit Secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GCP_API_KEY" in st.secrets:
            api_key = st.secrets["GCP_API_KEY"]
    except Exception:
        pass

    # 2. Fallback to local environment variable (.env)
    if not api_key:
        api_key = os.getenv("GCP_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "❌ Missing API Token: Please set 'GCP_API_KEY' in your .env file or Streamlit secrets."
        )

    # Authenticate gspread with API Key / Token
    return gspread.api_key(api_key)


def get_spreadsheet():
    """
    Opens the target spreadsheet using URL or Sheet Name.
    Requires the spreadsheet to be shared as "Anyone with the link can view".
    """
    gc = get_gspread_client()
    sheet_url = ""
    sheet_name = "SchoolDatabase"

    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            sheet_url = st.secrets.get("GOOGLE_SHEETS_URL", "")
            sheet_name = st.secrets.get("GOOGLE_SHEETS_NAME", sheet_name)
    except Exception:
        pass

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
    ดึงข้อมูลผู้ใช้จาก Google Sheets (Read-Only Operation - Works with API Key)
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
    ⚠️ NOTE: Requires write permissions. Will fail if using a read-only API Key.
    """
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("users")
        cell = ws.find(username.strip(), in_column=2)
        if cell:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.update_cell(cell.row, 8, now_str)
    except Exception as e:
        print(f"[DEBUG] Error updating last login (Write operation failed): {e}")


def write_login_log(username: str, success: bool):
    """
    ⚠️ NOTE: Requires write permissions. Will fail if using a read-only API Key.
    """
    try:
        sh = get_spreadsheet()
        ws = sh.worksheet("login_logs")
        log_id = str(uuid.uuid4())[:8]
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        ws.append_row([log_id, username, "TRUE" if success else "FALSE", now_str])
    except Exception as e:
        print(f"[DEBUG] Error writing login log (Write operation failed): {e}")


def authenticate(username: str, password: str):
    """
    ตรวจสอบชื่อผู้ใช้และรหัสผ่านแบบ Plain text
    """
    user = get_user_by_username(username)

    if user is None:
        write_login_log(username, False)
        return None, "ไม่พบชื่อผู้ใช้นี้ในระบบ"

    if not user["is_active"]:
        write_login_log(username, False)
        return None, "บัญชีนี้ถูกระงับการใช้งาน"

    stored_password = str(user.get("password_hash", "")).strip()
    if password.strip() != stored_password:
        write_login_log(username, False)
        return None, "รหัสผ่านไม่ถูกต้อง"

    touch_last_login(username)
    write_login_log(username, True)
    
    user.pop("password_hash", None)
    return user, None


def create_user(username, password, full_name, role="student", grade_level=None):
    """
    ⚠️ NOTE: Requires write permissions. Will fail if using a read-only API Key.
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
            password.strip(),
            full_name.strip(),
            role,
            grade_level if grade_level else "",
            "TRUE",
            now_str
        ]
        
        ws.append_row(new_row)
        return user_id

    except gspread.exceptions.SpreadsheetNotFound:
        print("❌ ข้อผิดพลาด: ไม่พบ Google Sheet ตามชื่อหรือ URL ที่ระบุ")
        return None
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดแบบไม่คาดคิด ({type(e).__name__}): {e}")
        return None