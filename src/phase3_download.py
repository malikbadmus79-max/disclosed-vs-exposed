"""Phase 3: download hazard datasets named in the frozen design (e1-e4) and WorldPop (section i).

Each file is fetched once with the project's User-Agent, at least 6 s apart, streamed to disk, hashed (SHA-256) and
logged in data/interim/fetch_log.csv and data/interim/phase3_downloads.csv. Files already present with a recorded
hash are skipped. Big files live under data/raw/hazards/ (gitignored).

usage: phase3_download.py jrc | worldpop | url <URL> <dest relative to project root> <dataset label>
"""
import csv
import hashlib
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import _log, _session  # noqa: E402

MANIFEST = ROOT / "data" / "interim" / "phase3_downloads.csv"
JRC = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard"
JRC_TILES = ["ID117_N20_W0", "ID118_N10_W0", "ID125_N20_E10", "ID126_N10_E10"]  # tiles intersecting Nigeria (tile_extents.geojson)
WORLDPOP = ("https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/NGA/v1/100m/constrained/"
            "nga_pop_2025_CN_100m_R2025A_v1.tif")


def manifest():
    return {r["file"]: r for r in csv.DictReader(MANIFEST.open(encoding="utf-8"))} if MANIFEST.exists() else {}


def fetch(url: str, dest: Path, label: str) -> None:
    rows = manifest()
    rel = str(dest.relative_to(ROOT)).replace("\\", "/")
    if rel in rows and dest.exists() and rows[rel]["status"] == "200":
        print("skip (have)", rel, flush=True)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    time.sleep(6)
    h, n = hashlib.sha256(), 0
    with _session.get(url, stream=True, timeout=180) as r:
        status = str(r.status_code)
        lastmod = r.headers.get("Last-Modified", "")
        if r.status_code == 200:
            tmp = dest.with_suffix(dest.suffix + ".part")
            with tmp.open("wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk); h.update(chunk); n += len(chunk)
            tmp.replace(dest)
    _log(url, status, f"Phase 3 download: {label}", n)
    rows[rel] = {"dataset": label, "url": url, "file": rel, "status": status, "bytes": n,
                 "sha256": h.hexdigest() if n else "", "last_modified": lastmod,
                 "accessed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")}
    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(next(iter(rows.values()))))
        w.writeheader()
        w.writerows(rows.values())
    print(status, n, rel, flush=True)


def main() -> None:
    what = sys.argv[1]
    if what == "jrc":
        for rp in ("RP100", "RP10", "RP500"):
            for t in JRC_TILES:
                name = f"{t}_{rp}_depth.tif"
                fetch(f"{JRC}/{rp}/{name}", ROOT / "data" / "raw" / "hazards" / "jrc" / rp / name, f"JRC river flood v2.1.2 {rp}")
    elif what == "worldpop":
        fetch(WORLDPOP, ROOT / "data" / "raw" / "hazards" / "worldpop" / Path(WORLDPOP).name, "WorldPop Global2 R2025A NGA 2025 100m constrained")
    elif what == "url":
        fetch(sys.argv[2], ROOT / sys.argv[3], sys.argv[4])


if __name__ == "__main__":
    main()
