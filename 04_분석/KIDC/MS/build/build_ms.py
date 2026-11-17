# build_ms.py — Journal of Nephrology(OUP, Editorial Manager) Original Article 원고 조립(2026-11-17, 32호 KIDC).
#  규정(OUP 저자 지침 2026-11-17 확인): 본문 ≤3,000단어, 구조 초록 150-250(Background/Methods/Results/Conclusions, 약어·인용 금지), 키워드 ≤4, 표+그림 ≤4, 참고 ≤30,
#  1단계 제목 Introduction·Methods·Results·Discussion·Ethical disclosure, 제목 ≤85자·약어 없음, 표지에 선언문, AMA 번호식(괄호), 영국식 철자, 표·그림 설명은 본문 끝, 그림마다 'Alt text:'.
#  보충 = Supplementary material(PDF). 사용: figs_kids.py → build_ms.py → esm_kids.py → cover_kids.py → sanitize → check_ms.py
import os, re, json
from docx.shared import Pt
from jkms_engine import JKMS
from british import brit
import content_kids as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_kids.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "01_manuscript_jn.md")
TITLE = C.TITLE
AUTHOR = "Seongdae Kim"; AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
EMAIL = "kimsd@hongik.ac.kr"; ORCID = "0000-0002-1525-0091"; PHONE = "+82-2-320-1114"
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
IRB = ("All procedures were in accordance with the ethical standards of the Institutional Review Board of Hongik University, which approved this study of published aggregate statistics "
       "(IRB approval number 7002340-202511-HR-012; continuing review 7002340-202611-HR-040), and with the 1964 Helsinki declaration and its later amendments.")
CONSENT = "The Institutional Review Board waived informed consent because only published aggregate statistics without individual identifiers were used."
COI = "None declared."
DATA = ("The source data are publicly available from the Korean Statistical Information Service (https://kosis.kr) and the other national statistics cited in the Methods. "
        f"The analysis code and the scripts that generate every number, table and figure are openly available on Zenodo (https://doi.org/{ZENODO}); "
        "the processed district-year data are available from the author on reasonable request.")
ACK = "None."
FUND = "None declared."
CREDIT = "S.K.: conceptualization, methodology, software, formal analysis, data curation, visualization, writing – original draft, writing – review and editing."
def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    src = "\n".join(t for _, t in C.METHODS + C.RESULTS) + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys()

KEEP = {"Korea", "Korean", "South", "United", "States", "US", "USA", "UK", "Japan", "Europe", "European", "Asia", "Asian", "Lancet", "Bayesian", "Laplace", "Gaussian",
        "Besag", "York", "Mollié", "Knorr-Held", "INLA", "BYM2", "STROBE", "GBD", "NHIS", "Global", "Burden", "Disease", "KDIGO", "CKD", "eGFR", "GFR", "National", "Health", "Insurance", "Service",
        "Korea's", "France"}
TFIX = {"shlipak2021case": "The case for early identification and intervention of chronic kidney disease: conclusions from a Kidney Disease: Improving Global Outcomes (KDIGO) Controversies Conference",
        "bae2022effects": "Effects of blood pressure according to age on end-stage renal disease development in patients with diabetes: a nationwide population-based cohort study",
        "kim2025burden": "Burden of end-stage kidney disease by type 2 diabetes mellitus status in South Korea: a nationwide epidemiologic study",
        "seong2017data": "Data resource profile: the National Health Information Database of the National Health Insurance Service in South Korea",
        "jung2026kidney": "Kidney-related screening indicator trends in Korea: 2010-2024 (eGFR, 2012-2024) and 2025-2028 forecasts using National Health Insurance Service health screening data",
        "shin2021albuminuria": "Albuminuria testing in hypertension and diabetes: an individual-participant data meta-analysis in a global consortium",
        "chang2020association": "Association between income disparities and risk of chronic kidney disease: a nationwide cohort study of seven million adults in Korea",
        "delanaye2019ckd": "CKD: a call for an age-adapted definition",
        "pinsky2007evidence": "Evidence of a healthy volunteer effect in the Prostate, Lung, Colorectal, and Ovarian Cancer Screening Trial"}
def sent(t):   # 문장형 제목(첫 단어·고유명사·약어 유지)
    w = t.split(" "); caps = sum(1 for x in w[1:] if x[:1].isupper())
    if len(w) < 4 or caps < 0.5 * (len(w) - 1): return t
    out = [w[0]]
    for x in w[1:]:
        core = x.strip("(),:;.?")
        keep = core in KEEP or core.isupper() or any(c.isdigit() for c in core) or out[-1].endswith((":", "?")) or (core.split("-")[0] in KEEP)
        if not keep: x = x[:1].lower() + x[1:]
        out.append(x)
    return " ".join(out)
def prange(p):   # AMA: 쪽 범위는 줄이지 않고 하이픈(2461-2482)
    return str(p).replace("–", "-")
def ref(k):   # AMA: Smith JJ. Title. Am J Sci. 1999;36(2):234-235. doi: 저자 6명 초과 시 3명 + et al.
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. {r['url']}. Accessed {r['accessed']}"
    if r["type"] == "report": return f"{r['authors']}. {r['title']}. {r['publisher']}; {r['year']}"
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al."
    t = TFIX.get(k) or sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a.replace('et al..', 'et al.')}{'' if a.endswith('.') else '.'} {t} {r['journal']}. {r['year']}"
    if r.get("vol"): s += f";{r['vol']}"
    if r.get("issue") and r.get("vol"): s += f"({r['issue']})"
    if r.get("pages"): s += f":{prange(r['pages'])}"
    s = s.replace(". .", ".").rstrip(".") + "."
    if r.get("doi"): s += f" doi:{r['doi']}"
    return s

class TX(JKMS):
    raw = False
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw:
            text = brit(text); text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

def foot_row(J, text, sz=9, ls=15):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(brit(t[0]), [brit(x) for x in t[1]], [[brit(x) for x in r] for r in t[2]], "", fs_max=fs, title_bold=True); foot_row(J, t[3], 8); J.counting = c

from tables_kids import TAB1_COV, GROUPS, LABEL, table1, table2
FIGCAP = {
 1: ("Geography and composition of suspected kidney disease judgements at general health screening, Korea. (A) Residual spatial rate ratio (RR) by district for 2015–2023, the posterior mean of the exponentiated Besag–York–Mollié 2 district effect from the principal model. Solid outlines, hot spots (posterior probability of a residual spatial RR above 1 greater than 0.95); dashed outlines, cold spots (less than 0.05); thick lines, province boundaries; grey, district without separate results. Boundaries are the 2024 administrative districts drawn from the national boundary file. (B) National shares of examinees judged to have suspected kidney disease, with an estimated glomerular filtration rate (eGFR) below 60 mL/min/1.73 m² and with dipstick proteinuria of 1+ or more, 2012–2024; shading marks the analysed years",
     "Alt text: Panel A is a map of Korean districts shaded from blue to red by residual rate ratio, with outlined hot spots and cold spots. Panel B is a line chart of three national percentages from 2012 to 2024: the kidney judgement rises from about 3.5% to 5.7%, the share with low eGFR declines slightly from about 4.1% to 3.4%, and dipstick proteinuria rises from about 2.2% to 3.7%."),
 2: ("Rate ratios per 1 standard deviation with 95% credible intervals for the three subset-stable district characteristics and the three physical activity characteristics across models: the principal model, models with Knorr-Held type II and type IV space–time interactions, the principal model with provincial eGFR and proteinuria shares added, the principal model fitted to 2015–2018 and to 2019–2023 only, and the principal model with expected numbers computed from the resident population",
     "Alt text: Forest plot of rate ratios across seven models. The treated hypertension and diabetes share, suspected hypertension and suspected diabetes lie above 1 in every model; walking, moderate or vigorous activity and public sports facilities have intervals that include 1."),
}
SUPM = "Supplementary material (Supplementary_material.pdf): Table S1, composition of the judgement; Table S2, supplementary methods; Table S3, covariates; Table S4, panel checks; Table S5, robustness, comparison outcomes, negative controls and model checks; Figure S1, persistence of the district pattern; Table S6, calendar windows; Table S7, STROBE checklist"

def build(words=None):
    D = read_draft(); J = TX(cite="paren")
    J.para(f"<b>{brit(TITLE)}</b>")
    J.para("Type of manuscript: Original Article", before=6)
    J.para(f"{AUTHOR}, PhD", before=12); J.para(AFFIL)
    J.para(f"Corresponding author: {AUTHOR}, PhD, {ADDRESS}. Telephone: {PHONE}. Fax: not available. Email: {EMAIL}. ORCID: {ORCID}", before=12)
    J.para(f"Word count (main text): {words if words else '[WORDS]'}. Tables: 2. Figures: 2. Supplementary material: 1 file", before=12)
    J.para(f"<b>Data availability</b> {DATA}", before=12)
    J.para(f"<b>Conflicts of interest</b> {COI}")
    J.para(f"<b>Author contributions (CRediT)</b> {CREDIT}")
    J.para(f"<b>Funding</b> {FUND}")
    J.para(f"<b>Acknowledgements</b> {ACK}")
    J.para(f"<b>Ethical approval</b> {IRB}")
    J.para(f"<b>Patient consent</b> {CONSENT}")
    J.page_break()
    J.head("Abstract", 1)
    for p in D["Abstract"]:
        m = re.match(r"^(Background|Methods|Results|Conclusions):\s*(.*)$", p, re.S); J.para(f"<b>{m.group(1)}</b> {m.group(2)}")
    J.para(f"<b>Keywords</b> {C.KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("Methods", 1)
    for h, p in C.METHODS: J.head(h, 2); J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for h, p in C.RESULTS: J.head(h, 2); J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    J.head("Ethical disclosure", 1)
    J.para(f"{IRB} {CONSENT}")
    J.head("Conflicts of interest", 1); J.para(COI)
    J.head("Funding", 1); J.para(FUND)
    J.head("Data availability", 1); J.para(DATA)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s_ = f"{i}. " + ref(k); rl.append(s_); J.para(s_)
    J.raw = False
    J.page_break(); put_table(J, table1()); J.new_page("landscape"); put_table(J, table2(), fs=9)
    J.new_page("portrait"); J.head("Figure legends", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Figure {k}.</b> {FIGCAP[k][0]}."); J.para(FIGCAP[k][1])
    J.head("Supplementary material", 1); J.para(SUPM)
    return J, rl, D
def count_words(path):   # 본문 = Introduction ~ Discussion 끝(Ethical disclosure 앞)
    from docx import Document
    ps = [p.text for p in Document(path).paragraphs]; t = "\n".join(ps)
    a = t.find("\nIntroduction\n"); body = len(t[a:t.find("\nEthical disclosure\n", a)].split())
    i0 = ps.index("Abstract"); i1 = next(i for i, p in enumerate(ps) if p.startswith("Keywords"))
    ab = len(" ".join(ps[i0 + 1:i1]).split())
    return body, ab
if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript.docx")
    J, rl, D = build(); J.save(p); bw, aw = count_words(p)
    J, rl, D = build(f"{bw:,}"); J.doc_title = "Manuscript"; J.save(p); bw2, aw2 = count_words(p); assert bw2 == bw
    open(os.path.join(OUT, "wordcount.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\ntitle_chars={len(TITLE)}\n")
    print(f"body {bw} (limit 3000) | abstract {aw} (150-250) | refs {len(KEYS)} (limit 30) | title chars {len(TITLE)}")
