# numbers_kids.py — 32호 KIDC(검진 신장질환 의심 복합 판정, 2015-2023) 원고의 모든 수치를 결과 CSV에서 읽는다(2026-11-17).
#  기억·손입력 금지, assert로 정합 확인. 사용: from numbers_kids import load; N = load()
import os, glob, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3")
ROOT = os.path.dirname(os.path.dirname(B)); PAN = os.path.join(ROOT, "02_패널")
WIN = [("W1_2015-18", 2015, 2018), ("W2_2019-23", 2019, 2023)]; Y0, Y1 = 2015, 2023; PER = "2015-2023"
rd = lambda f, **k: pd.read_csv(os.path.join(RS, f), encoding="utf-8-sig", **k)
HTN, DM, BLR = "screening_suspected_hypertension_share", "screening_suspected_diabetes_share", "basic_livelihood_rate"
DX, EDU = "ext__dx_cardiometabolic_share", "tertiary_educated_share"
ROB = [DX, HTN, DM]
PA = ["walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k"]
CAP = ("서울", "경기", "인천")
SHP = os.environ.get("ST_SHP", os.path.join(HERE, "..", "..", "..", "..", "data", "boundary", "final.shp"))
COV = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share", DX, HTN, DM, "screening_normalB_obesity_share",
       "current_smoking_rate"] + PA + ["diabetic_kidney_test_rate", "im_specialists_per_100k", "screening_uptake", BLR, EDU]

def load():
    N = {}
    P = pd.read_csv(os.path.join(B, "panel_KIDC_std3.csv"), low_memory=False); N["n_rows"] = len(P); N["n_districts"] = P.fbd_region.nunique()
    assert (N["n_rows"], N["n_districts"]) == (2052, 228), (N["n_rows"], N["n_districts"])
    E = pd.read_csv(os.path.join(PAN, "KIDS_Estd3.csv")); E = E[(E.year >= Y0) & (E.year <= Y1)]
    assert int(E.cases.sum()) == int(P.cases.sum()) and abs(E.examinees.sum() - P.offset.sum()) < 1
    N["cases_total"] = int(P.cases.sum()); N["exam_total"] = float(E.examinees.sum())
    y = E.groupby("year")[["examinees", "cases"]].sum()
    N["exam_y"] = y.examinees.to_dict(); N["cases_y"] = y.cases.to_dict(); N["pos_y"] = (100 * y.cases / y.examinees).to_dict()
    N["pos_first"], N["pos_last"] = N["pos_y"][Y0], N["pos_y"][Y1]
    N["rho_std_crude"] = float(E[["SIR_std", "SIR_crude"]].corr(method="spearman").iloc[0, 1])
    N["estd_ecrude"] = (float((E.E_std / E.E_crude).min()), float((E.E_std / E.E_crude).max()))
    T1 = {}
    for wn, a, b in WIN + [(PER, Y0, Y1)]:
        q = P[(P.year >= a) & (P.year <= b)]; e = E[(E.year >= a) & (E.year <= b)]
        sir = q.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
        T1[wn] = dict(n=len(q), cases=int(q.cases.sum()), exam=float(e.examinees.sum()), pos=100 * q.cases.sum() / e.examinees.sum(),
                      sir_p10=sir.quantile(.1), sir_p90=sir.quantile(.9), sir_med=sir.median(),
                      cov={v: (q[f"{v}_raw"].mean(), q[f"{v}_raw"].std()) for v in COV})
    N["T1"] = T1
    # 판정 구성(88K_kidc_definition)
    N["defn"] = json.load(open(os.path.join(RS, "S47_kidc_definition.json"))); N["defn"]["national"] = {int(k): v for k, v in N["defn"]["national"].items()}
    # 공간
    s6m = rd("S6_moran_year.csv"); N["moran_year_min"], N["moran_year_max"] = s6m.moran_I.min(), s6m.moran_I.max(); N["moran_y"] = s6m.set_index("year").moran_I.to_dict()
    r8 = rd("S8_residual_moran.csv").set_index("quantity"); N["moran_pooled"] = r8.loc["observed_logSIR_pooled", "moran_I"]
    N["moran_resid"] = r8.loc["pearson_residual_area_mean", "moran_I"]; N["moran_resid_p"] = r8.loc["pearson_residual_area_mean", "p_perm"]
    h = rd("S3_main_hyper.csv"); ph = h[h.hyperpar.str.startswith("Phi")].iloc[0]; N["phi"] = (ph["mean"], ph["X0.025quant"], ph["X0.975quant"])
    s6 = rd("S6_spatial_RR.csv"); N["rr_min"], N["rr_max"] = s6.RR.min(), s6.RR.max()
    N["n_hot"], N["n_cold"] = int((s6["class"] == "hotspot").sum()), int((s6["class"] == "coldspot").sum())
    sido = s6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
    N["hot_by_sido"] = s6[s6["class"] == "hotspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["cold_by_sido"] = s6[s6["class"] == "coldspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["hot_capital"] = int(((s6["class"] == "hotspot") & s6.fbd_region.str.startswith(CAP)).sum())
    N["cold_capital"] = int(((s6["class"] == "coldspot") & s6.fbd_region.str.startswith(CAP)).sum())
    wm = rd("S4b_window_spatialRR.csv"); N["win_hot"] = wm[wm["class"] == "hotspot"].groupby("window").size().to_dict(); N["win_cold"] = wm[wm["class"] == "coldspot"].groupby("window").size().to_dict()
    hs = {w: set(wm[(wm.window == w) & (wm["class"] == "hotspot")].fbd_region) for w in wm.window.unique()}; N["hot_all_windows"] = len(set.intersection(*hs.values()))
    cs = {w: set(wm[(wm.window == w) & (wm["class"] == "coldspot")].fbd_region) for w in wm.window.unique()}; N["cold_all_windows"] = len(set.intersection(*cs.values()))
    _pv = wm.pivot_table(index="fbd_region", columns="window", values="RR").corr(method="spearman"); N["win_rr_rho"] = float(_pv.iloc[0, 1])
    pe = rd("S12_persistence.csv").set_index("set"); N["kendall_W"] = pe.loc[PER, "kendall_W"]
    N["ehsa"] = rd("S11_ehsa_summary.csv").set_index("category").n.to_dict()
    ehs = rd("S11_ehsa.csv"); N["ehsa_tab"] = ehs
    # 주모형·다중우주
    m3 = rd("S3_main_IRR.csv").set_index("cov"); N["main"] = m3[["IRR", "lo", "hi", "cred", "role", "label_en", "P_gt1"]].to_dict("index")
    N["n_hyp"] = int((m3.role == "hypothesis").sum()); N["n_cred_hyp"] = int(((m3.role == "hypothesis") & m3.cred).sum())
    s7 = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = s7[["n_specs", "cred_frac", "sign_agree", "robust", "IRR_median", "IRR_min", "IRR_max"]].to_dict("index")
    N["n_specs_total"] = int(s7.n_specs_total.iloc[0])
    N["n_robust"] = int(s7.robust.sum()); N["robust_set"] = list(s7.index[s7.robust])
    hb = open(os.path.join(B, "HM_best_KIDC_std3.txt")).read(); N["waic_forced"] = float(hb.split("ref_forced_only_WAIC=")[1].split()[0])
    N["waic_main"] = float(hb.split("S1_narrative_full(")[1].split(",")[0])
    N["waic_pois"] = float(hb.split("poisson ")[1].split()[0]); N["waic_nb"] = float(hb.split("nbinomial ")[1].split(")")[0])
    sc = pd.read_csv(os.path.join(B, "HM_setcompare_KIDC_std3.csv")); N["setcompare"] = sc
    nc = rd("S3_negcontrol.csv").set_index("cov"); N["negctl"] = nc[["IRR", "lo", "hi", "cred"]].to_dict("index")
    wi = rd("S4_window_IRR.csv"); N["win_irr"] = {(r.cov, r.window): (r.IRR, r.lo, r.hi, r.cred) for r in wi.itertuples()}
    it = rd("S4_interaction.csv"); N["win_int"] = {r.cov: (r.IRR_ratio, r.lo, r.hi, bool(r.cred)) for r in it.itertuples()}
    S43 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S43_part_*.csv"))]); N["s43"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in S43.itertuples()}
    N["s43_waic"] = S43.groupby("analysis").WAIC.first().to_dict()
    T9 = rd("S9_typeI_IRR.csv"); N["s43"].update({("KH_typeI", r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in T9.itertuples()}); N["s43_waic"]["KH_typeI"] = float(T9.WAIC.iloc[0])
    S41 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S41_part_*.csv"))]); N["s41"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in S41.itertuples()}
    N["s41_waic"] = S41.groupby("analysis").WAIC.first().to_dict(); N["s41_n"] = int(S41.analysis.nunique())
    N["s41_kept"] = S41.groupby("analysis").robust_kept.first().to_dict()
    N["retention"] = rd("S41_retention_by_cov.csv").set_index("cov").to_dict("index"); N["rubin"] = rd("S41_noise_rubin.csv").set_index("cov").to_dict("index")
    N["evalue"] = rd("S41_evalues.csv").set_index("cov").to_dict("index"); N["oos"] = rd("S41_oos2024.csv").iloc[0].to_dict()
    N["ppc"] = rd("S42_ppc.csv").iloc[0].to_dict(); N["varpart"] = rd("S42_variance_partition.csv").set_index("component").to_dict("index")
    N["nco"] = {(r.analysis.replace("H1_nco_", ""), r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in rd("S41_nco_detail.csv").itertuples()}
    N["bw"] = {r.cov: (r.IRR, r.lo, r.hi, r.cred) for r in S41[S41.analysis == "bw_twoway"].itertuples()}
    N["drop_prov_min"] = int(S41[S41.analysis.str.startswith("F1_")].groupby("analysis").robust_kept.first().min())
    N["drop_year_min"] = int(S41[S41.analysis.str.startswith("F2_")].groupby("analysis").robust_kept.first().min())
    so = rd("S10_offset_sensitivity_IRR.csv"); N["epop"] = {r.cov: (r.IRR, r.lo, r.hi, bool(r.cred)) for r in so.itertuples()}
    N["sens_main"] = {}
    for v in ["s577", "s2", "s8"]:
        m = pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_IRR.csv")).set_index("cov"); N["sens_main"][v] = {c: (m.loc[c, "IRR"], m.loc[c, "lo"], m.loc[c, "hi"], bool(m.loc[c, "cred"])) for c in m.index}
    rs = rd("S50_region_slopes.csv"); N["s50_region_dwaic"] = rs.groupby("covariate").dWAIC_vs_common.first().to_dict()
    N["s50_moran"] = rd("S50_resid_moran_by_spec.csv").set_index("spec").to_dict("index")
    N["parsim"] = rd("S50_parsimonious.csv").set_index("cov").to_dict("index")
    N["comp"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in S41[S41.analysis.str.startswith("K")].itertuples()}; N["comp_waic"] = S41[S41.analysis.str.startswith("K")].groupby("analysis").WAIC.first().to_dict()
    cv = rd("S5_covid.csv"); N["covid"] = {r.cov: (r.IRR, r.lo, r.hi, bool(r.cred)) for r in cv[cv.term == "var_x_post"].itertuples()}
    N["covid_post"] = cv[cv.term == "post_main"].iloc[0][["IRR", "lo", "hi"]].tolist()
    return N

if __name__ == "__main__":
    N = load()
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in N.items() if not isinstance(v, (dict, list, pd.DataFrame, tuple))})
    print("hot_by_sido", N["hot_by_sido"]); print("cold_by_sido", N["cold_by_sido"]); print("ehsa", N["ehsa"]); print("win_hot", N["win_hot"], "win_cold", N["win_cold"], "both", N["hot_all_windows"], N["cold_all_windows"], "rho", round(N["win_rr_rho"], 3))
    print("pos_y", {k: round(v, 2) for k, v in N["pos_y"].items()}); print("phi", N["phi"], "rr", N["rr_min"], N["rr_max"])
    print("KH WAIC", {k: v for k, v in N["s43_waic"].items() if "KH" in k}, "main", N["waic_main"]); print("ppc", N["ppc"]); print("dwaic", N["s50_region_dwaic"])
    print("T1", {k: (round(v["pos"], 3), round(v["sir_p10"], 3), round(v["sir_p90"], 3)) for k, v in N["T1"].items()}); print("covid", N["covid"], N["covid_post"])
    print("win_int", N["win_int"])
