"""Build data/processed/spotcheck_app.html: a one-site-at-a-time helper for the owner's grade-A spot-check (OD-1).

The page embeds the grade-A rows of data/processed/facilities.csv (operational sites first, then offices) and shows
each on a Leaflet map with OSM tiles. The owner's checks autosave to the browser's local storage and are exported
as CSV (facility_id, owner_check, owner_lat, owner_lon, owner_note, checked_at); src/merge_spotcheck.py merges that
CSV into data/processed/spotcheck_gradeA.csv. Map data (c) OpenStreetMap contributors, ODbL.

usage: phase2_spotcheck_app.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
KEEP = ("facility_id", "ticker", "facility", "facility_type", "is_office", "rating", "source_doc", "pdf_page",
        "location_as_written", "state_as_written", "lat", "lon", "coord_method", "coord_source", "coord_precision_m",
        "state_check", "coord_note")


def main() -> None:
    rows = [r for r in csv.DictReader((P / "facilities.csv").open(newline="", encoding="utf-8")) if r["rating"] == "A"]
    rows.sort(key=lambda r: (r["is_office"] == "yes", r["facility_id"]))  # operational first, then offices
    data = [{k: r[k] for k in KEEP} for r in rows]
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (P / "spotcheck_app.html").write_text(html, encoding="utf-8")
    print("spotcheck_app.html:", len(data), "grade-A sites;", sum(r["is_office"] == "no" for r in data), "operational first")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Grade-A Spot-Check</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root { --bg:#ffffff; --fg:#1b1b1b; --muted:#5b5b5b; --panel:#f3f4f6; --line:#d6d8dc; --accent:#1f6feb;
        --ok:#1a7f37; --approx:#b07d00; --bad:#c0392b; --moved:#7b3fe4; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#141518; --fg:#e8e8e8; --muted:#a3a3a3;
        --panel:#1f2126; --line:#33363d; --accent:#4c8dff; --ok:#3fb950; --approx:#d4a72c; --bad:#f0625b; --moved:#a37bff; } }
:root[data-theme="dark"] { --bg:#141518; --fg:#e8e8e8; --muted:#a3a3a3; --panel:#1f2126; --line:#33363d; --accent:#4c8dff;
        --ok:#3fb950; --approx:#d4a72c; --bad:#f0625b; --moved:#a37bff; }
* { box-sizing:border-box; }
html,body { margin:0; height:100%; background:var(--bg); color:var(--fg); font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif; }
.wrap { display:grid; grid-template-columns:minmax(300px,420px) 1fr; height:100%; }
.side { padding:14px 16px; overflow:auto; border-right:1px solid var(--line); }
#map { height:100%; min-height:320px; }
h1 { font-size:16px; margin:0 0 6px; }
.bar { height:8px; background:var(--panel); border-radius:4px; overflow:hidden; margin:6px 0 2px; }
.bar > i { display:block; height:100%; background:var(--accent); width:0; }
.muted { color:var(--muted); font-size:12px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:10px 12px; margin:10px 0; }
.card b { font-size:15px; }
.quote { font-style:italic; margin:6px 0; }
.kv { display:grid; grid-template-columns:110px 1fr; gap:2px 8px; font-size:13px; }
.kv span:nth-child(odd) { color:var(--muted); }
.btns { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0; }
button { font:inherit; padding:6px 10px; border-radius:6px; border:1px solid var(--line); background:var(--bg); color:var(--fg); cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { outline:2px solid var(--accent); }
.status { font-weight:600; }
.s-correct { color:var(--ok); } .s-approximate { color:var(--approx); } .s-wrong { color:var(--bad); } .s-moved { color:var(--moved); }
textarea { width:100%; min-height:54px; font:inherit; background:var(--bg); color:var(--fg); border:1px solid var(--line); border-radius:6px; padding:6px; }
a { color:var(--accent); }
kbd { border:1px solid var(--line); border-bottom-width:2px; border-radius:4px; padding:0 4px; font-size:12px; }
.hint { background:var(--panel); border-left:3px solid var(--moved); padding:6px 8px; margin:6px 0; display:none; }
@media (max-width: 760px) { .wrap { grid-template-columns:1fr; grid-template-rows:auto 55vh; height:auto; }
  .side { border-right:0; border-bottom:1px solid var(--line); } #map { height:55vh; } }
</style></head><body>
<div class="wrap">
<div class="side">
  <h1>Grade-A spot-check</h1>
  <div class="bar"><i id="prog"></i></div>
  <div class="muted" id="progtxt"></div>
  <div class="card" id="site"></div>
  <div class="btns">
    <button data-k="correct"><kbd>1</kbd> Correct</button>
    <button data-k="approximate"><kbd>2</kbd> Approximate</button>
    <button data-k="wrong"><kbd>3</kbd> Wrong</button>
    <button data-k="moved"><kbd>M</kbd> Moved</button>
    <button id="notebtn"><kbd>N</kbd> Note</button>
  </div>
  <div class="hint" id="movehint">Click the map at the correct location. Press <kbd>Esc</kbd> to cancel.</div>
  <textarea id="note" placeholder="Note (optional). Saved automatically."></textarea>
  <div class="btns">
    <button id="prev">&larr; Previous</button><button id="next">Next &rarr;</button>
    <button id="export">Export CSV</button><button id="clear">Clear this site</button>
  </div>
  <p class="muted">Keys: <kbd>1</kbd> correct, <kbd>2</kbd> approximate, <kbd>3</kbd> wrong, <kbd>M</kbd> moved (then click the map),
  <kbd>N</kbd> note, <kbd>&larr;</kbd>/<kbd>&rarr;</kbd> previous/next. Checks are saved in this browser after each action;
  use Export CSV to hand them over. Map data &copy; OpenStreetMap contributors (ODbL).</p>
</div>
<div id="map"></div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const SITES = __DATA__;
const KEY = "spotcheck_gradeA_v1";
let state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { state = {}; }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} };
let i = 0; try { i = Math.min(SITES.length - 1, Number(localStorage.getItem(KEY + "_pos")) || 0); } catch (e) {}
let moving = false;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const map = L.map("map").setView([8.5, 7.5], 6);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
const layer = L.layerGroup().addTo(map);
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

function render() {
  const s = SITES[i], st = state[s.facility_id] || {};
  try { localStorage.setItem(KEY + "_pos", i); } catch (e) {}
  const done = SITES.filter(x => state[x.facility_id] && state[x.facility_id].owner_check).length;
  document.getElementById("prog").style.width = (100 * done / SITES.length) + "%";
  document.getElementById("progtxt").textContent = `Site ${i + 1} of ${SITES.length} · ${done} checked` +
    (s.is_office === "yes" ? " · office" : " · operational site");
  const has = s.lat !== "" && s.lon !== "";
  const osm = has ? `https://www.openstreetmap.org/?mlat=${s.lat}&mlon=${s.lon}#map=16/${s.lat}/${s.lon}` : "";
  document.getElementById("site").innerHTML = `
    <div class="muted">${esc(s.facility_id)} · grade ${esc(s.rating)} · ${esc(s.facility_type)}</div>
    <b>${esc(s.ticker)}: ${esc(s.facility)}</b>
    <div class="quote">“${esc(s.location_as_written)}”</div>
    <div class="kv">
      <span>Source</span><span>${esc(s.source_doc)}, PDF p.${esc(s.pdf_page)}</span>
      <span>Coordinates</span><span>${has ? esc(s.lat) + ", " + esc(s.lon) : "none assigned"}</span>
      <span>Method</span><span>${esc(s.coord_method || "-")} ${s.coord_precision_m ? "(nominal " + esc(s.coord_precision_m) + " m)" : ""}</span>
      <span>OSM source</span><span>${esc(s.coord_source || s.coord_note || "-")}</span>
      <span>State check</span><span>${esc(s.state_check || "-")}</span>
      <span>OSM link</span><span>${has ? `<a href="${osm}" target="_blank" rel="noopener">open on openstreetmap.org</a>` : "-"}</span>
      <span>Your check</span><span class="status s-${esc(st.owner_check || "")}">${esc(st.owner_check || "not checked")}
        ${st.owner_lat ? " → " + esc(st.owner_lat) + ", " + esc(st.owner_lon) : ""}</span>
    </div>`;
  document.getElementById("note").value = st.owner_note || "";
  document.querySelectorAll("button[data-k]").forEach(b => b.classList.toggle("on", b.dataset.k === st.owner_check));
  layer.clearLayers();
  if (has) {
    const ll = [Number(s.lat), Number(s.lon)];
    L.circle(ll, {radius: Number(s.coord_precision_m) || 1000, color: css("--accent"), weight: 1, fillOpacity: 0.08}).addTo(layer);
    L.circleMarker(ll, {radius: 7, color: css("--accent"), fillOpacity: 0.9}).addTo(layer).bindTooltip("assigned point");
    map.setView(ll, s.coord_precision_m && Number(s.coord_precision_m) > 2000 ? 13 : 15);
  } else { map.setView([8.5, 7.5], 6); }
  if (st.owner_lat) {
    const m = [Number(st.owner_lat), Number(st.owner_lon)];
    L.circleMarker(m, {radius: 7, color: css("--moved"), fillOpacity: 0.9}).addTo(layer).bindTooltip("your point");
    if (!has) map.setView(m, 15);
  }
}
function mark(k) {
  const s = SITES[i]; const st = state[s.facility_id] = state[s.facility_id] || {};
  st.owner_check = k; st.checked_at = new Date().toISOString();
  if (k !== "moved") { delete st.owner_lat; delete st.owner_lon; }
  save(); render();
  if (k === "moved") { moving = true; document.getElementById("movehint").style.display = "block"; }
}
map.on("click", e => {
  if (!moving) return;
  const s = SITES[i]; const st = state[s.facility_id] = state[s.facility_id] || {};
  st.owner_check = "moved"; st.owner_lat = e.latlng.lat.toFixed(6); st.owner_lon = e.latlng.lng.toFixed(6);
  st.checked_at = new Date().toISOString(); moving = false;
  document.getElementById("movehint").style.display = "none"; save(); render();
});
const go = d => { moving = false; document.getElementById("movehint").style.display = "none"; i = (i + d + SITES.length) % SITES.length; render(); };
document.querySelectorAll("button[data-k]").forEach(b => b.onclick = () => mark(b.dataset.k));
document.getElementById("prev").onclick = () => go(-1);
document.getElementById("next").onclick = () => go(1);
document.getElementById("notebtn").onclick = () => document.getElementById("note").focus();
document.getElementById("note").addEventListener("input", e => {
  const s = SITES[i]; const st = state[s.facility_id] = state[s.facility_id] || {};
  st.owner_note = e.target.value; st.checked_at = new Date().toISOString(); save();
});
document.getElementById("clear").onclick = () => { delete state[SITES[i].facility_id]; save(); render(); };
document.addEventListener("keydown", e => {
  if (e.target.tagName === "TEXTAREA") { if (e.key === "Escape") e.target.blur(); return; }
  const k = e.key.toLowerCase();
  if (k === "1") mark("correct"); else if (k === "2") mark("approximate"); else if (k === "3") mark("wrong");
  else if (k === "m") mark("moved"); else if (k === "n") { e.preventDefault(); document.getElementById("note").focus(); }
  else if (e.key === "ArrowRight") go(1); else if (e.key === "ArrowLeft") go(-1);
  else if (e.key === "Escape") { moving = false; document.getElementById("movehint").style.display = "none"; }
});
document.getElementById("export").onclick = () => {
  const q = v => /[",\n]/.test(v) ? '"' + String(v).replace(/"/g, '""') + '"' : String(v);
  const lines = ["facility_id,owner_check,owner_lat,owner_lon,owner_note,checked_at"];
  for (const s of SITES) { const st = state[s.facility_id]; if (!st) continue;
    lines.push([s.facility_id, st.owner_check || "", st.owner_lat || "", st.owner_lon || "", st.owner_note || "", st.checked_at || ""].map(q).join(",")); }
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([lines.join("\n") + "\n"], {type: "text/csv"}));
  a.download = "spotcheck_export_" + new Date().toISOString().slice(0, 10) + ".csv"; a.click();
};
render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
