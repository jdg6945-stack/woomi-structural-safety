import streamlit as st

st.set_page_config(layout="wide", page_title="우미건설 구조 안전성 검토 프로그램")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
.stApp {
    font-family: 'Noto Sans KR', sans-serif !important;
}
.stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
[data-testid="stSidebar"], [data-testid="stHeader"],
.stTextInput input, .stNumberInput input, .stSelectbox, .stMultiSelect,
.stButton button, .stTab button {
    font-family: 'Noto Sans KR', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

pages = {
    "메인 홈": [
        st.Page("Home.py", title="홈 화면", default=True, url_path="home")
    ],
    "구조 검토 시스템": [
        st.Page("본동_동바리_설치_층수_검토/app.py", title="본동 동바리 설치 층수 검토", url_path="shoring_project"),
        st.Page("지하주차장_동바리_설치_층수_검토/parking_app.py", title="지하주차장 동바리 설치 층수 검토", url_path="parking_shoring"),
        st.Page("주차장_장비하중_검토/equipment_app.py", title="주차장 장비하중 검토", url_path="equipment_load"),
        st.Page("시공단계_부력_검토/buoyancy_app.py", title="시공단계 부력 검토", url_path="buoyancy"),
        st.Page("PRD_축력_검토/app.py", title="PRD 축력 검토", url_path="prd_calc")
    ]
}

pg = st.navigation(pages)
pg.run()
