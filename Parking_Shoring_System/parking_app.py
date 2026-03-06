import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform
import os
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# 0. 환경 설정 및 스타일
# ==========================================
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='NanumGothic')

plt.rcParams['axes.unicode_minus'] = False
try:
    st.set_page_config(layout="wide", page_title="주차장 가설 동바리 설치 층 검토")
except Exception:
    pass

st.markdown("""
    <style>
    div[data-testid="stDataEditor"] div[role="gridcell"] {
        justify-content: center !important;
        text-align: center !important;
        font-size: 16px !important;
    }
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
    .full-width-table th { background-color: #f1f3f5; font-weight: bold; }
    .load-calc-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        font-size: 18px !important;
        line-height: 1.8;
    }
    .load-calc-total {
        font-size: 24px !important;
        font-weight: bold;
        color: #d32f2f;
        margin-top: 15px;
        border-top: 1px dashed #ccc;
        padding-top: 10px;
    }
    .beam-detail-item {
        font-size: 15px;
        color: #666;
        margin-left: 25px;
        border-left: 2px solid #007bff;
        padding-left: 12px;
        margin-bottom: 8px;
    }
    .highlight-thick {
        background-color: #fff3cd;
        padding: 2px 5px;
        border-radius: 4px;
        font-weight: bold;
        color: #856404;
    }
    .red-text { color: #FF4B4B; font-weight: bold; }
    .blue-text { color: #1F77B4; font-weight: bold; }
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
COL_LOAD_DEAD = "고정하중(kN/m²)" 
COL_LOAD_LIVE = "활하중(kN/m²)"

# ==========================================
# 1. 데이터 관리 로직
# ==========================================
st.sidebar.header("검토 설정")
num_floors = st.sidebar.number_input("검토 층수", value=3)
st.sidebar.divider()
st.sidebar.markdown("**단위모듈 정보**")
u_ax = st.sidebar.number_input("X방향 길이 (mm)", value=8200, key="unit_mod_x")
u_ay = st.sidebar.number_input("Y방향 길이 (mm)", value=8200, key="unit_mod_y")
u_area = st.sidebar.number_input("단위모듈 면적 (㎡)", value=0.0, help="0 입력 시 (X*Y)로 자동 계산됩니다.", key="unit_mod_area")
u_area_m2 = u_area if u_area > 0 else (u_ax * u_ay / 1e6)

n_check = 1 # 기본 타설 층수는 1층 (14MPa 미달 시 자동으로 하중 합산)
# num_beam_types removed: managed directly in the main UI via quantity input.

if 'parking_df' not in st.session_state:
    st.session_state.parking_df = pd.DataFrame({
        "층이름": ["RF", "B1F", "기초"],
        COL_THICK: [250, 150, 400],
        "설계강도(MPa)": [30.0, 30.0, 30.0],
        "예상강도(MPa)": ["-", 30.0, 30.0],
        "타설간격(일)": [28, 28, 28],
        COL_LOAD_DEAD: [22.5, 0.4, 0.4],
        COL_LOAD_LIVE: [16.0, 6.0, 6.0],
        COL_LOAD_CONST: [2.5, 1.0, 1.0]
    })

df = st.session_state.parking_df
if len(df) != num_floors:
    if len(df) < num_floors:
        diff = num_floors - len(df)
        new_rows = pd.DataFrame({
            "층이름": [f"B{len(df)-1+i}F" for i in range(diff)],
            COL_THICK: [150]*diff, "설계강도(MPa)": [30.0]*diff, "예상강도(MPa)": [30.0]*diff,
            "타설간격(일)": [28]*diff, COL_LOAD_DEAD: [0.4]*diff, COL_LOAD_LIVE: [6.0]*diff, COL_LOAD_CONST: [1.0]*diff
        })
        st.session_state.parking_df = pd.concat([df.iloc[:-1], new_rows, df.iloc[[-1]]], ignore_index=True)
    else:
        st.session_state.parking_df = pd.concat([df.iloc[:num_floors-1], df.iloc[[-1]]], ignore_index=True)
    st.rerun()

# ==========================================
# 2. UI 렌더링
# ==========================================
st.markdown("<h1 style='text-align: center;'>주차장 가설 동바리 설치 층 검토</h1>", unsafe_allow_html=True)

left_col, right_col = st.columns([1.3, 0.7])

with left_col:
    st.markdown("### 1. 현장 데이터 입력")
    st.markdown("""
        <div class="guide-box">
            <b>안내</b>: 층이름에 '기초', 'MAT', '매트'가 포함되거나 전이매트 선택 시 지반 지지로 간주되어 검토가 자동 종료됩니다.
        </div>
    """, unsafe_allow_html=True)

    df_for_edit = st.session_state.parking_df.copy()
    display_name_rf = f"{df_for_edit.iloc[0, 0]} (타설층)"
    df_for_edit.iloc[0, 0] = display_name_rf
    df_for_edit.iloc[0, 3] = "-" 

    edited_df = st.data_editor(
        df_for_edit, 
        use_container_width=True, hide_index=True, key="parking_editor"
    )
    edited_df.iloc[0, 0] = edited_df.iloc[0, 0].replace(" (타설층)", "")
    st.session_state.parking_df = edited_df.copy()

    st.divider()

    # --- 2. 보 데이터 ---
    st.markdown("### 2. 보 데이터 입력 (타설층)")
    st.markdown("""
        <div class="guide-box">
            단위 모듈 내 포함된 <b>보의 수량 및 단면 정보</b>를 입력하여 슬래브 환산 두께 및 타설 하중을 산출합니다.
        </div>
    """, unsafe_allow_html=True)
    s_thick = st.session_state.parking_df.iloc[0][COL_THICK]
    total_equiv_sum = 0
    beam_details = []

    # 콤팩트한 수량 입력 UI
    num_beams = st.number_input(f"보 종류 수량", value=1, key="parking_num_beams")
    
    tabs = st.tabs([f"보 {i+1}" for i in range(num_beams)])
    for i in range(num_beams):
        with tabs[i]:
            c1, c2 = st.columns(2)
            with c1: 
                bw = st.number_input(f"보 폭 (mm)", value=500, key=f"p_bw_{i}")
                bh = st.number_input(f"보 춤 (mm)", value=900, key=f"p_bh_{i}")
            with c2: 
                bl = st.number_input(f"보 길이 (mm)", value=8200, key=f"p_bl_{i}")
                bn = st.number_input(f"보 수량", value=1, key=f"p_bn_{i}")
            
            net_bh = bh - s_thick
            if u_area_m2 > 0:
                # 보 체적 (mm^3 -> m^3)
                vol_m3 = (bw * net_bh * bl * bn) / 1e9
                equiv_mm = (vol_m3 / u_area_m2) * 1000
                total_equiv_sum += equiv_mm
                
                area_formula = f"{u_area:.1f}㎡" if u_area > 0 else f"({u_ax}×{u_ay})㎟"
                beam_details.append(f"└ 보{i+1}: ({bw}×{net_bh}×{bl}×{bn}) / {area_formula} = {equiv_mm:.2f} mm")

    # 단위 모듈 평면도 가이드
    with st.expander("단위 모듈 평면도 (클릭하여 보기)", expanded=False):
        if os.path.exists(os.path.join(os.path.dirname(__file__), "plan.png")):
            # Pillow로 이미지 읽고 텍스트 입히기
            try:
                img = Image.open(os.path.join(os.path.dirname(__file__), "plan.png")).convert("RGB")
                draw = ImageDraw.Draw(img)
                
                # 폰트 설정 (이전 크기의 2배인 40으로 조정)
                try: 
                    font = ImageFont.truetype("malgun.ttf", 40)
                except: 
                    font = ImageFont.load_default()
                
                # X방향 길이 (550, 35)
                # Y방향 길이 (35, 500)
                curr_ax = u_ax
                curr_ay = u_ay
                
                text_x = f"{curr_ax:,.0f}"
                text_y = f"{curr_ay:,.0f}"
                
                # X방향 텍스트 박스와 텍스트
                tx_bbox = draw.textbbox((0, 0), text_x, font=font)
                tx_w, tx_h = tx_bbox[2] - tx_bbox[0], tx_bbox[3] - tx_bbox[1]
                padding = 10
                draw.rectangle([550 - tx_w//2 - padding, 35 - tx_h//2 - padding, 550 + tx_w//2 + padding, 35 + tx_h//2 + padding], fill="white")
                draw.text((550, 35), text_x, fill="black", font=font, anchor="mm")
                
                # Y방향 텍스트 박스와 텍스트
                ty_bbox = draw.textbbox((0, 0), text_y, font=font)
                ty_w, ty_h = ty_bbox[2] - ty_bbox[0], ty_bbox[3] - ty_bbox[1]
                
                txt_img = Image.new("RGBA", (ty_w + padding * 2, ty_h + padding * 2), (255, 255, 255, 255))
                txt_draw = ImageDraw.Draw(txt_img)
                txt_draw.text((padding, padding), text_y, fill="black", font=font)
                rotated_txt = txt_img.rotate(90, expand=True)
                
                img.paste(rotated_txt, (35 - rotated_txt.width//2, 500 - rotated_txt.height//2), rotated_txt)
                
                # 이미지 크기를 절반 정도로 줄여서 표시 (width=500 정도)
                st.image(img, width=500)
            except Exception as e:
                st.error(f"이미지 처리 중 오류 발생: {e}")
                st.image(os.path.join(os.path.dirname(__file__), "plan.png"), use_container_width=True)
        else:
            st.warning("plan.png 파일을 찾을 수 없습니다.")

    st.divider()

    # --- 계산 엔진 정의 (14MPa 로직 및 로그 수집 포함) ---
    def run_calculation(df_in, equiv_mm_sum, beam_logs):
        current_pu = 0
        res_list = []
        check_logs = []
        
        # 1. 타설층 하중 (ΣPu)
        row0 = df_in.iloc[0]
        sum_thick_mm = row0[COL_THICK] + equiv_mm_sum
        current_pu = (sum_thick_mm / 1000 * 24) + 0.4 + row0[COL_LOAD_CONST]
        
        res_list.append({
            "검토층": f"{row0['층이름']} (타설층)", 
            "양생일": "-", 
            "타설하중": f"{current_pu:.2f}", 
            "여유하중": "-", 
            "잔여하중": f"{current_pu:.2f}", 
            "판정": "하부 서포트 필요"
        })

        remaining_load = current_pu
        for i in range(1, len(df_in)):
            row = df_in.iloc[i]
            f_name = str(row["층이름"])
            curing_days = df_in.iloc[0:i]["타설간격(일)"].sum()
            is_mat = any(x in f_name.upper() for x in ["기초", "MAT", "매트"])
            
            if is_mat:
                res_list.append({
                    "검토층": f_name, "양생일": "-", "타설하중": "-", "여유하중": "지반 지지(MAT)", "잔여하중": "0.00", "판정": "종료(기초)"
                })
                check_logs.append({
                    "floor": f_name, "allowable_math": "지반 지지", "final_math": "MAT 기초 지붕 지지", "decision": ""
                })
                break
            
            # 14MPa 미만 체크
            est_strength = 0.0
            try: est_strength = float(row["예상강도(MPa)"])
            except: pass
            
            if est_strength < 14:
                thick_m = row[COL_THICK] / 1000
                floor_self_load = (thick_m * 24) + 0.4 + row[COL_LOAD_CONST]
                new_total_load = remaining_load + floor_self_load
                check_logs.append({
                    "floor": f_name,
                    "allowable_math": f"예상강도 {est_strength:.1f}MPa < 14MPa",
                    "final_math": f"{remaining_load:.2f}(상부) + {floor_self_load:.2f}(현재층) = {new_total_load:.2f}",
                    "decision": " <span style='color:#FF4B4B; font-weight:bold;'>→ 지지 불가 (하중 합산)</span>"
                })
                res_list.append({
                    "검토층": f"{f_name} (강도부족)", "양생일": f"{curing_days}일", 
                    "타설하중": f"{new_total_load:.2f}", "여유하중": "0.00", "잔여하중": f"{new_total_load:.2f}", "판정": "하부 서포트 필요"
                })
                remaining_load = new_total_load
                continue

            # 정상 지층 검토
            f_design = row["설계강도(MPa)"]
            is_fully_cured = (curing_days >= 28) or (est_strength >= f_design)
            ld, l = row[COL_LOAD_DEAD], row[COL_LOAD_LIVE]
            
            if is_fully_cured:
                allowable = (ld * 1.2) + (l * 1.6)
                math_all = f"({ld:.1f}×1.2 + {l:.1f}×1.6) = {allowable:.2f} kN/m²"
            else:
                allowable = ld + l
                math_all = f"{ld:.1f} + {l:.1f} = {allowable:.2f} kN/m²"
            
            p_const = row[COL_LOAD_CONST]
            current_active_load = remaining_load + p_const
            result_val = current_active_load - allowable
            
            final_decision = "하부 서포트 필요" if result_val > 0 else "하부 서포트 불필요"
            decision_color = "#FF4B4B" if result_val > 0 else "#1F77B4"
            
            check_logs.append({
                "floor": f_name,
                "allowable_math": math_all,
                "final_math": f"{remaining_load:.2f}(상부잔여) + {p_const:.1f}(시공) - {allowable:.2f}(허용) = {result_val:.2f} kN/m²",
                "decision": f" <span style='color:{decision_color}; font-weight:bold;'>→ {final_decision}</span>"
            })
            
            res_list.append({
                "검토층": f_name, "양생일": f"{curing_days}일", "타설하중": f"{current_active_load:.2f}",
                "여유하중": f"{allowable:.2f}", "잔여하중": f"{result_val:.2f}", "판정": final_decision
            })
            remaining_load = result_val
            if remaining_load <= 0: break
            
        return res_list, check_logs, current_pu

    res_data, detail_logs, final_pu = run_calculation(st.session_state.parking_df, total_equiv_sum, beam_details)

    # --- 3. 지지층 검토 결과 ---
    st.markdown("### 3. 지지층 검토 결과")
    
    if res_data:
        res_df = pd.DataFrame(res_data)
        # 헤더에 단위 추가
        res_df.columns = ["검토층", "양생일", "타설하중(kN/m²)", "여유하중(kN/m²)", "잔여하중(kN/m²)", "판정"]
        
        def color_decision(val):
            if "하부 서포트 필요" in str(val): return f'<span class="red-text">{val}</span>'
            elif "하부 서포트 불필요" in str(val): return f'<span class="blue-text">{val}</span>'
            return val
        res_df['판정'] = res_df['판정'].apply(color_decision)
        st.write(res_df.to_html(escape=False, index=False, classes='full-width-table'), unsafe_allow_html=True)

    # --- 4. 계산 근거 상세 ---
    with st.expander("4. 계산 근거 (클릭하여 상세 보기)", expanded=False):
        detail_html = "<div class='load-calc-box'>"
        # 1. 타설층
        detail_html += "<div style='font-weight:bold; color:#0056b3; margin-bottom:5px; font-size:16px;'>[타설층]</div>"
        detail_html += f"<div style='margin-left:10px; margin-bottom:15px;'>"
        detail_html += f"<b style='font-size:16px;'>{st.session_state.parking_df.iloc[0, 0]}</b> 타설하중 :<br>"
        if beam_details:
            detail_html += f"<span style='color:#666; font-size:15px;'>&nbsp;&nbsp;- 보 환산 : </span><br>"
            for b_log in beam_details:
                detail_html += f"<span style='color:#888; font-size:14px;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{b_log}</span><br>"
        
        s_thick_m = st.session_state.parking_df.iloc[0][COL_THICK] / 1000
        equiv_m = total_equiv_sum / 1000
        t_math = f"( ({s_thick_m:.2f}m + {equiv_m:.3f}m) × 24kN/m³ )" if total_equiv_sum > 0 else f"( {s_thick_m:.2f}m × 24kN/m³ )"
        detail_html += f"<span style='color:#666; font-size:15px;'>&nbsp;&nbsp;- 하중계산 : {t_math} + 0.4 + {st.session_state.parking_df.iloc[0][COL_LOAD_CONST]:.2f} = {final_pu:.2f} kN/m²</span><br>"
        detail_html += "</div>"
        detail_html += f"<div style='margin-left:10px; font-weight:bold; color:#d32f2f; font-size:18px;'>&nbsp;&nbsp;ΣPu = {final_pu:.2f} kN/m²</div>"
        detail_html += "<hr style='margin:15px 0; border:0; border-top:1px solid #ccc;'>"
        
        # 2. 지지층
        detail_html += "<div style='font-weight:bold; color:#0056b3; margin-bottom:5px; font-size:16px;'>[지지층]</div>"
        if detail_logs:
            for log in detail_logs:
                detail_html += f"<div style='margin-left:10px; margin-bottom:12px;'>"
                detail_html += f"<b style='font-size:16px;'>{log['floor']}</b> : 여유하중 계산<br>"
                detail_html += f"<span style='color:#666; font-size:15px;'>&nbsp;&nbsp;- 허용산식 : {log['allowable_math']}</span><br>"
                detail_html += f"<span style='font-size:15px;'>&nbsp;&nbsp;- 하중계산 : {log['final_math']}{log['decision']}</span>"
                detail_html += "</div>"
        else:
             detail_html += "<div style='margin-left:10px;'>검토된 지지층이 없습니다.</div>"
        detail_html += "</div>"
        st.markdown(detail_html, unsafe_allow_html=True)

with right_col:
    # --- 5. 서포트 배치도 ---
    st.markdown("### 5. 서포트 배치도")
    fig, ax = plt.subplots(figsize=(4, 4))
    f_list = df["층이름"].tolist()
    for i, name in enumerate(reversed(f_list)):
        y = i * 3
        is_mat = any(x in name.upper() for x in ["기초", "MAT", "매트"])
        ax.plot([0, 10], [y, y], color='black' if is_mat else '#454545', lw=10 if is_mat else 3, zorder=3)
        ax.text(-1, y, name, va='center', ha='right', fontweight='bold', fontsize=12)
        
    # 타설층 서포트 표시 (붉은색 라인)
    # n_check 대신 고정된 1층 표시 (14MPa 로직 결과에 따라 다르게 보일 수도 있으나 기본 시각화는 1층 기준)
    p_idx = (len(df)-1)-0-1
    if p_idx >= 0:
        for x in [2, 5, 8]: ax.plot([x, x], [p_idx*3, (p_idx+1)*3], color='red', lw=3, zorder=2)
            
    for r in res_data:
        if "하부 서포트 필요" in str(r["판정"]) and "(타설층)" not in r["검토층"]:
            try:
                # ' (강도부족)' 문자열 제거 후 찾기
                clean_name = r["검토층"].split(" (")[0]
                f_idx = df["층이름"].tolist().index(clean_name)
                p_idx = (len(df)-1)-f_idx-1
                if p_idx >= 0:
                    for x in [2, 5, 8]: ax.plot([x, x], [p_idx*3, (p_idx+1)*3], color='red', lw=3, zorder=2)
            except: continue
    ax.axis('off')
    st.pyplot(fig)