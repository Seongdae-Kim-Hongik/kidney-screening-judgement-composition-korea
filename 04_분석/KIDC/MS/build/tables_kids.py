# tables_kids.py — 32호 KIDC 원고 표 1·2(수치는 numbers_kids → content_kids에서만, 2026-11-17).
import content_kids as C
N = C.N
TAB1_COV = [("pop80_share", "Population aged 80 years or older, %"), (C.DX, "Treated hypertension and diabetes, summed % of examinees"),
            (C.HTN, "Suspected hypertension at screening, %"), (C.DM, "Suspected diabetes at screening, %"), ("screening_normalB_obesity_share", "Obesity management category at screening, %"),
            ("current_smoking_rate", "Current smoking, %"), ("walking_practice_rate", "Walking practice, %"), ("moderate_pa_rate", "Moderate or vigorous physical activity, %"), ("public_sports_facilities_per_100k", "Public sports facilities per 100,000"),
            ("diabetic_kidney_test_rate", "Urine albumin testing in diabetes, %"), ("im_specialists_per_100k", "Internal medicine specialists per 100,000"),
            ("screening_uptake", "Screening uptake, %"), (C.BLR, "Basic livelihood security recipients, %"), (C.EDU, "Tertiary education, % of adults")]
def table1():
    T = N["T1"]; cols = ["W1_2015-18", "W2_2019-23", "2015-2023"]
    rows = [["__H__", "Screening"],
            ["  District-years, n"] + [f"{T[c]['n']:,}" for c in cols],
            ["  Examinations, million"] + [f"{T[c]['exam']/1e6:.1f}" for c in cols],
            ["  Suspected kidney disease, n"] + [f"{T[c]['cases']:,}" for c in cols],
            ["  Suspected kidney disease, % of examinees"] + [f"{T[c]['pos']:.2f}" for c in cols],
            ["  District standardised ratio, median<sup>a</sup>"] + [f"{T[c]['sir_med']:.2f}" for c in cols],
            ["  District standardised ratio, P10–P90<sup>a</sup>"] + [f"{T[c]['sir_p10']:.2f}–{T[c]['sir_p90']:.2f}" for c in cols],
            ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1_COV:
        mx = max(abs(T[c]['cov'][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:,.{dp}f} ({T[c]['cov'][v][1]:,.{dp}f})" for c in cols])
    foot = ("Suspected kidney disease: programme judgement at general health screening, which on reconciliation with published distributions combines reduced estimated glomerular filtration rate and dipstick proteinuria (Table S1, Supplementary material). "
            "<sup>a</sup>Observed over expected numbers summed over the window, with expected numbers from national rates by sex and 5-year age group applied to district examinees. "
            "P10–P90, 10th–90th percentile; SD, standard deviation.")
    return ("Table 1. General health screening, suspected kidney disease judgements and district characteristics by calendar window, Korea, 2015–2023", ["Characteristic", "2015–2018", "2019–2023", "2015–2023"], rows, foot)

GROUPS = [("Upstream of kidney damage", [C.DX, C.HTN, C.DM, "screening_normalB_obesity_share"]),
          ("Behaviour", ["current_smoking_rate"] + C.PA),
          ("Care and selection", ["diabetic_kidney_test_rate", "im_specialists_per_100k", "screening_uptake"]),
          ("Structure", [C.BLR, C.EDU]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {C.DX: "Treated hypertension and diabetes (summed)", C.HTN: "Suspected hypertension (screening)", C.DM: "Suspected diabetes (screening)",
         "screening_normalB_obesity_share": "Obesity management category (screening)", "current_smoking_rate": "Current smoking",
         "walking_practice_rate": "Walking practice", "moderate_pa_rate": "Moderate or vigorous physical activity", "public_sports_facilities_per_100k": "Public sports facilities per 100,000",
         "diabetic_kidney_test_rate": "Urine albumin testing in diabetes", "im_specialists_per_100k": "Internal medicine specialists per 100,000", "screening_uptake": "Screening uptake",
         C.BLR: "Basic livelihood security recipients", C.EDU: "Tertiary education",
         "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1,000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged 80 years or older"}
def table2():
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"] and set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k2 = N["s43"][("KH_typeII", v)]; k4 = N["s43"][("KH_typeIV", v)]
            rows.append([f"  {LABEL[v]}", f"{m['IRR']:.3f} ({m['lo']:.3f}–{m['hi']:.3f})", f"{100*mv['cred_frac']:.0f}" if mv else "NA", f"{k2[0]:.3f} ({k2[1]:.3f}–{k2[2]:.3f})", f"{k4[0]:.3f} ({k4[1]:.3f}–{k4[2]:.3f})"])
    foot = (f"RR, rate ratio per 1 standard deviation; CrI, credible interval; NA, not applicable (forced into every specification). Principal model, negative binomial with a Besag–York–Mollié 2 district effect and random-walk and independent year effects (n={N['n_rows']:,} district-years). "
            f"<sup>a</sup>Share of the {N['n_specs_total']} covariate-subset fits containing the covariate in which the CrI excluded 1 (subset-stable, at least 75% with the same sign in at least 95%). "
            f"The share aged 80 years or older is a forced control beyond indirect standardisation and is not interpreted. <sup>b</sup>Principal model plus a Knorr-Held type II (difference in widely applicable information criterion −{-C.dW('KH_typeII'):,.0f}) or type IV (−{-C.dW('KH_typeIV'):,.0f}) space–time interaction.")
    return ("Table 2. District characteristics and the age- and sex-standardised ratio of suspected kidney disease judgements in the principal and space–time interaction models, 2015–2023", ["Characteristic", "Principal model RR (95% CrI)", "Subsets credible, %<sup>a</sup>", "Type II RR (95% CrI)<sup>b</sup>", "Type IV RR (95% CrI)<sup>b</sup>"], rows, foot)

