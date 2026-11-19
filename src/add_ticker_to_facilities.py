"""Phase 0: add ngx_ticker and census_status to data/interim/facility_locatability.csv from data/interim/firm_ticker_map.csv.

Lafarge Africa's facilities map to HBMNG (renamed HBM Nigeria Plc, July 2026). Flour Mills was delisted
(effective 30 Dec 2024), so its facility rows are kept only as a methods note.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "interim" / "facility_locatability.csv"
with (ROOT / "data" / "interim" / "firm_ticker_map.csv").open(newline="", encoding="utf-8") as f:
    m = {r["firm"]: r for r in csv.DictReader(f)}
with PATH.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
if any(None in r for r in rows) or any(r["firm"] not in m for r in rows):
    raise SystemExit("malformed row or unmapped firm; nothing written")
fields = list(rows[0])
for col in ("ngx_ticker", "census_status"):
    if col not in fields:
        fields.insert(1 + fields.index("firm") + (col == "census_status"), col)
for r in rows:
    r["ngx_ticker"] = m[r["firm"]]["ngx_ticker"]
    r["census_status"] = m[r["firm"]]["census_status"]
tmp = PATH.with_suffix(".csv.tmp")
with tmp.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fields)
    w.writeheader()
    w.writerows(rows)
tmp.replace(PATH)
main = [r for r in rows if r["census_status"] == "main" and r["is_office"] == "no"]
for label, sel in (("main operational", main), ("main point", [r for r in main if r["asset_type"] == "point"])):
    n = len(sel)
    print(label, n, {g: f"{sum(r['rating'] == g for r in sel)} ({100 * sum(r['rating'] == g for r in sel) / n:.1f}%)" for g in "ABCD"})
print("flour mills rows (methods note):", sum(r["firm"] == "flour_mills" for r in rows), "| lafarge rows ->", {r["ngx_ticker"] for r in rows if r["firm"] == "lafarge_africa"})
