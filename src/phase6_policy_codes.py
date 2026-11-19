"""Phase 6: firm-year policy coding P1-P7 (design i; amendment A25). DESCRIPTIVE, analyst-coded, no human validation.

candidates -> data/interim/policy_candidates.csv: every sentence matching a code's search pattern (A25), with doc, page,
              paragraph id; the analyst reads every candidate
build      -> data/processed/policy_codes_firm_year.csv and data/processed/policy_codes_evidence.csv from the analyst's
              decisions in data/interim/policy_decisions.csv (candidate_id, code, value, note)

usage: phase6_policy_codes.py candidates | build
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I = ROOT / "data" / "interim"
P = ROOT / "data" / "processed"
csv.field_size_limit(10 ** 8)
SENT = re.compile(r"(?<=[.!?])\s+")
HAZ = r"physical risk|flood|heat ?wave|extreme heat|\bheat\b|drought|water stress|water scarcity|sea[- ]level|coastal|storm|extreme weather|hazard|rainfall|erosion"
PATTERNS = {
    "P1": [r"resilien", r"climate|physical risk|flood|\bheat|drought|weather|hazard"],
    "P2": [r"scenario analysis|climate[- ]related scenario|climate scenario|scenarios?\b.{0,80}(?:\bRCP|\bSSP|NGFS|\bIEA\b|1\.5\s?°?\s?C|\b2\s?°\s?C|net[- ]zero|warming)"
           r"|(?:\bRCP|\bSSP|NGFS|1\.5\s?°?\s?C|warming).{0,80}scenarios?"],
    "P3": [r"\d+(?:\.\d+)?\s?%|\b\d[\d,.]*\b", HAZ, r"\basset|\bsite|facilit|operation|location"],
    "P4": [r"risk register|enterprise[- ]wide risk|enterprise risk|\bERM\b|risk management framework|risk map|risk committee|principal risk|risk universe",
           r"climate|weather|flood|physical risk"],
    "P5": [HAZ, r"\bsite|\bplant|facilit|\basset|location|terminal|\bestate|\bOML"],
    "P6": [r"IFRS\s?S\s?1|IFRS\s?S\s?2|\bISSB\b"],
    "P7": [r"Sustainability Disclosure Guidelines|(?:NGX|\bNSE\b|Nigerian (?:Stock )?Exchange).{0,80}sustainability.{0,20}guideline|"
           r"sustainability.{0,20}guideline.{0,80}(?:NGX|\bNSE\b|Nigerian (?:Stock )?Exchange)"],
}
RX = {k: [re.compile(p, re.I) for p in v] for k, v in PATTERNS.items()}


def scope():
    docs = [d for d in csv.DictReader(open(I / "phase4_documents.csv", encoding="utf-8"))
            if d["stratum"] == "main" and d["doc"] != "NNFM_2020_AR"]  # A23
    return {d["doc"]: d for d in docs}


def site_terms():
    S = json.load(open(ROOT / "config" / "dictionary_sites.json", encoding="utf-8"))
    return {t: re.compile("|".join(p for s in f["sites"] for term in s["terms"] for p in term["patterns"]) or r"(?!x)x")
            for t, f in S["firms"].items()}


def candidates():
    docs = scope(); st = site_terms()
    out = []
    with open(I / "paragraphs.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["doc"] not in docs or r["duplicate_of"]:
                continue
            for s in SENT.split(r["text"]):
                for code, rxs in RX.items():
                    ok = all(rx.search(s) for rx in rxs)
                    if code == "P5" and not ok and RX["P5"][0].search(s) and r["firm"] in st and st[r["firm"]].search(s):
                        ok = True  # hazard term + a site-dictionary term of the firm
                    if ok:
                        out.append({"candidate_id": f"{code}-{len(out):05d}", "code": code, "firm": r["firm"], "year": r["year"],
                                    "doc": r["doc"], "page": r["page"], "section": r.get("section", ""), "paragraph_id": r["paragraph_id"],
                                    "sentence": s[:600]})
    with open(I / "policy_candidates.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(out[0])); w.writeheader(); w.writerows(out)
    c = defaultdict(int); fy = defaultdict(set)
    for o in out:
        c[o["code"]] += 1; fy[o["code"]].add((o["firm"], o["year"]))
    print({k: (c[k], len(fy[k])) for k in sorted(c)})


def build():
    docs = scope()
    fys = sorted({(d["firm"], int(d["year"])) for d in docs.values()})
    cand = {r["candidate_id"]: r for r in csv.DictReader(open(I / "policy_candidates.csv", encoding="utf-8"))}
    dec = list(csv.DictReader(open(I / "policy_decisions.csv", encoding="utf-8")))
    codes = {fy: {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "P5": 0, "P6": "none", "P7": 0} for fy in fys}
    ev = []
    rank = {"none": 0, "none (readiness stated)": 1, "voluntary": 2, "early": 3}
    for d in dec:
        c = cand[d["candidate_id"]]; key = (c["firm"], int(c["year"]))
        if d["code"] == "P6":
            if rank[d["value"]] > rank[codes[key]["P6"]]:
                codes[key]["P6"] = d["value"]
        elif d["value"] == "1":
            codes[key][d["code"]] = 1
        if d["value"] not in ("0", "none"):
            ev.append({"firm": c["firm"], "year": c["year"], "code": d["code"], "value": d["value"], "doc": c["doc"], "page": c["page"],
                       "paragraph_id": c["paragraph_id"], "candidate_id": c["candidate_id"], "passage": c["sentence"], "note": d["note"]})
    with open(P / "policy_codes_firm_year.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["firm", "year", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "coder", "validation"]); w.writeheader()
        for (firm, year), c in codes.items():
            w.writerow({"firm": firm, "year": year, **c, "coder": "analyst (Claude), A25 rules",
                        "validation": "none: descriptive, analyst-coded, no human validation"})
    with open(P / "policy_codes_evidence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["firm", "year", "code", "value", "doc", "page", "paragraph_id", "candidate_id", "passage", "note"])
        w.writeheader(); w.writerows(ev)
    tot = {k: sum(1 for c in codes.values() if c[k] == 1) for k in ("P1", "P2", "P3", "P4", "P5", "P7")}
    p6 = defaultdict(int)
    for c in codes.values():
        p6[c["P6"]] += 1
    print("firm-years", len(codes), tot, dict(p6), "| evidence rows", len(ev))


if __name__ == "__main__":
    {"candidates": candidates, "build": build}[sys.argv[1]]()
