"""Phase 5 charts (PNG + SVG in outputs/figures/). Descriptive only. Palette: dataviz reference categorical slots 1-3
(blue #2a78d6, orange #eb6834, aqua #1baf7a; validated light mode: CVD pass, aqua below 3:1 contrast so every series
is directly labelled). One axis per panel; small multiples instead of dual axes.

usage: phase5_charts.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
FIG = ROOT / "outputs" / "figures"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"  # slots 1-4, validated (light)
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "font.size": 10, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "none"})


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def chart_a():
    f = pd.read_csv(P / "analysis_firm.csv")
    f = f[f.combined_index.notna() & f.Y3d_mean.notna()]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, (col, lab) in zip(axes, (("rf100_E_share", "River flood: share of firm's sites exposed"),
                                     ("heat_E_share", "Heat (ERA5): share of firm's sites exposed"))):
        ax.scatter(f[col], 100 * f.Y3d_mean, s=48, color=BLUE, edgecolor=SURF, linewidth=2, zorder=3)
        site = f[f.Y4d_any == 1]
        ax.scatter(site[col], 100 * site.Y3d_mean, s=110, facecolor="none", edgecolor=ORANGE, linewidth=2, zorder=4)
        for _, r in f[(f.Y3d_mean > f.Y3d_mean.quantile(0.85)) | (f.Y4d_any == 1)].iterrows():
            left = col == "heat_E_share" and r.firm == "SEPLAT"  # avoids collision with DANGCEM in the heat panel
            ax.annotate(r.firm, (r[col], 100 * r.Y3d_mean), xytext=(-6, 4) if left else (5, 4), textcoords="offset points",
                        ha="right" if left else "left", fontsize=8, color=INK2)
        ax.set_xlabel(lab); ax.set_xlim(-0.05, 1.05)
    axes[0].set_ylabel("Hazard-tagged paragraphs, % of narrative\n(firm mean over its years, frozen dictionary)")
    axes[1].scatter([], [], s=48, color=BLUE, label="firm (27 exposure-scored firms)")
    axes[1].scatter([], [], s=110, facecolor="none", edgecolor=ORANGE, linewidth=2, label="raw dictionary match (site name + hazard term), not a risk statement")
    fig.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=8)
    fig.subplots_adjust(bottom=0.24)
    fig.suptitle("(a) Site exposure vs physical-risk language, by firm (descriptive)", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, -0.11, "Exposure: Phase 3 E_share (main analysis sites). Language: Y3d, frozen hazard dictionary (precision 0.65, A21).\n"
             "Rings: raw matches; on reading none is a site physical-risk statement (docs/phase7_verification.md section 3). "
             "No causal reading; H1-H3 are descriptive only.", fontsize=8, color=INK2)
    save(fig, "a_exposure_vs_disclosure")


def chart_b():
    d = pd.read_csv(P / "analysis_firm_year.csv")
    d = d[d.h3_main == 1]; k = d.groupby("firm").year.nunique(); d = d[d.firm.isin(k[k >= 2].index)]
    g = d.groupby("year").agg(Y3d=("Y3d", "mean"), Y4r=("Y4r", "mean"), Y1=("Y1_cb", "mean"), n=("firm", "size")).reset_index()
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    for ax, (col, lab, color, note) in zip(axes, (("Y3d", "Hazard-tagged paragraphs (Y3d)", BLUE, "main dictionary"),
                                                 ("Y4r", "Site-named hazard paragraphs (Y4r)", ORANGE, "main dictionary"),
                                                 ("Y1", "Climate paragraphs (Y1, ClimateBERT)", AQUA, "exploratory, unvalidated"))):
        ax.plot(g.year, 100 * g[col], color=color, linewidth=2, marker="o", markersize=7, markeredgecolor=SURF, markeredgewidth=2)
        for _, r in g.iterrows():
            ax.annotate(f"{100 * r[col]:.2f}%", (r.year, 100 * r[col]), xytext=(0, 7), textcoords="offset points",
                        ha="center", fontsize=7.5, color=INK2)
        ax.set_title(f"{lab}\n{note}", fontsize=9.5, loc="left", color=INK)
        ax.set_xticks(g.year); ax.set_ylim(bottom=0)
    axes[0].set_ylabel("% of narrative paragraphs\n(mean over firm-years)")
    fig.subplots_adjust(top=0.78, wspace=0.28)
    for _, r in g.iterrows():
        axes[0].annotate(f"n={int(r.n)}", (r.year, 0), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=7, color=INK2)
    fig.suptitle("(b) 2020-2025: yearly means over the H3 sample (26 firms with >= 2 main-analysis years)", x=0.01, y=1.02, ha="left", fontsize=12)
    fig.text(0.01, -0.06, "The panel is unbalanced (n = firm-years per year, shown in the first panel): yearly means mix different firms. "
             "Trends are estimated within firms in docs/phase5_analysis.md (H3, descriptive only).", fontsize=8, color=INK2)
    save(fig, "b_trend_2020_2025")


def chart_c():
    s = pd.read_csv(P / "site_mentions.csv")
    s = s[(s.site_set == "main") & (s.census_stratum == "main")]
    rows = []
    for h, lab in (("rf100", "River flood"), ("heat", "Heat"), ("water", "Water stress"), ("coastal", "Coastal flood"), ("any", "Any hazard")):
        e = s[s[f"exp_{h}"] == 1]
        rows.append((lab, len(e), int(e.Y5_named_any.sum()), int(e.named_in_hazard_para.sum())))
    t = pd.DataFrame(rows, columns=["hazard", "exposed", "named", "named_hazard"])
    # Phase 7 re-reading (docs/phase7_verification.md section 3): none of the raw matches is a statement that the
    # site faces physical risk, so the count discussed as at physical risk on reading is 0 for every hazard.
    t["at_risk_on_reading"] = 0
    fig, ax = plt.subplots(figsize=(9, 5.0))
    y = range(len(t)); h = 0.2
    series = ((-1.5 * h, "exposed", BLUE, "exposed main sites"),
              (-0.5 * h, "named", ORANGE, "named anywhere in the firm's reports (Y5)"),
              (0.5 * h, "named_hazard", AQUA, "named in a hazard paragraph (raw dictionary match)"),
              (1.5 * h, "at_risk_on_reading", YELLOW, "discussed as at physical risk, on reading (Phase 7)"))
    for off, col, color, lab in series:
        bars = ax.barh([i + off for i in y], t[col], height=h - 0.03, color=color, label=lab)
        for b, v in zip(bars, t[col]):
            ax.text(b.get_width() + 0.4, b.get_y() + b.get_height() / 2, str(v), va="center", fontsize=8, color=INK2)
    ax.set_yticks(list(y)); ax.set_yticklabels(t.hazard); ax.invert_yaxis()
    ax.set_xlabel("Number of main-analysis point sites (main census)"); ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8)
    fig.suptitle("(c) The gap: exposed sites vs sites discussed as at physical risk", x=0.01, y=1.04, ha="left", fontsize=12)
    fig.text(0.01, -0.07, "Site list built from the same reports, so 'named anywhere' is near 100% by construction (see H4 caveat). "
             "Raw matches: frozen dictionary, narrative text only;\non reading (docs/phase7_verification.md section 3) none is a "
             "statement that the site faces physical risk.", fontsize=8, color=INK2)
    save(fig, "c_gap_exposed_vs_named")
    t[["hazard", "exposed", "named", "named_hazard"]].to_csv(ROOT / "outputs" / "tables" / "gap_sites_by_hazard.csv", index=False)
    print(t.to_string(index=False))


if __name__ == "__main__":
    chart_a(); chart_b(); chart_c()
