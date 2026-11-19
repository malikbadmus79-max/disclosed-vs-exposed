"""Phase 5: analysis datasets and the H1-H3 models (design h as amended: A16, A20-A23). DESCRIPTIVE ONLY: effect sizes
with 95% intervals; no test result is claimed.

data            -> data/processed/analysis_firm_year.csv, data/processed/analysis_firm.csv, outputs/tables/sample_flow.csv
h1 [i j]        -> outputs/tables/h1_results.csv (appends; specs i..j-1 of SPECS_H1, so it can run in short chunks)
h2              -> outputs/tables/h2_results.csv
h3              -> outputs/tables/h3_results.csv

Estimators (A22): fractional logit (GLM binomial, logit link; CR1 cluster SEs; firm pairs bootstrap, percentile) and
OLS (wild cluster bootstrap, Webb six-point weights, unrestricted, percentile-t). 9,999 replications, seed 20261118.
If a specification is not estimable (rank deficient, fewer residual degrees of freedom than 1, non-convergence or
separation), sector fixed effects are dropped, then year fixed effects; the specification actually fitted is reported.
"""
import csv
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
TAB = ROOT / "outputs" / "tables"
B = 9999
SEED = 20261118
WEBB = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
CONTROLS = ["log_total_assets", "foreign_parent_50", "assurance", "big4", "fs_only"]


# ------------------------------------------------------------------ data
def build_data():
    TAB.mkdir(parents=True, exist_ok=True)
    o = pd.read_csv(P / "outcomes_firm_year.csv")
    e = pd.read_csv(P / "firm_exposure.csv").rename(columns={"ticker": "firm"})
    c = pd.read_csv(ROOT / "data" / "interim" / "controls_firm_year.csv")
    cen = pd.read_csv(ROOT / "data" / "interim" / "ngx_census_frame.csv")[["ticker", "sector_provisional", "census_stratum", "document_test"]]
    cen = cen.rename(columns={"ticker": "firm", "sector_provisional": "sector"})
    flow = []
    d = o[o.stratum == "main"].copy(); flow.append(("main-census firm-years with documents", len(d), d.firm.nunique()))
    d = d[~((d.firm == "NNFM") & (d.year == 2020))]; flow.append(("minus NNFM FY2020 (A23: wrong issuer)", len(d), d.firm.nunique()))
    d = d.merge(cen[["firm", "sector"]], on="firm", how="left")
    d = d.merge(e, on="firm", how="left")
    d["has_exposure"] = d.combined_index.notna().astype(int)
    d = d.merge(c.drop(columns=["doc"]), on=["firm", "year"], how="left")
    d.to_csv(P / "analysis_firm_year.csv", index=False)
    h12 = d[d.has_exposure == 1]; flow.append(("H1/H2: firm-years of firms with an exposure score", len(h12), h12.firm.nunique()))
    h12c = h12.dropna(subset=["log_total_assets", "big4"]); flow.append(("H1/H2: with all controls", len(h12c), h12c.firm.nunique()))
    y4s = h12c[h12c.Y4s.notna()]; flow.append(("H1 primary (Y4s defined: >= 1 hazard-tagged paragraph)", len(y4s), y4s.firm.nunique()))
    flow.append(("  of which Y4s > 0", int((y4s.Y4s > 0).sum()), y4s[y4s.Y4s > 0].firm.nunique()))
    h3 = d[d.h3_main == 1]; k = h3.groupby("firm").year.nunique(); h3 = h3[h3.firm.isin(k[k >= 2].index)]
    flow.append(("H3: main-analysis firm-years of firms with >= 2 main years (A16)", len(h3), h3.firm.nunique()))
    h3r = d.copy(); k = h3r.groupby("firm").year.nunique(); h3r = h3r[h3r.firm.isin(k[k >= 2].index)]
    flow.append(("H3 robustness: pre-listing years included", len(h3r), h3r.firm.nunique()))
    pd.DataFrame(flow, columns=["step", "firm_years", "firms"]).to_csv(TAB / "sample_flow.csv", index=False)
    # firm-level file (for charts and H4 context): exposure + mean outcomes over the firm's main-analysis years
    f = d.groupby("firm").agg(sector=("sector", "first"), years=("year", "nunique"), n_scored=("n_scored", "sum"),
                              Y3d_mean=("Y3d", "mean"), Y4d_total=("Y4d", "sum"), Y4d_any=("Y4d_any", "max"),
                              Y1_cb_mean=("Y1_cb", "mean")).reset_index()
    f = f.merge(e, on="firm", how="left")
    f.to_csv(P / "analysis_firm.csv", index=False)
    for r in flow:
        print(r)


# ------------------------------------------------------------------ helpers
def design(df, xvars, fe):
    X = df[xvars].astype(float).copy()
    for col in fe:
        X = X.join(pd.get_dummies(df[col].astype(str), prefix=col, drop_first=True, dtype=float))
    X.insert(0, "const", 1.0)
    X = X.loc[:, (X.std() > 0) | (X.columns == "const")]
    return X


def ols(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b, y - X @ b


def cr1_se(X, u, g):
    n, k = X.shape
    XtXi = np.linalg.pinv(X.T @ X)
    meat = np.zeros((k, k))
    G = np.unique(g)
    for c in G:
        s = X[g == c].T @ u[g == c]
        meat += np.outer(s, s)
    adj = len(G) / (len(G) - 1) * (n - 1) / max(n - k, 1)
    return np.sqrt(np.diag(adj * XtXi @ meat @ XtXi))


def wcb_ols(y, X, g, j, rng):
    """Unrestricted wild cluster bootstrap (Webb), percentile-t 95% CI for coefficient j."""
    b, u = ols(y, X); se = cr1_se(X, u, g)
    G = np.unique(g); idx = np.searchsorted(G, g)
    t = np.empty(B)
    for r in range(B):
        w = rng.choice(WEBB, len(G))[idx]
        ys = X @ b + u * w
        bs, us = ols(ys, X)
        t[r] = (bs[j] - b[j]) / cr1_se(X, us, g)[j]
    lo, hi = np.quantile(t, [0.975, 0.025])
    return b[j], se[j], b[j] - lo * se[j], b[j] - hi * se[j]


def fit_glm(y, X, binary=False):
    import statsmodels.api as sm
    m = sm.GLM(y, X, family=sm.families.Binomial()).fit(maxiter=100)
    if not m.converged:
        raise RuntimeError("no convergence")
    if binary:
        p = m.fittedvalues
        if ((p < 1e-6) | (p > 1 - 1e-6)).any():
            raise RuntimeError("(quasi-)separation")
    return m


def pairs_boot_glm(y, X, g, j, rng, binary=False):
    G = np.unique(g); rows = {c: np.where(g == c)[0] for c in G}
    est, fail = [], 0
    for r in range(B):
        take = np.concatenate([rows[c] for c in rng.choice(G, len(G))])
        Xs = X[take]; keep = Xs.std(0) > 0; keep[0] = True
        if not keep[j] or np.linalg.matrix_rank(Xs[:, keep]) < keep.sum():
            fail += 1; continue  # exposure constant or design rank-deficient in this draw: counted as a failure
        try:
            m = fit_glm(y[take], Xs[:, keep], binary)
            est.append(m.params[list(np.where(keep)[0]).index(j)])
        except Exception:
            fail += 1
    est = np.array(est)
    return (np.quantile(est, 0.025), np.quantile(est, 0.975)) if len(est) > 100 else (np.nan, np.nan), fail


# ------------------------------------------------------------------ H1
EXPO_MAIN = [("rf100_E_share", "river flood E_share (primary)"), ("heat_E_share", "heat E_share, ERA5 (primary)"),
             ("combined_index", "combined index (secondary)"), ("coastal_E_share", "coastal flood E_share"),
             ("water_E_share", "water stress E_share")]
SPECS_H1 = (
    [("main", "Y4s", e, lab, "fraclogit") for e, lab in EXPO_MAIN]
    + [("secondary", "Y3d", e, lab, "fraclogit") for e, lab in EXPO_MAIN[:3]]
    + [("secondary", "Y4d_any", e, lab, "logit") for e, lab in EXPO_MAIN[:3]]
    + [("robustness: NASA POWER heat", "Y4s", "rob_nasa_heat_E_share", "heat E_share, NASA POWER", "fraclogit"),
       ("robustness: A7 500 m buffers", "Y4s", "rob_A7_500m_rf100_E_share", "river flood E_share, A7 500 m", "fraclogit"),
       ("robustness: A8 no permanent water", "Y4s", "rob_nopermwater_rf100_E_share", "river flood E_share, A8", "fraclogit"),
       ("robustness: refined dictionary", "Y4s_refined", "rf100_E_share", "river flood E_share (primary)", "fraclogit"),
       ("robustness: refined dictionary", "Y4s_refined", "heat_E_share", "heat E_share, ERA5 (primary)", "fraclogit"),
       ("robustness: refined dictionary", "Y3d_refined", "rf100_E_share", "river flood E_share (primary)", "fraclogit"),
       ("exploratory ClimateBERT (unvalidated)", "Y2_cb", "rf100_E_share", "river flood E_share (primary)", "fraclogit"),
       ("exploratory ClimateBERT (unvalidated)", "Y2_cb", "heat_E_share", "heat E_share, ERA5 (primary)", "fraclogit")]
)


def h1(i0, i1):
    d = pd.read_csv(P / "analysis_firm_year.csv")
    d = d[(d.has_exposure == 1)].dropna(subset=["log_total_assets", "big4"])
    out_path = TAB / "h1_results.csv"
    new = not out_path.exists()
    with open(out_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["label", "outcome", "exposure", "exposure_label", "estimator", "n", "firms", "nonzero",
                                "fitted_spec", "coef", "cr1_low", "cr1_high", "boot_low", "boot_high", "boot_method",
                                "boot_failures", "ols_coef", "ols_wcb_low", "ols_wcb_high", "instability"])
        if new:
            w.writeheader()
        for k, (label, yv, ev, elab, est) in enumerate(SPECS_H1[i0:i1], start=i0):
            rng = np.random.default_rng(SEED + k)
            s = d.dropna(subset=[yv, ev]).copy()
            y = s[yv].astype(float).values; g = s.firm.values
            row = {"label": label, "outcome": yv, "exposure": ev, "exposure_label": elab, "estimator": est, "n": len(s),
                   "firms": s.firm.nunique(), "nonzero": int((y > 0).sum())}
            notes = []
            if (y > 0).sum() < 10:
                notes.append(f"only {int((y > 0).sum())} non-zero outcomes")
            fitted = None
            for fe, tag in ((["year", "sector"], "controls + year FE + sector FE"), (["year"], "controls + year FE (sector FE dropped)"),
                            ([], "controls only (year and sector FE dropped)")):
                X = design(s, [ev] + CONTROLS, fe)
                if np.linalg.matrix_rank(X.values) < X.shape[1] or len(s) - X.shape[1] < 1 or ev not in X.columns:
                    notes.append(f"not estimable with {tag.split(' (')[0]}: {X.shape[1]} parameters, {len(s)} rows")
                    continue
                try:
                    m = fit_glm(y, X.values, binary=(est == "logit"))
                    fitted = (X, m, tag); break
                except Exception as ex:
                    notes.append(f"{tag}: {ex}")
            if fitted is None:
                row.update({"fitted_spec": "not estimable", "instability": "; ".join(notes)}); w.writerow(row); fh.flush()
                print(k, label, yv, ev, "not estimable"); continue
            X, m, tag = fitted
            j = list(X.columns).index(ev)
            import statsmodels.api as sm
            mc = sm.GLM(y, X.values, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(g)[0]})
            ci = mc.conf_int()[j]
            (bl, bh), fails = pairs_boot_glm(y, X.values, g, j, rng, binary=(est == "logit"))
            if fails > 0.1 * B:
                notes.append(f"{fails} of {B} bootstrap fits failed or lost the exposure column")
            b_ols, se_ols, lo_ols, hi_ols = wcb_ols(y, X.values, g, j, rng)
            row.update({"fitted_spec": tag, "coef": round(m.params[j], 4), "cr1_low": round(ci[0], 4), "cr1_high": round(ci[1], 4),
                        "boot_low": round(bl, 4), "boot_high": round(bh, 4), "boot_method": f"firm pairs bootstrap, {B} reps, percentile",
                        "boot_failures": fails, "ols_coef": round(b_ols, 4), "ols_wcb_low": round(lo_ols, 4),
                        "ols_wcb_high": round(hi_ols, 4), "instability": "; ".join(notes)})
            w.writerow(row); fh.flush()
            print(k, label, yv, ev, tag, "n", len(s), "coef", round(m.params[j], 3), "boot", (round(bl, 3), round(bh, 3)), "fails", fails)


# ------------------------------------------------------------------ H2
def h2():
    d = pd.read_csv(P / "analysis_firm_year.csv")
    d = d[d.has_exposure == 1].dropna(subset=["log_total_assets", "big4"])
    rows = []
    for yv, role in (("Y3d", "primary"), ("Y4s", "secondary"), ("Y3d_refined", "robustness: refined dictionary"),
                     ("Y1_cb", "exploratory ClimateBERT (unvalidated)")):
        s = d.dropna(subset=[yv]).copy()
        z = lambda v: (v - v.mean()) / v.std() if v.std() > 0 else v * 0
        expo = ["rf100_E_share", "heat_E_share"]
        inst = ["log_total_assets", "foreign_parent_50", "assurance", "big4"]
        for v in expo + inst:
            s[v + "_z"] = z(s[v].astype(float))
        base = design(s, ["fs_only"], ["year"])
        sec = pd.get_dummies(s.sector.astype(str), prefix="sector", drop_first=True, dtype=float)
        A = base.join(s[[v + "_z" for v in expo]]); Bk = base.join(s[[v + "_z" for v in inst]]).join(sec)
        C = Bk.join(s[[v + "_z" for v in expo]])
        y = z(s[yv].astype(float)).values; g = s.firm.values
        notes = [] if (s[yv] > 0).sum() >= 10 else [f"only {int((s[yv] > 0).sum())} non-zero outcomes"]
        if len(s) - C.shape[1] < 1 or np.linalg.matrix_rank(C.values) < C.shape[1]:
            notes.append(f"full model not estimable ({C.shape[1]} parameters, {len(s)} rows); sector FE dropped from the institutional block")
            Bk = base.join(s[[v + "_z" for v in inst]]); C = Bk.join(s[[v + "_z" for v in expo]])

        def r2(y, X):
            b, u = ols(y, X); return 1 - (u @ u) / ((y - y.mean()) @ (y - y.mean()))

        def stats(idx):
            yy = y[idx]; a, bb, cc = A.values[idx], Bk.values[idx], C.values[idx]
            ra, rb, rc, r0 = r2(yy, a), r2(yy, bb), r2(yy, cc), r2(yy, base.values[idx])
            return ra - r0, rb - r0, rc - rb, rc - ra, (rc - rb) - (rc - ra), rc

        point = stats(np.arange(len(y)))
        rng = np.random.default_rng(SEED + 500)
        G = np.unique(g); rws = {c: np.where(g == c)[0] for c in G}
        bs = []
        for r in range(B):
            idx = np.concatenate([rws[c] for c in rng.choice(G, len(G))])
            try:
                bs.append(stats(idx))
            except Exception:
                pass
        bs = np.array(bs)
        bad = int(np.isnan(bs).any(axis=1).sum()) + (B - len(bs))
        if bad:
            notes.append(f"{bad} of {B} bootstrap draws invalid (outcome without variance or singular design), ignored")
        names = ["R2 gain, exposure block alone (over year FE + document type)", "R2 gain, institutional block alone",
                 "R2 added by exposure given institutional", "R2 added by institutional given exposure",
                 "difference: exposure-added minus institutional-added", "R2 of the full model"]
        bfull, _ = ols(y, C.values)
        for i, nm in enumerate(names):
            rows.append({"outcome": yv, "role": role, "n": len(s), "firms": s.firm.nunique(), "quantity": nm,
                         "estimate": round(point[i], 4), "boot_low": round(np.nanquantile(bs[:, i], 0.025), 4),
                         "boot_high": round(np.nanquantile(bs[:, i], 0.975), 4), "instability": "; ".join(notes)})
        for v in expo + inst:
            j = list(C.columns).index(v + "_z")
            rows.append({"outcome": yv, "role": role, "n": len(s), "firms": s.firm.nunique(),
                         "quantity": f"standardised coefficient: {v} (full model)", "estimate": round(bfull[j], 4),
                         "boot_low": "", "boot_high": "", "instability": "; ".join(notes)})
        print(yv, "n", len(s), "point", np.round(point, 3))
    pd.DataFrame(rows).to_csv(TAB / "h2_results.csv", index=False)


# ------------------------------------------------------------------ H3
def h3():
    d = pd.read_csv(P / "analysis_firm_year.csv")
    rows = []
    variants = [("main (A16 post-listing years)", "Y3d", "Y4r", True), ("robustness: pre-listing years included (A16)", "Y3d", "Y4r", False),
                ("robustness: refined dictionary", "Y3d_refined", "Y4r_refined", True),
                ("exploratory ClimateBERT version of the design's H3 (unvalidated)", "Y1_cb", "Y4r", True)]
    for label, ya, yb, main_only in variants:
        s = d[d.h3_main == 1] if main_only else d.copy()
        k = s.groupby("firm").year.nunique(); s = s[s.firm.isin(k[k >= 2].index)].dropna(subset=[ya, yb]).copy()
        s["t"] = s.year - 2020
        sa, sb = s[ya].std(), s[yb].std()
        long = pd.concat([pd.DataFrame({"firm": s.firm, "eq": "a", "y": s[ya] / sa, "t": s.t}),
                          pd.DataFrame({"firm": s.firm, "eq": "b", "y": s[yb] / sb, "t": s.t})])
        fe = pd.get_dummies(long.firm + "_" + long["eq"], dtype=float)
        X = fe.copy(); X["t_a"] = long.t * (long["eq"] == "a"); X["t_b"] = long.t * (long["eq"] == "b")
        X["diff"] = 0.0
        Xv = X[[c for c in X.columns if c != "diff"]].values
        y = long.y.values; g = long.firm.values
        ja, jb = Xv.shape[1] - 2, Xv.shape[1] - 1
        b, u = ols(y, Xv); se = cr1_se(Xv, u, g)
        # difference tau_a - tau_b: reparametrise with t_a + t_b columns -> coef on t_a is the difference
        Xd = Xv.copy(); Xd[:, jb] = Xv[:, ja] + Xv[:, jb]
        rng = np.random.default_rng(SEED + 900)
        res = {}
        for nm, XX, j in (("tau " + ya, Xv, ja), ("tau " + yb, Xv, jb), (f"difference tau({ya}) - tau({yb})", Xd, ja)):
            res[nm] = wcb_ols(y, XX, g, j, rng)
        nz = int((s[yb] > 0).sum()); notes = f"{yb} non-zero in {nz} of {len(s)} firm-years" + ("; few non-zero cases" if nz < 10 else "")
        for nm, (bb, ss, lo, hi) in res.items():
            rows.append({"variant": label, "quantity": nm, "estimate_sd_per_year": round(bb, 4), "cr1_se": round(ss, 4),
                         "wcb_low": round(lo, 4), "wcb_high": round(hi, 4), "n_firm_years": len(s), "firms": s.firm.nunique(),
                         "sd_" + "a": round(sa, 6), "sd_b": round(sb, 6), "instability": notes})
        print(label, {k: round(v[0], 3) for k, v in res.items()})
    pd.DataFrame(rows).to_csv(TAB / "h3_results.csv", index=False)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "data":
        build_data()
    elif cmd == "h1":
        h1(int(sys.argv[2]) if len(sys.argv) > 2 else 0, int(sys.argv[3]) if len(sys.argv) > 3 else len(SPECS_H1))
    elif cmd == "h2":
        h2()
    elif cmd == "h3":
        h3()
