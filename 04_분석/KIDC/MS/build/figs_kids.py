# -*- coding: utf-8 -*-
# figs_kids.py — 32호 KIDC 그림(2026-11-17).
#  규칙: 컬러, 패널 문자 모두 같은 크기·11/10 기준 2배(48pt)·굵게, 방위표 3배, 그림 안 설명문 금지, 결합은 시군구 코드로만.
#  패널 문자: OUP 지침 원문 'labelled with a letter (A, B, C, D, etc.) in the upper-left corner' → 대문자, 크기는 11/10 규칙(2배·모두 같은 크기). 그림 파일 = TIFF 600 dpi(업로드), PDF 함께.
#  Fig 1 (A) 2015-2023 잔차 공간 RR (B) 전국 판정·eGFR<60·요단백 1+ 비율 2012-2024 · Fig 2 강건 3개+신체활동 3개 변수의 모형별 RR · 보충 Fig S1 (A) EHSA (B) 두 창 핫·콜드스팟
import os, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_kids import load, ROB, SHP, HTN, DM, BLR, PA, DX
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3")
FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
MM = 1 / 25.4; W = 174 * MM; DPI = 600; LW = 0.3; PANEL_LABEL_PT = 48
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "legend.fontsize": 7.5, "legend.title_fontsize": 8, "axes.linewidth": 0.5, "pdf.fonttype": 42})
NFC = lambda s: unicodedata.normalize("NFC", str(s)).strip()
N = load()
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
rd = lambda f: pd.read_csv(os.path.join(RS, f), encoding="utf-8-sig", dtype={"sigungu_cd": str})
def letter(fig, ch, x, y):   # 그림 좌표 하나의 상수 크기
    fig.text(x, y, ch, fontsize=PANEL_LABEL_PT, fontweight="bold", va="top", ha="left")
def mapax(ax):
    ax.set_rasterization_zorder(2.5)   # 지도 다각형만 래스터(600 dpi), 글자·범례는 벡터 — 업로드 10 MB 미만
    SIDO.boundary.plot(ax=ax, color="#404040", linewidth=0.45); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0
    bx, by = x0 + 0.60 * W_, y0 + 0.03 * H_
    ax.plot([bx, bx + 100000], [by, by], color="black", lw=1.2, solid_capstyle="butt"); ax.text(bx + 50000, by + 0.012 * H_, "100 km", ha="center", va="bottom", fontsize=7)
    ax.annotate("N", xy=(x0 + 0.93 * W_, y0 + 0.99 * H_), xytext=(x0 + 0.93 * W_, y0 + 0.80 * H_), ha="center", va="center", fontsize=24, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>,head_length=0.9,head_width=0.45", color="black", lw=2.4))
def save(fig, k):
    p = os.path.join(FIG, f"KIDC_Fig{k}.png"); fig.savefig(p, dpi=DPI, facecolor="white")
    if not str(k).startswith("S"): fig.savefig(os.path.join(OUTF, f"Fig{k}.pdf"), facecolor="white", dpi=DPI)
    plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(DPI, DPI))
    if not str(k).startswith("S"): im.save(os.path.join(OUTF, f"Fig{k}.tif"), dpi=(DPI, DPI), compression="tiff_lzw")
    return im.size

S6 = rd("S6_spatial_RR.csv"); assert len(S6) == 229
# Fig 1
BR = [0, 0.8, 0.9, 0.95, 1, 1.05, 1.1, 1.25, 99]; LB = ["<0.80", "0.80-0.89", "0.90-0.94", "0.95-0.99", "1.00-1.04", "1.05-1.09", "1.10-1.24", "≥1.25"]
PAL = ["#2166AC", "#4393C3", "#92C5DE", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
assert BR[0] < N["rr_min"] < BR[2] and N["rr_max"] < 2
fig = plt.figure(figsize=(W, 4.7)); a0 = fig.add_axes([0.00, 0.27, 0.49, 0.62]); a1 = fig.add_axes([0.62, 0.36, 0.36, 0.50])
d = S6.set_index("sigungu_cd"); gg = G.copy(); gg["v"] = gg.cd.map(d.RR); gg["c"] = gg.cd.map(d["class"]); assert gg.v.notna().all()
gg[gg.c != "unobserved"].plot(ax=a0, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#a0a0a0", linewidth=LW); gg[gg.c == "unobserved"].plot(ax=a0, color="#bdbdbd", edgecolor="#a0a0a0", linewidth=LW); mapax(a0)
assert int((gg.c == "unobserved").sum()) == 1
gg[gg.c == "coldspot"].boundary.plot(ax=a0, color="#2171B5", linewidth=0.6, linestyle=(0, (2.0, 1.2))); gg[gg.c == "hotspot"].boundary.plot(ax=a0, color="black", linewidth=0.6)
h = [Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL, LB)] + [Patch(facecolor="none", edgecolor="black", linewidth=0.8, label="Hot spot"), Patch(facecolor="none", edgecolor="#2171B5", linewidth=0.8, linestyle="--", label="Cold spot"), Patch(facecolor="#bdbdbd", edgecolor="#777777", linewidth=LW, label="Not observed")]
a0.legend(handles=h, title="Residual spatial RR, 2015-2023", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, columnspacing=0.8, handlelength=1.3)
NT = N["defn"]["national"]; yy = sorted(int(y) for y in NT)
SER = [("pct_suspected", "Suspected kidney disease (judgement)", "#B2182B", "o", "-"), ("pct_egfr_lt60", "eGFR below 60 mL/min/1.73 m²", "#2166AC", "s", "--"), ("pct_dip_1plus", "Dipstick proteinuria 1+ or more", "#1b7837", "^", ":")]
a1.axvspan(2014.5, 2023.5, color="#f0f0f0", zorder=0)
for k_, lab, col, mk, ls in SER: a1.plot(yy, [NT[y][k_] if y in NT else NT[str(y)][k_] for y in yy], color=col, marker=mk, ms=3.0, lw=1.0, ls=ls, label=lab)
a1.set_xlim(2011.5, 2024.5); a1.set_ylim(0, 6.5); a1.set_xticks([2012, 2015, 2018, 2021, 2024])
a1.set_ylabel("Share of examinees (%)"); a1.set_xlabel("Year"); a1.spines[["top", "right"]].set_visible(False)
a1.legend(loc="upper center", bbox_to_anchor=(0.45, -0.25), ncol=1, frameon=False)
letter(fig, "A", 0.005, 0.995); letter(fig, "B", 0.515, 0.995)
s1 = save(fig, 1)

# Fig 2 — 강건 3개 + 신체활동 3개 변수의 모형별 RR
LAB = {DX: "Treated hypertension\nor diabetes", HTN: "Suspected hypertension\nat screening", DM: "Suspected diabetes\nat screening", PA[0]: "Walking", PA[1]: "Moderate-or-vigorous\nphysical activity", PA[2]: "Public sports facilities\nper population"}
ORD = [DX, HTN, DM] + PA; assert set(ROB) <= set(ORD)
MOD = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"]), "#000000", "o"),
       ("Knorr-Held type II", lambda v: N["s43"][("KH_typeII", v)][:3], "#2166AC", "s"),
       ("Knorr-Held type IV", lambda v: N["s43"][("KH_typeIV", v)][:3], "#B2182B", "D"),
       ("Provincial eGFR and proteinuria added", lambda v: N["comp"][("K1_prov_components", v)][:3], "#762a83", "X"),
       ("2015-2018 only", lambda v: N["win_irr"][(v, "W1_2015-18")][:3], "#1b7837", "v"),
       ("2019-2023 only", lambda v: N["win_irr"][(v, "W2_2019-23")][:3], "#E08214", "P"),
       ("Expected cases from residents", lambda v: N["epop"][v][:3], "#7f7f7f", "^")]
lo_all = min(f(v)[1] for v in ORD for _, f, _, _ in MOD); hi_all = max(f(v)[2] for v in ORD for _, f, _, _ in MOD)
fig, ax = plt.subplots(figsize=(W, 4.4)); fig.subplots_adjust(left=0.25, right=0.98, top=0.97, bottom=0.26)
off = np.linspace(-0.34, 0.34, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, col, mk), o in zip(MOD, off):
        e, lo, hi = f(v); ax.plot([lo, hi], [i + o] * 2, color=col, lw=0.8); ax.plot(e, i + o, marker=mk, color=col, ms=3.4, mew=0, ls="none")
ax.axhline(2.5, color="#bdbdbd", lw=0.5)
ax.axvline(1, color="#404040", lw=0.5, ls=":"); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
xt = [0.95, 1.00, 1.05, 1.10, 1.15, 1.20]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Rate ratio per 1 SD (95% credible interval)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=c, marker=m, lw=0.8, ms=3.4, mew=0, label=l) for l, _, c, m in MOD], loc="upper center", bbox_to_anchor=(0.36, -0.13), ncol=4, frameon=False)
s2 = save(fig, 2)

# 보충 Fig S1
EH = rd("S11_ehsa.csv")
CATS = [f"{a} {b}" for b in ("hot", "cold") for a in ("New", "Consecutive", "Intensifying", "Persistent", "Diminishing", "Sporadic", "Oscillating", "Historical")] + ["No pattern"]
EPAL = {"New hot": "#fdd0a2", "Consecutive hot": "#fdae6b", "Intensifying hot": "#a50f15", "Persistent hot": "#de2d26", "Diminishing hot": "#fc9272", "Sporadic hot": "#fee0d2", "Oscillating hot": "#d6a5c9", "Historical hot": "#bcbddc",
        "New cold": "#c6dbef", "Consecutive cold": "#9ecae1", "Intensifying cold": "#08519c", "Persistent cold": "#3182bd", "Diminishing cold": "#6baed6", "Sporadic cold": "#deebf7", "Oscillating cold": "#a1d99b", "Historical cold": "#c7e9c0", "No pattern": "#f7f7f7", "Not observed": "#bdbdbd"}
WM = rd("S4b_window_spatialRR.csv")
nh = WM[WM["class"] == "hotspot"].groupby("sigungu_cd").size(); nc = WM[WM["class"] == "coldspot"].groupby("sigungu_cd").size()
assert int((nh == 2).sum()) == N["hot_all_windows"] and int((nc == 2).sum()) == N["cold_all_windows"]
fig = plt.figure(figsize=(W, 5.0)); a0 = fig.add_axes([0.00, 0.30, 0.49, 0.60]); a1 = fig.add_axes([0.51, 0.30, 0.49, 0.60])
gg = G.copy(); gg["c"] = gg.cd.map(EH.set_index("sigungu_cd").EHSA); assert int(gg.c.isna().sum()) == 1; NOOBS = gg.c.isna(); gg["c"] = gg.c.fillna("Not observed")
gg.plot(ax=a0, color=[EPAL[c] for c in gg.c], edgecolor="#a0a0a0", linewidth=LW); mapax(a0)
cnt = gg.c.value_counts(); pres = [c for c in CATS + ["Not observed"] if c in cnt.index]
a0.legend(handles=[Patch(facecolor=EPAL[c], edgecolor="#777777", linewidth=LW, label=f"{c} ({cnt[c]})") for c in pres], title="Category (districts)", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
hh = gg.cd.map(nh).fillna(0).astype(int); cc = gg.cd.map(nc).fillna(0).astype(int)
gg["k"] = np.where((hh > 0) & (cc > 0), 9, hh - cc); gg.loc[NOOBS, "k"] = 8
KP = {-2: "#2166AC", -1: "#92C5DE", 0: "#f7f7f7", 1: "#F4A582", 2: "#B2182B", 9: "#c2a5cf", 8: "#bdbdbd"}
KL = {-2: "Cold spot in both windows", -1: "Cold spot in one", 0: "Neither", 1: "Hot spot in one", 2: "Hot spot in both windows", 9: "Hot or cold by window", 8: "Not observed"}
gg.plot(ax=a1, color=[KP[k] for k in gg.k], edgecolor="#a0a0a0", linewidth=LW); mapax(a1)
kc = gg.k.value_counts()
a1.legend(handles=[Patch(facecolor=KP[k], edgecolor="#777777", linewidth=LW, label=f"{KL[k]} ({kc.get(k, 0)})") for k in (2, 1, 0, -1, -2, 9, 8) if kc.get(k, 0)], title="Windows 2015-2018 and 2019-2023", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
letter(fig, "A", 0.005, 0.995); letter(fig, "B", 0.515, 0.995)
s3 = save(fig, "S1")
for k, s in zip((1, 2, "S1"), (s1, s2, s3)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/DPI*25.4:.0f} x {s[1]/DPI*25.4:.0f} mm")
