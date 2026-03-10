import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import platform
from datetime import datetime

# 페이지 설정
try:
    st.set_page_config(layout="wide", page_title="시공단계 부력 검토")
except Exception:
    pass

# 스타일 설정 (이전 화면의 사용자 정의 스타일 복구)
# 세션 상태 초기화 (기초 두께 공유용)
if "fd" not in st.session_state:
    st.session_state.fd = 900

# 스타일 설정 (이전 화면의 사용자 정의 스타일 복구)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    .stApp {
        font-family: 'Noto Sans KR', sans-serif !important;
        background-color: #f8fafc;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    [data-testid="stSidebar"], [data-testid="stHeader"],
    .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiSelect,
    .stButton button, .stTab button {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* 상단 여백 */
    [data-testid="stSidebarNav"] { padding-top: 0.5rem !important; }
    h2 { font-size: 1.1rem !important; margin-top: 0.8rem !important; margin-bottom: 0.4rem !important; color: #1e293b !important; }
    h3 { font-size: 0.95rem !important; margin-bottom: 0.3rem !important; color: #1e293b !important; }
    
    /* 입력창 스타일 - 깔끔한 사각 테두리 */
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stTextInput"] > div { border: none !important; box-shadow: none !important; background: transparent !important; }
    [data-baseweb="base-input"],
    [data-baseweb="base-input"] > div { border: none !important; box-shadow: none !important; background-color: #ffffff !important; }
    div[data-baseweb="input"],
    div[data-baseweb="number-input"] { background-color: #ffffff !important; border: none !important; outline: 1px solid #94a3b8 !important; outline-offset: -1px !important; border-radius: 4px !important; box-shadow: none !important; min-height: 32px !important; height: auto !important; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; border: none !important; outline: 1px solid #94a3b8 !important; outline-offset: -1px !important; border-radius: 4px !important; box-shadow: none !important; }
    /* 탭 하단 선 제거 */
    div[data-baseweb="tab-highlight"] { display: none !important; }
    div[data-baseweb="tab-list"] { border-bottom: none !important; }
    input[type=number] { 
        -moz-appearance: textfield; 
        font-size: 12px !important; 
        padding: 4px 8px !important;
    }
    /* 테이블 배경 흰색 */
    div[data-testid="stTable"] table { background-color: #ffffff !important; }
    div[data-testid="stTable"] th, div[data-testid="stTable"] td { background-color: #ffffff !important; }
    
    /* 라벨 관련 스타일 */
    div[data-testid="stWidgetLabel"] p {
        font-size: 11.5px !important;
        margin-bottom: 2px !important;
        line-height: 1.2 !important;
    }
    
    /* 요소 간격 조절 */
    .stNumberInput { margin-bottom: 2px !important; }
    .stCheckbox { margin-bottom: 2px !important; }
    div[data-testid="stVerticalBlock"] > div { border: none !important; gap: 0.2rem !important; }
    
    /* 사이드바 여백 축소 */
    div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] { gap: 0.1rem !important; }
    hr { margin: 0.5rem 0 !important; }
    
    .sub-title { 
        background-color: #64748b; color: white; padding: 2px 8px; border-radius: 4px; 
        font-weight: bold; margin-top: 3px; margin-bottom: 2px; font-size: 11px; 
    }
    .section-title { 
        color: #1e293b; border-bottom: 1.5px solid #1e293b; padding-bottom: 2px; 
        margin-top: 8px; margin-bottom: 6px; font-weight: bold; font-size: 14.5px;
    }
    .result-container-ok { 
        background-color: #3b82f6; color: white; padding: 8px; border-radius: 6px; 
        text-align: center; font-size: 16px; font-weight: bold; margin: 8px 0; 
    }
    .result-container-ng { 
        background-color: #dc2626; color: white; padding: 8px; border-radius: 6px; 
        text-align: center; font-size: 16px; font-weight: bold; margin: 8px 0; 
    }
    
    /* 메트릭(결과 수치) 크기 축소 */
    div[data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: bold !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    
    /* 탭 스타일 조정 */
    button[data-baseweb="tab"] { padding: 4px 12px !important; font-size: 12px !important; }
    
    /* 테이블 스타일 */
    div[data-testid="stTable"] table { width: 100% !important; border: 1px solid #e2e8f0 !important; }
    div[data-testid="stTable"] th, div[data-testid="stTable"] td { padding: 4px 6px !important; font-size: 11px !important; border: 1px solid #e2e8f0 !important; }
    
    div[data-testid="stTable"] th:nth-child(1), div[data-testid="stTable"] td:nth-child(1) { display: none !important; }
    div[data-testid="stTable"] th:nth-child(2), div[data-testid="stTable"] td:nth-child(2) { width: 110px !important; background-color: #fdfdfd; }
    div[data-testid="stTable"] th:nth-child(4), div[data-testid="stTable"] td:nth-child(4) { width: 95px !important; text-align: right !important; font-weight: bold; }

    /* 이미지 중앙 정렬 */
    [data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
    }
    [data-testid="stImage"] img {
        margin: 0 auto !important;
    }

    @media print {
        @page { size: A4; margin: 8mm; }
        .no-print { display: none !important; }
        .print-only { display: block !important; }
    }
    .print-only { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 이미지 함수
def get_font(size):
    """시스템별 한글 폰트 로드 (저장소 내 직접 업로드 폰트 우선)"""
    _local_font = os.path.join(os.path.dirname(os.path.abspath(__file__)), "malgunbd.ttf")
    try:
        return ImageFont.truetype(_local_font, size)
    except:
        pass

    system = platform.system()
    try:
        if system == "Windows":
            return ImageFont.truetype("malgunbd.ttf", size)
        elif system == "Darwin": # macOS
            return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
        else: # Linux (Streamlit Cloud)
            paths = [
                "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf", 
                "/usr/share/fonts/nanum/NanumGothicBold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
            ]
            for path in paths:
                try: return ImageFont.truetype(path, size)
                except: continue
            return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def overlay_text(img_path, measurements):
    try: img = Image.open(img_path).convert("RGB")
    except Exception: img = Image.new("RGB", (1000, 800), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)
    
    font = get_font(45)
    
    for pos, val, is_vertical in measurements:
        text = f"{val:,}"; tw, th = draw.textbbox((0, 0), text, font=font)[2:4]; padding = 12; x, y = pos
        if is_vertical:
            txt_img = Image.new("RGBA", (tw + padding * 2, th + padding * 2), (255, 255, 255, 255))
            ImageDraw.Draw(txt_img).text((padding, padding), text, fill="black", font=font)
            rotated = txt_img.rotate(90, expand=True); img.paste(rotated, (x-rotated.width//2, y-rotated.height//2), rotated)
        else:
            draw.rectangle([x-tw//2-padding, y-th//2-padding, x+tw//2+padding, y+th//2+padding], fill="white")
            draw.text((x, y), text, fill="black", font=font, anchor="mm")
    return img

def draw_dynamic_section(h_soil, floor_heights, fd, gl_minus):
    scale = 2
    img_h = 420 * scale
    img_w = 450 * scale
    
    num_f = len(floor_heights)
    top_margin = 50 * scale
    bottom_margin = 100 * scale
    soil_h_px = 60 * scale
    foot_h_px = 50 * scale
    
    available_h = img_h - top_margin - bottom_margin - soil_h_px - foot_h_px
    row_h_px = available_h / num_f
    
    img = Image.new("RGB", (img_w, img_h), color="white")
    draw = ImageDraw.Draw(img)
    
    try: font_size = 18 if num_f <= 2 else (16 if num_f <= 4 else 14)
    except: font_size = 15
    font = get_font(font_size * scale)
    
    gl_y = top_margin
    draw.line([(30 * scale, gl_y), (320 * scale, gl_y)], fill="black", width=2 * scale)
    draw.text((325 * scale, gl_y), "GL", fill="red", font=font, anchor="lm")
    
    draw.rectangle([100 * scale, gl_y, 300 * scale, gl_y + soil_h_px], fill="#F0F0F0", outline="black", width=1 * scale)
    draw.line([(80 * scale, gl_y), (80 * scale, gl_y + soil_h_px)], fill="black", width=1 * scale)
    draw.text((75 * scale, gl_y + soil_h_px/2), f"{h_soil:,}", fill="black", font=font, anchor="rm")
    draw.text((200 * scale, gl_y + soil_h_px/2), "흙높이", fill="#666666", font=font, anchor="mm")
    
    curr_y = gl_y + soil_h_px
    for i, fh in enumerate(floor_heights):
        draw.rectangle([100 * scale, curr_y, 300 * scale, curr_y + row_h_px], outline="black", width=1 * scale)
        draw.line([(100 * scale, curr_y), (300 * scale, curr_y)], fill="black", width=3 * scale)
        draw.line([(80 * scale, curr_y), (80 * scale, curr_y + row_h_px)], fill="black", width=1 * scale)
        draw.text((75 * scale, curr_y + row_h_px/2), f"{fh:,}", fill="black", font=font, anchor="rm")
        draw.text((200 * scale, curr_y + row_h_px/2), f"B{i+1}F", fill="#666666", font=font, anchor="mm")
        curr_y += row_h_px
        
    foot_h = 50 * scale
    draw.rectangle([50 * scale, curr_y, 350 * scale, curr_y + foot_h], fill="#E0E0E0", outline="black", width=1 * scale)
    draw.text((200 * scale, curr_y + foot_h/2), f"기초 ({fd:,})", fill="black", font=font, anchor="mm")

    actual_depth = gl_minus * 1000
    total_soil_floor_h = h_soil + sum(floor_heights)
    total_dwg_h = soil_h_px + (len(floor_heights) * row_h_px)
    
    gwl_y = gl_y
    if actual_depth <= h_soil:
        ratio = actual_depth / h_soil if h_soil > 0 else 0
        gwl_y = gl_y + (ratio * soil_h_px)
    else:
        gwl_y = gl_y + soil_h_px
        rem = actual_depth - h_soil
        for fh in floor_heights:
            if rem <= fh: gwl_y += (rem / fh * row_h_px); rem = 0; break
            else: gwl_y += row_h_px; rem -= fh
        if rem > 0: gwl_y += (min(rem / 1000, 1.0) * foot_h)

    draw.line([(310 * scale, gwl_y), (340 * scale, gwl_y)], fill="blue", width=1 * scale)
    tri_h = 10 * scale
    draw.polygon([(325 * scale, gwl_y), ((325-6)*scale, gwl_y-tri_h), ((325+6)*scale, gwl_y-tri_h)], outline="blue", fill="white")
    draw.line([(321 * scale, gwl_y + 4 * scale), (329 * scale, gwl_y + 4 * scale)], fill="blue", width=1 * scale)
    draw.text((345 * scale, gwl_y), f"(GL-{gl_minus})", fill="blue", font=font, anchor="lm")
        
    return img

# 1. 사이드바 설정
with st.sidebar:
    st.header("검토 설정")
    num_floors = st.number_input("검토 층수(기초 포함)", min_value=1, max_value=10, value=2)
    st.divider()

    sidebar_tabs = st.tabs(["기본", "단면", "수위"])
    
    with sidebar_tabs[0]:
        x_dist = st.number_input("X방향 길이 (mm)", value=8200)
        y_dist = st.number_input("Y방향 길이 (mm)", value=8200)
        area = (x_dist * y_dist) / 10**6

    with sidebar_tabs[1]:
        h_soil = st.number_input("흙 높이 (mm)", value=1200)
        floor_heights = []
        for i in range(num_floors):
            h = st.number_input(
                f"B{i+1}F 층고 (mm)", value=4050 if i == 0 else 5380, key=f"h_{i}"
            )
            floor_heights.append(h)

    with sidebar_tabs[2]:
        gl_minus = st.number_input("지하수위(GL-m)", value=2.35)
        target_fs = st.number_input("목표 안전율", value=1.2)
        unit_c = st.number_input("콘크리트 중량(kN/m³)", value=24.0)

# 메인 타이틀
st.markdown("<h1 style='color: #1e293b; font-size: 1.6rem; font-weight: 800; margin-bottom: 10px;'>시공단계 부력 검토</h1>", unsafe_allow_html=True)

main_left, main_right = st.columns([1.3, 0.7], gap="large")

with main_right:
    _plan_path = os.path.join(os.path.dirname(__file__), "plan.png")
    if os.path.exists(_plan_path):
        st.markdown("<h3 style='color:#1e3a8a; margin-bottom:0px;'>[평면 정보]</h3>", unsafe_allow_html=True)
        _plan_img = overlay_text(_plan_path, [((550, 30), x_dist, False), ((30, 500), y_dist, True)])
        _pw, _ph = _plan_img.size
        _plan_img = _plan_img.resize((int(_pw * 1/2), int(_ph * 1/2)))
        st.image(_plan_img, use_container_width=False)
    st.markdown("<h3 style='color:#1e3a8a; margin-bottom:0px;'>[층고 정보]</h3>", unsafe_allow_html=True)
    st.image(draw_dynamic_section(h_soil, floor_heights, st.session_state.fd, gl_minus), use_container_width=True)

with main_left:
    st.info("각 지하층 탭에서 시공 완료 여부(체크박스)를 선택하여 단계별 검토가 가능합니다.")

    main_tabs = st.tabs(["1. 설계하중 설정", "2. 부재정보 및 시공단계 설정"])

    with main_tabs[0]:
        ld_cols = st.columns(1 + num_floors)
        with ld_cols[0]:
            with st.container(border=True):
                st.markdown("**지붕층 (Roof)**")
                t_topping = st.number_input("Topping (mm)", value=1100, key="ld_t_top")
                t_plain_r = st.number_input("무근 Con'c (mm)", value=100, key="ld_t_pr_r")
                t_slab_r = st.number_input("슬래브 두께 (mm)", value=250, key="ld_t_slab_r")
                l_cl_r = st.number_input("Ceiling (kN/㎡)", value=0.3, key="ld_l_cl_r")
                roof_load = (18 * t_topping / 1000) + (23 * t_plain_r / 1000) + (unit_c * t_slab_r / 1000) + l_cl_r
                st.caption(f"하중: {roof_load:.2f} kN/㎡")

        floor_load_data = []
        for i in range(num_floors):
            with ld_cols[i+1]:
                with st.container(border=True):
                    if i < num_floors - 1:
                        st.markdown(f"**지하 {i+1}층 (B{i+1}F)**")
                        t_slab_i = st.number_input("슬래브 두께 (mm)", value=150, key=f"ld_slab_{i}")
                        l_cl_i = st.number_input("Ceiling (kN/㎡)", value=0.3, key=f"ld_cl_{i}")
                        fl_i = (unit_c * t_slab_i / 1000) + l_cl_i
                        floor_load_data.append({"tf": t_slab_i, "fl": fl_i, "tp": 0, "lc": l_cl_i})
                    else:
                        st.markdown(f"**지하 {i+1}층 (B{i+1}F)**")
                        t_plain_i = st.number_input("무근 Con'c (mm)", value=100, key=f"ld_plain_{i}")
                        t_slab_i = st.number_input("내수압슬래브 두께 (mm)", value=400, key=f"ld_slab_{i}")
                        fl_i = (23 * t_plain_i / 1000) + (unit_c * t_slab_i / 1000)
                        floor_load_data.append({"tf": t_slab_i, "fl": fl_i, "tp": t_plain_i, "lc": 0})
                    st.caption(f"하중: {fl_i:.2f} kN/㎡")


    with main_tabs[1]:

        tab_names = ["지붕층 (Roof)"] + [f"지하 {i+1}층 (B{i+1}F)" for i in range(num_floors)] + ["기초 (Footing)"]
        tabs = st.tabs(tab_names)

        with tabs[0]:
            is_roof_done = st.checkbox("지붕층 시공 완료", value=True, key="is_roof_done_chk")
            bc1, bc2, bc3 = st.columns(3)
            with bc1: 
                with st.container(border=True):
                    st.markdown("**B1**")
                    w1, h1 = st.columns(2)
                    bw_rb1 = w1.number_input("폭(mm)", 500, key="brb1"); bh_rb1 = h1.number_input("높이(mm)", 900, key="hrb1")
            with bc2: 
                with st.container(border=True):
                    st.markdown("**G1**")
                    w2, h2 = st.columns(2)
                    bw_rg1 = w2.number_input("폭(mm)", 500, key="brg1"); bh_rg1 = h2.number_input("높이(mm)", 900, key="hrg1")
            with bc3: 
                with st.container(border=True):
                    st.markdown("**G2**")
                    w3, h3 = st.columns(2)
                    bw_rg2 = w3.number_input("폭", 700, key="brg2"); bh_rg2 = h3.number_input("높이", 900, key="hrg2")

        floor_inputs = []
        for i in range(num_floors):
            with tabs[i+1]:
                is_f_done = st.checkbox(f"지하 {i+1}층 시공 완료", value=True, key=f"f_done_{i}")
                fld = floor_load_data[i]
                curr_tf, curr_fl, curr_tp, curr_lc = fld["tf"], fld["fl"], fld["tp"], fld["lc"]
                fc1, fc2 = st.columns([2.5, 0.7])
                with fc1:
                    fbc1, fbc2, fbc3 = st.columns(3)
                    with fbc1: 
                        with st.container(border=True):
                            st.markdown("**B1**")
                            w_b, h_b = st.columns(2)
                            bw_b1 = w_b.number_input("폭(mm)", 400, key=f"bb1_{i}"); bh_b1 = h_b.number_input("높이(mm)", 600, key=f"hb1_{i}")
                    with fbc2:
                        with st.container(border=True):
                            st.markdown("**G1**")
                            w_g1, h_g1 = st.columns(2)
                            bw_g1 = w_g1.number_input("폭(mm)", 400, key=f"bg1_{i}"); bh_g1 = h_g1.number_input("높이(mm)", 600, key=f"hg1_{i}")
                    with fbc3:
                        with st.container(border=True):
                            st.markdown("**G2**")
                            w_g2, h_g2 = st.columns(2)
                            bw_g2 = w_g2.number_input("폭(mm)", 500, key=f"bg2_{i}"); bh_g2 = h_g2.number_input("높이(mm)", 600, key=f"hg2_{i}")
                with fc2:
                    with st.container(border=True):
                        st.markdown("**기둥**")
                        w_c, h_c = st.columns(2)
                        bw_c = w_c.number_input("가로(mm)", 500, key=f"bc_{i}"); bh_c = h_c.number_input("세로(mm)", 700, key=f"hc_{i}")
                floor_inputs.append({"tf": curr_tf, "fl": curr_fl, "tp": curr_tp, "lc": curr_lc, "bw_b1": bw_b1, "bh_b1": bh_b1, "bw_g1": bw_g1, "bh_g1": bh_g1, "bw_g2": bw_g2, "bh_g2": bh_g2, "bw_c": bw_c, "bh_c": bh_c, "done": is_f_done})

        with tabs[-1]:
            st.info("기초는 시공 완료를 가정합니다.")
            ftc1, ftc2, ftc3 = st.columns(3)
            fw = ftc1.number_input("기초 가로(mm)", 3000, key="ft_w")
            flv = ftc2.number_input("기초 세로(mm)", 3000, key="ft_l")
            fd = ftc3.number_input("기초 두께(mm)", value=900, key="fd_main")
            st.session_state.fd = fd

    # ---------------------------------------------------------
    # 계산 로직
    # ---------------------------------------------------------
    def get_step(w, h, t, l, m): return unit_c * (w/1000) * (h/1000 - t/1000) * l * m, f"{unit_c} x {w/1000} x ({h/1000} - {t/1000}) x {l} x {m}"

    total_w = 0; roof_calc = []; floor_calcs = []
    m_r = 1.0 if is_roof_done else 0.0
    w_rs = roof_load * area * m_r
    total_w += w_rs
    roof_calc.append(["지붕층 슬래브", f"({18}*({t_topping/1000}) + {23}*({t_plain_r/1000}) + {unit_c}*({t_slab_r/1000}) + {l_cl_r}) x {area:.2f} x {m_r}", f"{w_rs:,.2f}"])
    v1, e1 = get_step(bw_rb1, bh_rb1, t_slab_r, x_dist/1000, m_r); roof_calc.append(["지붕층 B1", e1, f"{v1:,.2f}"]); total_w += v1
    v2, e2 = get_step(bw_rg1, bh_rg1, t_slab_r, y_dist/1000, m_r); roof_calc.append(["지붕층 G1", e2, f"{v2:,.2f}"]); total_w += v2
    v3, e3 = get_step(bw_rg2, bh_rg2, t_slab_r, x_dist/1000, m_r); roof_calc.append(["지붕층 G2", e3, f"{v3:,.2f}"]); total_w += v3

    for i, f in enumerate(floor_inputs):
        fh = floor_heights[i]/1000; m_f = 1.0 if f["done"] else 0.0; f_rows = []
        w_c = unit_c * (f["bw_c"]/1000) * (f["bh_c"]/1000) * fh * m_f
        f_rows.append([f"지하{i+1}층 기둥", f"{unit_c} x {f['bw_c']/1000} x {f['bh_c']/1000} x {fh} x {m_f}", f"{w_c:,.2f}"]); total_w += w_c
        if i == num_floors-1:
            fa = (fw*flv)/10**6; w_sn = f["fl"]*(area-fa)*m_f; w_ft = (f["fl"] + unit_c*(fd/1000 - f["tf"]/1000))*fa
            f_expr = f"({23}*({f['tp']/1000}) + {unit_c}*({f['tf']/1000}))"
            f_rows.append([f"지하{i+1}층 슬래브", f"{f_expr} x ({area:.2f}-{fa:.2f}) x {m_f}", f"{w_sn:,.2f}"])
            f_rows.append([f"지하{i+1}층 기초부", f"({f_expr} + {unit_c} x ({fd/1000}-{f['tf']/1000})) x {fa:.2f}", f"{w_ft:,.2f}"])
            total_w += (w_sn + w_ft)
        else:
            ws = f["fl"]*area*m_f; f_expr = f"({unit_c}*({f['tf']/1000}) + {f['lc']})"
            f_rows.append([f"지하{i+1}층 슬래브", f"{f_expr} x {area:.2f} x {m_f}", f"{ws:,.2f}"]); total_w += ws
            vb1, eb1 = get_step(f["bw_b1"], f["bh_b1"], f["tf"], x_dist/1000, m_f); f_rows.append([f"지하{i+1}층 B1", eb1, f"{vb1:,.2f}"]); total_w += vb1
            vg1, eg1 = get_step(f["bw_g1"], f["bh_g1"], f["tf"], y_dist/1000, m_f); f_rows.append([f"지하{i+1}층 G1", eg1, f"{vg1:,.2f}"]); total_w += vg1
            vg2, eg2 = get_step(f["bw_g2"], f["bh_g2"], f["tf"], x_dist/1000, m_f); f_rows.append([f"지하{i+1}층 G2", eg2, f"{vg2:,.2f}"]); total_w += vg2
        floor_calcs.append(f_rows)

    ht = (h_soil+sum(floor_heights))/1000; wh = ht - gl_minus; fa = (fw*flv)/10**6
    u1 = 10 * (wh + floor_inputs[-1]["tf"]/1000) * (area-fa); u2 = 10 * (wh + fd/1000) * fa
    u_total = u1 + u2; fs_val = total_w / u_total if u_total > 0 else 0

    # ---------------------------------------------------------
    # 3. 검토 결과
    # ---------------------------------------------------------
    st.markdown("<h2 class='section-title'>검토 결과</h2>", unsafe_allow_html=True)
    res1, res2, res3 = st.columns(3)
    res1.metric("총 하중 (ΣW)", f"{total_w:,.2f} kN")
    res2.metric("총 부력 (ΣU)", f"{u_total:,.2f} kN")
    res3.metric("안전율 (FS)", f"{fs_val:.4f}")

    if fs_val >= target_fs:
        st.markdown(f"<div class='result-container-ok'>판정 : OK ({fs_val:.4f} ≥ {target_fs})</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='result-container-ng'>판정 : NG ({fs_val:.4f} < {target_fs})</div>", unsafe_allow_html=True)
        st.error("부력 대책 수립이 필요합니다.")

    # ---------------------------------------------------------
    # 4. 데이터 보기 및 PDF 출력용 섹션
    # ---------------------------------------------------------
    st.divider()
    if st.button("계산 근거 보기"):
        st.info("이제 Ctrl + P를 눌러 PDF로 저장하세요.")

        st.markdown(f"""
            <div class="print-only">
                <h1>시공단계 부력 검토 상세 보고서</h1>
                <p>출력 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
            </div>
        """, unsafe_allow_html=True)

        with st.expander("지붕층(Roof) 상세", expanded=True):
            st.table(pd.DataFrame(roof_calc, columns=["부재명", "상세 산식", "하중(kN)"]))
        for i, floor_data in enumerate(floor_calcs):
            with st.expander(f"지하 {i+1}층 상세", expanded=True):
                st.table(pd.DataFrame(floor_data, columns=["부재명", "상세 산식", "하중(kN)"]))
        with st.expander("부력(U) 상세", expanded=True):
            u_rows = [
                ["일반구간 부력 (U1)", f"10 x ({wh:.3f} + {floor_inputs[-1]['tf']/1000}) x ({area:.2f} - {fa:.2f})", f"{u1:,.2f}"],
                ["기초구간 부력 (U2)", f"10 x ({wh:.3f} + {fd/1000}) x {fa:.2f}", f"{u2:,.2f}"],
                ["총 부력 합계 (ΣU)", "U1 + U2", f"{u_total:,.2f}"]
            ]
            st.table(pd.DataFrame(u_rows, columns=["구분", "상세 산식", "결과(kN)"]))
