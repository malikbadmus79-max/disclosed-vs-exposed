"""Phase 2 fallback for OSM place lookup and state check (owner decision 2026-11-12, option b).

Both Overpass routes failed on 2026-11-12: overpass-api.de returned HTTP 502 twice, and overpass.private.coffee
returned HTTP 504. The Geofabrik Nigeria extract is therefore downloaded once and read locally with pyosmium.
Only place nodes and admin_level=4 boundary relations are read, in streaming passes, to keep memory low.
Data (c) OpenStreetMap contributors, ODbL.

Outputs mimic the Overpass JSON files, so src/phase2_coordinates.py applies the same matching rules:
  data/raw/osm_phase2/places3.json          place nodes whose name is one of the requested names
  data/raw/osm_phase2/states_check3.json    the admin_level=4 state containing each point in states_check3_index.json

usage: phase2_osm_extract.py download | places Name1,Name2,... | states | named Name1,Name2,...
"""
import hashlib
from importlib import metadata
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import _log, _session  # noqa: E402

URL = "https://download.geofabrik.de/africa/nigeria-latest.osm.pbf"
PBF = ROOT / "data" / "raw" / "osm" / "nigeria-latest.osm.pbf"
OUT = ROOT / "data" / "raw" / "osm_phase2"


def download():
    PBF.parent.mkdir(parents=True, exist_ok=True)
    md5_remote = _session.get(URL + ".md5", timeout=60).text.split()[0]
    h_sha, h_md5, n = hashlib.sha256(), hashlib.md5(), 0
    with _session.get(URL, stream=True, timeout=120) as r:
        r.raise_for_status()
        tmp = PBF.with_suffix(".part")
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk); h_sha.update(chunk); h_md5.update(chunk); n += len(chunk)
        tmp.replace(PBF)
        last_mod = r.headers.get("Last-Modified", "")
    ok = h_md5.hexdigest() == md5_remote
    _log(URL, "200", f"Geofabrik Nigeria extract (owner-authorised fallback); md5 {'ok' if ok else 'MISMATCH'}; Last-Modified {last_mod}", n)
    info = {"url": URL, "bytes": n, "sha256": h_sha.hexdigest(), "md5": h_md5.hexdigest(), "md5_published": md5_remote,
            "md5_ok": ok, "last_modified": last_mod}
    (PBF.parent / "nigeria-latest.osm.pbf.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(info)


def places(names):
    import osmium
    want = set(names)
    els = []
    for o in osmium.FileProcessor(str(PBF), osmium.osm.NODE).with_filter(osmium.filter.KeyFilter("place")):
        if o.tags.get("name") in want and o.tags.get("place") != "state":
            els.append({"type": "node", "id": o.id, "lat": o.location.lat, "lon": o.location.lon, "tags": dict(o.tags)})
    body = {"generator": f"pyosmium {metadata.version("osmium")} on {PBF.name}", "source": "Geofabrik extract", "elements": els}
    (OUT / "places3.json").write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
    print("place nodes:", len(els), {n: sum(e["tags"]["name"] == n for e in els) for n in names})


def states(check="states_check3"):
    import osmium
    from shapely.geometry import LineString, Point
    from shapely.ops import polygonize, unary_union
    rels, way_ids = {}, set()
    for o in osmium.FileProcessor(str(PBF), osmium.osm.RELATION):  # pass 1: state boundary relations
        if o.tags.get("boundary") == "administrative" and o.tags.get("admin_level") == "4":
            ws = [m.ref for m in o.members if m.type == "w" and m.role in ("outer", "")]
            rels[o.id] = (o.tags.get("name", ""), ws)
            way_ids.update(ws)
    ways, node_ids = {}, set()
    for o in osmium.FileProcessor(str(PBF), osmium.osm.WAY):  # pass 2: their ways
        if o.id in way_ids:
            ways[o.id] = [n.ref for n in o.nodes]
            node_ids.update(ways[o.id])
    coords = {}
    for o in osmium.FileProcessor(str(PBF), osmium.osm.NODE):  # pass 3: their nodes
        if o.id in node_ids:
            coords[o.id] = (o.location.lon, o.location.lat)
    polys = {}
    for rid, (name, ws) in rels.items():
        lines = [LineString([coords[n] for n in ways[w] if n in coords]) for w in ws if w in ways and len(ways[w]) > 1]
        polys[name] = unary_union(list(polygonize(unary_union(lines))))
    pts = json.loads((OUT / f"{check}_index.json").read_text(encoding="utf-8"))
    els = []
    for i, (_, lat, lon) in enumerate(pts):
        hit = [n for n, poly in polys.items() if poly.contains(Point(lon, lat))]
        els.append({"type": "st", "id": i, "tags": {"idx": str(i), "state": ";".join(hit)}})
    body = {"generator": f"pyosmium {metadata.version("osmium")} + shapely on {PBF.name}", "source": "Geofabrik extract",
            "states_assembled": len(polys), "elements": els}
    (OUT / f"{check}.json").write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
    print("states assembled:", len(polys), "| points:", len(pts), "| unmatched:", sum(not e["tags"]["state"] for e in els))


def named(names):
    """Owner decision 2026-11-12: ways and relations (not only place nodes) whose name is one of `names`.
    Centroid of the assembled geometry (shapely); OSM type and id are kept. Output: places4.json (Overpass-like)."""
    import osmium
    from shapely.geometry import LineString, MultiPoint, Point, Polygon
    from shapely.ops import unary_union
    want = set(names)
    rels, ways, need_w = {}, {}, set()
    for o in osmium.FileProcessor(str(PBF), osmium.osm.RELATION):
        if o.tags.get("name") in want:
            rels[o.id] = (dict(o.tags), [m.ref for m in o.members if m.type == "w"], [m.ref for m in o.members if m.type == "n"])
            need_w.update(rels[o.id][1])
    named_w = {}
    for o in osmium.FileProcessor(str(PBF), osmium.osm.WAY):
        if o.tags.get("name") in want:
            named_w[o.id] = dict(o.tags)
        if o.tags.get("name") in want or o.id in need_w:
            ways[o.id] = [n.ref for n in o.nodes]
    need_n = {n for w in ways.values() for n in w} | {n for r in rels.values() for n in r[2]}
    xy = {}
    for o in osmium.FileProcessor(str(PBF), osmium.osm.NODE):
        if o.id in need_n:
            xy[o.id] = (o.location.lon, o.location.lat)

    def way_geom(wid):
        pts = [xy[n] for n in ways.get(wid, []) if n in xy]
        if len(pts) >= 4 and pts[0] == pts[-1]:
            return Polygon(pts)
        return LineString(pts) if len(pts) >= 2 else (Point(pts[0]) if pts else None)

    els = []
    for wid, tags in named_w.items():
        g = way_geom(wid)
        if g is not None:
            c = g.centroid
            els.append({"type": "way", "id": wid, "center": {"lat": c.y, "lon": c.x}, "tags": tags})
    for rid, (tags, wl, nl) in rels.items():
        parts = [g for g in (way_geom(w) for w in wl) if g is not None] + [Point(xy[n]) for n in nl if n in xy]
        if parts:
            c = unary_union(parts).centroid
            els.append({"type": "relation", "id": rid, "center": {"lat": c.y, "lon": c.x}, "tags": tags})
    body = {"generator": f"pyosmium {metadata.version('osmium')} + shapely on {PBF.name}", "source": "Geofabrik extract",
            "note": "ways and relations with an exact name match; centroid of the assembled geometry", "elements": els}
    (OUT / "places4.json").write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
    for e in els:
        t = e["tags"]
        kind = next((f"{k}={t[k]}" for k in ("place", "landuse", "boundary", "highway", "amenity", "building", "natural") if k in t), "other")
        print(e["type"], e["id"], t.get("name"), kind, round(e["center"]["lat"], 5), round(e["center"]["lon"], 5))
    print("matches:", len(els), {n: sum(e["tags"]["name"] == n for e in els) for n in names})


def geoms(way_ids, rel_ids):
    """Phase 3: polygons of given OSM ways/relations plus all admin_level=4 state boundaries, from the extract.
    Writes data/interim/osm_feature_polygons.geojson and data/interim/osm_states.geojson (ODbL)."""
    import osmium
    from shapely.geometry import LineString, Polygon, mapping
    from shapely.ops import polygonize, unary_union
    rel_ids, way_ids = set(rel_ids), set(way_ids)
    rels, states, need_w = {}, {}, set(way_ids)
    for o in osmium.FileProcessor(str(PBF), osmium.osm.RELATION):
        if o.id in rel_ids:
            rels[o.id] = (dict(o.tags), [m.ref for m in o.members if m.type == "w" and m.role in ("outer", "")])
            need_w.update(rels[o.id][1])
        elif o.tags.get("boundary") == "administrative" and o.tags.get("admin_level") == "4":
            states[o.id] = (dict(o.tags), [m.ref for m in o.members if m.type == "w" and m.role in ("outer", "")])
            need_w.update(states[o.id][1])
    ways = {}
    for o in osmium.FileProcessor(str(PBF), osmium.osm.WAY):
        if o.id in need_w:
            ways[o.id] = [n.ref for n in o.nodes]
    need_n = {n for w in ways.values() for n in w}
    xy = {}
    for o in osmium.FileProcessor(str(PBF), osmium.osm.NODE):
        if o.id in need_n:
            xy[o.id] = (o.location.lon, o.location.lat)

    def area_of(wl):
        lines = [LineString([xy[n] for n in ways[w] if n in xy]) for w in wl if w in ways and len(ways[w]) > 1]
        return unary_union(list(polygonize(unary_union(lines))))

    feats = []
    for wid in way_ids:
        pts = [xy[n] for n in ways.get(wid, []) if n in xy]
        g = Polygon(pts) if len(pts) >= 4 and pts[0] == pts[-1] else LineString(pts)
        feats.append({"type": "Feature", "properties": {"osm": f"way/{wid}", "geom_type": g.geom_type}, "geometry": mapping(g)})
    for rid, (tags, wl) in rels.items():
        g = area_of(wl)
        feats.append({"type": "Feature", "properties": {"osm": f"relation/{rid}", "name": tags.get("name", ""), "geom_type": g.geom_type},
                      "geometry": mapping(g)})
    meta = {"source": f"Geofabrik {PBF.name} (see data/raw/osm/nigeria-latest.osm.pbf.json); (c) OpenStreetMap contributors, ODbL"}
    (ROOT / "data" / "interim" / "osm_feature_polygons.geojson").write_text(
        json.dumps({"type": "FeatureCollection", **meta, "features": feats}), encoding="utf-8")
    sf = [{"type": "Feature", "properties": {"osm": f"relation/{rid}", "name": t.get("name", ""), "name_en": t.get("name:en", ""),
                                             "ISO3166-2": t.get("ISO3166-2", "")}, "geometry": mapping(area_of(wl))}
          for rid, (t, wl) in states.items()]
    (ROOT / "data" / "interim" / "osm_states.geojson").write_text(
        json.dumps({"type": "FeatureCollection", **meta, "features": sf}), encoding="utf-8")
    print("feature polygons:", [(f["properties"]["osm"], f["properties"]["geom_type"]) for f in feats])
    print("states:", len(sf), sorted(f["properties"]["ISO3166-2"] for f in sf if f["properties"]["ISO3166-2"].startswith("NG")))


if __name__ == "__main__":
    {"download": download, "places": lambda: places(sys.argv[2].split(",")), "states": lambda: states(sys.argv[2] if len(sys.argv) > 2 else "states_check3"),
     "named": lambda: named(sys.argv[2].split(",")),
     "geoms": lambda: geoms([int(x) for x in sys.argv[2].split(",")], [int(x) for x in sys.argv[3].split(",")])}[sys.argv[1]]()
