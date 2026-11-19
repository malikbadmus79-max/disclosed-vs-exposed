"""Phase 5: Y5 (site ever named), hazard gap tables and H4 (A22). Descriptive only.

Outputs
  data/processed/site_mentions.csv          per site: Y5 (named anywhere), named in a hazard-tagged scored paragraph
                                            (frozen / refined), exposures
  outputs/tables/gap_firm_hazard.csv        per firm x hazard (exposed firms): mentions the hazard family? names an
                                            exposed site in a hazard-tagged paragraph?
  outputs/tables/h4.csv                     H4: share of exposed main point sites never named, overall / by sector / by firm

usage: phase5_sites.py
"""
import csv
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase4_precision_results import clopper_pearson  # noqa: E402

I = ROOT / "data" / "interim"
CFG = ROOT / "config"
TAB = ROOT / "outputs" / "tables"
SENT = re.compile(r"(?<=[.!?])\s+")
HAZ = {"rf100": ("river flood", ["flood"]), "coastal": ("coastal flood", ["flood", "coastal / erosion / sea level"]),
       "heat": ("heat", ["heat"]), "water": ("water stress", ["drought / water stress"])}
EXPOSED_COL = {"rf100": "rf100_exposed", "coastal": "coastal_rp100_exposed", "heat": "heat_exposed", "water": "water_stress_exposed"}
csv.field_size_limit(10 ** 8)


def site_matchers():
    S = json.load(open(CFG / "dictionary_sites.json", encoding="utf-8"))
    ctx = re.compile("|".join(c["pattern"] for c in S["facility_context_terms"]), re.I)
    firms = {}
    for t, f in S["firms"].items():
        terms = [(s["facility_id"], term["match_rule"], re.compile("|".join(term["patterns"]), 0 if term["case_sensitive"] else re.I))
                 for s in f["sites"] for term in s["terms"]]
        firms[t] = (terms, [re.compile(re.escape(p), re.I) for p in f["exclude_phrases"]])
    return firms, ctx


def sites_named(text, firm, firms, ctx):
    """Set of facility_ids of `firm` named in `text` under A17 rules R1-R3."""
    if firm not in firms:
        return set()
    terms, ex = firms[firm]
    for rx in ex:
        text = rx.sub(" ", text)
    para_ctx, sents, out = None, None, set()
    for fid, rule, rx in terms:
        if fid in out or not rx.search(text):
            continue
        if rule == "R3":
            out.add(fid)
        elif rule == "R1":
            if para_ctx is None:
                para_ctx = bool(ctx.search(text))
            if para_ctx:
                out.add(fid)
        else:  # R2, R3+R2
            sents = sents or SENT.split(text)
            if any(rx.search(s) and ctx.search(s) for s in sents):
                out.add(fid)
    return out


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    firms, ctx = site_matchers()
    fam_rx = {}
    for name, fn in (("frozen", "dictionary_hazard.json"), ("refined", "dictionary_hazard_refined.json")):
        H = json.load(open(CFG / fn, encoding="utf-8"))
        fam_rx[name] = {g: re.compile("|".join(p for t in H["terms"] if t["hazard_group"] == g for p in t["patterns"]), re.I)
                        for g in {t["hazard_group"] for t in H["terms"]}}
    y5 = set()                                   # facility ids named anywhere
    named_haz = {"frozen": set(), "refined": set()}   # named in a hazard-tagged scored paragraph
    named_fam = defaultdict(set)                 # (dict, family) -> facility ids named in a paragraph with that family
    fam_firm = defaultdict(set)                  # (dict, family) -> firms with >= 1 scored paragraph using that family
    with open(I / "paragraphs.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            named = sites_named(r["text"], r["firm"], firms, ctx)
            y5 |= named
            if r["model_eligible"] != "1" or r["section"] != "narrative":
                continue
            for d, fams in fam_rx.items():
                hit = [g for g, rx in fams.items() if rx.search(r["text"])]
                for g in hit:
                    fam_firm[(d, g)].add(r["firm"])
                    named_fam[(d, g)] |= named
                if hit:
                    named_haz[d] |= named
    sites = list(csv.DictReader(open(ROOT / "data" / "processed" / "site_hazards.csv", encoding="utf-8")))
    sector = {r["ticker"]: r["sector_provisional"] for r in csv.DictReader(open(I / "ngx_census_frame.csv", encoding="utf-8"))}
    out = []
    for s in sites:
        exp = {h: int(s[c] == "1") for h, c in EXPOSED_COL.items()}
        out.append({"facility_id": s["facility_id"], "ticker": s["ticker"], "census_stratum": s["census_stratum"],
                    "site_set": s["site_set"], "facility": s["facility"], "sector": sector.get(s["ticker"], ""),
                    **{f"exp_{h}": v for h, v in exp.items()}, "exp_any": int(any(exp.values())),
                    "Y5_named_any": int(s["facility_id"] in y5),
                    "named_in_hazard_para": int(s["facility_id"] in named_haz["frozen"]),
                    "named_in_hazard_para_refined": int(s["facility_id"] in named_haz["refined"])})
    with open(ROOT / "data" / "processed" / "site_mentions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(out[0])); w.writeheader(); w.writerows(out)

    # gap table: exposed firms x hazard (main census, main site set)
    main = [s for s in out if s["site_set"] == "main" and s["census_stratum"] == "main"]
    by_firm = defaultdict(list)
    for s in main:
        by_firm[s["ticker"]].append(s)
    gap = []
    for t in sorted(by_firm):
        for h, (label, fams) in HAZ.items():
            ex = [s for s in by_firm[t] if s[f"exp_{h}"]]
            if not ex:
                continue
            row = {"firm": t, "sector": sector.get(t, ""), "hazard": label, "main_sites": len(by_firm[t]), "exposed_sites": len(ex)}
            for d in ("frozen", "refined"):
                sfx = "" if d == "frozen" else "_refined"
                row[f"mentions_hazard{sfx}"] = int(any(t in fam_firm[(d, g)] for g in fams))
                row[f"names_exposed_site_in_hazard_para{sfx}"] = int(any(s["facility_id"] in set().union(*[named_fam[(d, g)] for g in fams]) for s in ex))
                row[f"names_exposed_site_in_any_hazard_para{sfx}"] = int(any(s["facility_id"] in named_haz[d] for s in ex))
            row["exposed_sites_ever_named_Y5"] = sum(s["Y5_named_any"] for s in ex)
            gap.append(row)
    with open(TAB / "gap_firm_hazard.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(gap[0])); w.writeheader(); w.writerows(gap)

    # H4
    rows = []
    def h4(level, name, ss):
        ex = [s for s in ss if s["exp_any"]]
        n, k = len(ex), sum(1 for s in ex if not s["Y5_named_any"])
        lo, hi = clopper_pearson(k, n) if n else ("", "")
        rows.append({"level": level, "group": name, "exposed_sites": n, "never_named": k,
                     "share_never_named": round(k / n, 4) if n else "", "cp_low": round(lo, 4) if n else "", "cp_high": round(hi, 4) if n else ""})
    h4("overall", "main census, main point sites", main)
    for sec in sorted({s["sector"] for s in main}):
        h4("sector", sec, [s for s in main if s["sector"] == sec])
    for t in sorted(by_firm):
        h4("firm", t, by_firm[t])
    rob = [s for s in out if s["site_set"] == "main" and s["census_stratum"] != "main"]
    h4("robustness stratum", "robustness-stratum main point sites (separate)", rob)
    with open(TAB / "h4.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
    print("sites", len(out), "| main point sites", len(main), "| exposed", sum(s["exp_any"] for s in main),
          "| Y5=1 among main", sum(s["Y5_named_any"] for s in main), "| gap rows", len(gap))
    print("H4 overall:", rows[0])


if __name__ == "__main__":
    main()
