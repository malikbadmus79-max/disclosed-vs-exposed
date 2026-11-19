# Study design: Disclosed vs exposed

**Status: FROZEN on 2026-11-07 (version frozen-2026-11-07).** This document was written before any hazard score, model run on the corpus, or regression. Every number and choice below is repeated in `config/parameters.json`. The freeze record, with the SHA-256 hashes of both files, is in `docs/amendments.md`. Any later change must be logged there as an amendment (A1, A2, …) before it is applied.

**Status note (2026-11-17; the body of this design is unchanged).** The design has been amended after the freeze; read it together with `docs/amendments.md`. In particular, **A20** dropped the human validation of section g, made the frozen dictionary measures (Y3d, Y4d, Y4s, Y4r) the main outcomes for H1–H3 in place of the ClimateBERT measures (Y1, Y2, now exploratory and unvalidated), decided OD-11 by a pre-set rule (bare "heat" dropped, "extreme heat" added), and replaced the dictionary validation with a precision check. A18 and A19 are superseded.

**Owner decisions, all decided 2026-11-07.** Items marked "OD-n" in the text below are now decided as follows:

| ID | Decision |
|---|---|
| OD-1 | Coordinates are assigned by hand from OSM features and stated addresses; no web geocoding service in Phase 2. **The owner will spot-check every grade-A site location by hand before Phase 3** |
| OD-2 | Buffer radii: grade A 500 m; grade B 2 km (main) and 5 km (robustness); OSM polygon plus 250 m. These are analyst proposals without a citation, tested in the robustness checks |
| OD-3 | Flood depth > 0 m (main); depth ≥ 0.5 m as a robustness check |
| OD-4 | No separate coastal zone: every grade A and B point site is scored for coastal flood, and inland sites score zero |
| OD-5 | Heat exposure: the continuous score is the 2020–2025 mean annual TX90p-type count minus the 1991–2020 mean. A site is "exposed" if it is in the top tercile of sites on that score |
| OD-6 | **No fixed-threshold heat-index check.** The owner asked for the NWS categories to be verified from https://www.weather.gov/media/unr/heatindex.pdf. On 2026-11-07 that URL returned HTTP 404, so the categories were not verified and the agreed fallback applies. Adding the check later requires an amendment |
| OD-7 | ERA5 is not used. It is revisited only if several sites share one NASA POWER grid cell and need separating, which would require an amendment |
| OD-8 | The combined index (mean of hazard-specific `E_share`) is secondary. River flood and heat are the primary hazards |
| OD-9 | Readability threshold: a proposed 30% share of common English words, **calibrated on the Phase 0 files before use** (Unilever 2025 must fail and the other files pass). The calibrated value is recorded as an amendment |
| OD-10 | ClimateBERT thresholds of 0.5, with the one pre-declared recalibration if validation falls short |
| OD-11 | The hazard word list is accepted. Bare "heat" is dropped if validation shows false positives (for example "heat recovery"), and that change is recorded as an amendment |
| OD-12 | Minimums: intra-coder alpha ≥ 0.80 and model-versus-human kappa ≥ 0.61. **Benchmark values to be confirmed in the original texts before the paper** |
| OD-13 | Foreign-parent threshold of 50% (main control), with 20% as a robustness check |
| OD-14 | 9,999 wild-bootstrap replications (analyst proposal) |
| OD-15 | Benjamini–Hochberg at q = 0.05 across the H1–H3 primary tests |
| OD-16 | Population within 5 km of each exposed point site (analyst proposal) |

**Conventions.**

- "Not verified" means a claim or citation was not confirmed from a primary source read for this project.
- Citations marked *(Crossref)* were checked against Crossref metadata.
- Citations marked *(read)* were checked against the primary page or document.
- No other citations are used.
- The census figures come from `docs/phase0_audit.md`.

---

## a. Research questions and hypotheses (stated in advance)

**RQ.** Among NGX-listed firms with physical operations in Nigeria, how does the content of disclosure on physical climate risk relate to the measured hazard exposure of their sites, in 2020–2025, ahead of mandatory IFRS S1/S2 reporting? Mandatory reporting covers periods beginning on or after 1 January 2028, per the SEC circular of 23 September 2026 *(read)*.

| ID | Hypothesis | Test |
|---|---|---|
| H1 (substantive disclosure) | The specificity of a firm's physical-risk disclosure rises with the measured physical exposure of its sites | Positive association between firm exposure score and outcome Y2 (specificity share), net of controls |
| H2 (decoupling) | Disclosure is explained more by organisational and institutional characteristics (size, foreign parent, external assurance, sector) than by exposure | Relative explanatory contribution of the exposure block versus the institutional block for Y1–Y3 (section h) |
| H3 (symbolic adoption) | Climate language rises from 2020 to 2025 without a matching rise in site-specific physical-risk disclosure | Year trend in Y1 (climate share) is positive and larger than the trend in Y4 (site-named physical-risk mentions) |
| H4 (silence on exposed sites) | A substantial share of high-exposure sites is never named in the firm's reports | Descriptive: share of high-exposure point sites with zero mentions in any of the firm's documents for 2020–2025 |

**Pre-specification.** H1–H3 are confirmatory. H4 is descriptive, so no significance test is planned for it. All other analyses are exploratory and will be labelled as such.

**Theory.** The decoupling framing draws on Meyer & Rowan (1977), *American Journal of Sociology* 83(2), 340–363 *(Crossref)*, and Bromley & Powell (2012), *Academy of Management Annals* 6(1), 483–530 *(Crossref)*. Bromley & Powell distinguish policy–practice decoupling from means–ends decoupling. Selective disclosure follows Marquis, Toffel & Zhou (2016), *Organization Science* 27(2), 483–504 *(Crossref)*, and symbol versus substance follows Marquis & Qian (2014), *Organization Science* 25(1), 127–148 *(Crossref)*.

The study treats a mismatch between disclosure and exposure as a descriptive measure of possible decoupling. **It does not treat a mismatch as evidence of intent or misconduct by any firm.**

---

## b. Units of analysis

| Unit | Definition | Used for |
|---|---|---|
| Site | One facility record in the geodatabase, a point site or a dispersed asset | Exposure scoring; H4 |
| Firm | One NGX issuer in the census | Firm exposure score; cross-sectional H1/H2 |
| Firm-year | Firm × fiscal year, 2020–2025, keyed to the fiscal-year end of each document | Text outcomes; H1–H3 panel models |
| Paragraph | One text segment (section f) | Classification; validation |

**Fiscal years.** These differ by firm; Guinness's year ends in June, for example. A firm-year is labelled by the calendar year in which its fiscal year ends.

---

## c. Census

- **Main census: 59 firms.** These are the core firms with physical operations in Nigeria in the NGX equities price list of 06 Nov 2026: 50 mainly point sites, 9 mainly dispersed assets. Source: `data/interim/ngx_census_frame.csv`, column `census_stratum = main`.
- **Robustness stratum: 18 firms.** These are services firms with physical sites, analysed separately and never pooled into the main estimates.
- **Document test.** A firm stays in the census if a full annual report is available for at least one fiscal year from 2023 to 2025. 14 firms have passed and 45 are pending. A firm that fails is excluded and listed with the reason.
- **Exclusion rules:**
  1. Funds, REITs and other non-operating instruments are already excluded (8 tickers).
  2. Delisted firms are excluded. Flour Mills of Nigeria is kept only as a methods note.
  3. Firms that fail the document test are excluded.
  4. **Board flags.** A firm is excluded only if its flag is confirmed, from a primary NGX source, to mean suspended or delisting. As of Phase 0, no flag meaning is verified. If DWL is confirmed to mean delisting, MULTITREX and UNIONDICON leave the main census, an amendment is logged, and all main results are reported both with and without them.
  5. The 10 unresolved tickers stay excluded unless Phase 2 identifies them as firms with physical operations. Any that are added are logged as an amendment.
- **Verification in Phase 2.** Each firm's sector and issuer identity is confirmed from a primary source; Phase 0 identifications are marked "not verified". Reclassifications are logged.
- **Fixing the census.** The census is fixed at the end of Phase 2, before any outcome is computed.

---

## d. Location rules

**Grades:**

| Grade | Meaning |
|---|---|
| A | Exact coordinates or a full address |
| B | Town or industrial estate |
| C | State only, or local government area (LGA) only |
| D | Not stated |

**Rule C1.** An estate name without a town is grade B only if it can be matched to a unique location in report text or OSM; otherwise it is C.

**Asset types:**

- **Point sites:** plants, breweries, factories, mills, terminals, flow stations, platforms, distribution centres, data centres and plantation estates. Plantation estates are flagged as bounded areas, where a polygon is preferred.
- **Dispersed assets:** oil and gas licence areas, telecom networks, and unnamed networks of many small sites such as depots. They are measured at state or area level and analysed separately. Licence-block boundaries are out of scope.

**Allowed location sources, in priority order.** The source of every coordinate is recorded in `location_source`.

1. The company's own reports.
2. The company's website, environmental impact assessments (EIAs) and public regulator records.
3. OpenStreetMap, under ODbL with the attribution "© OpenStreetMap contributors".
4. For dispersed assets only: the company's own reports, then Global Energy Monitor (only after its licence is verified), then regulator records such as NUPRC and NCC.

The Phase 0 access rules apply to every source: robots.txt, site terms, no logins and no workarounds.

**Analysis sets:**

- **Main analysis:** grade A and B point sites, located from the report or from priority-2 sources.
- **Robustness R1:** add grade C point sites.
- **Robustness R2:** add point sites whose location comes from OSM.
- **Robustness R3:** report-only locations.
- **Separate analysis:** dispersed assets at state level.

**Geocoding.**

- Grade A addresses are geocoded to a point.
- Grade B towns or estates are geocoded to the town or estate centroid, or to the OSM feature centroid where a name match is confirmed.
- Every coordinate carries a `geocode_precision_m` value.
- **Geocoding is done by hand** from OSM features and stated addresses, with no web geocoding service in Phase 2 (OD-1).
- The owner spot-checks every grade-A site location by hand before Phase 3.

---

## e. Hazard rules

All hazard data are baseline unless stated. Future scenarios are reported descriptively only: they enter no hypothesis test, because the disclosures concern 2020–2025.

### e1. River flood

| Item | Proposal | Justification / source |
|---|---|---|
| Dataset | JRC Global river flood hazard maps v2.1.2, 3 arc-second (about 90 m) depth tiles | README *(read)*. Licence ODbL v1.0 *(read)* |
| Variable | Water depth (m) in the 1-in-100-year (RP100) map | |
| Exposure threshold (main) | Site exposed if any cell within the buffer has depth > 0 m in RP100 | The EU Floods Directive 2007/60/EC, Art. 6(3)(b), defines the medium-probability hazard-map scenario as "likely return period ≥ 100 years" *(read)*. No citable depth-damage source was verified, so depth ≥ 0.5 m is used only as a robustness check (OD-3) |
| Continuous score | Share of buffer area with depth > 0 m; maximum depth in buffer | |
| Robustness | RP10 (high probability) and RP500 (low probability) maps | The same Directive article lists high- and low-probability scenarios *(read)* |
| Scenario | Baseline only (the maps are static) | README *(read)* |

### e2. Coastal flood

| Item | Proposal | Justification / source |
|---|---|---|
| Dataset | WRI Aqueduct Floods Hazard Maps v2.0, coastal layer | Data page *(read)*. Licence not verified |
| Variable | Inundation depth (m), RP100, baseline | The return-period choice mirrors e1 |
| Threshold | Depth > 0 m within the buffer | As e1 |
| Future (descriptive only) | 2050 under the higher-emissions scenario offered by the dataset | The dataset page lists 2030, 2050 and 2080 *(read)*. The scenario names (RCP4.5/RCP8.5) come from a search summary of the Earth Engine catalogue: not verified |
| Applies to | Every grade A and B point site; inland sites score zero, so no separate coastal zone is defined (OD-4) | |
| Resolution | Not verified (Phase 0). It must be confirmed before freezing. If coarser than about 1 km, coastal flood is scored only for grade A and B sites, as a robustness check | |

### e3. Heat

| Item | Proposal | Justification / source |
|---|---|---|
| Dataset | NASA POWER daily point API (MERRA-2 based): T2M_MAX, T2M_MIN, RH2M | Phase 0 test passed for Ota, 1990–2025 *(read)*. NASA POWER is sufficient for Phases 0–2 (owner decision) |
| Main metric | Annual count of days with T2M_MAX above the site's own 90th percentile for 1991–2020 (a TX90p-type index) | Percentile-based extreme indices follow Zhang et al. (2011), *WIREs Climate Change* 2(6), 851–870 *(Crossref)*. 1991–2020 is the current WMO standard normal period (WMO material seen in search; WMO-No. 1203 not read: not verified) |
| Exposure score and flag | Continuous score: the 2020–2025 mean annual count minus the 1991–2020 mean. A site is exposed if it is in the top tercile of sites on that score (OD-5) | The tercile rule avoids an absolute margin that has no citation |
| Fixed-threshold heat-index check | **Not included (OD-6).** The official NWS chart URL supplied by the owner (https://www.weather.gov/media/unr/heatindex.pdf) returned HTTP 404 on 2026-11-07, so the category thresholds could not be verified | If the chart is verified later, adding the check needs an amendment. The heat index would be computed with the NWS Rothfusz regression (NOAA WPC; NWS TA SR 90-23 *(read)*; Steadman 1979, *J. Applied Meteorology* 18(7), 861–873 *(Crossref)*) |
| Known limitation | RH2M is a daily mean, not the humidity at the time of maximum temperature, so the heat index will be approximate | |
| ERA5 | Not used (OD-7). It is revisited only if several sites share one NASA POWER grid cell (0.5° latitude; longitude spacing not verified) and need separating, which would require an amendment | |
| Buffer | None: one grid-cell value per site | The grid is far coarser than any buffer |

### e4. Water stress

| Item | Proposal | Justification / source |
|---|---|---|
| Dataset | WRI Aqueduct 4.0, baseline annual | CC BY 4.0 *(read)*. Kuzma et al. (2023), DOI 10.46830/writn.23.00061 *(Crossref)* |
| Variable | `bws_cat`, `bws_label` and `bws_raw` (baseline water stress) at HydroBASIN level 6 sub-basin | Column names from the Earth Engine catalogue *(read)*. HydroBASIN level 6 from the WRI FAQ *(read)* |
| Threshold | Site exposed if it lies in a sub-basin in the dataset's two highest stress categories | The band cut-offs and label text are **not verified** and must be read from `bws_label` and the technical note in Phase 2 |
| Future (descriptive only) | 2030 and 2050 under the dataset's business-as-usual scenario | Scenario names come from a search summary: not verified |
| Buffer | None: sub-basin polygon containing the site | |

### e5. Buffers (river and coastal flood only)

| Location grade | Proposed buffer radius | Justification |
|---|---|---|
| A | 500 m | Covers a typical plant footprint plus geocoding error. Analyst proposal; no citation |
| B (town or estate centroid) | 2 km in the main analysis, with 5 km as a robustness check | Reflects town-level positional uncertainty. Analyst proposal; no citation |
| C | State level only: share of the state's area exposed. Robustness only | |
| OSM polygon available | The polygon itself, plus 250 m | Analyst proposal; no citation |

These radii were decided under OD-2. They are analyst proposals and are tested in the robustness checks.

### e6. Firm exposure score

There are no capacity or output weights, unless a report states them for every site of the firm (owner rule). For each hazard *h* and firm *i*, over its main-analysis point sites:

- `E_share[h,i]` = share of the firm's sites exposed. **This is the main measure.**
- `E_any[h,i]` = 1 if any site is exposed.
- `E_max[h,i]` = the largest continuous score across sites.

**Primary hazards:** river flood and heat. A combined index, the mean of the hazard-specific `E_share` values, is reported as secondary (OD-8). Hazard-specific results are always reported.

**Dispersed assets** get a separate state-level score: the share of the states they operate in that are exposed. It is reported separately and never averaged into the point-site score.

**Exposure enters the analysis as a cross-sectional firm characteristic,** using baseline hazard plus the 2020–2025 heat anomaly. The exposure measures are computed before any text outcome is examined, in Phase 3, after the design is frozen.

---

## f. Text rules

### f1. Documents and sections

- **Documents:** for each firm-year from 2020 to 2025, the annual report and any separate sustainability or integrated report. The document type is recorded for each one: full annual report, integrated report, sustainability report, sustainability extract, or financial-statement-only filing.
- **Sections:** all narrative text. The audited financial statements and notes are excluded, except notes that name sites, which are used for the site-mention measure. Section boundaries are tagged by hand in a small table per document, recording start and end pages.
- **Financial-statement-only filings** stay in the corpus with their document type recorded. "No narrative disclosure" is itself a finding.

### f2. Text extraction and OCR

- **Text layer:** PyMuPDF, with Unicode NFKC normalisation to fix ligatures (the Phase 0 finding).
- **Readability check (new):** a document passes if at least a threshold share of its tokens are among the 1,000 most common English words. This catches garbled text layers like the one in Unilever's 2025 report, which a character-count test passed. The proposed threshold is 30%. **It is calibrated on the Phase 0 files before use** (Unilever 2025 must fail and the other files pass), and the calibrated value is recorded as an amendment (OD-9).
- **OCR** for files with no text layer or that fail the readability check: OCRmyPDF (MPL-2.0) driving Tesseract (Apache-2.0), with English language data. Licences are from the GitHub API *(read)*. The tool versions are recorded when installed. OCR quality is checked by reading 2 random pages per OCR'd document against the page image.

### f3. Segmentation

- **Paragraphs:** PyMuPDF text blocks. Adjacent blocks with the same font size and no blank line between them are merged.
- **Minimum length:** 40 words, as in the Phase 0 smoke test. Shorter blocks, such as headings and table cells, are dropped from model scoring but kept for the site-mention dictionary.
- **Long paragraphs:** those over 512 tokens (the model limit) are split at sentence boundaries into pieces of 512 tokens or fewer, and each piece is scored separately.
- **Deduplication:** identical paragraphs repeated within one document (for example, running headers) are counted once.

### f4. Models and decision thresholds

The ClimateBERT classifiers come from Hugging Face; all are Apache-2.0 *(read)*. The model revision hash used is recorded in `config/parameters.json` when the corpus is scored.

| Model | Label used | Decision rule (decided, OD-10) |
|---|---|---|
| climatebert/distilroberta-base-climate-detector | yes | Climate paragraph if P(yes) ≥ 0.5 |
| climatebert/distilroberta-base-climate-specificity | spec | Among climate paragraphs, specific if P(spec) ≥ 0.5 |
| climatebert/distilroberta-base-climate-tcfd | governance, strategy, risk, metrics | Arg-max label among climate paragraphs |
| climatebert/distilroberta-base-climate-sentiment | risk, opportunity, neutral | Arg-max label among climate paragraphs |

**Thresholds.** The 0.5 thresholds were decided under OD-10. Whether the original papers used 0.5 is not verified. The thresholds may be changed only through the validation step in section g, before outcomes are computed, and any change is logged as an amendment.

**Physical-risk identification.** No ClimateBERT physical-risk classifier was verified: `climatebert/transition-physical` publishes only the labels LABEL_0–LABEL_2. A climate paragraph is therefore tagged *physical-risk* if it contains at least one term from a pre-specified hazard dictionary, frozen with the design:

> flood, flooding, inundation, rainfall, storm, drought, water scarcity, water stress, heat, heatwave, extreme temperature, erosion, sea level, coastal, desertification, wildfire

The term list was decided under OD-11, and its accuracy is validated in section g. If validation shows false positives for bare "heat" (for example "heat recovery"), that term is dropped and the change is recorded as an amendment.

Background on the models: Webersinke et al., arXiv:2110.12010 *(read)*; Bingler et al. (2022), *Finance Research Letters* 47, 102776 *(Crossref)*; Bingler et al. (2024), *Journal of Banking & Finance* 164, 107191 *(Crossref)*.

### f5. Site-mention dictionary

The dictionary is built from `data/interim/facility_locatability.csv` before scoring. For each site it holds:

- the facility name
- the town or estate name
- any alternative spellings found in the firm's own reports

Generic words such as "plant" or "factory" are never used alone. A paragraph **names a site** if it contains a site's town or estate name together with that firm's facility context within the same paragraph. The dictionary is frozen before outcomes are computed.

### f6. Outcome measures (per firm-year)

| ID | Measure | Definition |
|---|---|---|
| Y1 | Climate share | Climate paragraphs ÷ all scored narrative paragraphs |
| Y2 | Specificity share | Specific climate paragraphs ÷ climate paragraphs (missing if there are no climate paragraphs) |
| Y3 | Physical-risk share | Physical-risk climate paragraphs ÷ climate paragraphs |
| Y4 | Site-named physical-risk mentions | Count of physical-risk climate paragraphs that name at least one of the firm's sites. Also reported as a binary (any mention) |
| Y5 (site level, for H4) | Site ever named | 1 if the site is named in any of the firm's documents for 2020–2025, in any context |

---

## g. Validation

- **Sample:** 200 paragraphs, drawn before any outcome is examined. They are stratified by:
  - document type, with financial-statement-only filings capped at 10%
  - model prediction (climate yes/no; within climate, specific/non-specific)
  - physical-risk dictionary tag (yes/no)

  Each firm contributes at most 10 paragraphs. The random seed is fixed in `config/parameters.json`.
- **Coder:** the project owner. The coder sees no model outputs.
- **Codebook:** written before coding and frozen with the design. For each paragraph it records:
  - (i) climate-related yes/no
  - (ii) specific yes/no, defined as containing a quantity, date, named location, named asset or named action
  - (iii) physical-risk yes/no
  - (iv) TCFD category
  - (v) names a company site yes/no

  Each item has a definition, inclusion and exclusion rules, and two worked examples. The examples come from the Phase 0 smoke-test document, whose labels were never recorded.
- **Intra-coder reliability:** the owner re-codes the same 200 paragraphs, in a new random order, at least 7 days after the first pass.
- **Metrics:**
  - Krippendorff's alpha for intra-coder reliability (Hayes & Krippendorff 2007, *Communication Methods and Measures* 1(1), 77–89 *(Crossref)*).
  - Cohen's kappa and F1 for model against human (Cohen 1960, *Educational and Psychological Measurement* 20(1), 37–46 *(Crossref)*).
  - The reference coding is the owner's first pass, with disagreements resolved in the second pass.
- **Minimum acceptable levels (decided, OD-12):**
  - Intra-coder alpha ≥ 0.80.
  - Model against human: kappa ≥ 0.61 for each classifier used for Y1–Y3.

  The 0.80 level is attributed to Krippendorff, *Content Analysis* (2019 edition, DOI 10.4135/9781071878781 *(Crossref)*), and the 0.61 band to Landis & Koch (1977), *Biometrics* 33(1), 159 *(Crossref)*. **Benchmark values to be confirmed in the original texts before the paper.**
- **Fallback if a classifier falls short:**
  1. Recalibrate the decision threshold on half of the validation sample and re-test on the other half. This is one pre-declared attempt, logged as an amendment.
  2. If the classifier still falls short, the outcome is measured from human coding of a firm-stratified sample instead of the model, and the affected hypothesis is reported as descriptive only.
  3. If intra-coder alpha falls short, the codebook is revised, a fresh sample of 100 paragraphs is coded, and the revision is logged.

---

## h. Analysis plan

**Data:** the firm-year panel of the main census, 2020–2025. Firms enter only for years with documents.

**H1:**

`Y2_it = β·E_i + γ·X_it + δ_t + σ_s + ε_it`

- `E_i`: firm exposure (`E_share`, combined index; hazard-specific versions reported).
- `X_it`: the controls listed below.
- `δ_t`: year fixed effects.
- `σ_s`: sector fixed effects.
- Estimated by fractional logit (main) and OLS (robustness).

**Firm fixed effects** are not used for H1/H2, because exposure does not vary over time. They are used for H3.

**H2:**

- **Specifications:** the H1 specification is estimated with three blocks of regressors, on standardised variables: (a) exposure only, (b) institutional variables only, (c) both.
- **Comparison:** the increase in explained variation from each block, and the standardised coefficients.
- **Result in favour of H2:** the institutional block explains more than the exposure block. The comparison is reported with bootstrap intervals.

**H3:**

`Y_it = α_i + τ·t + ε_it`

- Estimated for Y1 and for Y4. `α_i` is the firm fixed effect.
- H3 is supported if τ(Y1) > 0 and τ(Y1) exceeds τ(Y4), on comparable standardised scales, with a bootstrap interval for the difference.

**H4:** descriptive. It is the share of high-exposure point sites (exposed on at least one hazard) with Y5 = 0, reported overall, by firm and by sector, with exact binomial intervals.

**Controls:**

| Control | Definition |
|---|---|
| Size | Log total assets, from audited statements, in the reporting currency |
| Sector | Phase 2-verified NGX sector |
| Foreign parent | Parent or ultimate owner domiciled outside Nigeria holding at least 50%, per the annual report (OD-13). A 20% threshold is a robustness check |
| External assurance | Independent assurance of sustainability or climate information, yes/no |
| Auditor | Big Four yes/no |
| Document type | As section f1 |
| Year | Year fixed effects |

**Standard errors:** clustered by firm. With about 59 clusters, inference uses the wild cluster bootstrap (Cameron, Gelbach & Miller 2008, *Review of Economics and Statistics* 90(3), 414–427 *(Crossref)*; MacKinnon & Webb 2017, *Journal of Applied Econometrics* 32(2), 233–254 *(Crossref)*). The bootstrap uses 9,999 replications (OD-14).

**Small-N caveat:** about 59 firms, fewer after the document test. Reporting emphasises effect sizes with intervals, and descriptives such as scatterplots of exposure against disclosure and firm-level tables, over p-values. Firm-level results are reported in neutral terms and make no claim about any firm's motives.

**Multiple testing:** the confirmatory family is H1, H2 and H3, each with its primary outcome, so three tests. Benjamini & Hochberg (1995), *JRSS-B* 57(1), 289–300 *(Crossref)*, controls the false discovery rate at q = 0.05 (OD-15, decided). Hazard-specific and robustness results are exploratory and unadjusted, and labelled as such.

**Robustness checks:**

1. R1–R3 location sets (section d).
2. 5 km buffers for grade B sites.
3. RP10 and RP500 flood maps.
4. Flood depth ≥ 0.5 m in place of > 0 m.
5. OLS in place of fractional logit.
6. A 20% foreign-parent threshold in place of 50%.
7. Excluding financial-statement-only firm-years.
8. Excluding DWL-flagged firms.
9. The 18-firm robustness stratum, estimated separately.
10. Leave-one-sector-out.
11. Dispersed-asset firms analysed separately.

---

## i. Sociology and policy component

**Decoupling framing:**

- **Policy–practice decoupling** (Meyer & Rowan 1977; Bromley & Powell 2012): the gap between climate-risk statements and site-level exposure.
- **Means–ends decoupling** (Bromley & Powell 2012): disclosure activity, such as TCFD-labelled sections, that is not linked to the sites where hazards occur.

The study is descriptive. It measures alignment and does not infer intent.

**Workers and communities near exposed sites:**

- **Population:** WorldPop Global2 R2025A, 100 m, 2025, constrained (CC BY 4.0) *(read)*. The figure is the population within the site buffer and within 5 km of each exposed point site (OD-16, decided), summed across a firm's exposed sites without double counting overlapping buffers.
- **Workers:** employee numbers where reports state them by site; otherwise firm totals only, labelled as such.
- **Reporting:** results are reported in aggregate and by sector. No individual or household data are used.

**Policy coding scheme.** Each firm-year is coded against the following elements:

| Code | Element | Source of element |
|---|---|---|
| P1 | Climate resilience of strategy to physical risks discussed | FRC Roadmap (Amended 2026), PDF p23: "Climate resilience of strategy and business model to both transition and physical risks" *(read)* |
| P2 | Scenario analysis used (qualitative or quantitative) | FRC Roadmap, PDF p23–24 *(read)* |
| P3 | A metric for climate-related physical risks reported | FRC Roadmap, PDF p25: cross-industry metric category "Climate-related physical risks" *(read)* |
| P4 | Physical-risk process integrated in risk management | FRC Roadmap §7.4 *(read)* |
| P5 | Locations or assets at physical risk identified | To be anchored to IFRS S2 paragraph text: **pending — owner to supply IFRS S2 before Phase 6**. Until then, defined from the FRC Roadmap only |
| P6 | Adoption status: early, voluntary, or none per the FRC phases | FRC Roadmap §6.1 *(read)*; SEC circular *(read)* |
| P7 | Reference to the NGX Sustainability Disclosure Guidelines | NGX Guidelines, approved by the SEC on 9 Nov 2018 *(read)* |

**IFRS S2 quotes and paragraph numbers** are added only after the standard is supplied and read. Until then, no IFRS S2 paragraph number appears in any output.

---

## j. Known limitations and threats to validity

1. **Location precision.** Most sites are town-level, and none has coordinates. River-flood exposure from a 90 m map with 2 km buffers measures exposure near the site, not damage.
2. **Hazard maps measure hazard, not risk.** JRC and Aqueduct flood maps ignore local protection; Aqueduct states it models no flood protection *(read)*. The NASA POWER grid is coarse.
3. **Heat is measured by temperature only.** No heat-index check is included, because the NWS chart URL supplied was unavailable (OD-6). If a heat index is added later, it would be approximate, because only daily-mean humidity is available.
4. **Coverage of dispersed assets is weak.** Telecom networks and oil licences are scored only at state level.
5. **Classifier transfer.** ClimateBERT was not trained on Nigerian reports, so validation results bound all text outcomes.
6. **Documents vary.** Financial-statement-only filings, integrated reports, OCR'd scans and garbled text layers produce measurement error that varies by document type.
7. **Small N.** About 59 firms limits power and the number of covariates, so results lean on effect sizes.
8. **Survivorship.** The census is drawn from firms listed on 06 Nov 2026. Firms delisted between 2020 and 2025, such as Flour Mills, are excluded, which may bias results towards survivors.
9. **Provisional census.** Sector and issuer labels are not verified until Phase 2, and board-flag meanings are not verified.
10. **Single coder.** Validation uses one coder, measuring intra-coder reliability only. Inter-coder reliability is not measured.
11. **Access asymmetry.** Some firms' reports were obtained only through the owner's browser downloads, so documents may be missing unevenly across firms.
12. **The policy benchmark is incomplete.** IFRS S2 text is pending, so P5 rests on the FRC Roadmap until it is supplied.
