"""Phase 4, final step: outcome measures per firm-year (amendments A20, A21). No H1-H3 model is estimated here.

refine            -> config/dictionary_hazard_refined.json (exploratory, post hoc, A21): frozen dictionary minus
                     'storm', 'erosion', 'coastal'
score MODEL [n]   -> data/interim/climatebert_scores.csv (resumable; at most n paragraphs per run)
                     detector / specificity: reused from data/interim/validation_predictions.csv where present (same
                     revision, same text, deterministic models), new scores only for the other scored paragraphs;
                     tcfd / sentiment: all detector-positive paragraphs
measures          -> data/processed/outcomes_firm_year.csv

Scored paragraphs = model_eligible = 1 and section = narrative in data/interim/paragraphs.csv (split pieces count
separately, f3). Site matching: config/dictionary_sites.json rules R1-R3 (A17), the firm's own sites only.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I = ROOT / "data" / "interim"
CFG = ROOT / "config"
CACHE = ROOT / "data" / "raw" / "hf_cache"
SCORES = I / "climatebert_scores.csv"
OUT = ROOT / "data" / "processed" / "outcomes_firm_year.csv"
DROP_REFINED = {"storm", "erosion", "coastal"}
THR = 0.5
MODELS = {"detector": "climatebert/distilroberta-base-climate-detector",
          "specificity": "climatebert/distilroberta-base-climate-specificity",
          "tcfd": "climatebert/distilroberta-base-climate-tcfd",
          "sentiment": "climatebert/distilroberta-base-climate-sentiment"}
SENT = re.compile(r"(?<=[.!?])\s+")
csv.field_size_limit(10 ** 8)


def scored():
    out = []
    with open(I / "paragraphs.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["model_eligible"] == "1" and r["section"] == "narrative":
                out.append({k: r[k] for k in ("paragraph_id", "firm", "year", "doc", "doc_type", "text")})
    return out


# ------------------------------------------------------------------ refined dictionary
def refine():
    H = json.load(open(CFG / "dictionary_hazard.json", encoding="utf-8"))
    R = dict(H)
    R["name"] = "EXPLORATORY refined hazard dictionary (post hoc, A21): frozen dictionary minus 'storm', 'erosion', 'coastal'"
    R["amendment"] = "A21 (chosen after seeing the A20 precision results; its precision on the same sample is optimistic)"
    R["source"] = "config/dictionary_hazard.json (frozen, A20) with three terms removed; matching rule unchanged (A17)"
    R["terms"] = [t for t in H["terms"] if t["term"] not in DROP_REFINED]
    R["dropped_terms"] = sorted(DROP_REFINED)
    R["status"] = "exploratory; the frozen dictionary stays the main one"
    p = CFG / "dictionary_hazard_refined.json"
    p.write_text(json.dumps(R, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(p.name, len(R["terms"]), "terms")


# ------------------------------------------------------------------ ClimateBERT (exploratory)
def load_scores():
    s = defaultdict(dict)
    if SCORES.exists():
        for r in csv.DictReader(open(SCORES, encoding="utf-8")):
            s[r["id"]][r["model"]] = r
    return s


def score(which, limit):
    rev = (CACHE / f"models--{MODELS[which].replace('/', '--')}" / "refs" / "main").read_text().strip()
    have = load_scores()
    rows = scored()
    new = not SCORES.exists()
    f = open(SCORES, "a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, ["id", "model", "label", "p", "revision", "source"])
    if new:
        w.writeheader()
    if which in ("detector", "specificity"):
        reuse = {}
        for r in csv.DictReader(open(I / "validation_predictions.csv", encoding="utf-8")):
            if r["model"] == which and r["revision"] == rev:
                reuse[r["id"]] = r["p"]
        lab = "yes" if which == "detector" else "spec"
        n_reused = 0
        for r in rows:
            if which not in have.get(r["paragraph_id"], {}) and r["paragraph_id"] in reuse:
                w.writerow({"id": r["paragraph_id"], "model": which, "label": lab, "p": reuse[r["paragraph_id"]],
                            "revision": rev, "source": "reused (validation_predictions.csv)"})
                n_reused += 1
        f.flush()
        have = load_scores()
        print(which, "reused", n_reused)
    todo = [r for r in rows if which not in have.get(r["paragraph_id"], {})]
    if which != "detector":
        todo = [r for r in todo if "detector" in have.get(r["paragraph_id"], {})
                and float(have[r["paragraph_id"]]["detector"]["p"]) >= THR]
    todo = sorted(todo[:limit], key=lambda r: len(r["text"]))
    if todo:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        torch.set_num_threads(4)
        tok = AutoTokenizer.from_pretrained(MODELS[which], cache_dir=CACHE, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(MODELS[which], cache_dir=CACHE, local_files_only=True).eval()
        id2 = model.config.id2label
        for i in range(0, len(todo), 16):
            b = todo[i:i + 16]
            enc = tok([r["text"] for r in b], truncation=True, max_length=512, padding=True, return_tensors="pt")
            with torch.no_grad():
                pr = torch.softmax(model(**enc).logits, -1)
            for r, p in zip(b, pr):
                if which == "detector":
                    lab, val = "yes", float(p[[k for k, v in id2.items() if v == "yes"][0]])
                elif which == "specificity":
                    lab, val = "spec", float(p[[k for k, v in id2.items() if v == "spec"][0]])
                else:
                    k = int(p.argmax()); lab, val = id2[k], float(p[k])
                w.writerow({"id": r["paragraph_id"], "model": which, "label": lab, "p": f"{val:.6f}", "revision": rev, "source": "scored"})
            f.flush()
    f.close()
    have = load_scores()
    left = sum(1 for r in rows if which not in have.get(r["paragraph_id"], {})
               and (which == "detector" or float(have.get(r["paragraph_id"], {}).get("detector", {}).get("p", -1)) >= THR))
    print(which, "scored new", len(todo), "| still to score:", left)


# ------------------------------------------------------------------ site matching (A17 R1-R3)
def compile_sites():
    S = json.load(open(CFG / "dictionary_sites.json", encoding="utf-8"))
    ctx = re.compile("|".join(c["pattern"] for c in S["facility_context_terms"]), re.I)
    firms = {}
    for t, f in S["firms"].items():
        terms = []
        for site in f["sites"]:
            for term in site["terms"]:
                flags = 0 if term["case_sensitive"] else re.I
                rx = re.compile("|".join(term["patterns"]), flags)
                terms.append((site["facility_id"], term["match_rule"], rx))
        ex = [re.compile(re.escape(p), re.I) for p in f["exclude_phrases"]]
        firms[t] = (terms, ex)
    return firms, ctx


def names_site(text, firm, sites, ctx):
    if firm not in sites:
        return False
    terms, ex = sites[firm]
    for rx in ex:
        text = rx.sub(" ", text)
    para_ctx = bool(ctx.search(text))
    sents = None
    for fid, rule, rx in terms:
        if not rx.search(text):
            continue
        if rule == "R3":
            return True
        if rule == "R1" and para_ctx:
            return True
        if rule in ("R2", "R3+R2"):
            sents = sents or SENT.split(text)
            if any(rx.search(s) and ctx.search(s) for s in sents):
                return True
    return False


# ------------------------------------------------------------------ measures
def measures():
    docs = {d["doc"]: d for d in csv.DictReader(open(I / "phase4_documents.csv", encoding="utf-8"))}
    dicts = {}
    for name, fn in (("frozen", "dictionary_hazard.json"), ("refined", "dictionary_hazard_refined.json")):
        H = json.load(open(CFG / fn, encoding="utf-8"))
        dicts[name] = re.compile("|".join(p for t in H["terms"] for p in t["patterns"]), re.I)
    sites, ctx = compile_sites()
    sc = load_scores()
    tcfd_labels = ["governance", "strategy", "risk", "metrics"]
    sent_labels = ["risk", "opportunity", "neutral"]
    agg = defaultdict(lambda: defaultdict(float))
    meta = {}
    missing_scores = 0
    for r in scored():
        key = (r["firm"], int(r["year"]))
        d = docs[r["doc"]]
        m = meta.setdefault(key, {"firm": r["firm"], "year": int(r["year"]), "stratum": d["stratum"], "h3_main": d["h3_main"],
                                  "doc_types": set(), "docs": set()})
        m["doc_types"].add(r["doc_type"]); m["docs"].add(r["doc"])
        a = agg[key]; a["n_scored"] += 1
        site = None
        for name, rx in dicts.items():
            if rx.search(r["text"]):
                a[f"n_tagged_{name}"] += 1
                if site is None:
                    site = names_site(r["text"], r["firm"], sites, ctx)
                a[f"n_site_tagged_{name}"] += site
        s = sc.get(r["paragraph_id"], {})
        if "detector" not in s:
            missing_scores += 1
            continue
        if float(s["detector"]["p"]) >= THR:
            a["n_climate"] += 1
            if "specificity" in s and float(s["specificity"]["p"]) >= THR:
                a["n_specific"] += 1
            for mdl, labs in (("tcfd", tcfd_labels), ("sentiment", sent_labels)):
                if mdl in s:
                    a[f"n_{mdl}_{s[mdl]['label']}"] += 1
    # firm-years whose documents have no scored narrative paragraph (e.g. FS-only filings) are kept with n_scored = 0 and
    # empty shares: "no narrative disclosure" is itself a finding (f1)
    for d in docs.values():
        key = (d["firm"], int(d["year"]))
        m = meta.setdefault(key, {"firm": d["firm"], "year": int(d["year"]), "stratum": d["stratum"], "h3_main": d["h3_main"],
                                  "doc_types": set(), "docs": set()})
        m["doc_types"].add(d["doc_type"]); m["docs"].add(d["doc"])
        agg[key]  # creates an empty aggregate if absent
    rows = []
    for key in sorted(agg):
        a, m = agg[key], meta[key]
        n = a["n_scored"]
        if n == 0:
            rows.append({"firm": m["firm"], "year": m["year"], "stratum": m["stratum"], "h3_main": m["h3_main"],
                         "doc_types": "+".join(sorted(m["doc_types"])), "n_docs": len(m["docs"]),
                         "fs_only": int(m["doc_types"] == {"FS"}), "n_scored": 0})
            continue
        row = {"firm": m["firm"], "year": m["year"], "stratum": m["stratum"], "h3_main": m["h3_main"],
               "doc_types": "+".join(sorted(m["doc_types"])), "n_docs": len(m["docs"]), "fs_only": int(m["doc_types"] == {"FS"}),
               "n_scored": int(n)}
        for name in dicts:
            t, st = a[f"n_tagged_{name}"], a[f"n_site_tagged_{name}"]
            sfx = "" if name == "frozen" else "_refined"
            row.update({f"n_tagged{sfx}": int(t), f"Y3d{sfx}": round(t / n, 6), f"Y4d{sfx}": int(st),
                        f"Y4d_any{sfx}": int(st > 0), f"Y4s{sfx}": round(st / t, 6) if t else "", f"Y4r{sfx}": round(st / n, 6)})
        c = a["n_climate"]
        row.update({"n_climate_cb": int(c), "Y1_cb": round(c / n, 6), "Y2_cb": round(a["n_specific"] / c, 6) if c else ""})
        for lab in tcfd_labels:
            row[f"tcfd_{lab}_share_cb"] = round(a[f"n_tcfd_{lab}"] / c, 6) if c else ""
        for lab in sent_labels:
            row[f"sentiment_{lab}_share_cb"] = round(a[f"n_sentiment_{lab}"] / c, 6) if c else ""
        rows.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(max(rows, key=len)), restval=""); w.writeheader(); w.writerows(rows)
    print("firm-years", len(rows), "| paragraphs without a detector score:", missing_scores)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "refine":
        refine()
    elif cmd == "score":
        score(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9)
    elif cmd == "measures":
        measures()
