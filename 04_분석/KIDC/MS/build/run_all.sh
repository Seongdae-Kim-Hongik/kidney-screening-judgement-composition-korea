#!/bin/bash
# 32호 KIDC Journal of Nephrology 전체 빌드(2026-11-17): 그림 → 원고 → 보충 → 커버 → ICMJE → sanitize → PDF → 검사기
set -e; cd "$(dirname "$0")"; O=../out
python3 figs_kids.py 2>&1 | grep -v Warning
python3 build_ms.py
python3 esm_kids.py
python3 cover_kids.py "$@"
python3 forms_ms.py
python3 sanitize_docx.py $O/Manuscript.docx $O/Supplementary_material.docx $O/Cover_Letter.docx > /dev/null
for f in Manuscript Supplementary_material Cover_Letter; do /opt/homebrew/bin/soffice --headless -env:UserInstallation=file:///tmp/lo_kidc_ms --convert-to pdf --outdir $O $O/$f.docx > /dev/null 2>&1; done
python3 check_ms.py
