import streamlit as st
import pandas as pd
from PIL import Image
import os

# 페이지 설정
try:
    st.set_page_config(layout="wide", page_title="주차장 장비하중 검토")
except Exception:
    pass

# 1. 기본 차량 데이터 세팅
if 'vehicle_df' not in st.session_state:
    data = [
        {"차량종류": "펌프카 63m", "총중량(ton)": 42.95, "하중분담률": 0.120, "후륜바퀴축수": 3, "축간거리(m)": 1.3},
        {"차량종류": "레미콘 6m³", "총중량(ton)": 26.30, "하중분담률": 0.220, "후륜바퀴축수": 2, "축간거리(m)": 1.3},
        {"차량종류": "덤프트럭 25t", "총중량(ton)": 38.80, "하중분담률": 0.170, "후륜바퀴축수": 2, "축간거리(m)": 1.3},
        {"차량종류": "Hydro Crane 50t(RK-500)", "총중량(ton)": 38.90, "하중분담률": 0.500, "후륜바퀴축수": 1, "축간거리(m)": 1.3},
        {"차량종류": "Hydro Crane 70t(LTM-1070)", "총중량(ton)": 37.10, "하중분담률": 0.125, "후륜바퀴축수": 2, "축간거리(m)": 1.3},
        {"차량종류": "Hydro Crane 105t(LTM-1095)", "총중량(ton)": 51.10, "하중분담률": 0.100, "후륜바퀴축수": 4, "축간거리(m)": 1.3},
    ]
    st.session_state.vehicle_df = pd.DataFrame(data)

# 스타일 설정
st.markdown("""
    <style>
    .formula-title { font-size: 20px; font-weight: bold; color: #495057; margin-top: 15px; margin-bottom: 15px; border-left: 5px solid #495057; padding-left: 10px; }
    .result-item { font-size: 18px; margin-bottom: 5px; }
    .result-bold { font-size: 20px; font-weight: bold; }
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    /* 안내 문구 박스 스타일 */
    .guide-box {
        background-color: #f1f3f5;
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 5px solid #adb5bd;
        margin-bottom: 25px;
        line-height: 1.6;
        color: #495057;
    }
    .guide-box ul {
        margin: 0;
        padding-left: 20px;
    }
    .guide-box li {
        margin-bottom: 5px;
        font-size: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 이미지 매핑
img_mapping = {
    "펌프카 63m": ["펌프카 63m 그림.png", "펌프카 63m 하중 분담률, 축간 거리.png"],
    "레미콘 6m³": ["레미콘 그림.png", "레미콘 하중 분담률, 축간 거리.png"],
    "덤프트럭 25t": ["덤프트럭.png", "덤프트럭 하중 분담률, 축간 거리.png"],
    "Hydro Crane 50t(RK-500)": ["HydroCrane 50t(RK-500).png", "HydroCrane 50t(RK-500) 하중 분담률, 축간 거리.png"],
    "Hydro Crane 70t(LTM-1070)": ["HydroCrane 70t(LTM-1070).png", "HydroCrane 70t(LTM-1070) 하중 분담률, 축간 거리.png"],
    "Hydro Crane 105t(LTM-1095)": ["HydroCrane 105t(LTM-1095).png", "HydroCrane 105t(LTM-1095) 하중 분담률, 축간 거리.png"]
}

# -------------------------------------------
# 1. 왼쪽 사이드바 (검토 설정)
# -------------------------------------------
with st.sidebar:
    st.title("검토 설정")
    st.subheader("설계 여유하중 입력")
    finish_load = st.number_input("마감하중 (kN/m²)", value=2.0, step=0.1)
    live_load = st.number_input("활하중 (kN/m²)", value=30.0, step=0.1)
    impact_percent = st.number_input("충격계수 (%)", value=30, step=5)
    
    allowable_total = finish_load + live_load
    st.info(f"✅ 설계 여유하중 합계: {allowable_total:.2f} kN/m²")

# -------------------------------------------
# 2. 메인 화면
# -------------------------------------------
st.title("주차장 장비하중 검토 시스템")

# 시스템 안내 문구 추가
st.markdown("""
    <div class="guide-box">
        <strong>⚠️ 사용 전 안내 사항</strong>
        <ul>
            <li>본 프로그램은 공사 차량에 대한 안정성을 간편하게 확인할 수 있는 약식 검토용 시스템입니다.</li>
            <li>시스템에 입력된 차량 제원은 참고용 규격이며, 실제 현장에서 운용되는 차량에 맞게 하단의 <strong>[차량 데이터 관리]</strong>에서 수정 후 검토하시기 바랍니다.</li>
            <li><strong>설계 여유하중</strong>은 아직 시공되지 않은 마감재 하중을 장비 하중에 대한 여유분으로 간주하여 검토합니다.</li>
            <li>안전 사고 예방을 위해 현장 내 모든 차량은 <strong>시속 10km/h 이하</strong>의 속도 제한을 엄격히 준수하여 운행해야 합니다.</li>
            <li>공식적인 검토의견서가 필요한 경우, 반드시 <strong>원구조설계사</strong>의 정밀 상세 검토를 통해 확인을 받으시기 바랍니다.</li>
        </ul>
    </div>
""", unsafe_allow_html=True)
st.write("---")

# 2-1. 검토 차량 선택
selected_v = st.selectbox("검토할 차량을 선택하세요", st.session_state.vehicle_df["차량종류"].tolist())

# 데이터 로드 및 계산
v_data = st.session_state.vehicle_df[st.session_state.vehicle_df["차량종류"] == selected_v].iloc[0]
weight, ratio, axles, dist = v_data["총중량(ton)"], v_data["하중분담률"], v_data["후륜바퀴축수"], v_data["축간거리(m)"]
P_base = weight * 9.81 * ratio
P_impact = P_base * (1 + impact_percent/100)
area = (1.8 + dist * (axles - 1)) * 1.8
equiv_load = (P_impact * axles) / area if area > 0 else 0
load_ratio = (equiv_load / allowable_total) * 100 if allowable_total > 0 else 0

# 상단 레이아웃 분할: 좌(이미지 영역 축소), 우(결과 영역 확대)
left_col, right_col = st.columns([0.8, 1.2])

with left_col:
    # 2-2. 이미지 섹션
    st.markdown('<p class="formula-title">차량 이미지 및 제원</p>', unsafe_allow_html=True)
    if selected_v in img_mapping:
        files = img_mapping[selected_v]
        img_tabs = st.tabs(["차량 외관", "제원 상세"])
        try:
            with img_tabs[0]:
                # 이미지 크기 조절을 위한 내측 여백 추가
                _, img_c1, _ = st.columns([0.05, 0.9, 0.05])
                with img_c1:
                    st.image(os.path.join(os.path.dirname(__file__), files[0]), use_container_width=True)
            with img_tabs[1]:
                # 이미지 크기 조절을 위한 내측 여백 추가
                _, img_c2, _ = st.columns([0.05, 0.9, 0.05])
                with img_c2:
                    st.image(os.path.join(os.path.dirname(__file__), files[1]), use_container_width=True)
        except: st.info(f"ℹ️ '{selected_v}' 이미지를 불러올 수 없습니다.")

with right_col:
    # 2-3. 검토 결과 섹션
    st.markdown('<p class="formula-title">검토 결과</p>', unsafe_allow_html=True)
    
    # 하중 비율 표시
    st.metric("하중 비율 (Ratio)", f"{load_ratio:.1f}%")
    
    # 결과 판정 표시 (줄 나눔)
    if load_ratio <= 100:
        st.success(f"**결과: 주행 가능 (O.K)**")
    elif 100 < load_ratio <= 105:
        st.warning(f"**결과: 주행 가능 (Say O.K)**")
    else:
        st.error(f"**결과: 주행 불가 (N.G)**")

st.write("---")

# 2-4. 차량 데이터 관리
with st.expander("차량 데이터 관리"):
    edited_df = st.data_editor(st.session_state.vehicle_df, num_rows="dynamic", use_container_width=True, key="vehicle_editor")
    st.session_state.vehicle_df = edited_df

# 2-5. 상세 계산 근거 (최하단 이동 및 왼쪽 정렬)
with st.expander("상세 계산 근거 보기"):
    st.write(f"**1) 바퀴당 집중하중(P)**")
    st.markdown(rf"&nbsp;&nbsp;&nbsp;&nbsp;$P = {weight}t \times 9.81 \times {ratio} = {P_base:.2f}$ kN")
    
    st.write(f"**2) 충격고려 하중(P')**")
    st.markdown(rf"&nbsp;&nbsp;&nbsp;&nbsp;$P' = {P_base:.2f} \times (1 + {impact_percent}/100) = {P_impact:.2f}$ kN")
    
    st.write(f"**3) 분담 면적(Area)**")
    st.markdown(rf"&nbsp;&nbsp;&nbsp;&nbsp;$Area = (1.8 + {dist} \times ({int(axles)}-1)) \times 1.8 = {area:.2f}$ m²")
    
    st.write(f"**4) 환산 장비하중**")
    st.markdown(rf"&nbsp;&nbsp;&nbsp;&nbsp;$W_{{eq}} = \frac{{{P_impact:.2f} \times {int(axles)}}}{{{area:.2f}}} = {equiv_load:.2f}$ kN/m²")
    
    st.write(f"**5) 하중 비율(Ratio)**")
    st.markdown(rf"&nbsp;&nbsp;&nbsp;&nbsp;$Ratio = \frac{{{equiv_load:.2f}}}{{{allowable_total:.2f}}} \times 100 = {load_ratio:.1f}$ %")



