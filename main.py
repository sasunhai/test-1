import streamlit as st
from db import authenticate

st.set_page_config(
    page_title="เช็คคะแนน | โรงเรียนบ้านสระบัว",
    page_icon="📖",
    layout="wide",
)

# ------------------------------------------------------------
# Custom CSS Style
# ------------------------------------------------------------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .grade-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 24px;
        border: 1px solid #dfe9e4;
        box-shadow: 0 3px 15px rgba(18, 59, 48, 0.05);
        text-align: center;
        margin-bottom: 15px;
    }
    .grade-card h4 {
        color: #71817a;
        margin: 0 0 10px 0;
        font-weight: normal;
        font-size: 16px;
    }
    .grade-card .card-title {
        color: #183b30;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .link-btn {
        display: inline-block;
        background-color: #167653;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .link-btn:hover { background-color: #0b4d3a; }

    .login-hero {
        background: linear-gradient(135deg, #17664c, #2f8b62);
        color: white;
        border-radius: 18px;
        padding: 28px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# Session State Setup
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"


def do_logout():
    st.session_state.user = None
    st.session_state.current_page = "home"
    st.rerun()


# ------------------------------------------------------------
# Login Screen
# ------------------------------------------------------------
def render_login():
    left, mid, right = st.columns([1, 1.4, 1])

    with mid:
        st.markdown("""
            <div class="login-hero">
                <h2 style="margin:0;">📖 สมุดคะแนนออนไลน์</h2>
                <p style="margin:6px 0 0; opacity:.9;">โรงเรียนบ้านสระบัว</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("ชื่อผู้ใช้", placeholder="กรอกชื่อผู้ใช้")
            password = st.text_input("รหัสผ่าน", type="password", placeholder="กรอกรหัสผ่าน")
            submitted = st.form_submit_button("🔐 เข้าสู่ระบบ", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.warning("กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน")
            else:
                try:
                    user, error = authenticate(username.strip(), password)
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
                    return

                if error:
                    st.error(error)
                else:
                    st.session_state.user = user
                    st.session_state.current_page = "home"
                    st.rerun()

        st.caption("หากลืมรหัสผ่าน กรุณาติดต่อครูประจำวิชา")


if st.session_state.user is None:
    render_login()
    st.stop()


# ------------------------------------------------------------
# Dashboard & Navigation
# ------------------------------------------------------------
user = st.session_state.user
role_label = {"student": "นักเรียน", "teacher": "ครูผู้สอน", "admin": "ผู้ดูแลระบบ"}

with st.sidebar:
    st.title("📖 สมุดคะแนน")
    st.caption("โรงเรียนบ้านสระบัว")
    st.divider()

    st.markdown(f"**👤 {user.get('full_name', 'ผู้ใช้งาน')}**")
    st.caption(f"สิทธิ์: {role_label.get(user.get('role'), user.get('role', 'ไม่ระบุ'))}")
    st.divider()

    st.markdown("**เมนูหลัก**")
    if st.button("🏠 หน้าหลัก", use_container_width=True, type="primary" if st.session_state.current_page == "home" else "secondary"):
        st.session_state.current_page = "home"
        st.rerun()

    if user.get("role") in ("teacher", "admin"):
        if st.button("⚙️ จัดการผู้ใช้", use_container_width=True, type="primary" if st.session_state.current_page == "users" else "secondary"):
            st.session_state.current_page = "users"
            st.rerun()

    st.divider()
    if st.button("🚪 ออกจากระบบ", use_container_width=True):
        do_logout()


# ------------------------------------------------------------
# Page Routing
# ------------------------------------------------------------
if st.session_state.current_page == "home":
    col_head1, col_head2 = st.columns([3, 1])

    with col_head1:
        st.title("หน้าหลัก")
        st.caption("ระบบตรวจสอบและติดตามคะแนนนักเรียน")

    with col_head2:
        st.info("👨‍🏫 **นายศาสตราพันธ์ อันไฮ**\n\nครูผู้สอน")

    st.divider()

    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #17664c, #2f8b62);
            color: white;
            border-radius: 18px;
            padding: 32px;
            margin-bottom: 25px;
        ">
            <h2 style="margin-top:0; font-size: 28px;">📊 ระบบเช็คคะแนนนักเรียน</h2>
            <p style="font-size: 16px; opacity: 0.9;">
                ตรวจสอบคะแนนรายวิชา คะแนนรายงาน และผลการเรียนของนักเรียนได้อย่างรวดเร็ว
            </p>
        </div>
    """, unsafe_allow_html=True)

    GRADE_LINKS = {
        1: None,
        2: "https://docs.google.com/spreadsheets/d/1XUU74c_xTI_l0AOVm0Q8doWV3LzbH2KH/edit?gid=1438887448#gid=1438887448",
        3: "https://docs.google.com/spreadsheets/d/1ckVJD_BOCdFqQ1IlClHunktVbzwUgWHG/edit?gid=1172977025#gid=1172977025",
    }

    if user.get("role") == "student" and user.get("grade_level"):
        visible = [user["grade_level"]]
    else:
        visible = [1, 2, 3]

    cols = st.columns(len(visible))

    for col, level in zip(cols, visible):
        link = GRADE_LINKS.get(level)
        body = (
            f'<a href="{link}" target="_blank" class="link-btn">คลิก ลิงก์</a>'
            if link else
            '<p style="color:#888;">(ยังไม่มีลิงก์)</p>'
        )

        with col:
            st.markdown(f"""
                <div class="grade-card">
                    <h4>ชั้นมัธยมศึกษาปีที่ {level}</h4>
                    <div class="card-title">คะแนน</div>
                    {body}
                </div>
            """, unsafe_allow_html=True)

elif st.session_state.current_page == "users":
    st.title("⚙️ จัดการผู้ใช้")
    st.caption("ส่วนผู้ดูแลระบบสำหรับการจัดการบัญชีผู้ใช้งาน")
    st.divider()
    st.info("อยู่ในช่วงการพัฒนาเมนูจัดการผู้ใช้")