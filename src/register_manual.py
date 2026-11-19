"""Phase 0: add owner-supplied PDFs in data/raw/manual/ to the inventory with the same extractability checks.

Files were downloaded manually by the project owner; their original source URL is recorded where known.
Supplied files that were requested but are absent are recorded as "not tested — file not supplied".
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import download_pilot as dp  # noqa: E402

MANUAL = ROOT / "data" / "raw" / "manual"
# (firm, fiscal year, type, file name or None if not supplied, note on provenance)
SUPPLIED = [
    ("mtn_nigeria", 2025, "AR", "mtn/MTN-Nigeria-2025-Annual-Report.pdf",
     "owner browser download 2026-11-07: https://www.mtn.ng/wp-content/uploads/2026/05/MTN-Nigeria-2025-Annual-Report.pdf"),
    ("mtn_nigeria", 2025, "SR", "mtn/MTN-Nigeria-2025-Sustainability-Report-Final.pdf",
     "owner browser download 2026-11-07: https://www.mtn.ng/wp-content/uploads/2026/04/MTN-Nigeria-2025-Sustainability-Report-Final.pdf"),
    ("nestle_nigeria", 2025, "AR", "nestle/Nestle_Nigeria_2025_Annual_Report.pdf",
     "owner browser download 2026-11-07: https://www.nestle-cwa.com/en/investors/nigeria"),
    ("unilever_nigeria", 2025, "AR", "unilever/Unilever_Nigeria_2025_Annual_Report.pdf",
     "owner browser download 2026-11-07: https://africanfinancials.com/document/ng-unilev-2025-ar-00/"),
    ("nigerian_breweries", 2025, "AR", "nigerian_breweries/Nigerian_Breweries_2025_Annual_Report.pdf",
     "owner browser download 2026-11-07: https://www.nbplc.com/investor-relations/financial-reports/"),
    ("seplat_energy", 2025, "IAR", "seplat/Seplat_2025_Integrated_Annual_Report.pdf",
     "owner browser download 2026-11-07: https://www.seplatenergy.com/investors/results-and-presentations/"),
    ("seplat_energy", 2023, "SR", None, "requested from owner"),
    ("seplat_energy", 2025, "SPR", None, "requested from owner (Social Performance Report)"),
]
PENDING = "pending — owner to supply before Phase 6"


def main() -> None:
    rows = dp.load_inventory()
    for firm, year, kind, name, note in SUPPLIED:
        key = (firm, str(year), kind)
        old = rows.get(key, {})
        row = {"firm": firm, "fiscal_year": year, "type": kind, "host_class": "manual", "url": note}
        path = MANUAL / name if name else None
        if path is None or not path.exists():
            row["status"] = PENDING
        else:
            data = path.read_bytes()
            row.update(status="ok", file=str(path.relative_to(ROOT)).replace("\\", "/"), bytes=len(data),
                       sha256=hashlib.sha256(data).hexdigest())
            if data[:4] != b"%PDF":
                row["status"] = "not_a_pdf"
            else:
                try:
                    row.update(dp.measure(path))
                except Exception as exc:
                    row["status"] = f"parse_error:{type(exc).__name__}"
        rows[key] = row
        dp.save_inventory(rows)
        print(*key, row["status"], row.get("pages"), row.get("extractability"), "|", row.get("first_text", "")[:110])


if __name__ == "__main__":
    main()
