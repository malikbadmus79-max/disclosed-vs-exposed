"""Phase 3, heat (main) from ERA5 - amendment A10 (design e3, OD-5, OD-7).

Data: Copernicus Climate Data Store, "ERA5 post-processed daily statistics on single levels from 1940 to present"
(derived-era5-single-levels-daily-statistics, DOI 10.24381/cds.4991cf48, CC-BY-4.0). 2m_temperature, daily_maximum of
1-hourly values, time zone UTC+01:00 (West Africa Time), 1991-2025, area N14 W2.5 S4 E15, CDS default 0.25 deg grid.
One request per year (the form allows one year per request). Access through `cdsapi`, which reads the owner's key from
~/.cdsapirc; this script never reads or prints that file.

Cell rule (A10): each site takes the nearest 0.25 deg grid point (cell = point +/- 0.125 deg); an exact edge goes north/east.
Metric (e3, unchanged): per cell, 90th percentile of all daily maxima 1991-2020 pooled; score = mean annual exceedance
days 2020-2025 minus mean 1991-2020. Exposure (OD-5) is applied in phase3_firms.py (top tercile of main-set sites).

usage: phase3_era5.py download [year ...] | inspect | score

A11 (2026-11-17): `score` now reads the 43 hourly point files in data/raw/hazards/era5_timeseries/ through
phase3_era5_ts.daily_max (same local-day maximum); `download` and `inspect` concern the A10 yearly files only.
"""
import csv
import hashlib
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import _log  # noqa: E402

RAW = ROOT / "data" / "raw" / "hazards" / "era5"
I = ROOT / "data" / "interim"
DATASET = "derived-era5-single-levels-daily-statistics"
AREA = [14, 2.5, 4, 15]  # N, W, S, E
YEARS = list(range(1991, 2026))
BASE, RECENT = (1991, 2020), (2020, 2025)
RES = 0.25


def request(year):
    return {"product_type": "reanalysis", "variable": ["2m_temperature"], "year": str(year),
            "month": [f"{m:02d}" for m in range(1, 13)], "day": [f"{d:02d}" for d in range(1, 32)],
            "daily_statistic": "daily_maximum", "time_zone": "utc+01:00", "frequency": "1_hourly", "area": AREA}


def download(years):
    import cdsapi
    RAW.mkdir(parents=True, exist_ok=True)
    c = cdsapi.Client(quiet=True, progress=False)
    for y in years:
        f = RAW / f"era5_t2m_dailymax_utc+01_{y}.nc"
        if f.exists():
            continue
        t0 = time.time()
        try:
            res = c.retrieve(DATASET, request(y))
            tmp = f.with_suffix(".part")
            res.download(str(tmp))
            tmp.rename(f)
            _log(f"https://cds.climate.copernicus.eu/api/retrieve/v1/processes/{DATASET} year={y}", "200",
                 "Phase 3 A10 ERA5 daily max 2m temperature (cdsapi; owner account)", f.stat().st_size)
            print(y, "ok", f.stat().st_size, f"{time.time() - t0:.0f}s", flush=True)
        except Exception as e:  # report, do not retry blindly
            _log(f"https://cds.climate.copernicus.eu/api/retrieve/v1/processes/{DATASET} year={y}", "error",
                 f"Phase 3 A10 ERA5: {type(e).__name__}: {str(e)[:200]}")
            print(y, "FAILED", type(e).__name__, str(e)[:300], flush=True)
            break


def read_year(f):
    """(dates as YYYYMMDD strings, lats, lons, data[t, lat, lon] in deg C) from one yearly netCDF via GDAL."""
    import rasterio
    with rasterio.open(f) as ds:
        subs = ds.subdatasets or [None]
    sub = next((s for s in subs if s and s.endswith(":t2m")), None) or f"netcdf:{f}:t2m"
    with rasterio.open(sub) as ds:
        arr = ds.read().astype("float64")
        tags = ds.tags()
        nodata = ds.nodata
        tr = ds.transform
        lons = np.array([tr.c + tr.a * (k + 0.5) for k in range(ds.width)])
        lats = np.array([tr.f + tr.e * (k + 0.5) for k in range(ds.height)])
        bandtags = [ds.tags(b + 1) for b in range(ds.count)]
    scale = float(tags.get("t2m#scale_factor", 1)); off = float(tags.get("t2m#add_offset", 0))
    fill = tags.get("t2m#_FillValue")
    bad = np.zeros(arr.shape, bool)
    for v in (nodata, fill):
        if v is not None:
            bad |= arr == float(v)
    arr = arr * scale + off
    arr[bad] = np.nan
    units = tags.get("t2m#units", "")
    if units.strip().upper() == "K":
        arr = arr - 273.15
    tunits = tags.get("valid_time#units") or tags.get("time#units") or ""
    import datetime as dt
    origin = dt.datetime.fromisoformat(tunits.split("since")[1].strip().replace(" ", "T")[:19]) if "since" in tunits else None
    step = {"days": 86400, "hours": 3600, "seconds": 1}[tunits.split()[0]] if origin else None
    dates = []
    for bt in bandtags:
        v = bt.get("NETCDF_DIM_valid_time") or bt.get("NETCDF_DIM_time")
        dates.append((origin + dt.timedelta(seconds=float(v) * step)).strftime("%Y%m%d"))
    return dates, lats, lons, arr, units, tunits


def inspect():
    for f in sorted(RAW.glob("*.nc")):
        d, la, lo, a, u, tu = read_year(f)
        print(f.name, a.shape, d[0], d[-1], len(set(d)), "| lat", la[0], la[-1], "| lon", lo[0], lo[-1], "| units", u, "|", tu,
              "| nan", int(np.isnan(a).sum()), "| range", round(float(np.nanmin(a)), 2), round(float(np.nanmax(a)), 2))


def cell_of(lat, lon):
    """Nearest 0.25-degree grid point; exact edges (x.125, x.375, ...) go north/east."""
    return math.floor(lat / RES + 0.5) * RES, math.floor(lon / RES + 0.5) * RES


def score():
    import phase3_hazards as H
    sites = H.load_sites()
    import phase3_era5_ts as T  # A11: hourly point series -> local-day (UTC+01:00) maximum
    cells = {}
    for s in sites:
        cells.setdefault(cell_of(s["lat"], s["lon"]), []).append(s)
    missing = [k for k in cells if not T.fname(*k).exists()]
    if missing:
        sys.exit(f"missing ERA5 point files: {missing}")
    series = {}
    for (clat, clon) in sorted(cells):
        dm, meta = T.daily_max(clat, clon)
        assert abs(meta["latitude"] - clat) < 1e-6 and abs(meta["longitude"] - clon) < 1e-6, (clat, clon, meta)
        series[(clat, clon)] = {d.strftime("%Y%m%d"): float(v) for d, v in dm["max"].items()}
    per = {}
    for k, ser in series.items():
        days = sorted(ser)
        yrs = np.array([int(x[:4]) for x in days]); vals = np.array([ser[x] for x in days])
        ok = ~np.isnan(vals)
        base = vals[ok & (yrs >= BASE[0]) & (yrs <= BASE[1])]
        p90 = float(np.percentile(base, 90))
        counts = {y: int((vals[ok & (yrs == y)] > p90).sum()) for y in YEARS}
        nd = {y: int((ok & (yrs == y)).sum()) for y in YEARS}
        bm = float(np.mean([counts[y] for y in range(BASE[0], BASE[1] + 1)]))
        rm = float(np.mean([counts[y] for y in range(RECENT[0], RECENT[1] + 1)]))
        per[k] = {"era5_cell_lat": k[0], "era5_cell_lon": k[1], "tx_p90_c": round(p90, 2), "tx90_days_base_mean": round(bm, 2),
                  "tx90_days_recent_mean": round(rm, 2), "heat_score": round(rm - bm, 2),
                  "days_total": int(ok.sum()), "missing_days": int((~ok).sum()),
                  "years_incomplete": ";".join(str(y) for y in YEARS if nd[y] < (366 if y % 4 == 0 else 365))}
    out = []
    for k, ss in cells.items():
        for s in ss:
            out.append({"facility_id": s["r"]["facility_id"], "site_set": s["set"], **per[k],
                        "heat_source": "ERA5 hourly time series, CDS (A11)"})
    cols = list(out[0])
    with (I / "phase3_heat_era5.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(sorted(out, key=lambda r: r["facility_id"]))
    print("sites", len(out), "| ERA5 cells", len(cells), "| main-site cells", len({cell_of(s['lat'], s['lon']) for s in sites if s['set'] == 'main'}),
          "| incomplete years", sorted({r["years_incomplete"] for r in out}))


def hashes():
    rows = []
    for f in sorted(RAW.glob("*.nc")):
        rows.append({"file": f.name, "bytes": f.stat().st_size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()})
    with (I / "phase3_era5_files.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["file", "bytes", "sha256"]); w.writeheader(); w.writerows(rows)
    print(len(rows), "files hashed")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "download":
        download([int(a) for a in sys.argv[2:]] or YEARS)
    else:
        {"inspect": inspect, "score": score, "hashes": hashes}[cmd]()
