# 88K_kidc_component_panel.py — 32호 KIDC: 시도·연도 eGFR<60 비율·요단백 +1 이상 비율을 시군구 행에 붙인 민감도 입력(2026-11-17).
#  입력 results_std3/S47_kidc_province.csv(88K_kidc_definition.py), panel_KIDC_std3.csv. 출력 results_std3/S41_panel_comp.csv(z 점수, 2015-2023 행 기준).
import os, pandas as pd
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); K = os.path.join(R, "04_분석", "KIDC"); RS = os.path.join(K, "results_std3")
import importlib.util; sp = importlib.util.spec_from_file_location("d", os.path.join(R, "01_스크립트", "88K_kidc_definition.py"))
key = {"서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시", "인천": "인천광역시", "광주": "광주광역시", "대전": "대전광역시", "울산": "울산광역시", "경기": "경기도", "강원": "강원특별자치도",
       "충청북": "충청북도", "충북": "충청북도", "충청남": "충청남도", "충남": "충청남도", "전라북": "전북특별자치도", "전북": "전북특별자치도", "전라남": "전라남도", "전남": "전라남도",
       "경상북": "경상북도", "경북": "경상북도", "경상남": "경상남도", "경남": "경상남도", "제주": "제주특별자치도", "세종": "세종특별자치시"}
sd = lambda r: next(key[k] for k in sorted(key, key=len, reverse=True) if r.startswith(k))
P = pd.read_csv(os.path.join(K, "panel_KIDC_std3.csv"), usecols=["year", "fbd_region"]); P["s"] = P.fbd_region.map(sd)
Z = pd.read_csv(os.path.join(RS, "S47_kidc_province.csv"))[["year", "sido", "egfr", "dip"]]
X = P.merge(Z, left_on=["year", "s"], right_on=["year", "sido"], how="left"); assert X[["egfr", "dip"]].notna().all().all(), X[X.egfr.isna()].head()
for c in ("egfr", "dip"): X[f"prov_{c}_z"] = (X[c] - X[c].mean()) / X[c].std()
X[["year", "fbd_region", "prov_egfr_z", "prov_dip_z"]].to_csv(os.path.join(RS, "S41_panel_comp.csv"), index=False, encoding="utf-8")
print(X[["prov_egfr_z", "prov_dip_z"]].corr().round(3), len(X))
