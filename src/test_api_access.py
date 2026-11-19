"""Phase 0 access tests: one NASA POWER point request and one Overpass query.

Both hosts disallow /api/ in robots.txt. The project owner granted a written exception for these two
official public APIs on 2026-11-07, limited to one small request each. The exception lives here, not in
polite_fetch, so every other site remains subject to the robots check. No retries. No metrics computed.

Outputs: data/raw/nasa_power_ota_1990_2025.json, data/raw/osm_pilot_named_features.json,
data/interim/api_access_tests.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import _log, _session, _wait  # noqa: E402

LAT, LON = 6.68, 3.23  # Ota, Ogun State: approximate town-centre test point, not a facility location
POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
    f"?parameters=T2M,T2M_MAX,T2M_MIN,RH2M&community=AG&longitude={LON}&latitude={LAT}"
    "&start=19900101&end=20251231&format=JSON"
)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# One query for all pilot firms. Tags only, within Nigeria. Results are matched to facilities offline.
NAMES = ("Dangote|BUA|Lafarge|WAPCO|Nestl|Unilever|Nigerian Breweries|Guinness|International Breweries|"
         "Beta Glass|Okomu|Presco|Seplat|Flour Mills|Golden Penny|Cadbury|MTN Nigeria|Obajana|Ibese|Gboko|"
         "Ewekoro|Mfamosing|Ashaka|Kalambaina|Sokoto Cement|Obu Cement|Okpella")
OVERPASS_QUERY = f"""[out:json][timeout:90][maxsize:10000000];
area["ISO3166-1"="NG"][admin_level=2]->.ng;
(nwr(area.ng)["name"~"{NAMES}",i];
 nwr(area.ng)["operator"~"{NAMES}",i];
 nwr(area.ng)["brand"~"{NAMES}",i];);
out center tags;"""

summary = {}

_wait()
power = _session.get(POWER_URL, timeout=180)
_log(POWER_URL, str(power.status_code), "robots exception granted by project owner", len(power.content))
summary["nasa_power"] = {"status": power.status_code, "bytes": len(power.content)}
if power.status_code == 200:
    (ROOT / "data" / "raw" / "nasa_power_ota_1990_2025.json").write_bytes(power.content)
    payload = power.json()
    fill = payload.get("header", {}).get("fill_value")
    summary["nasa_power"].update(
        grid_point_returned=payload["geometry"]["coordinates"],
        api_version=payload.get("header", {}).get("api", {}).get("version"),
        sources=payload.get("header", {}).get("sources"),
        fill_value=fill,
        parameters={
            name: {"first": min(v), "last": max(v), "days": len(v), "fill_values": sum(x == fill for x in v.values())}
            for name, v in payload["properties"]["parameter"].items()
        },
    )

_wait()
osm = _session.post(OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=150)
_log(OVERPASS_URL, str(osm.status_code), "robots exception granted by project owner; POST, one query", len(osm.content))
summary["overpass"] = {"status": osm.status_code, "bytes": len(osm.content)}
if osm.status_code == 200:
    (ROOT / "data" / "raw" / "osm_pilot_named_features.json").write_bytes(osm.content)
    body = osm.json()
    summary["overpass"].update(elements=len(body.get("elements", [])), remark=body.get("remark"),
                               timestamp_osm_base=body.get("osm3s", {}).get("timestamp_osm_base"))

(ROOT / "data" / "interim" / "api_access_tests.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
