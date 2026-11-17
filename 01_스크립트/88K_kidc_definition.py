# 88K_kidc_definition.py — 32호 KIDC: 검진 신장질환 의심 판정의 구성 대조(2026-11-17). 모형 적합 없음.
#  입력: 00_원천/C_NHIS_검진보험/DT_35007_N104·N099_national_long.csv(의심·수검), N129_national.json(eGFR 연령별 전국),
#        KOSIS_eGFR_요단백_261117/(N065 전국 요단백, N064 시도 요단백, N128 시도 eGFR; KOSIS API 2026-11-17 조회), 02_패널/KIDS_Estd3.csv(시군구 의심·수검)
#  출력: 04_분석/KIDC/results_std3/S47_kidc_definition.json, S47_kidc_national.csv, S47_kidc_province.csv
import os, json, numpy as np, pandas as pd
import statsmodels.formula.api as smf
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC = os.path.join(R, "00_원천", "C_NHIS_검진보험"); K2 = os.path.join(SRC, "KOSIS_eGFR_요단백_261117")
OUT = os.path.join(R, "04_분석", "KIDC", "results_std3"); os.makedirs(OUT, exist_ok=True)
def kj(p):
    d = pd.DataFrame(json.load(open(p))); d["DT"] = pd.to_numeric(d.DT, errors="coerce"); d["year"] = d.PRD_DE.astype(int); return d
LT60 = ["002", "003", "004", "005"]; P1 = ["+1", "+2", "+3", "+4"]
g = kj(os.path.join(SRC, "DT_35007_N129_national.json")); g = g[(g.C1 == "001") & (g.C2 == "001")].pivot_table(index="year", columns="C3", values="DT")
u = kj(os.path.join(K2, "DT_35007_N065_national.json")); u = u[u.C2_NM == "합계"].pivot_table(index="year", columns="C3_NM", values="DT")
n104 = pd.read_csv(os.path.join(SRC, "DT_35007_N104_national_long.csv"), dtype={"grp_code": str, "age_code": str})
n099 = pd.read_csv(os.path.join(SRC, "DT_35007_N099_national_long.csv"), dtype={"grp_code": str, "age_code": str})
tot = lambda d: d[(d.age_code == "001") & (d.sex == "합계")]
susp = tot(n104)[tot(n104).grp_code == "00306"].set_index("year").value; exm = tot(n099)[tot(n099).grp_code == "001"].set_index("year").value.astype(float)
T = pd.DataFrame({"judged_examinees": exm, "suspected": susp, "egfr_measured": g["001"], "egfr_lt60": g[LT60].sum(1), "egfr_ge150": g["010"], "egfr_60_79": g["007"],
                  "dip_measured": u["계"], "dip_1plus": u[P1].sum(1)}).loc[2012:2024]
T["pct_suspected"] = 100 * T.suspected / T.judged_examinees; T["pct_egfr_lt60"] = 100 * T.egfr_lt60 / T.egfr_measured; T["pct_dip_1plus"] = 100 * T.dip_1plus / T.dip_measured
T["ratio_susp_to_egfr"] = T.suspected / T.egfr_lt60; T["excess_over_egfr"] = T.suspected - T.egfr_lt60; T["excess_share_of_dip"] = T.excess_over_egfr / T.dip_1plus
T.to_csv(os.path.join(OUT, "S47_kidc_national.csv"))
# 시도 대조
a = kj(os.path.join(K2, "DT_35007_N064_sido.json")); pa = a.pivot_table(index=["year", "C1_NM"], columns="C3_NM", values="DT"); pa["dip"] = 100 * pa[P1].sum(1) / pa["계"]
b = kj(os.path.join(K2, "DT_35007_N128_sido.json")); pb = b.pivot_table(index=["year", "C1_NM"], columns="C3", values="DT"); pb["egfr"] = 100 * pb[LT60].sum(1) / pb["001"]
X = pa[["dip"]].join(pb[["egfr"]]).reset_index()
key = {"서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시", "인천": "인천광역시", "광주": "광주광역시", "대전": "대전광역시", "울산": "울산광역시", "경기": "경기도", "강원": "강원특별자치도",
       "충청북": "충청북도", "충북": "충청북도", "충청남": "충청남도", "충남": "충청남도", "전라북": "전북특별자치도", "전북": "전북특별자치도", "전라남": "전라남도", "전남": "전라남도",
       "경상북": "경상북도", "경북": "경상북도", "경상남": "경상남도", "경남": "경상남도", "제주": "제주특별자치도", "세종": "세종특별자치시"}
def sd(r):
    for kk in sorted(key, key=len, reverse=True):
        if r.startswith(kk): return key[kk]
E = pd.read_csv(os.path.join(R, "02_패널", "KIDS_Estd3.csv")); E["sido"] = E.fbd_region.map(sd); assert E.sido.notna().all()
S = E.groupby(["year", "sido"])[["cases", "examinees"]].sum().reset_index(); S["susp"] = 100 * S.cases / S.examinees
Z = S.merge(X, left_on=["year", "sido"], right_on=["year", "C1_NM"]).drop(columns="C1_NM"); Z.to_csv(os.path.join(OUT, "S47_kidc_province.csv"), index=False)
J = {"n_province": int(Z.sido.nunique()), "years": [int(Z.year.min()), int(Z.year.max())]}
for nm, f in [("egfr", "susp~egfr+C(year)"), ("dip", "susp~dip+C(year)"), ("both", "susp~egfr+dip+C(year)"), ("year_only", "susp~C(year)")]:
    for per, q in [("2012_2024", Z), ("2015_2023", Z[(Z.year >= 2015) & (Z.year <= 2023)])]:
        r = smf.ols(f, q).fit(); J[f"r2_{nm}_{per}"] = float(r.rsquared)
        for c in ("egfr", "dip"):
            if c in r.params: J[f"b_{c}_{nm}_{per}"] = float(r.params[c]); J[f"ci_{c}_{nm}_{per}"] = [float(x) for x in r.conf_int().loc[c]]
# 연도 고정효과 위에서 성분이 더하는 설명력(시도 내 연도별 변동이 아닌 시도 간 차이)
for per, q in [("2015_2023", Z[(Z.year >= 2015) & (Z.year <= 2023)])]:
    q = q.copy()
    for c in ("susp", "egfr", "dip"): q[c + "_dm"] = q[c] - q.groupby("year")[c].transform("mean")
    r = smf.ols("susp_dm~egfr_dm+dip_dm-1", q).fit(); J["r2_between_both_" + per] = float(r.rsquared)
    J["r2_between_egfr_" + per] = float(smf.ols("susp_dm~egfr_dm-1", q).fit().rsquared); J["r2_between_dip_" + per] = float(smf.ols("susp_dm~dip_dm-1", q).fit().rsquared)
J["yearly_corr"] = {int(y): dict(egfr=float(d.susp.corr(d.egfr)), dip=float(d.susp.corr(d.dip))) for y, d in Z.groupby("year")}
J["national"] = {int(y): {k: (float(v) if pd.notna(v) else None) for k, v in r.items()} for y, r in T.iterrows()}
json.dump(J, open(os.path.join(OUT, "S47_kidc_definition.json"), "w"), indent=1, ensure_ascii=False)
print(T[["pct_suspected", "pct_egfr_lt60", "pct_dip_1plus", "ratio_susp_to_egfr", "excess_share_of_dip"]].round(3).to_string())
print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in J.items() if k.startswith(("r2", "b_"))})
