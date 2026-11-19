# Phase 5: Analysis (descriptive)

**Date:** 2026-11-18. **Status: draft results for checking in Phase 7. Nothing here is a final finding.**

**How to read this document:**
- **H1–H3 are descriptive only.** The dictionary precision check came in below the pre-set bar of 0.80 (A20, A21).
- **What is reported:** effect sizes with 95% intervals. No hypothesis is called "supported" or "rejected", and nothing is called "significant".
- **No causal claims:** disclosure and exposure are described side by side; nothing here says why firms disclose what they do.
- **Design:** `docs/design.md` section h, as amended by A16 and A20–A23 (`docs/amendments.md`).
- **Phase 5 implementation choices:** A22, logged before any control was collected or any model was run.
- **A23:** the "NNFM FY2020" file turned out to be Flour Mills of Nigeria's report and is excluded.

---

## 1. Data and samples

| Step | Firm-years | Firms |
|---|---|---|
| Main-census firm-years with documents | 100 | 56 |
| Minus NNFM FY2020 (A23: wrong company) | 99 | 56 |
| **H1/H2:** firms with an exposure score (Phase 3) | 69 | 27 |
| H1/H2 with all controls | 69 | 27 |
| **H1 primary outcome defined** (Y4s needs at least one hazard-tagged paragraph) | 25 | 12 |
| of which Y4s > 0 (a hazard paragraph names a site) | **8** | **4** |
| **H3:** firms with ≥ 2 main-analysis years (A16) | 68 (66 with narrative text) | 27 (26) |

**Why firms drop out:**
- **H1/H2:** 29 of the 56 main-census firms have no main-analysis point site with a coordinate, so they have no exposure score.
- **H1 primary outcome:** among the 27 scored firms, 15 never use a hazard term in any year held. For them Y4s is undefined (no hazard paragraphs, so no share).
- **H3:** Cadbury's two filings are financial statements only, with no narrative text, so its shares are undefined. That leaves 26 firms.
- **Robustness stratum:** analysed separately (H4 only here).

**Files:**
- `data/processed/analysis_firm_year.csv` and `analysis_firm.csv`;
- `outputs/tables/sample_flow.csv`.

### Controls (collected for this phase; A22)

The design's controls had not been collected before Phase 5. They were taken from the reports held, for the 27 firms and 70 firm-years in the H1/H2 sample (`data/interim/controls_firm_year.csv`, with page and evidence for every value).

| Control | How | Result |
|---|---|---|
| Size (log total assets) | "Total assets" on the statement of financial position. 17 values read by the analyst where the rule failed (page images, word positions, comparatives) | 69 of 69; ₦ throughout (Dangote and Seplat in ₦ million converted; Seplat and Aradel also report US$) |
| Big Four auditor | Auditor's report pages, then the directors' report | 69 of 69; 15 non-Big Four firm-years |
| External assurance (sustainability information) | Assurance-statement sentences, each read | Dangote Cement only (all 5 years) |
| Foreign parent ≥ 50% | Shareholding / parent statements, each read | Guinness, NB, Nestlé, Unilever, Lafarge, Beta Glass (indirect), Okomu = 1. Seplat FY2020 20.46% (1 at the 20% threshold only); Seplat FY2025 0 at both thresholds (Phase 7b: the 20.07% stake passed to the Nigerian Heirs Group on 31 December 2025, p107) |
| Sector | Census frame (activity-based, provisional) | 9 sectors |

**12 values are flagged for the owner to check** (the `flag` column):
- **Total assets:** Aradel FY2024 and Okomu FY2021 are taken from the next report's comparative column; Geregu FY2024 is an OCR page; Vitafoam FY2025 comes from the five-year summary.
- **Foreign parent:** Beta Glass is held indirectly; Guinness FY2025 is held through a Nigerian vehicle; Unilever FY2020's percentage is carried from FY2025; Seplat FY2025 shareholder sold on 31 December 2025 (resolved in Phase 7b: no foreign holder of 20% or more at year-end).
- **Auditor:** Japaul Gold FY2021's auditor is inferred from the letterhead.
- **Excluded:** NNFM FY2020 (A23).

---

## 2. The gap, in plain numbers (descriptive)

Hazard outcomes are sparse:
- 68 of 97 main firm-years with narrative text (NNFM FY2020 excluded, A23) have no hazard-tagged paragraph at all. [Phase 7: corrected from "68 of 98", which still counted NNFM FY2020.]
- Only 8 have a hazard paragraph that names one of the firm's sites.

So the simplest view comes first: for each firm whose sites are exposed to a hazard, does it ever mention that hazard, and does it ever name an exposed site in that context? (`outputs/tables/gap_firm_hazard.csv`, `gap_sites_by_hazard.csv`.)

**Firms** (main census, main-analysis sites, all years held; frozen dictionary):

| Hazard | Firms with ≥ 1 exposed site | … that ever use that hazard's terms | … that ever name an exposed site in a paragraph with that hazard's terms |
|---|---|---|---|
| River flood | 21 | 6 [Phase 7b: corrected from 7, which still counted the excluded NNFM FY2020 file, A23] | 2 |
| Heat | 15 | 2 | 0 |
| Water stress | 13 | 4 | 1 |
| Coastal flood | 2 | 2 | 0 |

**Sites:** 51 main-analysis point sites are exposed to at least one hazard.
- 50 are named somewhere in their firm's reports.
- Only 7 are named in a hazard-tagged paragraph. By hazard: river flood 5 of 38, heat 1 of 23, water stress 2 of 16, coastal 0 of 4 (any hazard paragraph counted). **[Phase 7 re-read: the matches behind these 7 sites come from donation tables, executive biographies and community-support paragraphs that happen to contain a hazard word and a site name. None is a statement that the site is at physical risk. On reading, 0 of 51 exposed main point sites are named in a genuine physical-risk statement; docs/phase7_verification.md §3.]**

With the refined dictionary (exploratory; storm, erosion and coastal dropped), the firm counts are the same, except that one fewer firm "mentions" coastal flooding.

**Plain reading:** exposed sites are almost always *named* somewhere in the reports. They are rarely named *in physical-risk text*. Heat is the clearest case: 15 firms have heat-exposed sites, and 2 ever use heat terms.

---

## 3. H4: exposed sites never named (descriptive, as designed)

| Group | Exposed sites | Never named (Y5 = 0) | Share | Exact 95% interval |
|---|---|---|---|---|
| Main census, main point sites | 51 | 1 | 2.0% | 0.05%–10.4% |
| Robustness stratum (separate) | 5 | 0 | 0% | 0%–52% |

- **The one unnamed site:** BUA Foods' Ikeja plant.
- **By sector:** zero or one per sector (`outputs/tables/h4.csv`).
- **Important caveat:** this result is close to automatic. The site list (Phase 2, `facilities.csv`) was built by reading these same reports, so almost every site is named somewhere by construction. H4 as designed cannot really detect silence about sites.
- **Post-hoc descriptive (owner decision, 2026-11-18; added after the results were seen, not part of the design):**
  - Of 51 exposed main sites, **7 are named in a hazard-tagged paragraph**. **[Phase 7 re-read: the matches behind these 7 sites come from donation tables, executive biographies and community-support paragraphs that happen to contain a hazard word and a site name. None is a statement that the site is at physical risk. On reading, 0 of 51 exposed main point sites are named in a genuine physical-risk statement; docs/phase7_verification.md §3.]** This is a supplementary description, not a replacement for H4. Hazard-tagged paragraphs come from the frozen dictionary, narrative text only.
  - **By hazard** (section 2): river flood 5 of 38, heat 1 of 23, water stress 2 of 16, coastal 0 of 4.
  - **H4 itself is reported as designed**, with the caveat above.

---

## 4. H1: exposure and site-specific physical-risk disclosure (descriptive)

> **Phase 7 caution:** a re-read of all 11 site-named hazard paragraphs (the 8 firm-years with Y4d > 0) found 10 false positives (donation tables, biographies, community items, a drainage study) and 1 genuine site/asset physical-risk statement (Seplat FY2025, OML 40). Results that rest on Y4d, Y4s or Y4r (H1 primary, the Y4 side of H3, the Y4s rows of H2) therefore mostly measure noise and should not be interpreted, beyond the fact that genuine site-level physical-risk statements are almost absent.

**Specification (design h, A22):**
- **Model:** Y4s (share of a firm-year's hazard paragraphs that name one of its sites) on site exposure (E_share), with size, foreign parent, assurance, Big Four, FS-only filing, and year and sector fixed effects.
- **Main estimator:** fractional logit, with firm-cluster pairs bootstrap intervals.
- **Robustness estimator:** OLS, with wild cluster bootstrap intervals (9,999 replications each).
- **Primary hazards:** river flood and heat.

**What happened:**
- **The primary model is unstable and uninformative.**
  - Y4s exists for 25 firm-years of 12 firms, and only 8 of them, from 4 firms, are non-zero.
  - The fractional logit fits about 17 parameters to 25 rows.
  - **80–86% of bootstrap fits fail** (separation or a rank-deficient design), and the intervals that come out are absurdly wide (e.g. −77 to +702 on the logit scale).
  - It is reported as fitted, but it tells us nothing.
- **The linear (OLS) version gives a usable-looking but fragile number.**
  - River flood: +0.84 (wild bootstrap interval +0.29 to +1.36). In words, a firm whose sites are all flood-exposed has hazard paragraphs that name a site about 0.8 more often (on the 0–1 share scale) than one with none exposed.
  - **Treat this with great caution:** it rests on 8 non-zero firm-years from 4 firms, and a few firms drive it.
  - Heat: +1.08 (−0.37 to +2.59). Combined index: +1.70 (−0.06 to +3.45). Coastal and water stress: intervals wide and centred near zero.
- **Secondary outcomes:**
  - **Y3d** (share of paragraphs that are hazard-tagged, 69 firm-years): OLS river flood +0.0027 (−0.0050 to +0.0105), heat +0.0048 (−0.0032 to +0.0130). These are small: on the order of a few tenths of a percentage point.
  - **Y4d binary** (any site-named hazard paragraph): **not estimable.** Separation: 8 positive firm-years, perfectly predicted by firm and year dummies.
- **Robustness checks** (`outputs/tables/h1_results.csv`):
  - NASA POWER heat, A7 500 m buffers, A8 no-permanent-water flood and the refined dictionary all show the same picture: unstable fractional logits, OLS intervals mostly spanning zero.
  - With the refined dictionary, Y4s exists for only 21 firm-years of 8 firms, and sector fixed effects had to be dropped.
- **Exploratory, unvalidated:** ClimateBERT specificity (Y2, the design's original H1 outcome; 62 firm-years) gives OLS river flood +0.20 (−0.13 to +0.53) and heat −0.19 (−0.60 to +0.23).

---

## 5. H2: exposure versus institutional characteristics (descriptive)

**Specification:**
- **Blocks:** standardised OLS with three blocks, each over a base of year fixed effects and document type: (a) exposure (river flood and heat E_share); (b) institutional (size, foreign parent, assurance, Big Four, sector); (c) both.
- **Intervals:** firm pairs bootstrap, 9,999 replications.

| Outcome | R² added by exposure (given institutional) | R² added by institutional (given exposure) | Difference |
|---|---|---|---|
| **Y3d** (main) | 0.04 (0.00 to 0.15) | 0.17 (0.11 to 0.43) | −0.13 (−0.37 to −0.06) |
| Y4s (secondary; 25 firm-years, 8 non-zero) | 0.09 | 0.34 | −0.25 (−0.62 to −0.01) |
| Y3d, refined dictionary (exploratory) | 0.02 | 0.23 | −0.21 (−0.43 to −0.11) |
| Y1 ClimateBERT (exploratory, unvalidated) | 0.01 | 0.50 | −0.49 (−0.65 to −0.14) |

**Plain reading:** in this sample, firm characteristics account for more of the variation in physical-risk language than site exposure does. The pattern is the same for every outcome version.
- **Size of the block:** the institutional block has more parameters (four variables plus sector dummies, against two exposure variables), and raw R² gains favour bigger blocks. The design did not ask for an adjustment, and none was made.
- **Standardised coefficients (Y3d, full model):** size +0.40 (Phase 7 re-run after A26; was +0.39), foreign parent −0.45, river flood +0.15, heat +0.24, Big Four −0.05, assurance −0.06.

---

## 6. H3: language trend versus site-specific trend (descriptive)

**Specification:**
- **Model:** within-firm (firm fixed effects) yearly trend of each outcome, divided by its standard deviation, so the two trends share a scale.
- **Sample:** firms with ≥ 2 main-analysis years (26 firms, 66 firm-years).
- **Intervals:** wild cluster bootstrap.

| Version | Trend in hazard language Y3d (SD per year) | Trend in site-named hazard rate Y4r | Difference |
|---|---|---|---|
| **Main** (A16 post-listing years) | +0.013 (−0.113 to +0.141) | +0.052 (−0.015 to +0.120) | −0.039 (−0.147 to +0.071) |
| Pre-listing years included (A16) | +0.007 (−0.111 to +0.126) | +0.049 (−0.014 to +0.112) | −0.041 (−0.142 to +0.061) |
| Refined dictionary | +0.057 (−0.043 to +0.156) | +0.048 (−0.018 to +0.114) | +0.009 (−0.077 to +0.096) |
| ClimateBERT Y1 vs Y4r (exploratory, unvalidated) | +0.045 (−0.036 to +0.128) | +0.052 (−0.015 to +0.120) | −0.007 (−0.098 to +0.082) |

**Plain reading:**
- **No clear trend:** within firms, neither physical-risk language nor site-named physical-risk language shows a clear trend over 2020–2025. All intervals include zero.
- **No clear gap:** the difference between the two trends is small and its interval spans zero in every version.
- **Thin data:** Y4r is non-zero in only 8 firm-years, and most firms have only two years, usually 2020 and one recent year.

---

## 7. Charts

All charts are in `outputs/figures/` as PNG and SVG. They use a colour-blind-checked palette, one axis per panel and direct labels.

| Chart | What it shows |
|---|---|
| **(a)** `a_exposure_vs_disclosure` | Firm-level site exposure (river flood, heat) against the share of hazard-tagged paragraphs. Firms that ever name a site in a hazard paragraph are ringed |
| **(b)** `b_trend_2020_2025` | Yearly means of Y3d, Y4r and (exploratory) ClimateBERT Y1 over the H3 sample. The panel is unbalanced (n per year shown), so these means mix different firms; section 6 gives the within-firm trends |
| **(c)** `c_gap_exposed_vs_named` | Exposed sites, sites named anywhere, and sites named in a hazard-tagged paragraph, by hazard |

---

## 8. What we can and cannot say

**We can say (descriptively, for the documents held):**
- **Physical-risk language is rare** in these reports. In the median main firm-year no narrative paragraph uses any hazard term. The average share is about 0.3% of narrative paragraphs.
- **Exposed sites are rarely named in physical-risk text,** even though they are named elsewhere in the reports. Of 51 exposed main sites, 7 appear in a hazard-tagged paragraph. On re-reading (Phase 7), none of these is a genuine statement that the site is at physical risk: 0 of 51. Of 15 firms with heat-exposed sites, 2 ever use heat terms.
- **Firm characteristics account for more variation than exposure:** across firms, size, ownership and sector account for more of the variation in physical-risk language than measured site exposure does. This holds in every outcome version, with the block-size caveat in section 5.
- **No clear trend:** there is no clear rise in physical-risk language within firms over 2020–2025 in this sample, and no clear gap between its trend and the site-named trend.

**We cannot say:**
- **No confirmatory tests:** the dictionary's measured precision (0.65) is below the pre-set bar, so H1–H3 are descriptive only.
- **That exposure has no link to site-specific disclosure:** H1's outcome exists for only 12 firms, with 8 non-zero firm-years. The main model is unstable, and the one usable-looking estimate (OLS, river flood) is fragile.
- **That firms are silent about exposed sites (H4):** the site list comes from the same reports, so "never named" is near zero by construction.
- **Anything about motives:** nothing here explains why firms disclose as they do, or shows decoupling as intent. The study describes a mismatch only (design a).
- **About all listed firms:** 29 main-census firms have no exposure score. Most firms have one or two years. Tier-2 years were not collected.
- **Anything resting on the ClimateBERT results:** they are unvalidated and exploratory.
- **Precise effect sizes:** with about 25 clusters and sparse outcomes, intervals are wide and estimates move with a few firms.

---

## 9. Open items before Phase 7

**Owner decisions of 2026-11-18** (recorded in `docs/amendments.md`; no outcome changed):
1. **The 12 flagged control values** will be re-verified against their page references in Phase 7.
2. **H4 is reported as designed**, with its near-mechanical caveat. The "named in hazard text" gap (7 of 51 exposed sites) is added as a labelled post-hoc descriptive (section 3), not a replacement.
3. **NNFM FY2020:** no replacement will be sought (A23 stands).

**Still to do in Phase 7:**
- Verify every number in this document against the tables.
- Re-verify the 12 flagged control values.
- Re-read the 8 site-named hazard firm-years by hand.

**Code:** `src/phase5_sites.py` (Y5, gap tables, H4), `src/phase5_controls.py` / `src/phase5_controls_build.py` (controls), `src/phase5_models.py` (data, H1–H3), `src/phase5_charts.py`.

**Tables:** `outputs/tables/` (`sample_flow`, `gap_firm_hazard`, `gap_sites_by_hazard`, `h4`, `h1_results`, `h2_results`, `h3_results`).

**Implementation notes** (no effect on the rules in A22):
- Bootstrap draws in which the design was rank-deficient or the exposure was constant are counted as failures and reported.
- H2 draws with an outcome of zero variance are ignored and counted.
- statsmodels, matplotlib and scipy were installed for this phase.
