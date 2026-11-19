"""Merge an owner spot-check export (from data/processed/spotcheck_app.html) into data/processed/spotcheck_gradeA.csv.

The export has: facility_id, owner_check (correct / approximate / wrong / moved), owner_lat, owner_lon, owner_note,
checked_at. Rows are matched by facility_id. The check goes into the column "owner_check (ok / wrong / move-to)"
(with the moved-to point appended for "moved") and the note into "owner_comment". Separate columns owner_lat,
owner_lon and checked_at are added. Facility IDs that are not in the spot-check file are reported, not added.
A copy of the previous file is kept as spotcheck_gradeA.csv.bak.

usage: merge_spotcheck.py path/to/spotcheck_export_YYYY-MM-DD.csv
"""
import csv
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPOT = ROOT / "data" / "processed" / "spotcheck_gradeA.csv"
CHECK_COL, NOTE_COL = "owner_check (ok / wrong / move-to)", "owner_comment"
VALID = {"correct", "approximate", "wrong", "moved", ""}


def main() -> None:
    export = [r for r in csv.DictReader(Path(sys.argv[1]).open(newline="", encoding="utf-8-sig"))]
    rows = list(csv.DictReader(SPOT.open(newline="", encoding="utf-8")))
    fields = list(rows[0]) + [c for c in ("owner_lat", "owner_lon", "checked_at") if c not in rows[0]]
    by = {r["facility_id"]: r for r in rows}
    merged, unknown, bad = 0, [], []
    for e in export:
        fid = e["facility_id"].strip()
        if fid not in by:
            unknown.append(fid); continue
        chk = e.get("owner_check", "").strip().lower()
        if chk not in VALID:
            bad.append((fid, chk)); continue
        r = by[fid]
        r[CHECK_COL] = chk + (f" -> {e['owner_lat']},{e['owner_lon']}" if chk == "moved" and e.get("owner_lat") else "")
        r[NOTE_COL] = e.get("owner_note", "")
        r["owner_lat"], r["owner_lon"], r["checked_at"] = e.get("owner_lat", ""), e.get("owner_lon", ""), e.get("checked_at", "")
        merged += 1
    shutil.copy(SPOT, SPOT.with_suffix(".csv.bak"))
    with SPOT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"merged {merged} of {len(export)} exported rows into {SPOT.name}")
    if unknown:
        print("not in spotcheck_gradeA.csv (skipped):", unknown)
    if bad:
        print("unrecognised owner_check values (skipped):", bad)


if __name__ == "__main__":
    main()
