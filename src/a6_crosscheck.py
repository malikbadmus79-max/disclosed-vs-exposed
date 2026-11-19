"""Amendment A6: rule-based cross-check of grade-A locations (replaces the owner's visual spot-check, OD-1).

  correct (rule-based)     coord_method osm_feature, OSM name matches the firm/site, state_check consistent or no state
                           in report -> buffer 500 m (OD-2 grade-A buffer)
  approximate (rule-based) coord_method osm_place / osm_place_rank (place centroid), or an osm_feature row failing the
                           name or state test -> buffer = coord_precision_m
  no coordinate            no coordinate or withdrawn -> not scored in Phase 3

Only grade-A rows get a category and buffer_m; grade B/C buffers follow OD-2 and are set in Phase 3.
"""
import re

GRADE_A_BUFFER_M = 500  # OD-2
COMMENT = "A6 rule-based cross-check, 2026-11-12"
# Firm or brand names as written in the reports, used for the OSM-name test (lower case)
FIRM_NAMES = {
    "DANGCEM": ["dangote"], "BUACEMENT": ["bua cement", "bua"], "GUINNESS": ["guinness"], "CADBURY": ["cadbury"],
    "NB": ["nigerian breweries"], "OKOMUOIL": ["okomu"], "INTBREW": ["international breweries", "intbrew"],
    "UNILEVER": ["unilever"], "SEPLAT": ["seplat", "qua iboe"], "TRANSCORP": ["transcorp"],
}


def osm_name(coord_source: str) -> str:
    m = re.search(r"'([^']*)'", coord_source)
    return m.group(1).lower() if m else ""


def category(r: dict):
    """(category, buffer_m) for one facilities.csv row; ("", "") for rows that are not grade A."""
    if r["rating"] != "A":
        return "", ""
    if not r["lat"] or r["coord_method"] in ("", "withdrawn"):
        return "no coordinate", ""
    if r["coord_method"] == "osm_feature":
        name_ok = any(n in osm_name(r["coord_source"]) for n in FIRM_NAMES.get(r["ticker"], [r["ticker"].lower()]))
        state_ok = r["state_check"] in ("consistent", "no state in report text")
        if name_ok and state_ok:
            return "correct (rule-based)", GRADE_A_BUFFER_M
    return "approximate (rule-based)", int(float(r["coord_precision_m"]))
