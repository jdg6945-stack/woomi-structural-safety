import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform
from datetime import datetime

# ==========================================
# 0. 환경 설정 및 스타일 (글자 크기 확대 + 가독성 강화)
# ==========================================
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='NanumGothic')

plt.rcParams['axes.unicode_minus'] = False
try:
    st.set_page_config(layout="wide", page_title="가설 동바리 검토 시스템")
except Exception:
    pass

st.markdown("""
    <style>
    /* 1. 현장 데이터 입력 표 글자 크기 확대 */
    div[data-testid="stDataEditor"] div[role="gridcell"] {
        justify-content: center !important;
        text-align: center !important;
        font-size: 16px !important;
    }
    
    /* 2. 지지층 검토 결과 표 스타일 */
    .full-width-table {
        width: 100% !important;
        border-collapse: collapse;
        margin-top: 15px;
        font-size: 17px !important;
    }
    .full-width-table th, .full-width-table td {
        text-align: center !important;
        vertical-align: middle !important;
        padding: 15px 10px !important;
        border: 1px solid #dee2e6;
    }
    .full-width-table th {
        background-color: #f1f3f5;
        font-weight: bold;
    }

    /* 3. 타설하중 계산 결과 텍스트 */
    .load-calc-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        font-size: 18px !important;
        line-height: 1.6;
    }
    .load-calc-total {
        font-size: 22px !important;
        font-weight: bold;
        color: #d32f2f;
        margin-top: 10px;
    }

    /* 4. 판정 결과 색상 */
    .red-text { color: #FF4B4B; font-weight: bold; }
    .blue-text { color: #1F77B4; font-weight: bold; }

    /* 5. 안내 문구 스타일 (수정됨) */
    .guide-box {
        background-color: #eef2f7;
        padding: 15px;
        border-radius: 8px;
        font-size: 15px;
        color: #2c3e50;
        margin-bottom: 15px;
        border-left: 5px solid #adb5bd;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

COL_THICK = "슬래브 두께(mm)"
COL_LOAD_CONST = "시공하중(kN/m²)"
COL_LOAD_EXTRA = "마감여유(kN/m²)"
COL_LOAD_LIVE = "활하중(kN/m²)"

# ==========================================
# 1. 데이터 관리 로직
# ==========================================
def reset_data(total_rows=6):
    default_floors = [f"{i}F" for i in range(total_rows, 0, -1)]
    if total_rows > 0: default_floors[-1] = "B1F(기초)"
    init_data = {
        "층이름": default_floors + [""] * (20 - len(default_floors)),
        COL_THICK: [210] * 20, "설계강도(MPa)": [30] * 20, "예상강도(MPa)": [14] * 20,
        "타설간격(일)": [7] * 20, "전이유형": ["일반"] * 20,
        COL_LOAD_EXTRA: [1.9] * 20, COL_LOAD_LIVE: [2.0] * 20, COL_LOAD_CONST: [1.0] * 20
    }
    init_data[COL_LOAD_CONST][0] = 2.5
    df = pd.DataFrame(init_data).iloc[:total_rows]
    # 타설층(첫 번째 행)의 예상강도를 '-'로 설정
    if len(df) > 0:
        df["예상강도(MPa)"] = df["예상강도(MPa)"].astype(object)
        df.iat[0, df.columns.get_loc("예상강도(MPa)")] = "-"
    st.session_state.master_df = df

def update_df_callback():
    if "main_editor" in st.session_state:
        edited = st.session_state["main_editor"]
        for row_idx, changes in edited["edited_rows"].items():
            for key, val in changes.items():
                st.session_state.master_df.iat[row_idx, st.session_state.master_df.columns.get_loc(key)] = val

if 'master_df' not in st.session_state:
    reset_data(6)

st.sidebar.header("검토 설정")
cur_rows = len(st.session_state.master_df)
new_rows = st.sidebar.number_input("전체 층수", min_value=1, max_value=20, value=cur_rows)

if new_rows != cur_rows:
    if new_rows > cur_rows:
        add_count = new_rows - cur_rows
        new_rows_df = pd.DataFrame({
            "층이름": [""] * add_count, COL_THICK: [210] * add_count, "설계강도(MPa)": [30] * add_count,
            "예상강도(MPa)": [14] * add_count, "타설간격(일)": [7] * add_count, "전이유형": ["일반"] * add_count,
            COL_LOAD_EXTRA: [1.9] * add_count, COL_LOAD_LIVE: [2.0] * add_count, COL_LOAD_CONST: [1.0] * add_count
        })
        st.session_state.master_df = pd.concat([st.session_state.master_df, new_rows_df], ignore_index=True)
    else:
        st.session_state.master_df = st.session_state.master_df.iloc[:new_rows]
    st.rerun()

n_check = 1 # 기본 타설 층수는 1층으로 고정 (14MPa 미달 시 자동으로 하중 합산됨)
# num_beam_types input removed as requested.
if st.sidebar.button("데이터 초기화"): reset_data(6); st.rerun()

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
st.markdown("<h1 style='text-align: center;'>가설 동바리 존치기간 검토</h1>", unsafe_allow_html=True)

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
            "예상강도(MPa)": st.column_config.Column("예상강도(MPa)")
        },
        use_container_width=True, height=350, key="main_editor", on_change=update_df_callback, hide_index=True
    )

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
            
            # 콤팩트한 수량 입력 UI
            num_beams = st.number_input(f"전이보 수량 ({f_name})", min_value=1, max_value=10, value=1, key=f"num_{f_name}")
            
            tabs = st.tabs([f"보 {i+1}" for i in range(num_beams)])
            f_beams = []
            for i in range(num_beams):
                with tabs[i]:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        ax = st.number_input(f"영향가로(X) (mm)", value=8000.0, key=f"{f_name}_{i}_ax")
                        ay = st.number_input(f"영향세로(Y) (mm)", value=8000.0, key=f"{f_name}_{i}_ay")
                        area_influence = st.number_input(f"영향 면적 (㎡)", value=0.0, help="0 입력 시 (X*Y)로 자동 계산됩니다.", key=f"{f_name}_{i}_area_influence")
                    with c2:
                        bw = st.number_input(f"보폭 (mm)", value=500.0, key=f"{f_name}_{i}_bw")
                        bh = st.number_input(f"보춤 (mm)", value=900.0, key=f"{f_name}_{i}_bh")
                    with c3:
                        bl = st.number_input(f"보길이 (mm)", value=8000.0, key=f"{f_name}_{i}_bl")
                        bn = st.number_input(f"수량 (EA)", value=1, min_value=1, key=f"{f_name}_{i}_bn")
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
    fig, ax = plt.subplots(figsize=(4, 7))
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