"""Phase 2, Task 4: assign coordinates under OD-1 (OSM features and stated addresses; no web geocoder).

Rules, applied in order, and recorded per row in coord_method / coord_source:
 1. osm_feature  - an OSM feature that matches the firm and site (fixed list below, each checked by the analyst).
 2. osm_place    - otherwise, an OSM place matching geocode_place, used only if exactly one candidate exists
                   (state-level "place=state" nodes ignored) or all candidates lie within 5 km of each other.
 3. otherwise    - no coordinate ("ambiguous" or "no OSM match").
Then, if the OSM state of the point (from states_check.json, if that query succeeded) contradicts a state named
in the report text, the coordinate is withdrawn ("state mismatch").
Precision values are nominal classes (analyst assumption), not measured errors.

usage: phase2_coordinates.py assign | finalize
"""
import csv
import json
import math
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RAW = ROOT / "data" / "raw"
FAC = ROOT / "data" / "interim" / "phase2_facilities_nocoords.csv"
STAGE = ROOT / "data" / "interim" / "phase2_facilities_coords_stage.csv"
PRECISION_M = {"feature": 250, "city": 10000, "town": 5000, "suburb": 2000, "neighbourhood": 1000, "quarter": 1000,
               "village": 2000, "hamlet": 1000, "island": 2000, "locality": 2000,
               "admin_area": 2000, "named_feature": 2000}  # last two: added 2026-11-12, nominal (analyst assumption)
STATES = ["Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", "Cross River", "Delta", "Ebonyi",
          "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos",
          "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"]
# (ticker, facility) -> OSM element (type/id), checked by the analyst against the report location
FEATURES = {
    ("DANGCEM", "Obajana plant"): "way/944919621", ("DANGCEM", "Gboko plant"): "way/1288604749",
    ("DANGCEM", "Ibese plant"): "way/945308310", ("DANGCEM", "Head office"): "node/5700588895",
    ("BUACEMENT", "Obu plant"): "node/13075110580", ("BUACEMENT", "Sokoto (Kalambaina) plant"): "way/975425452",
    ("GUINNESS", "Headquarters"): "way/135619504", ("GUINNESS", "Ogba Brewery"): "way/135619504",
    ("OKOMUOIL", "Main estate (registered office and principal place of business)"): "relation/14379780",
    ("OKOMUOIL", "Rubber factory"): "relation/14379936",
    ("CADBURY", "Registered office"): "way/223754822", ("CADBURY", "Factory"): "way/223754822",
    ("INTBREW", "Breweries"): "relation/8382484",
    ("NB", "Ibadan Brewery"): "way/82466274",
    ("UNILEVER", "Agbara manufacturing site"): "node/5678239529",
    ("SEPLAT", "Qua Iboe Terminal"): "relation/15408639",
    ("TRANSCORP", "[location text from a company report removed in the public copy]"): "relation/12186132",
}
# Place names first needed in owner round 3 (2026-11-11). No Overpass result yet: the network was down on 2026-11-11, and the
# owner-approved 'places3' query returned HTTP 502 (server at capacity) twice on 2026-11-12. Pending.
NOT_QUERIED = {"Umuahia", "Uyo", "Oshodi", "Agidingbi", "Libeli", "Warewa", "Abule Oshun", "Okpai", "Utako", "Iguelaba",
               "Adani", "Alagunten", "Abuni", "Inyishi", "Suleja", "Ibafon", "Arepo", "Geregu", "Ajaokuta"}
NOTES = {"way/945308310": "feature is the plant's power station", "node/5678239529": "feature tagged office=company",
         "way/135619504": "single building feature shared by HQ and brewery", "relation/8382484": "OSM supplies the only location"}


def elements():
    out = {}
    files = [RAW / "osm_pilot_named_features.json", RAW / "osm_phase2" / "features.json", RAW / "osm_phase2" / "places.json"]
    files += [f for f in [RAW / "osm_phase2" / "places2.json", RAW / "osm_phase2" / "places3.json"] if f.exists()]  # places3: Geofabrik extract
    for f in files:
        for e in json.loads(f.read_text(encoding="utf-8"))["elements"]:
            c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
            out[f"{e['type']}/{e['id']}"] = (c["lat"], c["lon"], e.get("tags", {}))
    return out


def km(a, b):
    p = math.pi / 180
    return 12742 * math.asin(math.sqrt(math.sin((b[0] - a[0]) * p / 2) ** 2 + math.cos(a[0] * p) * math.cos(b[0] * p) * math.sin((b[1] - a[1]) * p / 2) ** 2))


def assign():
    els = elements()
    places = {}
    for k, (lat, lon, t) in els.items():
        if "place" in t and t.get("place") != "state" and "name" in t:
            places.setdefault(t["name"], []).append((k, lat, lon, t["place"]))
    # Owner decision 2026-11-12: named OSM ways/relations (Geofabrik extract) also count as candidates for the names
    # still unmatched; centroid of the geometry. An administrative-area relation gets the nominal class "admin_area".
    f4 = RAW / "osm_phase2" / "places4.json"
    if f4.exists():
        for e in json.loads(f4.read_text(encoding="utf-8"))["elements"]:
            t = e.get("tags", {})
            kind = t.get("place") or ("admin_area" if t.get("boundary") == "administrative" else "named_feature")
            places.setdefault(t["name"], []).append((f"{e['type']}/{e['id']}", e["center"]["lat"], e["center"]["lon"], kind))
    with FAC.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r.update(lat="", lon="", coord_method="", coord_source="", coord_precision_m="", coord_note="")
        key = (r["ticker"], r["facility"])
        if key in FEATURES:
            lat, lon, t = els[FEATURES[key]]
            r.update(lat=f"{lat:.6f}", lon=f"{lon:.6f}", coord_method="osm_feature", coord_precision_m=PRECISION_M["feature"],
                     coord_source=f"OSM {FEATURES[key]} '{t.get('name', '')}'", coord_note=NOTES.get(FEATURES[key], ""))
            continue
        p = r["geocode_place"]
        if not p:
            continue
        cands = places.get(p, [])
        if not cands:
            if p in NOT_QUERIED and (RAW / "osm_phase2" / "places3.json").exists():
                r["coord_note"] = f"no OSM place node named '{p}' in the Geofabrik extract (2026-11-12)"
            elif p in NOT_QUERIED:
                r["coord_note"] = f"'{p}' pending: not yet located in OSM (no network 2026-11-11; Overpass HTTP 502 'at capacity' twice on 2026-11-12)"
            else:
                r["coord_note"] = f"no OSM place named '{p}' returned"
            continue
        major = [c for c in cands if c[3] in ("city", "town")]
        if len(cands) == 1 or max(km(cands[0][1:3], c[1:3]) for c in cands) <= 5:
            k, lat, lon, ptype = cands[0]
            r.update(lat=f"{lat:.6f}", lon=f"{lon:.6f}", coord_method="osm_place", coord_precision_m=PRECISION_M.get(ptype, 5000),
                     coord_source=f"OSM {k} place={ptype} '{p}'")
        elif len(major) == 1:  # rule 2b: the only city/town among same-named places
            k, lat, lon, ptype = major[0]
            r.update(lat=f"{lat:.6f}", lon=f"{lon:.6f}", coord_method="osm_place_rank", coord_precision_m=PRECISION_M.get(ptype, 5000),
                     coord_source=f"OSM {k} place={ptype} '{p}'",
                     coord_note=f"only city/town among {len(cands)} same-named OSM places")
        else:
            r["coord_note"] = f"ambiguous: {len(cands)} OSM places named '{p}'; not assigned"
    write(rows, STAGE)
    pts = [(r["facility_id"], float(r["lat"]), float(r["lon"])) for r in rows if r["lat"]]
    idx_file = RAW / "osm_phase2" / "states_check_index.json"
    if not (RAW / "osm_phase2" / "states_check.json").exists():  # keep the index that matches the completed state query
        idx_file.write_text(json.dumps(pts), encoding="utf-8")
    else:
        checked = set()
        for ix in ("states_check_index.json", "states_check2_index.json", "states_check3_index.json"):
            if (RAW / "osm_phase2" / ix).exists():
                checked |= {(round(a, 6), round(b, 6)) for _, a, b in json.loads((RAW / "osm_phase2" / ix).read_text(encoding="utf-8"))}
        new = [p for p in pts if (round(p[1], 6), round(p[2], 6)) not in checked]
        print("points not covered by the earlier state queries:", [p[0] for p in new])
        if new and not (RAW / "osm_phase2" / "states_check2.json").exists():
            (RAW / "osm_phase2" / "states_check2_index.json").write_text(json.dumps(new), encoding="utf-8")
        elif new and not (RAW / "osm_phase2" / "states_check3.json").exists():  # 2026-11-12: checked locally (Geofabrik)
            (RAW / "osm_phase2" / "states_check3_index.json").write_text(json.dumps(new), encoding="utf-8")
        elif new and not (RAW / "osm_phase2" / "states_check4.json").exists():  # 2026-11-12: named ways/relations
            (RAW / "osm_phase2" / "states_check4_index.json").write_text(json.dumps(new), encoding="utf-8")
    print("assigned", len(pts), "of", len(rows), "| by method:",
          {m: sum(r["coord_method"] == m for r in rows) for m in ("osm_feature", "osm_place", "osm_place_rank")})
    for r in rows:
        if r["coord_note"].startswith(("ambiguous", "no OSM")):
            print("  ", r["facility_id"], r["ticker"], r["facility"][:40], "|", r["coord_note"])


MULTI_SITE = re.compile(r"facilities in Aba, Ikeja, Jos, and Kano|located at Kano and Abuja")  # one sentence, several sites


def stated_states(text):
    """States named in the report text for this site. Road names ('Lagos/Abeokuta Expressway', 'Lagos Badagry
    Expressway') are ignored, 'Cross Rivers' is read as Cross River, and sentences listing several sites give none."""
    if MULTI_SITE.search(text):
        return set()
    text = re.sub(r"Lagos\s*[/-]\s*(Abeokuta|Ibadan)|Lagos Badagry", " ", text).replace("Cross Rivers", "Cross River")
    found = {s for s in STATES if re.search(rf"\b{s}\b", text)}
    if "Cross River" in found:
        found.discard("Rivers") if not re.search(r"(?<!Cross )\bRivers\b", text) else None
    return found | ({"Federal Capital Territory"} if re.search(r"\bFCT\b", text) else set())


def finalize():
    rows = list(csv.DictReader(STAGE.open(newline="", encoding="utf-8")))
    sfile = RAW / "osm_phase2" / "states_check.json"
    osm_state = {}
    for res, ix in (("states_check.json", "states_check_index.json"), ("states_check2.json", "states_check2_index.json"),
                    ("states_check3.json", "states_check3_index.json"), ("states_check4.json", "states_check4_index.json")):
        sfile = RAW / "osm_phase2" / res
        if not sfile.exists():
            continue
        try:
            idx = json.loads((RAW / "osm_phase2" / ix).read_text(encoding="utf-8"))
            for e in json.loads(sfile.read_text(encoding="utf-8"))["elements"]:
                i = int(e["tags"]["idx"])  # keyed by coordinates, so later re-runs of `assign` cannot misalign results
                osm_state[(round(idx[i][1], 6), round(idx[i][2], 6))] = e["tags"].get("state", "")
        except (ValueError, KeyError):
            print("could not read", res)
    for r in rows:
        r["osm_state"] = osm_state.get((round(float(r["lat"]), 6), round(float(r["lon"]), 6)), "") if r["lat"] else ""
        r["state_check"] = ""
        if not r["lat"]:
            continue
        written = stated_states(r["location_as_written"] + " " + r["state_as_written"])
        if not r["osm_state"]:
            r["state_check"] = "not checked (no OSM state result)"
        elif not written:
            r["state_check"] = "no state in report text"
        elif any(w.split()[0] in r["osm_state"] for w in written):
            r["state_check"] = "consistent"
        else:
            r["state_check"] = f"MISMATCH: report {sorted(written)} vs OSM {r['osm_state']}; coordinate withdrawn"
            r.update(coord_note=(r["coord_note"] + "; " if r["coord_note"] else "") + "withdrawn after state mismatch",
                     lat="", lon="", coord_method="withdrawn", coord_precision_m="")
    from a6_crosscheck import category  # amendment A6: grade-A rule-based cross-check and Phase 3 buffer
    for r in rows:
        r["a6_check"], r["buffer_m"] = category(r)
    write(rows, ROOT / "data" / "processed" / "facilities.csv")
    print("final:", {k: sum(r["state_check"].startswith(k) for r in rows) for k in ("consistent", "no state", "not checked", "MISMATCH")})
    for r in rows:
        if r["state_check"].startswith("MISMATCH"):
            print("  ", r["facility_id"], r["ticker"], r["facility"][:40], "|", r["state_check"])


def write(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


if __name__ == "__main__":
    {"assign": assign, "finalize": finalize}[sys.argv[1]]()
