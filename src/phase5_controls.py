"""Phase 5: control variables for the H1/H2 sample (A22). Rule-based first pass with evidence; analyst decisions for
flagged values are applied from ANALYST below (each with page and quote).

candidates -> data/interim/controls_candidates.csv (all rule hits with evidence, for review)
build      -> data/interim/controls_firm_year.csv

usage: phase5_controls.py candidates | build
"""
import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I = ROOT / "data" / "interim"
csv.field_size_limit(10 ** 8)
BIG4 = {"KPMG": r"\bKPMG\b", "PwC": r"PricewaterhouseCoopers|\bPwC\b", "EY": r"Ernst\s*&\s*Young|\bEY\b", "Deloitte": r"\bDeloitte\b"}
ASSUR = re.compile(r"limited assurance|reasonable assurance|independent assurance|assurance statement|assurance engagement", re.I)
ASSUR_TOPIC = re.compile(r"sustainab|\bESG\b|\bGHG\b|greenhouse|emission|non-financial|climate|environmental", re.I)
ASSUR_EXCL = re.compile(r"internal control|\bICFR\b", re.I)
TA = re.compile(r"total\s+assets", re.I)
NUM = re.compile(r"\(?-?\d{1,3}(?:,\d{3})+(?:\.\d+)?\)?|\(?-?\d+\.\d+\)?")
UNIT = re.compile(r"(?:₦|N|NGN|\$|US\$|USD)\s*['’]?\s*000|(?:₦|N|NGN|\$|US\$|USD)?\s*(?:million|billion|m\b|bn\b)", re.I)
PARENT = re.compile(r"subsidiary of|parent company|holding company|ultimate (?:parent|holding|controlling)|substantial interest|"
                    r"(?:holds?|owns?|holding of)\s+\d{1,3}(?:\.\d+)?\s*%|\d{1,3}(?:\.\d+)?\s*%\s+of the (?:issued|ordinary|share)", re.I)


def sample():
    e = {r["ticker"]: r for r in csv.DictReader(open(ROOT / "data" / "processed" / "firm_exposure.csv", encoding="utf-8"))}
    c = {r["ticker"]: r for r in csv.DictReader(open(I / "ngx_census_frame.csv", encoding="utf-8"))}
    firms = {t for t, r in c.items() if r["census_stratum"] == "main" and not r["document_test"].startswith("failed")
             and t in e and e[t]["combined_index"] not in ("", "nan")}
    docs = [d for d in csv.DictReader(open(I / "phase4_documents.csv", encoding="utf-8")) if d["firm"] in firms]
    return firms, docs


def candidates():
    firms, docs = sample()
    tags = {r["doc"]: r for r in csv.DictReader(open(I / "section_tags.csv", encoding="utf-8"))}
    want = {d["doc"]: d for d in docs}
    pages = defaultdict(lambda: defaultdict(list))  # doc -> page -> texts
    with open(I / "paragraphs.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["doc"] in want:
                pages[r["doc"]][int(r["page"])].append(r["text"])
    out = []
    for doc, d in sorted(want.items()):
        t = tags[doc]
        fs0 = int(t["fs_start"]) if t["fs_start"] else None
        fs1 = int(t["fs_end"]) if t["fs_end"] else None
        base = {"doc": doc, "firm": d["firm"], "year": d["year"], "doc_type": d["doc_type"]}
        # auditor: FS start .. start+5
        if fs0:
            found = {}
            for p in range(fs0, fs0 + 6):
                txt = " ".join(pages[doc].get(p, []))
                for k, rx in BIG4.items():
                    m = re.search(rx, txt)
                    if m and k not in found:
                        found[k] = (p, txt[max(0, m.start() - 80):m.end() + 80])
            if found:
                for k, (p, q) in found.items():
                    out.append({**base, "variable": "big4", "value": k, "page": p, "evidence": q})
            else:
                txt = " ".join(" ".join(pages[doc].get(p, [])) for p in range(fs0, fs0 + 6))
                out.append({**base, "variable": "big4", "value": "none found", "page": f"{fs0}-{fs0 + 5}",
                            "evidence": ("text chars %d: " % len(txt)) + txt[:300]})
        # assurance
        for p, ts in sorted(pages[doc].items()):
            for tx in ts:
                for s in re.split(r"(?<=[.!?])\s+", tx):
                    if ASSUR.search(s) and ASSUR_TOPIC.search(s) and not ASSUR_EXCL.search(s):
                        out.append({**base, "variable": "assurance", "value": "hit", "page": p, "evidence": s[:400]})
        # total assets: first 'Total assets' in FS range with a number
        if fs0:
            got = 0
            for p in range(fs0, (fs1 or fs0) + 1):
                ts = pages[doc].get(p, [])
                page_txt = " ".join(ts)
                for tx in ts:
                    m = TA.search(tx)
                    if m:
                        nums = NUM.findall(tx[m.end():m.end() + 200])
                        unit = UNIT.findall(page_txt)
                        out.append({**base, "variable": "total_assets", "value": nums[0] if nums else "no number",
                                    "page": p, "evidence": f"units on page: {sorted(set(u.strip() for u in unit))[:4]} | "
                                                          + tx[max(0, m.start() - 60):m.end() + 160]})
                        got += 1
                        break
                if got >= 2:
                    break
        # foreign parent candidates (narrative + notes, first 40 hits)
        n = 0
        for p, ts in sorted(pages[doc].items()):
            for tx in ts:
                for m in PARENT.finditer(tx):
                    if n < 40:
                        out.append({**base, "variable": "parent", "value": "candidate", "page": p,
                                    "evidence": tx[max(0, m.start() - 200):m.end() + 200]})
                        n += 1
    with open(I / "controls_candidates.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["doc", "firm", "year", "doc_type", "variable", "value", "page", "evidence"]); w.writeheader(); w.writerows(out)
    print("firms", len(firms), "docs", len(want), "candidate rows", len(out))


if __name__ == "__main__":
    {"candidates": candidates}[sys.argv[1]]()
