"""Phase 3: combine site hazard scores into data/processed/site_hazards.csv and firm scores data/processed/firm_exposure.csv
(design e6, OD-8; A6/A7). No capacity weights. No report text is read.

Firm measures per hazard h over the firm's main-analysis point sites (site_set == "main"):
  E_share = share of sites exposed (main measure); E_any = 1 if any site exposed; E_max = largest continuous score.
Primary hazards: river flood (RP100, depth > 0 m, A6/OD-2 buffers) and heat (top tercile of main-set sites on the
2020-2025 minus 1991-2020 TX90p-type anomaly). Heat main = ERA5 (A10 method; A11 source: hourly point time series,
data/interim/phase3_heat_era5.csv) in the heat_* columns; the NASA POWER 0.5-degree-bin scores (data/interim/phase3_heat.csv)
are kept side by side as a robustness check in the heat_nasa_* columns, with their own tercile.
Water stress 2030/2050 business-as-usual (Aqueduct 4.0 future_annual; data/interim/phase3_water_future.csv) is copied into
the water_stress_future_* site columns as DESCRIPTIVE ONLY (design e4): it enters no exposure measure, index or hypothesis. Coastal flood and water stress are included only if their inputs exist.
Combined index (secondary, OD-8) = mean of the hazard-specific E_share values; flagged "partial" when a hazard is missing.
Robustness columns: river flood with the robustness buffers (A7 500 m for grade A; 5 km for grade B circles), RP10, RP500,
depth >= 0.5 m, and R2 (adds OSM-sourced sites).
Population (OD-16): WorldPop people within the main buffer and within 5 km of the firm's exposed sites, as the union of
the circles (no double counting), for sites exposed to river flood, to heat, and to either.

usage: phase3_firms.py
"""
import csv
import sys
from pathlib import Path

import numpy as np
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import phase3_hazards as H  # noqa: E402

I, P = H.I, H.P


def read(path):
    return {r["facility_id"]: r for r in csv.DictReader(path.open(newline="", encoding="utf-8"))} if path.exists() else {}


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main() -> None:
    flood, pop = read(I / "phase3_flood.csv"), read(I / "phase3_pop.csv")
    heat, nasa = read(I / "phase3_heat_era5.csv"), read(I / "phase3_heat.csv")  # A10: ERA5 main; NASA POWER robustness
    coastal, water = read(I / "phase3_coastal.csv"), read(I / "phase3_water.csv")
    permw = read(I / "phase3_flood_permwater.csv")
    wfut = read(I / "phase3_water_future.csv")  # descriptive only (e4)
    sites = {s["r"]["facility_id"]: s for s in H.load_sites()}
    # heat exposure: top tercile of main-set sites (OD-5)
    main_scores = [fnum(heat[f]["heat_score"]) for f, s in sites.items() if s["set"] == "main" and f in heat and fnum(heat[f]["heat_score"]) is not None]
    q = float(np.quantile(main_scores, 2 / 3)) if main_scores else None
    nasa_scores = [fnum(nasa[f]["heat_score"]) for f, s in sites.items() if s["set"] == "main" and f in nasa and fnum(nasa[f]["heat_score"]) is not None]
    qn = float(np.quantile(nasa_scores, 2 / 3)) if nasa_scores else None
    rows = []
    for fid, s in sites.items():
        r = dict(flood.get(fid, {"facility_id": fid}))
        h = heat.get(fid, {})
        hs = fnum(h.get("heat_score"))
        r.update({"heat_cell_lat": h.get("era5_cell_lat", ""), "heat_cell_lon": h.get("era5_cell_lon", ""), "heat_tx_p90_c": h.get("tx_p90_c", ""),
                  "heat_tx90_days_1991_2020": h.get("tx90_days_base_mean", ""), "heat_tx90_days_2020_2025": h.get("tx90_days_recent_mean", ""),
                  "heat_score": h.get("heat_score", ""), "heat_tercile_cut": round(q, 3) if q is not None else "",
                  "heat_exposed": (int(hs >= q) if (hs is not None and q is not None) else "")})
        c, w = coastal.get(fid, {}), water.get(fid, {})
        pw = permw.get(fid, {})
        r.update({"rf100_nopermwater_exposed": pw.get("rf100_nopw_exposed", ""), "rf100_nopermwater_share": pw.get("rf100_nopw_share", ""),
                  "permwater_cells_in_buffer": pw.get("permwater_cells", "")})
        r.update({"coastal_rp100_exposed": c.get("exposed", "not scored: data not obtained"), "coastal_rp100_share": c.get("coastal_share", ""),
                  "coastal_rp100_maxdepth_m": c.get("coastal_maxdepth_m", ""), "coastal_rp100_exposed_ge0.5m": c.get("exposed_ge0.5m", ""),
                  "coastal_cells_touching_buffer": c.get("coastal_cells", ""),
                  "water_stress_pfaf_id": w.get("pfaf_id", ""), "water_stress_raw": w.get("bws_raw", ""),
                  "water_stress_cat": w.get("bws_cat", "not scored: data not obtained"), "water_stress_label": w.get("bws_label", ""),
                  "water_stress_exposed": w.get("exposed", "")})
        wf = wfut.get(fid, {})
        for k in ("bau2030", "bau2050"):
            r.update({f"water_stress_future_{k}_raw": wf.get(f"{k}_raw", ""), f"water_stress_future_{k}_cat": wf.get(f"{k}_cat", ""),
                      f"water_stress_future_{k}_label": wf.get(f"{k}_label", "")})
        r["water_stress_future_note"] = ("descriptive only (design e4): Aqueduct 4.0 future_annual, business-as-usual, water stress (ws); "
                                         "not used in any exposure measure, index or hypothesis") if wf else ""
        r["heat_source"] = h.get("heat_source", "not scored: ERA5 file missing")
        # robustness: NASA POWER (0.5-degree bins, owner manual download), own top-tercile cut among main sites
        n = nasa.get(fid, {})
        ns = fnum(n.get("heat_score"))
        nsrc = n.get("heat_source", "")
        if nsrc.startswith("not scored") and s["set"] != "office":
            # the owner did not download cells with no main-analysis site; R2 (OSM-sourced) sites are not offices
            nsrc = f"not scored — no owner download (cell has no main-analysis site; {s['set']} site)"
        r.update({"heat_nasa_cell_lat": n.get("cell_lat", ""), "heat_nasa_cell_lon": n.get("cell_lon", ""),
                  "heat_nasa_tx_p90_c": n.get("tx_p90_c", ""), "heat_nasa_tx90_days_1991_2020": n.get("tx90_days_base_mean", ""),
                  "heat_nasa_tx90_days_2020_2025": n.get("tx90_days_recent_mean", ""),
                  "heat_nasa_score": n.get("heat_score", ""), "heat_nasa_tercile_cut": round(qn, 3) if qn is not None else "",
                  "heat_nasa_exposed": (int(ns >= qn) if (ns is not None and qn is not None) else nsrc),
                  "heat_nasa_source": nsrc})
        # split the robustness buffer into its two sources: A7 (grade A at 500 m) and OD-2 (grade B circles at 5 km)
        rob, mainx = r.get("rf100_rob_exposed", ""), r.get("rf100_exposed", "")
        is_b_circle = r.get("rating") == "B" and "circle" in r.get("buffer_main", "")
        r["rf100_A7_500m_exposed"] = rob if r.get("rating") == "A" else mainx
        r["rf100_B_5km_exposed"] = rob if is_b_circle else mainx
        p = pop.get(fid, {})
        r.update({"pop_in_main_buffer": p.get("pop_in_main_buffer", ""), "pop_within_5km": p.get("pop_within_5km", "")})
        rows.append(r)
    H.write(rows, P / "site_hazards.csv")
    print("site_hazards rows", len(rows), "| heat tercile cut (ERA5)", q, "| NASA robustness cut", qn)

    # ---------------- firm scores
    by = {}
    for r in rows:
        by.setdefault(r["ticker"], []).append(r)
    mos = H.Mosaic([H.WORLDPOP]) if H.WORLDPOP.exists() else None
    frame = {x["ticker"]: x for x in csv.DictReader((I / "ngx_census_frame.csv").open(newline="", encoding="utf-8"))}
    fac = list(csv.DictReader((P / "facilities.csv").open(newline="", encoding="utf-8")))
    disp = {}
    for x in fac:
        if x["asset_type"] == "dispersed":
            disp.setdefault(x["ticker"], []).append(x)
    states = {r["state"]: r for r in csv.DictReader((I / "phase3_states.csv").open(newline="", encoding="utf-8"))} if (I / "phase3_states.csv").exists() else {}
    census = [t for t, x in frame.items() if x["census_stratum"] in ("main", "robustness_stratum") and x["document_test"].startswith("passed")]
    for t in census:
        by.setdefault(t, [])
    out = []
    for t, rs in sorted(by.items()):
        main = [x for x in rs if x["site_set"] == "main"]
        r2 = [x for x in rs if x["site_set"] in ("main", "R2")]
        row = {"ticker": t, "census_stratum": frame.get(t, {}).get("census_stratum", ""), "n_main_sites": len(main),
               "n_r2_sites": len(r2), "n_office_sites": sum(x["site_set"] == "office" for x in rs)}

        def agg(prefix, sel, col, maxcol=None):
            v = [fnum(x[col]) for x in sel if fnum(x.get(col)) is not None]
            if not v:
                row.update({f"{prefix}_E_share": "", f"{prefix}_E_any": ""}); return
            row.update({f"{prefix}_E_share": round(sum(v) / len(v), 4), f"{prefix}_E_any": int(max(v) > 0)})
            if maxcol:
                m = [fnum(x[maxcol]) for x in sel if fnum(x.get(maxcol)) is not None]
                row[f"{prefix}_E_max"] = round(max(m), 4) if m else ""

        agg("rf100", main, "rf100_exposed", "rf100_share")
        row["rf100_E_max_depth_m"] = max([fnum(x["rf100_maxdepth_m"]) for x in main if fnum(x.get("rf100_maxdepth_m")) is not None], default="")
        agg("heat", main, "heat_exposed", "heat_score")
        agg("coastal", main, "coastal_rp100_exposed", "coastal_rp100_share")
        agg("water", main, "water_stress_exposed", "water_stress_raw")
        if main:
            prim = [row["rf100_E_share"], row["heat_E_share"]]
            row["combined_index_primary2"] = round(sum(prim) / 2, 4) if all(p != "" for p in prim) else ""
            allh = [row["rf100_E_share"], row["heat_E_share"], row["coastal_E_share"], row["water_E_share"]]
            row["combined_index"] = round(sum(allh) / 4, 4) if all(p != "" for p in allh) else ""
            row["combined_index_status"] = "mean of the four hazard-specific E_share values (OD-8); heat from ERA5 (A10 method, A11 hourly time series)"
        # robustness
        agg("rob_A7_500m_rf100", main, "rf100_A7_500m_exposed")
        agg("rob_B5km_rf100", main, "rf100_B_5km_exposed")
        agg("rob_bothbuffers_rf100", main, "rf100_rob_exposed")
        agg("rob_rf10", main, "rf10_exposed")
        agg("rob_rf500", main, "rf500_exposed")
        agg("rob_depth05_rf100", main, "rf100_exposed_ge0.5m")
        agg("rob_R2_rf100", r2, "rf100_exposed")
        agg("rob_nopermwater_rf100", main, "rf100_nopermwater_exposed")
        agg("rob_nasa_heat", main, "heat_nasa_exposed", "heat_nasa_score")
        if main and row.get("rob_nasa_heat_E_share", "") != "":
            alln = [row["rf100_E_share"], row["rob_nasa_heat_E_share"], row["coastal_E_share"], row["water_E_share"]]
            row["rob_nasa_heat_combined_index"] = round(sum(alln) / 4, 4) if all(p != "" for p in alln) else ""
        agg("rob_depth05_coastal", main, "coastal_rp100_exposed_ge0.5m")
        # population (union of 5 km circles / main buffers of exposed sites)
        if mos is not None and main:
            for lab, cond in (("rf100", lambda x: x["rf100_exposed"] == "1"), ("heat", lambda x: str(x["heat_exposed"]) == "1"),
                              ("either", lambda x: x["rf100_exposed"] == "1" or str(x["heat_exposed"]) == "1"),
                              ("coastal", lambda x: str(x["coastal_rp100_exposed"]) == "1"),
                              ("water", lambda x: str(x["water_stress_exposed"]) == "1")):
                ex = [sites[x["facility_id"]] for x in main if cond(x)]
                if ex:
                    u5 = unary_union([s["g_pop5"] for s in ex]); ub = unary_union([s["g_main"] for s in ex])
                    row[f"pop5km_exposed_{lab}"] = round(float(np.nansum(mos.values(u5))), 0)
                    row[f"popbuffer_exposed_{lab}"] = round(float(np.nansum(mos.values(ub))), 0)
                else:
                    row[f"pop5km_exposed_{lab}"] = row[f"popbuffer_exposed_{lab}"] = 0
        d = disp.get(t, [])
        if d:
            with_states = [x for x in d if x["state_as_written"]]
            row["n_dispersed_assets"] = len(d)
            row["dispersed_status"] = ("not scored: the design (e6) defines the dispersed score as the share of operating states "
                                       "that are exposed, but does not define when a state counts as exposed")
            if with_states:
                desc = []
                for x in with_states:
                    names = [n.strip() for n in x["state_as_written"].split(";")]
                    vals = [f"{n}={states[('Federal Capital Territory' if n == 'FCT' else n)]['rf100_share_area']}"
                            for n in names if ('Federal Capital Territory' if n == 'FCT' else n) in states]
                    desc.append(f"{x['facility_id']}: " + ", ".join(vals))
                row["dispersed_state_rf100_area_share_descriptive"] = " | ".join(desc)
        if not main:
            row["note"] = ("not scored: no main-analysis point site with a coordinate"
                           + ("" if rs else "; no point site with a coordinate at all"))
        out.append(row)
    cols = []
    for r in out:
        for k in r:
            if k not in cols:
                cols.append(k)
    with (P / "firm_exposure.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        for r in out:
            w.writerow({c: r.get(c, "") for c in cols})
    print("firms", len(out), "| scored", sum(1 for r in out if r["n_main_sites"]))


if __name__ == "__main__":
    main()
