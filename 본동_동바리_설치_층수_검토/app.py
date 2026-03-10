import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
from datetime import datetime

# ==========================================
# 0. 환경 설정 및 스타일 (글자 크기 확대 + 가독성 강화)
# ==========================================
_font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "malgunbd.ttf")
if os.path.exists(_font_path):
    fm.fontManager.addfont(_font_path)
    plt.rc('font', family=fm.FontProperties(fname=_font_path).get_name())
elif platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    # Linux (Streamlit Cloud) - NanumGothic via packages.txt
    for _lp in ["/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"]:
        if os.path.exists(_lp):
            fm.fontManager.addfont(_lp)
            plt.rc('font', family=fm.FontProperties(fname=_lp).get_name())
            break
    else:
        plt.rc('font', family='sans-serif')

plt.rcParams['axes.unicode_minus'] = False
try:
    st.set_page_config(layout="wide", page_title="본동 동바리 설치 층수 검토")
except Exception:
    pass

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    /* 전역 폰트 & 배경 */
    .stApp { font-family: 'Noto Sans KR', sans-serif !important; background-color: #f8fafc; }
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    [data-testid="stSidebar"], [data-testid="stHeader"],
    .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiSelect {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    /* 사이드바 */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    /* 데이터 에디터 - 가운데 정렬 */
    div[data-testid="stDataEditor"] [data-testid="glide-cell"] {
        justify-content: center !important; text-align: center !important;
    }
    div[data-testid="stDataEditor"] div[role="gridcell"] {
        justify-content: center !important; text-align: center !important; font-size: 16px !important;
    }
    div[data-testid="stDataEditor"] div[role="gridcell"] input {
        text-align: center !important;
    }
    div[data-testid="stDataEditor"] div[role="columnheader"],
    div[data-testid="stDataEditor"] div[role="columnheader"] span,
    div[data-testid="stDataEditor"] [data-testid="column-header-name"] {
        justify-content: center !important; text-align: center !important; width: 100%;
    }
    div[data-testid="stDataEditor"] canvas + div {
        text-align: center !important;
    }
    div[data-testid="stDataEditor"] [class*="cell"] {
        text-align: center !important; justify-content: center !important;
    }
    /* 테이블 */
    .full-width-table { width: 100% !important; border-collapse: collapse; margin-top: 15px; font-size: 16px !important; }
    .full-width-table th, .full-width-table td {
        text-align: center !important; vertical-align: middle !important;
        padding: 12px 10px !important; border: 1px solid #e2e8f0;
    }
    .full-width-table th { background-color: #f1f5f9; font-weight: 700; color: #1e293b; }
    /* 하중 계산 박스 */
    .load-calc-box {
        background-color: #ffffff; padding: 18px; border-radius: 10px;
        border: 1px solid #e2e8f0; border-left: 5px solid #3b82f6;
        font-size: 16px !important; line-height: 1.7;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .load-calc-total { font-size: 20px !important; font-weight: 800; color: #dc2626; margin-top: 10px; }
    /* 판정 */
    .red-text { color: #dc2626; font-weight: 700; }
    .blue-text { color: #3b82f6; font-weight: 700; }
    /* 안내 문구 */
    .guide-box {
        background-color: #f1f5f9; padding: 15px; border-radius: 8px;
        font-size: 14px; color: #334155; margin-bottom: 15px;
        border-left: 5px solid #94a3b8; line-height: 1.6;
    }
    /* 입력 필드 스타일 - 깔끔한 사각 테두리 */
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stTextInput"] > div { border: none !important; box-shadow: none !important; background: transparent !important; }
    [data-baseweb="base-input"],
    [data-baseweb="base-input"] > div { border: none !important; box-shadow: none !important; background-color: #ffffff !important; }
    div[data-baseweb="input"],
    div[data-baseweb="number-input"] { background-color: #ffffff !important; border: none !important; outline: 1px solid #94a3b8 !important; outline-offset: -1px !important; border-radius: 4px !important; box-shadow: none !important; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border: none !important; outline: 1px solid #94a3b8 !important; outline-offset: -1px !important; border-radius: 4px !important; box-shadow: none !important; }
    /* 라벨 스타일 */
    div[data-testid="stWidgetLabel"] p { font-size: 11.5px !important; margin-bottom: 2px !important; line-height: 1.2 !important; }
    /* 입력 높이 통일 */
    div[data-baseweb="input"], div[data-baseweb="number-input"] { min-height: 32px !important; height: auto !important; }
    input[type=number] { -moz-appearance: textfield; font-size: 13px !important; padding: 4px 8px !important; }
    /* 요소 간격 */
    .stNumberInput { margin-bottom: 2px !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.3rem !important; }
    div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] { gap: 0.2rem !important; }
    /* 테이블 배경 흰색 */
    .full-width-table td { background-color: #ffffff; }
    div[data-testid="stTable"] table { background-color: #ffffff !important; }
    div[data-testid="stDataEditor"] { background-color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

COL_THICK = "슬래브 두께(mm)"
COL_LOAD_CONST = "시공하중(kN/m²)"
COL_LOAD_EXTRA = "여유하중(kN/m²)"
COL_LOAD_LIVE = "활하중(kN/m²)"

# ==========================================
# 1. 데이터 관리 로직
# ==========================================
def generate_floor_names(top_type, top_num, bot_type, bot_num):
    """시작층(최상층)~끝층(최하층)에 따라 층이름 리스트 생성
    top_type/bot_type: '지상' 또는 '지하'
    top_num/bot_num: 층 번호 (양수)
    """
    # 통합 인덱스로 변환: 지상 N층=+N, 지하 M층=-M
    top_idx = top_num if top_type == "지상" else -top_num
    bot_idx = bot_num if bot_type == "지상" else -bot_num

    names = []
    for idx in range(top_idx, bot_idx - 1, -1):
        if idx == 0:
            continue  # 0층은 없음
        if idx > 0:
            names.append(f"{idx}F")
        else:
            names.append(f"B{abs(idx)}F")
    # 마지막 층에 (기초) 붙이기
    if names:
        names[-1] = names[-1] + "(기초)"
    return names

def reset_data(top_type="지상", top_num=5, bot_type="지하", bot_num=1):
    floor_names = generate_floor_names(top_type, top_num, bot_type, bot_num)
    total_rows = len(floor_names)
    init_data = {
        "층이름": floor_names,
        COL_THICK: [210] * total_rows, "설계강도(MPa)": [30] * total_rows, "예상강도(MPa)": [14] * total_rows,
        "타설간격(일)": [7] * total_rows, "전이유형": ["일반"] * total_rows,
        COL_LOAD_EXTRA: [1.9] * total_rows, COL_LOAD_LIVE: [2.0] * total_rows, COL_LOAD_CONST: [1.0] * total_rows
    }
    init_data[COL_LOAD_CONST][0] = 2.5
    df = pd.DataFrame(init_data)
    st.session_state.master_df = df

def update_df_callback():
    if "main_editor" in st.session_state:
        edited = st.session_state["main_editor"]
        for row_idx, changes in edited["edited_rows"].items():
            for key, val in changes.items():
                # 층이름에서 '(타설층)' 접미사 제거
                if key == "층이름" and isinstance(val, str):
                    val = val.replace(" (타설층)", "").replace("(타설층)", "")
                st.session_state.master_df.iat[row_idx, st.session_state.master_df.columns.get_loc(key)] = val

if 'master_df' not in st.session_state:
    reset_data("지상", 5, "지하", 1)

# 세션 상태 초기화
if 'top_type' not in st.session_state:
    st.session_state.top_type = "지상"
if 'top_num' not in st.session_state:
    st.session_state.top_num = 5
if 'bot_type' not in st.session_state:
    st.session_state.bot_type = "지하"
if 'bot_num' not in st.session_state:
    st.session_state.bot_num = 1

st.sidebar.header("검토 설정")
st.sidebar.markdown("**최상층 (타설층)**")
top_c1, top_c2, top_c3 = st.sidebar.columns([1, 1, 1])
new_top_type = top_c1.selectbox("구분##top", ["지상", "지하"], index=0 if st.session_state.top_type == "지상" else 1, label_visibility="collapsed")
new_top_num = top_c2.number_input("층##top", min_value=1, max_value=30, value=st.session_state.top_num, label_visibility="collapsed")
top_c3.markdown("<div style='line-height:38px; padding-top:4px;'>층</div>", unsafe_allow_html=True)

st.sidebar.markdown("**최하층**")
bot_c1, bot_c2, bot_c3 = st.sidebar.columns([1, 1, 1])
new_bot_type = bot_c1.selectbox("구분##bot", ["지상", "지하"], index=0 if st.session_state.bot_type == "지상" else 1, label_visibility="collapsed")
new_bot_num = bot_c2.number_input("층##bot", min_value=1, max_value=30, value=st.session_state.bot_num, label_visibility="collapsed")
bot_c3.markdown("<div style='line-height:38px; padding-top:4px;'>층</div>", unsafe_allow_html=True)

# 유효성 검사: 최상층이 최하층보다 위에 있어야 함
top_idx = new_top_num if new_top_type == "지상" else -new_top_num
bot_idx = new_bot_num if new_bot_type == "지상" else -new_bot_num

if top_idx <= bot_idx:
    st.sidebar.error("최상층이 최하층보다 위에 있어야 합니다.")
elif (new_top_type != st.session_state.top_type or new_top_num != st.session_state.top_num or
      new_bot_type != st.session_state.bot_type or new_bot_num != st.session_state.bot_num):
    st.session_state.top_type = new_top_type
    st.session_state.top_num = new_top_num
    st.session_state.bot_type = new_bot_type
    st.session_state.bot_num = new_bot_num
    new_floor_names = generate_floor_names(new_top_type, new_top_num, new_bot_type, new_bot_num)
    new_total = len(new_floor_names)
    old_total = len(st.session_state.master_df)
    if new_total > old_total:
        add_count = new_total - old_total
        new_rows_df = pd.DataFrame({
            "층이름": [""] * add_count, COL_THICK: [210] * add_count, "설계강도(MPa)": [30] * add_count,
            "예상강도(MPa)": [14] * add_count, "타설간격(일)": [7] * add_count, "전이유형": ["일반"] * add_count,
            COL_LOAD_EXTRA: [1.9] * add_count, COL_LOAD_LIVE: [2.0] * add_count, COL_LOAD_CONST: [1.0] * add_count
        })
        st.session_state.master_df = pd.concat([st.session_state.master_df, new_rows_df], ignore_index=True)
    elif new_total < old_total:
        st.session_state.master_df = st.session_state.master_df.iloc[:new_total]
    # 층이름 갱신
    st.session_state.master_df["층이름"] = new_floor_names
    st.rerun()

n_check = 1 # 기본 타설 층수는 1층으로 고정 (14MPa 미달 시 자동으로 하중 합산됨)
# num_beam_types input removed as requested.
if st.sidebar.button("데이터 초기화"):
    st.session_state.top_type = "지상"
    st.session_state.top_num = 5
    st.session_state.bot_type = "지하"
    st.session_state.bot_num = 1
    reset_data("지상", 5, "지하", 1)
    st.rerun()

# ==========================================
# 2. 계산 엔진
# ==========================================
def calculate_shoring_status(df, n_check, transfer_details):
    calc_logs, results = [], []
    total_pu = 0
    for i in range(min(n_check, len(df))):
        row = df.iloc[i]; f_name = row["층이름"]; added_t = 0
        beam_conversion_details = []
        if row["전이유형"] == "전이보" and f_name in transfer_details:
            f_beams = transfer_details[f_name]
            for idx, b in enumerate(f_beams):
                # 보 유효 체적 (mm^3 -> m^3)
                vol_m3 = (b['bw'] * (b['bh'] - row[COL_THICK]) * b['bl'] * b['bn']) / 1e9
                # 영향 면적 (m2) 사용, 없으면 (X*Y)/1e6 사용
                area_m2 = b['area_influence'] if b['area_influence'] > 0 else (b['ax'] * b['ay'] / 1e6)
                increment_m = vol_m3 / area_m2 if area_m2 != 0 else 0
                added_t += (increment_m * 1000) # mm로 변환하여 누적
                
                # 로그용 산식 구성
                area_formula = f"{b['area_influence']:.1f}㎡" if b['area_influence'] > 0 else f"({b['ax']:.0f}×{b['ay']:.0f})㎟"
                beam_conversion_details.append(
                    f"보{idx+1}: ({b['bw']:.0f}×({b['bh']:.0f}-{row[COL_THICK]:.0f})×{b['bl']:.0f}×{b['bn']:.0f}) / {area_formula} = {increment_m*1000:.1f}mm"
                )
        
        thick_mm = row[COL_THICK] + added_t
        thick_m = thick_mm / 1000
        floor_pu = (thick_m * 24) + 0.4 + row[COL_LOAD_CONST]
        total_pu += floor_pu
        
        # 타설층 로그 구성 (상세화)
        calc_logs.append({
            "floor": f_name,
            "beam_details": beam_conversion_details,
            "added_t_mm": added_t,
            "added_t_m": added_t / 1000,
            "base_t_m": row[COL_THICK] / 1000,
            "total_t_m": thick_m,
            "const_load": row[COL_LOAD_CONST],
            "floor_pu": floor_pu
        })

    # 타설층 정보 추가 (젤 상단 1개 또는 n_check개 요약)
    results = []
    # 타설층의 하중 합계(ΣPu)를 첫 행으로 추가
    pouring_names = ", ".join([df.iloc[k]["층이름"] for k in range(min(n_check, len(df)))])
    results.append({
        "검토층": f"{pouring_names} (타설층)",
        "양생일": "-",
        "타설하중(kN/m²)": f"{total_pu:.2f}",
        "여유하중(kN/m²)": "-",
        "잔여하중(kN/m²)": f"{total_pu:.2f}",
        "판정": "하부 서포트 필요"
    })

    remaining_load = total_pu
    check_logs = []
    for i in range(n_check, len(df)):
        row = df.iloc[i]; f_name = str(row["층이름"]).upper()
        # 시공하중 변수화
        const_load = row[COL_LOAD_CONST]
        is_mat = any(x in f_name for x in ["기초", "MAT", "매트"]) or row["전이유형"] == "전이매트"
        
        curing_days = df.iloc[0:i]["타설간격(일)"].sum()
        is_fully_cured = (curing_days >= 28) or (row["예상강도(MPa)"] >= row["설계강도(MPa)"])
        ld, l = row[COL_LOAD_EXTRA], row[COL_LOAD_LIVE]
        allowable = (ld * 1.2) + (l * 1.6) if is_fully_cured else ld + l
        
        if is_mat:
            results.append({
                "검토층": row["층이름"], 
                "양생일": "-", 
                "타설하중(kN/m²)": "-", 
                "여유하중(kN/m²)": "지반 지지(MAT)", 
                "잔여하중(kN/m²)": "0.00", 
                "판정": "종료(기초)"
            })
            check_logs.append({
                "floor": row['층이름'],
                "allowable_math": "지반 지지",
                "final_math": "MAT 기초 지지",
                "decision": ""
            })
            break

        # 14MPa 미만 체크 (지지층으로서 역할 불가, 하중 합산 후 통과)
        try:
            est_strength = float(row["예상강도(MPa)"])
        except (ValueError, TypeError):
            # 숫자가 아닌 경우(예: '-')는 매우 낮은 강도로 간주하여 하중 합산 처리
            est_strength = 0.0

        if est_strength < 14:
            # 현재 층의 하중 계산 (자중+거푸집+시공하중)
            thick_m = row[COL_THICK] / 1000
            floor_self_load = (thick_m * 24) + 0.4 + const_load
            new_total_load = remaining_load + floor_self_load
            
            check_logs.append({
                "floor": row['층이름'],
                "allowable_math": f"예상강도 {est_strength}MPa < 14MPa",
                "final_math": f"{remaining_load:.2f}(상부) + {floor_self_load:.2f}(현재층) = {new_total_load:.2f} kN/m²",
                "decision": " <span style='color:#FF4B4B; font-weight:bold;'>→ 지지 불가 (하중 합산)</span>"
            })
            
            results.append({
                "검토층": f"{row['층이름']} (강도부족)", 
                "양생일": f"{curing_days}일", 
                "타설하중(kN/m²)": f"{new_total_load:.2f}", 
                "여유하중(kN/m²)": "0.00", 
                "잔여하중(kN/m²)": f"{new_total_load:.2f}", 
                "판정": "하부 서포트 필요"
            })
            remaining_load = new_total_load
            continue

        formula = f"({ld:.1f}×1.2)+({l:.1f}×1.6)={allowable:.2f} kN/m²" if is_fully_cured else f"{ld:.1f}+{l:.1f}={allowable:.2f} kN/m²"
        current_active_load = remaining_load + const_load
        result_val = current_active_load - allowable
        
        final_decision = "하부 서포트 필요" if result_val > 0 else "하부 서포트 불필요"
        
        # 상세 계산식 기록 (판정 추가)
        decision_color = "#FF4B4B" if result_val > 0 else "#1F77B4"
        check_logs.append({
            "floor": row['층이름'],
            "allowable_math": formula,
            "final_math": f"{remaining_load:.2f}(상부잔여) + {const_load:.2f}(시공) - {allowable:.2f}(허용) = {result_val:.2f} kN/m²",
            "decision": f" <span style='color:{decision_color}; font-weight:bold;'>→ {final_decision}</span>"
        })
        
        results.append({
            "검토층": row["층이름"], 
            "양생일": f"{curing_days}일", 
            "타설하중(kN/m²)": f"{current_active_load:.2f}", 
            "여유하중(kN/m²)": f"{allowable:.2f}", 
            "잔여하중(kN/m²)": f"{result_val:.2f}", 
            "판정": final_decision
        })
        
        remaining_load = result_val
        if remaining_load <= 0: break
    return total_pu, calc_logs, results, check_logs

# ==========================================
# 3. UI 렌더링
# ==========================================
st.markdown("<h1 style='color: #1e293b; font-size: 1.6rem; font-weight: 800; margin-bottom: 10px;'>본동 동바리 설치 층수 검토</h1>", unsafe_allow_html=True)

left_col, right_col = st.columns([1.3, 0.7])

with left_col:
    st.markdown("### 1. 현장 데이터 입력")
    
    # 수정된 안내 문구 (이모지 제거 및 내용 변경)
    st.markdown("""
        <div class="guide-box">
            <b>안내</b>: 전이유형에서 전이매트 선택 시 전이매트 두께에 맞게 슬래브 두께를 조정하시기 바라며, 
            전이보 선택 시 전이보 정보를 입력해주시기 바랍니다.<br>
            (층이름에 '기초', 'MAT', '매트'가 포함되거나 전이매트 선택 시 지반 지지로 간주되어 검토가 자동 종료됩니다.)
        </div>
    """, unsafe_allow_html=True)

    display_input_df = st.session_state.master_df.copy()
    if len(display_input_df) > 0:
        raw_val = str(display_input_df.iloc[0, 0])
        if "(타설층)" not in raw_val: display_input_df.iloc[0, 0] = f"{raw_val} (타설층)"

    st.data_editor(
        display_input_df, 
        column_config={
            "전이유형": st.column_config.SelectboxColumn("전이유형", options=["일반", "전이보", "전이매트"], required=True),
            "예상강도(MPa)": st.column_config.NumberColumn("예상강도(MPa)", min_value=0, max_value=100, step=1),
            "_index": None
        },
        use_container_width=True, height=350, key="main_editor", on_change=update_df_callback, hide_index=True,
        num_rows="fixed"
    )

    # 하중 정보 입력 안내 이미지
    _img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "하중정보_안내.png")
    if os.path.exists(_img_path):
        if "show_load_guide" not in st.session_state:
            st.session_state.show_load_guide = False
        _gc1, _gc2, _gc3 = st.columns([1, 1.2, 1])
        with _gc2:
            if st.button("하중 정보 입력 안내 보기 / 닫기", use_container_width=True):
                st.session_state.show_load_guide = not st.session_state.show_load_guide
        if st.session_state.show_load_guide:
            st.image(_img_path, use_container_width=True)

    transfer_floors = st.session_state.master_df[st.session_state.master_df["전이유형"] == "전이보"]["층이름"].tolist()
    transfer_details = {}
    if transfer_floors:
        st.write("---")
        st.markdown("### 전이보 상세 제원")
        
        # 보 종류(수량) 관리를 위한 세션 상태 초기화
        if "beam_counts" not in st.session_state:
            st.session_state.beam_counts = {}

        for f_name in transfer_floors:
            if not f_name: continue
            
            st.markdown(f"**{f_name}**")
            # 영향 면적 입력 (층 공통)
            _ac1, _ac2, _ac3 = st.columns(3)
            with _ac1:
                ax = st.number_input(f"x-dir (mm)", value=8000, step=100, key=f"{f_name}_ax")
            with _ac2:
                ay = st.number_input(f"y-dir (mm)", value=8000, step=100, key=f"{f_name}_ay")
            with _ac3:
                area_influence = st.number_input(f"영향 면적 (㎡)", value=0.0, help="0 입력 시 (X×Y)로 자동 계산됩니다.", key=f"{f_name}_area_influence")
            
            # 전이보 수량 입력
            _bcol1, _bcol2 = st.columns([1, 2])
            with _bcol1:
                num_beams = st.number_input(f"전이보 수량 ({f_name})", min_value=1, max_value=10, value=1, key=f"num_{f_name}")
            
            tabs = st.tabs([f"보 {i+1}" for i in range(num_beams)])
            f_beams = []
            for i in range(num_beams):
                with tabs[i]:
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        bw = st.number_input(f"보폭 (mm)", value=500, step=50, key=f"{f_name}_{i}_bw")
                    with c2:
                        bl = st.number_input(f"보길이 (mm)", value=8000, step=100, key=f"{f_name}_{i}_bl")
                    with c3:
                        bh = st.number_input(f"보춤 (mm)", value=900, step=50, key=f"{f_name}_{i}_bh")
                    with c4:
                        bn = st.number_input(f"중복수량 (EA)", value=1, min_value=1, key=f"{f_name}_{i}_bn")
                    f_beams.append({'ax':ax, 'ay':ay, 'area_influence': area_influence, 'bw':bw, 'bh':bh, 'bl':bl, 'bn':bn})
            transfer_details[f_name] = f_beams

        with st.expander("전이보 설명 (클릭하여 상세보기)", expanded=False):
            st.image(os.path.join(os.path.dirname(__file__), "전이보 설명.png"), use_container_width=True)

    total_pu, pu_logs, results_data, detail_logs = calculate_shoring_status(st.session_state.master_df, n_check, transfer_details)

    # st.markdown("### 2. 타설하중 계산")
    # ... (생략)
    
    st.markdown("### 2. 지지층 검토 결과")
    if results_data:
        res_df = pd.DataFrame(results_data)
        def color_decision(val):
            if val == "하부 서포트 필요": return f'<span class="red-text">{val}</span>'
            elif val == "하부 서포트 불필요": return f'<span class="blue-text">{val}</span>'
            return val
        res_df['판정'] = res_df['판정'].apply(color_decision)
        st.write(res_df.to_html(escape=False, index=False, classes='full-width-table'), unsafe_allow_html=True)

    with st.expander("3. 계산 근거 (클릭하여 상세 보기)", expanded=False):
        detail_html = "<div class='load-calc-box'>"
        # 1. 타설층 정보
        detail_html += "<div style='font-weight:bold; color:#0056b3; margin-bottom:5px;'>[타설층]</div>"
        for log in pu_logs:
            detail_html += f"<div style='margin-left:10px; margin-bottom:15px;'>"
            detail_html += f"<b style='font-size:16px;'>{log['floor']}</b> 타설하중 :<br>"
            
            # 전이보 환산 내역 (있는 경우에만)
            if log['beam_details']:
                detail_html += f"<span style='color:#666; font-size:15px;'>&nbsp;&nbsp;- 전이보 환산 : </span><br>"
                for b_log in log['beam_details']:
                    detail_html += f"<span style='color:#888; font-size:14px;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ㄴ {b_log}</span><br>"
                detail_html += f"<span style='color:#666; font-size:15px;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;합계 = {log['added_t_m']:.3f}m</span><br>"
            
            # 하중계산식
            t_math = f"( ({log['base_t_m']:.2f}m + {log['added_t_m']:.3f}m) × 24kN/m³ )" if log['added_t_mm'] > 0 else f"( {log['base_t_m']:.2f}m × 24kN/m³ )"
            detail_html += f"<span style='color:#666; font-size:15px;'>&nbsp;&nbsp;- 하중계산 : {t_math} + 0.4kN/m² + {log['const_load']:.2f}kN/m² = {log['floor_pu']:.2f} kN/m²</span><br>"
            detail_html += "</div>"
        detail_html += f"<div style='margin-left:10px; font-weight:bold; color:#d32f2f; font-size:18px;'>&nbsp;&nbsp;ΣPu = {total_pu:.2f} kN/m²</div>"
        
        detail_html += "<hr style='margin:15px 0; border:0; border-top:1px solid #ccc;'>"
        
        # 2. 지지층 정보
        detail_html += "<div style='font-weight:bold; color:#0056b3; margin-bottom:5px; font-size:16px;'>[지지층]</div>"
        for log in detail_logs:
            detail_html += f"<div style='margin-left:10px; margin-bottom:12px;'>"
            detail_html += f"<b style='font-size:16px;'>{log['floor']}</b> : 여유하중 계산<br>"
            detail_html += f"<span style='color:#666; font-size:15px;'>&nbsp;&nbsp;- 허용산식 : {log['allowable_math']}</span><br>"
            detail_html += f"<span style='font-size:15px;'>&nbsp;&nbsp;- 하중계산 : {log['final_math']}{log['decision']}</span>"
            detail_html += "</div>"
        
        detail_html += "</div>"
        st.markdown(detail_html, unsafe_allow_html=True)

with right_col:
    st.markdown("### 4.서포트 배치도")
    fig, ax = plt.subplots(figsize=(4, 5))
    df = st.session_state.master_df
    for i in range(len(df)):
        idx = (len(df)-1)-i; f_name = str(df.iat[idx,0]); f_type = df.iat[idx, 5]
        is_mat = any(x in f_name.upper() for x in ["기초", "MAT", "매트"]) or f_type == "전이매트"
        ax.plot([0, 10], [i*3, i*3], color='black' if is_mat else '#454545', lw=10 if is_mat else 3, zorder=3)
        ax.text(-1, i*3, f_name, va='center', ha='right', fontweight='bold', fontsize=12)
    for i in range(n_check):
        p_idx = (len(df)-1)-i-1
        if p_idx >= 0:
            for x in [2, 5, 8]: ax.plot([x, x], [p_idx*3, (p_idx+1)*3], color='red', lw=3, zorder=2)
    for res in results_data:
        if res["판정"] == "하부 서포트 필요":
            try:
                f_idx = df["층이름"].tolist().index(res["검토층"])
                p_idx = (len(df)-1)-f_idx-1
                if p_idx >= 0:
                    for x in [2, 5, 8]: ax.plot([x, x], [p_idx*3, (p_idx+1)*3], color='red', lw=3, zorder=2)
            except: continue
    ax.axis('off')
    st.pyplot(fig)