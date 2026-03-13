# -*- coding: utf-8 -*-
# calculator.py — ASTM E1300 기반 IGU 추천 + 층별 풍하중 연동
# - 화면: #층별 추천(그룹화)만 출력(요약)
# - PDF: 요약 + 상세(계산 근거) + 전 층 “조합 근거” 포함
# - “조합 근거”에서 각 층의 채택 조합은 **볼드 표시**
# - 8mm/FT 유무와 관계없이 모든 층의 조합 근거를 간단하게 표기

import math
from typing import Dict, List, Tuple, Optional

# ---------------- 처짐 기준 설정 ----------------
DEFLECTION_MODE = "ratio"     # "ratio" | "abs" | "both_min"
DEFLECTION_VALUE = 60.0       # ratio면 60.0(=L/60), abs면 mm값(예: 25.0)

def get_deflection_limit_mm(a_mm: int, b_mm: int) -> float:
    L = min(a_mm, b_mm)
    if DEFLECTION_MODE == "ratio":
        return L / max(1e-9, DEFLECTION_VALUE)
    elif DEFLECTION_MODE == "abs":
        return float(DEFLECTION_VALUE)
    elif DEFLECTION_MODE == "both_min":
        ratio_mm = L / max(1e-9, DEFLECTION_VALUE)
        abs_mm = float(DEFLECTION_VALUE)
        return min(ratio_mm, abs_mm)
    return L / 60.0

# ---------------- ASTM 표 데이터 ----------------
NFL_DATA = {
    5: [
        (2200, 2000, 0.964), (2200, 1900, 1.000), (2200, 1800, 1.061), (2200, 1700, 1.116),
        (2200, 1600, 1.175), (2200, 1400, 1.296), (2200, 1200, 1.370), (2200, 1000, 1.356),
        (2000, 2000, 1.048), (2000, 1800, 1.155), (2000, 1600, 1.271), (2000, 1400, 1.415),
        (2000, 1200, 1.535), (2000, 1000, 1.546), (1600, 1000, 2.064), (1600, 800, 2.130),
        (1600, 600, 2.771), (1400, 1000, 2.395), (1400, 800, 2.487), (1200, 1000, 2.777),
        (1200, 800, 3.021), (1000, 800, 3.678), (1000, 600, 4.276),
    ],
    6: [
        (2200, 2000, 1.261), (2200, 1900, 1.322), (2200, 1800, 1.383), (2200, 1700, 1.442),
        (2200, 1600, 1.496), (2200, 1400, 1.602), (2200, 1200, 1.644), (2200, 1000, 1.703),
        (2000, 2000, 1.373), (2000, 1800, 1.500), (2000, 1600, 1.652), (2000, 1400, 1.781),
        (2000, 1200, 1.853), (2000, 1000, 1.900), (1600, 1000, 2.476), (1600, 800, 2.782),
        (1600, 600, 4.000), (1400, 1000, 2.892), (1400, 800, 3.218), (1200, 1000, 3.426),
        (1200, 800, 3.797), (1000, 800, 4.591), (1000, 600, 5.806),
    ],
    8: [
        (2200, 2000, 1.819), (2200, 1900, 1.874), (2200, 1800, 1.925), (2200, 1700, 1.969),
        (2200, 1600, 2.018), (2200, 1400, 2.107), (2200, 1200, 2.237), (2200, 1000, 2.596),
        (2000, 2000, 1.943), (2000, 1800, 2.096), (2000, 1600, 2.239), (2000, 1400, 2.211),
        (2000, 1200, 2.462), (2000, 1000, 2.806), (1600, 1000, 3.592), (1600, 800, 4.502),
        (1600, 600, 7.000), (1400, 1000, 4.120), (1400, 800, 5.000), (1200, 1000, 4.817),
        (1200, 800, 6.004), (1000, 800, 6.855), (1000, 600, 9.786),
    ],
}

GTF_TABLE = {
    ("AN", "AN"): (0.9, 0.9),
    ("HS", "AN"): (1.9, 1.0),
    ("FT", "AN"): (3.8, 1.0),
    ("AN", "HS"): (1.0, 1.9),
    ("HS", "HS"): (1.8, 1.8),
    ("FT", "HS"): (3.8, 1.9),
    ("AN", "FT"): (1.0, 3.8),
    ("HS", "FT"): (1.9, 3.8),
    ("FT", "FT"): (3.6, 3.6),
}

LSF_TABLE = {
    (5, 5): (0.5, 0.5),
    (6, 5): (0.643, 0.357),
    (8, 5): (0.811, 0.189),
    (5, 6): (0.357, 0.643),
    (6, 6): (0.5, 0.5),
    (8, 6): (0.704, 0.296),
    (5, 8): (0.189, 0.811),
    (6, 8): (0.296, 0.704),
    (8, 8): (0.5, 0.5),
}

MIN_EFFECTIVE_THICKNESS_MM = {5: 4.57, 6: 5.56, 8: 7.42}
E_KN_M2 = 7.17e7  # kN/m^2


  # 층별 추천시 아래 순서대로 추천됨 (1순위 : 두께 , 2순위 : 재질 / 8mm 및 강화유리는 후순위)
COMBOS = [
    # 5mm (AN → HS → FT)
    (5, 5, "AN", "AN"),
    (5, 5, "HS", "AN"),
    (5, 5, "HS", "HS"),

    # 6mm (AN → HS → FT)
    (6, 6, "AN", "AN"),
    (6, 6, "HS", "AN"),
    (6, 6, "HS", "HS"),

    # 8mm (AN → HS → FT)
    (8, 8, "AN", "AN"),
    (8, 8, "HS", "AN"),
    (8, 8, "HS", "HS"),

    # FT 포함 (두께 동일하게 5 → 6 → 8 순)
    (5, 5, "FT", "AN"),
    (6, 6, "FT", "AN"),
    (8, 8, "FT", "AN"),

    (5, 5, "FT", "HS"),
    (6, 6, "FT", "HS"),
    (8, 8, "FT", "HS"),

    (5, 5, "FT", "FT"),
    (6, 6, "FT", "FT"),
    (8, 8, "FT", "FT"),
]



# ---------- 유틸 ----------
def get_nearest_nfl(thickness_mm: int, long_side_mm: int, short_side_mm: int) -> Tuple[float, int, int]:
    data = NFL_DATA.get(thickness_mm)
    if not data:
        raise ValueError(f"No NFL data for thickness {thickness_mm} mm")
    L = max(long_side_mm, short_side_mm)
    S = min(long_side_mm, short_side_mm)
    nearest = min(data, key=lambda r: abs(r[0] - L) + abs(r[1] - S))
    return nearest[2], nearest[0], nearest[1]  # (nfl, L_used, S_used)

def calc_lr_pair(t1: int, t2: int, type1: str, type2: str,
                 long_side_mm: int, short_side_mm: int):
    nfl1, nfl1_L, nfl1_S = get_nearest_nfl(t1, long_side_mm, short_side_mm)
    nfl2, nfl2_L, nfl2_S = get_nearest_nfl(t2, long_side_mm, short_side_mm)
    gtf1, gtf2 = GTF_TABLE[(type1, type2)]
    lsf1, lsf2 = LSF_TABLE[(t1, t2)]
    lr1 = nfl1 * gtf1 / lsf1
    lr2 = nfl2 * gtf2 / lsf2
    return lr1, lr2, nfl1, nfl2, gtf1, gtf2, lsf1, lsf2, nfl1_L, nfl1_S, nfl2_L, nfl2_S

def compute_r_values(ar: float):
    ro = 0.553 - 3.83 * ar + 1.11 * (ar ** 2) - 0.0969 * (ar ** 3)
    r1 = -2.29 + 5.83 * ar - 2.17 * (ar ** 2) + 0.2067 * (ar ** 3)
    r2 = 1.485 - 1.908 * ar + 0.815 * (ar ** 2) - 0.0822 * (ar ** 3)
    return ro, r1, r2

def compute_deflection_mm(design_pressure_kN_m2: float, ls_factor: float,
                          a_mm: int, b_mm: int, thickness_effective_mm: float):
    p = design_pressure_kN_m2 * ls_factor
    a_m = max(a_mm, b_mm) / 1000.0
    b_m = min(a_mm, b_mm) / 1000.0
    ar = a_m / b_m
    t_m = thickness_effective_mm / 1000.0
    t_mm = thickness_effective_mm

    ro, r1, r2 = compute_r_values(ar)
    inner = p * (a_m * b_m) ** 2 / (E_KN_M2 * (t_m ** 4))
    info = {"ar": ar, "ro": ro, "r1": r1, "r2": r2, "inner": inner}

    if inner <= 1.0:
        info["note"] = "inner <= 1 → ln(ln(.)) 불가 → 보수적으로 fail"
        return float("inf"), info

    x = math.log(math.log(inner))
    info["x"] = x
    w_mm = t_mm * math.exp(ro + r1 * x + r2 * (x ** 2))

    info["w_allow_mm"] = get_deflection_limit_mm(a_mm, b_mm)
    return w_mm, info

def check_combo_with_deflection(design_pressure_kN_m2: float, long_side_mm: int, short_side_mm: int,
                                t1: int, t2: int, type1: str, type2: str) -> dict:
    (lr1, lr2, nfl1, nfl2, gtf1, gtf2, lsf1, lsf2,
     nfl1_L, nfl1_S, nfl2_L, nfl2_S) = calc_lr_pair(t1, t2, type1, type2, long_side_mm, short_side_mm)

    status_lr1 = (design_pressure_kN_m2 / lr1) < 1.0
    status_lr2 = (design_pressure_kN_m2 / lr2) < 1.0

    t_eff1 = MIN_EFFECTIVE_THICKNESS_MM[t1]
    t_eff2 = MIN_EFFECTIVE_THICKNESS_MM[t2]
    w1_mm, info1 = compute_deflection_mm(design_pressure_kN_m2, lsf1, long_side_mm, short_side_mm, t_eff1)
    w2_mm, info2 = compute_deflection_mm(design_pressure_kN_m2, lsf2, long_side_mm, short_side_mm, t_eff2)

    status_def1 = (w1_mm <= info1.get("w_allow_mm", float("-inf"))) if (math.isfinite(w1_mm) and "w_allow_mm" in info1) else False
    status_def2 = (w2_mm <= info2.get("w_allow_mm", float("-inf"))) if (math.isfinite(w2_mm) and "w_allow_mm" in info2) else False

    ok_lr = status_lr1 and status_lr2
    ok_def = status_def1 and status_def2
    ok_all = ok_lr and ok_def

    return {
        "lr1": lr1, "lr2": lr2, "nfl1": nfl1, "nfl2": nfl2,
        "gtf1": gtf1, "gtf2": gtf2, "lsf1": lsf1, "lsf2": lsf2,
        "nfl1_L": nfl1_L, "nfl1_S": nfl1_S, "nfl2_L": nfl2_L, "nfl2_S": nfl2_S,
        "status_lr1": status_lr1, "status_lr2": status_lr2,
        "w1_mm": w1_mm, "w2_mm": w2_mm, "info1": info1, "info2": info2,
        "status_def1": status_def1, "status_def2": status_def2,
        "ok_lr": ok_lr, "ok_def": ok_def, "ok_all": ok_all,
        "t_eff1_mm": t_eff1, "t_eff2_mm": t_eff2,
    }

def _pane_price(unit_prices: dict, thickness: int, glass_type: str) -> float:
    key = f"{thickness}_{glass_type}"
    try:
        return float(unit_prices.get(key, 0.0))
    except Exception:
        return 0.0


def _combo_spec(t1: int, t2: int, typ1: str, typ2: str) -> str:
    return f"{t1}mm({typ1}) + Air + {t2}mm({typ2})"


def _combo_price(
    unit_prices: dict,
    t1: int,
    t2: int,
    typ1: str,
    typ2: str,
    recommend_option: str = "추천2",
) -> Tuple[float, bool]:
    """
    조합 단가를 반환한다.
    반환값: (price, is_missing)
    - combo_prices에 값이 있으면 해당 값을 사용
    - 없으면 pane 합계를 fallback으로 사용
    - 둘 다 없으면 missing 처리
    """
    combo_prices = {}
    if isinstance(unit_prices, dict):
        if recommend_option == "추천1":
            combo_prices = unit_prices.get("rec1_combo_prices", {})
        elif recommend_option == "추천2":
            combo_prices = unit_prices.get("rec2_combo_prices", {})
        else:
            # 하위호환/예외 상황에서는 추천2 단가표를 우선 사용
            combo_prices = unit_prices.get("rec2_combo_prices", {})
        if not isinstance(combo_prices, dict) or not combo_prices:
            combo_prices = unit_prices.get("combo_prices", {})

    spec = _combo_spec(t1, t2, typ1, typ2)

    if isinstance(combo_prices, dict) and spec in combo_prices:
        try:
            p = float(combo_prices.get(spec, 0.0) or 0.0)
            if p > 0:
                return p, False
        except Exception:
            pass

    # 하위호환: 단판 단가가 전달된 경우 합산 사용
    p1 = _pane_price(unit_prices, t1, typ1)
    p2 = _pane_price(unit_prices, t2, typ2)
    if p1 > 0 and p2 > 0:
        return p1 + p2, False

    return 0.0, True


def recommend_glass_for_floor(
    design_pressure_kN_m2: float,
    long_side_mm: int,
    short_side_mm: int,
    recommend_option: str = "추천1",
    unit_prices: Optional[dict] = None,
) -> dict:
    """
    - 모든 조합을 계산하여 floor_results에 담고,
        - 추천(best)은 옵션별 정렬 기준에 따라 OK 조합 중 최우선 1개를 선택한다.
    """
    if unit_prices is None:
        unit_prices = {}

    results = []
    result_by_combo = {}
    combo_rank = {combo: idx for idx, combo in enumerate(COMBOS)}

    for t1, t2, typ1, typ2 in COMBOS:
        res = check_combo_with_deflection(
            design_pressure_kN_m2, long_side_mm, short_side_mm, t1, t2, typ1, typ2
        )
        spec_cost, price_missing = _combo_price(unit_prices, t1, t2, typ1, typ2, recommend_option)
        lr_min = min(res["lr1"], res["lr2"])
        res.update({
            "t1": t1,
            "t2": t2,
            "type1": typ1,
            "type2": typ2,
            "spec_cost": spec_cost,
            "price_missing": price_missing,
            "lr_min": lr_min,
            "combo_rank": combo_rank[(t1, t2, typ1, typ2)],
        })
        results.append(res)
        result_by_combo[(t1, t2, typ1, typ2)] = res

    ok_results = [r for r in results if r.get("ok_all")]
    best = None

    if ok_results:
        if recommend_option == "추천2":
            # 단가 우선: 단가 입력 조합 우선 -> 조합 단가 낮은 순 -> 기본 순위
            ok_results.sort(key=lambda r: (r["price_missing"], r["spec_cost"], r["combo_rank"]))
            best = ok_results[0]
        elif recommend_option == "추천3":
            # 구조 우선(요청 기준): 허용 풍압이 낮은 순, 동률 시 기존 순위
            ok_results.sort(key=lambda r: (r["lr_min"], r["combo_rank"]))
            best = ok_results[0]
        else:
            # 추천1(기본 순위): 단가 미입력 조합은 후순위, 그 외는 기존 COMBOS 순서
            ok_results.sort(key=lambda r: (r["price_missing"], r["combo_rank"]))
            best = ok_results[0]

    return {"floor_results": results, "best": best}

# --------- 메인: 화면용/ PDF용 동시 생성 ---------
# ---- (이 아래는 기존 import/상수/함수 등은 그대로 두고) calculate_outputs만 교체 ----

  # ==== GlassCalculator 클래스 (복붙) ====

# 일부 전역 상수가 없다면 기본값을 안전하게 설정
try:
    DEFLECTION_MODE
except NameError:
    DEFLECTION_MODE = "ratio"   # "ratio" | "abs" | "mixed"
try:
    DEFLECTION_VALUE
except NameError:
    DEFLECTION_VALUE = 60       # L/60 기본

# recommend_glass_for_floor 함수가 이 파일 상단에 정의되어 있어야 합니다.
# (없다면 기존 코드의 함수를 그대로 유지하세요)

class GlassCalculator:
    @staticmethod
    def calculate_outputs(data: dict, tab_type: str) -> dict:
        """
        반환:
          {
            "brief": 화면용 문자열 (요약만),
            "detail": PDF용 상세 문자열 (요약 + 상세 + 조합 근거)
          }
        """
        # ---- 입력 ----
        try:
            num_floors = int(data["건물층수"])
            top_floor_height = float(data["최고층 층고 [m]"])
            standard_floor_height = float(data["기준층 층고 [m]"])
            lowest_floor_height = float(data["최저층 층고 [m]"])
            V0 = float(data["기본풍속 (V0) [m/sec]"])
            노풍도 = data["노풍도 (A, B, C, D)"].strip().upper()
            review_position = data["검토위치 (중앙부, 모서리부)"].strip()
        except Exception as e:
            return {"brief": f"건물 및 풍속 입력값 오류: {e}", "detail": f"오류: {e}"}

        try:
            glass_width = float(data["유리 폭 (m)"])
            glass_height = float(data["유리 높이 (m)"])
        except Exception as e:
            return {"brief": f"유리 면적 입력값 오류: {e}", "detail": f"오류: {e}"}

        recommend_option = str(data.get("유리 Spec 추천 옵션", "추천1")).strip()
        unit_prices = data.get("단가표", {})
        if not isinstance(unit_prices, dict):
            unit_prices = {}

        # ---- 층고 입력 모드 해석 ----
        input_mode = str(data.get("입력방식", "grouped")).strip().lower()
        floor_heights = []

        if input_mode == "individual":
            raw_heights = data.get("층고목록", [])
            if not isinstance(raw_heights, list):
                return {"brief": "층고목록 형식 오류", "detail": "층고목록은 list 형식이어야 합니다."}
            try:
                floor_heights = [float(h) for h in raw_heights]
            except Exception:
                return {"brief": "층고목록 값 오류", "detail": "층고목록에는 숫자만 입력해야 합니다."}
            if len(floor_heights) != num_floors:
                return {
                    "brief": f"층고목록 개수 오류: 건물층수({num_floors})와 층고 개수({len(floor_heights)})가 다릅니다.",
                    "detail": "층고목록 개수 오류",
                }
            if any(h <= 0 for h in floor_heights):
                return {"brief": "층고 입력 오류: 0 이하 값이 있습니다.", "detail": "층고 입력 오류"}
        else:
            # grouped 모드: 최저층 N개 / 기준층 자동 / 최고층 N개
            try:
                top_count = int(data.get("최고층 개수", 1))
                low_count = int(data.get("최저층 개수", 2))
            except Exception:
                return {"brief": "최고층/최저층 개수 입력 오류", "detail": "최고층/최저층 개수 입력 오류"}

            if top_count < 0 or low_count < 0:
                return {"brief": "최고층/최저층 개수는 0 이상이어야 합니다.", "detail": "층수 개수 입력 오류"}

            standard_count = num_floors - top_count - low_count
            if standard_count < 0:
                return {
                    "brief": f"층수 배분 오류: 최고층({top_count}) + 최저층({low_count}) > 건물층수({num_floors})",
                    "detail": "층수 배분 오류",
                }

            floor_heights = (
                [lowest_floor_height] * low_count
                + [standard_floor_height] * standard_count
                + [top_floor_height] * top_count
            )

        # ---- 건물 높이/계수 ----
        H = sum(floor_heights)
        Zb = {'A': 20, 'B': 15, 'C': 10, 'D': 5}.get(노풍도, 10)
        Zg = {'A': 550, 'B': 450, 'C': 350, 'D': 250}.get(노풍도, 350)
        alfa = {'A': 0.33, 'B': 0.22, 'C': 0.15, 'D': 0.10}.get(노풍도, 0.15)
        Kzr_low = {'A': 0.58, 'B': 0.81, 'C': 1.00, 'D': 1.13}.get(노풍도)
        Kzr_mid = {'A': 0.22, 'B': 0.45, 'C': 0.71, 'D': 0.98}.get(노풍도)
        if Kzr_low is None or Kzr_mid is None:
            msg = "노풍도 입력 오류: A, B, C, D 중 하나여야 합니다."
            return {"brief": msg, "detail": msg}

        Kzt = 1.00; Iw = 1.00; Kd = 1.00; rho = 1.225

        # ---- 저장 버퍼 ----
        floor_recommendations = []   # (층, applied_stress_Pa, spec or 'FAIL')
        floor_debug = []             # 층별 선택 조합 요약
        floor_evidences = []         # 층별 조합 근거(간단 OK/NG)
        long_side_mm = int(round(max(glass_width, glass_height) * 1000.0))
        short_side_mm = int(round(min(glass_width, glass_height) * 1000.0))

        # ---- 층별 루프 ----
        for i in range(1, num_floors + 1):
            # i층 높이까지의 누적 높이(m)
            z_i = sum(floor_heights[:i])
            if H <= Zb:
                Kzr_i = Kzr_low
            elif H <= Zg:
                Kzr_i = Kzr_mid * (H ** alfa)
            else:
                Kzr_i = Kzr_mid * (Zg ** alfa)

            if z_i <= Zb:
                Kz_i = (Zb / H) ** (2 * alfa)
            elif z_i < 0.8 * H:
                Kz_i = (z_i / H) ** (2 * alfa)
            else:
                Kz_i = (0.8) ** (2 * alfa)

            Vh_i = V0 * Kd * Kzr_i * Kzt * Iw
            qh_i = 0.5 * rho * (Vh_i ** 2)

            Pc_Positive_1 = Kz_i * qh_i * (1.8 - 0)
            Pc_Positive_2 = Kz_i * qh_i * (1.8 - (-0.52))
            Pc_Positive = Pc_Positive_1 if abs(Pc_Positive_1) >= abs(Pc_Positive_2) else Pc_Positive_2

            Pc_center_1 = qh_i * (-1.8 - 0)
            Pc_center_2 = qh_i * (-1.8 - (-0.52))
            Pc_center = Pc_center_1 if abs(Pc_center_1) >= abs(Pc_center_2) else Pc_center_2

            Pc_edge_1 = qh_i * (-3.6 - 0)
            Pc_edge_2 = qh_i * (-3.6 - (-0.52))
            Pc_edge = Pc_edge_1 if abs(Pc_edge_1) >= abs(Pc_edge_2) else Pc_edge_2

            if review_position == "중앙부":
                selected_negative = abs(Pc_center)
            elif review_position == "모서리부":
                selected_negative = abs(Pc_edge)
            else:
                msg = "검토위치는 '중앙부' 또는 '모서리부'여야 합니다."
                return {"brief": msg, "detail": msg}

            applied_stress = max(abs(Pc_Positive), selected_negative)  # Pa
            design_pressure_kN_m2 = applied_stress / 1000.0

            # ➜ 기존 코드의 핵심 함수 사용
            floor_eval = recommend_glass_for_floor(
                design_pressure_kN_m2,
                long_side_mm,
                short_side_mm,
                recommend_option=recommend_option,
                unit_prices=unit_prices,
            )
            best = floor_eval["best"]

            if best:
                picked_spec = f"{best['t1']}mm({best['type1']}) + Air + {best['t2']}mm({best['type2']})"
            else:
                picked_spec = "FAIL"

            floor_recommendations.append((i, applied_stress, picked_spec))

            # 선택 조합의 상세
            best_detail = None
            if best:
                for r in floor_eval["floor_results"]:
                    if (r["t1"] == best["t1"] and r["t2"] == best["t2"]
                        and r["type1"] == best["type1"] and r["type2"] == best["type2"]):
                        best_detail = r
                        break

            floor_debug.append({
                "floor": i,
                "floor_height": floor_heights[i-1],  # \uce35\uace0 \ucd94\uac00
                "applied_stress_kN_m2": design_pressure_kN_m2,
                "best_spec": picked_spec,
                "long_mm": long_side_mm, "short_mm": short_side_mm,
                **({
                    "lr1_kN_m2": best_detail["lr1"],
                    "lr2_kN_m2": best_detail["lr2"],
                    "w1_mm": best_detail["w1_mm"],
                    "w2_mm": best_detail["w2_mm"],
                    "w_allow_mm": best_detail["info1"].get("w_allow_mm", None),
                    "nfl1_L": best_detail["nfl1_L"], "nfl1_S": best_detail["nfl1_S"],
                } if best_detail else {})
            })

            # 층별 "조합 근거" 저장 (간단: spec | OK/NG | 단가)
            evid_items = []
            for r in floor_eval["floor_results"]:
                spec = f"{r['t1']}mm({r['type1']}) + Air + {r['t2']}mm({r['type2']})"
                ok = "OK" if r["ok_all"] else "NG"
                total_price, price_missing = _combo_price(
                    unit_prices,
                    r['t1'],
                    r['t2'],
                    r['type1'],
                    r['type2'],
                    recommend_option,
                )
                evid_items.append({
                    "spec": spec,
                    "ok": ok,
                    "total_price": total_price,
                    "price_missing": price_missing,
                })
            floor_evidences.append({
                "floor": i,
                "kn": design_pressure_kN_m2,
                "items": evid_items,
                "picked": picked_spec,
                "recommend_option": recommend_option
            })

        # ---- 그룹화 ----
        groups = []
        if floor_recommendations:
            group_start = floor_recommendations[0][0]
            current_spec = floor_recommendations[0][2]
            for idx in range(1, len(floor_recommendations)):
                fl, stress, spec = floor_recommendations[idx]
                if spec != current_spec:
                    group_end = floor_recommendations[idx - 1][0]
                    groups.append((group_start, group_end, current_spec))
                    group_start = fl
                    current_spec = spec
            groups.append((group_start, floor_recommendations[-1][0], current_spec))

        groups.sort(key=lambda x: x[0], reverse=True)

        # =========================
        # 라벨
        # =========================
        deflection_label = (
            f"L/{int(DEFLECTION_VALUE)}" if DEFLECTION_MODE == "ratio"
            else (f"{DEFLECTION_VALUE:.0f} mm" if DEFLECTION_MODE == "abs"
                  else f"min(L/{int(DEFLECTION_VALUE)}, 고정mm)")
        )

        # =========================
        # 화면용 요약 (brief_lines)
        # =========================
        brief_lines = []
        # ▶ 프로그램 개요
        brief_lines.append("▶ 프로그램 개요")
        brief_lines.append("- 적용 기준 : ASTM E1300-16")
        brief_lines.append("- 유리 사양 : 복층유리")
        brief_lines.append("- 검토 유리두께 : 5mm, 6mm, 8mm")
        brief_lines.append("- 지지방식 : 4변 지지방식")
        brief_lines.append("※ AN : 일반유리, HS : 반강화유리, FT : 강화유리")
        brief_lines.append("※ 발주/입찰 단계의 검토용. 실제 발주 시 낙찰(계약)업체의 구조계산 결과를 제출·검토하도록 발주서에 명시할 것\n")

        # ▶ 검토 조건
        brief_lines.append("▶ 검토 조건")
        brief_lines.append(f"- 건물높이 (H): {H:.2f} m")
        brief_lines.append(f"- 검토위치: {review_position}")
        brief_lines.append(f"- 유리크기: {long_side_mm} x {short_side_mm} mm (가로 x 세로)")
        brief_lines.append(f"- 유리 Spec 추천 옵션: {recommend_option}")
        brief_lines.append(f"- 처짐기준: {deflection_label}\n")

        # ▶ 검토 결과(층별 추천_그룹화)
        brief_lines.append("!!BLUEBOLD!!▶ 검토 결과(층별 추천_그룹화)")
        for s, e, spec in groups:
            if spec == "FAIL":
                line = f"{s}층 ~ {e}층 : (충족 조합 없음) → 두께/재질 상향 필요"
            else:
                line = f"{s}층 ~ {e}층 : {spec}"
                if s == 1 and e == num_floors and spec == "6mm(HS) + Air + 6mm(HS)":
                    line = "!!BLUEBOLD!!" + line
            brief_lines.append(line)

        brief = "\n".join(brief_lines) + "\n"

        # =========================
        # PDF용 상세 (detail)
        # =========================
        detail = (
            "▶ 프로그램 개요\n"
            "- 적용 기준 : ASTM E1300-16\n"
            "- 유리 사양 : 복층유리\n"
            "- 검토 유리두께 : 5mm, 6mm, 8mm\n"
            "- 지지방식 : 4변 지지방식\n\n"
            "※ AN : 일반유리, HS : 반강화유리, FT : 강화유리\n"
            "※ 발주/입찰 단계의 검토용. 실제 발주 시 낙찰(계약)업체의 구조계산 결과를 제출·검토하도록 발주서에 명시할 것\n\n"
            "▶ 검토 조건\n"
            f"- 건물높이 (H): {H:.2f} m\n"
            f"- 검토위치: {review_position}\n"
            f"- 유리크기: {long_side_mm} x {short_side_mm} mm (가로 x 세로)\n"
            f"- 유리 Spec 추천 옵션: {recommend_option}\n"
            f"- 처짐기준: {deflection_label}\n\n"
            "!!BLUEBOLD!!▶ 검토 결과(층별 추천_그룹화)\n\n"
        )

        # 그룹화 리스트
        detail += "\n".join(
            (
                "!!BLUEBOLD!!" + f"{s}층 ~ {e}층 : {spec}"
                if (spec != "FAIL" and s == 1 and e == num_floors and spec == "6mm(HS) + Air + 6mm(HS)")
                else (f"{s}층 ~ {e}층 : (충족 조합 없음) → 두께/재질 상향 필요" if spec == "FAIL"
                      else f"{s}층 ~ {e}층 : {spec}")
            )
            for s, e, spec in groups
        ) + "\n"

        # 상세(계산 근거)
        detail += "\n# 상세(계산 근거)\n"
        detail += "층 | 층고(m) | 설계풍압(kN·m^-2) | 허용풍압LR(외/내,kN·m^-2) | 처짐(외/내,mm) ≤ 허용 | 유리크기(mm) | NFL 사용크기(mm)\n"
        for d in floor_debug:
            kn = d["applied_stress_kN_m2"]
            fh = d.get("floor_height", 0.0)  # 층고
            lr_pair = "—/—"
            def_pair = "—/—"
            nfl_size = "—"
            if "lr1_kN_m2" in d:
                lr_pair = f"{d['lr1_kN_m2']:.3g}/" + f"{d['lr2_kN_m2']:.3g}"
                def_pair = f"{d['w1_mm']:.2f}/{d['w2_mm']:.2f} ≤ {d.get('w_allow_mm', float('nan')):.2f}"
                nfl_size = f"{d['nfl1_L']}×{d['nfl1_S']}"
            size_str = f"{d['long_mm']}×{d['short_mm']}"
            detail += f"{d['floor']} | {fh:.2f} | {kn:.3f} | {lr_pair} | {def_pair} | {size_str} | {nfl_size}\n"

        # 조합 근거(층별)
        detail += "\n# 조합 근거(층별)\n"
        for ev in floor_evidences:
            # 층 제목: ▶ 제거
            detail += f"{ev['floor']}층 (설계풍압 {ev['kn']:.3f} kN·m^-2)\n"
            show_price = (ev.get("recommend_option", "") == "추천2")
            for item in ev["items"]:
                if show_price:
                    if item.get("price_missing"):
                        price_calc = " | 단가 미입력"
                    else:
                        price_calc = f" | {int(item['total_price'])}원/m²"
                    line = f"{item['spec']} | {item['ok']}{price_calc}"
                else:
                    line = f"{item['spec']} | {item['ok']}"
                if item["spec"] == ev["picked"]:
                    detail += f"**{line}**\n"
                else:
                    detail += line + "\n"

        # !!BLUEBOLD!! 제거
        brief = brief.replace("!!BLUEBOLD!!", "")
        detail = detail.replace("!!BLUEBOLD!!", "")

        return {"brief": brief, "detail": detail}



    @staticmethod
    def calculate(data: dict, tab_type: str) -> str:
        outs = GlassCalculator.calculate_outputs(data, tab_type)
        return outs["brief"]
