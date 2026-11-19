"""Phase 0: point owner-supplied inventory rows at the copies inside data/raw/manual/<firm>/ subfolders.

Checks each loose file in data/raw/manual/ against the subfolder copies by SHA-256 and lists duplicates.
Deletes nothing: the owner removes loose duplicates.
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import download_pilot as dp  # noqa: E402

MANUAL = ROOT / "data" / "raw" / "manual"
SUB = {("mtn_nigeria", "2025", "AR"): "mtn/MTN-Nigeria-2025-Annual-Report.pdf",
       ("mtn_nigeria", "2025", "SR"): "mtn/MTN-Nigeria-2025-Sustainability-Report-Final.pdf",
       ("nestle_nigeria", "2025", "AR"): "nestle/Nestle_Nigeria_2025_Annual_Report.pdf",
       ("unilever_nigeria", "2025", "AR"): "unilever/Unilever_Nigeria_2025_Annual_Report.pdf",
       ("nigerian_breweries", "2025", "AR"): "nigerian_breweries/Nigerian_Breweries_2025_Annual_Report.pdf",
       ("seplat_energy", "2025", "IAR"): "seplat/Seplat_2025_Integrated_Annual_Report.pdf"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


sub_hashes = {sha(p): p for p in MANUAL.rglob("*") if p.is_file() and p.parent != MANUAL}
print("Loose files in data/raw/manual/:")
for p in sorted(x for x in MANUAL.iterdir() if x.is_file()):
    h = sha(p)
    twin = sub_hashes.get(h)
    print(f"  {p.name} | {'DUPLICATE of ' + str(twin.relative_to(MANUAL)) if twin else 'NO identical copy in a subfolder'}")

rows = dp.load_inventory()
for key, rel in SUB.items():
    path = MANUAL / rel
    h = sha(path)
    old = rows[key]
    same = "same content as before" if old.get("sha256") == h else "CONTENT DIFFERS from the file measured earlier"
    old["file"] = str(path.relative_to(ROOT)).replace("\\", "/")
    print(f"{key}: -> {old['file']} ({same})")
    if old.get("sha256") != h:
        old.update(sha256=h, bytes=path.stat().st_size, **dp.measure(path))
dp.save_inventory(rows)
