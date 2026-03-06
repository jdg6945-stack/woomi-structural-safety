import streamlit as st
import os

st.title("우미건설 구조 안전성 검토 프로그램")
st.markdown("---")
st.write("원하시는 구조 검토 프로그램을 선택하여 실행하세요.")
st.write("")

# 3 Column layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 본동 동바리 설치 층수 검토")
    st.write("시공 단계별 동바리 설치 층수 검토")
    st.write("")
    if st.button("실행하기", key="btn1", use_container_width=True, type="primary"):
        st.switch_page("ShoringProject/app.py")

with col2:
    st.markdown("#### 지하주차장 동바리 설치 층수 검토")
    st.write("시공 단계별 동바리 설치 층수 검토")
    st.write("")
    if st.button("실행하기", key="btn2", use_container_width=True, type="primary"):
        st.switch_page("Parking_Shoring_System/parking_app.py")

with col3:
    st.markdown("#### 주차장 장비하중 검토")
    st.write("주차장 진입 펌프카, 레미콘, 하이드로 크레인 등 안전성 검토")
    st.write("")
    if st.button("실행하기", key="btn3", use_container_width=True, type="primary"):
        st.switch_page("Equipment_Load_Check/equipment_app.py")

st.write("---")
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("#### 시공단계 부력 검토")
    st.write("시공 중 지반 수위 변화에 따른 지하 구조물 부력 안정성 검토")
    st.write("")
    if st.button("실행하기", key="btn4", use_container_width=True, type="primary"):
        st.switch_page("Construction_Safety_System/buoyancy_app.py")

with col5:
    st.markdown("#### PRD 축력 검토")
    st.write("역타 공법(Top-down) 적용 시 PRD 기초 허용 축력 및 목표층 시공 한계 검토")
    st.write("")
    if st.button("실행하기", key="btn5", use_container_width=True, type="primary"):
        st.switch_page("PRD_Axial_Load_Calc/app.py")

with col6:
    st.markdown("#### To be continue...")
    st.write("준비 중")
    st.write("")
    st.button("업데이트", key="btn6", use_container_width=True, disabled=True)

st.write(" ")
st.markdown("<div style='text-align: right; color: #94a3b8; font-size: 0.9rem;'>Posco E&C AI Solutions</div>", unsafe_allow_html=True)
