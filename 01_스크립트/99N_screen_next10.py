#!/usr/bin/env python3
# 99N — 다음 종속변수 후보 10종(11개 창) 공간 선별 지표·분류(2026-11-11; 99C_screen_cogn.py 복제, 지표·분류 규칙 98과 동일·결과 전 고정).
#  계수형 10개: SIR = Σcases/ΣE_std(성×연령 간접표준화). PHQ-9: 로짓 SR(직접표준화) 연도 평균, FH 강제통제 모형 phi.
#  순위 지속: 14년 = 2011-15 대 2020-24(98), 7년 = 앞 3년 대 뒤 3년(99C), PHQ-9 8년 = 2017-19 대 2022-24.
#  영과잉: 0칸 관측 수 대 음이항(연도 고정효과 + log E_std 오프셋) 기대 0칸 수.
#  산출: 04_분석/00_공간선별_다음후보10_261111.csv/.md
import os, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); AN = os.path.join(ROOT, "04_분석")
src = open(os.path.join(HERE, "98_screen_std.py"), encoding="utf-8").read(); src = src[:src.index("SCR = pd.read_csv")]
g = {"__file__": os.path.join(HERE, "98_screen_std.py")}; exec(compile(src, "98head", "exec"), g)
read_graph, clusters, moran, classify, failed = g["read_graph"], g["clusters"], g["moran"], g["classify"], g["failed"]
KO = {"KIDS": "검진 신장질환 의심", "ANEM": "검진 빈혈증 의심", "LIVS": "검진 간장질환 의심", "TBS": "검진 폐결핵 의심",
      "LIPSA": "검진 이상지질혈증 의심(주 2011-17)", "LIPSB": "검진 이상지질혈증 의심(보조 2018-24)", "CHES": "검진 기타흉부질환 의심",
      "LIPT": "검진 이상지질혈증 유질환자", "RESP": "호흡계통 질환 사망(J00-J98)", "CIRC": "순환계통 질환 사망(I00-I99)", "PHQ9": "KCHS 우울 증상 유병률(PHQ-9)"}
def zi_check(pan):
    import statsmodels.api as sm
    d = pan.dropna(subset=["cases"]).copy(); X = pd.get_dummies(d.year.astype(str), drop_first=False).astype(float)
    m = sm.NegativeBinomial(d.cases.values, X.values, offset=np.log(d.E_std.values)).fit(disp=0, maxiter=500)
    mu = np.exp(X.values @ m.params[:-1] + np.log(d.E_std.values)); a = m.params[-1]; p0 = (1 / (1 + a * mu)) ** (1 / a)
    return int((d.cases == 0).sum()), round(float(p0.sum()), 1), round(float(a), 3)
rows = []
for T in KO:
    D = os.path.join(AN, T); rng = np.random.default_rng(20261019)
    pan = pd.read_csv(f"{D}/panel_{T}.csv", encoding="utf-8-sig")
    yrs = sorted(pan.year.unique()); ny = len(yrs)
    if T == "PHQ9":
        pan["cases"] = pan.y_logit; pan["E_std"] = 1.0
    else:
        es = pd.read_csv(os.path.join(ROOT, "02_패널", f"{T}_Estd.csv"), encoding="utf-8-sig")
        pan = pan.merge(es, on=["year", "fbd_region"], how="left", validate="one_to_one"); assert pan.E_std.notna().all()
    nb = read_graph(f"{D}/results/nb_{T}.graph")
    rr = pd.read_csv(f"{D}/results_screen/forced_std_RR.csv"); hy = pd.read_csv(f"{D}/results_screen/forced_std_hyper.csv")
    agg = dict(pop=("population", "mean"), km2=("area_m2", lambda x: x.mean() / 1e6), urban=("urban_population_share_raw", "mean"))
    if T == "PHQ9": g0 = pan.groupby("fbd_region").agg(y=("y_logit", "mean"), SR=("SR", "mean"), **agg)
    else: g0 = pan.groupby("fbd_region").agg(cases=("cases", "sum"), E_std=("E_std", "sum"), **agg)
    g0 = rr[["area", "fbd_region"]].merge(g0, left_on="fbd_region", right_index=True, how="inner").sort_values("area").dropna(subset=["urban", "pop", "km2"])
    if T != "PHQ9": g0 = g0[g0.cases > 0]
    idx = {a: i for i, a in enumerate(g0.area.values)}; W = np.zeros((len(g0), len(g0)))
    for a, i in idx.items():
        nbs = [idx[b] for b in nb.get(a, []) if b in idx]
        if nbs: W[i, nbs] = 1 / len(nbs)
    dens = np.log(g0["pop"] / g0["km2"]).values; u = g0.urban.values; X = np.column_stack([np.ones(len(g0)), u, u ** 2, dens, dens ** 2])
    if T == "PHQ9": y = g0.y.values; lev = g0.SR.values
    else: lev = (g0.cases / g0.E_std).values; y = np.log(lev)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None); res = y - X @ beta; r2 = 1 - res.var() / y.var()
    I_raw, _ = moran(y, W, rng); I_ur, p_ur = moran(res, W, rng); ratio = float(np.percentile(lev, 90) / np.percentile(lev, 10))
    imin = []; iyr = {}
    for yr, d in pan.groupby("year"):
        d = d.set_index("fbd_region").reindex(g0.fbd_region)
        if T == "PHQ9": k = d.y_logit.notna().values; v = d.y_logit.values[k]
        else: k = d.cases.notna().values & (d.E_std > 0).values; v = np.log((d.cases.values[k] + 0.5) / d.E_std.values[k])
        Wk = W[np.ix_(k, k)].copy(); rs = Wk.sum(1); Wk[rs > 0] = Wk[rs > 0] / rs[rs > 0, None]
        iyr[yr] = moran(v, Wk)[0]; imin.append(iyr[yr])
    w = 5 if ny >= 14 else 3
    a1, a2 = pan[pan.year <= yrs[w - 1]], pan[pan.year >= yrs[-w]]
    if T == "PHQ9": s1 = a1.groupby("fbd_region").y_logit.mean(); s2 = a2.groupby("fbd_region").y_logit.mean()
    else:
        e1 = a1.groupby("fbd_region")[["cases", "E_std"]].sum(); e2 = a2.groupby("fbd_region")[["cases", "E_std"]].sum(); s1 = e1.cases / e1.E_std; s2 = e2.cases / e2.E_std
    cm = s1.index.intersection(s2.index); pers = float(spearmanr(s1[cm], s2[cm]).correlation)
    hot = rr.loc[rr["class"] == "hotspot", "area"].tolist(); cold = rr.loc[rr["class"] == "coldspot", "area"].tolist(); hc = clusters(hot, nb)
    ph = hy[hy.hyperpar.str.startswith("Phi")].iloc[0]; phi = float(ph["mean"]); rl = float(np.corrcoef(dens, y)[0, 1])
    big = rr.set_index("area").loc[hc[0], "fbd_region"].tolist() if hc else []
    zi = zi_check(pan) if T != "PHQ9" else (None, None, None)
    rows.append(dict(TAG=T, 질환=KO[T], 연도=f"{yrs[0]}-{yrs[-1]}", n_sgg=len(g0), 합계=int(pan.cases.sum()) if T != "PHQ9" else None, 연평균_칸당=round(pan.cases.mean(), 1) if T != "PHQ9" else None,
                     P90P10=round(ratio, 3), I_raw=round(I_raw, 3), I_min_year=round(min(imin), 3), I_max_year=round(max(imin), 3), 최소연도=int(min(iyr, key=iyr.get)),
                     persistence=round(pers, 3), R2_UR=round(r2, 3), I_UR=round(I_ur, 3), P_UR=p_ur, r_logdens=round(rl, 3),
                     phi=round(phi, 3), phi_lo=round(float(ph["X0.025quant"]), 2), phi_hi=round(float(ph["X0.975quant"]), 2),
                     hot=len(hot), cold=len(cold), largest_hot=len(hc[0]) if hc else 0, hot_core="; ".join(big[:8]),
                     zeros_obs=zi[0], zeros_NB=zi[1], NB_alpha=zi[2],
                     track=classify(I_raw, r2, I_ur, p_ur, phi, ratio), fail=failed(I_ur, p_ur, phi, ratio),
                     방향="도시 높음" if rl > 0.2 else "농촌 높음" if rl < -0.2 else "도농 차 작음"))
O = pd.DataFrame(rows); O.to_csv(os.path.join(AN, "00_공간선별_다음후보10_261111.csv"), index=False, encoding="utf-8-sig")
print(O[["TAG", "track", "I_raw", "I_UR", "I_min_year", "persistence", "phi", "P90P10", "R2_UR", "largest_hot", "fail", "zeros_obs", "zeros_NB", "방향"]].to_string())
for r in O.itertuples(): print(r.TAG, r.hot_core)
