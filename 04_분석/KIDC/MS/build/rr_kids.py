# rr_kids.py — KIDC 개정판(2026-11-19) 추가 수치: 판정 기준 원문·성·연령 대조(88R)·표준화 불확실성(99K3+88g GROUP 7). 손입력 금지.
import os, glob, json, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3"); RR = os.path.join(B, "JN_RR_261119")
from numbers_kids import ROB, DX, HTN, DM
def load():
    R = {}
    S = json.load(open(os.path.join(RR, "R1_reconcile_summary.json"))); R["S"] = S
    R["nat"] = {int(k): v for k, v in S["national"].items()}; R["ds"] = {int(k): v for k, v in S["direct_std_2019"].items()}
    A = pd.read_csv(os.path.join(RR, "R1_ageband_reconcile.csv")); R["ab"] = A
    q = A[A.year.between(2015, 2023)].copy(); q["J"] = q.j * q.exam; q["Aa"] = q.a * q.exam; q["Bb"] = q.b * q.exam
    g = q.groupby(["sex", "ageband"])[["J", "Aa", "Bb", "exam"]].sum(); g["j_b"] = g.J / g.Bb; g["j_a"] = g.J / g.Aa
    g["j"] = 100 * g.J / g.exam; g["a"] = 100 * g.Aa / g.exam; g["b"] = 100 * g.Bb / g.exam; R["pool"] = g
    R["y2039"] = A[A.year.between(2015, 2023) & (A.ageband == "20-39")].pivot(index="year", columns="sex", values="j_over_b")
    R["o70"] = A[A.year.between(2015, 2023) & (A.ageband == "70+")].pivot(index="year", columns="sex", values="j_over_a")
    AS = pd.read_csv(os.path.join(RR, "R1_age_sex_reconcile.csv")); R["as"] = AS
    # 표준화 불확실성
    U = []
    for f in sorted(glob.glob(os.path.join(RS, "S41_part_U1_*.csv"))):
        d = pd.read_csv(f); U.append(d)
    U = pd.concat(U); U["scen"] = U.analysis.str.replace("U1_E_", "", regex=False); R["U"] = U
    mc = U[U.scen.str.startswith("mc")]; R["n_mc"] = mc.scen.nunique()
    R["mc"] = {v: dict(med=float(mc[mc["cov"] == v].IRR.median()), lo=float(mc[mc["cov"] == v].IRR.min()), hi=float(mc[mc["cov"] == v].IRR.max()),
                       ncred=int(((mc["cov"] == v) & mc.cred & (mc.IRR > 1)).sum()), lomin=float(mc[mc["cov"] == v].lo.min())) for v in ROB}
    R["tilt"] = {(s, v): tuple(U[(U.scen == s) & (U["cov"] == v)][["IRR", "lo", "hi", "cred"]].iloc[0]) for s in U.scen.unique() if s.startswith("tilt") for v in ROB}
    R["mc_hotJ"] = (float(mc.drop_duplicates("scen").hot_jaccard_vs_main.min()), float(mc.drop_duplicates("scen").hot_jaccard_vs_main.median()))
    CB = pd.read_csv(os.path.join(RR, "R1_creatinine_reconcile.csv")); R["cb"] = CB
    R["cbp"] = CB.groupby(["sex", "ageband"])[["j", "a", "b", "c_lo", "c_hi"]].mean() * 100
    R["eunc_sd"] = None
    return R
if __name__ == "__main__":
    R = load(); print(R["pool"].round(3)); print(R["mc"]); print({k: v for k, v in R["tilt"].items()}); print(R["mc_hotJ"], R["n_mc"])
