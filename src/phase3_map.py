"""Phase 3: data/processed/hazard_map.html - scored point sites with their main buffers, coloured by river-flood (RP100)
and heat exposure. Leaflet 1.9.4 from unpkg; OSM tiles. Map data (c) OpenStreetMap contributors (ODbL); flood
hazard (c) European Union, JRC; heat from ERA5 (A10 method, A11 hourly time series; Copernicus C3S, CC BY 4.0), NASA POWER as robustness.

usage: phase3_map.py
"""
import csv
import json
import sys
from pathlib import Path

from shapely.geometry import mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import phase3_hazards as H  # noqa: E402

KEEP = ["facility_id", "ticker", "facility", "rating", "site_set", "buffer_main", "rf100_exposed", "rf100_share", "rf100_maxdepth_m",
        "rf100_rob_exposed", "rf10_exposed", "rf500_exposed", "rf100_exposed_ge0.5m", "heat_score", "heat_exposed",
        "heat_nasa_score", "heat_nasa_exposed",
        "pop_within_5km", "coastal_rp100_exposed", "coastal_rp100_maxdepth_m", "water_stress_cat", "water_stress_label",
        "water_stress_exposed", "rf100_nopermwater_exposed"]


def main() -> None:
    rows = {r["facility_id"]: r for r in csv.DictReader((H.P / "site_hazards.csv").open(newline="", encoding="utf-8"))}
    feats = []
    for s in H.load_sites():
        r = rows.get(s["r"]["facility_id"])
        if not r:
            continue
        props = {k: r.get(k, "") for k in KEEP}
        g = s["g_main"].simplify(0.0002)
        feats.append({"type": "Feature", "properties": {**props, "lat": s["lat"], "lon": s["lon"]}, "geometry": mapping(g)})
    data = json.dumps({"type": "FeatureCollection", "features": feats}).replace("</", "<\\/")
    (H.P / "hazard_map.html").write_text(TEMPLATE.replace("__DATA__", data), encoding="utf-8")
    print("hazard_map.html:", len(feats), "sites")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phase 3 Hazard Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root { --bg:#ffffff; --fg:#1b1b1b; --muted:#5b5b5b; --panel:#f3f4f6; --line:#d6d8dc; --both:#b42318; --flood:#1f6feb; --heat:#d97706; --none:#6b7280; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#141518; --fg:#e8e8e8; --muted:#a3a3a3; --panel:#1f2126; --line:#33363d;
  --both:#f0625b; --flood:#4c8dff; --heat:#f0a43a; --none:#9ca3af; } }
:root[data-theme="dark"] { --bg:#141518; --fg:#e8e8e8; --muted:#a3a3a3; --panel:#1f2126; --line:#33363d; --both:#f0625b; --flood:#4c8dff; --heat:#f0a43a; --none:#9ca3af; }
html,body { margin:0; height:100%; background:var(--bg); color:var(--fg); font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif; }
header { padding:10px 16px; background:var(--panel); border-bottom:1px solid var(--line); }
header p { margin:4px 0 0; color:var(--muted); font-size:12px; }
.k { display:inline-flex; gap:12px; flex-wrap:wrap; margin-top:4px; font-size:13px; }
.k i { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:4px; vertical-align:middle; }
label { margin-left:12px; font-size:13px; }
#map { height:calc(100% - 96px); min-height:300px; }
</style></head><body>
<header><strong>Phase 3 hazard exposure: point sites (main buffers)</strong>
<div class="k"><span><i style="background:var(--both)"></i>river flood and heat</span><span><i style="background:var(--flood)"></i>river flood only</span>
<span><i style="background:var(--heat)"></i>heat only</span><span><i style="background:var(--none)"></i>neither</span>
<label><input type="checkbox" id="offices" checked> show offices</label><label><input type="checkbox" id="r2" checked> show R2 (OSM-sourced)</label></div>
<p>River flood: JRC v2.1.2 RP100, depth &gt; 0 m in the main buffer. Heat: top tercile of main-set sites on the 2020&ndash;2025 minus 1991&ndash;2020 TX90p-type anomaly (ERA5 hourly time series, 0.25&deg;; amendments A10, A11).
Coastal flood (Aqueduct Floods v2.0 RP100) and water stress (Aqueduct 4.0) are shown in the popups. The NASA POWER heat result (robustness) is in the popups. Contains modified Copernicus Climate Change Service information (ERA5). Map data &copy; OpenStreetMap contributors (ODbL); flood hazard &copy; European Union, JRC.</p></header>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const data = __DATA__;
const map = L.map('map').setView([8.5, 7.5], 6);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const col = p => { const f = p.rf100_exposed === '1', h = String(p.heat_exposed) === '1';
  return css(f && h ? '--both' : f ? '--flood' : h ? '--heat' : '--none'); };
let layer = L.layerGroup().addTo(map);
function draw() {
  layer.clearLayers();
  const off = document.getElementById('offices').checked, r2 = document.getElementById('r2').checked;
  for (const f of data.features) {
    const p = f.properties;
    if (p.site_set === 'office' && !off) continue;
    if (p.site_set === 'R2' && !r2) continue;
    const c = col(p);
    L.geoJSON(f.geometry, {style: {color: c, weight: 1, fillOpacity: 0.12, dashArray: p.site_set === 'main' ? null : '4 3'}}).addTo(layer);
    L.circleMarker([p.lat, p.lon], {radius: p.site_set === 'main' ? 6 : 4, color: c, fillOpacity: 0.9}).addTo(layer).bindPopup(
      `<b>${esc(p.ticker)}: ${esc(p.facility)}</b><br>${esc(p.facility_id)} &middot; grade ${esc(p.rating)} &middot; set: ${esc(p.site_set)}<br>` +
      `Buffer: ${esc(p.buffer_main)}<br>RP100 flood: exposed=${esc(p.rf100_exposed)}, share=${esc(p.rf100_share)}, max depth ${esc(p.rf100_maxdepth_m)} m<br>` +
      `RP10 ${esc(p.rf10_exposed)} &middot; RP500 ${esc(p.rf500_exposed)} &middot; &ge;0.5 m ${esc(p['rf100_exposed_ge0.5m'])} &middot; robustness buffer ${esc(p.rf100_rob_exposed)}<br>` +
      `Without permanent water (A8): exposed=${esc(p.rf100_nopermwater_exposed)}<br>` +
      `Heat (ERA5) score ${esc(p.heat_score)} days (exposed=${esc(p.heat_exposed)}); NASA POWER robustness ${esc(p.heat_nasa_score)} (exposed=${esc(p.heat_nasa_exposed)})<br>` +
      `Coastal RP100: exposed=${esc(p.coastal_rp100_exposed)}, max depth ${esc(p.coastal_rp100_maxdepth_m)} m<br>` +
      `Water stress: ${esc(p.water_stress_label)} (exposed=${esc(p.water_stress_exposed)})<br>People within 5 km: ${esc(p.pop_within_5km)}`);
  }
}
document.getElementById('offices').onchange = draw; document.getElementById('r2').onchange = draw;
draw();
</script></body></html>
"""

if __name__ == "__main__":
    main()
