"""Phase 4: dictionary precision-check sample (amendment A20). Draws 100 snippets of hazard-tagged paragraphs.

Frame: scored narrative paragraphs (model_eligible = 1, section = narrative) of main-census firms with >= 1 match of the
frozen config/dictionary_hazard.json. Stratified by hazard term family (equal allocation 17/17/17/17/16/16; a shortfall
goes to the other families in turn), at most 5 snippets per firm and 1 per paragraph, seed 20261117 (numpy default_rng).
Snippet = sentence containing the match +/- 1 sentence, match marked [[ ]].

Writes data/interim/precision_sample.csv (id, firm, year, term, snippet), in random order. No count, share or measure is
computed or printed: only the composition of the drawn sample is printed.

usage: phase4_precision_sample.py
"""
import csv
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
I = ROOT / "data" / "interim"
P = json.load(open(ROOT / "config" / "parameters.json", encoding="utf-8"))["validation"]["precision_check"]
SEED, N, FIRM_CAP = P["seed"], 100, 5
FAMILIES = ["flood", "storm", "drought / water stress", "heat", "coastal / erosion / sea level", "wildfire"]
TARGET = dict(zip(FAMILIES, [17, 17, 17, 17, 16, 16]))
SENT = re.compile(r"(?<=[.!?])\s+")
csv.field_size_limit(10 ** 8)


def main():
    H = json.load(open(ROOT / "config" / "dictionary_hazard.json", encoding="utf-8"))
    pats = [(t["term"], t["hazard_group"], re.compile(p, re.I)) for t in H["terms"] for p in t["patterns"]]
    docs = {d["doc"]: d for d in csv.DictReader(open(I / "phase4_documents.csv", encoding="utf-8"))}
    cand = {f: [] for f in FAMILIES}  # family -> [(paragraph row, [(term, start, end)])]
    with open(I / "paragraphs.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["model_eligible"] != "1" or r["section"] != "narrative" or docs[r["doc"]]["stratum"] != "main":
                continue
            hits = {}
            for term, fam, rx in pats:
                for m in rx.finditer(r["text"]):
                    hits.setdefault(fam, []).append((term, m.start(), m.end()))
            for fam, h in hits.items():
                cand[fam].append(({k: r[k] for k in ("paragraph_id", "firm", "year", "text")}, sorted(set(h), key=lambda x: x[1])))
    rng = np.random.default_rng(SEED)
    queues = {}
    for fam in FAMILIES:
        lst = sorted(cand[fam], key=lambda x: x[0]["paragraph_id"])
        queues[fam] = [lst[i] for i in rng.permutation(len(lst))]
    target, got, pos = dict(TARGET), {f: 0 for f in FAMILIES}, {f: 0 for f in FAMILIES}
    picked, used, firm_n = [], set(), {}
    while len(picked) < N:
        progress = False
        for fam in FAMILIES:
            if got[fam] >= target[fam] or len(picked) >= N:
                continue
            q = queues[fam]
            while pos[fam] < len(q):
                row, hits = q[pos[fam]]; pos[fam] += 1
                if row["paragraph_id"] in used or firm_n.get(row["firm"], 0) >= FIRM_CAP:
                    continue
                term, a, b = hits[int(rng.integers(len(hits)))]
                picked.append((fam, row, term, a, b)); used.add(row["paragraph_id"])
                firm_n[row["firm"]] = firm_n.get(row["firm"], 0) + 1; got[fam] += 1; progress = True
                break
        if not progress:  # a family ran out (frame or caps): give its remaining places to the other families in turn
            open_f = [f for f in FAMILIES if pos[f] < len(queues[f])]
            if not open_f:
                break
            for fam in FAMILIES:
                if got[fam] < target[fam] and pos[fam] >= len(queues[fam]):
                    rest = target[fam] - got[fam]; target[fam] = got[fam]
                    for k in range(rest):
                        target[open_f[k % len(open_f)]] += 1
    rows = []
    for fam, row, term, a, b in picked:
        t = row["text"]
        marked = t[:a] + "[[" + t[a:b] + "]]" + t[b:]
        sents = SENT.split(marked)
        idx = next(i for i, s in enumerate(sents) if "[[" in s)
        snippet = " ".join(sents[max(0, idx - 1):idx + 2])
        rows.append({"id": f"{row['paragraph_id']}@{a}", "firm": row["firm"], "year": row["year"], "term": term, "snippet": snippet})
    rows = [rows[i] for i in np.random.default_rng(SEED + 1).permutation(len(rows))]
    with open(I / "precision_sample.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["id", "firm", "year", "term", "snippet"]); w.writeheader(); w.writerows(rows)
    print("sampled", len(rows), "| per family", got, "| firms", len(firm_n), "| max per firm", max(firm_n.values()))


if __name__ == "__main__":
    main()
