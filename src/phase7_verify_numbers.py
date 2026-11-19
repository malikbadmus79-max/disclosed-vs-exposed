"""Phase 7: recompute every number quoted in docs/phase5_analysis.md and docs/phase6_policy.md from the data files.
Prints label = value; the analyst compares each against the documents (results in docs/phase7_verification.md).

usage: phase7_verify_numbers.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P, T, I = ROOT / "data" / "processed", ROOT / "outputs" / "tables", ROOT / "data" / "interim"


def out(k, v):
    print(f"{k} = {v}")


def main():
    o = pd.read_csv(P / "outcomes_firm_year.csv"); m = o[o.stratum == "main"]
    m_ex = m[~((m.firm == "NNFM") & (m.year == 2020))]
    sc = m[m.n_scored > 0]
    out("main firm-years with documents (incl. NNFM 2020)", f"{len(m)} / firms {m.firm.nunique()}")
    out("main firm-years with scored paragraphs", len(sc))
    out("of these with no hazard-tagged paragraph", int((sc.n_tagged == 0).sum()))
    out("firm-years with Y4d>0 (main)", int((m.Y4d > 0).sum()))
    out("mean Y3d main (scored)", round(sc.Y3d.mean(), 4)); out("median Y3d", sc.Y3d.median())
    print(pd.read_csv(T / "sample_flow.csv").to_string(index=False))
    c = pd.read_csv(I / "controls_firm_year.csv"); c2 = c[c.excluded_A23 == 0]
    out("controls firm-years / firms", f"{len(c2)} / {c2.firm.nunique()}")
    out("non-Big4 firm-years", int((c2.big4 == 0).sum())); out("TA analyst-read", int((c2.ta_method == "analyst").sum()))
    out("flagged control rows (incl. A23)", int(c.flag.notna().sum()))
    out("assurance=1 firms", sorted(c2[c2.assurance == 1].firm.unique()))
    out("foreign_parent_50=1 firms", sorted(c2[c2.foreign_parent_50 == 1].firm.unique()))
    out("foreign_parent_20 only", sorted(set(c2[c2.foreign_parent_20 == 1].firm) - set(c2[c2.foreign_parent_50 == 1].firm)))
    g = pd.read_csv(T / "gap_firm_hazard.csv")
    for h in ["river flood", "heat", "water stress", "coastal flood"]:
        r = g[g.hazard == h]
        out(f"gap {h}", f"firms {len(r)} mention {int(r.mentions_hazard.sum())} (refined {int(r.mentions_hazard_refined.sum())}) "
                        f"name exposed site in that-hazard para {int(r.names_exposed_site_in_hazard_para.sum())}")
    print(pd.read_csv(T / "gap_sites_by_hazard.csv").to_string(index=False))
    h4 = pd.read_csv(T / "h4.csv"); print(h4[h4.level != "firm"].to_string(index=False))
    out("H4 firm rows with never_named>0", h4[(h4.level == "firm") & (h4.never_named > 0)][["group", "never_named", "exposed_sites"]].values.tolist())
    h1 = pd.read_csv(T / "h1_results.csv")
    print(h1[["label", "outcome", "exposure", "n", "firms", "nonzero", "fitted_spec", "coef", "boot_low", "boot_high", "boot_failures",
              "ols_coef", "ols_wcb_low", "ols_wcb_high"]].round(4).to_string(index=False))
    h2 = pd.read_csv(T / "h2_results.csv"); print(h2[["outcome", "n", "firms", "quantity", "estimate", "boot_low", "boot_high"]].to_string(index=False))
    h3 = pd.read_csv(T / "h3_results.csv"); print(h3[["variant", "quantity", "estimate_sd_per_year", "wcb_low", "wcb_high", "n_firm_years", "firms"]].to_string(index=False))
    s = o[o.firm == "SEPLAT"][["year", "n_scored", "n_tagged", "Y3d", "Y4d", "n_tagged_refined", "Y4d_refined"]]
    print(s.to_string(index=False))
    pc = pd.read_csv(P / "policy_codes_firm_year.csv")
    out("policy firm-years", len(pc))
    for k in ["P1", "P2", "P3", "P4", "P5", "P7"]:
        out(f"{k} firm-years", int(pc[k].sum()))
    out("P6", pc.P6.value_counts().to_dict())
    lat = pc.sort_values("year").groupby("firm").tail(1)
    out("latest-year dist", lat.year.value_counts().sort_index().to_dict())
    for k in ["P1", "P2", "P3", "P4", "P5", "P7"]:
        out(f"{k} latest firms", sorted(lat[lat[k] == 1].firm))
    out("P6 latest", lat.P6.value_counts().to_dict())
    x = lat[["P1", "P2", "P3", "P4", "P5"]].sum(axis=1)
    out("latest all P1-P5 / >=1 / none", f"{int((x == 5).sum())} / {int((x >= 1).sum())} / {int((x == 0).sum())}")
    fs = m[["firm", "year", "fs_only"]]
    out("latest FS-only", int(lat.merge(fs, on=["firm", "year"]).fs_only.sum()))
    ev = pd.read_csv(P / "policy_codes_evidence.csv"); out("evidence rows", len(ev))
    pr = pd.read_csv(I / "precision_results.csv"); print(pr.to_string(index=False))


if __name__ == "__main__":
    main()
