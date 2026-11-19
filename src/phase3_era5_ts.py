"""Phase 3, heat (main) from ERA5 hourly point time series - amendment A11 (method of A10 unchanged).

Data: Copernicus Climate Data Store, "ERA5 hourly time-series data on single levels from 1940 to present"
(reanalysis-era5-single-levels-timeseries, CC-BY-4.0). 2m_temperature, 1991-01-01 to 2025-12-31 (UTC), one request per
ERA5 0.25 deg grid point, requested at the exact grid-point coordinates (A10 cell rule picks the point for each site).
Access through `cdsapi`, which reads the owner's key from ~/.cdsapirc; this script never reads or prints that file.

Daily maximum (A10/A11): hourly UTC timestamps shifted to UTC+01:00 (West Africa Time); max of the hourly values per
local calendar day. Raw files: data/raw/hazards/era5_timeseries/point_<lat>_<lon>.csv (as delivered by the CDS).

usage: phase3_era5_ts.py points | download [N|all] | daily <lat> <lon> | crosscheck <lat> <lon> | hashes
"""
import hashlib
import io
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import _log  # noqa: E402
from phase3_era5 import cell_of, read_year, RAW as RAW_DS  # noqa: E402

RAW = ROOT / "data" / "raw" / "hazards" / "era5_timeseries"
DATASET = "reanalysis-era5-single-levels-timeseries"
DATE = "1991-01-01/2025-12-31"
URL = f"https://cds.climate.copernicus.eu/api/retrieve/v1/processes/{DATASET}"


def points():
    s = pd.read_csv(ROOT / "data" / "processed" / "site_hazards.csv")
    cells = sorted({cell_of(a, b) for a, b in zip(s.lat, s.lon)})
    return cells


def fname(lat, lon):
    return RAW / f"point_{lat:.2f}_{lon:.2f}.csv"


def request(lat, lon):
    return {"variable": ["2m_temperature"], "location": {"latitude": lat, "longitude": lon},
            "date": [DATE], "data_format": "csv"}


def _to_csv_bytes(path):
    """The CDS may deliver a zip holding one CSV; store the CSV itself."""
    b = path.read_bytes()
    if b[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            assert len(names) == 1, z.namelist()
            return z.read(names[0])
    return b


def _transient(e):
    import requests
    if isinstance(e, (requests.ConnectionError, requests.Timeout, ConnectionError, TimeoutError)):
        return True
    r = getattr(e, "response", None)
    code = getattr(r, "status_code", None)
    return code is not None and (code >= 500 or code == 429)


def download_one(c, lat, lon, tries=5):
    f = fname(lat, lon)
    if f.exists():
        return "skip", 0, 0.0
    t0 = time.time()
    for k in range(1, tries + 1):
        try:
            res = c.retrieve(DATASET, request(lat, lon))
            tmp = f.with_suffix(".part")
            res.download(str(tmp))
            f.write_bytes(_to_csv_bytes(tmp))
            tmp.unlink()
            _log(f"{URL} lat={lat} lon={lon}", "200", "Phase 3 A11 ERA5 hourly 2m temperature point series (cdsapi; owner account)",
                 f.stat().st_size)
            return "ok", f.stat().st_size, time.time() - t0
        except Exception as e:
            _log(f"{URL} lat={lat} lon={lon}", "error", f"Phase 3 A11 ERA5 ts try {k}: {type(e).__name__}: {str(e)[:200]}")
            if k < tries and _transient(e):
                print(f"  retry {k} after {type(e).__name__}: {str(e)[:150]}", flush=True)
                time.sleep(30 * k)
                continue
            raise


def download(n):
    import cdsapi
    RAW.mkdir(parents=True, exist_ok=True)
    c = cdsapi.Client(quiet=True, progress=False)
    todo = [p for p in points() if not fname(*p).exists()]
    print(f"{len(points())} points, {len(todo)} to download", flush=True)
    for lat, lon in todo[:n]:
        st, size, dt = download_one(c, lat, lon)
        print(f"{lat:.2f} {lon:.2f} {st} {size} bytes {dt:.0f}s", flush=True)


def read_hourly(lat, lon):
    f = fname(lat, lon)
    d = pd.read_csv(f, comment="#")
    tcol = next(c for c in d.columns if c.lower() in ("valid_time", "time", "date"))
    vcol = next(c for c in d.columns if c.lower() in ("t2m", "2m_temperature"))
    t = pd.DatetimeIndex(pd.to_datetime(d[tcol], utc=True))
    v = d[vcol].astype(float)
    if v.mean() > 150:  # Kelvin
        v = v - 273.15
    meta = {c: d[c].iloc[0] for c in d.columns if c.lower() in ("latitude", "longitude", "lat", "lon")}
    return pd.Series(v.values, index=t), meta


def daily_max(lat, lon):
    s, meta = read_hourly(lat, lon)
    local = s.index.tz_convert("Etc/GMT-1")  # UTC -> fixed UTC+01:00 (WAT, no DST; POSIX sign is inverted)
    g = pd.Series(s.values, index=local.tz_localize(None).normalize())
    dm = g.groupby(level=0).agg(["max", "count"])
    dm = dm[(dm.index.year >= 1991) & (dm.index.year <= 2025)]  # drops the 1-hour local day 2026-01-01
    return dm, meta


def crosscheck(lat, lon):
    dm, meta = daily_max(lat, lon)
    print("served point:", meta)
    out = []
    for y in (1991, 2025):
        dates, la, lo, a, *_ = read_year(RAW_DS / f"era5_t2m_dailymax_utc+01_{y}.nc")
        ii = int(np.argmin(np.abs(la - lat))); jj = int(np.argmin(np.abs(lo - lon)))
        assert abs(la[ii] - lat) < 1e-6 and abs(lo[jj] - lon) < 1e-6
        g = pd.Series(a[:, ii, jj], index=pd.to_datetime(dates))
        j = pd.concat([dm["max"].rename("ts"), dm["count"].rename("n"), g.rename("grid")], axis=1, join="inner")
        d = (j.ts - j.grid).abs()
        print(f"{y}: days {len(j)}, max|diff| {d.max():.4f} C on {d.idxmax().date()} (hours {j.n[d.idxmax()]}), "
              f"mean|diff| {d.mean():.4f} C, mean diff (ts-grid) {(j.ts - j.grid).mean():+.4f}", flush=True)
        out.append(d)
    a = pd.concat(out)
    print(f"1991+2025: max|diff| {a.max():.4f} C, mean|diff| {a.mean():.4f} C")


def hashes():
    for f in sorted(RAW.glob("point_*.csv")):
        print(f.name, f.stat().st_size, hashlib.sha256(f.read_bytes()).hexdigest())


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "points"
    if cmd == "points":
        p = points(); print(len(p)); [print(f"{a:.2f} {b:.2f}") for a, b in p]
    elif cmd == "download":
        a = sys.argv[2] if len(sys.argv) > 2 else "1"
        download(10 ** 6 if a == "all" else int(a))
    elif cmd == "one":
        import cdsapi
        RAW.mkdir(parents=True, exist_ok=True)
        lat, lon = float(sys.argv[2]), float(sys.argv[3])
        assert (lat, lon) in points()
        st, size, dt = download_one(cdsapi.Client(quiet=True, progress=False), lat, lon)
        print(f"{lat:.2f} {lon:.2f} {st} {size} bytes {dt:.1f}s")
    elif cmd == "daily":
        dm, meta = daily_max(float(sys.argv[2]), float(sys.argv[3]))
        print(meta); print(dm.head(3)); print(dm.tail(3)); print("days", len(dm), "| hour counts", dm["count"].value_counts().to_dict())
    elif cmd == "crosscheck":
        crosscheck(float(sys.argv[2]), float(sys.argv[3]))
    elif cmd == "hashes":
        hashes()
