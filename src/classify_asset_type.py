"""Phase 0: add asset_type (point / dispersed) to data/interim/facility_locatability.csv.

Owner rule (2026-11-07): point sites are plants, breweries, factories, terminals and similar single sites;
dispersed assets are oil and gas licence areas and telecom networks, measured at state/area level and
analysed separately. Plantation estates are bounded single sites, so they are classed as point sites with
a flag. Unnamed networks of many small sites (such as depots) are classed as dispersed.
"""
import csv
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data" / "interim" / "facility_locatability.csv"
DISPERSED_TYPES = {"oil and gas licence area", "offshore licence area", "network sites", "network facility", "depots"}
AREA_POINT_TYPES = {"plantation", "plantation and oil mill", "plantation and corporate office"}

with PATH.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
bad = [r["facility"] for r in rows if None in r]
if bad:  # an unquoted comma shifts columns; stop before writing anything
    raise SystemExit(f"Malformed rows (extra fields): {bad}")
fields = list(rows[0].keys())
if "asset_type" not in fields:
    fields.insert(fields.index("rating") + 1, "asset_type")
if "asset_note" not in fields:
    fields.insert(fields.index("asset_type") + 1, "asset_note")
for r in rows:
    t = r["facility_type"]
    r["asset_type"] = "dispersed" if t in DISPERSED_TYPES else "point"
    r["asset_note"] = "bounded area site (estate); polygon preferred" if t in AREA_POINT_TYPES else ""
tmp = PATH.with_suffix(".csv.tmp")  # write fully, then replace, so a failure cannot truncate the table
with tmp.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fields)
    w.writeheader()
    w.writerows(rows)
tmp.replace(PATH)

op = [r for r in rows if r["is_office"] == "no"]
for kind in ("point", "dispersed"):
    sel = [r for r in op if r["asset_type"] == kind]
    counts = {g: sum(r["rating"] == g for r in sel) for g in "ABCD"}
    print(kind, len(sel), counts, {g: f"{100 * c / len(sel):.1f}%" for g, c in counts.items()})
    if kind == "dispersed":
        for r in sel:
            print("   ", r["firm"], "|", r["facility"], "|", r["rating"])
print("area point sites:", sum(r["asset_note"] != "" for r in op))
