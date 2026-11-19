"""Phase 0: apply the owner's grading rule C1 (2026-11-07) to data/interim/facility_locatability.csv.

Rule: a location given only by local government area is grade C. An estate name without a town is grade B
only if the estate can be uniquely matched (in report text or OSM); otherwise it is grade C.
Presco's estates are named without a town, and no unique match was found in the report text read or in the
OSM query results, so they move from B to C.
"""
import csv
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data" / "interim" / "facility_locatability.csv"
ESTATES = {("presco", "Cowan estate"), ("presco", "Ologbo estate"), ("presco", "ATO estate"),
           ("presco", "Elele estate"), ("presco", "Ubima estate"),
           ("presco", "Sakponba Estate (new 50 t/h palm oil mill)")}
NOTE = "Rule C1: estate name without a town; no unique match in report text or OSM, so grade C"

with PATH.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
if any(None in r for r in rows):
    raise SystemExit("malformed row; nothing written")
changed = 0
for r in rows:
    if (r["firm"], r["facility"]) in ESTATES and r["rating"] != "C":
        r["rating"] = "C"
        r["note"] = (r["note"] + "; " if r["note"] else "") + NOTE
        changed += 1
tmp = PATH.with_suffix(".csv.tmp")
with tmp.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, list(rows[0]))
    w.writeheader()
    w.writerows(rows)
tmp.replace(PATH)
print("changed:", changed)
op = [r for r in rows if r["is_office"] == "no"]
for label, sel in (("all", rows), ("operational", op), ("point", [r for r in op if r["asset_type"] == "point"])):
    n = len(sel)
    print(label, n, {g: f"{sum(r['rating'] == g for r in sel)} ({100 * sum(r['rating'] == g for r in sel) / n:.1f}%)" for g in "ABCD"})
