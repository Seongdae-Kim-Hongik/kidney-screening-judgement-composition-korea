#!/usr/bin/env python3
# 99N-prep(GPT 기준) — 다음 후보 10종 공간 선별 준비(2026-11-11). 99O_screen_osteo_prep_gpt.py 복제(대상만 교체), 원본 수정 없음.
#  공변량: 기준 SQLite disease_panel tag='PERIO' + 수급률 양쪽 규칙 정정(2021-23 < 0.2× 또는 > 5× (2020·2024 평균) → 결측, 지역 내 선형 보간).
#  그래프: 593쌍(nb_METS_std.graph). 강제통제 = 98 선별 규칙(std 모드에서 고령비 제외).
import os, json, shutil, sqlite3, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); AN = os.path.join(ROOT, "04_분석"); PAN = os.path.join(ROOT, "02_패널")
DB = os.environ["ST_REF_SQLITE"]   # reference district-year SQLite
NFC = lambda s: unicodedata.normalize("NFC", str(s))
c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
base = pd.read_sql("select * from disease_panel where tag='PERIO'", c).drop(columns=["tag"], errors="ignore"); base["fbd_region"] = base.fbd_region.map(NFC)
base = base.sort_values(["fbd_region", "year"]).reset_index(drop=True)
_ref = base[base.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate_raw.mean(); _r = base.fbd_region.map(_ref)
_bad = base.year.isin([2021, 2022, 2023]) & ((base.basic_livelihood_rate_raw < 0.2 * _r) | (base.basic_livelihood_rate_raw > 5 * _r))
print("[99N-prep] 수급률 위반 칸", int(_bad.sum()), base.loc[_bad, ["fbd_region", "year", "basic_livelihood_rate_raw"]].values.tolist())
base.loc[_bad, "basic_livelihood_rate_raw"] = np.nan
base["basic_livelihood_rate_raw"] = base.groupby("fbd_region").basic_livelihood_rate_raw.transform(lambda s: s.interpolate(method="linear", limit_area="inside"))
_s = base.basic_livelihood_rate_raw; base["basic_livelihood_rate"] = (_s - _s.mean()) / _s.std(ddof=0)
_r2 = base.fbd_region.map(base[base.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate_raw.mean()); _yy = base.year.isin([2021, 2022, 2023])
assert not (_yy & ((base.basic_livelihood_rate_raw < 0.2 * _r2) | (base.basic_livelihood_rate_raw > 5 * _r2))).any() and base.basic_livelihood_rate_raw.notna().all()
print("[99N-prep] 창원 정정 후", base.loc[base.fbd_region.eq(NFC("경상남도창원시")) & base.year.between(2020, 2024), ["year", "basic_livelihood_rate_raw"]].round(3).values.tolist())
cfg = json.loads(c.execute("select content from model_settings where tag='PERIO' and kind='config'").fetchone()[0])
cfg["forced"] = ["care_institutions_per_100k", "urban_population_share", "older_adult_share", "sex_ratio", "fiscal_independence"]
for T in ["KIDS", "ANEM", "LIVS", "TBS", "LIPSA", "LIPSB", "CHES", "LIPT", "RESP", "CIRC"]:
    X = pd.read_csv(os.path.join(PAN, f"{T}_Estd3n.csv"), encoding="utf-8-sig"); X["fbd_region"] = X.fbd_region.map(NFC); X = X[X.cases.notna()]
    D = os.path.join(AN, T); os.makedirs(os.path.join(D, "results"), exist_ok=True)
    P = base.drop(columns=["cases", "E", "E_crude", "SIR", "offset"], errors="ignore").merge(X[["year", "fbd_region", "offset", "cases", "E_crude"]], on=["year", "fbd_region"], how="inner", validate="one_to_one").rename(columns={"E_crude": "E"})
    P["cases"] = P.cases.astype(int); P["SIR"] = P.cases / P.E
    P.to_csv(os.path.join(D, f"panel_{T}.csv"), index=False, encoding="utf-8-sig")
    X[["year", "fbd_region", "E_std"]].to_csv(os.path.join(PAN, f"{T}_Estd.csv"), index=False, encoding="utf-8-sig")
    json.dump(cfg, open(os.path.join(D, f"config_{T}.json"), "w"), ensure_ascii=False, indent=1)
    shutil.copy2(os.path.join(AN, "METS_std", "results", "nb_METS_std.graph"), os.path.join(D, "results", f"nb_{T}.graph"))
    print(f"[99N-prep] {T}: 행 {len(P)}, {P.year.min()}-{P.year.max()}, 시군구 {P.fbd_region.nunique()}, cases {int(P.cases.sum()):,}")
