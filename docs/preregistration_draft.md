# Preregistration draft: Disclosed vs exposed

**Status:** matches the frozen design (version `frozen-2026-11-07`), but **not yet submitted to OSF**. It follows common preregistration headings; the exact OSF template version was not verified. The full design is in `docs/design.md`, and all parameters are in `config/parameters.json`.

**Frozen file hashes (SHA-256, 2026-11-07):**

- `config/parameters.json`: `0ca716a8ea027ddc210d3e6bdfe2863f58a9ba1d61c5a66c623852daff67167f`
- `docs/design.md`: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`

## 1. Title

Disclosed vs exposed: physical climate risk disclosure and site-level hazard exposure at Nigeria's listed companies, 2020–2025.

## 2. Research question

Among NGX-listed firms with physical operations in Nigeria, does the content of disclosure on physical climate risk reflect the measured hazard exposure of their sites, ahead of mandatory IFRS S1/S2 reporting? That reporting covers periods beginning on or after 1 January 2028, per the SEC circular of 23 September 2026.

## 3. Hypotheses

- **H1:** the specificity of physical-risk disclosure rises with firm-level site exposure.
- **H2:** disclosure is explained more by size, foreign parent, external assurance and sector than by exposure (decoupling).
- **H3:** the share of climate-related text rises from 2020 to 2025 faster than site-specific physical-risk disclosure.
- **H4 (descriptive):** a substantial share of high-exposure sites is never named in the firm's reports.

## 4. Design and data already in hand

This is an observational census study with no manipulation.

**Collected before registration:**

- The NGX equities price list of 06 Nov 2026.
- Pilot reports for 15 firms.
- A pilot facility table of 94 entries.
- One NASA POWER test series for a single town point, not a facility.
- An operational smoke test of 4 ClimateBERT models on 20 paragraphs. Its labels and scores were not recorded.

**Not yet computed or seen:** no hazard score, no corpus-level text outcome and no regression result.

## 5. Sample

- **Main census:** 59 NGX-listed firms with physical operations in Nigeria (06 Nov 2026 list), before the document test. A firm needs a full annual report for at least one year from 2023 to 2025.
- **Robustness stratum:** 18 services firms with physical sites, analysed separately.
- **Exclusions:** non-operating instruments, delisted firms, firms that fail the document test, and firms whose board flag is confirmed to mean suspended or delisting.
- **Fixing the census:** the census is fixed at the end of Phase 2, before outcomes are computed.
- **Sample size:** no power analysis is reported. N is fixed by the census, so the emphasis is on effect sizes.

## 6. Variables

**Exposure:**

- **River flood:** JRC, 1-in-100-year map, depth > 0 m. Depth ≥ 0.5 m is a robustness check.
- **Coastal flood:** Aqueduct Floods, 1-in-100-year, depth > 0 m. Every grade A and B site is scored; inland sites score zero.
- **Heat:** NASA POWER. The score is the 2020–2025 mean annual count of days above the site's 1991–2020 90th percentile, minus the 1991–2020 mean. Sites in the top tercile count as exposed. There is no fixed-threshold heat-index check, because the NWS chart could not be verified, and ERA5 is not used.
- **Water stress:** Aqueduct 4.0, top two baseline categories.

**Buffers:** 500 m for grade A sites; 2 km for grade B sites, with 5 km as a robustness check; OSM polygons plus 250 m. Locations are geocoded by hand, and the owner spot-checks every grade-A site.

**Firm score:** the unweighted share of grade A and B point sites exposed. River flood and heat are the primary hazards, and a combined index is secondary.

**Outcomes per firm-year:**

- Y1: climate share.
- Y2: specificity share.
- Y3: physical-risk share.
- Y4: site-named physical-risk mentions.

Y1 and Y2 come from ClimateBERT classifiers with a 0.5 decision threshold, validated against 200 hand-coded paragraphs. Y3 comes from a frozen hazard dictionary. Y4 combines a site dictionary with Y3. A readability threshold, calibrated on the Phase 0 files before use, sends garbled text layers to OCR.

**Controls:** log total assets, sector, foreign parent (50%; 20% as a robustness check), external assurance, Big Four auditor, document type and year.

## 7. Analysis

- **H1:** fractional logit of Y2 on exposure plus controls, with year and sector fixed effects.
- **H2:** comparison of explained variation for the exposure block against the institutional block.
- **H3:** firm fixed-effects trends in Y1 and Y4, and their difference.
- **H4:** descriptive shares with exact binomial intervals.
- **Inference:** standard errors clustered by firm, with the wild cluster bootstrap (9,999 replications).
- **Multiple testing:** Benjamini–Hochberg at q = 0.05 across the three confirmatory tests.
- **Population near exposed sites:** WorldPop, within 5 km.

The robustness checks are listed in `docs/design.md` §h.

## 8. Validation and stopping rules

- **Reliability:** intra-coder reliability from a re-code at least 7 days after the first pass, with a minimum alpha of 0.80.
- **Model accuracy:** a minimum kappa of 0.61 for model against human. The benchmark values are to be confirmed in the original texts before the paper.
- **If a classifier falls short:** one pre-declared threshold recalibration on a split sample. If it still falls short, the outcome is measured by human coding and the hypothesis becomes descriptive.

## 9. Deviations

All deviations are logged in `docs/amendments.md` before they are applied, stating whether outcome data had been seen.

## 10. Ethics and neutrality

The study uses public company documents and open data. Only aggregate population data are used, with no personal data. Results describe how disclosure aligns with exposure and make no claim about any firm's intent.

## Items to settle before submission

None for the design: OD-1 to OD-16 were decided on 2026-11-07. Submission to OSF is the owner's step. The IFRS S2 text is pending before Phase 6 and is not needed for registration.
