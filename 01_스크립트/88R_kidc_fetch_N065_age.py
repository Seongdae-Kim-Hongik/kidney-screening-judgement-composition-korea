# 88R_kidc_fetch_N065_age.py — KIDC 개정판(2026-11-19): KOSIS 연령별·성별 요단백 분포(N065) 전체 차원 재수집
import os, json, urllib.request, urllib.parse
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(R, "00_원천", "C_NHIS_검진보험", "KOSIS_JN_RR_261119"); os.makedirs(OUT, exist_ok=True)
K = open(os.path.expanduser("~/.kosis_key")).read().strip()
for t in ["DT_35007_N065", "DT_35007_N129", "DT_35007_N079"]:
    p = os.path.join(OUT, t + "_age_sex.json")
    if os.path.exists(p): continue
    out = []
    for y in range(2012, 2025):
        u = "https://kosis.kr/openapi/Param/statisticsParameterData.do?" + urllib.parse.urlencode(dict(method="getList", apiKey=K, orgId="350", tblId=t, itmId="ALL", objL1="ALL", objL2="ALL", objL3="ALL", format="json", jsonVD="Y", prdSe="Y", startPrdDe=str(y), endPrdDe=str(y)))
        d = json.loads(urllib.request.urlopen(u, timeout=120).read().decode()); out += d if isinstance(d, list) else []; print(t, y, len(d) if isinstance(d, list) else d)
    json.dump(out, open(p, "w"), ensure_ascii=False)
