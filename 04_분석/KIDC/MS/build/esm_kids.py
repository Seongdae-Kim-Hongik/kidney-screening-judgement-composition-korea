# esm_kids.py — Supplementary material(단일 파일: Table S1-S7 + Figure S1, 본문 첫 인용 순서). 수치는 결과 CSV에서만(2026-11-17, 32호 KIDC).
#  single-anonymized: 첫 쪽에 제목·저자. 영국식 철자(TX._emit에서 brit 적용).
import os, json, subprocess, pandas as pd
from docx.shared import Cm
import content_kids as C
from tables_kids import LABEL, GROUPS
from build_ms import TX, TITLE as DTITLE, AUTHOR, AFFIL, EMAIL, foot_row, read_draft, ref
from british import brit
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out"); B = os.path.dirname(MSD); RS = os.path.join(B, "results_std3")
N = C.N
f3 = lambda t: f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
B1 = "Intervals with a bound shown as 1.000 were classified from unrounded values."
ROBV = [C.DX, C.HTN, C.DM]
SH = {C.DX: "Treated hypertension and diabetes", C.HTN: "Suspected hypertension", C.DM: "Suspected diabetes"}
J = TX(cite="bracket")
_NB = [False]
def TF(title, header, rows, foot="", fs=8, fixed=1, per=None, left=()):
    title = brit(title); header = [brit(h) for h in header]; rows = [[brit(x) for x in r] for r in rows]
    if per is None or len(header) - fixed <= per:
        (None if _NB[0] else J.page_break()); _NB[0] = False; J.table_fit(title, header, rows, "", fs_max=fs, left_cols=left)
        if foot: foot_row(J, foot, 8, 12)
        return
    rest = list(range(fixed, len(header))); chunks = [rest[i:i + per] for i in range(0, len(rest), per)]
    _f = _NB[0]; _NB[0] = False
    for n, ch in enumerate(chunks):
        cols = list(range(fixed)) + ch; tt = f"{title} (part {'ABCD'[n]})"
        rr = [r if r and r[0] == "__H__" else [r[c] for c in cols] for r in rows]
        (None if (_f and n == 0) else J.page_break()); J.table_fit(tt, [header[c] for c in cols], rr, "", fs_max=fs)
        if foot: foot_row(J, foot, 8, 12)
J.para("<b>Supplementary material</b>"); J.para(f"Article title: {DTITLE}"); J.para("Journal: Journal of Nephrology"); J.para(f"Author: {AUTHOR}"); J.para(f"Affiliation: {AFFIL}"); J.para(f"Email of the corresponding author: {EMAIL}")
J.para("Contents: Table S1 (composition of the judgement); Table S2 (supplementary methods); Table S3 (covariates); Table S4 (panel checks); Table S5 (robustness, comparison outcomes, negative controls and model checks); Figure S1 (persistence); Table S6 (windows and the coronavirus disease 2019 period); Table S7 (STROBE checklist).")
_LK = C._LK; _MT = pd.read_csv(os.path.join(B, "panel_META_KIDC_std3.csv"), encoding="utf-8-sig").set_index("variable")
_imp = lambda v: int(_MT.loc[v, "n_imputed_interp"] + _MT.loc[v, "n_imputed_sgg_mean"] + _MT.loc[v, "n_imputed_year_mean"])
# Table S1 — 판정 구성 대조(88K_kidc_definition)
DF = N["defn"]; NT = DF["national"]
rows = [["__H__", "National, % of examinees (suspected = judgement; eGFR and dipstick = published distributions)"]]
for y in range(2012, 2025):
    r = NT[y]; rows.append([f"  {y}{' (analysed)' if 2015 <= y <= 2023 else ''}", f"{r['pct_suspected']:.2f}", f"{r['pct_egfr_lt60']:.2f}", f"{r['pct_dip_1plus']:.2f}", f"{r['ratio_susp_to_egfr']:.2f}", f"{r['excess_share_of_dip']:.2f}"])
rows += [["__H__", f"Provinces ({DF['n_province']}) × years, 2015–2023: suspected % regressed on component shares"]]
rows += [["  Year effects only, R²", f"{DF['r2_year_only_2015_2023']:.2f}", "", "", "", ""],
         ["  Year effects + eGFR below 60, R²", f"{DF['r2_egfr_2015_2023']:.2f}", "", "", "", ""],
         ["  Year effects + dipstick 1+ or more, R²", f"{DF['r2_dip_2015_2023']:.2f}", "", "", "", ""],
         ["  Year effects + both, R²", f"{DF['r2_both_2015_2023']:.2f}", f"{DF['b_egfr_both_2015_2023']:.2f}", f"{DF['b_dip_both_2015_2023']:.2f}", "", ""],
         ["  Between-province differences (year-centred), both components, R²", f"{DF['r2_between_both_2015_2023']:.2f}", "", "", "", ""],
         ["  Between-province differences, eGFR only; dipstick only, R²", f"{DF['r2_between_egfr_2015_2023']:.2f}", f"{DF['r2_between_dip_2015_2023']:.2f}", "", "", ""]]
rows += [["__H__", "eGFR distribution, % of examinees with eGFR measured"]]
for y in (2022, 2023, 2024):
    r = NT[y]; rows.append([f"  {y}: 150 or more; 60–79 mL/min/1.73 m²", f"{100*r['egfr_ge150']/r['egfr_measured']:.2f}", f"{100*r['egfr_60_79']/r['egfr_measured']:.2f}", "", "", ""])
J.page_break(); _NB[0] = True
TF("Table S1. Composition of the suspected kidney disease judgement: comparison with published distributions of estimated glomerular filtration rate and dipstick proteinuria",
   ["Year or quantity", "Suspected, %", "eGFR <60, %", "Dipstick 1+, %", "Suspected ÷ eGFR <60", "Excess ÷ dipstick 1+"], rows,
   "eGFR, estimated glomerular filtration rate (mL/min/1.73 m²). Sources: general health screening judgement results (DT_35007_N104, N099), eGFR distribution by age (N129, national) and province (N128), dipstick proteinuria distribution by age (N065, national) and province (N064), Korean Statistical Information Service, accessed 17 November 2026. Excess = judgements minus examinees with eGFR below 60; Excess ÷ dipstick 1+ = excess as a share of examinees with dipstick proteinuria 1+ or more. In the regression rows, the second and third columns give the coefficients (percentage points per percentage point) for eGFR below 60 and dipstick 1+ or more. Before 2015 the judgement was below the number with eGFR below 60, and in 2024 the eGFR distribution changed abruptly; 2015–2023 was analysed.", fs=8)
# Table S1 — supplementary methods(본문 텍스트 표)
SM = [("Outcome and denominator", f"The national statistics portal publishes, for each year, the number of general health screening examinees with a judgement and the number judged to have suspected kidney disease by administrative district, and the same numbers nationally by sex and 5-year age group. The published criteria for the suspected kidney disease judgement are an estimated glomerular filtration rate below 60 mL/min/1.73 m² or a serum creatinine above 1.5 mg/dL; Table S1 shows that the judgement also follows dipstick proteinuria. The analysis used 2015–2023. Rows for ordinary districts were used; where a city reported both a city total and sub-city wards, the wards were used to match the district boundary set. Sejong, created in 2012, had no separate district results and was excluded, leaving {N['n_districts']} districts. One district-year (2016) missing from the compiled panel was taken from the original statistics; district sums were 99.4–99.7% of national totals in 2015–2023."),
      ("Standardisation", f"Indirect standardisation followed standard methods [S1]. Expected numbers E = Σ(examinees in sex s and age a) × (national rate in s and a), rescaled each year to the national number with suspected kidney disease. District examinees by sex and age were estimated as the resident population by sex and 5-year age group (registration statistics [S2]) multiplied by national uptake in that group and rescaled to the observed district examinees by sex. The ratio of standardised to crude expected numbers ranged from {N['estd_ecrude'][0]:.2f} to {N['estd_ecrude'][1]:.2f} across district-years. In the resident-based sensitivity analysis, expected numbers were computed from the resident population by sex and age."),
      ("Covariates", "Suspected hypertension and suspected diabetes are the shares of general health screening examinees judged to have suspected disease on measured blood pressure and fasting glucose; the treated share is the sum of the shares of examinees already treated for hypertension and for diabetes (correlation 0.95 between the two shares; variance inflation factors 16 and 18 when entered separately), combined before any covariate model was fitted; the obesity category is the share judged normal with lifestyle management for obesity. Community Health Survey indicators are age-standardised district estimates [S3]. Tertiary education is the census share of adults (2015 and 2020, interpolated and held at the 2020 value thereafter). Basic livelihood security values for 2021–2023 that fell below 20% or above five times the mean of 2020 and 2024 (33 cells) were treated as missing and interpolated within districts."),
      ("Models", f"Software: R 4.6.0 [S4] with R-INLA; Python 3.9 for data preparation, emerging hot spot analysis and figures. Negative binomial likelihood (WAIC of the forced-controls model {_LK['nbinomial']:,.1f} vs {_LK['poisson']:,.1f} for Poisson); log expected numbers as offset; Besag–York–Mollié 2 district effect with penalised-complexity priors [S5] (P(σ>0.5)=0.01; P(φ<0.5)=2/3); first-order random-walk and independent year effects; one thread per fit. District adjacency was taken from an audited 593-edge contact graph with island districts linked to the nearest mainland district. Regions for region-specific slopes: Capital (Seoul, Incheon, Gyeonggi), Chungcheong, Honam, Yeongnam and Gangwon–Jeju. Covariates with a variance inflation factor above 10 were retained and reported (the share aged 80 years or older, a forced control). Robustness to covariate selection used a multiverse of random covariate subsets [S6]; district means and within-district deviations followed the within–between decomposition [S7]; the spatial confounding sensitivity analysis followed the Spatial+ approach [S8]; negative-control exposures [S9] and E-values [S10] addressed residual confounding."),
      ("Composition analysis", "National and provincial numbers of examinees with an estimated glomerular filtration rate below 60 mL/min/1.73 m² (DT_35007_N129, N128) and with dipstick proteinuria of 1+ or more (N065, N064) were retrieved on 17 November 2026. Provinces were matched to the district panel by province name; Sejong was not observed. The judged share by province and year (district numbers summed) was regressed by ordinary least squares on the two component shares with year indicators; between-province variance explained was estimated after centring each share on its yearly mean. The provincial component shares were then standardised and added to the principal model, together and one at a time.")]
J.page_break(); J.table_fit(brit("Table S2. Supplementary methods"), ["Topic", "Description"], [[a, brit(b)] for a, b in SM], "", fs_max=8, left_cols=(1,))
# Table S3 — covariates
J_SETS = json.load(open(os.path.join(B, "sets_KIDC_std3.json"), encoding="utf-8"))
DIRN = {k: v.split()[0].replace("-", "−") for k, v in J_SETS["expected_direction"].items()}
MAPV = {_MT.loc[v, "source_column"]: v for v in _MT.index}
DIR = {MAPV[k]: d for k, d in DIRN.items() if k in MAPV}
SRC = {"kchs": "KCHS", "chk": "NHIS screening", "eloc": "KOSIS", "fac": "MCST facilities", "nhis": "NHIS"}
EXTSRC = {"ext__pop80_share": "Population registry", "ext__tertiary_educated_share": "Census", "ext__basic_livelihood_rate": "KOSIS", "ext__im_specialists_per100k": "KOSIS", "ext__dx_cardiometabolic_share": "NHIS screening"}
def unit(l): return "Std. rate, %" if "(SR %)" in l else ("per 100,000" if ("per 100k" in l or "per 100,000" in l) else ("per 1,000" if ("per 1000" in l or "per 1,000" in l) else ("ratio" if "per 100 women" in l else ("%" if "%" in l else "index"))))
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = _MT.loc[v]; sc = str(m.source_column); src = EXTSRC.get(sc, SRC.get(sc.split("__")[0], sc.split("__")[0]))
        rows.append([f"  {LABEL[v]}", unit(str(m.label_en)), src, f"{int(m.obs_year_min)}–{int(m.obs_year_max)}", ("NA" if m.role == "forced" else DIR[v]), f"{_imp(v):,}"])
assert all(r[4] in ("+", "−", "NA") for r in rows if r[0] != "__H__")
TF("Table S3. Source, observed years, expected direction and filled cells for each covariate", ["Covariate", "Unit", "Source", "Years", "Direction", "Filled"], rows,
   f"KCHS, Community Health Survey; KOSIS, Korean Statistical Information Service; MCST, Ministry of Culture, Sports and Tourism; NHIS, National Health Insurance Service; NA, no direction specified (forced control); ratio, men per 100 women; Std. rate, age-standardised rate; Filled, filled cells of {N['n_rows']:,} district-years. Directions were fixed before covariate models were fitted. 33 basic livelihood security cells (2021–2023) were set to missing and interpolated, and tertiary education was observed in the 2015 and 2020 censuses, interpolated and held at the 2020 value; these values were prepared before panel construction and are not counted as filled.", fs=7.5)
# Table S4 — panel checks
imp = json.load(open(os.path.join(RS, "S41_imputed_cells.json")))
rows = [["Year with all districts zero or missing", "≥98% of districts in a year", "1 (COVID-19 period indicator)", "None (indicator by design)"],
        ["Year means differ twofold or more", "Largest/smallest positive yearly mean ≥2", "Outcome, expected numbers and standardised covariates with yearly means near 0", "Original-scale columns checked; retained"],
        ["Ratio-type column above 100", "Maximum >100 for a rate or ratio", "1 (sex ratio, men per 100 women)", "Retained (definition)"],
        ["Missing district-years", "No observation", f"{sum(imp.values()):,} cells", "Filled within districts; perturbation sensitivity"],
        ["Outcome reconstruction", "District counts equal compiled panel", "0 differences; 1 compiled blank filled from source", "None"],
        ["Implausible source value", "2021–2023 value <20% or >5 times adjacent mean", "Basic livelihood security, 33 cells", "Set to missing and interpolated"],
        ["Collinearity", "Variance inflation factor >10", "Share aged 80 years or older (forced control)", "Retained and reported"]]
TF("Table S4. Panel checks: rules, thresholds, flags and actions", ["Check", "Threshold", "Flags in this panel", "Action"], rows, left=(1, 2, 3), foot=f"Checks were run on the analytic panel ({N['n_rows']:,} district-years) before any covariate model was fitted.", fs=8)
# Table S5 — robustness
LO = pd.read_csv(os.path.join(RS, "S41_leaveout_ranges.csv")).set_index(["set", "cov"])
def rrow(lab, fn): return [lab] + [fn(v) for v in ROBV]
rows = [rrow("Subsets credible / same sign, %", lambda v: f"{100*N['mv'][v]['cred_frac']:.0f} / {100*N['mv'][v]['sign_agree']:.0f}"),
        rrow("Alternative, province and year fits retained", lambda v: f"{N['retention'][v]['kept']}/{N['retention'][v]['n_specs']}"),
        rrow("Leave-one-province retained", lambda v: f"{LO.loc[('province', v), 'n_cred_same_sign']}/{LO.loc[('province', v), 'n']}"),
        rrow("Leave-one-year retained", lambda v: f"{LO.loc[('year', v), 'n_cred_same_sign']}/{LO.loc[('year', v), 'n']}"),
        rrow("Perturbed filled values, pooled RR", lambda v: f"{N['rubin'][v]['IRR_pooled']:.3f} ({N['rubin'][v]['lo']:.3f}–{N['rubin'][v]['hi']:.3f})"),
        rrow("Age-only standardisation", lambda v: f3(N["sens_main"]["s8"][v])),
        rrow("Share aged 80+ not forced", lambda v: f3(N["sens_main"]["s2"][v])),
        rrow("Queen contiguity graph", lambda v: f3(N["sens_main"]["s577"][v])),
        rrow("Expected numbers from residents", lambda v: f3(N["epop"][v])),
        rrow("Knorr-Held type I", lambda v: f3(N["s43"][("KH_typeI", v)])),
        rrow("Knorr-Held type III", lambda v: f3(N["s43"][("KH_typeIII", v)])),
        rrow("District mean (between)", lambda v: f3(N["bw"][v + "__between"])),
        rrow("Two-way-centred deviation (within)", lambda v: f3(N["bw"][v + "__within"])),
        rrow("Covariates lagged 1 year", lambda v: f3(N["s41"][("E1_lag1", v)])),
        rrow("Covariates lagged 2 years", lambda v: f3(N["s41"][("E2_lag2", v)])),
        rrow("Provincial eGFR <60 and dipstick shares added", lambda v: f3(N["comp"][("K1_prov_components", v)])),
        rrow("Provincial dipstick share added", lambda v: f3(N["comp"][("K2_prov_dipstick", v)])),
        rrow("Provincial eGFR <60 share added", lambda v: f3(N["comp"][("K3_prov_egfr", v)])),
        rrow("Gastric cancer care (comparison outcome)", lambda v: f3(N["nco"][("GCA", v)])),
        rrow("Infectious disease care (comparison outcome)", lambda v: f3(N["nco"][("INFECT", v)])),
        rrow("ΔWAIC, region-specific vs common slope", lambda v: f"{N['s50_region_dwaic'][v]:+.1f}"),
        rrow("E-value, point / limit", lambda v: f"{N['evalue'][v]['E_point']:.2f} / {N['evalue'][v]['E_limit']:.2f}")]
J.page_break(); _NB[0] = True
TF("Table S5. Robustness of the three subset-stable covariates", ["Analysis"] + [SH[v] for v in ROBV], rows,
   "RR, rate ratio per 1 standard deviation (95% credible or pooled interval). Retained = credible with the principal-model sign. Alternative fits: forced controls smoothed; Poisson with observation-level effect; second-order random-walk and first-order autoregressive year effects; province-by-year effect; Spatial+-type adjustment; covariates lagged 1 and 2 years; extreme district-years refilled; survey covariates averaged over 3 years; odd and even years; plus leave-one-province and leave-one-year fits. Comparison outcomes are numbers of people treated for gastric cancer (C16) and infectious diseases (A00–B99), each with its own expected numbers. " + B1, fs=7.5, per=3)
NCN = {"hit_and_run_rate": "Hit-and-run accidents", "fires_per_10000": "Fires per 10,000", "waste_recycling_rate": "Household waste recycling"}
rows = [["__H__", "Negative-control exposures (added one at a time)"]] + [[f"  {NCN[k]}", f"{v['IRR']:.3f} ({v['lo']:.3f}–{v['hi']:.3f})"] for k, v in N["negctl"].items()]
rows += [["__H__", "Model checks"], ["  95% posterior predictive coverage, %", f"{100*N['ppc']['coverage95']:.1f}"], ["  50% posterior predictive coverage, %", f"{100*N['ppc']['coverage50']:.1f}"],
         ["  PIT Kolmogorov–Smirnov P", f"{N['ppc']['pit_ks_p']:.2g}"], ["  Held-out 2023 coverage (95%), %", f"{100*N['oos']['coverage95']:.1f}"],
         ["  Residual Moran's I (permutation P)", f"{N['moran_resid']:.2f} ({N['moran_resid_p']:.2f})"],
         ["  Linear predictor variance, structured spatial, %", f"{100*N['varpart']['spatial_structured']['share_of_linear_predictor_var']:.1f}"],
         ["  Linear predictor variance, hypothesis covariates, %", f"{100*N['varpart']['fixed_hypothesis']['share_of_linear_predictor_var']:.1f}"]]
TF("Table S5 (continued). Negative-control exposures and model checks", ["Analysis", "Result"], rows, "Rate ratios per 1 standard deviation (95% credible interval). PIT, probability integral transform. Variance shares are the variance of each linear-predictor component divided by the variance of the full linear predictor and are not additive because components are correlated. " + B1, fs=9)
# Figure S1
_T1 = N["T1"]; _eh = N["ehsa"]
J.page_break(); J.head("Figure S1. Persistence of the district pattern", 2)
J.para(f"The 10th–90th percentile range of district standardised ratios was {_T1['W1_2015-18']['sir_p10']:.2f}–{_T1['W1_2015-18']['sir_p90']:.2f} in 2015–2018 and {_T1['W2_2019-23']['sir_p10']:.2f}–{_T1['W2_2019-23']['sir_p90']:.2f} in 2019–2023. "
       f"Hot spots numbered {N['win_hot']['W1_2015-18']} and {N['win_hot']['W2_2019-23']}, and cold spots {N['win_cold']['W1_2015-18']} and {N['win_cold']['W2_2019-23']}, in the two windows; the Spearman correlation of window residual rate ratios was {N['win_rr_rho']:.2f}, and Kendall's W of annual district rankings of empirical Bayes-smoothed ratios was {N['kendall_W']:.2f}. "
       f"Emerging hot spot analysis classified {_eh['Persistent hot']} districts as persistent, {_eh['Consecutive hot']} as consecutive and {_eh['Sporadic hot']} as sporadic hot spots; {_eh['Persistent cold']} as persistent, {_eh['Consecutive cold']} as consecutive and {_eh['Sporadic cold']} as sporadic cold spots; {_eh['No pattern']} as showing no pattern; and {N['n_districts'] - _eh['Persistent hot'] - _eh['Consecutive hot'] - _eh['Sporadic hot'] - _eh['Persistent cold'] - _eh['Consecutive cold'] - _eh['Sporadic cold'] - _eh['No pattern']} in other categories (oscillating hot spot or new cold spot).")
_pp = J.para(""); _pp.add_run().add_picture(os.path.join(HERE, "figs", "KIDC_FigS1.png"), width=Cm(16))
J.para("<b>Figure S1.</b> (A) Emerging hot spot analysis (Getis–Ord Gi* with Mann–Kendall trend) of empirical Bayes-smoothed standardised ratios, 2015–2023; numbers of districts in parentheses. (B) Number of calendar windows (2015–2018, 2019–2023) in which each district was a residual hot or cold spot in the principal model refitted in each window. Grey, district without separate results.")
J.para("Alt text: Two maps of South Korea. The left map shows persistent and consecutive hot spots in north-eastern Seoul and nearby Gyeonggi and persistent and consecutive cold spots in South Gyeongsang, Ulsan and South Chungcheong. The right map shows districts that were hot spots in both windows concentrated around the capital region and cold spots in both windows in the south-east.")
# Table S6 — windows
WI = pd.read_csv(os.path.join(RS, "S4_window_IRR.csv")).set_index(["cov", "window"]); IT = pd.read_csv(os.path.join(RS, "S4_interaction.csv")).set_index("cov")
CV = pd.read_csv(os.path.join(RS, "S5_covid.csv")); CVX = CV[CV.term == "var_x_post"].set_index("cov")
rows = []
for g, vs in GROUPS[:-1]:
    rows.append(["__H__", g])
    for v in vs: rows.append([f"  {LABEL[v]}"] + [f3(tuple(WI.loc[(v, w), ["IRR", "lo", "hi", "cred"]])) for w in ("W1_2015-18", "W2_2019-23")] + [f3(tuple(IT.loc[v, ["IRR_ratio", "lo", "hi", "cred"]])), f3(tuple(CVX.loc[v, ["IRR", "lo", "hi", "cred"]]))])
J.page_break(); _NB[0] = True
TF("Table S6. Rate ratios for the hypothesis covariates by calendar window and interactions with the window and with the coronavirus disease 2019 period", ["Covariate", "2015–2018", "2019–2023", "Ratio, 2019–2023 vs 2015–2018", "Interaction with 2020 onwards"], rows,
   "Rate ratio per 1 standard deviation of the whole period (95% credible interval). Window columns: principal model structure fitted separately to each window with all forced controls. Ratio: exponentiated covariate-by-window interaction from a pooled model, which is not the ratio of the separately fitted window estimates. Interaction with 2020 onwards: ratio of the rate ratio from 2020 onwards to that before 2020. " + B1, fs=7.5, fixed=1, per=2)
# Table S7 STROBE
DS = [x[4:].strip() for x in read_draft()["Discussion"] if x.startswith("### ")]; MH = [h for h, _ in C.METHODS]; RH = [h for h, _ in C.RESULTS]
LIM = next(d for d in DS if "limitation" in d.lower())
CK = [("Title and abstract", "1", "Title; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"), ("Study design", "4", f"Methods, {MH[0]}"), ("Setting", "5", f"Methods, {MH[0]}"),
      ("Participants", "6", f"Methods, {MH[0]}; {MH[1]} (district aggregates; ecological)"), ("Variables", "7", f"Methods, {MH[2]}; {MH[3]}; Table S3"), ("Data sources/measurement", "8", "Methods; Table S1"),
      ("Bias", "9", f"Methods, {MH[5]}; Tables S2, S4 and S5"), ("Study size", "10", f"Methods, {MH[0]} (all {N['n_districts']} districts with results)"), ("Quantitative variables", "11", f"Methods, {MH[3]}"),
      ("Statistical methods", "12", f"Methods, {MH[4]}; {MH[5]}"), ("Participants (flow)", "13", "Not applicable (aggregate district data)"), ("Descriptive data", "14", f"Results, {RH[0]}; Table 1"), ("Outcome data", "15", f"Results, {RH[0]}"),
      ("Main results", "16", f"Results, {RH[1]}; {RH[2]}; Table 2; Fig. 1"), ("Other analyses", "17", f"Results, {RH[3]}; Fig. 2; Tables S5 and S6; Figure S1"),
      ("Key results", "18", "Discussion, first paragraph"), ("Limitations", "19", f"Discussion, {LIM}"), ("Interpretation", "20", "Discussion"), ("Generalisability", "21", f"Discussion, {LIM}"),
      ("Funding", "22", "Title page; Funding")]
J.page_break()
J.table_fit("Table S7. STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=9, left_cols=(2,))
foot_row(J, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology.", 8, 12)
SREF = ["inskip1983methods", "web:mois2026population", "kang2015korea", "web:rcore2026", "simpson2017penalising", "steegen2016increasing", "bell2015explaining", "dupont2022spatial", "lipsitch2010negative", "vanderweele2017sensitivity"]
J.page_break(); J.para("<b>Supplementary references</b>"); J.raw = True
for i, k in enumerate(SREF, 1): J.para(f"S{i}. " + ref(k))
J.raw = False
ps = os.path.join(OUT, "Supplementary_material.docx"); J.doc_title = "Supplementary material"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_kidc_esm", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps))
