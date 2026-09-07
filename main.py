import streamlit as st
from db import authenticate, create_user

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

    # 📌 New Sample Page Navigation
    if st.button("🧪 หน้าทดสอบ (Test 1)", use_container_width=True, type="primary" if st.session_state.current_page == "test1" else "secondary"):
        st.session_state.current_page = "test1"
        st.rerun()

    st.divider()
    if st.button("🚪 ออกจากระบบ", use_container_width=True):
        do_logout()


# ------------------------------------------------------------
# Page Routing
# ------------------------------------------------------------

# 1. HOME PAGE
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

# 2. USERS MANAGEMENT PAGE
elif st.session_state.current_page == "users":
    st.title("⚙️ จัดการผู้ใช้")
    st.caption("เพิ่มผู้ใช้งานใหม่เข้าสู่ระบบ Google Sheets")
    st.divider()

    if user.get("role") not in ("teacher", "admin"):
        st.error("❌ คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()

    st.subheader("➕ เพิ่มบัญชีผู้ใช้งานใหม่")

    with st.form("create_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input("ชื่อผู้ใช้ (Username)", placeholder="เช่น std101")
            new_password = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="กำหนดรหัสผ่าน")
            new_fullname = st.text_input("ชื่อ-นามสกุล", placeholder="เช่น ด.ช. สมชาย ใจดี")

        with col2:
            new_role = st.selectbox(
                "สิทธิ์ผู้ใช้งาน (Role)",
                options=["student", "teacher", "admin"],
                format_func=lambda x: role_label.get(x, x)
            )

            grade_level = None
            if new_role == "student":
                grade_level = st.selectbox(
                    "ระดับชั้นมัธยมศึกษา",
                    options=[1, 2, 3],
                    format_func=lambda x: f"มัธยมศึกษาปีที่ {x}"
                )

        submit_user = st.form_submit_button("➕ สร้างบัญชีผู้ใช้", type="primary", use_container_width=True)

    if submit_user:
        if not new_username or not new_password or not new_fullname:
            st.warning("⚠️ กรุณากรอกข้อมูลที่จำเป็น (ชื่อผู้ใช้, รหัสผ่าน, และชื่อ-นามสกุล) ให้ครบถ้วน")
        else:
            with st.spinner("กำลังบันทึกข้อมูลผู้ใช้ลงในระบบ..."):
                user_id = create_user(
                    username=new_username.strip(),
                    password=new_password.strip(),
                    full_name=new_fullname.strip(),
                    role=new_role,
                    grade_level=grade_level if new_role == "student" else None
                )

                if user_id:
                    st.success(f"✅ เพิ่มผู้ใช้ '{new_fullname}' (Username: {new_username}) สำเร็จเรียบร้อยแล้ว!")
                else:
                    st.error("❌ เกิดข้อผิดพลาด ไม่สามารถสร้างผู้ใช้ได้")

# 3. SAMPLE PAGE (TEST 1)
elif st.session_state.current_page == "test1":
    st.title("🧪 หน้าทดสอบ 1 (Sample Test Page)")
    st.caption("ตัวอย่างการเพิ่มหน้าใหม่และการจัดการองค์ประกอบ Streamlit")
    st.divider()

    st.success("👋 ยินดีต้อนรับสู่หน้าทดสอบระบบ!")

    # Summary Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric(label="คะแนนเฉลี่ยรวม", value="85.4 %", delta="2.1 %")
    m2.metric(label="ส่งงานตรงเวลา", value="92 %", delta="-0.5 %")
    m3.metric(label="จำนวนนักเรียนทั้งหมด", value="120 คน", delta="3 คน")

    st.divider()

    # Interactive Sample Inputs
    st.subheader("📝 แบบฟอร์มทดสอบ")
    col_a, col_b = st.columns(2)

    with col_a:
        test_subject = st.selectbox("เลือกรายวิชา", ["วิทยาศาสตร์", "คณิตศาสตร์", "ภาษาไทย", "ภาษาอังกฤษ"])
        test_score = st.slider("กำหนดคะแนนทดสอบ", min_value=0, max_value=100, value=75)

    with col_b:
        test_note = st.text_area("หมายเหตุเพิ่มเติม", placeholder="กรอกข้อความทดสอบที่นี่...")

    if st.button("💾 บันทึกข้อมูลทดสอบ", type="primary"):
        st.info(f"📌 **บันทึกสำเร็จ:** วิชา {test_subject} | คะแนน: {test_score} | หมายเหตุ: {test_note or 'ไม่มี'}")