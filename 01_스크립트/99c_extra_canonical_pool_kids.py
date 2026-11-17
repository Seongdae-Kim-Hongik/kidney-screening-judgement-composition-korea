#!/usr/bin/env python3
# 99c — 32호 KIDS(검진 신장질환 의심) 가설 풀 추가 열(2026-11-11, 99c_extra_canonical_pool_undx.py 복제, 수급률 정정만 양쪽 규칙으로 바꿈). 결합 규칙(코드표, 이름 결합 금지, 군위군 37310 별칭)은 99c_perio와 같다.
#  정본 통합자료(통합자료_261030/01_공변량_229x2011_2024.csv)
#   im_specialists_per100k = 내과 전문의 ÷ 정본 인구 × 10만 — 가능 요인(공급)
#   basic_livelihood_rate  = 국민기초생활보장 수급자 비율(%) — 소인(박탈). 2021-23 일반구 시 붕괴 칸 + 창원 2021-23(부풀림) 정정(19호 규칙, 33칸)
#   tertiary_educated_share= 대졸 이상 비율(%) — 소인(교육; 인구총조사 사이 보간·2020 이후 고정)
#   unmet_need_rate        = KCHS 연간 미충족의료율(병의원) SR, 2011-18 DT_NECE_NOTTREAT + 2019-24 DT_117075_NECE_NTR02 이어 붙임(표 교체, 지표명 동일)
#  산출: 02_패널/EXT_canonical_pool_KIDS_261111.csv
import os, unicodedata
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, ".."))
ZD = os.environ.get("ST_CANON", os.path.join(os.path.expandvars("$ST_DATA_ROOT"), "기타/R_Studio/FBD_DATA_ZIP/통합자료_261030"))
PAN = os.path.join(ROOT, "02_패널")
C = pd.read_csv(os.path.join(ZD, "01_공변량_229x2011_2024.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str})
K = pd.read_csv(os.path.join(ZD, "00_시군구_229_대응표.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str}); assert K.sigungu_cd.is_unique and len(K) == 229
K.loc[K.sigungu_cd == "37310", "region"] = "대구시군위군"
C = C.drop(columns=["region"]).merge(K[["sigungu_cd", "region"]], on="sigungu_cd", how="left", validate="many_to_one"); assert C.region.notna().all()
out = pd.DataFrame({"year": C.year, "fbd_region": C.region.map(NFC),
                    "im_specialists_per100k": C.internal_medicine_specialists.astype(float) / C["pop"].astype(float) * 1e5,
                    "basic_livelihood_rate": C.basic_livelihood_recipient_rate.astype(float),
                    "tertiary_educated_share": C.tertiary_educated_share.astype(float)})
out = out[(out.year >= 2011) & (out.year <= 2024)].sort_values(["fbd_region", "year"]).copy()
ref = out[out.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean()
yy = out.year.isin([2021, 2022, 2023])
bad = yy & ((out.basic_livelihood_rate < 0.2 * out.fbd_region.map(ref)) | (out.basic_livelihood_rate > 5 * out.fbd_region.map(ref)))   # 양쪽 규칙(11/11, 00_INDEX 맨 위 절): 20% 미만 또는 5배 초과
print("[99c-kids] 수급률 결함 칸", int(bad.sum()), sorted(out.loc[bad, "fbd_region"].unique()))
assert bad.sum() == 33 and out.loc[bad, "fbd_region"].nunique() == 11 and bad[out.fbd_region == NFC("경상남도창원시")].sum() == 3
out.loc[bad, "basic_livelihood_rate"] = np.nan
# 내과 전문의 0값 13칸(신안·영양·울릉·산청·군위)은 1명↔0명 소규모 군의 실제 값으로 보고 유지(이웃 연도도 1~2명 수준) → 80에서 log1p 변환
print("[99c-kids] 내과 전문의 0값 칸(유지)", int((out.im_specialists_per100k <= 0).sum()))
# KCHS 연간 미충족의료율(병의원): 2011-18 표 DT_NECE_NOTTREAT, 2019-24 표 DT_117075_NECE_NTR02(같은 지표명, 표 교체) → 이어 붙임(마스터 열, 시군구 코드 결합은 마스터가 이미 함)
M = pd.read_parquet(os.path.join(PAN, "MASTER_시군구_연도_wide.parquet")); M.columns = [NFC(c) for c in M.columns]; M["fbd_region"] = M.fbd_region.map(NFC)
a, b = "kchs__DT_NECE_NOTTREAT__SR", "kchs__DT_117075_NECE_NTR02__SR"
assert M.loc[M.year.between(2019, 2024), a].isna().all() and M.loc[M.year.between(2011, 2018), b].isna().all()
M["unmet_need_rate"] = M[a].where(M.year <= 2018, M[b])
out = out.merge(M[["year", "fbd_region", "unmet_need_rate"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
print("[99c-kids] 미충족의료율 이어 붙임 결측", int(out.unmet_need_rate.isna().sum()), sorted(out.loc[out.unmet_need_rate.isna(), "fbd_region"].unique()))
for c in ["im_specialists_per100k", "basic_livelihood_rate", "tertiary_educated_share", "unmet_need_rate"]:
    out[c] = out.groupby("fbd_region")[c].transform(lambda s: s.interpolate(method="linear", limit_area="inside"))
    out[c] = out[c].fillna(out.groupby("fbd_region")[c].transform("mean"))
    nb = out.groupby("fbd_region")[c].transform(lambda s: (s.shift(1) + s.shift(-1)) / 2)
    lo = (out[c] < 0.2 * nb).sum(); hi = (out[c] > 5 * nb).sum()
    print(f"[99c-kids] 게이트 {c}: 이웃 평균 20% 미만 {int(lo)}칸, 5배 초과 {int(hi)}칸, 0값 {int((out[c] == 0).sum())}칸")
assert out.groupby("fbd_region").year.nunique().eq(14).all() and out.fbd_region.nunique() == 229 and not out.duplicated(["year", "fbd_region"]).any()
assert out.notna().all().all(), out.isna().sum()
fp = os.path.join(PAN, "EXT_canonical_pool_KIDS_261111.csv"); out.to_csv(fp, index=False, encoding="utf-8-sig")
print(f"[99c-kids] 저장 {fp} {out.shape}"); print(out.describe().T[["min", "50%", "max"]].round(2))
# (32호 추가, 적합 전 고정) 치료 중 심대사 부담 = 검진 고혈압 유질환자 비율 + 당뇨 유질환자 비율(25호 EXT_undx_dxshare_261110.csv 읽기만).
#  두 비율 시군구-연도 상관 0.947(VIF 16·18) → 한 변수로 합침(한 사람이 둘 다면 두 번 세는 부담 지수). 합친 뒤 VIF 7.3.
DX = pd.read_csv(os.path.join(PAN, "EXT_undx_dxshare_261110.csv"), encoding="utf-8-sig"); DX["fbd_region"] = DX.fbd_region.map(NFC)
DX["dx_cardiometabolic_share"] = DX.dx_htn_share + DX.dx_dm_share
fp3 = os.path.join(PAN, "EXT_kids_dxburden_261111.csv"); DX[["year", "fbd_region", "dx_cardiometabolic_share"]].to_csv(fp3, index=False, encoding="utf-8-sig")
print(f"[99c-kids] 저장 {fp3}, 상관(htn,dm) {DX.dx_htn_share.corr(DX.dx_dm_share):.3f}, 결측 {int(DX.dx_cardiometabolic_share.isna().sum())}")
