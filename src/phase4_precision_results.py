"""Phase 4: results of the A20 dictionary precision check (external helper C1). Precision overall, per term family and
per term, with exact Clopper-Pearson 95% intervals (pre-specified in A20) and Wilson 95% intervals (owner request).
Writes data/interim/precision_results.csv.

usage: phase4_precision_results.py
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I = ROOT / "data" / "interim"
FAMILIES = ["flood", "storm", "drought / water stress", "heat", "coastal / erosion / sea level", "wildfire"]
Z = 1.959963984540054


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def bisect(f, lo=0.0, hi=1.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) else (lo, mid)
    return (lo + hi) / 2


def clopper_pearson(k, n, a=0.05):
    lo = 0.0 if k == 0 else bisect(lambda p: 1 - binom_cdf(k - 1, n, p) < a / 2)   # P(X >= k) = a/2
    hi = 1.0 if k == n else bisect(lambda p: binom_cdf(k, n, p) > a / 2)            # P(X <= k) = a/2
    return lo, hi


def wilson(k, n):
    p = k / n; d = 1 + Z * Z / n; c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def main():
    ans = list(csv.DictReader(open(I / "precision_answers_C1.csv", encoding="utf-8-sig")))
    fam = {t["term"]: t["hazard_group"] for t in json.load(open(ROOT / "config" / "dictionary_hazard.json", encoding="utf-8"))["terms"]}
    groups = [("overall", "all", ans)] + [("family", f, [r for r in ans if fam[r["term"]] == f]) for f in FAMILIES] + \
             [("term", t, [r for r in ans if r["term"] == t]) for t in sorted({r["term"] for r in ans})]
    out = []
    for level, name, rs in groups:
        n = len(rs); k = sum(r["answer"].strip().lower() == "yes" for r in rs)
        row = {"level": level, "group": name, "n": n, "yes": k, "precision": round(k / n, 4) if n else ""}
        if n:
            c, w = clopper_pearson(k, n), wilson(k, n)
            row.update({"cp_low": round(c[0], 4), "cp_high": round(c[1], 4), "wilson_low": round(w[0], 4), "wilson_high": round(w[1], 4)})
        out.append(row)
    cols = ["level", "group", "n", "yes", "precision", "cp_low", "cp_high", "wilson_low", "wilson_high"]
    with open(I / "precision_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, restval=""); w.writeheader(); w.writerows(out)
    for r in out:
        print(f"| {r['level']} | {r['group']} | {r['yes']}/{r['n']} | {r['precision']} | {r.get('cp_low','')}–{r.get('cp_high','')} | {r.get('wilson_low','')}–{r.get('wilson_high','')} |")


if __name__ == "__main__":
    main()
