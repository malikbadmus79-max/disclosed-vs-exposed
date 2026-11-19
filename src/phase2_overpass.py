"""Phase 2, Task 4: small Overpass queries for coordinates (OD-1: OSM features and stated addresses only).

Overpass robots.txt disallows /api/; the owner authorised use within the Overpass usage policy in small
queries (Phase 2 brief, 2026-11-07). Each query runs once, at least 10 s apart, with no retries.
Outputs (ODbL, (c) OpenStreetMap contributors): data/raw/osm_phase2/{places,features,states}.json

usage: phase2_overpass.py places|features|states
"""
import csv
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import _log, _session  # noqa: E402

import os
# Owner decision 2026-11-12: one alternative public instance listed on the OSM wiki "Overpass API" page may be used.
URL = os.environ.get("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
RAW = ROOT / "data" / "raw" / "osm_phase2"
FAC = ROOT / "data" / "interim" / "phase2_facilities_nocoords.csv"
NAMES_FEATURES = ("Dangote Sugar|FTN Cocoa|Conoil|NASCON|Nascon|Vitafoam|Neimeth|Cutix|Berger Paints|PZ Cussons|"
                  "May & Baker|May and Baker|Morison|Honeywell|Transcorp|ABC Transport|Briscoe|Qua Iboe|Seplat|MTN Plaza|"
                  "Nigerian Breweries|Nestle|Nestlé|Unilever|Guinness|Beta Glass|Lafarge|Ashakacem|Okomu|Presco")


def run(query: str, name: str) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    time.sleep(10)
    resp = _session.post(URL, data={"data": query}, timeout=200)
    _log(URL, str(resp.status_code), f"Phase 2 Overpass query '{name}' at {URL} (owner-authorised; no retry)", len(resp.content))
    (RAW / f"{name}.json").write_bytes(resp.content)
    try:
        body = resp.json()
        print(name, resp.status_code, "elements:", len(body.get("elements", [])), "remark:", body.get("remark"))
    except ValueError:
        print(name, resp.status_code, "non-JSON response:", resp.text[:300])


def main() -> None:
    which = sys.argv[1]
    if which == "places":
        with FAC.open(newline="", encoding="utf-8") as f:
            places = sorted({r["geocode_place"] for r in csv.DictReader(f) if r["geocode_place"]})
        rx = "|".join(re.escape(p) for p in places)
        q = f"""[out:json][timeout:120];
area["ISO3166-1"="NG"][admin_level=2]->.ng;
(node(area.ng)["place"]["name"~"^({rx})$"];
 way(area.ng)["place"]["name"~"^({rx})$"];
 relation(area.ng)["place"]["name"~"^({rx})$"];);
out center tags;"""
        run(q, "places")
    elif which == "features":
        q = f"""[out:json][timeout:150];
area["ISO3166-1"="NG"][admin_level=2]->.ng;
nwr(area.ng)["name"~"{NAMES_FEATURES}"];
out center tags;"""
        run(q, "features")
    elif which in ("places2", "places3"):  # supplementary place names: phase2_overpass.py places3 Name1,Name2
        rx = "|".join(re.escape(p) for p in sys.argv[2].split(","))
        run(f"""[out:json][timeout:90];
area["ISO3166-1"="NG"][admin_level=2]->.ng;
(node(area.ng)["place"]["name"~"^({rx})$"]; way(area.ng)["place"]["name"~"^({rx})$"];);
out center tags;""", which)
    elif which in ("states_check2", "states_check3"):  # only points not covered by earlier state checks
        pts = json.loads((RAW / f"{which}_index.json").read_text(encoding="utf-8"))
        stmts = "\n".join(f'is_in({lat},{lon})->.a{i}; area.a{i}[admin_level=4]; '
                          f'make st idx="{i}",state=set(t["name"]); out;' for i, (_, lat, lon) in enumerate(pts))
        run(f"[out:json][timeout:120];\n{stmts}", which)
    elif which == "states_check":  # one point per assigned facility (smaller than the 'states' query)
        pts = json.loads((RAW / "states_check_index.json").read_text(encoding="utf-8"))
        stmts = "\n".join(f'is_in({lat},{lon})->.a{i}; area.a{i}[admin_level=4]; '
                          f'make st idx="{i}",state=set(t["name"]); out;' for i, (_, lat, lon) in enumerate(pts))
        run(f"[out:json][timeout:170];\n{stmts}", "states_check")
    elif which == "states":
        pts = []
        for fname in ("places", "features"):
            body = json.loads((RAW / f"{fname}.json").read_text(encoding="utf-8"))
            for e in body["elements"]:
                c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
                if c.get("lat") is not None:
                    pts.append((f"{e['type']}/{e['id']}", c["lat"], c["lon"]))
        # `make` emits exactly one element per point, tagged with its index, so empty results cannot misalign
        stmts = "\n".join(f'is_in({lat},{lon})->.a{i}; area.a{i}[admin_level=4]; '
                          f'make st idx="{i}",state=set(t["name"]); out;' for i, (_, lat, lon) in enumerate(pts))
        (RAW / "states_index.json").write_text(json.dumps(pts), encoding="utf-8")
        run(f"[out:json][timeout:170];\n{stmts}", "states")


if __name__ == "__main__":
    main()
