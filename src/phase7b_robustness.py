"""Phase 7b: the design-h robustness checks that Phase 5 did not run (docs/phase7_verification.md section 7).
DESCRIPTIVE ONLY (A21): effect sizes with 95% intervals; nothing is called supported, rejected or significant.

usage:
  phase7b_robustness.py cache             paragraph pass -> data/interim/phase7b_paragraph_cache.csv of hazard families and site names per paragraph
  phase7b_robustness.py desc              descriptive claims 1-4 and 7 under each check -> outputs/tables/robustness_7b_descriptive.csv
  phase7b_robustness.py models CHECK...   H1 (OLS + fractional logit point), H2 (Y3d) and H3 (main) under each check
                                          -> outputs/tables/robustness_7b_models.csv (rows for CHECK replaced)
  CHECK in: baseline rp10 rp500 depth05 b5km no_fs dwl fp20 fp20_alt loso

Estimators as in src/phase5_models.py (A22): OLS with the unrestricted wild cluster bootstrap (Webb weights,
percentile-t, 9,999 replications, seed 20261118); H2 standardised OLS blocks with firm pairs bootstrap (9,999);
H3 within-firm SD-scaled trends with the wild cluster bootstrap. The fractional logit is reported as point estimate
with a CR1 cluster interval only: its firm pairs bootstrap failed in 80-86% of draws in Phase 5, and is not repeated.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase5_models import design, ols, cr1_se, fit_glm, B, SEED, WEBB  # noqa: E402
from phase5_sites import site_matchers, sites_named, HAZ  # noqa: E402

P, I, TAB = ROOT / "data" / "processed", ROOT / "data" / "interim", ROOT / "outputs" / "tables"
CACHE = I / "phase7b_paragraph_cache.csv"
DWL = ["MULTITREX", "UNIONDICON"]
RF_VARIANT = {"baseline": ("rf100_E_share", "rf100_exposed"), "rp10": ("rob_rf10_E_share", "rf10_exposed"),
              "rp500": ("rob_rf500_E_share", "rf500_exposed"), "depth05": ("rob_depth05_rf100_E_share", "rf100_exposed_ge0.5m"),
              "b5km": ("rob_B5km_rf100_E_share", "rf100_B_5km_exposed")}
csv.field_size_limit(10 ** 8)


# ------------------------------------------------------------------ paragraph cache
def cache():
    firms, ctx = site_matchers()
    H = json.load(open(ROOT / "config" / "dictionary_hazard.json", encoding="utf-8"))
    fam = {g: re.compile("|".join(p for t in H["terms"] if t["hazard_group"] == g for p in t["patterns"]), re.I)
           for g in {t["hazard_group"] for t in H["terms"]}}
    out = []
    with open(I / "paragraphs.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            named = sites_named(r["text"], r["firm"], firms, ctx)
            narr = r["model_eligible"] == "1" and r["section"] == "narrative"
            hit = [g for g, rx in fam.items() if rx.search(r["text"])] if narr else []
            if named or hit:
                out.append({"firm": r["firm"], "year": r["year"], "doc_type": r["doc_type"], "narrative": int(narr),
                            "families": "|".join(sorted(hit)), "sites": "|".join(sorted(named))})
    pd.DataFrame(out).to_csv(CACHE, index=False)
    print("cached rows", len(out))


# ------------------------------------------------------------------ descriptive claims
def desc():
    o = pd.read_csv(P / "outcomes_firm_year.csv")
    o = o[~((o.firm == "NNFM") & (o.year == 2020))]
    m = o[o.stratum == "main"]
    sh = pd.read_csv(P / "site_hazards.csv")
    c = pd.read_csv(CACHE, dtype={"families": str, "sites": str}).fillna("")
    c = c[~((c.firm == "NNFM") & (c.year == 2020))]
    fsonly = set(map(tuple, m[m.fs_only == 1][["firm", "year"]].values))
    unsc = pd.read_csv(TAB / "unscored_firms_reasons.csv")
    pc = pd.read_csv(P / "policy_codes_firm_year.csv")
    pc = pc[~((pc.firm == "NNFM") & (pc.year == 2020))]
    rows = []

    def add(check, claim, quantity, value, baseline=""):
        rows.append({"check": check, "claim": claim, "quantity": quantity, "value": value, "baseline_value": baseline})

    def claims(check, mm, cc, rfcol, pcc, unsc_firms):
        # claim 1
        sc = mm[mm.n_scored > 0]
        add(check, 1, "firm-years with narrative text / of which no hazard-tagged paragraph",
            f"{len(sc)} / {int((sc.n_tagged == 0).sum())}", "97 / 68")
        add(check, 1, "mean Y3d (share of narrative paragraphs hazard-tagged)", round(sc.Y3d.mean(), 4), "about 0.003")
        # claims 2-3: main census, main point sites
        s = sh[(sh.site_set == "main") & (sh.census_stratum == "main") & sh.ticker.isin(mm.firm.unique())].copy()
        s["e_rf"] = s[rfcol].fillna(0).astype(int)
        s["e_any"] = ((s.e_rf == 1) | (s.coastal_rp100_exposed == 1) | (s.heat_exposed == 1) | (s.water_stress_exposed == 1)).astype(int)
        named_any = set("|".join(cc.sites).split("|")) - {""}
        named_haz = set("|".join(cc[(cc.families != "")].sites).split("|")) - {""}
        ex = s[s.e_any == 1]
        add(check, 2, "exposed main point sites / named anywhere / named in a hazard-tagged paragraph (mechanical)",
            f"{len(ex)} / {int(ex.facility_id.isin(named_any).sum())} / {int(ex.facility_id.isin(named_haz).sum())}", "51 / 50 / 7")
        add(check, 2, "exposed main point sites named in a genuine site physical-risk statement (Phase 7 reading)",
            "0 (the only genuine statement, Seplat FY2025 OML 40, concerns a licence area)", "0")
        famfirm = defaultdict(set)
        for _, r in cc[cc.families != ""].iterrows():
            for g in r.families.split("|"):
                famfirm[g].add(r.firm)
        for h, col in (("river flood", "e_rf"), ("heat", "heat_exposed")):
            fams = HAZ["rf100" if h == "river flood" else "heat"][1]
            ef = set(s[s[col] == 1].ticker)
            users = {f for f in ef if any(f in famfirm[g] for g in fams)}
            add(check, 3 if h == "heat" else 2, f"firms with a {h}-exposed site / of which ever use {h} terms",
                f"{len(ef)} / {len(users)}", "15 / 2" if h == "heat" else "21 / 7")
        # claim 4
        u = unsc[unsc.firm.isin(unsc_firms)] if "firm" in unsc.columns else unsc
        if "reason" in u.columns:
            add(check, 4, "unscored firms / of which generic facility description only (C1)",
                f"{len(u)} / {int(u.reason.astype(str).str.startswith('C1').sum())}", "29 / 22")
        # claim 7
        lat = pcc.sort_values("year").groupby("firm").tail(1)
        x = lat[["P1", "P2", "P3", "P4", "P5"]].sum(axis=1)
        add(check, 7, "firms (latest year held) / with all five elements / with none",
            f"{len(lat)} / {int((x == 5).sum())} / {int((x == 0).sum())}", "56 / 2 / 50")

    for chk, (_, rfcol) in RF_VARIANT.items():
        claims(chk, m, c, rfcol, pc, set(unsc.iloc[:, 0]))
    # FS-only firm-years excluded
    keep = lambda df: df[[(f, y) not in fsonly for f, y in zip(df.firm, df.year)]]
    mm = m[m.fs_only == 0]
    claims("no_fs", mm, keep(c), "rf100_exposed", keep(pc), set(unsc.iloc[:, 0]) & set(mm.firm))
    # DWL firms excluded
    claims("dwl", m[~m.firm.isin(DWL)], c[~c.firm.isin(DWL)], "rf100_exposed", pc[~pc.firm.isin(DWL)],
           set(unsc.iloc[:, 0]) - set(DWL))
    # robustness stratum (separate; no controls collected)
    r = o[o.stratum != "main"]
    rs = sh[(sh.site_set == "main") & (sh.census_stratum != "main")]
    rex = rs[(rs.rf100_exposed == 1) | (rs.coastal_rp100_exposed == 1) | (rs.heat_exposed == 1) | (rs.water_stress_exposed == 1)]
    cr = c[c.firm.isin(r.firm)]
    named_haz = set("|".join(cr[cr.families != ""].sites).split("|")) - {""}
    add("stratum", "1", "firm-years / firms / with no hazard-tagged paragraph / mean Y3d",
        f"{len(r)} / {r.firm.nunique()} ({', '.join(sorted(r.firm.unique()))}) / {int((r[r.n_scored > 0].n_tagged == 0).sum())} of {int((r.n_scored > 0).sum())} / {round(r.Y3d.mean(), 4)}")
    add("stratum", "2", "exposed main point sites / named in a hazard-tagged paragraph", f"{len(rex)} / {int(rex.facility_id.isin(named_haz).sum())}")
    add("stratum", "-", "doc types", "; ".join(f"{a} {b} {t}" for a, b, t in r[["firm", "year", "doc_types"]].values))
    # dispersed-asset firms (main census; no exposure score defined, e6)
    e = pd.read_csv(P / "firm_exposure.csv")
    disp = e[(e.census_stratum == "main") & (e.n_dispersed_assets > 0)]
    only = set(disp[disp.n_main_sites == 0].ticker); mixed = set(disp[disp.n_main_sites > 0].ticker)
    for lab, fs in (("dispersed only", only), ("dispersed + point sites", mixed), ("point sites only / none", set(m.firm) - only - mixed)):
        d = m[m.firm.isin(fs) & (m.n_scored > 0)]
        lat = pc[pc.firm.isin(fs)].sort_values("year").groupby("firm").tail(1)
        x = lat[["P1", "P2", "P3", "P4", "P5"]].sum(axis=1)
        add("dispersed", "1/7", f"{lab}: firms / firm-years with narrative / with no hazard paragraph / mean Y3d / latest-year all five P1-P5 / none",
            f"{len(fs & set(m.firm))} / {len(d)} / {int((d.n_tagged == 0).sum())} / {round(d.Y3d.mean(), 4)} / "
            f"{int((x == 5).sum())} ({', '.join(sorted(lat[x == 5].firm))}) / {int((x == 0).sum())}")
    add("dispersed", "-", "firms", f"dispersed only: {', '.join(sorted(only))}; mixed: {', '.join(sorted(mixed))}")
    pd.DataFrame(rows).to_csv(TAB / "robustness_7b_descriptive.csv", index=False)
    print(pd.DataFrame(rows)[["check", "claim", "quantity", "value"]].to_string(index=False, max_colwidth=90))


# ------------------------------------------------------------------ models
def wcb(y, X, g, j, rng):
    """As phase5_models.wcb_ols (unrestricted, Webb, percentile-t); X is fixed, so (X'X)^-1 is computed once."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    XtXi = np.linalg.pinv(X.T @ X); G, idx = np.unique(g, return_inverse=True)
    n, k = X.shape; adj = len(G) / (len(G) - 1) * (n - 1) / max(n - k, 1)
    H = XtXi @ X.T

    def fit(yy):
        b = H @ yy; u = yy - X @ b
        S = np.zeros((len(G), k)); np.add.at(S, idx, X * u[:, None])
        V = adj * XtXi @ (S.T @ S) @ XtXi
        return b, np.sqrt(max(V[j, j], 0))
    b, se = fit(y); u = y - X @ b
    t = np.empty(B)
    for r in range(B):
        w = rng.choice(WEBB, len(G))[idx]
        bs, ses = fit(X @ b + u * w)
        t[r] = (bs[j] - b[j]) / ses
    lo, hi = np.quantile(t, [0.975, 0.025])
    return b[j], b[j] - lo * se, b[j] - hi * se


def h1(s, yv, ev, controls, k):
    s = s.dropna(subset=[yv, ev]); y = s[yv].astype(float).values; g = s.firm.values
    row = {"model": "H1", "outcome": yv, "term": ev, "n": len(s), "firms": s.firm.nunique(), "nonzero": int((y > 0).sum())}
    for fe, tag in ((["year", "sector"], "year+sector FE"), (["year"], "year FE (sector dropped)"), ([], "no FE")):
        X = design(s, [ev] + controls, fe)
        if ev in X.columns and np.linalg.matrix_rank(X.values) == X.shape[1] and len(s) - X.shape[1] >= 1:
            break
    else:
        row["note"] = "not estimable (exposure constant or design rank-deficient)"; return row
    j = list(X.columns).index(ev)
    b, lo, hi = wcb(y, X.values, g, j, np.random.default_rng(SEED + k))
    row.update({"spec": tag, "estimate": round(b, 4), "low": round(lo, 4), "high": round(hi, 4), "interval": "OLS, wild cluster bootstrap"})
    try:
        import statsmodels.api as sm
        mc = sm.GLM(y, X.values, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(g)[0]})
        fit_glm(y, X.values)
        row["fraclogit"] = f"{mc.params[j]:.3f} (CR1 {mc.conf_int()[j][0]:.3f} to {mc.conf_int()[j][1]:.3f})"
    except Exception as ex:
        row["fraclogit"] = f"not estimable: {ex}"
    return row


def h2(s, yv, expo, inst, k):
    s = s.dropna(subset=[yv]).copy()
    dropped = [v for v in inst if s[v].astype(float).std() == 0]  # e.g. assurance once Dangote (Industrial Goods) is left out
    inst = [v for v in inst if v not in dropped]
    z = lambda v: (v - v.mean()) / v.std() if v.std() > 0 else v * 0
    for v in expo + inst:
        s[v + "_z"] = z(s[v].astype(float))
    base = design(s, ["fs_only"], ["year"])
    sec = pd.get_dummies(s.sector.astype(str), prefix="sector", drop_first=True, dtype=float)
    A = base.join(s[[v + "_z" for v in expo]]); Bk = base.join(s[[v + "_z" for v in inst]]).join(sec); C = Bk.join(s[[v + "_z" for v in expo]])
    note = f"constant in sample, dropped: {dropped}" if dropped else ""
    if len(s) - C.shape[1] < 1 or np.linalg.matrix_rank(C.values) < C.shape[1]:
        note = "; ".join(x for x in (note, "sector FE dropped from the institutional block") if x)
        Bk = base.join(s[[v + "_z" for v in inst]]); C = Bk.join(s[[v + "_z" for v in expo]])
    y = z(s[yv].astype(float)).values; g = s.firm.values

    def r2(yy, X):
        b, u = ols(yy, X); return 1 - (u @ u) / ((yy - yy.mean()) @ (yy - yy.mean()))

    def stats(ix):
        yy = y[ix]; rb, rc, ra = r2(yy, Bk.values[ix]), r2(yy, C.values[ix]), r2(yy, A.values[ix])
        return rc - rb, rc - ra, (rc - rb) - (rc - ra)
    pt = stats(np.arange(len(y)))
    rng = np.random.default_rng(SEED + 500 + k); G = np.unique(g); rws = {c: np.where(g == c)[0] for c in G}
    bs = []
    for _ in range(B):
        try:
            bs.append(stats(np.concatenate([rws[c] for c in rng.choice(G, len(G))])))
        except Exception:
            pass
    bs = np.array(bs); bad = int(np.isnan(bs).any(axis=1).sum()) + B - len(bs)
    out = []
    for i, nm in enumerate(["R2 added by exposure", "R2 added by institutional", "difference (exposure - institutional)"]):
        out.append({"model": "H2", "outcome": yv, "term": nm, "n": len(s), "firms": s.firm.nunique(), "estimate": round(pt[i], 4),
                    "low": round(np.nanquantile(bs[:, i], 0.025), 4), "high": round(np.nanquantile(bs[:, i], 0.975), 4),
                    "interval": "firm pairs bootstrap", "note": "; ".join(x for x in (note, f"{bad} invalid draws" if bad else "") if x)})
    return out


def h3(s, k):
    s = s[s.h3_main == 1]; kk = s.groupby("firm").year.nunique(); s = s[s.firm.isin(kk[kk >= 2].index)].dropna(subset=["Y3d", "Y4r"]).copy()
    s["t"] = s.year - 2020; sa, sb = s.Y3d.std(), s.Y4r.std()
    long = pd.concat([pd.DataFrame({"firm": s.firm, "eq": "a", "y": s.Y3d / sa, "t": s.t}),
                      pd.DataFrame({"firm": s.firm, "eq": "b", "y": s.Y4r / sb, "t": s.t})])
    X = pd.get_dummies(long.firm + "_" + long["eq"], dtype=float)
    X["t_a"] = long.t * (long["eq"] == "a"); X["t_b"] = long.t * (long["eq"] == "b")
    Xv = X.values; y = long.y.values; g = long.firm.values; ja, jb = Xv.shape[1] - 2, Xv.shape[1] - 1
    Xd = Xv.copy(); Xd[:, jb] = Xv[:, ja] + Xv[:, jb]
    rng = np.random.default_rng(SEED + 900 + k); out = []
    for nm, XX, j in (("tau Y3d", Xv, ja), ("tau Y4r", Xv, jb), ("difference tau(Y3d) - tau(Y4r)", Xd, ja)):
        b, lo, hi = wcb(y, XX, g, j, rng)
        out.append({"model": "H3", "outcome": "Y3d vs Y4r (SD per year)", "term": nm, "n": len(s), "firms": s.firm.nunique(),
                    "nonzero": int((s.Y4r > 0).sum()), "estimate": round(b, 4), "low": round(lo, 4), "high": round(hi, 4),
                    "interval": "wild cluster bootstrap"})
    return out


CONTROLS = ["log_total_assets", "foreign_parent_50", "assurance", "big4", "fs_only"]
INST = ["log_total_assets", "foreign_parent_50", "assurance", "big4"]


def run_check(chk):
    d = pd.read_csv(P / "analysis_firm_year.csv")
    h12 = d[d.has_exposure == 1].dropna(subset=["log_total_assets", "big4"])
    rows = []

    def tag(rs, label):
        for r in rs:
            r["check"] = label
        rows.extend(rs)

    def block(label, s, rf="rf100_E_share", ctl=CONTROLS, inst=INST, dh3=None, y4s=True, k0=0):
        tag([h1(s, "Y3d", rf, ctl, k0 + 1), h1(s, "Y3d", "heat_E_share", ctl, k0 + 2)], label)
        if y4s:
            tag([h1(s, "Y4s", rf, ctl, k0 + 3)], label)
        tag(h2(s, "Y3d", [rf, "heat_E_share"], inst, k0), label)
        if dh3 is not None:
            tag(h3(dh3, k0), label)

    if chk == "baseline":
        block("baseline (re-computed with this script)", h12, dh3=d)
    elif chk in ("rp10", "rp500", "depth05", "b5km"):
        block(chk, h12, rf=RF_VARIANT[chk][0])
    elif chk == "no_fs":
        block("excluding FS-only firm-years", h12[h12.fs_only == 0], dh3=d[d.fs_only == 0])
    elif chk == "dwl":
        inside = {"H1/H2 sample": sorted(set(DWL) & set(h12.firm)), "H3 sample": sorted(set(DWL) & set(d[d.h3_main == 1].firm))}
        rows.append({"check": "excluding DWL firms", "model": "H1/H2/H3", "note": f"DWL firms in model samples: {inside}; models unchanged"})
    elif chk in ("fp20", "fp20_alt"):
        s = h12.copy()
        if chk == "fp20_alt":
            s.loc[(s.firm == "SEPLAT") & (s.year == 2025), "foreign_parent_20"] = 1
        c20 = [x if x != "foreign_parent_50" else "foreign_parent_20" for x in CONTROLS]
        i20 = [x if x != "foreign_parent_50" else "foreign_parent_20" for x in INST]
        block("20% foreign-parent threshold" + (" (Seplat FY2025 coded 1, pre-sale reading)" if chk == "fp20_alt" else ""), s, ctl=c20, inst=i20)
    elif chk == "loso":
        for i, sec in enumerate(sorted(h12.sector.unique())):
            block(f"leave out sector: {sec}", h12[h12.sector != sec], dh3=d[d.sector != sec], y4s=False, k0=10 * (i + 1))
    out = TAB / "robustness_7b_models.csv"
    old = pd.read_csv(out) if out.exists() else pd.DataFrame()
    new = pd.DataFrame(rows)
    if len(old):
        old = old[~old.check.isin(new.check.unique())]
    cols = ["check", "model", "outcome", "term", "n", "firms", "nonzero", "spec", "estimate", "low", "high", "interval", "fraclogit", "note"]
    pd.concat([old, new]).reindex(columns=cols).to_csv(out, index=False)
    print(new.reindex(columns=cols[:-1] + ["note"]).drop(columns=["interval"]).to_string(index=False, max_colwidth=60))


if __name__ == "__main__":
    if sys.argv[1] == "cache":
        cache()
    elif sys.argv[1] == "desc":
        desc()
    else:
        for c in sys.argv[2:]:
            run_check(c)
