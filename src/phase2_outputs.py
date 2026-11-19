"""Phase 2, Tasks 6-7: write facilities.geojson, spotcheck_gradeA.csv and sites_map.html from facilities.csv.

No hazard data are used. OSM-derived coordinates: (c) OpenStreetMap contributors, ODbL.
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
rows = list(csv.DictReader((P / "facilities.csv").open(newline="", encoding="utf-8")))

features = []
for r in rows:
    if not r["lat"]:
        continue
    props = {k: v for k, v in r.items() if k not in ("lat", "lon")}
    features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(r["lon"]), float(r["lat"])]},
                     "properties": props})
geo = {"type": "FeatureCollection", "name": "facilities_phase2",
       "attribution": "Coordinates from OpenStreetMap (c) OpenStreetMap contributors, ODbL; locations as written in company reports",
       "features": features}
(P / "facilities.geojson").write_text(json.dumps(geo, ensure_ascii=False, indent=1), encoding="utf-8")

import sys
sys.path.insert(0, str(ROOT / "src"))
from a6_crosscheck import COMMENT as A6_COMMENT  # noqa: E402
# Keep any owner checks already entered, matched by facility_id, so a rebuild never erases them
OWNER_COLS = ("owner_check (ok / wrong / move-to)", "owner_comment", "owner_lat", "owner_lon", "checked_at")  # last three: from merge_spotcheck.py
prev = {}
if (P / "spotcheck_gradeA.csv").exists():
    prev = {r["facility_id"]: r for r in csv.DictReader((P / "spotcheck_gradeA.csv").open(newline="", encoding="utf-8"))}
spot = []
for r in rows:
    if r["rating"] != "A":
        continue
    link = (f"https://www.openstreetmap.org/?mlat={r['lat']}&mlon={r['lon']}#map=16/{r['lat']}/{r['lon']}" if r["lat"] else "")
    spot.append({"facility_id": r["facility_id"], "ticker": r["ticker"], "facility": r["facility"], "is_office": r["is_office"],
                 "source_doc": r["source_doc"], "pdf_page": r["pdf_page"], "report_quote": r["location_as_written"],
                 "lat": r["lat"], "lon": r["lon"], "coord_method": r["coord_method"], "coord_source": r["coord_source"],
                 "coord_precision_m": r["coord_precision_m"], "state_check": r["state_check"], "osm_link": link,
                 **{c: prev.get(r["facility_id"], {}).get(c, "") for c in OWNER_COLS},
                 "a6_check": r["a6_check"], "buffer_m": r["buffer_m"]})
    # A6: the rule-based label fills the owner columns unless a manual owner entry (not from A6) is already there
    s_ = spot[-1]
    if not s_[OWNER_COLS[0]] or s_[OWNER_COLS[1]] == A6_COMMENT:
        s_[OWNER_COLS[0]], s_[OWNER_COLS[1]] = r["a6_check"], A6_COMMENT
with (P / "spotcheck_gradeA.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, list(spot[0]))
    w.writeheader()
    w.writerows(spot)

html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phase 2 sites</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
 :root { --bg:#ffffff; --fg:#1b1b1b; --muted:#555; --panel:#f4f4f4; }
 @media (prefers-color-scheme: dark) { :root { --bg:#151515; --fg:#eaeaea; --muted:#aaa; --panel:#222; } }
 html,body { margin:0; height:100%; background:var(--bg); color:var(--fg); font:14px/1.4 system-ui,sans-serif; }
 header { padding:10px 16px; background:var(--panel); }
 header p { margin:4px 0 0; color:var(--muted); font-size:12px; }
 #map { height:calc(100% - 78px); }
 .k span { display:inline-block; width:10px; height:10px; border-radius:50%; margin:0 4px 0 10px; }
</style></head><body>
<header><strong>Phase 2 facility locations (for owner review)</strong>
<span class="k"><span style="background:#1a7f37"></span>A <span style="background:#d4a017"></span>B <span style="background:#c0392b"></span>C/D</span>
<p>Points are OSM feature or place centroids, not surveyed sites; circle size shows nominal precision. No hazard data shown.
Map data &copy; OpenStreetMap contributors (ODbL).</p></header>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const data = __DATA__;
const map = L.map('map').setView([8.5, 7.5], 6);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
const col = g => g === 'A' ? '#1a7f37' : g === 'B' ? '#d4a017' : '#c0392b';
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
for (const f of data.features) {
  const p = f.properties, [lon, lat] = f.geometry.coordinates;
  L.circle([lat, lon], {radius: Number(p.coord_precision_m) || 1000, color: col(p.rating), weight: 1, fillOpacity: 0.15}).addTo(map);
  L.circleMarker([lat, lon], {radius: 5, color: col(p.rating), fillOpacity: 0.9}).addTo(map)
   .bindPopup(`<b>${esc(p.ticker)}: ${esc(p.facility)}</b><br>Grade ${esc(p.rating)} | ${esc(p.asset_type)}${p.is_office === 'yes' ? ' | office' : ''}<br>`
    + `<i>${esc(p.location_as_written)}</i><br>${esc(p.source_doc)} p.${esc(p.pdf_page)}<br>${esc(p.coord_method)}: ${esc(p.coord_source)}<br>State check: ${esc(p.state_check)}`);
}
</script></body></html>"""
(P / "sites_map.html").write_text(html.replace("__DATA__", json.dumps(geo, ensure_ascii=False)), encoding="utf-8")

print("manual owner checks carried over:", sum(1 for v in prev.values() if v.get(OWNER_COLS[0]) and v.get(OWNER_COLS[1]) != A6_COMMENT),
      "| A6 labels:", dict(__import__("collections").Counter(x["a6_check"] for x in spot)))
print("features with coordinates:", len(features), "of", len(rows), "| grade-A spot-check rows:", len(spot),
      "| grade-A with coordinates:", sum(1 for s in spot if s["lat"]))
op = [r for r in rows if r["is_office"] == "no"]
print("grades (all):", dict(Counter(r["rating"] for r in rows)), "| operational:", dict(Counter(r["rating"] for r in op)))
print("asset types (operational):", dict(Counter(r["asset_type"] for r in op)))
print("strata:", dict(Counter(r["census_stratum"] for r in rows)))
print("coord methods:", dict(Counter(r["coord_method"] or "none" for r in rows)))
st = Counter((r["osm_state"] or "").replace(" State", "") for r in op if r["lat"])
print("OSM state of operational sites with coordinates:", dict(sorted(st.items(), key=lambda x: -x[1])))
