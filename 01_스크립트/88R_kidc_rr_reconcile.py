# 88R_kidc_rr_reconcile.py — KIDC 개정판(2026-11-19): 판정 인원의 성·연령별 성분 대조. 모형 적합 없음.
# 입력: N104(판정 질환의심 세부, 신장질환 grp 00306)·N099(판정 수검자 grp 001) 전국 성·5세 연령, N129(eGFR 성·연령), N065(요단백 성·연령; KOSIS 2026-11-19)
# 근거: 보건복지부 건강검진 실시기준 [별표 5의 별첨](2014·2017)·[별표 4의 별첨](2024·2026) 신장질환 = 요단백 +1↑ 또는 크레아티닌>1.5 또는 eGFR<60
#        [별표 1] eGFR = MDRD(186 또는 IDMS 175)(~2023), CKD-EPI(2024)
# 출력: 04_분석/KIDC/JN_RR_261119/R1_age_sex_reconcile.csv, R1_reconcile_summary.json
import os, json, numpy as np, pandas as pd
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC = os.path.join(R, "00_원천", "C_NHIS_검진보험"); K3 = os.path.join(SRC, "KOSIS_JN_RR_261119")
OUT = os.path.join(R, "04_분석", "KIDC", "JN_RR_261119"); os.makedirs(OUT, exist_ok=True)
AGE = {"19세 이하": "<20", "20 ~ 24세": "20-24", "25 ~ 29세": "25-29", "30 ~ 34세": "30-34", "35 ~ 39세": "35-39", "40 ~ 44세": "40-44", "45 ~ 49세": "45-49", "50 ~ 54세": "50-54", "55 ~ 59세": "55-59",
       "60 ~ 64세": "60-64", "65 ~ 69세": "65-69", "70 ~ 74세": "70-74", "75 ~ 79세": "75-79", "80 ~ 84세": "80-84", "85세 이상": "85+", "계": "all"}
SEX = {"합계": "all", "남자": "M", "여자": "F"}
def kj(p):
    d = pd.DataFrame(json.load(open(p))); d["DT"] = pd.to_numeric(d.DT, errors="coerce"); d["year"] = d.PRD_DE.astype(int)
    d["age"] = d.C1_NM.map(AGE); d["sex"] = d.C2_NM.map(SEX); assert d.age.notna().all() and d.sex.notna().all(); return d
g = kj(os.path.join(K3, "DT_35007_N129_age_sex.json")); G = g.pivot_table(index=["year", "sex", "age"], columns="C3", values="DT", aggfunc="sum")
u = kj(os.path.join(K3, "DT_35007_N065_age_sex.json")); U = u.pivot_table(index=["year", "sex", "age"], columns="C3_NM", values="DT", aggfunc="sum")
n104 = pd.read_csv(os.path.join(SRC, "DT_35007_N104_national_long.csv"), dtype={"grp_code": str, "age_code": str})
n099 = pd.read_csv(os.path.join(SRC, "DT_35007_N099_national_long.csv"), dtype={"grp_code": str, "age_code": str})
for d in (n104, n099): d["age"] = d.age.map(AGE); d["sex"] = d.sex.map(SEX)
J = n104[n104.grp_code == "00306"].set_index(["year", "sex", "age"]).value
D = n099[n099.grp_code == "001"].set_index(["year", "sex", "age"]).value.astype(float)
T = pd.DataFrame({"judged_examinees": D, "kidney_judged": J, "egfr_measured": G["001"], "egfr_lt60": G[["002", "003", "004", "005"]].sum(1, min_count=1),
                  "egfr_ge150": G["010"], "dip_measured": U["계"], "dip_1plus": U[["+1", "+2", "+3", "+4"]].sum(1, min_count=1), "dip_trace": U["+-"]}).dropna(subset=["kidney_judged"])
T = T.loc[(slice(2012, 2024), slice(None), slice(None)), :].copy()
T["j"] = T.kidney_judged / T.judged_examinees; T["a"] = T.egfr_lt60 / T.egfr_measured; T["b"] = T.dip_1plus / T.dip_measured
T["lo_union"] = T[["a", "b"]].max(1); T["hi_union"] = (T.a + T.b).clip(upper=1); T["indep_union"] = T.a + T.b - T.a * T.b
T["j_minus_a"] = T.j - T.a; T["within_bounds"] = (T.j >= T.lo_union - 1e-9) & (T.j <= T.hi_union + 1e-9)
T["pos_in_band"] = (T.j - T.lo_union) / (T.hi_union - T.lo_union)  # 0 = 완전 겹침(최소 합집합), 1 = 겹침 없음(최대 합집합)
T["denom_ratio_egfr"] = T.egfr_measured / T.judged_examinees; T["denom_ratio_dip"] = T.dip_measured / T.judged_examinees
T.reset_index().to_csv(os.path.join(OUT, "R1_age_sex_reconcile.csv"), index=False)
S = {}
st = T.loc[(slice(2015, 2023), ["M", "F"], [a for a in AGE.values() if a not in ("all",)]), :]
S["strata_2015_2023"] = int(len(st)); S["strata_within_union_bounds"] = int(st.within_bounds.sum())
S["strata_j_gt_a"] = int((st.j > st.a).sum()); S["strata_j_gt_sum"] = int((st.j > st.hi_union + 1e-9).sum()); S["strata_j_lt_max"] = int((st.j < st.lo_union - 1e-9).sum())
for sx in ("M", "F"):
    q = st.xs(sx, level="sex"); S[f"{sx}_within"] = int(q.within_bounds.sum()); S[f"{sx}_n"] = int(len(q)); S[f"{sx}_j_gt_a"] = int((q.j > q.a).sum())
    S[f"{sx}_pos_in_band_median"] = float(q.pos_in_band.median())
# 젊은 층(<40)·여성: 크레아티닌 단독이 eGFR<60 밖으로 나올 수 없는 층
for key, sel in [("F_all_ages", st.xs("F", level="sex")), ("F_20_39", st.xs("F", level="sex").loc[(slice(None), ["20-24", "25-29", "30-34", "35-39"]), :])]:
    S[f"{key}_sum_excess_over_egfr"] = float((sel.kidney_judged - sel.a * sel.judged_examinees).sum()); S[f"{key}_sum_dip1p_scaled"] = float((sel.b * sel.judged_examinees).sum())
tot = T.xs(("all", "all"), level=("sex", "age"))
S["national"] = {int(y): {c: (None if pd.isna(r[c]) else float(r[c])) for c in ["judged_examinees", "egfr_measured", "dip_measured", "j", "a", "b", "lo_union", "hi_union", "indep_union", "pos_in_band", "denom_ratio_egfr", "denom_ratio_dip"]} for y, r in tot.iterrows()}
# 크레아티닌 단독(크레아티닌>1.5 이면서 eGFR≥60)이 가능한 성·연령 상한(MDRD 186/IDMS 175, CKD-EPI 2021)
def mdrd(scr, age, f, k=186.0): return k * scr ** -1.154 * age ** -0.203 * (0.742 if f else 1)
def ckdepi21(scr, age, f):
    kap, al = (0.7, -0.241) if f else (0.9, -0.302); return 142 * min(scr / kap, 1) ** al * max(scr / kap, 1) ** -1.200 * 0.9938 ** age * (1.012 if f else 1)
ages = np.arange(18, 100)
S["creat_only_possible_max_age"] = {"MDRD186_M": int(ages[[mdrd(1.5001, a, False) >= 60 for a in ages]].max(initial=0)), "MDRD186_F": int(ages[[mdrd(1.5001, a, True) >= 60 for a in ages]].max(initial=0)),
    "MDRD175_M": int(ages[[mdrd(1.5001, a, False, 175) >= 60 for a in ages]].max(initial=0)), "MDRD175_F": int(ages[[mdrd(1.5001, a, True, 175) >= 60 for a in ages]].max(initial=0)),
    "CKDEPI21_M": int(ages[[ckdepi21(1.5001, a, False) >= 60 for a in ages]].max(initial=0)), "CKDEPI21_F": int(ages[[ckdepi21(1.5001, a, True) >= 60 for a in ages]].max(initial=0))}
def scr_max(age, f, eq):  # eGFR=60 이 되는 크레아티닌(이 값 이하·1.5 초과면 크레아티닌 단독)
    lo, hi = 0.3, 5.0
    for _ in range(60):
        m = (lo + hi) / 2; v = eq(m, age, f)
        lo, hi = (m, hi) if v >= 60 else (lo, m)
    return lo
S["creat_only_band_M20"] = {"MDRD186": round(scr_max(20, False, mdrd), 3), "MDRD175": round(scr_max(20, False, lambda s, a, f: mdrd(s, a, f, 175)), 3), "CKDEPI21": round(scr_max(20, False, ckdepi21), 3)}
# 남성 20-29세 대 여성 20-29세 판정 초과(eGFR 대비) 비교: 크레아티닌 단독이 기여한다면 남성 젊은 층에만 초과가 몰려야 함
yy = st.loc[(slice(None), ["M", "F"], ["20-24", "25-29"]), :].copy(); yy["excess_pct"] = 100 * yy.j_minus_a; yy["dip_pct"] = 100 * yy.b
S["young_excess_vs_dip"] = yy.groupby(level="sex")[["excess_pct", "dip_pct"]].mean().round(3).to_dict()
json.dump(S, open(os.path.join(OUT, "R1_reconcile_summary.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in S.items() if k != "national"}, indent=1, ensure_ascii=False))
print(pd.DataFrame(S["national"]).T.round(4).to_string())
# ── 성·연령 직접표준화(2019 판정 수검자 구조, 20세 이상) 연도별 j·a·b, 그리고 연령대별 판정/eGFR<60 비 ──
AG20 = [a for a in AGE.values() if a not in ("all", "<20")]
W = T.loc[(2019, ["M", "F"], AG20), "judged_examinees"]; W = W / W.sum(); W.index = W.index.droplevel(0)
DS = {}
for y in range(2012, 2025):
    q = T.loc[(y, ["M", "F"], AG20), ["j", "a", "b", "dip_trace", "dip_measured"]]; q.index = q.index.droplevel(0)
    DS[y] = {"j_std": float((q.j * W).sum()), "a_std": float((q.a * W).sum()), "b_std": float((q.b * W).sum()), "trace_std": float(((q.dip_trace / q.dip_measured) * W).sum())}
S["direct_std_2019"] = DS
AGEB = {"20-39": ["20-24", "25-29", "30-34", "35-39"], "40-59": ["40-44", "45-49", "50-54", "55-59"], "60-69": ["60-64", "65-69"], "70+": ["70-74", "75-79", "80-84", "85+"]}
RT = []
for y in range(2012, 2025):
    for sx in ("M", "F"):
        for nm, ags in AGEB.items():
            q = T.loc[(y, sx, ags), :]; RT.append(dict(year=y, sex=sx, ageband=nm, judged=float(q.kidney_judged.sum()), exam=float(q.judged_examinees.sum()),
                j=float(q.kidney_judged.sum() / q.judged_examinees.sum()), a=float((q.a * q.judged_examinees).sum() / q.judged_examinees.sum()), b=float((q.b * q.judged_examinees).sum() / q.judged_examinees.sum())))
RT = pd.DataFrame(RT); RT["j_over_a"] = RT.j / RT.a; RT["j_minus_a_over_b"] = (RT.j - RT.a) / RT.b; RT["j_over_b"] = RT.j / RT.b
RT.to_csv(os.path.join(OUT, "R1_ageband_reconcile.csv"), index=False)
json.dump(S, open(os.path.join(OUT, "R1_reconcile_summary.json"), "w"), indent=1, ensure_ascii=False)
print(pd.DataFrame(DS).T.mul(100).round(3).to_string())
print(RT[RT.year.isin([2015, 2019, 2023])].round(3).to_string(index=False))
# ── 크레아티닌 분포(N079) 대조: 판정이 eGFR<60 대신 크레아티닌>1.5를 따르는지 ──
c = kj(os.path.join(K3, "DT_35007_N079_age_sex.json")); CR = c.pivot_table(index=["year", "sex", "age"], columns="C3", values="DT", aggfunc="sum")
T["cr_measured"] = CR["001"]; T["cr_ge15"] = CR[["007", "008", "009", "010"]].sum(1, min_count=1); T["cr_ge17"] = CR[["008", "009", "010"]].sum(1, min_count=1)
T["c_hi"] = T.cr_ge15 / T.cr_measured; T["c_lo"] = T.cr_ge17 / T.cr_measured
CB = []
for y in range(2015, 2024):
    for sx in ("M", "F"):
        for nm, ags in AGEB.items():
            q = T.loc[(y, sx, ags), :]; w_ = q.judged_examinees; f = lambda col: float((q[col] * w_).sum() / w_.sum())
            CB.append(dict(year=y, sex=sx, ageband=nm, j=f("j"), a=f("a"), b=f("b"), c_lo=f("c_lo"), c_hi=f("c_hi")))
CB = pd.DataFrame(CB)
for k_, (x, z) in {"egfr": ("a", "a"), "creat_lo": ("c_lo", "c_lo"), "creat_hi": ("c_hi", "c_hi")}.items():
    CB[f"lo_{k_}"] = CB[[x, "b"]].max(1); CB[f"hi_{k_}"] = CB[x] + CB.b; CB[f"in_{k_}"] = (CB.j >= CB[f"lo_{k_}"] - 1e-9) & (CB.j <= CB[f"hi_{k_}"] + 1e-9)
CB.to_csv(os.path.join(OUT, "R1_creatinine_reconcile.csv"), index=False)
G2 = CB.groupby(["sex", "ageband"])[["j", "a", "b", "c_lo", "c_hi", "in_egfr", "in_creat_lo", "in_creat_hi"]].mean()
print((G2 * [100, 100, 100, 100, 100, 1, 1, 1]).round(3).to_string())
S["creat_bounds_in"] = {k_: int(CB[f"in_{k_}"].sum()) for k_ in ("egfr", "creat_lo", "creat_hi")}; S["creat_bounds_n"] = int(len(CB))
json.dump(S, open(os.path.join(OUT, "R1_reconcile_summary.json"), "w"), indent=1, ensure_ascii=False)
print(S["creat_bounds_in"], S["creat_bounds_n"])
