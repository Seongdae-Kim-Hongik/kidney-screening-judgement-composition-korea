# content_kids.py — 32호 KIDC 원고의 Methods·Results 문장(수치는 numbers_kids에서만, 2026-11-17).
#  인용 = [@key] 또는 [@web:...]; 번호식 [n]. 단독 저자 → 1인칭 금지. 영국식 철자. 결과 절 해석 금지.
#  제목 쌍점 금지, 시리즈 제목 틀 반복 금지. 보충 = Supplementary material(PDF).
from numbers_kids import load, ROB, RS, HTN, DM, BLR, DX, EDU, PA, PER
import os, pandas as pd
N = load()
def ci(v, src=None):
    r = (src or N["main"])[v]; return f"RR {r['IRR']:.3f}; 95% CrI {r['lo']:.3f}–{r['hi']:.3f}"
def tci(t): return f"RR {t[0]:.3f}; 95% CrI {t[1]:.3f}–{t[2]:.3f}"
M = N["main"]; T1 = N["T1"]; DF = N["defn"]; NT = DF["national"]
S43 = lambda a, v: N["s43"][(a, v)]
dW = lambda a: N["s43_waic"][a] - N["waic_main"]
NCO = lambda o, v: N["nco"][(o, v)]
S46 = lambda a, v: N["s46"][(a, v)]
SC = lambda s, v: N["sens_main"][s][v]
EN = {"전라남도": "South Jeolla", "경상북도": "North Gyeongsang", "경상남도": "South Gyeongsang", "충청남도": "South Chungcheong", "전라북도": "North Jeolla",
      "강원도": "Gangwon", "부산시": "Busan", "충청북도": "North Chungcheong", "대구시": "Daegu", "경기도": "Gyeonggi", "서울시": "Seoul", "인천시": "Incheon",
      "광주시": "Gwangju", "울산시": "Ulsan", "대전시": "Daejeon", "세종시": "Sejong", "제주도": "Jeju"}
def sidos(d, n):
    l = [f"{EN.get(k, k)} ({v})" for k, v in list(d.items())[:n]]; return ", ".join(l[:-1]) + " and " + l[-1]
KH = ("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV")
TITLE = "Reduced filtration or proteinuria? Unpacking a kidney screening judgement in Korea"
assert ":" not in TITLE and "229" not in TITLE and "standardi" not in TITLE.lower() and len(TITLE) <= 85 and "eGFR" not in TITLE
KEYWORDS = "Glomerular filtration rate; Proteinuria; Mass screening; Spatial analysis"
assert len(KEYWORDS.split(";")) <= 4
_LK = pd.read_csv(os.path.join(RS, "S1_likelihood.csv")); _LK = _LK[_LK.set == "REF_forced_only"].set_index("family").WAIC
_FAM = pd.read_csv(os.path.join(RS, "S3_main_fit.csv")).family.iloc[0]
assert _FAM == "nbinomial" and _LK["nbinomial"] < _LK["poisson"] and abs(_LK["nbinomial"] - N["waic_forced"]) < 0.05
NHYP = N["n_hyp"]; assert NHYP == 13
SUP = {"composition": "S1", "methods": "S2", "covariates": "S3", "checks": "S4", "specs": "S5", "windows": "S6", "strobe": "S7"}
def sup(k): return (f"Table {SUP[k]}" if k != "maps" else "Figure S1") + ", Supplementary material"
_pc = lambda v: f"{100*N['mv'][v]['cred_frac']:.0f}%"
ALT = N["retention"]
NULLV = ["screening_normalB_obesity_share", "current_smoking_rate"] + PA + ["diabetic_kidney_test_rate", "im_specialists_per_100k", "screening_uptake", BLR]
BEST = min(KH, key=lambda a: N["s43_waic"][a])
ALT_N = ALT[HTN]["n_specs"]
r1 = lambda x: f"{x:.1f}"; r2 = lambda x: f"{x:.2f}"
EX_P = lambda y: 100 * NT[y]["excess_share_of_dip"]

METHODS = [
("Design and data",
 f"This ecological study used the general health screening programme of the National Health Insurance Service, which offers adults an examination every 2 years, including serum creatinine and a urine dipstick, and records a judgement for each examinee against published criteria [@seong2017data; @web:nhis2019report]. The outcome was the judgement of suspected kidney disease, for which the published criteria are an estimated glomerular filtration rate (eGFR) below 60 mL/min/1.73 m² or a serum creatinine above 1.5 mg/dL [@web:nhis2019report]. Annual numbers of examinees with a judgement and of judgements of suspected kidney disease by district, and nationally by sex and 5-year age group, were taken from the national statistics portal, together with the published national and provincial distributions of eGFR and of dipstick proteinuria [@web:kosis2026screening] (sources in {sup('composition')}). Districts were harmonised to {N['n_districts']} units; one district created in 2012 without separate results was excluded ({sup('methods')})."),
("Composition of the judgement",
 "For each year from 2012, when eGFR distributions were first published, to 2024, the national number of judgements was compared with the numbers of examinees with an eGFR below 60 mL/min/1.73 m² and with dipstick proteinuria of 1+ or more. Across provinces and years, the judged share was regressed on the two component shares with year effects, and the between-province share of variance explained was estimated after centring each share on its yearly mean. The analysis period was set to the years in which the judgement was at least the eGFR count and the eGFR distribution was continuous."),
("Age and sex standardisation",
 "Expected numbers were obtained by indirect standardisation, applying national rates by sex and 5-year age group to the estimated examinees of each district and rescaling each year to the national total. The sex and age structure of district examinees, which is not published, was estimated from the resident population and national uptake and scaled to the observed district examinees by sex; expected numbers computed from the resident population were used as a sensitivity analysis."),
("Covariates",
 f"Thirteen district characteristics and their expected directions were fixed before any covariate model was fitted ({sup('covariates')}; panel checks in {sup('checks')}). Upstream characteristics were the summed shares of examinees already treated for hypertension and diabetes, the shares with suspected hypertension and with suspected diabetes at screening, and the share in the lifestyle-management category for obesity. Behaviour was represented by current smoking, walking and moderate or vigorous physical activity from the Community Health Survey and by public sports facilities per 100,000 population; care and selection by urine albumin testing among people with diabetes, internal medicine specialists per 100,000 population and screening uptake; and structure by the shares receiving basic livelihood security and with tertiary education. Higher upstream, smoking and deprivation values were expected to raise, and the others to lower, the standardised ratio. Urban population share, physician density, sex ratio, fiscal autonomy and the share aged 80 years or older were forced into every model. Covariates were standardised to 1 standard deviation (SD)."),
("Statistical analysis",
 f"The likelihood was chosen by the widely applicable information criterion (WAIC). Models had an offset of log expected numbers, a Besag–York–Mollié 2 district effect with penalised-complexity priors [@riebler2016intuitive] and random-walk and independent year effects, fitted by integrated nested Laplace approximation [@rue2009approximate]. Rate ratios (RRs) per 1 SD are reported with 95% credible intervals (CrIs); an association was credible when the interval excluded 1. RRs are mutually adjusted ecological associations, not causal effects, and intervals were not adjusted for multiplicity. Robustness to covariate selection was assessed in {N['n_specs_total']} random covariate subsets; a covariate was subset-stable if credible in at least 75% of the subsets containing it, with the same sign in at least 95%. Residual hot and cold spots had a posterior probability of a residual spatial RR above 1 greater than 0.95 or less than 0.05."),
("Sensitivity analyses",
 f"Knorr-Held type I–IV space–time interactions were added [@knorrheld2000bayesian]; subset-stable covariates were split into district means and within-district deviations; the model was refitted in 2015–2018 and 2019–2023; expected numbers were recomputed from the resident population; and the provincial shares with an eGFR below 60 mL/min/1.73 m² and with dipstick proteinuria were added to test whether the associations reflected one component. Further specifications varied the likelihood, time effects, priors, neighbourhoods, lags and left-out provinces or years. Treated gastric cancer and infectious disease served as comparison outcomes, hit-and-run accidents, fires and recycling as negative-control exposures, and E-values quantified the confounding needed to explain associations ({sup('specs')}). The study is reported according to the STROBE statement [@vonelm2007strengthening]. The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript."),
]

C1 = lambda a, v: N["comp"][(a, v)]
RESULTS = [
("What the judgement counts",
 f"Nationally, judgements were fewer than examinees with an eGFR below 60 mL/min/1.73 m² in 2012–2014 (ratio {r2(NT[2012]['ratio_susp_to_egfr'])}–{r2(NT[2014]['ratio_susp_to_egfr'])}) and more from 2015 onwards, rising to {r2(NT[2023]['ratio_susp_to_egfr'])} times that number in 2023 (Fig. 1B; {sup('composition')}). Between 2015 and 2023 the judged share rose from {r2(NT[2015]['pct_suspected'])}% to {r2(NT[2023]['pct_suspected'])}%, the share with an eGFR below 60 mL/min/1.73 m² fell from {r2(NT[2015]['pct_egfr_lt60'])}% to {r2(NT[2023]['pct_egfr_lt60'])}%, and the share with dipstick proteinuria of 1+ or more rose from {r2(NT[2015]['pct_dip_1plus'])}% to {r2(NT[2023]['pct_dip_1plus'])}%; judgements in excess of the eGFR count equalled {EX_P(2023):.0f}% of examinees with proteinuria in 2023. Across {DF['n_province']} provinces in 2015–2023, the two component shares with year effects explained {100*DF['r2_both_2015_2023']:.0f}% of the variance in the judged share (year effects alone, {100*DF['r2_year_only_2015_2023']:.0f}%), and {100*DF['r2_between_both_2015_2023']:.0f}% of between-province differences (eGFR alone, {100*DF['r2_between_egfr_2015_2023']:.0f}%; proteinuria alone, {100*DF['r2_between_dip_2015_2023']:.0f}%). In 2024 the share with an eGFR of 150 mL/min/1.73 m² or more fell from {100*NT[2023]['egfr_ge150']/NT[2023]['egfr_measured']:.1f}% to {100*NT[2024]['egfr_ge150']/NT[2024]['egfr_measured']:.1f}%. The analysis was therefore restricted to 2015–2023."),
("Screening and geography",
 f"Over 2015–2023, {N['exam_total']/1e6:.1f} million examinations recorded {N['cases_total']:,} judgements of suspected kidney disease in {N['n_rows']:,} district-years (Table 1). Pooled standardised ratios ranged from {T1[PER]['sir_p10']:.2f} to {T1[PER]['sir_p90']:.2f} between the 10th and 90th percentile districts. Moran's I of observed log ratios was {N['moran_pooled']:.2f} pooled over years and {N['moran_year_min']:.2f}–{N['moran_year_max']:.2f} annually. Residual RRs ranged from {N['rr_min']:.2f} to {N['rr_max']:.2f}, with {N['n_hot']} hot spots, {N['hot_capital']} of them in the capital region of Seoul, Incheon and Gyeonggi, and {N['n_cold']} cold spots, mainly in {sidos(N['cold_by_sido'], 3)} (Fig. 1A); annual rankings were moderately concordant (Kendall's W {N['kendall_W']:.2f}) ({sup('maps')})."),
("District correlates",
 f"The negative binomial likelihood was selected (WAIC {_LK['nbinomial']:,.1f} vs {_LK['poisson']:,.1f} for Poisson), and adding the {NHYP} covariates lowered WAIC to {N['waic_main']:,.1f}. Four of the {NHYP} hypothesis covariates were credible and three were subset-stable (Table 2). The standardised ratio was higher with a larger share of examinees treated for hypertension or diabetes ({ci(DX)}), more suspected hypertension at screening ({ci(HTN)}) and more suspected diabetes at screening ({ci(DM)}); each was credible in every subset that contained it. Against the expected direction, tertiary education was associated with a higher ratio ({ci(EDU)}) but was credible in only {_pc(EDU)} of subsets. Walking ({ci('walking_practice_rate')}), moderate or vigorous activity ({ci('moderate_pa_rate')}), public sports facilities ({ci('public_sports_facilities_per_100k')}), smoking, obesity, albumin testing, specialists, uptake and basic livelihood security receipt ({ci(BLR)}) were not credibly associated, and none of the negative-control exposures was."),
("Robustness",
 f"All four space–time interaction types fitted better than the principal model (type {BEST.replace('KH_type', '')} best), and the three subset-stable covariates remained credible in each (Fig. 2; Table 2). With the provincial eGFR and proteinuria shares added, both of which were associated with the district ratio (eGFR below 60 mL/min/1.73 m², {tci(C1('K1_prov_components', 'prov_egfr_z'))}; proteinuria, {tci(C1('K1_prov_components', 'prov_dip_z'))}; WAIC lower by {N['waic_main'] - N['comp_waic']['K1_prov_components']:,.0f}), the estimates were {tci(C1('K1_prov_components', DX))} for the treated share, {tci(C1('K1_prov_components', HTN))} for suspected hypertension and {tci(C1('K1_prov_components', DM))} for suspected diabetes. Within districts over time, the treated share ({tci(N['bw'][DX + '__within'])}) and suspected hypertension ({tci(N['bw'][HTN + '__within'])}) were credible, and between districts suspected diabetes was ({tci(N['bw'][DM + '__between'])}) ({sup('specs')}). The three covariates were credible in both windows and with expected numbers from the resident population ({sup('windows')}), and in {ALT[DX]['kept']}, {ALT[HTN]['kept']} and {ALT[DM]['kept']} of {ALT_N} alternative specifications. In the comparison outcomes, treated gastric cancer and infectious disease, the three covariates had rate ratios of 1.000 or slightly below. E-values were small (point estimates {N['evalue'][DX]['E_point']:.2f}, {N['evalue'][HTN]['E_point']:.2f} and {N['evalue'][DM]['E_point']:.2f}). Residual Moran's I was {N['moran_resid']:.2f}, and 95% predictive intervals covered {100*N['oos']['coverage95']:.1f}% of held-out 2023 numbers, conditional on same-year covariates."),
]

# 문장 주장 대조(결과표와 어긋나면 빌드 중단)
assert set(N["robust_set"]) == set(ROB) and all(N["mv"][v]["cred_frac"] == 1 for v in ROB)
assert N["n_cred_hyp"] == 4 and all(M[v]["cred"] and M[v]["IRR"] > 1 for v in ROB + [EDU]) and not N["mv"][EDU]["robust"]
assert not any(M[v]["cred"] for v in NULLV) and not any(N["negctl"][v]["cred"] for v in N["negctl"])
assert all(N["s43_waic"][a] < N["waic_main"] for a in KH) and all(S43(a, v)[3] for a in KH for v in ROB)
assert all(N["comp"][("K1_prov_components", v)][3] for v in ROB + ["prov_egfr_z", "prov_dip_z"]) and N["comp_waic"]["K1_prov_components"] < N["waic_main"]
assert all(N["win_irr"][(v, w)][3] for v in ROB for w in ("W1_2015-18", "W2_2019-23")) and all(N["epop"][v][3] for v in ROB)
assert N["bw"][DX + "__within"][3] and N["bw"][HTN + "__within"][3] and N["bw"][DM + "__between"][3] and not N["bw"][DX + "__between"][3]
assert all(N["nco"][(o, v)][0] <= 1.0 for o in ("GCA", "INFECT") for v in ROB)
assert N["covid"][HTN][3] and N["covid"][HTN][0] < 1 and N["covid"][DM][3] and N["covid"][DM][0] < 1
assert NT[2012]["ratio_susp_to_egfr"] < 1 and NT[2014]["ratio_susp_to_egfr"] < 1 and all(NT[y]["ratio_susp_to_egfr"] >= 1 for y in range(2015, 2024))
assert round(100 * (NT[2023]["ratio_susp_to_egfr"] - 1)) == 68 and round(100 * DF["r2_between_both_2015_2023"]) == 76 and round(N["exam_total"] / 1e6, 1) == 137.5
assert (round(M[DX]["IRR"], 3), M[DX]["lo"], M[DX]["hi"]) == (1.084, 1.055, 1.114) and (M[HTN]["IRR"], M[HTN]["lo"], M[HTN]["hi"]) == (1.013, 1.003, 1.024) and (M[DM]["IRR"], M[DM]["lo"], M[DM]["hi"]) == (1.018, 1.007, 1.028)
assert list(N["cold_by_sido"])[:2] == ["경상북도", "경상남도"] and N["hot_capital"] >= N["n_hot"] / 2

if __name__ == "__main__":
    import re
    for h, t in METHODS + RESULTS: print("##", h, "\n", t, "\n")
