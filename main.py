import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="เช็คคะแนน | โรงเรียนบ้านสระบัว",
    page_icon="📖",
    layout="wide"
)

# Custom CSS เพื่อปรับแต่งโทนสีให้ตรงกับธีมเดิม
st.markdown("""
    <style>
    /* ซ่อน Streamlit Menu และ Footer ส่วนเกิน */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* สไตล์การ์ด */
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
    .link-btn:hover {
        background-color: #0b4d3a;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("📖 สมุดคะแนน")
    st.caption("โรงเรียนบ้านสระบัว")
    st.divider()
    st.markdown("**เมนูหลัก**")
    st.button("🏠 หน้าหลัก", use_container_width=True, type="primary")

# --- Header ---
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.title("หน้าหลัก")
    st.caption("ระบบตรวจสอบและติดตามคะแนนนักเรียน")

with col_head2:
    st.info("👨‍🏫 **นายศาสตราพันธ์ อันไฮ**\n\nครูผู้สอน")

st.divider()

# --- Hero Section ---
with st.container():
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

# --- Grade Cards Section ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="grade-card">
            <h4>ชั้นมัธยมศึกษาปีที่ 1</h4>
            <div class="card-title">คะแนน</div>
            <p style="color: #888;">(ยังไม่มีลิงก์)</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="grade-card">
            <h4>ชั้นมัธยมศึกษาปีที่ 22</h4>
            <div class="card-title">คะแนน</div>
            <a href="https://docs.google.com/spreadsheets/d/1XUU74c_xTI_l0AOVm0Q8doWV3LzbH2KH/edit?gid=1438887448#gid=1438887448" target="_blank" class="link-btn">คลิก ลิงก์</a>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="grade-card">
            <h4>ชั้นมัธยมศึกษาปีที่ 3</h4>
            <div class="card-title">คะแนน</div>
            <a href="https://docs.google.com/spreadsheets/d/1ckVJD_BOCdFqQ1IlClHunktVbzwUgWHG/edit?gid=1172977025#gid=1172977025" target="_blank" class="link-btn">คลิก ลิงก์</a>
        </div>
    """, unsafe_allow_html=True)