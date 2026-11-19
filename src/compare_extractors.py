"""Phase 0, Task 3: compare PyMuPDF and pdfplumber text extraction on a 10-page sample of three reports.

Measures text-layer quality only (characters, ligature and replacement glyphs). No content analysis.
Output: data/interim/extraction_comparison.json
"""
import json
import re
import sys
from pathlib import Path

import pdfplumber
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ["dangote_cement/2025_SRX.pdf", "guinness_nigeria/2025_AR.pdf", "okomu_oil/2024_AR.pdf"]
ODD = re.compile("[ﬀ-ﬆ�ƒƠ-ǿ]")  # ligatures, replacement char, odd Latin glyphs
results = []
for rel in REPORTS:
    path = ROOT / "data" / "raw" / "pilot_reports" / rel
    with pymupdf.open(path) as doc:
        n = len(doc)
        pages = sorted({int(i * n / 10) for i in range(10)})
        mu = [doc[i].get_text() for i in pages]
    with pdfplumber.open(path) as pdf:
        pl = [(pdf.pages[i].extract_text() or "") for i in pages]
    results.append({
        "report": rel, "pages_in_file": n, "sample_pages": [p + 1 for p in pages],
        "pymupdf_chars": sum(len(t.strip()) for t in mu), "pdfplumber_chars": sum(len(t.strip()) for t in pl),
        "pymupdf_odd_glyphs": sum(len(ODD.findall(t)) for t in mu),
        "pdfplumber_odd_glyphs": sum(len(ODD.findall(t)) for t in pl),
        "pymupdf_empty_pages": sum(len(t.strip()) < 100 for t in mu),
        "pdfplumber_empty_pages": sum(len(t.strip()) < 100 for t in pl),
    })
out = ROOT / "data" / "interim" / "extraction_comparison.json"
out.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
