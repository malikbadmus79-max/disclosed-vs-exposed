"""Phase 0: the second and final Overpass query, approved by the project owner on 2026-11-07.

The first query (test_api_access.py) timed out on the server. This one searches name tags only, is case
sensitive, and uses a short list of firm names. It does not retry and computes no metrics.

Outputs: data/raw/osm_pilot_named_features.json and an "overpass_narrow" entry in
data/interim/api_access_tests.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import _log, _session, _wait  # noqa: E402

URL = "https://overpass-api.de/api/interpreter"
NAMES = "Dangote|BUA|Lafarge|Guinness|Nigerian Breweries|International Breweries|Okomu|Presco|Seplat|Flour Mills|Cadbury|Nestl|Unilever|Beta Glass"
QUERY = f"""[out:json][timeout:170][maxsize:10000000];
area["ISO3166-1"="NG"][admin_level=2]->.ng;
nwr(area.ng)["name"~"{NAMES}"];
out center tags;"""

_wait()
resp = _session.post(URL, data={"data": QUERY}, timeout=200)
_log(URL, str(resp.status_code), "robots exception granted by project owner; POST, narrow query", len(resp.content))
result = {"status": resp.status_code, "bytes": len(resp.content), "query_names": NAMES}
if resp.status_code == 200:
    body = resp.json()
    elements = body.get("elements", [])
    result.update(elements=len(elements), remark=body.get("remark"),
                  timestamp_osm_base=body.get("osm3s", {}).get("timestamp_osm_base"))
    if body.get("remark") is None:
        (ROOT / "data" / "raw" / "osm_pilot_named_features.json").write_bytes(resp.content)

summary_path = ROOT / "data" / "interim" / "api_access_tests.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))
summary["overpass_narrow"] = result
summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
