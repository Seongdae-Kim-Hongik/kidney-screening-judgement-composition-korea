# check_ms.py — 32호 KIDC Journal of Nephrology 원고 검사기(2026-11-17). 규정 한도 > 플레이북(3선 표·네모·지문) > 문체·수치. sanitize 뒤 실행. FAIL 0이면 PASS.
import os, re, subprocess, zipfile, sys
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
import content_kids as C
from build_ms import read_draft, TITLE, KEYS, FIGCAP, IRB, CONSENT, COI, ORCID
AI = "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript."
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out"); R = []
PREV = ["Is suspected kidney disease at health screening judged more often where blood pressure and glucose are high? Thirteen years of Korean district data", "Suspected kidney disease at health screening tracks high blood pressure and glucose across Korean districts"]
def ok(c, m): R.append(("ok  " if c else "FAIL") + " " + m)
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount.txt")).read().split())
D = read_draft(); AB = D["Abstract"]; ab = " ".join(AB)
MSF, SUPF, CLF = "Manuscript.docx", "Supplementary_material.docx", "Cover_Letter.docx"
for f in (MSF, SUPF, "Supplementary_material.pdf", CLF, "Cover_Letter.pdf", "Figures/Fig1.tif", "Figures/Fig2.tif", "ICMJE_Disclosure_Form.pdf"): ok(os.path.exists(os.path.join(OUT, f)), f"파일 {f}")
# 1. J Nephrol 한도(OUP 저자 지침 2026-11-17)
ok(int(W["body_words"]) <= 3000, f"본문 {W['body_words']} ≤ 3,000")
aw = int(W["abstract_words"]); ok(150 <= aw <= 250, f"초록 {aw}단어 150-250")
ok([p.split(":")[0] for p in AB] == ["Background", "Methods", "Results", "Conclusions"], "초록 소제목 Background·Methods·Results·Conclusions")
ok(not re.search(r"\[@", ab) and "2015" in ab and "2023" in ab, "초록 인용 없음·기간")
ok(not re.search(r"\b(SD|BYM2|WAIC|eGFR|RR|CrI|CKD)\b|\([A-Z]{2,}\)", ab), "초록 약어 없음")
ok(":" not in TITLE and "229" not in TITLE and "standardi" not in TITLE.lower() and TITLE not in PREV and len(TITLE) <= 85 and not re.search(r"\b[A-Z]{2,}\b", TITLE), f"제목 {len(TITLE)}자·쌍점·약어·이전 제목 없음")
KW = [k.strip() for k in C.KEYWORDS.split(";")]; ok(len(KW) <= 4, f"키워드 {len(KW)}개 ≤4")
ok(int(W["refs"]) <= 30, f"참고문헌 {W['refs']} ≤ 30")
d = Document(os.path.join(OUT, MSF)); ps = [p.text.strip() for p in d.paragraphs]; dx = "\n".join(ps)
tp = dx[:dx.find("\nAbstract\n")]
for t in ("Original Article", "Seongdae Kim, PhD", "kimsd@hongik.ac.kr", "Hongik University", "94 Wausan-ro", ORCID, "Telephone", "Data availability", "Conflicts of interest", "Author contributions (CRediT)", "Funding", "Acknowledgements", "Ethical approval", "Patient consent", f"{int(W['body_words']):,}"): ok(t in tp, f"제목면 '{t}'")
z = zipfile.ZipFile(os.path.join(OUT, MSF)); ftr = "".join(z.read(n).decode() for n in z.namelist() if re.match(r"word/(footer|header)\d*\.xml", n)); ok("PAGE" in ftr, "자동 쪽 번호")
ok(z.read("word/document.xml").decode().count("<w:drawing") == 0, "그림은 별도 파일(본문 삽입 없음)")
# 2. 절·순서
order = ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Ethical disclosure", "Conflicts of interest", "Funding", "Data availability", "References", "Figure legends", "Supplementary material"]
pos = [len(ps) - 1 - ps[::-1].index(k) if k in ("Conflicts of interest", "Funding", "Data availability", "Supplementary material") and k in ps else (ps.index(k) if k in ps else -1) for k in order]
ok(all(p >= 0 for p in pos) and pos == sorted(pos), f"원고 순서(규정) {pos}")
es = "\n".join(ps[pos[5]:pos[9]])
ok(IRB in es and "1964 Helsinki declaration" in es and CONSENT in es and "7002340-202611-HR-040" in es and "None declared." in es, "Ethical disclosure·COI·Funding")
ok("zenodo" in es.lower(), "데이터·코드 가용성")
meth = "\n".join(ps[pos[2]:pos[3]]); ok(AI in meth and dx.count("Claude (Anthropic)") == 1, "AI 고지 정본 문장 Methods 안 1회")
caps = [p for p in ps if re.match(r"^Figure \d\. ", p)]; alts = [p for p in ps if p.startswith("Alt text: ")]
ok(len(caps) == 2 and len(alts) == 2, "그림 설명 2개·Alt text 2개")
ok(re.search(r"Fig\. 1", dx[dx.find("\nResults\n"):]) and re.search(r"Fig\. 2", dx[dx.find("\nResults\n"):]), "본문 그림 인용")
ok(len(d.tables) == 2 and len(d.tables) + 2 <= 4, "표 2개(표+그림 ≤4)")
for k in (1, 2):
    im = Image.open(os.path.join(OUT, "Figures", f"Fig{k}.tif")); dpi = round(im.info.get("dpi", (0, 0))[0]); wmm = im.size[0] / dpi * 25.4; hmm = im.size[1] / dpi * 25.4
    ok(im.mode == "RGB" and dpi >= 600 and wmm <= 178.5 and hmm <= 242 and os.path.getsize(os.path.join(OUT, "Figures", f"Fig{k}.tif")) < 10e6, f"Fig{k}.tif RGB {dpi} dpi {wmm:.0f}x{hmm:.0f} mm")
heads = [h for h, _ in C.METHODS + C.RESULTS] + [p[4:] for p in D["Discussion"] if p.startswith("###")]
ok(not any(":" in h for h in heads) and not any(re.search(r"\b(eGFR|CKD|RR|WAIC|BYM2)\b", h) for h in heads), "소제목 쌍점·약어 없음")
# 3. 표·문서 위생
for nm, f in (("원고", MSF), ("보충", SUPF), ("커버", CLF)):
    dd = Document(os.path.join(OUT, f))
    for i, t in enumerate(dd.tables):
        b = t._tbl.tblPr.find(qn("w:tblBorders"))
        ok(b is not None and all(b.find(qn(f"w:{s}")).get(qn("w:val")) == "nil" for s in ("insideV", "insideH", "left", "right")), f"{nm} 표{i+1} 3선")
        bad = [r.text for j, row in enumerate(t.rows) if j > 0 for c in row.cells if len({id(x._tc) for x in row.cells}) == len(row.cells) for p in c.paragraphs for r in p.runs if r.bold and r.text.strip()]
        ok(not bad, f"{nm} 표{i+1} 데이터 칸 볼드 없음 {bad[:2]}")
        ok(not [c.text for r in t.rows for c in r.cells if re.search(r"\d\*", c.text)], f"{nm} 표{i+1} 별표 없음")
    x = subprocess.run(["unzip", "-p", os.path.join(OUT, f), "word/*.xml"], capture_output=True, text=True).stdout
    ok(not re.findall(r"<w:keepNext[ />]|<w:keepLines[ />]|<w:pageBreakBefore[ />]", x), f"{nm} Word 검은 네모 0")
    zz = zipfile.ZipFile(os.path.join(OUT, f)); core = zz.read("docProps/core.xml").decode(); app = zz.read("docProps/app.xml").decode()
    ok("2013-12-23" not in core and not any(n.startswith("customXml/") for n in zz.namelist()) and "<Words>0<" not in app, f"{nm} python-docx 지문 없음")
# 4. 문체·인용
body = re.sub(r"\s+", " ", dx[dx.find("\nIntroduction\n"):dx.find("\nEthical disclosure\n")])
ok(not re.search(r"\b(we|our|us|We|Our)\b|(?<!type )(?<!Moran's )\bI\b(?! *[–-])", body), "1인칭 없음")
supt = "\n".join(p.text for p in Document(os.path.join(OUT, SUPF)).paragraphs) + "\n".join(c.text for t in Document(os.path.join(OUT, SUPF)).tables for r in t.rows for c in r.cells)
cov = subprocess.run(["pdftotext", os.path.join(OUT, CLF.replace(".docx", ".pdf")), "-"], capture_output=True, text=True).stdout
allt = dx + supt + cov
ok("—" not in allt and not re.search(r"[가-힣]", allt), "em-dash·한글 없음"); ok(not re.search(r"\bsignifican", dx + supt, re.I), "'significant' 없음")
US = r"\b(\w*(standardiz|harmoniz|summariz|characteriz(?!tic)|categoriz|minimiz|randomiz|generaliz|normaliz|prioritiz|organiz|utiliz|penaliz)\w*|analyz(e|ed|ing)|modeled|modeling|center(s|ed)?|neighbor\w*|behavior\w*|aging|color|favor\w*|labeled|gray|anemia|hemo\w*)\b"
us = sorted(set(m.group(0) for m in re.finditer(US, body + " " + supt.split("Supplementary references")[0] + " " + cov)))   # 원문 제목(보충 참고문헌)은 제외; ok(not us, f"미국식 철자 없음 {us}")
ok(not re.search(r"(?<![\w.])-\d", body.replace("–", "")), "마이너스 U+2212")
ok(not re.search(r"\[(@|web:)", dx) and "{{" not in dx and not re.search(r"\{(sup|N|tci|ci)\(|\{N\[", allt), "미해결 인용·코드 조각 없음")
disc = re.sub(r"\([\d, –\-]+\)", "", dx[dx.find("\nDiscussion\n"):dx.find("\nEthical disclosure\n")])
dn = [m for m in re.findall(r".{15}\d.{8}", disc) if not re.search(r"(2015|2020|2023|2024|stage 3|3 months|788 million|6%|1964|17 million|60 mL|1\.73 m)", m)][:3]; ok(not dn, f"고찰 통계 수치 없음 {dn}")
ns = re.findall(r"(?:^|[.!?] )(\d+ [a-z])", body); ok(not ns, f"문장 첫머리 숫자 없음 {ns[:2]}")
refs = dx[dx.find("\nReferences\n"):dx.find("\nTable 1. ")]; rl = [l for l in refs.split("\n") if re.match(r"^\d+\. ", l)]
ok(len(rl) == len(KEYS), f"참고문헌 목록 {len(rl)}"); ok(not re.search(r"github|zenodo", refs, re.I), "참고문헌에 GitHub·Zenodo 없음")
ok(not re.search(r"\b[a-z]+-[A-Z][a-z]", refs.replace("Knorr-Held", "")) , "참고문헌 제목 대소문자 오류 없음")
ok(all(re.search(r"\. (19|20)\d\d;", l) or "Accessed" in l or "; 20" in l or "doi:" in l for l in rl), "AMA 연;권(호):쪽")
ok(re.search(r"\(\d+(, \d+|-\d+)*\)", body) and not re.search(r"\[\d+", body), "본문 인용 괄호 번호")
cc = subprocess.run([sys.executable, os.path.expandvars("$ST_DATA_ROOT") + "/G.Downloads/00_PLAYBOOK/검증기록/check_citation_order.py", os.path.join(OUT, MSF)], capture_output=True, text=True).stdout
ok("결과: PASS" in cc, "인용 순서 검사기 PASS")
cited = []
for m in re.finditer(r"(Table S\d|Figure S\d)", body):
    if m.group(1) not in cited: cited.append(m.group(1))
listed = ["Table S1", "Table S2", "Table S3", "Table S4", "Table S5", "Figure S1", "Table S6", "Table S7", "Table S8"]
ok(cited == [x for x in listed if x in cited] and set(listed) - set(cited) <= {"Table S8"}, f"보충 인용 순서 {cited}")
ok(all(x in supt for x in listed) and "Journal of Nephrology" in supt[:800] and "kimsd@hongik.ac.kr" in supt[:800] and "Supplementary material" in body, "보충 첫 쪽 정보·명칭")
sr = re.findall(r"\[S(\d+)\]", supt); fs_ = []; [fs_.append(int(n)) for n in sr if int(n) not in fs_]; ok(fs_ == list(range(1, 11)) and "S10. " in supt, "보충 참고문헌 S1-S10 순서")
ok("[ZENODO DOI]" not in dx + cov and re.search(r"10\.5281/zenodo\.\d+", dx) and re.search(r"10\.5281/zenodo\.\d+", cov), "Zenodo 공개 DOI")
ok(not re.search(r"(?i)nephrology d" + "ialysis|\bN" + "DT\b|\bC" + "EN\b|Clinical and E" + "xperimental|European Renal|overlap|previously submitted|companion|unpublished|resubmi", dx + cov + supt), "이전 저널·중복 고지·재투고 언급 없음")
ok("Chun" not in cov, "커버레터에 제외 심사자 없음")
icm = subprocess.run(["pdftotext", os.path.join(OUT, "ICMJE_Disclosure_Form.pdf"), "-"], capture_output=True, text=True).stdout
ok(TITLE[:50] in re.sub(r"\s+", " ", icm) and "Dial" + "ysis" not in icm, "ICMJE 제목 교체")
open(os.path.join(OUT, "check.txt"), "w").write("\n".join(R)); nf = sum(r.startswith("FAIL") for r in R)
print("\n".join(r for r in R if r.startswith("FAIL")) or "", f"\n{len(R)} checks, FAIL {nf}", "PASS" if nf == 0 else "")
