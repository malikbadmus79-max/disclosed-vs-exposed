"""Phase 3: site hazard scores (design section e; amendments A6, A7). No report text is read here.

Site sets (design d; facilities.csv):
  main     grade A/B point sites with a coordinate, location from the report, not an office (design d lists plants,
           breweries, factories, mills, terminals, flow stations, platforms, distribution centres, data centres and
           plantation estates as point sites; offices are not listed)
  office   offices with a coordinate: scored descriptively, not in firm scores
  R2       OSM-sourced point sites (robustness set R2)
Buffers (e5 + A6 + A7): grade A main = A6 buffer_m, robustness = 500 m (A7); grade B = OSM polygon + 250 m when the
site was located from an OSM way/relation, else 2 km main / 5 km robustness; R2 OSM sites = polygon + 250 m.
Circles and polygon buffers are built in a local equirectangular metric frame around the site (approximation).

usage: phase3_hazards.py flood | pop | states | permwater | coastal | water | water_future
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import Window, from_bounds
from shapely.affinity import affine_transform
from shapely.geometry import Point, shape
from shapely.ops import unary_union

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "hazards"
P = ROOT / "data" / "processed"
I = ROOT / "data" / "interim"
PARAMS = json.loads((ROOT / "config" / "parameters.json").read_text(encoding="utf-8"))
B_MAIN = PARAMS["buffers_m"]["B_main"]["value"]          # 2000
B_ROB = PARAMS["buffers_m"]["B_robustness"]["value"]     # 5000
PAD = PARAMS["buffers_m"]["osm_polygon_padding"]["value"]  # 250
A_ROB = PARAMS["buffers_m"]["A_robustness_500"]["value"]  # 500 (A7)
DEPTH_MAIN = PARAMS["hazards"]["river_flood"]["depth_threshold_m"]["value"]       # > 0.0
DEPTH_ROB = PARAMS["hazards"]["river_flood"]["depth_threshold_m"]["robustness"]  # >= 0.5 check
RP_MAIN = PARAMS["hazards"]["river_flood"]["return_period_main"]["value"]        # 100
RP_ROB = PARAMS["hazards"]["river_flood"]["return_periods_robustness"]["value"]  # [10, 500]
POP_R = PARAMS["sociology_policy"]["population_radius_m"]["value"]               # 5000
WORLDPOP = RAW / "worldpop" / "nga_pop_2025_CN_100m_R2025A_v1.tif"


# ---------------------------------------------------------------- geometry helpers
def to_local(g, lat0, lon0):
    k = math.cos(math.radians(lat0))
    return affine_transform(g, [111320.0 * k, 0, 0, 110574.0, -111320.0 * k * lon0, -110574.0 * lat0])


def to_geo(g, lat0, lon0):
    k = math.cos(math.radians(lat0))
    return affine_transform(g, [1 / (111320.0 * k), 0, 0, 1 / 110574.0, lon0, lat0])


def circle(lat, lon, r_m):
    return to_geo(Point(0, 0).buffer(r_m, 64), lat, lon)


def pad(geom, r_m):
    c = geom.centroid
    return to_geo(to_local(geom, c.y, c.x).buffer(r_m, 32), c.y, c.x)


def area_km2(geom):
    c = geom.centroid
    return to_local(geom, c.y, c.x).area / 1e6


# ---------------------------------------------------------------- sites and buffers
def load_sites():
    polys = {}
    fp = I / "osm_feature_polygons.geojson"
    if fp.exists():
        for f in json.loads(fp.read_text(encoding="utf-8"))["features"]:
            g = shape(f["geometry"])
            if g.geom_type in ("Polygon", "MultiPolygon") and not g.is_empty:
                polys[f["properties"]["osm"]] = g
    out = []
    for r in csv.DictReader((P / "facilities.csv").open(newline="", encoding="utf-8")):
        if r["asset_type"] != "point" or not r["lat"]:
            continue
        lat, lon = float(r["lat"]), float(r["lon"])
        osm = r["coord_source"].split()[1] if r["coord_method"] == "osm_feature" else ""
        poly = polys.get(osm)
        if r["location_source"] == "osm":
            site_set = "R2"
        elif r["is_office"] == "yes":
            site_set = "office"
        elif r["rating"] in ("A", "B"):
            site_set = "main"
        else:
            site_set = "other"
        if r["rating"] == "A":
            bm, rule_m = float(r["buffer_m"]), f"A6 {r['a6_check']}: {int(float(r['buffer_m']))} m circle"
            br, rule_r = A_ROB, f"A7 robustness: {A_ROB} m circle"
            gm, gr = circle(lat, lon, bm), circle(lat, lon, br)
        elif poly is not None:
            gm = gr = pad(poly, PAD)
            bm = br = None
            rule_m = rule_r = f"OSM polygon {osm} + {PAD} m (e5)"
        else:
            bm, br = B_MAIN, B_ROB
            rule_m, rule_r = f"{B_MAIN} m circle (OD-2 grade {r['rating']} main)", f"{B_ROB} m circle (OD-2 robustness)"
            gm, gr = circle(lat, lon, bm), circle(lat, lon, br)
        out.append({"r": r, "lat": lat, "lon": lon, "set": site_set, "g_main": gm, "g_rob": gr,
                    "rule_main": rule_m, "rule_rob": rule_r, "g_pop5": circle(lat, lon, POP_R)})
    return out


# ---------------------------------------------------------------- raster sampling
class Mosaic:
    """Read values under a geometry from one or more GeoTIFF tiles (windowed; low memory)."""

    def __init__(self, paths):
        self.ds = [rasterio.open(p) for p in paths]

    def values(self, geom, all_touched=False):
        vals = []
        minx, miny, maxx, maxy = geom.bounds
        for d in self.ds:
            b = d.bounds
            if maxx < b.left or minx > b.right or maxy < b.bottom or miny > b.top:
                continue
            win = from_bounds(max(minx, b.left), max(miny, b.bottom), min(maxx, b.right), min(maxy, b.top), d.transform)
            c0, r0 = math.floor(win.col_off), math.floor(win.row_off)
            win = Window(c0, r0, math.ceil(win.col_off + win.width) - c0 + 1, math.ceil(win.row_off + win.height) - r0 + 1)
            try:
                win = win.intersection(Window(0, 0, d.width, d.height))
            except Exception:  # no overlap
                continue
            if win.width <= 0 or win.height <= 0:
                continue
            a = d.read(1, window=win)
            m = geometry_mask([geom], out_shape=a.shape, transform=d.window_transform(win), invert=True, all_touched=all_touched)
            v = a[m].astype("float64")
            if d.nodata is not None:
                v[v == d.nodata] = np.nan
            vals.append(v)
        return np.concatenate(vals) if vals else np.array([])


def flood_metrics(mos, geom):
    v = mos.values(geom)
    n = v.size
    if n == 0:
        return {"cells": 0}
    wet = np.nan_to_num(v, nan=0.0)
    return {"cells": n, "any": int((wet > DEPTH_MAIN).any()), "share": round(float((wet > DEPTH_MAIN).mean()), 4),
            "max": round(float(wet.max()), 3), "any05": int((wet >= DEPTH_ROB).any())}


def jrc(rp):
    return Mosaic(sorted((RAW / "jrc" / f"RP{rp}").glob("*_depth.tif")))


# ---------------------------------------------------------------- tasks
def flood():
    sites = load_sites()
    mos = {rp: jrc(rp) for rp in [RP_MAIN] + RP_ROB}
    rows = []
    for s in sites:
        r = s["r"]
        row = {"facility_id": r["facility_id"], "ticker": r["ticker"], "census_stratum": r["census_stratum"],
               "facility": r["facility"], "rating": r["rating"], "is_office": r["is_office"], "site_set": s["set"],
               "lat": r["lat"], "lon": r["lon"], "osm_state": r["osm_state"], "a6_check": r["a6_check"],
               "buffer_main": s["rule_main"], "buffer_main_km2": round(area_km2(s["g_main"]), 3),
               "buffer_rob": s["rule_rob"], "buffer_rob_km2": round(area_km2(s["g_rob"]), 3)}
        m = flood_metrics(mos[RP_MAIN], s["g_main"])
        row.update({f"rf{RP_MAIN}_cells": m["cells"], f"rf{RP_MAIN}_exposed": m.get("any", ""),
                    f"rf{RP_MAIN}_share": m.get("share", ""), f"rf{RP_MAIN}_maxdepth_m": m.get("max", ""),
                    f"rf{RP_MAIN}_exposed_ge0.5m": m.get("any05", "")})
        for rp in RP_ROB:
            m = flood_metrics(mos[rp], s["g_main"])
            row.update({f"rf{rp}_exposed": m.get("any", ""), f"rf{rp}_share": m.get("share", ""), f"rf{rp}_maxdepth_m": m.get("max", "")})
        m = flood_metrics(mos[RP_MAIN], s["g_rob"])
        row.update({f"rf{RP_MAIN}_rob_exposed": m.get("any", ""), f"rf{RP_MAIN}_rob_share": m.get("share", ""),
                    f"rf{RP_MAIN}_rob_maxdepth_m": m.get("max", "")})
        rows.append(row)
        print(row["facility_id"], row["site_set"], row["buffer_main"][:28], row[f"rf{RP_MAIN}_exposed"], row[f"rf{RP_MAIN}_share"],
              row[f"rf{RP_MAIN}_maxdepth_m"], "| rob", row[f"rf{RP_MAIN}_rob_exposed"], flush=True)
    write(rows, I / "phase3_flood.csv")


def pop():
    """WorldPop people within the main buffer and within POP_R of each site (per site; firm unions in phase3_firms.py)."""
    if not WORLDPOP.exists():
        print("WorldPop raster missing"); return
    mos = Mosaic([WORLDPOP])
    rows = []
    for s in load_sites():
        a = mos.values(s["g_main"]); b = mos.values(s["g_pop5"])
        rows.append({"facility_id": s["r"]["facility_id"], "pop_in_main_buffer": round(float(np.nansum(a)), 1),
                     "pop_within_5km": round(float(np.nansum(b)), 1)})
    write(rows, I / "phase3_pop.csv")
    print("pop rows", len(rows))


def states():
    """Share of each state's area with RP100 depth > 0 (grade C robustness; dispersed-asset input)."""
    sf = json.loads((I / "osm_states.geojson").read_text(encoding="utf-8"))["features"]
    mos = jrc(RP_MAIN)
    rows = []
    for f in sf:
        iso = f["properties"].get("ISO3166-2", "")
        if not iso.startswith("NG"):
            continue
        g = shape(f["geometry"])
        if g.is_empty:
            rows.append({"state": f["properties"]["name"], "iso": iso, "cells": 0, "rf100_share_area": "",
                         "note": "state polygon not assembled from OSM (empty geometry)"})
            print(rows[-1], flush=True)
            continue
        v = np.nan_to_num(mos.values(g), nan=0.0)
        rows.append({"state": f["properties"]["name"], "iso": iso, "cells": v.size,
                     "rf100_share_area": round(float((v > DEPTH_MAIN).mean()), 4) if v.size else "", "note": ""})
        print(rows[-1], flush=True)
        del v
    write(rows, I / "phase3_states.csv")


# ---------------------------------------------------------------- A8: permanent-water mask (robustness)
def flood_permwater():
    """RP100 exposure and flooded share with JRC permanent-water cells (mask value 1) removed from both numerator
    and denominator (A8). Main buffers. Tiles share the depth tiles' grid, so values align cell by cell."""
    depth = jrc(RP_MAIN)
    mask = Mosaic(sorted((RAW / "jrc" / "Permanent_WaterBodies").glob("*_permanent_water.tif")))
    rows = []
    for s in load_sites():
        d = np.nan_to_num(depth.values(s["g_main"]), nan=0.0)
        m = mask.values(s["g_main"])
        assert d.size == m.size, s["r"]["facility_id"]
        perm = m == 1
        land = ~perm
        rows.append({"facility_id": s["r"]["facility_id"], "permwater_cells": int(perm.sum()), "cells": int(d.size),
                     "rf100_nopw_exposed": int((d[land] > DEPTH_MAIN).any()) if land.any() else 0,
                     "rf100_nopw_share": round(float((d[land] > DEPTH_MAIN).mean()), 4) if land.any() else ""})
    write(rows, I / "phase3_flood_permwater.csv")
    print("A8 rows", len(rows), "| sites with permanent water in buffer", sum(r["permwater_cells"] > 0 for r in rows))


# ---------------------------------------------------------------- coastal flood (e2)
COASTAL = RAW / "aqueduct_floods" / "inuncoast_historical_nosub_hist_rp0100_0.tif"


def coastal():
    """Aqueduct Floods v2.0 coastal, baseline (historical, no subsidence), RP100; 30 arc-second cells (~0.92 km).
    Depth > 0 m within the main buffer (e2/OD-3), >= 0.5 m as the OD-3 robustness check. Because cells are larger than
    many buffers, every cell touching the buffer counts (all_touched=True); nodata (-9999) counts as dry."""
    mos = Mosaic([COASTAL])
    rows = []
    for s in load_sites():
        v = np.nan_to_num(mos.values(s["g_main"], all_touched=True), nan=0.0)
        rows.append({"facility_id": s["r"]["facility_id"], "coastal_cells": int(v.size),
                     "exposed": int((v > DEPTH_MAIN).any()) if v.size else "",
                     "coastal_share": round(float((v > DEPTH_MAIN).mean()), 4) if v.size else "",
                     "coastal_maxdepth_m": round(float(v.max()), 3) if v.size else "",
                     "exposed_ge0.5m": int((v >= DEPTH_ROB).any()) if v.size else ""})
    write(rows, I / "phase3_coastal.csv")
    print("coastal rows", len(rows), "| exposed", sum(r["exposed"] == 1 for r in rows))


# ---------------------------------------------------------------- water stress (e4)
AQ40 = RAW / "aqueduct40" / "unzipped" / "Aqueduct40_waterrisk_download_Y2023M07D05" / "GDB" / "Aq40_Y2023D07M05.gdb"
WS_EXPOSED = {3, 4}  # the dataset's two highest bws categories: 3 "High (40-80%)", 4 "Extremely High (>80%)"


def water():
    """Aqueduct 4.0 baseline annual layer: bws_cat/bws_label/bws_raw of the polygon containing each site (no buffer)."""
    import pyogrio
    from shapely import STRtree, from_wkb
    meta, _, geom, fields = pyogrio.raw.read(AQ40, layer="baseline_annual", bbox=(2.0, 3.5, 15.5, 14.5),
                                             columns=["pfaf_id", "gid_1", "bws_raw", "bws_cat", "bws_label"])
    f = dict(zip(meta["fields"].tolist(), fields))
    geoms = from_wkb(geom)
    tree = STRtree(geoms)
    rows = []
    for s in load_sites():
        pt = Point(s["lon"], s["lat"])
        hits = [i for i in tree.query(pt) if geoms[i].contains(pt)]
        if not hits:
            rows.append({"facility_id": s["r"]["facility_id"], "pfaf_id": "", "gid_1": "", "bws_raw": "", "bws_cat": "",
                         "bws_label": "no polygon contains the site", "exposed": ""})
            continue
        i = hits[0]
        cat = f["bws_cat"][i]
        rows.append({"facility_id": s["r"]["facility_id"], "pfaf_id": int(f["pfaf_id"][i]), "gid_1": f["gid_1"][i],
                     "bws_raw": round(float(f["bws_raw"][i]), 4), "bws_cat": int(cat) if cat == cat else "",
                     "bws_label": f["bws_label"][i], "exposed": int(cat in WS_EXPOSED), "n_polygons_containing": len(hits)})
    write(rows, I / "phase3_water.csv")
    print("water rows", len(rows), "| exposed", sum(r["exposed"] == 1 for r in rows), "| polygons read", len(geoms))


FUTURE = {"bau2030": "bau30_ws_x", "bau2050": "bau50_ws_x"}  # design e4: 2030 and 2050, business-as-usual


def water_future():
    """DESCRIPTIVE ONLY (design e4; 'Future scenarios are reported descriptively only'). Aqueduct 4.0 future_annual layer,
    business-as-usual water stress (ws) for 2030 and 2050, joined by the HydroBASINS level-6 pfaf_id of the baseline
    polygon that contains each site (phase3_water.csv). Not used in any exposure measure, index or hypothesis."""
    import pyogrio
    base = {r["facility_id"]: r for r in csv.DictReader((I / "phase3_water.csv").open(newline="", encoding="utf-8"))}
    cols = ["pfaf_id"] + [f"{v}_{s}" for v in FUTURE.values() for s in ("r", "c", "l")]
    meta, _, _, fields = pyogrio.raw.read(AQ40, layer="future_annual", read_geometry=False, columns=cols)
    f = dict(zip(meta["fields"].tolist(), fields))
    idx = {int(p): i for i, p in enumerate(f["pfaf_id"])}
    assert len(idx) == len(f["pfaf_id"]), "pfaf_id not unique in future_annual"
    rows = []
    for fid, b in base.items():
        r = {"facility_id": fid, "pfaf_id": b["pfaf_id"]}
        i = idx.get(int(b["pfaf_id"])) if b["pfaf_id"] else None
        for k, v in FUTURE.items():
            if i is None:
                r.update({f"{k}_raw": "", f"{k}_cat": "", f"{k}_label": "no future_annual row for this pfaf_id"}); continue
            raw, cat = f[f"{v}_r"][i], f[f"{v}_c"][i]
            r.update({f"{k}_raw": round(float(raw), 4) if raw == raw else "", f"{k}_cat": int(cat) if cat == cat else "",
                      f"{k}_label": f[f"{v}_l"][i]})
        rows.append(r)
    write(rows, I / "phase3_water_future.csv")
    print("future rows", len(rows), "| unmatched", sum(r["bau2030_raw"] == "" for r in rows))


def write(rows, path):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    {"flood": flood, "pop": pop, "states": states, "permwater": flood_permwater, "coastal": coastal, "water": water, "water_future": water_future}[sys.argv[1]]()
