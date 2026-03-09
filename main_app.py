import streamlit as st

st.set_page_config(layout="wide", page_title="우미건설 구조 안전성 검토 프로그램", page_icon="🏢")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');
html, body, [class*="css"], .stMarkdown, p, div, span, button, label, h1, h2, h3, h4, h5 {
    font-family: 'Noto Sans KR', sans-serif !important;
}
.material-symbols-rounded {
    font-family: 'Material Symbols Rounded' !important;
}
</style>
""", unsafe_allow_html=True)

pages = {
    "메인 홈": [
        st.Page("Home.py", title="홈 화면", icon="🏠", default=True, url_path="home")
    ],
    "구조 검토 시스템": [
        st.Page("ShoringProject/app.py", title="가설 동바리 검토 시스템", icon="🏗️", url_path="shoring_project"),
        st.Page("Parking_Shoring_System/parking_app.py", title="주차장 가설 동바리 리뷰", icon="🚗", url_path="parking_shoring"),
        st.Page("Equipment_Load_Check/equipment_app.py", title="주차장 장비하중 검토", icon="🚜", url_path="equipment_load"),
        st.Page("Construction_Safety_System/buoyancy_app.py", title="시공단계 부력 검토", icon="⚓", url_path="buoyancy"),
        st.Page("PRD_Axial_Load_Calc/app.py", title="PRD 축력 검토", icon="🏢", url_path="prd_calc")
    ]
}

pg = st.navigation(pages)
pg.run()
