"""Phase 3, heat (design e3; OD-5, OD-6, OD-7).

NASA POWER daily point API under the owner's robots.txt exception for this service (docs/data_sources.md). The POWER
daily-API page asks for one request per 0.5 x 0.5 degree grid cell, so sites are grouped by 0.5-degree bin (cell
edges at multiples of 0.5 degrees: assumed, not verified) and one request is made at each bin centre, at least
6 s apart. Raw JSON responses are kept in data/raw/hazards/nasa_power/.

Metric (e3): for each site, the 90th percentile of daily T2M_MAX over 1991-2020 (all days pooled; the design says
"the site's own 90th percentile for 1991-2020"); annual count of days above it; score = mean annual count over
2020-2025 minus mean over 1991-2020. Exposure (OD-5): top tercile of main-set sites on that score, i.e.
score >= the 2/3 quantile (numpy linear) of main-set site scores. No heat-index threshold (OD-6).

Owner decision 2026-11-12: the robots.txt exception does NOT cover further NASA POWER requests (its robots.txt names
Anthropic agents). `fetch` is disabled. The 33 API files in data/raw/hazards/nasa_power/ are provisional and are to be
replaced by the owner's manual downloads (docs/nasa_manual_download.md) in data/raw/hazards/nasa_power_manual/.
Owner's manual downloads received 2026-11-12: 29 cells (every cell with a main-analysis site); `compare` found all 29 identical
to the API files. Heat is scored from the manual files (`score manual`). The owner did not download the 4 cells without a
main-analysis site (bins 10_15, 11_14, 12_15, 15_9); their sites are "not scored" and the API files are NOT used for them.
Native grid (file headers): MERRA-2, 0.5 deg lat x 0.625 deg lon - not the 0.5 x 0.5 deg grid the bins assume
(see docs/phase3_hazards.md, section 1.4).

A9 (2026-11-12): each site takes the MERRA-2 native cell that contains it (0.5 deg lat x 0.625 deg lon; centres at
-90 + 0.5*i, -180 + 0.625*j; half-open cells, edge ties go north/east). `cells2` writes the assignment
(data/interim/phase3_heat_cells_v2.csv) and the owner's download list (docs/nasa_manual_download_v2.md).

usage: phase3_heat.py score [api|manual] | compare | cells | cells2
"""
import csv
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import _log, _session  # noqa: E402

RAW = ROOT / "data" / "raw" / "hazards" / "nasa_power"
I = ROOT / "data" / "interim"
URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS_Q = "T2M_MAX,T2M_MIN,RH2M"
START, END = "19910101", "20251231"
BASE = (1991, 2020)
RECENT = (2020, 2025)


def bin_of(lat, lon):
    return math.floor(lat / 0.5), math.floor(lon / 0.5)


def bins():
    out = {}
    for r in csv.DictReader((ROOT / "data" / "processed" / "facilities.csv").open(newline="", encoding="utf-8")):
        if r["asset_type"] == "point" and r["lat"]:
            out.setdefault(bin_of(float(r["lat"]), float(r["lon"])), []).append(r["facility_id"])
    return out


MANUAL = ROOT / "data" / "raw" / "hazards" / "nasa_power_manual"
# owner decision 2026-11-12: cells with no main-analysis site were not downloaded; their sites are not scored
NOT_SCORED = "not scored — no owner download (office-only cell)"


def fetch():
    sys.exit("disabled: owner decision 2026-11-12 - no further NASA POWER requests (see docs/nasa_manual_download.md)")
    RAW.mkdir(parents=True, exist_ok=True)
    b = bins()
    print("sites", sum(len(v) for v in b.values()), "| distinct 0.5-degree bins", len(b), flush=True)
    for (bi, bj), ids in sorted(b.items()):
        f = RAW / f"bin_{bi}_{bj}.json"
        if f.exists():
            continue
        lat, lon = bi * 0.5 + 0.25, bj * 0.5 + 0.25
        time.sleep(6)
        resp = _session.get(URL, params={"parameters": PARAMS_Q, "community": "AG", "latitude": f"{lat:.2f}",
                                         "longitude": f"{lon:.2f}", "start": START, "end": END, "format": "JSON"}, timeout=180)
        _log(resp.url, str(resp.status_code), "Phase 3 NASA POWER daily point (owner robots.txt exception; one request per 0.5-degree cell)",
             len(resp.content))
        if resp.status_code == 200:
            f.write_bytes(resp.content)
        print(resp.status_code, f.name, len(resp.content), len(ids), "sites", flush=True)
        if resp.status_code in (401, 403, 429, 451):
            print("blocked or rate-limited: stopping"); break


def load_tmax(bi, bj, source):
    """{YYYYMMDD: value} of daily T2M_MAX for one bin, from the API JSON or the owner's manual file (CSV or JSON from the
    POWER Data Access Viewer, named bin_<i>_<j>.csv/.json). Returns (series, fill value) or (None, None)."""
    if source == "api":
        f = RAW / f"bin_{bi}_{bj}.json"
        if not f.exists():
            return None, None
        d = json.loads(f.read_text(encoding="utf-8"))
        return d["properties"]["parameter"]["T2M_MAX"], d.get("header", {}).get("fill_value", -999)
    for f in (MANUAL / f"bin_{bi}_{bj}.json", MANUAL / f"bin_{bi}_{bj}.csv"):
        if not f.exists():
            continue
        if f.suffix == ".json":
            d = json.loads(f.read_text(encoding="utf-8"))
            return d["properties"]["parameter"]["T2M_MAX"], d.get("header", {}).get("fill_value", -999)
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        start = next((i + 1 for i, l in enumerate(lines) if l.strip().startswith("-END HEADER-")), 0)
        rd = csv.DictReader(lines[start:])
        out = {}
        for row in rd:
            row = {k.strip(): v for k, v in row.items() if k}
            if "DOY" in row:
                import datetime as dt
                day = dt.date(int(row["YEAR"]), 1, 1) + dt.timedelta(days=int(row["DOY"]) - 1)
                key = day.strftime("%Y%m%d")
            else:
                key = f"{int(row['YEAR']):04d}{int(row['MO']):02d}{int(row['DY']):02d}"
            out[key] = float(row["T2M_MAX"])
        return out, -999.0
    return None, None


def compare():
    """Owner's manual files vs the provisional API files: maximum absolute daily difference per bin."""
    rows = []
    for (bi, bj), ids in sorted(bins().items()):
        a, _ = load_tmax(bi, bj, "api")
        m, _ = load_tmax(bi, bj, "manual")
        if m is None:
            rows.append({"bin": f"{bi}_{bj}", "status": "manual file missing"}); continue
        common = sorted(set(a) & set(m))
        diff = max((abs(a[k] - m[k]) for k in common), default=None)
        rows.append({"bin": f"{bi}_{bj}", "status": "compared", "days_common": len(common), "days_api": len(a), "days_manual": len(m),
                     "max_abs_diff_c": diff})
    for r in rows:
        print(r)
    print("bins matching exactly:", sum(1 for r in rows if r.get("max_abs_diff_c") == 0), "of", len(rows))


def cells():
    for (bi, bj), ids in sorted(bins().items()):
        print(f"bin_{bi}_{bj}", bi * 0.5 + 0.25, bj * 0.5 + 0.25, len(ids))


def score(source="api"):
    b = bins()
    per_bin = {}
    for (bi, bj), ids in b.items():
        tmax, fill = load_tmax(bi, bj, source)
        if tmax is None:
            continue
        days = [(k, v) for k, v in tmax.items() if v is not None and v != fill]
        yrs = np.array([int(k[:4]) for k, _ in days]); vals = np.array([v for _, v in days], dtype=float)
        base = vals[(yrs >= BASE[0]) & (yrs <= BASE[1])]
        p90 = float(np.percentile(base, 90))
        counts = {y: int((vals[yrs == y] > p90).sum()) for y in range(BASE[0], RECENT[1] + 1) if (yrs == y).any()}
        ndays = {y: int((yrs == y).sum()) for y in counts}
        bmean = float(np.mean([counts[y] for y in range(BASE[0], BASE[1] + 1)]))
        rec = [counts[y] for y in range(RECENT[0], RECENT[1] + 1) if y in counts]
        per_bin[(bi, bj)] = {"cell_lat": bi * 0.5 + 0.25, "cell_lon": bj * 0.5 + 0.25, "tx_p90_c": round(p90, 2),
                             "tx90_days_base_mean": round(bmean, 2), "tx90_days_recent_mean": round(float(np.mean(rec)), 2),
                             "heat_score": round(float(np.mean(rec)) - bmean, 2),
                             "recent_years_complete": all(ndays.get(y, 0) >= 365 for y in range(RECENT[0], RECENT[1] + 1)),
                             "missing_days": int(sum(1 for _, v in tmax.items() if v is None or v == fill))}
    rows = []
    for key, ids in b.items():
        for fid in ids:
            rows.append({"facility_id": fid, **per_bin.get(key, {"heat_score": ""})})
    for r in rows:
        if source == "api":
            r["heat_source"] = "NASA POWER API (provisional; to be replaced by owner manual download)"
        elif r.get("heat_score", "") == "":
            r["heat_source"] = NOT_SCORED
        else:
            r["heat_source"] = "NASA POWER Data Access Viewer, owner manual download"
    with (I / "phase3_heat.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = ["facility_id", "cell_lat", "cell_lon", "tx_p90_c", "tx90_days_base_mean", "tx90_days_recent_mean", "heat_score",
                "recent_years_complete", "missing_days", "heat_source"]
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print("heat rows", len(rows), "| bins with data", len(per_bin), "of", len(b))


# ---------------------------------------------------------------- A9: MERRA-2 native cells
MANUAL_V2 = ROOT / "data" / "raw" / "hazards" / "nasa_power_manual_v2"
DLAT, DLON = 0.5, 0.625


def native_cell(lat, lon):
    """(i, j) of the MERRA-2 native cell containing the point; centre = (-90 + 0.5 i, -180 + 0.625 j). Half-open cells
    [centre - half, centre + half): a point exactly on an edge goes to the cell to its north / east."""
    return math.floor((lat + 90 + DLAT / 2) / DLAT), math.floor((lon + 180 + DLON / 2) / DLON)


def cell_centre(i, j):
    return round(-90 + DLAT * i, 4), round(-180 + DLON * j, 4)


def power_name(lat, lon):
    """Expected Data Access Viewer file name. Verified for two-decimal coordinates (e.g. 004d75N_007d25E); the format
    for three-decimal longitudes such as 3.125 is not verified."""
    def part(v, h):
        txt = f"{abs(v):.3f}".rstrip("0")
        if len(txt.split(".")[1]) < 2:
            txt = f"{abs(v):.2f}"
        a, b = txt.split(".")
        return f"{int(a):03d}d{b}{h}"
    return f"POWER_Point_Daily_19910101_20251231_{part(lat, 'N')}_{part(lon, 'E')}_LST.csv"


def cells2():
    import phase3_hazards as H
    sites = H.load_sites()
    rows, cells = [], {}
    old_reqs = {(bi * 0.5 + 0.25, bj * 0.5 + 0.25) for bi, bj in bins()} | {(6.75, 7.0)}  # incl. owner's typo file
    for s in sites:
        i, j = native_cell(s["lat"], s["lon"])
        clat, clon = cell_centre(i, j)
        on_edge = any(abs(((v + 90 + DLAT / 2) / DLAT) % 1) < 1e-9 for v in [s["lat"]]) or             abs(((s["lon"] + 180 + DLON / 2) / DLON) % 1) < 1e-9
        rows.append({"facility_id": s["r"]["facility_id"], "ticker": s["r"]["ticker"], "site_set": s["set"],
                     "lat": s["lat"], "lon": s["lon"], "cell": f"m2_{i}_{j}", "cell_lat": clat, "cell_lon": clon,
                     "on_cell_edge": int(on_edge)})
        c = cells.setdefault((i, j), {"main": [], "office": [], "R2": [], "other": [], "tickers": set()})
        c[s["set"]].append(s["r"]["facility_id"])
        if s["set"] == "main":
            c["tickers"].add(s["r"]["ticker"])
    cols = list(rows[0])
    with (I / "phase3_heat_cells_v2.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(rows)
    dl = sorted(((k, v) for k, v in cells.items() if v["main"]), key=lambda kv: (-len(kv[1]["main"]), kv[0]))
    nodl = [(k, v) for k, v in cells.items() if not v["main"]]
    print("sites", len(rows), "| on a cell edge", sum(r["on_cell_edge"] for r in rows),
          "| native cells", len(cells), "| with a main site", len(dl), "| without", len(nodl))
    print("existing downloads at a native cell centre:",
          [k for k in old_reqs if native_cell(*k) and cell_centre(*native_cell(*k)) == k] or "none")
    return rows, cells, dl, nodl


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "score":
        score(sys.argv[2] if len(sys.argv) > 2 else "api")
    else:
        {"fetch": fetch, "compare": compare, "cells": cells, "cells2": cells2}[cmd]()
