import streamlit as st
import os

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

/* 전역 폰트 */
.stApp {
    font-family: 'Noto Sans KR', sans-serif !important;
    background-color: #f8fafc;
}
.stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
[data-testid="stSidebar"], [data-testid="stHeader"],
.stTextInput input, .stNumberInput input, .stSelectbox, .stMultiSelect {
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* 상단 헤더 배너 */
.home-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #3b6fa0 100%);
    color: white;
    padding: 32px 36px;
    border-radius: 14px;
    margin-bottom: 28px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.home-header h1 {
    font-size: 26px;
    font-weight: 900;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.home-header p {
    font-size: 14px;
    color: #cbd5e1;
    margin: 0;
}

/* 카드 그리드 */
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-top: 8px;
}

/* 카드 스타일 */
.nav-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 26px 22px 22px 22px;
    transition: all 0.2s ease;
    min-height: 140px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    position: relative;
}
.nav-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 6px 20px rgba(59,130,246,0.12);
    transform: translateY(-3px);
}
.nav-card h4 {
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 8px 0;
    line-height: 1.4;
}
.nav-card p {
    font-size: 13px;
    color: #64748b;
    margin: 0;
    line-height: 1.6;
}
.nav-card .card-arrow {
    position: absolute;
    right: 18px;
    top: 50%;
    transform: translateY(-50%);
    color: #cbd5e1;
    font-size: 20px;
    transition: all 0.2s;
}
.nav-card:hover .card-arrow {
    color: #3b82f6;
    right: 14px;
}

/* 투명 버튼 오버레이 — 카드 위에 겹침 */
div[data-testid="stButton"] {
    margin-top: -148px !important;
    position: relative;
    z-index: 10;
}
div[data-testid="stButton"] > button {
    opacity: 0 !important;
    height: 148px !important;
    width: 100% !important;
    cursor: pointer !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* 비활성 카드 */
.nav-card-disabled {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    padding: 26px 22px 22px 22px;
    min-height: 140px;
}
.nav-card-disabled h4 { font-size: 24px; font-weight: 700; color: #94a3b8; margin: 0 0 8px 0; }
.nav-card-disabled p { font-size: 13px; color: #cbd5e1; margin: 0; }

/* 섹션 라벨 */
.section-label {
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
    padding-left: 2px;
}

/* 하단 여백 */
.footer-spacer { height: 40px; }
</style>
""", unsafe_allow_html=True)

# ── 상단 헤더 ──
st.markdown("""
<div class="home-header">
    <h1>우미건설 구조 안전성 검토 프로그램</h1>
    <p>원하시는 구조 검토 프로그램을 선택하여 실행하세요</p>
</div>
""", unsafe_allow_html=True)

# ── 카드 데이터 ──
cards = [
    {"title": "본동 동바리 설치 층수 검토", "desc": "시공 단계별 동바리 설치 층수 검토", "key": "btn1", "page": "본동_동바리_설치_층수_검토/app.py"},
    {"title": "지하주차장 동바리 설치 층수 검토", "desc": "시공 단계별 동바리 설치 층수 검토", "key": "btn2", "page": "지하주차장_동바리_설치_층수_검토/parking_app.py"},
    {"title": "주차장 장비하중 검토", "desc": "주차장 진입 펌프카, 레미콘, 하이드로 크레인 등 안전성 검토", "key": "btn3", "page": "주차장_장비하중_검토/equipment_app.py"},
    {"title": "시공단계 부력 검토", "desc": "시공 중 지반 수위 변화에 따른 지하 구조물 부력 안정성 검토", "key": "btn4", "page": "시공단계_부력_검토/buoyancy_app.py"},
    {"title": "PRD 축력 검토", "desc": "역타 공법(Top-down) 적용 시 PRD 기초 허용 축력 및 목표층 시공 한계 검토", "key": "btn5", "page": "PRD_축력_검토/app.py"},
]

# ── 카드 렌더링 ──
st.markdown('<div class="section-label">구조 검토 시스템</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for i, card in enumerate(cards):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="nav-card">
            <h4>{card["title"]}</h4>
            <p>{card["desc"]}</p>
            <div class="card-arrow">&rsaquo;</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("go", key=card["key"], use_container_width=True):
            st.switch_page(card["page"])
    if i == 2:
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

# 마지막 빈 카드
with cols[2]:
    st.markdown("""
    <div class="nav-card-disabled">
        <h4>To be continue...</h4>
        <p>준비 중</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer-spacer"></div>', unsafe_allow_html=True)
