"""Phase 1: apply the owner's 2026-11-07 decisions to config/parameters.json and mark it frozen.

Every owner-decision-needed item becomes "decided" with decided_on = 2026-11-07. The file is written to a
temporary path first and then replaced, so a failure cannot leave it half-written.
"""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "config" / "parameters.json"
DATE = "2026-11-07"
p = json.loads(PATH.read_text(encoding="utf-8"))

loc, buf, hz, txt, val, an = p["location"], p["buffers_m"], p["hazards"], p["text"], p["validation"], p["analysis"]
loc["geocoder"].update(value="manual geocoding from OSM features and named addresses; no web geocoder in Phase 2",
                       owner_spot_check="owner manually spot-checks every grade-A site location before Phase 3")
hz["river_flood"]["depth_threshold_m"]["robustness"] = 0.5
hz["coastal_flood"]["depth_threshold_m"]["robustness"] = 0.5
hz["coastal_flood"]["coastal_zone"]["value"] = "none defined: every A/B point site scored; inland sites score zero"
hz["heat"]["exposure_margin"].update(value="continuous anomaly (2020-2025 mean minus 1991-2020 mean); exposed = top tercile of sites")
hz["heat"]["absolute_heat_index_threshold"].update(
    value=None,
    decision="no fixed-threshold heat-index check (fallback)",
    verification_attempt="owner-specified URL https://www.weather.gov/media/unr/heatindex.pdf returned HTTP 404 on 2026-11-07; NWS categories not verified",
)
hz["heat"]["era5"]["value"] = "not used; revisit only via amendment if several sites share one NASA POWER cell"
p["firm_exposure"]["combined_index"].update(value="mean of hazard-specific E_share (secondary)", primary_hazards=["river_flood", "heat"])
txt["readability_min_common_word_share"]["calibration"] = "calibrate on Phase 0 files before use (Unilever 2025 must fail, others pass); log calibrated value as an amendment"
txt["physical_risk_dictionary"]["rule"] = "drop bare 'heat' if validation shows false positives; log as amendment"
for k in ("min_alpha", "min_kappa"):
    val[k]["note"] = "benchmark values to be confirmed in the original texts before the paper"
an["foreign_parent_threshold"]["robustness"] = 0.20


def decide(o):
    if isinstance(o, dict):
        if o.get("status") == "owner-decision-needed":
            o["status"] = "decided"
            o["decided_on"] = DATE
            o.pop("recommendation", None)
        for v in o.values():
            decide(v)
    elif isinstance(o, list):
        for v in o:
            decide(v)


decide(p)
p["_meta"].update(version="frozen-2026-11-07", frozen=True, frozen_on=DATE,
                  freeze_record="docs/amendments.md (SHA-256 of this file and docs/design.md)")
p["_meta"]["status_values"].pop("owner-decision-needed", None)

text = json.dumps(p, indent=2, ensure_ascii=False) + "\n"
json.loads(text)  # must round-trip before replacing the original
tmp = PATH.with_suffix(".json.tmp")
tmp.write_text(text, encoding="utf-8")
tmp.replace(PATH)
left = text.count('"owner-decision-needed"')
print("written; remaining owner-decision-needed:", left, "| decided_on entries:", text.count('"decided_on"'))
