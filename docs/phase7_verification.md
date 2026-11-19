# Phase 7: Verification

**Date:** 2026-11-18.
- **Scope:** every verification list in the project:
  - `docs/phase5_analysis.md` §9;
  - `docs/phase6_policy.md` §7 and its [V7] flags;
  - the A25 list.
- **Rule for corrections:** no design rule was changed. Text was corrected where it disagreed with the data. Data were corrected only with page evidence, and each correction was logged (`docs/amendments.md`, A26 and the Phase 7 notes).
- **Code:** `src/phase7_verify_numbers.py` recomputes every quoted number. The other checks below were run as short scripts, and their results are recorded here. Phase 7b robustness: `src/phase7b_robustness.py` (§9).

---

## 1. Numbers quoted in the Phase 5 and Phase 6 documents

Every number in `docs/phase5_analysis.md` and `docs/phase6_policy.md` was recomputed from the files: the sample flow, controls, gap tables, H4, H1, H2, H3, the Seplat case, the policy codes, readiness and precision.

| Item | Result |
|---|---|
| Sample flow, controls counts, gap table, site counts, H4, H3, precision, policy codes, readiness, Seplat figures | **Match** |
| "68 of 98 main firm-years have no hazard-tagged paragraph" | **Text corrected to 68 of 97:** 98 still counted NNFM FY2020, excluded under A23. The 68 is unchanged (NNFM FY2020 had one tagged paragraph) |
| H1 and H2 after the A26 control correction (§2) | Re-run. The only quoted figure that changes at two decimals is the H2 Y3d **size coefficient, +0.39 → +0.40** (text updated). Other H1/H2 changes are in the third or fourth decimal |
| "29 of the 56 main-census firms have no main-analysis point site with a coordinate" | Confirmed (§5) |

---

## 2. The 12 flagged control values

| Flag | Check (page) | Outcome |
|---|---|---|
| Aradel FY2024 total assets (from the FY2025 comparative) | FY2024 report's own statement, p77 | Confirmed (₦1,749,835,623k); page reference corrected |
| Okomu FY2021 total assets (from the FY2022 comparative) | FY2021 report's own statement, p38 | Confirmed (₦65,772,444k); page reference corrected |
| Geregu FY2024 total assets (OCR page) | Page image p52: 72,669,749 + 170,800,674 | Confirmed |
| **Vitafoam FY2025 total assets** (five-year summary) | Group statement of financial position, p57 image | **Wrong. Corrected (A26) from ₦43,693,181k to ₦65,275,389k.** The summary's "total assets" was net of current liabilities. H1/H2 re-run |
| Unilever FY2020 foreign parent (carried from FY2025) | Shareholder table p133: 57.81% + 18.16% = 75.97% | Confirmed; evidence updated |
| Guinness FY2025 foreign parent (Tolaram) | p9 "ultimate Parent Company Tolaram Group"; p45 Singapore headquarters; 70.86% (p14/19) | Confirmed |
| Japaul FY2021 auditor (inferred) | Whole file: no Big Four name anywhere | Big Four = 0 confirmed; auditor's identity still inferred (PKF, letterhead) |
| Seplat FY2020 foreign share | p142: MPI (Maurel & Prom) 20.46% | Share corrected from 20.07% to 20.46%; codes unchanged |
| Seplat FY2025 foreign share | M&P sold 20.07% on 31 December 2025 | **Resolved in Phase 7b:** FY2025 IAR p107 lists Heirs Group 20.07% at 31 December 2025 (it acquired the M&P shares that day). No foreign holder of 20% or more at year-end, so it is coded 0 at both thresholds. Treating Heirs as Nigerian is the analyst's reading. The pre-sale reading (coded 1) is run as a sensitivity check (§9) |
| Beta Glass FY2020 / FY2023 (indirect foreign parent) | p53 / p51: the Nigerian parent holds 61.9%; ultimate controlling party abroad | Quote confirmed. Coding the parent as foreign is an interpretation, and stays flagged |
| NNFM FY2020 | — | Excluded (A23); no replacement sought |

---

## 3. Site-named hazard paragraphs, policy codes, zero-coded sample

**The 8 firm-years with Y4d > 0 (11 paragraphs), re-read in full:**

| Firm-year | Paragraph | What it is | Site at physical risk? |
|---|---|---|---|
| BUA Cement FY2021 | p36 | Chairman's philanthropy | No |
| BUA Cement FY2025 | p15 | Reclamation plot, "drought-tolerant" crops at the Sokoto plant | No |
| BUA Cement FY2025 | p27 | Chairman's biography | No |
| BUA Foods FY2024 | p8 | Donations table (Maiduguri flood victims; Kano) | No |
| Dangote FY2020 | p65 | Social investment list | No |
| Dangote FY2022 | p194 | Donations table | No |
| Dangote FY2023 | p57 | "Coastal communities" of the Onne terminal (community support) | No |
| Dangote FY2023 | p195 | Donations table (Tanzania flood relief) | No |
| Dangote FY2024 | p257 | Donations table | No |
| Seplat FY2025 | p125 | "Storm water design studies" at Amukpe (drainage) | No |
| Seplat FY2025 | p153 | OML 40 exposure to precipitation and pluvial flooding | **Yes** (a licence area, not a point site) |

**Consequences** (text only; the frozen rules were applied correctly, so no data change):
- **1 of 11 paragraphs**, and 1 of 8 firm-years, is a genuine statement that a named site or asset faces physical risk.
- **0 of 51** exposed main point sites are named in a genuine physical-risk statement. The Phase 5/6 figure "7 of 51" counts mechanical matches only. Both documents now carry this correction.
- **Measures based on Y4d, Y4s or Y4r** (H1's primary outcome, the Y4 side of H3, the Y4s rows of H2) mostly measure noise. They are not interpreted beyond "genuine site-level physical-risk statements are almost absent". A caution was added to `docs/phase5_analysis.md` §4.

**Policy codes (A25):**
- **38 positive codes:** each passage was found, on its stated page and paragraph, in the extracted text.
- **Borderline codes, re-read and kept as coded:**
  - MTN P3 counts realised damage as a physical-risk metric.
  - Dangote FY2020 P4 is a climate risk register kept by HSSE.
  - Seplat FY2020 P4 is risk committee oversight of climate risk.
- **20 random zero-coded candidates** (seed 20261118, from 109 candidates with no decision in firm-years with no positive for that code): **all correctly 0.** They were notes on new standards, tree planting, waste-heat recovery, donation tables, generic "resilience" wording, and Seplat FY2020's "Nigeria is vulnerable" (no asset named).
- **P6 "voluntary"** (MTN Nigeria and Seplat FY2025) rests on explicit statements of compliance: "comply with IFRS Sustainability Disclosure Standards" (MTN AR p84), and "prepared in accordance with IFRS Sustainability Disclosure Standards" (Seplat IAR p112).

---

## 4. Standards and regulatory claims

**IFRS S2** (`data/raw/manual/policy/issb-2026-a-…pdf`): paragraph numbers were identified from the page layout, and each paraphrase's key phrase was found in that paragraph's text.

| Cited | Verified |
|---|---|
| 3(a)(i), 10(a)–(d), 11, 13(b), 22 (incl. B1–B18 reference), 25(a)(i)–(iii), B65(b), C1, Appendix A (acute/chronic) | Yes |
| 29(c) | Yes. Paragraph 29 runs onto the next page, where items (b)–(g) continue it with no new paragraph number |
| IFRS S1 materiality (Phase 6 §4) | **Not verified.** IFRS S1 is not held |

**Nigeria sources:**
- **SEC circular:** live page, read 2026-11-18.
- **FRC Roadmap and NGX Guidelines:** fetched 2026-11-18. The text was extracted locally from the downloaded PDFs.

| Claim | Source | Verified |
|---|---|---|
| Implementation Plan by 15 October 2026; mandatory from periods beginning 1 January 2028 (SMEs 1 January 2030); voluntary 1 January 2024 to periods ending 31 December 2027; published 23 September 2026 | SEC circular | Yes |
| Phases: early adopters (to 31 December 2023), voluntary 2024–2027, mandatory from 1 January 2028 (all PIEs; SMEs from 1 January 2030) | FRC Roadmap PDF pp19–20 | Yes |
| Readiness test compulsory; collects a climate-risk materiality assessment and a scenario-analysis description | FRC Roadmap pp20–21 | Yes |
| Assurance from the third year of reporting | FRC Roadmap p30 | Yes |
| "Climate resilience of strategy and business model to both transition and physical risks" | FRC Roadmap p23 | Yes |
| "Climate-related physical risks" cross-industry metric | FRC Roadmap p25 | Yes |
| §7.4 Risk management | FRC Roadmap p24 | Yes |
| Approved by the SEC on 9 November 2018 | NGX Guidelines p1 | Yes |
| "begins with detecting key risks of operational disruptions from climate change, resource scarcity, or community issues" | NGX Guidelines p8 | Yes |

**Still not verified:**
- secondary reports of a timing mismatch between the SEC and the FRC;
- the FRC "41" figure;
- whether the Qua Iboe Terminal lies in Ibeno;
- which national agency could host a hazard dataset (Phase 6, R2).

---

## 5. Why 29 main-census firms have no exposure score

**Table:** `outputs/tables/unscored_firms_reasons.csv`. Each firm's facility records (`facilities.csv`) are classified by a fixed order of precedence: only an office; dispersed only; generic facility; named place without a coordinate.

| Reason | Firms | of which FS-only in every year held | Firms |
|---|---|---|---|
| A. Only an office or registered address stated | 0 | – | – |
| B. Dispersed assets only (networks, licences, depots) | 2 | 1 | CONOIL, JBERGER |
| C1. Facility stated only generically ("Factory", "Brewery"), with no place named | 22 | 13 | AIRTELAFRI, BERGER, CADBURY, CAP, CHAMPION, ENAMELWA, EUNISELL, GOLDBREW, IMG, INTBREW, MCNICHOLS, MECURE, MEYER, MORISON, MTNN, MULTITREX, NASCON, PZ, THOMASWY, TOTAL, TRIPPLEG, UNIONDICON |
| C2. Place named in the report, but no coordinate could be assigned in Phase 2 | 5 | 2 | ETERNA, FTNCOCOA, MULTIVERSE, OANDO, PRESCO |
| **Total** | **29** | **16** | |

**Plain reading:**
- **Most common reason:** the reports do not say *where* the firm's plants are (22 of 29).
- **FS-only filings:** 16 of the 29 hold only financial-statement filings, where facility locations are rarely stated.
- **What this means for the findings:** the exposure analyses rest on the 27 firms that do name their sites. That is itself a disclosure finding, related to IFRS S2 13(b).

---

## 6. Reproducibility (re-runs and hashes)

**Method:** 35 output files were hashed before the re-runs. Then these steps were re-run from their inputs: dictionaries, outcomes, refined dictionary, precision, Y5/gap/H4, controls, analysis data, H1, H2, H3, policy codes (candidates and build) and charts.

| Result | Files |
|---|---|
| **Byte-identical** | 28 of 35: dictionaries, outcomes, site mentions, gap and H4 tables, H3, policy codes and evidence, precision results, paragraphs, section tags, document list, scores, chart PNGs |
| Changed as expected (A26) | Controls, analysis dataset, H1 and H2 tables |
| Changed, not substantively | The 3 chart SVGs: only the embedded creation date (`<dc:date>`) differs. The PNGs are identical |

**Raw to interim:** three documents were re-segmented from their PDFs:
- GUINNESS FY2023 (text layer);
- ELLAHLAKES FY2020 (OCR, A3–A5 page selection);
- LIVESTOCK FY2025 (A12/A15).

All three are **identical** to `paragraphs.csv`, row by row (ids, pages, word and token counts, eligibility, duplicates, text).

**Not re-run:**
- OCR (hours of compute; the OCR copies are verified by their logged hashes);
- Phase 2–3 geocoding and hazard extraction (large rasters);
- ClimateBERT scoring (deterministic; scores are reused and hashed).

---

## 7. What changed in Phase 7

1. **Data, A26:** Vitafoam FY2025 total assets corrected; H1/H2 re-run.
2. **Evidence and page references:** Aradel FY2024, Okomu FY2021, Unilever FY2020, Guinness FY2025, Seplat FY2020 (share corrected to 20.46%).
3. **Text:** "68 of 98" → "68 of 97". H2 size coefficient +0.39 → +0.40. The "7 of 51" site gap is now qualified (0 of 51 on reading), and H1/H3 results based on Y4 carry a caution.
4. **New table:** reasons for the 29 unscored firms.
5. **Robustness checks in design h that Phase 5 did not run:** RP10/RP500, depth ≥ 0.5 m, 5 km grade-B buffers, excluding FS-only firm-years, DWL, the robustness stratum, leave-one-sector-out, dispersed-asset firms, and the 20% foreign-parent threshold. Phase 5 ran only NASA POWER heat, A7, A8, the refined dictionary, pre-listing years and ClimateBERT. **All of these checks were run in Phase 7b (§9).**
6. **Phase 7b corrections:**
   - River flood "7 of 21" → **6 of 21**: the 7 still counted the excluded NNFM FY2020 file (A23). Corrected in `docs/phase5_analysis.md` §2 and `docs/phase6_policy.md` F1.
   - Seplat FY2025 foreign parent resolved to 0 (§2; `src/phase5_controls_build.py`). This does not change the ≥ 50% control, so the main H1/H2 results are unchanged.

---

## 8. Claims that are SAFE to state publicly

Each claim holds for the documents held (2020–2025, 56 main-census firms, 99 firm-years), is descriptive, and is verified in this phase.

1. **Physical-risk language is rare.** In 68 of 97 main-census firm-years with narrative text, no paragraph uses any term of the frozen hazard dictionary. On average, about 0.3% of narrative paragraphs do. *(Dictionary precision 0.65; recall not measured.)*
2. **Exposed sites are almost never discussed as being at physical risk.** Of 51 main point sites exposed to river flood, heat, coastal flood or water stress (Phase 3 open data), 50 are named somewhere in their firm's reports. On reading, none is named in a statement that the site faces physical climate risk. The only asset-level physical-risk assessment found is Seplat's FY2025 licence-area assessment.
3. **Heat is the clearest silence.** 15 firms have heat-exposed sites, and 2 ever use heat terms.
4. **Most firms do not say where their plants are.** 22 of 29 firms without an exposure score describe their facilities only generically. 16 of the 29 hold only financial-statement filings.
5. **Firm characteristics account for more variation than exposure:** firm characteristics (size, ownership, sector) explain more variation in hazard language than measured site exposure. ΔR² 0.17 against 0.04; difference −0.13 (95% bootstrap interval −0.37 to −0.06). *Descriptive, not a test; the institutional block has more parameters.*
6. **No clear trend 2020–2025** within firms in hazard language (all intervals include zero). *Mostly two years per firm.*
7. **2028 readiness (analyst-coded, not validated):** in their latest year held, 2 of 56 firms (MTN Nigeria and Seplat) show all five physical-risk elements (resilience, scenario analysis, metric, risk process, locations). 50 show none. 2 state that their disclosures follow IFRS S1/S2 (FY2025).
8. **Regulatory facts:** IFRS S1/S2 reporting in Nigeria becomes mandatory for public-interest entities for periods beginning on or after 1 January 2028 (SMEs 2030), with voluntary adoption in 2024–2027 (SEC circular of 23 September 2026; FRC Roadmap 2026). IFRS S2 13(b) and 29(c) ask for where physical risks are concentrated and the share of assets vulnerable to them.

**Not safe to state:**
- that exposure is or is not related to site-specific disclosure (H1 not estimable in practice; the Y4 measures are mostly noise);
- any confirmatory result (H1–H3 are descriptive only);
- motives, decoupling as intent, or non-compliance by any firm;
- anything resting on ClimateBERT outcomes (unvalidated);
- H4's "2% never named" as evidence of openness (near-mechanical);
- claims about firms outside the 27 exposure-scored firms for H1/H2.

---

## 9. Phase 7b: robustness checks (design h)

**Code and tables:**
- `src/phase7b_robustness.py`, which uses the Phase 5 estimators (A22);
- `outputs/tables/robustness_7b_descriptive.csv` (claims 1–4 and 7 under each check);
- `outputs/tables/robustness_7b_models.csv` (H1, H2 and H3 under each check);
- paragraph cache: `data/interim/phase7b_paragraph_cache.csv`.

**Status:** all checks are descriptive only (A21). Both tables are complete: every check named in the script is present, and leave-one-sector-out covers all 7 sectors in the model sample.

**Baseline reproduction:** the script's baseline matches Phase 5 exactly for H2 and H3, and for the H1 point estimates. The H1 bootstrap intervals differ slightly because the script uses a different seed offset (for example, Y4s OLS: 0.33 to 1.35 here, 0.29 to 1.36 in `h1_results.csv`).

### Descriptive claims

| Check | Firm-years with narrative / no hazard paragraph; mean Y3d | Exposed main sites / named / named in hazard paragraph (mechanical) | River flood: firms exposed / use terms | Heat: firms exposed / use terms | Latest year: firms / all five / none |
|---|---|---|---|---|---|
| Baseline | 97 / 68; 0.0031 | 51 / 50 / 7 | 21 / 6 | 15 / 2 | 56 / 2 / 50 |
| RP10 | same | same | 19 / 6 | same | same |
| RP500 | same | same | 22 / 6 | same | same |
| Depth ≥ 0.5 m | same | same | 20 / 6 | same | same |
| 5 km grade-B buffer | same | 57 / 56 / 7 | 23 / 6 | same | same |
| Excluding FS-only firm-years | 68 / 39; 0.0044 | 49 / 45 / 7 | 20 / 6 | 14 / 2 | 37 / 2 / 31 |
| Excluding DWL firms | 95 / 66; 0.0032 | 51 / 50 / 7 | 21 / 6 | 15 / 2 | 54 / 2 / 48 |

**Other descriptive checks:**
- **Genuine site physical-risk statements:** 0 under every check. The §3 re-reading covered every site-named hazard paragraph, whatever the exposure definition.
- **Robustness stratum** (ABCTRANS, RTBRISCOE, TRANSCORP; FY2025, FS only): 3 of 3 firm-years have no hazard paragraph. 5 sites are exposed, and none is named in a hazard paragraph.
- **Unscored firms:** 29 / 22 (C1). Excluding FS-only years gives 13 / 9; excluding DWL firms gives 27 / 20.

**Dispersed-asset firms** (no exposure score is defined for them, e6):

| Group | Firms | Firm-years with narrative / no hazard paragraph | Mean Y3d | All five P1–P5 / none |
|---|---|---|---|---|
| Dispersed only | 8 | 8 / 5 | 0.0019 | 1 (MTNN) / 6 |
| Dispersed + point sites | 3 | 10 / 2 | 0.0080 | 1 (SEPLAT) / 1 |
| Point sites only, or none | 45 | 79 / 61 | 0.0026 | 0 / 43 |

Both firms that show all five elements hold dispersed assets.

### Models

**H2 (Y3d), difference in R² added (exposure − institutional), 95% firm pairs bootstrap.** Every interval lies below zero.

| Check | Difference |
|---|---|
| Baseline | −0.13 (−0.37 to −0.06) |
| RP10 / RP500 / depth 0.5 m / 5 km buffer | −0.13 / −0.13 / −0.13 / −0.13; upper bounds −0.05 to −0.06 |
| Excluding FS-only firm-years | −0.15 (−0.43 to −0.06) |
| 20% foreign-parent threshold | −0.13 (−0.39 to −0.06) |
| 20% threshold, Seplat FY2025 coded 1 | −0.10 (−0.37 to −0.04) |
| Leave out one sector | −0.06 to −0.19. The weakest is Industrial Goods: −0.06 (−0.37 to −0.01), with assurance dropped as constant once Dangote is left out |

**H3 (SD per year, wild cluster bootstrap):** under the baseline, excluding FS-only firm-years, and all 7 leave-one-sector-out samples, all 27 intervals (τ Y3d, τ Y4r and their difference) include zero. Exposure variants and the foreign-parent threshold do not enter H3.

**H1 (Y3d, OLS):**
- For the river flood exposure share, every interval includes zero under every check.
- For heat, the same is true.

**H1 (Y4s):**
- OLS intervals exclude zero under every check where Y4s was estimated (n = 25, 8 non-zero; Y4 measures are mostly noise, §3).
- The Y4s rows for RP10, RP500 and depth 0.5 m are identical to the baseline at four decimals.

**Fractional logit** (point estimate, CR1 interval only): a few leave-one-sector-out cells have CR1 intervals that exclude zero. These are river flood without Agriculture, and heat without Consumer Goods or Industrial Goods. The cell for river flood without Consumer Goods is degenerate (120.09, zero-width interval: separation) and should be read as not estimable.

**DWL firms:** neither DWL firm is in the H1/H2 sample. Both are in the H3 sample, but the model check was not re-estimated without them (script note: "models unchanged").

### Do the §8 safe claims still hold?

| # | Claim | After Phase 7b |
|---|---|---|
| 1 | Hazard language is rare (68 of 97; about 0.3%) | **Holds.** It does not depend on exposure. Without FS-only years, 39 of 68 and 0.44%. In the robustness stratum, 3 of 3. Without DWL firms, 66 of 95 |
| 2 | Exposed sites are not discussed as at risk (51; 50 named; 0 on reading) | **Holds.** The counts are unchanged for RP10, RP500 and depth 0.5 m. The 5 km buffer gives 57 / 56, still 0 on reading. Without FS-only years, 49 / 45. In the robustness stratum, 5 exposed and 0 named |
| 3 | Heat: 15 exposed firms, 2 use heat terms | **Holds** under every check (14 / 2 without FS-only years) |
| 4 | 22 of 29 unscored firms describe facilities only generically; 16 FS-only | **Holds.** It is a count of the frame, not sensitive to any check |
| 5 | Firm characteristics over exposure (difference −0.13, −0.37 to −0.06) | **Holds in direction.** Every interval lies below zero. The size ranges from −0.06 (leaving out Industrial Goods) to −0.19 (leaving out Consumer Goods) |
| 6 | No clear within-firm trend | **Holds.** All 27 H3 intervals across the checks include zero |
| 7 | 2 of 56 show all five elements; 50 none | **Holds** (2 of 37 without FS-only years; 2 of 54 without DWL). Both firms hold dispersed assets |
| 8 | Regulatory facts | **Holds.** No check bears on it |

**The §8 list is unchanged.** No check reverses or materially weakens a claim. The river flood correction (7 → 6 of 21) does not concern any listed claim. The "not safe" list also stands: H1 on Y4 outcomes and the fractional-logit cells above stay off-limits.

---

## 10. Phase 8 addition: safe claim 3 under NASA POWER heat (owner review, 2026-11-18)

**Code and table:**
- `src/phase8_nasa_heat_check.py`;
- `outputs/tables/robustness_8_nasa_heat_silence.csv`.

**Status:** descriptive. No existing output held this count, so it was computed for the paper. It uses the same rule as the Phase 7b claim-3 row. Only the site exposure flag changes, from `heat_exposed` (ERA5) to `heat_nasa_exposed` (NASA POWER).

| Heat source | Main point sites scored / exposed | Firms with a heat-exposed site | … of which ever use heat terms |
|---|---|---|---|
| ERA5 (main) | 65 / 23 | 15 | 2 (Dangote Cement, Seplat) |
| NASA POWER (robustness) | 65 / 21 | 13 | 2 (Dangote Cement, Seplat) |

**Overlap:** 9 firms are heat-exposed under both sources. Three main-census firms ever use heat terms: Airtel Africa, Dangote Cement and Seplat. Airtel Africa has no main point site.

**Claim 3 holds under NASA POWER:** 13 firms are exposed and 2 use heat terms. The firms behind the exposed counts differ between the two sources.

**Implementation note:** `heat_nasa_exposed` is stored as text in `site_hazards.csv`. The first run compared it with the number 1, matched nothing and returned 0. The script now converts it to a number. Only the corrected result is reported here.
