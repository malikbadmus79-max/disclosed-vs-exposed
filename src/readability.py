"""Readability check (design f2, OD-9; amendment A1).

A document passes if at least THRESHOLD of its word tokens are among the 1,000 most common English words.
- Text: PyMuPDF, Unicode NFKC (design f2), whole document.
- Word list: wordfreq top_n_list('en', 1000) (wordfreq 3.1.1; code Apache-2.0, data CC BY-SA 4.0;
  Speer 2022, doi:10.5281/zenodo.7199437).
- Tokens: wordfreq.tokenize(text, 'en'), keeping only tokens that contain at least one letter, so that figures
  in financial tables do not count as non-words.

usage:
  readability.py calibrate   share for every Phase 0 file with a text layer -> data/interim/readability_calibration.csv
  readability.py run         share and pass/fail for every report in the corpus, originals and _ocr copies
                             -> data/interim/readability.csv (THRESHOLD must be set by amendment A1 first)
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf
import wordfreq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
THRESHOLD = 0.25  # OD-9, calibrated 2026-11-12; amendment A1 (docs/amendments.md); was 0.30
COMMON = set(wordfreq.top_n_list("en", 1000))
LETTER = re.compile(r"[^\W\d_]")


def share(path: Path):
    with pymupdf.open(path) as d:
        text = unicodedata.normalize("NFKC", " ".join(pg.get_text() for pg in d))
    toks = [t for t in wordfreq.tokenize(text, "en") if LETTER.search(t)]
    hit = sum(t in COMMON for t in toks)
    return len(toks), hit, (hit / len(toks) if toks else 0.0)


def write(rows, path):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def calibrate():
    rows = []
    for r in csv.DictReader((ROOT / "data" / "interim" / "pilot_report_inventory.csv").open(encoding="utf-8")):
        if r["status"] != "ok" or r["extractability"] == "scanned_or_image":
            continue
        n, hit, s = share(ROOT / r["file"])
        rows.append({"firm": r["firm"], "fiscal_year": r["fiscal_year"], "type": r["type"], "file": r["file"],
                     "word_tokens": n, "common_tokens": hit, "common_share": f"{s:.4f}"})
        print(f"{s:.4f} {n:>8} {r['firm']} {r['fiscal_year']} {r['type']}", flush=True)
    write(rows, ROOT / "data" / "interim" / "readability_calibration.csv")


def corpus_files():
    """(ticker or firm, role, path) for every report file in the corpus."""
    out = []
    for r in csv.DictReader((ROOT / "data" / "interim" / "pilot_report_inventory.csv").open(encoding="utf-8")):
        if r["status"] == "ok":
            out.append((r["firm"], f"pilot {r['fiscal_year']} {r['type']}", r["file"]))
    for r in csv.DictReader((ROOT / "data" / "interim" / "phase2_report_inventory.csv").open(encoding="utf-8")):
        if r["status"] == "ok":
            out.append((r["ticker"], f"phase2 {r['fiscal_year']} {r['type']}", r["file"]))
    seen = {f for _, _, f in out}
    for p in sorted((ROOT / "data" / "raw" / "manual").rglob("*.pdf")):
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        if rel in seen or p.parent.name == "manual":  # loose duplicates in data/raw/manual/ are skipped
            continue
        out.append((p.parent.name.upper(), "owner-supplied" + (" OCR copy" if p.stem.endswith("_ocr") else ""), rel))
        seen.add(rel)
    # owner-supplied files later placed in the pilot/phase2 folders (Phase 4 tier-1 downloads, 2026-11-17)
    for sub in ("pilot_reports", "phase2_reports"):
        for p in sorted((ROOT / "data" / "raw" / sub).rglob("*.pdf")):
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            if rel in seen or p.stem.endswith("_ocr"):
                continue
            out.append((p.parent.name, "owner-supplied (Phase 4)", rel))
            seen.add(rel)
    for sub, role in (("pilot_reports", "pilot OCR copy"), ("phase2_reports", "phase2 OCR copy")):
        for p in sorted((ROOT / "data" / "raw" / sub).rglob("*_ocr.pdf")):
            out.append((p.parent.name, role, str(p.relative_to(ROOT)).replace("\\", "/")))
    return out


def run():
    rows = []
    for key, role, f in corpus_files():
        n, hit, s = share(ROOT / f)
        res = "pass" if s >= THRESHOLD else "fail"
        rows.append({"key": key, "role": role, "file": f, "word_tokens": n, "common_tokens": hit,
                     "common_share": f"{s:.4f}", "threshold": THRESHOLD, "result": res})
        print(f"{res} {s:.4f} {n:>8} {key} | {role} | {Path(f).name}", flush=True)
    write(rows, ROOT / "data" / "interim" / "readability.csv")


PAGE_BELOW, MAX_PAGE_SHARE = 0.20, 0.10  # amendment A2 (page-level rule)


def page_shares(path: Path):
    """Common-word share per page; a page with no word tokens has share 0 (A2)."""
    out = []
    with pymupdf.open(path) as d:
        for pg in d:
            toks = [t for t in wordfreq.tokenize(unicodedata.normalize("NFKC", pg.get_text()), "en") if LETTER.search(t)]
            out.append(sum(t in COMMON for t in toks) / len(toks) if toks else 0.0)
    return out


def pages():
    """A2: every original report file; OCR'd if more than 10% of pages are below 0.20 -> readability_pages.csv"""
    rows = []
    for key, role, f in corpus_files():
        if Path(f).stem.endswith("_ocr"):
            continue
        sh = page_shares(ROOT / f)
        low = sum(x < PAGE_BELOW for x in sh)
        frac = low / len(sh) if sh else 0.0
        rows.append({"key": key, "role": role, "file": f, "pages": len(sh), "pages_below_0.20": low,
                     "share_of_pages_below": f"{frac:.4f}", "a2_ocr": "yes" if frac > MAX_PAGE_SHARE else "no"})
        print(f"{rows[-1]['a2_ocr']:3} {frac:.3f} {low:>4}/{len(sh):<4} {key} | {role} | {Path(f).name}", flush=True)
    write(rows, ROOT / "data" / "interim" / "readability_pages.csv")


if __name__ == "__main__":
    {"calibrate": calibrate, "run": run, "pages": pages}[sys.argv[1]]()
