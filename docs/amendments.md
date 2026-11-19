# Amendments log

This log records every change to `docs/design.md` or `config/parameters.json` after the design is frozen. Changes made before the freeze are not logged here.

**Freeze status: FROZEN on 2026-11-07,** version `frozen-2026-11-07`.

## Freeze record

| File | SHA-256 | Size (bytes) |
|---|---|---|
| `config/parameters.json` | `0ca716a8ea027ddc210d3e6bdfe2863f58a9ba1d61c5a66c623852daff67167f` | 17,596 |
| `docs/design.md` | `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714` | 32,278 |

- **Frozen by:** the project owner, with decisions dated 2026-11-07.
- **Hash method:** computed on 2026-11-07 with PowerShell `Get-FileHash -Algorithm SHA256`, over the files exactly as saved.
- **To check later,** run `Get-FileHash <file> -Algorithm SHA256` or `sha256sum <file>`. Any difference means the file changed after the freeze and needs an amendment.
- **Outcome data seen before the freeze:** none. No hazard score, corpus-level text outcome or regression had been computed. Phase 0 produced only access tests: a NASA POWER series for one town point, and a ClimateBERT smoke test on 20 paragraphs whose labels and scores were never recorded.
- **Decisions made at the freeze:** OD-1 to OD-16 are all decided. They are listed at the top of `docs/design.md` and recorded with `decided_on: 2026-11-07` in `config/parameters.json`.
- **OD-6:** the owner-specified NWS chart URL (https://www.weather.gov/media/unr/heatindex.pdf) returned HTTP 404 on 2026-11-07, so the categories were not verified. The fallback applies: there is no fixed-threshold heat-index check.
- **Follow-ups already committed to before use, each to be logged as an amendment when it is done:**
  - Calibrate the readability threshold (OD-9).
  - Drop bare "heat" from the dictionary if validation shows false positives (OD-11).
  - Confirm the alpha and kappa benchmark values in the original texts before the paper (OD-12).
  - Exclude DWL-flagged firms if DWL is confirmed to mean delisting.
  - Add any resolved tickers.
  - Add the IFRS S2 paragraph anchors for policy code P5, once the standard is supplied.

**Rules.**

1. Number amendments in order: A1, A2, and so on. Never renumber or delete an entry.
2. Log an amendment *before* the changed method is applied.
3. State whether any outcome data had been seen when the change was decided.
4. Update `config/parameters.json` in the same step, and record the new file hash once hashing is in use.

---

## Template

```
### A<n>: <short title>
- Date:
- Decided by:
- Section(s) of design.md affected:
- Parameter(s) in config/parameters.json affected (old value -> new value):
- Reason:
- Outcome data seen before this decision? (yes/no; if yes, which):
- Effect on confirmatory hypotheses (none / H1 / H2 / H3):
- Results to be reported both ways? (yes/no):
- parameters.json hash after change:
```

---

## Amendments

### A1: Readability threshold calibrated (OD-9) and word-list source fixed
- Date: 2026-11-12 (logged before the test was run on the corpus).
- Decided by: the project owner (decision of 2026-11-12: use wordfreq's top 1,000 English words, calibrate the 30% threshold on the Phase 0 files and log the result as A1). The calibrated value was computed by the analyst under the frozen calibration rule.
- Section(s) of design.md affected: f2, "Readability check". design.md itself is not edited; this entry records the calibrated value, as f2 and OD-9 require.
- Parameter(s) in config/parameters.json affected (old value -> new value):
  - `text.readability_min_common_word_share.value`: 0.3 -> 0.25.
  - New fields: `calibrated_on`, `amendment`, `previous_value`, `word_list`, `tokens` and `calibration_file`.
- Method fixed by this amendment:
  - **Word list:** `wordfreq.top_n_list('en', 1000)` from wordfreq 3.1.1 (https://github.com/rspeer/wordfreq). The code is Apache-2.0 and the data CC BY-SA 4.0, per the package metadata. Citation: Robyn Speer (2022), rspeer/wordfreq: v3.0 (v3.0.2), Zenodo, https://doi.org/10.5281/zenodo.7199437.
  - **Text:** PyMuPDF with Unicode NFKC (f2), whole document.
  - **Tokens:** `wordfreq.tokenize(text, 'en')`, keeping only tokens with at least one letter, so that figures in financial tables do not count as non-words.
  - **Share:** tokens in the list / all kept tokens. A document passes if the share is at least the threshold.
  - **Code:** `src/readability.py`.
- Reason: OD-9 requires calibration on the Phase 0 files before use, such that Unilever 2025 fails and the other files pass. The calibration set is the 35 Phase 0 files with a text layer. The three scanned Okomu files (FY2020, FY2023, FY2024) have no text to test; they are OCR cases. Results are in `data/interim/readability_calibration.csv`:

  | File | Share |
  |---|---|
  | Unilever 2025 | 0.0095 |
  | BUA Cement 2024 | 0.2807 |
  | All other 33 files | 0.459 to 0.636 |

  - **0.30 fails the rule.** BUA Cement 2024 would also fail. Its text layer is partly garbled: 36 of its 148 pages have a share below 0.20, and some carry stray non-Latin glyphs.
  - **Any value from 0.0095 up to and including 0.2807 meets the rule.** 0.25 is the highest multiple of 0.05 in that range, which keeps the threshold as close as possible to the proposed 0.30.
- Outcome data seen before this decision? No. No hazard score, ClimateBERT label, dictionary count or regression had been computed. The only data seen were the readability shares of the Phase 0 calibration files, which the calibration rule requires.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none directly. The threshold decides which files need OCR before text analysis, not the outcome measures.
- Results to be reported both ways? Yes, as a robustness note: corpus files with a share between 0.25 and 0.30 are listed in `docs/phase2_sites.md`.
- parameters.json hash after change: `f3182d6ecb93f960b13d260dcb9e8b16fa51d33f77c9c6e01a1c16df7e1126f2` (SHA-256; frozen hash was `0ca716a8ea027ddc210d3e6bdfe2863f58a9ba1d61c5a66c623852daff67167f`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.
- **Confirmed by the owner on 2026-11-12,** including the parameters.json edit and its new hash.

### A2: Page-level readability rule
- Date: 2026-11-12 (logged before the rule was applied to any file).
- Decided by: the project owner (decision of 2026-11-12).
- Section(s) of design.md affected: f2, "OCR". design.md itself is not edited; this entry adds a second trigger for OCR.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `text.readability_page_rule` (none -> `{"page_share_below": 0.2, "max_share_of_pages": 0.1}`, with its rule text).
- **Rule.** A report file is also OCR'd if more than 10% of its pages have a common-word share below 0.20.
  - **Share:** same word list (wordfreq 3.1.1 top 1,000 English words), text extraction (PyMuPDF + NFKC) and tokens (tokens with at least one letter) as A1.
  - **Empty pages:** a page with no word tokens counts as share 0. This is the analyst's implementation choice, fixed before the rule was applied; the rule targets pages with no usable text.
  - **Pages:** all pages of the file are counted.
  - **OCR:** same tools and settings as the other OCR copies (OCRmyPDF 16.13.0, Tesseract 5.4.0, Ghostscript 10.08.0; `--force-ocr -l eng --oversample 300 --jobs 4 --output-type pdf`). The OCR copy is used for all later text work.
  - **Scope:** every report file. OCR copies are not re-tested by this rule.
- Reason: the document-level test (A1) passes files whose text layer is garbled on many pages but not all of them. BUA Cement FY2024 scores 0.2807 overall, with 36 of 148 pages below 0.20. A whole-document average can hide such pages.
- Outcome data seen before this decision? No. No hazard score, ClimateBERT label, dictionary count or regression had been computed. The only data seen were readability shares (A1 calibration and corpus run) and BUA Cement FY2024's page-level shares, found while checking its calibration result.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none directly. The rule decides which text source (original layer or OCR copy) feeds later text measures, not how they are computed.
- Results to be reported both ways? Not planned. The files the rule catches are listed in `docs/phase2_sites.md`, so a check against the original text layer is possible.
- parameters.json hash after change: `bb6e2e885552c20bcbb5696d33152a2096e4cb229d86c0c61fee8250ba97e09c` (SHA-256; previous hash after A1 was `f3182d6ecb93f960b13d260dcb9e8b16fa51d33f77c9c6e01a1c16df7e1126f2`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A3: Page-level text selection for reports with an OCR copy
- Date: 2026-11-12 (logged before the rule was applied).
- Decided by: the project owner (decision of 2026-11-12).
- Section(s) of design.md affected: f2, "Text layer" and "OCR". design.md itself is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `text.page_text_selection` (none -> `{"original_page_min_share": 0.2}`, with its rule text). `text.readability_page_rule` (A2) is unchanged.
- **Rule.** For every report that has an OCR copy, the text used for all later analysis is chosen page by page:
  1. The original page text, if that page's common-word share is 0.20 or more.
  2. Otherwise, the OCR page text, if its share is 0.20 or more.
  3. If both are below 0.20, whichever has the higher share, and the page is flagged. On a tie, the original is used; this is the analyst's implementation choice, fixed before applying the rule.
- **Share:** same word list (wordfreq 3.1.1 top 1,000), text extraction (PyMuPDF + NFKC) and tokens (at least one letter) as A1 and A2. A page with no word tokens has share 0.
- **Effect on A2:** this replaces A2's "use the whole OCR copy". A2's trigger rule (which files get OCR'd) stays.
- **Outputs:** one text file per report, `data/interim/text/<key>.txt`, with page markers, and a per-page source table, `data/interim/text_sources.csv`. Code: `src/text_select.py`. No PDF is modified.
- Reason: `data/interim/a2_ocr_text_loss.csv` shows 42 pages where forced OCR lost text that the original layer had: 16 in Champion 2025, 20 in Guinness 2020, and 1 to 3 in Lafarge 2023, Academy 2025, and Guinness 2022 and 2024. Using whole OCR copies would discard good text.
- Outcome data seen before this decision? No. No hazard score, ClimateBERT label, dictionary count or regression had been computed. The only data seen were readability shares, OCR quality-check pages and page character counts.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none directly. The rule decides the text source, not how outcome measures are computed.
- Results to be reported both ways? Not planned. The per-page source table makes it possible to rebuild either text version.
- parameters.json hash after change: `3c81a7c2047df83a23a7f3ec686aa02208cec45279035c4aa3993397d02a91a4` (SHA-256; previous hash after A2 was `bb6e2e885552c20bcbb5696d33152a2096e4cb229d86c0c61fee8250ba97e09c`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A4: Refined page-level text selection (replaces A3's selection order)
- Date: 2026-11-12 (logged before the rule was applied).
- Decided by: the project owner (decision of 2026-11-12).
- Section(s) of design.md affected: f2, "Text layer" and "OCR". design.md itself is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `text.page_text_selection_a4` (none -> `{"both_low_share": 0.2, "min_token_ratio": 0.5}`, with its rule text). The A3 key is kept as a record.
- **Rule.** For each page of a report with an OCR copy, where an original and an OCR version both exist:
  1. **Default:** use the version with the higher common-word share.
  2. **Token-count override:** if that version has fewer than half the word tokens of the other version, use the other one.
  3. **Both low:** if both shares are below 0.20, keep A3's rule: use the higher share (the original on a tie) and flag the page.
- **Implementation choices, fixed before applying:**
  - **Equal shares:** the original is used.
  - **Override flag:** when the token-count override selects a version whose share is below 0.20, the page is also flagged.
  - **Shares and tokens:** the same as A1 to A3.
- **Outputs and code:** the same as A3, `data/interim/text/<key>.txt` and `data/interim/text_sources.csv`, written by `src/text_select.py`. The A3 versions are kept as `data/interim/text_sources_a3.csv` and `readability_merged_a3.csv` for the comparison. No PDF is modified.
- Reason: under A3, BUA Cement FY2024 kept partly garbled original pages (share at least 0.20) on 64 pages where the OCR page scored more than 0.15 higher; its merged text scored 0.382, against 0.541 for the whole OCR copy. The token-count override keeps the protection against pages where forced OCR lost text (`data/interim/a2_ocr_text_loss.csv`).
- Outcome data seen before this decision? No. No hazard score, ClimateBERT label, dictionary count or regression had been computed. The only data seen were readability shares, OCR quality-check pages and page token and character counts.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none directly. The rule decides the text source, not how outcome measures are computed.
- Results to be reported both ways? Not planned. The per-page changes from A3 to A4 are reported in `docs/phase2_sites.md`, and the A3 table is kept.
- parameters.json hash after change: `600bda8493bcd1e46e0cfaf69f0d5407f6ac50cf5b2911ef9b500727fdd37528` (SHA-256; previous hash after A3 was `3c81a7c2047df83a23a7f3ec686aa02208cec45279035c4aa3993397d02a91a4`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A5: Share condition on A4's token-count guard (text selection final)
- Date: 2026-11-12 (logged before the rule was applied).
- Decided by: the project owner (decision of 2026-11-12).
- Section(s) of design.md affected: f2, "Text layer" and "OCR". design.md itself is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `text.page_text_selection_a5` (none -> `{"guard_requires_other_share_at_least": 0.2}`, with its rule text). The A3 and A4 keys are kept as a record.
- **Rule.** A4's guard ("if the higher-share version has fewer than half the word tokens of the other, use the other one") applies only when the other version's share is at least 0.20. A version with a share below 0.20 can never win through the guard. Everything else in A4 stays: the higher share wins (the original on a tie), and if both shares are below 0.20 the higher share is used and the page is flagged.
- **Outputs and code:** the same as A4 (`src/text_select.py`, `data/interim/text/<key>.txt`, `data/interim/text_sources.csv`, `data/interim/readability_merged.csv`). The A4 versions are kept as `text_sources_a4.csv` and `readability_merged_a4.csv`. No PDF is modified.
- Reason: under A4, Unilever 2025's garbled original won on 7 pages (pp. 12, 15, 108 and 146–149). Its junk tokens inflated its token count, so the OCR page had fewer than half as many tokens, although its share was 0.21–0.66 against 0.00–0.14.
- Outcome data seen before this decision? No. No hazard score, ClimateBERT label, dictionary count or regression had been computed. The only data seen were readability shares and page token counts.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none directly. The rule decides the text source, not how outcome measures are computed.
- Results to be reported both ways? Not planned. The changes from A4 are reported in `docs/phase2_sites.md`, and the A3 and A4 tables are kept.
- parameters.json hash after change: `abe2795a83b263e3ef0cbb09f224916a80a66d7cc15d1abb78356dd1fc9eb86a` (SHA-256; previous hash after A4 was `600bda8493bcd1e46e0cfaf69f0d5407f6ac50cf5b2911ef9b500727fdd37528`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.
- **Text selection is final.** After A5, the text-selection rules (A2 trigger; A3 as refined by A4 and A5) are final for this study (owner decision of 2026-11-12). No further changes to text selection are planned.

### A6: Rule-based cross-check of grade-A locations replaces the owner's visual spot-check (OD-1)
- Date: 2026-11-12 (logged before the rule was applied).
- Decided by: the project owner (decision of 2026-11-12).
- Section(s) of design.md affected:
  - The OD-1 row in the decision table ("The owner will spot-check every grade-A site location by hand before Phase 3").
  - d, "Geocoding" ("The owner spot-checks every grade-A site location by hand before Phase 3").
  - The grade-A buffer (OD-2) for sites located only to a place centroid.
  - j, known limitations (note below).
  design.md itself is not edited; this entry records the change.
- Parameter(s) in config/parameters.json affected (old value -> new value):
  - `location.geocoder`: new fields `owner_spot_check_status` and `amendment`. The old `owner_spot_check` text is kept as a record.
  - New key `buffers_m.A_crosscheck` (none -> the category-to-buffer rule below).
  - `buffers_m.A` (500 m) is unchanged.
- **Rule.** Every grade-A row in `data/processed/spotcheck_gradeA.csv` (87 rows) is put in one category:

  | Category | Condition | Phase 3 buffer |
  |---|---|---|
  | `correct (rule-based)` | `coord_method` = osm_feature, the OSM feature's name matches the firm or site, and `state_check` is "consistent" or "no state in report text" | The design's grade-A buffer of 500 m (OD-2) |
  | `approximate (rule-based)` | `coord_method` = osm_place or osm_place_rank (a town, suburb, village or admin-area centroid) | The row's nominal precision (`coord_precision_m`: 2,000, 5,000 or 10,000 m) instead of 500 m |
  | `no coordinate` | No coordinate, or the coordinate was withdrawn | Not scored in Phase 3; reported as a limitation |

- **Implementation choices, fixed before applying:**
  - **Name test:** the OSM name of the feature (in `coord_source`) must contain the firm's name or brand as written in the report: Dangote, BUA Cement, Guinness, Cadbury, Nigerian Breweries, and so on.
  - **Failing osm_feature rows:** an osm_feature row that fails the name or state test would be treated as `approximate (rule-based)` with buffer = `coord_precision_m`. No row is in this case.
  - **Where the labels go:** in `spotcheck_gradeA.csv`, the label goes in "owner_check (ok / wrong / move-to)" and the comment "A6 rule-based cross-check, 2026-11-12" in "owner_comment".
  - **The buffer column:** `facilities.csv` gains a `buffer_m` column, filled for grade-A rows only. Grade B and C buffers follow OD-2 unchanged and are set in Phase 3.
  - **Code:** `src/a6_crosscheck.py`, called from `src/phase2_coordinates.py finalize` and `src/phase2_outputs.py`.
- **Counts** (set before applying, from the current `facilities.csv`; confirmed after applying in `docs/phase2_sites.md`):

  | Category | Rows | Detail |
  |---|---|---|
  | `correct (rule-based)` | 7 | |
  | `approximate (rule-based)` | 67 | 46 osm_place, 21 osm_place_rank |
  | `no coordinate` | 13 | 12 with no coordinate, 1 withdrawn |

- **Limitations note** (for design section j): "Location accuracy was assessed by a documented rule-based cross-check rather than manual visual inspection."
- Reason: owner decision to replace the manual visual spot-check with a documented, reproducible rule.
- Outcome data seen before this decision? No. No hazard score, ClimateBERT label, dictionary count or regression had been computed. Only location metadata (coordinate method, precision class, state check) was used.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): possible, through exposure measurement. Grade-A sites with a centroid location get larger buffers, and grade-A sites without a coordinate drop out of Phase 3 scoring. No outcome was computed before the decision.
- Results to be reported both ways? Not decided by the owner. A sensitivity check using 500 m for all grade-A sites with a coordinate would show the effect of the buffer change.
- parameters.json hash after change: `4d59d116d85bbdde45c8872677f09725a3548df4272e5fe9e8c4f89b78dfb1f4` (SHA-256; previous hash after A5 was `abe2795a83b263e3ef0cbb09f224916a80a66d7cc15d1abb78356dd1fc9eb86a`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A7: 500 m robustness check for grade-A sites; buffer precedence in Phase 3
- Date: 2026-11-12 (logged before any hazard was computed).
- Decided by: the project owner (Phase 3 brief, 2026-11-12). The precedence wording is the analyst's reading of the existing rules, logged here so that it is fixed before use.
- Section(s) of design.md affected: e5 (buffers), together with A6. design.md itself is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `buffers_m.A_robustness_500` (none -> 500, with its rule and precedence text).
- **Rule.** Besides the A6 buffers, which stay the main analysis, every grade-A site with a coordinate (A6 "correct" or "approximate") is also scored with a 500 m buffer. This version is labelled a robustness check everywhere.
- **Buffer precedence for river and coastal flood** (e5 with A6):

  | Grade | Main analysis | Robustness |
  |---|---|---|
  | A | The A6 buffer: 500 m if "correct", the nominal precision if "approximate"; not scored if "no coordinate". A6 is the later and more specific rule, so it is used even when the site's OSM feature is a polygon | 500 m for every grade-A site with a coordinate (A7) |
  | B | The OSM polygon plus 250 m if the site was located from an OSM way or relation feature (e5); otherwise a 2 km circle | 5 km for sites without a polygon. No polygon variant is defined, so polygon sites keep their main buffer |
  | C | State-level share only | Robustness only (e5) |

  Heat and water stress use no buffer (e3, e4).
- Reason: owner decision, to show how sensitive grade-A flood exposure is to the A6 buffer change.
- Outcome data seen before this decision? No. No hazard score, ClimateBERT label, dictionary count or regression had been computed. No hazard data had been downloaded.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none. This is an extra robustness check; the main analysis is unchanged.
- Results to be reported both ways? Yes: main (A6) and robustness (500 m), side by side in `docs/phase3_hazards.md`.
- parameters.json hash after change: `c0d34927e0dbce7e9e78865ee309d13b4804cc4d39e13d2bd32706ae48486d8e` (SHA-256; previous hash after A6 was `4d59d116d85bbdde45c8872677f09725a3548df4272e5fe9e8c4f89b78dfb1f4`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A8: JRC permanent-water mask as a river-flood robustness check
- Date: 2026-11-12 (logged before the mask was downloaded or applied).
- Decided by: the project owner (decision of 2026-11-12).
- Section(s) of design.md affected: e1 (river flood, robustness). design.md itself is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `hazards.river_flood.permanent_water_robustness` (none -> the rule below).
- **Rule.** Robustness check only; the main river-flood measure (e1) is unchanged.
  - **Mask:** the JRC v2.1.2 permanent-water tiles (`Permanent_WaterBodies/ID<n>_..._permanent_water.tif`), from the same JRC source under the same access rules.
  - **Measures:** for each scored site and its main buffer, two values are computed with permanent-water cells excluded: the share of the buffer flooded at RP100 (depth > 0 m), and an RP100 exposure flag.
  - **Firm level:** the firm `E_share` is recomputed from that flag.
  - **Implementation choice, fixed before applying:** a cell is "permanent water" if its mask value is non-zero and not nodata. The exact encoding is checked from the tile, and recorded in `docs/phase3_hazards.md`, before use.
- Reason: in the Phase 3 river-flood results, sites beside lagoons, rivers or the sea may count as exposed because of permanent water rather than flooding.
- Outcome data seen before this decision? No. No ClimateBERT label, dictionary count, disclosure measure or regression had been computed. Phase 3 hazard exposure results had been seen; they are exposure data, not outcome data.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none. This is an additional robustness check.
- Results to be reported both ways? Yes: main and permanent-water-excluded, side by side in `docs/phase3_hazards.md`.
- parameters.json hash after change: `587eb47d9db2c1c66d86b13d17e5f2939913c1f1473174e3fad009e3725051a0` (SHA-256; previous hash after A7 was `c0d34927e0dbce7e9e78865ee309d13b4804cc4d39e13d2bd32706ae48486d8e`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A9: heat uses the MERRA-2 native grid cell that contains each site
- Date: 2026-11-12 (logged before the new cell assignment is applied to any heat score, and before the new files are downloaded).
- Decided by: the project owner (decision of 2026-11-12).
- Section(s) of design.md affected: e3 (heat). design.md itself is not edited: e3 already says "one grid-cell value per site", and this amendment fixes how the cell is found.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `hazards.heat.grid_cell_assignment` (none -> the rule below).
- **Rule (fixed, not chosen on results).** Each site's heat series is the NASA POWER series of the **MERRA-2 native grid cell that contains the site**.
  - **Grid:** MERRA-2's published native grid, 0.5° latitude × 0.625° longitude, with cell centres at latitude −90° + 0.5° × i and longitude −180° + 0.625° × j. The NASA POWER file headers give the 0.5 × 0.625 cell size; the alignment is MERRA-2's published grid definition.
  - **Cell of a site:** the cell whose latitude range [centre − 0.25°, centre + 0.25°) and longitude range [centre − 0.3125°, centre + 0.3125°) contain the site's coordinate. A site exactly on an edge goes to the cell to its north or east.
  - **Request:** one POWER Data Access Viewer download per cell, at the exact cell centre, so the request point is never on a cell edge.
  - **Cells downloaded:** every native cell containing at least one main-analysis site (`docs/nasa_manual_download_v2.md`). Office and R2 sites are assigned the same way; one in a cell without a main-analysis site is not scored for heat, as under the owner's earlier decision for the first download.
  - **Unchanged:** metric (TX90p-type, pooled 1991–2020 90th percentile), score (2020–2025 mean minus 1991–2020 mean), exposure (top tercile of main-set sites, OD-5), OD-6 and OD-7.
- **Replaces:** the 0.5° × 0.5° bins with edges at multiples of 0.5°, requested at the bin centre. That was an implementation choice based on the POWER API page's "0.5° x 0.5° global grid", not a design rule. The file headers later showed the native grid is 0.5° × 0.625°. Under the old mapping, every request latitude lay exactly on a native cell edge, and the series used came from the cell containing the site for only 26–32 of the 71 main sites (`docs/phase3_hazards.md`, section 1.4).
- Reason: a technical correction. The old bins did not match the data's native grid, so many sites took the series of a neighbouring cell. The rule above is the only one consistent with e3's "one grid-cell value per site".
- Outcome data seen before this decision? **Yes, heat exposure results had been seen.** The heat scores from the old 0.5° bins (first from the API files, then identical from the owner's manual downloads), the 16.06 days/yr tercile cut-off, the site and firm heat exposure, and the combined index had all been computed and reported in `docs/phase3_hazards.md`. These are exposure data, not disclosure outcomes: no ClimateBERT label, dictionary count, disclosure measure or regression had been computed. The change was not chosen on those results. It follows from the file headers, and the rule is fixed above before any new score is computed.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): no change to any hypothesis or test. Heat exposure is an input to the firm exposure measures, so the corrected scores replace the old ones in the main analysis.
- Results to be reported both ways? Yes, for transparency: the main analysis uses A9; the number of sites and firms whose heat exposure changes from the old 0.5° bins is reported in `docs/phase3_hazards.md`.
- parameters.json hash after change: `67ef08d1bdf6790901f9400e7e6dbdd380fbbcb9d1005af9a115294ec084eb20` (SHA-256; previous hash after A8 was `587eb47d9db2c1c66d86b13d17e5f2939913c1f1473174e3fad009e3725051a0`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A10: heat (main) from ERA5, under the OD-7 condition; supersedes A9
- Date: 2026-11-12 (logged before any ERA5 data was requested or any ERA5 heat score was computed).
- Decided by: the project owner (decision of 2026-11-12). The dataset choice, time zone and cell rule below are the analyst's implementation of that decision, fixed here before any request.
- Section(s) of design.md affected: e3 (heat: dataset) and OD-7. design.md itself is not edited. OD-7 says ERA5 "is revisited only if several sites share one NASA POWER grid cell and need separating, which would require an amendment". This is that amendment.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `hazards.heat.era5_main` (none -> the rule below); `hazards.heat.era5` gains a `revisited` note pointing to A10 (its OD-7 value is kept as a record); `hazards.heat.grid_cell_assignment` (A9) gains `superseded_by` A10.
- **Trigger (pre-specified, not results).** The OD-7 condition is met: several main sites share one NASA POWER cell. Under the MERRA-2 native grid, 18 Lagos main sites fall in a single cell (`docs/nasa_manual_download_v2.md`), so NASA POWER cannot separate them.
- **Rule.**
  - **Data:** ERA5 post-processed daily statistics on single levels (Copernicus Climate Data Store dataset `derived-era5-single-levels-daily-statistics`, DOI 10.24381/cds.4991cf48, licence CC-BY-4.0). product_type `reanalysis`; variable `2m_temperature`; daily_statistic `daily_maximum`; frequency `1_hourly`; years 1991–2025, all days; area N 14°, W 2.5°, S 4°, E 15° (a box around Nigeria); the CDS default regular 0.25° latitude-longitude grid. This is the most efficient CDS route to a daily maximum: one small file per year, against about 24 times the volume for the hourly dataset.
  - **Day boundary:** time_zone `utc+01:00`, i.e. West Africa Time (Nigeria's civil time, no daylight saving), so each "day" is a local calendar day.
  - **Daily maximum definition:** the maximum of the 24 hourly 2 m temperature values in the local day, as computed by the CDS. It is not ERA5's separate "maximum temperature at 2 m since previous post-processing" field, so it can be slightly lower than the true daily peak. The metric uses exceedances of the cell's own percentile, so a consistent offset largely cancels.
  - **Cell of a site:** the 0.25° grid point nearest to the site, i.e. the cell centred on that point ± 0.125°. A site exactly on a cell edge goes to the cell to its north or east. Every main, office and R2 point site with a coordinate gets a cell, and all cells are inside the box, so all sites are scored.
  - **Metric (unchanged, e3 and OD-5):** for each cell, the 90th percentile of all daily maxima 1991–2020, pooled; score = mean annual exceedance days 2020–2025 minus the mean for 1991–2020; exposed = score ≥ the 2/3 quantile of main-set site scores. OD-6 is unchanged.
  - **Robustness:** the NASA POWER heat scores already computed (0.5° bins; owner manual download, identical to the API files) are kept and reported side by side, with the number of sites and firms whose heat exposure differs.
- **Supersedes A9.** A9 was logged but never applied; no A9 file was downloaded or scored. The NASA v2 download list is not needed. Any NASA v2 files the owner started downloading are ignored.
- Reason: owner decision under OD-7, the condition the frozen design set for revisiting ERA5.
- Outcome data seen before this decision? **Yes, NASA POWER heat exposure results had been seen.** Heat scores from the 0.5° bins (first from the API files, then identical from the owner's manual downloads), the 16.06 days/yr tercile cut-off, the site and firm heat exposure, and the combined index had been computed and reported in `docs/phase3_hazards.md`. These are exposure data, not disclosure outcomes: no ClimateBERT label, dictionary count, disclosure measure or regression had been computed. The switch follows the pre-specified OD-7 condition and was not chosen on those results. No ERA5 value had been seen.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): no change to any hypothesis or test. Heat exposure is an input to the firm exposure measures, and ERA5 replaces NASA POWER as its main source.
- Results to be reported both ways? Yes: ERA5 (main) and NASA POWER (robustness), side by side in `docs/phase3_hazards.md`.
- parameters.json hash after change: `a62ebd9f7d4df82ab4eb5b4b7852293996ddf94e5b0dd5153c579df264fdfbcb` (SHA-256; previous hash after A9 was `67ef08d1bdf6790901f9400e7e6dbdd380fbbcb9d1005af9a115294ec084eb20`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A11: ERA5 heat source switched to the hourly point time series (speed); method unchanged
- Date: 2026-11-17 (logged before `config/parameters.json` or any code is changed, and before any time-series data is requested).
- Decided by: the project owner (decision of 2026-11-17). The request details below are the analyst's implementation of that decision.
- Section(s) of design.md affected: e3 (heat: data access only). design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): `hazards.heat.era5_main.value` (CDS `derived-era5-single-levels-daily-statistics`, one Nigeria-box file per year -> CDS `reanalysis-era5-single-levels-timeseries`, one hourly series per 0.25° grid point, daily maximum computed locally); new key `hazards.heat.era5_main.source_A11` recording the change.
- **Rule.**
  - **Data:** ERA5 hourly time-series data on single levels (Copernicus Climate Data Store dataset `reanalysis-era5-single-levels-timeseries`, licence CC-BY-4.0). Variable `2m_temperature`; dates 1991-01-01 to 2025-12-31 (UTC); one request per grid point, at the exact coordinates of the ERA5 0.25° grid point that is the site's cell under the A10 cell rule. Same CDS account and key file (`~/.cdsapirc`, read only by `cdsapi`).
  - **Points:** the unique 0.25° grid points (A10 cell rule: nearest point, exact edges north/east) of the 125 point sites in `data/processed/site_hazards.csv` (main, office and R2).
  - **Daily maximum:** timestamps are shifted from UTC to UTC+01:00 (West Africa Time); the daily maximum is the maximum of the hourly 2 m temperature values in each local calendar day. This matches the A10 definition (maximum of the 24 hourly values in the local day). Because the request starts at 1991-01-01 00:00 UTC, the local day 1991-01-01 has 23 hourly values (01:00–23:00 WAT); this one day is kept.
  - **Unchanged (A10, e3, OD-5, OD-6):** cell rule, 90th percentile of all daily maxima 1991–2020 pooled, score = mean annual exceedance days 2020–2025 minus mean 1991–2020, exposed = top tercile of main-set site scores, NASA POWER robustness.
  - **Validation gate (fixed before any request):** one point is downloaded first. Its daily maxima for 1991 and 2025 are compared with the same cell in the two A10 daily-statistics files already downloaded (`data/raw/hazards/era5/era5_t2m_dailymax_utc+01_1991.nc` and `_2025.nc`). If the maximum absolute difference is above 0.5 °C, the switch stops and the owner is told; otherwise the remaining points are downloaded one request at a time.
- Reason: speed. The daily-statistics route needs 35 yearly jobs in the CDS queue; the queue rejected parallel jobs on 2026-11-12 (`data/interim/fetch_log.csv`) and only 1991 and 2025 were obtained. The time-series dataset serves a whole 35-year point series in one request.
- Outcome data seen before this decision? Heat exposure from NASA POWER had been seen (see A9, A10). From ERA5, only the 1991 and 2025 daily-statistics files had been downloaded and read for format checks; no ERA5 heat score, percentile or exposure had been computed. No disclosure outcome had been computed.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none. Data access change only; the heat metric is unchanged.
- Results to be reported both ways? No: the two routes deliver the same quantity (subject to the validation gate). The gate result is recorded in `docs/data_sources.md`.
- parameters.json hash after change: `255e924607910fbb22f9f1206f24c6f545f10119125fee53b91c2d969857bfc2` (SHA-256; previous hash after A10 was `a62ebd9f7d4df82ab4eb5b4b7852293996ddf94e5b0dd5153c579df264fdfbcb`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A12: OCR also triggered by run-together text (no spaces between words); applied to LIVESTOCK FY2025
- Date: 2026-11-17 (logged before the file is OCR'd or any text or paragraph is rebuilt).
- Decided by: the project owner (instruction of 2026-11-17); the trigger rule below is the analyst's implementation.
- Section(s) of design.md affected: f2 (text extraction and OCR). design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `text.ocr_trigger_run_together` (none -> the rule below).
- **Rule.** In addition to the A1/A2 triggers, a report is OCR'd if more than 1% of the whitespace tokens of its segmented text (Phase 4 step 1, duplicates excluded) are "run-together" tokens: 25 or more characters with no space, at least 85% letters, not a URL or e-mail address. The OCR tools and settings are the same as for every earlier OCR copy: OCRmyPDF 16.13.0, Tesseract 5.4.0 (eng), Ghostscript 10.08.0, `--force-ocr -l eng --oversample 300 --jobs 4 --output-type pdf`, via `src/phase2_ocr.py`. The original is kept unchanged (SHA-256 checked before and after). Pages are then chosen between the original and the OCR copy by the A3–A5 page-level rule, unchanged.
- **Applies to:** LIVESTOCK FY2025 (`data/raw/manual/livestock/2025_AR.pdf`), whose text layer has no spaces between words: 2.9% of tokens are run-together. No other document exceeds 0.05%.
- Reason: the A1 (document) and A2 (page) readability triggers did not catch this defect, and the file yields only 61 model-eligible paragraphs from 132 pages, so the firm's narrative would be undercounted.
- Outcome data seen before this decision? No disclosure outcome had been computed: no ClimateBERT label, no dictionary count, no Y measure. The trigger uses only text-layer statistics. Hazard exposure results had been seen (see A9–A11).
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none. This is a text-extraction correction for one document.
- Results to be reported both ways? No. The before/after paragraph counts are reported in `docs/phase4_corpus.md`.
- parameters.json hash after change: recorded under A14 (A12–A14 were applied to `config/parameters.json` in one edit).

### A13: rule-based repair of ligature glyphs in text extraction
- Date: 2026-11-17 (logged before the repair is applied and before `paragraphs.csv` is rebuilt; no climate term has been counted at any point).
- Decided by: the project owner (instruction of 2026-11-17); the rule below is the analyst's implementation.
- Section(s) of design.md affected: f2. f2 says NFKC normalisation fixes ligatures. That holds for the Unicode ligature characters (U+FB00–FB06), but not for two other forms found in Phase 4 step 1. design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `text.ligature_repair` (none -> the rule below).
- **Findings that motivate the rule** (Phase 4 step 1; text-layer inspection only):
  - **Private-use code points.** U+F001 ("fi") and U+F002 ("fl") occur only between letters (e.g. "pro_t", "_nancial", "cash _ows"), in Academy Press FY2025 and LIVESTOCK FY2025. The other private-use code points in the corpus (for example U+F0FC, U+F0B7, U+F0A7 and U+F053 in Airtel, MTN and Dangote) are standalone bullets and check marks, not ligatures. **This corrects `docs/phase4_corpus.md` step 1, which counted all private-use code points as possible ligatures.**
  - **Dropped glyphs.** A few original text layers drop the ligature or replace it with a space, e.g. "e ective" for "effective" (Guinness FY2025) and "nancial" (Okomu FY2022).
- **Rule** (applied to each text block after NFKC, before segmentation):
  1. **Code points:** U+F001 -> "fi" and U+F002 -> "fl" (the Adobe/Apple private-use ligature convention). No other private-use code point is changed.
  2. **Dropped glyphs, original text-layer pages only** (OCR pages are not touched, because Tesseract outputs letters, and on OCR pages the test proposes false repairs of OCR noise). The word list is `wordfreq` 3.1.1 English (the A1 package), via `zipf_frequency`.
     - **(a) Single token:** a token of 3 or more letters with Zipf frequency < 1.5 is replaced by T[:k] + L + T[k:], where L ∈ {ffi, ffl, ff, fi, fl}, if exactly one distinct such string has Zipf ≥ 3.0.
     - **(b) Split token:** "A B", where A is 1–6 letters, B is 2 or more lower-case letters and B has Zipf < 1.5, is replaced by A + L + B if exactly one L gives Zipf ≥ 3.0.
     - Matching ignores case; the repaired word keeps the case of its first letter.
  3. Every repair is logged (document, page, before, after) to `data/interim/ligature_repairs.csv` for review.
- **Check (outcome-blind):** before/after counts of common non-climate words ("financial", "profit", "office", "benefit", "significant", "effective", "efficient", "affected", "flows", "inflation") in Airtel, MTN, Academy, Dangote and Guinness FY2025. No climate or hazard term is counted.
- Reason: unrepaired, these glyphs split or truncate words, which can hide words from the f4 hazard dictionary and f5 site names.
- Outcome data seen before this decision? No disclosure outcome had been computed and no climate term had been counted. Hazard exposure results had been seen (see A9–A11).
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none. This is a text-extraction correction.
- Results to be reported both ways? No. The number of repairs per document is reported.
- parameters.json hash after change: recorded under A14.

### A14: section tagging (f1) by a documented rule with analyst review, replacing hand tagging
- Date: 2026-11-17 (logged before any document is tagged).
- Decided by: the project owner (instruction of 2026-11-17: "do it yourself (I will not hand-tag)"); the rule below is the analyst's implementation.
- Section(s) of design.md affected: f1 ("Section boundaries are tagged by hand in a small table per document, recording start and end pages"). design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): `text.exclude_sections` gains `tagging` (none -> the rule below).
- **Rule.**
  - **Section excluded from model scoring:** the audited financial statements and notes, including the independent auditor's report, as one page range per document. Paragraphs in the range stay in `paragraphs.csv` with `section = financial_statements`, so notes that name sites remain available for the site-mention measure (f1).
  - **Evidence headings**, matched case-insensitively at the start of a heading-like block (20 words or fewer) among the first 6 blocks of a page:
    - (A) auditor's report: "independent auditor's/auditors' report", "report of the independent auditor(s)";
    - (S) primary statements: "statement(s) of financial position / profit or loss / comprehensive income / changes in equity / cash flows", "balance sheet", "income statement", "cash flow statement", optionally preceded by "consolidated (and separate)" or "separate";
    - (N) notes: "notes to the (consolidated (and separate)) financial statements".
  - **Contents pages are ignored:** a page with a "contents" heading, or with 4 or more evidence headings, or where the heading ends in a page number.
  - **Start** = the first page with A or S evidence. **Last evidence** = the last page with A, S or N evidence.
  - **End** = the page before the first later page headed by a post-statement section ("other national disclosures", "value added statement", "five-year (financial) summary", "shareholder information", "proxy form", "notice of annual general meeting", "e-dividend", "unclaimed dividend"); otherwise the last page of the document.
  - **Flags (analyst review):**
    - no A or S evidence in an annual, integrated or FS document;
    - the range covers under 15% of an AR/IAR's pages;
    - more than 10 pages between the last evidence and the end;
    - a narrative heading inside the range ("chairman's statement", "report of the directors", "directors' report", "sustainability report", "corporate governance").

    Flagged documents are reviewed by the analyst from their page headings. The boundaries may be set by hand, recording the page and heading used as evidence, with `method = analyst review`.
  - **Sustainability reports and extracts** (SR, SRX) are expected to have no financial-statement section. If no evidence is found, they are recorded as "none" and not flagged.
- Output: `data/interim/section_tags.csv`, one row per document with the start and end pages, evidence (page and heading text) for each boundary, method, and flag with reason.
- Reason: owner instruction. The rule makes the f1 boundaries reproducible.
- Outcome data seen before this decision? No disclosure outcome had been computed and no climate term had been counted. The boundaries depend only on financial-statement headings. Hazard exposure results had been seen (see A9–A11).
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none on the tests themselves. The rule defines which paragraphs are scored for Y1–Y4.
- Results to be reported both ways? No. The flagged documents and the analyst's decisions are listed in `docs/phase4_corpus.md`.
- parameters.json hash after change: `c779f45abc2555df0a4a0b39e1ef4c606fbba8520d184b363fc690939fb53143` (SHA-256; previous hash after A11 was `255e924607910fbb22f9f1206f24c6f545f10119125fee53b91c2d969857bfc2`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A15: control characters in text layers are read as spaces (f2)
- Date: 2026-11-17 (logged before the change is applied and before `paragraphs.csv` is rebuilt; no climate term has been counted).
- Decided by: the analyst, within the owner's instruction of 2026-11-17 to repair LIVESTOCK FY2025's text and the f2 extraction. Flagged to the owner in `docs/phase4_corpus.md`.
- **Confirmed by the project owner on 2026-11-17** (after it was applied and reported).
- Section(s) of design.md affected: f2. design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `text.control_characters` (none -> the rule below).
- **Finding.** After A12, LIVESTOCK FY2025 still had 1.3% run-together tokens, and only 106 eligible paragraphs. The A3–A5 rule kept the original text on 83 of 132 pages, because the original and OCR common-word shares are almost equal (e.g. p22: 0.589 against 0.584). The cause is not missing spaces: the file's font maps the space glyph to the control character U+0003 (about 19,500 occurrences). `wordfreq` treats U+0003 as a separator, so A1–A5 saw normal words, but whitespace splitting and the segmentation word counts did not. The A12 OCR copy was therefore not strictly needed. It is kept, and the A3–A5 page choice for LIVESTOCK is unchanged. Other control characters occur in 17 documents, about 2,100 in all (U+0007, U+0001, U+0008, U+0011 and others).
- **Rule.** In extracted text, every C0 control character other than tab, line feed and carriage return (U+0000–U+0008, U+000B, U+000C, U+000E–U+001F), and U+007F, is replaced by a space before NFKC and whitespace normalisation. A control character is never valid text content.
- Reason: technical correction of text extraction.
- Outcome data seen before this decision? No disclosure outcome had been computed and no climate term had been counted. Hazard exposure results had been seen (see A9–A11).
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none. This is a text-extraction correction.
- Results to be reported both ways? No. LIVESTOCK's eligible-paragraph counts before A12, after A12 and after A15 are reported in `docs/phase4_corpus.md`.
- parameters.json hash after change: `cac7518c6836dc5b8c396cc760a639d24134c5fb1b58784a0f22de9592f3e34c` (SHA-256; previous hash after A12–A14 was `c779f45abc2555df0a4a0b39e1ef4c606fbba8520d184b363fc690939fb53143`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### Owner decisions of 2026-11-17 (no amendment)
- **H3 sample: the design as written** (Option A in `docs/phase4_corpus.md`, section 5.1). H3 is estimated on all main-census firms, and a firm contributes to τ only if it has documents for at least two fiscal years, which follows from the firm fixed effects in section h. design.md and `config/parameters.json` are not changed. The proposed amendment restricting H3 to the exposure-scored firms (Option B) was **not adopted**, and no amendment is logged for it.
- **Collection order:** the owner collects the 23 tier-1 firms first (exposure-scored firms with one year only), then the 28 tier-2 firms. For each, the target is one additional annual report, FY2020 first, then FY2021, then FY2022 (`data/interim/phase4_minimum_download_list.csv`). This is a collection plan, not an analysis rule.
- **A15 confirmed** (see A15).

### A16: H3 main sample counts only firm-years ending on or after the NGX listing date
- Date: 2026-11-17 (logged before any new tier-1 file is processed and before any H3 sample is formed).
- Decided by: the project owner (decision of 2026-11-17). The owner confirmed the listing dates for Transcorp Power (4 March 2024) and Aradel (14 October 2024), citing nairametrics.com of 2024-03-04 and 2024-10-14.
- Section(s) of design.md affected: h (H3 data), and a (RQ: "NGX-listed firms"). design.md is not edited. The design did not say whether pre-listing firm-years count.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `analysis.h3_listing_rule` (none -> the rule below, with the listing dates).
- **Rule.** For H3, a firm-year counts in the **main** analysis only if the fiscal year ends on or after the firm's NGX listing date. Pre-listing firm-years stay in the corpus and are used in a **robustness** check only (H3 re-estimated with them included).
- **Scope:** H3 only. H1/H2 are not changed by this amendment; the owner's decision was stated for H3. Whether the same rule should apply to the H1/H2 panel is left for the owner.
- **Listing dates checked for main-census firms listed after the start of 2020** (web search, 2026-11-17; secondary sources unless stated):

  | Firm | NGX listing | Effect on documents held or filed |
  |---|---|---|
  | TRANSPOWER | 4 March 2024 (owner) | FY2020 (year ended 31 Dec 2020) is pre-listing: robustness only. FY2024 and FY2025 count |
  | ARADEL | 14 October 2024 (owner) | FY2021 (as NDEP Plc) is pre-listing: robustness only. FY2024 and FY2025 count |
  | BUAFOODS | 5 January 2022 (listing by introduction; NGX announcement, nairametrics.com 2022-01-05) | FY2022 (31 Dec 2022) and FY2024 count. Any FY2020/FY2021 file would be pre-listing |
  | GEREGU | 5 October 2022 (listing by introduction; nairametrics.com 2022-10-05) | FY2022 (31 Dec 2022) and FY2024 count |
  | MECURE | 7–8 November 2023 (Growth Board, by introduction; nairametrics.com 2023-11-08/09; company press release dated 8 November 2023) | FY2025 counts. A tier-2 download for FY2020–2022 would be pre-listing: robustness only |

  - **Ellah Lakes** is reported as listed since May 2000 (simplywall.st). Its October 2021 "begin trading" report is not a first listing.
  - **All other main-census firms** are taken as listed before 2020. This was not individually verified from a primary source; it is the analyst's understanding of long-standing NGX listings.
  - **Sources disagree on two dates:** Mecure (7 or 8 November 2023) and one report placing Aradel's listing in 2025. Neither changes any firm-year's status: Mecure has no FY ending between 7 and 8 November, and the owner's date is used for Aradel.
- Reason: owner decision. The RQ concerns NGX-listed firms, so disclosure before listing is not disclosure by a listed issuer.
- Outcome data seen before this decision? No disclosure outcome had been computed: no ClimateBERT label, no dictionary count, no Y measure. Hazard exposure results had been seen (see A9–A11).
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): H3 (estimation sample).
- Results to be reported both ways? Yes: H3 main (post-listing firm-years only) and H3 robustness (including pre-listing firm-years).
- parameters.json hash after change: `583c0e272f51b011399566adfba2bfb64b9e455aa1aab2c7554284f06f27edcf` (SHA-256; previous hash after A15 was `cac7518c6836dc5b8c396cc760a639d24134c5fb1b58784a0f22de9592f3e34c`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A17: dictionary implementation (f4 matching rule; f5 source file, facility context and ambiguity rule)
- Date: 2026-11-17. Logged before either dictionary file was frozen and before any dictionary was applied to the corpus.
- Decided by: the analyst, under the owner's instruction of 2026-11-17 to build and freeze both dictionaries ("flag ambiguous names and propose a rule"). **The ambiguity rule (R2) is the analyst's proposal; the owner may change it by amendment before any count.**
- Section(s) of design.md affected: f4 (hazard dictionary) and f5 (site-mention dictionary). design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value):
  - `text.physical_risk_dictionary`: the 16 terms are **unchanged**. New keys `file`, `matching`, `matching_id`, `matching_decided_on`.
  - `text.site_dictionary.value`: "built from data/interim/facility_locatability.csv; frozen before outcomes" -> `config/dictionary_sites.json`, built from `data/processed/facilities.csv`. Status proposed -> decided; new key `rule`.
- **What the design left open, and how it is filled:**
  - **f4 matching.** The design gives the terms but not how they match. Rule: case-insensitive whole words; regular plural -s/-es for count nouns only (floods, storms, droughts, heatwaves, wildfires, inundations, rainfalls, extreme temperatures, sea levels); a space in a term also matches a hyphen (sea-level, water-stress); "heatwave" also matches "heat wave".
    - **No other inflection is matched:** "flooded", "floodplain", "water-stressed", "heated", "eroded" are not.
    - This keeps the design's list literal. Validation item (iii) will show whether such forms are missed, and adding any form needs a further amendment.
    - **Bare "heat" is kept (OD-11).** The Phase 0 test document already contains one likely false positive ("Waste Heat Recovery"), which is coding-guide example 3-B. The OD-11 drop decision is taken only from the validation results.
  - **f5 source file.** f5 names `data/interim/facility_locatability.csv`, the Phase 0 file (94 rows, pilot firms only). Phase 2 replaced it with `data/processed/facilities.csv`: 214 sites of 59 tickers, with census stratum, rating, asset type and coordinates. The dictionary is built from the Phase 2 file.
  - **f5 terms.** Per site, the analyst curated the town, district or estate names, the facility's own proper name, and oil-licence names, from the `facility`, `location_as_written` and `geocode_place` columns.
    - **Excluded:** generic descriptions ("Head office", "Depots"); street names and P.O. boxes; the firm's own name (e.g. "Geregu").
    - **Spelling variants:** hyphen or space, Otta/Ota, Shagamu/Sagamu. They come from the facility records and common usage; no corpus text was searched for them.
    - **Result:** 173 of the 214 sites have at least one term (165 distinct terms). The other 41 sites have no proper name in the data (mostly dispersed assets and generic "factory" records), so the dictionary cannot name them (Y5 = 0 by construction).
  - **f5 "facility context"** (not defined in the design): a list of facility words (plant, factory, mill, brewery, refinery, depot, terminal, warehouse, estate, plantation, farm, quarry, mine, field, station, office, headquarters, operations, project, …) given in the file.
  - **Ambiguity flags**, computed by rule for each term:
    - shared by two or more firms (e.g. Ikeja, 8 firms; Ikoyi and Victoria Island, 7 each; Apapa and Oregun, 5 each);
    - a state, state capital or major city or district (e.g. Abuja, Kano, Port Harcourt, Benin City);
    - a common English word (single words with wordfreq zipf ≥ 3.0: Aba, Abuja, Cowan, Jos, Kano, Marina);
    - another sense (an analyst list, e.g. Adani, ATO, Kwale, Yoho).
    - **Collision with the firm's own name:** Okomu (Okomu Oil Palm Company) and Ashaka (Ashaka Cement). The firm-name phrases are deleted before matching.
    - In all, 52 of the 165 terms carry a flag.
  - **Matching rules:**
    - **R1** (unflagged place term): the term and a facility-context word anywhere in the same paragraph, as f5 states.
    - **R2** (flagged place term, proposed): a case-sensitive match, with a facility-context word in the **same sentence**.
    - **R3** (a facility's proper name or licence, e.g. "MTN Plaza", "Qua Iboe", "OML 40"): counts on its own, case-sensitive. A flagged facility name also needs a context word in the same sentence (R3+R2).
  - **Known limits:**
    - Office sites will usually be named in the corporate-information pages, so their Y5 is 1 almost by construction.
    - One term that belongs to several sites of one firm names them all; for example, NB's "Aba" covers a brewery, a malting plant and a sales office.
    - OML lists written as "OMLs 4, 38 and 41" match only the first number.
- **Files:** `config/dictionary_hazard.json` and `config/dictionary_sites.json`, written by `src/phase4_dictionaries.py`. The builder is deterministic: two runs give identical files.
- Reason: the design fixes the term list (f4) and the principle (f5), but the dictionaries cannot be applied without a matching rule, a current source file and a definition of facility context. These are fixed now, before any count, so that they cannot be tuned to results.
- Outcome data seen before this decision? No. No dictionary had been applied to the corpus and nothing had been counted. The only text read was the Phase 0 test document (Dangote Cement 2025 sustainability extract), used for the coding-guide examples. No ClimateBERT label exists.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): H1–H3 through Y3 (hazard tag) and H3 through Y4 (site mentions); H4 through Y5.
- Results to be reported both ways? No. R2 is the main rule. A sensitivity check with R2 replaced by R1 (paragraph-level context for every place term) will be reported, as an exploratory check of the rule's effect.
- parameters.json hash after A17 and A18 (one edit): `78faf3de252c635a5e5a5cc30bc990d4d7e7442231b3d892e64dde794b2f7694` (SHA-256; previous hash after A16 was `583c0e272f51b011399566adfba2bfb64b9e455aa1aab2c7554284f06f27edcf`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

### A18: validation coder is one external coder, not the project owner (g)
- **Status (2026-11-17): superseded by A20; not used.** Kept as a record.
- Date: 2026-11-17. Logged **before** the validation sample is drawn and before any coding.
- Decided by: the project owner (instruction of 2026-11-17: "ONE external coder codes the sample twice, at least 7 days apart").
- Section(s) of design.md affected: g ("Coder: the project owner"; "the owner re-codes the same 200 paragraphs"; "The reference coding is the owner's first pass"). design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `validation.coder` (implicitly "the project owner" -> one external coder), and new key `validation.codebook` (`docs/coding_guide.md`).
- **Rule.** One external coder, not the owner, codes every sampled paragraph twice:
  - **Order:** the second pass uses a new random order, at least 7 days after the first (`validation.recode_min_days` = 7, unchanged).
  - **Blind:** the coder sees no model output and no dictionary tag.
  - **Reference coding:** the external coder's first pass, with disagreements resolved in that coder's second pass (as g, with the coder substituted).
  - **Unchanged:** the metrics (Krippendorff's alpha intra-coder; Cohen's kappa and F1 model against human), the thresholds (OD-12) and the fallback.
  - **Identity:** the owner records the coder's identity and dates; they are not stored in the repository.
- Reason: owner decision. An external coder is independent of the project owner, who knows the hypotheses.
- Outcome data seen before this decision? No disclosure outcome has been computed: no ClimateBERT label, no dictionary count, no Y measure.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none directly. It changes who produces the reference labels used to validate the classifiers behind Y1–Y3 and the dictionaries.
- Results to be reported both ways? No.
- parameters.json hash after change: as A17 (one edit).

### Freeze of the dictionaries and the codebook (2026-11-17, before any count or coding)

| File | SHA-256 | Size (bytes) |
|---|---|---|
| `config/dictionary_hazard.json` | `d7a73fc0115c531876fb2e8fbded4b3e22b850912c11a93e37c5d63d71b882e9` | 4,636 |
| `config/dictionary_sites.json` | `0a182e5940cb8a1d9349ef1dad9c2d39c1903f2f0f9e446aca753cac3e63a8f8` | 186,667 |
| `docs/coding_guide.md` | `4935305284b4a9e916ddbc3d6ea7ff394fdff7c0f85a185b61d0442edd93a2f7` | 21,940 |
| `src/phase4_dictionaries.py` (builder) | `533bb21a56e388bdceea32c497d561b7c1e32e03e0abb911f8da892a1b90d29f` | |
| `config/parameters.json` | `78faf3de252c635a5e5a5cc30bc990d4d7e7442231b3d892e64dde794b2f7694` | |

- **Hash method:** `sha256sum`, over the files exactly as saved.
- **State at the freeze:**
  - no dictionary has been applied to the corpus, and no term, site or paragraph has been counted;
  - no ClimateBERT model has been run on the corpus;
  - no Y measure exists;
  - the validation sample has not been drawn.
- **Changes after this point:** any change to these files needs an amendment, including the OD-11 decision on bare "heat", which is taken after validation.
- **parameters.json after A19** (logged below): `4a213f1b37ac4ac768a218c6b9c009f676faac29eff0e9907b16b9df127dd756`. The dictionary, codebook and builder hashes above are unchanged by A19.
- **Codebook:** `docs/coding_guide.md` is the codebook of design g. The design says it is "frozen with the design", but it had not been written by the design freeze of 2026-11-07. It is frozen here, before any coding. Its worked and practice examples come from the Phase 0 test document (Dangote Cement 2025 sustainability extract), as g specifies, and that document is excluded from the sampling frame.

### A19: validation sample frame, cell allocation and caps (g)
- **Status (2026-11-17): superseded by A20; not used.** Kept as a record.
- Date: 2026-11-17. Logged before any model was run on the corpus and before the sample was drawn.
- Decided by: the project owner chose, on 2026-11-17, to stratify as the design specifies, running the detector and specificity models only to form the strata. The frame, allocation and order of drawing below are the analyst's, because the design does not give them.
- Section(s) of design.md affected: g (sample). design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `validation.sampling` (none -> the rule below). The existing `validation.n_paragraphs` (200), `max_per_firm` (10), `fs_only_cap_share` (0.10) and `random_seed` (20261107) are unchanged and used as they stand.
- **Rule.**
  - **Frame:** every model-eligible narrative paragraph (≥ 40 words, not a duplicate, outside the A14 financial-statement range) of the main-census firms.
    - The robustness-stratum firms are left out; they are analysed separately (h, robustness check 9).
    - The Phase 0 test document (DANGCEM_2025_SRX) is left out, because the coding guide's examples come from it.
    - Pre-listing documents (A16) stay in the frame, since validation concerns the classifiers rather than H3.
  - **Strata (as g):** detector prediction at the OD-10 threshold (P(yes) ≥ 0.5). For climate paragraphs, the specificity prediction (P(spec) ≥ 0.5) gives three prediction classes, crossed with the hazard-dictionary tag (frozen `config/dictionary_hazard.json`), for six cells.
  - **Allocation:** equal, 34/33/33/33/34/33. Equal allocation is used so that each classifier and the dictionary are tested on enough positive and negative cases.
    - **Shortfall:** a cell with too few paragraphs is filled from the other cell of the same prediction class, then from any cell.
  - **Caps (g):** at most 10 paragraphs per firm and at most 20 (10%) from FS-type documents. They are enforced while drawing: each cell's frame is put in a seeded random order, and the cells take turns to add their next paragraph that does not break a cap.
  - **Seed:** `validation.random_seed` = 20261107, with numpy `default_rng`. The pass-2 order uses seed + 1.
  - **Predictions** are written only to `data/interim/validation_strata.csv`, with the model revisions:
    - the coder never sees them, and `validation_sample.csv` holds only id, firm, year and text;
    - they are used only to form strata and, after coding, for the model-against-human metrics;
    - no corpus-level share or outcome is computed or reported from them.
  - **Weights:** each sampled paragraph carries its cell's inclusion weight (frame cell size ÷ sampled cell size), so that the metrics can also be reported for the frame as a whole.
- Reason: g specifies the stratifying variables but not the frame, allocation or order of drawing. They are fixed before any prediction exists.
- Outcome data seen before this decision? No. No model prediction, dictionary count or Y measure existed when this was logged.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none directly (validation of the Y1–Y3 classifiers and the hazard dictionary).
- Results to be reported both ways? The model-against-human metrics will be reported unweighted (sample) and weighted to the frame.
- parameters.json hash after change: `4a213f1b37ac4ac768a218c6b9c009f676faac29eff0e9907b16b9df127dd756` (SHA-256; previous hash after A17–A18 was `78faf3de252c635a5e5a5cc30bc990d4d7e7442231b3d892e64dde794b2f7694`). design.md is unchanged: `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714`.

**A19 draw record (2026-11-17).**
- **Models:** the detector and specificity models were run on the 15,293 frame paragraphs only, at revisions `2c3bc660d45a59e31b35f5d3e365ee4f59fdf76c` (detector) and `4ada96ed4bf5c3a7a711282e41f1ab9b29f0ddea` (specificity). Scores are in `data/interim/validation_predictions.csv`. No corpus-level share was computed or reported.
- **Sample:** 200 paragraphs, 37 firms, at most 10 per firm, 19 from FS-type documents.
- **By cell:**

  | Cell | Paragraphs |
  |---|---|
  | Not climate, untagged | 50 |
  | Not climate, tagged | 17 |
  | Climate specific, untagged | 52 |
  | Climate specific, tagged | 14 |
  | Climate non-specific, untagged | 48 |
  | Climate non-specific, tagged | 19 |

- **Why the tagged cells are short:**
  - The not-climate tagged cell has fewer paragraphs in the frame than its target.
  - The two climate tagged cells were cut by the per-firm cap: their paragraphs are concentrated in a few firms.
  - Their shortfall went to the sibling untagged cells, as A19 specifies.
- **Superseded first draw:** an earlier draw that day used a fallback that sent shortfalls to the first cell, not to the sibling cell. It was discarded before anyone saw or coded it, and the code was corrected.
- **Files (SHA-256):**
  - `data/interim/validation_sample.csv` (coder, pass 1): `f49aa45b3ab8767e105855b13b2bb7a41b590892be19d64dcd4b213186733106`
  - `data/interim/validation_sample_pass2.csv`: `b10d455485b95bb34ab514acf90c23a13a33f94e223d6554782bfbb4e54d9201`
  - `data/interim/validation_strata.csv` (not for the coder): `c5389a44345c7c58e22d79dc9c73a8bb0cecbf34cd224da23b5b4d8eab60bb0c`
  - `src/phase4_validation_sample.py`: `b48e0a5a4e9160af69b93b4513c961b312519617c2b11a6fdc9a7a89044213a3`

### A20: human validation dropped; dictionary measures become the main outcomes; OD-11 decided by rule; dictionary precision check
- Date: 2026-11-17. **Logged before any count, measure or corpus scoring**, before the hazard dictionary was rebuilt and before the precision sample was drawn.
- Decided by: the project owner, in two decisions on 2026-11-17: "drop human validation", and confirmation of the mapping and the precision check below. The analyst proposed the mapping and the OD-11 rule; the owner confirmed both.
- Section(s) of design.md affected: f4 (OD-11), f6 (outcomes), g (validation), h (H1–H3 outcomes). The body of design.md is not edited; a status note pointing here is added at the top of the file (new hash below).
- **Status of earlier steps:**
  - A18 (external coder) and A19 (validation sample) are **superseded and not used**.
  - The following are kept as records only, **not used**:
    - `docs/coding_guide.md`;
    - `data/interim/validation_sample.csv`, `validation_sample_pass2.csv` and `validation_strata.csv`;
    - `data/interim/validation_predictions.csv`.
  - **No codes:** the validation sample was never coded, by a person or by AI. AI-generated codes are not used as validation, and none are saved in the project.

**1. Main outcomes (dictionary only, no climate filter).** Per firm-year, over scored narrative paragraphs: model-eligible (at least 40 words, not a duplicate) and outside the A14 financial-statement range.

| ID | Measure | Definition |
|---|---|---|
| Y3d | Hazard share | hazard-tagged paragraphs ÷ all scored paragraphs |
| Y4d | Site-named hazard mentions | count of hazard-tagged paragraphs that name at least one of the firm's sites (`config/dictionary_sites.json`, rules R1–R3), and a binary for any |
| Y4s | Site specificity of physical-risk disclosure | Y4d ÷ hazard-tagged paragraphs; missing if there are none |
| Y4r | Site-named hazard rate | Y4d ÷ all scored paragraphs |
| Y5 | Site ever named | unchanged (H4) |

"Hazard-tagged" means at least one term of the re-frozen `config/dictionary_hazard.json` (section 3 below). The design's Y3 and Y4 used the ClimateBERT detector as a filter ("physical-risk *climate* paragraphs"). The filter is removed, so that the main outcomes do not depend on an unvalidated classifier.

**2. Hypotheses re-operationalised.** The confirmatory family stays H1, H2 and H3, one primary outcome each, with Benjamini–Hochberg at q = 0.05 (OD-15).

| | Design | Now |
|---|---|---|
| H1 | Y2 ~ exposure | **Primary Y4s** ~ exposure (fractional logit; OLS as robustness). Secondary: Y3d and the Y4d binary |
| H2 | exposure vs institutional blocks for Y1–Y3 | **Primary Y3d**, secondary Y4s; the same three-block comparison |
| H3 | τ(Y1) > 0 and τ(Y1) > τ(Y4) | **τ(Y3d) > 0 and τ(Y3d) > τ(Y4r)**, standardised, with a bootstrap interval for the difference; A16 sample rules unchanged |
| H4 | Y5 | unchanged |

- **Changes in meaning:**
  - H1's "specificity" is now the site specificity of physical-risk disclosure.
  - H3's "climate language" is narrowed to physical-risk language, because no frozen dictionary measures climate language as a whole.
- **ClimateBERT outcomes** (Y1, Y2, TCFD category, sentiment) and the ClimateBERT version of H3 (τ(Y1) vs τ(Y4)) are **exploratory and unvalidated**. They are reported with a limitation note: "not validated against human coding; design g's validation was dropped by owner decision (A20)". The OD-10 thresholds stay at 0.5, and the g recalibration fallback cannot be used.

**3. OD-11 decided by a pre-set rule, without looking at any count.**
- **Rule:**
  - drop bare "heat";
  - add "extreme heat";
  - keep "heatwave" (also "heat wave") and "extreme temperature";
  - do not add "high temperature".
- **Why:**
  - The corpus is dominated by kiln, furnace, brewery, mill and power-plant operators, where "heat" mostly means process heat ("waste heat recovery", "heat exchanger", "heat treatment"). The Phase 0 test document already contains one such use ("Waste Heat Recovery").
  - With human validation dropped, the false-positive check that OD-11 relied on cannot be run, so the rule favours precision.
  - "Extreme heat" is added because it is the unambiguous hazard phrase that dropping bare "heat" would otherwise lose.
  - "High temperature" is mostly process language in cement and glass reports.
- **The new list has 16 terms:** the design's 16, minus "heat", plus "extreme heat". The matching rule of A17 is unchanged. The re-frozen hash is recorded below, after the rebuild.

**4. Dictionary precision check** (replaces design g's dictionary validation).
- **Sample:** 100 snippets of hazard-tagged paragraphs, drawn before any count. Seed `20261117`, numpy `default_rng`.
  - **Frame:** scored narrative paragraphs (as in section 1) of the main-census firms that match at least one term.
  - **Stratification by term family**, using the dictionary's hazard groups: flood; storm; drought / water stress; heat; coastal / erosion / sea level; wildfire. Allocation is equal, 17/17/17/17/16/16.
  - **Shortfall:** a family with fewer candidates gives its remaining places to the other families in turn.
  - **Caps:** at most 5 snippets per firm, and one snippet per paragraph.
  - **Drawing order:** within a family, paragraphs are taken in seeded random order, the families take turns, and one matched occurrence of a term from that family is chosen at random within the paragraph.
- **Snippet:** the sentence containing the match, plus one sentence before and one after (sentences split at . ! ? followed by a space). The matched word is marked with [[ ]].
- **File:** `data/interim/precision_sample.csv` (id, firm, year, term, snippet) in random order, with no other scores. id is the paragraph id plus the character offset of the match.
- **Checker:** one external person, not the analyst and not an AI, answers one question per snippet:
  > "Is the highlighted word used about a real weather/climate hazard (flood, drought, storm, heatwave, water stress, sea-level rise, erosion…)? yes/no"
- **Pre-set rule:**
  - **Report:** precision (share of "yes") overall and per term family, with exact (Clopper–Pearson) 95% intervals.
  - **If overall precision is below 0.80,** H1–H3 are reported as descriptive only.
  - **Terms with precision below 0.50 (n ≥ 5)** are listed as a limitation. The counts are not changed unless a later amendment says so.
  - Precision is measured on the unweighted stratified sample. The per-family estimates are the primary check.
- **Not measured:** recall (missed hazard mentions) and the site dictionary's accuracy. Both are stated as limitations.
- Reason: owner decision to drop human validation. The dictionary measures are frozen, transparent and do not depend on a classifier that can no longer be validated.
- Outcome data seen before this decision? No count, measure or corpus-level share has been computed. ClimateBERT detector and specificity probabilities exist for the A19 frame (strata only). No share or total was computed from them, and they are now not used.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): H1, H2 and H3 (primary outcomes changed).
- Results to be reported both ways? ClimateBERT-based versions are reported as exploratory only, not as a second confirmatory version.

**A20 re-freeze record (2026-11-17, before any count).**

| File | SHA-256 | Note |
|---|---|---|
| `config/dictionary_hazard.json` | `8d7456ab58e8d75392ea30b86f4f49fe1485de220298d1964a3b142148128574` | **re-frozen**: 16 terms ("heat" dropped, "extreme heat" added); replaces `d7a73fc0…82e9` |
| `config/dictionary_sites.json` | `0a182e5940cb8a1d9349ef1dad9c2d39c1903f2f0f9e446aca753cac3e63a8f8` | unchanged (A17) |
| `src/phase4_dictionaries.py` | `bccd29b5ccf32dc2c0dd7da4cfa715a2612a7978398be3cc0ec16511e0144dc1` | builder after the OD-11 change |
| `config/parameters.json` | `fd1f9fff10e0790c8d10e3ceff09f6ea001129a9adc8a93ba208bfbaa4e3e014` | A20 keys; previous `4a213f1b…d756` (A19) |
| `docs/design.md` | `ed4bf262f4fd46b294ea27c72b815bbe744795cb396562290661c78688b7a534` | status note added at the top; body unchanged; previous `f563379e…1714` |
| `docs/coding_guide.md` | `d988a94603cf0b291ddfa6f7b7fd6b39696f6c37c59f3b9856bb9ddacddce387` | "not used" notice added; previous `49353052…a2f7` |

**Precision sample: pending an owner decision.**
- The first draw under the A20 rule (seed 20261117) produced **46 snippets, not 100**:

  | Family | Snippets |
  |---|---|
  | Flood | 14 |
  | Storm | 8 |
  | Drought / water stress | 10 |
  | Heat | 3 |
  | Coastal / erosion / sea level | 11 |
  | Wildfire | 0 |

- 17 firms are represented, with at most 5 each.
- The drawing loop stops only when every family's candidates are used up under the caps (5 per firm, 1 per paragraph). So 46 is the most the frame can supply under these caps. Nothing was counted to establish this.
- The file `data/interim/precision_sample.csv` (46 rows, SHA-256 `8a1e951dcf3741fd40e06d9054ffb9b989bfc8e75c155337d9b64246cee5b39a`) has **not** been given to anyone.
- Whether to keep it, or to change the cap and redraw, is to be decided by the owner and logged before any count.
- **Owner decision (2026-11-17, before any count): keep the 46 snippets as drawn.** The A20 caps are unchanged; the shortfall from 100 is accepted.
  - The overall 95% interval will be wider than planned.
  - **Heat** (n = 3) and **wildfire** (n = 0) cannot be estimated, so they are listed as limitations: precision not checked.
  - The pre-set rule otherwise applies as written: overall precision below 0.80 means H1–H3 are descriptive only, and terms with precision below 0.50 (n ≥ 5) are listed as limitations.
  - `data/interim/precision_sample.csv` (SHA-256 `8a1e951dcf3741fd40e06d9054ffb9b989bfc8e75c155337d9b64246cee5b39a`) and `src/phase4_precision_sample.py` (SHA-256 `52b81cac266d33cab6ed0f09f48d4b1bdec6f79db220abeb9bb5023324ae847a`) are final.

### A21: precision-check results applied (H1–H3 descriptive only); exploratory refined dictionary; outcome computation plan
- Date: 2026-11-17. **Logged after the precision results and before any outcome measure was computed.**
- Decided by: the project owner (instruction of 2026-11-17). The precision rule was pre-set in A20; the refined dictionary is a post-hoc owner decision.
- Section(s) of design.md affected: f4, f6, h (status of H1–H3). design.md is not edited.

**1. Precision check (A20) results.**
- **Answers:** external helper C1, collected 2026-11-17 via the owner's coding page, in `data/interim/precision_answers_C1.csv` (46 rows; SHA-256 `301c6de77fd443595ad622ca9ca4620a1277bd64772ebc02e13c1a80020fed13`).
- **Checks:** the ids and terms match `precision_sample.csv` exactly; there is one coder (C1); the answers are yes or no only.
- **Code:** `src/phase4_precision_results.py`, writing `data/interim/precision_results.csv`.
- **Intervals:** A20 pre-specified exact (Clopper–Pearson) 95% intervals, and the owner also asked for Wilson intervals; both are reported. The rule uses the point estimate, so the choice of interval does not affect it.

| Group | Yes / n | Precision | Exact 95% CI | Wilson 95% CI |
|---|---|---|---|---|
| **Overall** | **30/46** | **0.65** | 0.50–0.79 | 0.51–0.77 |
| Flood | 13/14 | 0.93 | 0.66–1.00 | 0.69–0.99 |
| Storm | 1/8 | 0.13 | 0.00–0.53 | 0.02–0.47 |
| Drought / water stress | 9/10 | 0.90 | 0.56–1.00 | 0.60–0.98 |
| Heat | 3/3 | 1.00 | 0.29–1.00 | 0.44–1.00 |
| Coastal / erosion / sea level | 4/11 | 0.36 | 0.11–0.69 | 0.15–0.65 |
| Wildfire | 0/0 | not estimable | | |

| Term | Yes / n |
|---|---|
| flood | 7/7 |
| flooding | 5/5 |
| rainfall | 1/2 |
| storm | 1/8 |
| drought | 4/4 |
| water scarcity | 2/2 |
| water stress | 3/4 |
| heatwave | 1/1 |
| extreme temperature | 2/2 |
| erosion | 2/6 |
| coastal | 1/4 |
| sea level | 1/1 |

**2. A20 rule applied as written.**
- **Overall precision 0.65 < 0.80, so H1–H3 are reported as descriptive only.** No confirmatory test is claimed; the BH family (OD-15) is not applied as a confirmatory claim.
- **Limitations (terms with precision below 0.50 and n ≥ 5):**
  - **storm** (1/8 = 0.13);
  - **erosion** (2/6 = 0.33).
- **Noted separately (n < 5, below the rule's minimum):** **coastal** (1/4 = 0.25).
- **Not estimated:** heat (n = 3) and wildfire (n = 0) remain limitations, as recorded in A20.
- **Counts are unchanged:** the frozen dictionary remains the main dictionary.

**3. Exploratory refined dictionary (post hoc).**
- **Terms:** `config/dictionary_hazard_refined.json` is the frozen dictionary minus "storm", "erosion" and "coastal", leaving 13 terms with the same matching rule (A17).
- **No phrases kept:** the frozen list contains no multi-word phrase with these words (no "storm surge" or "coastal erosion"), so nothing is kept from them.
- **Chosen after seeing the precision results.** Its precision on the same 46 snippets (26/28 = 0.93, after removing the 18 storm, erosion and coastal snippets) is **optimistic and not an independent estimate**.
- **Reporting:** results with the frozen dictionary (main) and the refined dictionary (exploratory) are both reported. The refined version never replaces the main one.

**4. Outcome computation (no H1–H3 model is estimated; that is Phase 5).**
- **Unit:** firm-year (all documents of a firm with the same fiscal-year label combined).
- **Firms:** all firms with documents, main and robustness strata, with `stratum` and the A16 `h3_main` flag carried along.
- **Scored paragraphs:** model-eligible narrative rows of `paragraphs.csv` (split pieces count separately, as in f3).
- **Dictionary measures:**
  - **Measures:** Y3d, Y4d (count and binary), Y4s and Y4r as defined in A20, each computed with the frozen and with the refined hazard dictionary.
  - **Site matching:** `config/dictionary_sites.json` rules R1–R3, matching only the firm's own sites, with its `exclude_phrases` removed first.
- **ClimateBERT measures (exploratory, unvalidated, A20):**
  - **Y1** (climate share): P(yes) ≥ 0.5.
  - **Y2** (specific share among climate paragraphs): P(spec) ≥ 0.5.
  - **TCFD category shares** and **sentiment shares** among climate paragraphs (argmax).
  - **Reuse of predictions:** the detector and specificity probabilities already in `data/interim/validation_predictions.csv` (A19 frame, same revisions `2c3bc660…` and `4ada96ed…`, same text) are reused, because the models are deterministic. Only rows outside that frame are scored new: robustness-stratum firms and DANGCEM_2025_SRX. TCFD and sentiment are run on all detector-positive paragraphs.
  - **Revisions** are recorded in `parameters.json` `text.models.revision_hash`.
- **Not computed in this step:** Y5 (site ever named, H4).
- Outcome data seen before this decision? Precision-check answers only. No outcome measure, corpus count or corpus share had been computed.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): H1–H3 become descriptive only (A20 rule).
- Results to be reported both ways? Yes: frozen dictionary (main) and refined dictionary (exploratory, post hoc).

**A21 computation record (2026-11-18).**

**Precision results:** `data/interim/precision_results.csv` (SHA-256 `89853f89c27890057b0100f8635e586d255eaffaf550270e98eb3d338de27f46`), written by `src/phase4_precision_results.py` (`b68e5df2…a5e1`).

**Refined dictionary:** `config/dictionary_hazard_refined.json` (13 terms), SHA-256 `957f1f2c992e047d03d5688f8e8549b60ead9241af7d4fbd879ca9a3f3db261f`.

**ClimateBERT scores (exploratory):** `data/interim/climatebert_scores.csv`, SHA-256 `85e619067323a06728108d7c80a7eb04ec3855f77d5a4c4513a618a2a2d5e416`.

| Model | Paragraphs | How obtained |
|---|---|---|
| Detector | 15,601 scored paragraphs | 15,293 reused from `validation_predictions.csv`, 308 scored new |
| Specificity | 3,079 detector-positive paragraphs | 2,960 reused, 119 new |
| TCFD | 3,079 detector-positive paragraphs | all new |
| Sentiment | 3,079 detector-positive paragraphs | all new |

The four model revisions are recorded in `parameters.json` (`text.models.revision_hash`). After the A21 entries, `parameters.json` has SHA-256 `9a10985b807c5c6767fd482a04aade59d79ef7e72befd1be28264382a5fb9f05`.

**Outcomes:** `data/processed/outcomes_firm_year.csv` (103 firm-years), SHA-256 `b785798df87555e8ae5cc2ab8d6f6f1e0128271774b57087cf4b3d0c6deaa6c8`, written by `src/phase4_outcomes.py` (`ad8bb84d…16a9`).
- The two Cadbury FS-only firm-years have no scored narrative paragraph. They are kept with `n_scored` = 0 and empty shares.
- No H1–H3 model was estimated.

### A22: Phase 5 implementation: control-variable collection, Y5, exposure measures and estimators
- Date: 2026-11-18. **Logged before any control was extracted, before Y5 was computed and before any H1–H4 estimate.**
- Decided by: the project owner chose to extract the missing controls from the documents held (2026-11-18). The rules below are the analyst's, because the design does not give them.
- Section(s) of design.md affected: h (controls, estimation, inference), a (H4 via Y5), e6 (which exposure measure). design.md is not edited.
- **Status reminder:** under A20/A21, H1–H3 are **descriptive only**. Effect sizes are reported with 95% intervals, and no test result is claimed.

**1. Controls (design h; collected only for the H1/H2 sample: the 27 exposure-scored main-census firms, 70 firm-years).**
- **Output:** `data/interim/controls_firm_year.csv`, with value, source document, page, quoted evidence, method (rule / analyst) and flag for every value.
- **Flagged values** are listed for the owner. Until the owner checks them, models use the analyst's value; a firm-year with a missing value is dropped from the models that need it, and the drop is reported.

| Control | Rule |
|---|---|
| **Big Four auditor** (1/0) | **Search:** the pages of the firm-year's AR/FS document from the A14 financial-statement start to start + 5, for KPMG; PricewaterhouseCoopers / PwC; Ernst & Young / "EY" (whole word); Deloitte. **1** if found. **0** if these pages have text naming another auditor. If the pages have no usable text, the analyst reads the directors' report "Auditors" paragraph; if still unclear, missing and flagged |
| **External assurance** (1/0) | **1** if any document of the firm-year contains a sentence with ("limited assurance" or "reasonable assurance" or "independent assurance" or "assurance statement" or "assurance engagement") together with (sustainability, ESG, GHG, greenhouse, emission, non-financial, climate or environmental) and **not** ("internal control" or "ICFR"). Every hit is read by the analyst and kept only if it is assurance of sustainability or climate information by an independent provider. **0** otherwise |
| **Size** (log total assets, reporting currency) | **Value:** the first "Total assets" row on a statement-of-financial-position page inside the A14 range; current-year value; group column if consolidated. **Unit:** from the page ('000 / million / billion), converted to currency units. **Currency** recorded (₦ or US$). Any value with an unclear unit, column or currency is read by the analyst on the page and flagged. US$ reporters stay in US$, as the design says "in the reporting currency"; this is noted as a limitation |
| **Foreign parent** (≥ 50%, OD-13; 20% robustness) | **Candidates:** sentences naming a parent, holding company or substantial shareholder with a percentage or "subsidiary of", from the firm-year's documents (corporate information, directors' report shareholding analysis, note 1). **Analyst:** records the largest foreign-domiciled holder's share with page and quote. **1** if ≥ 50% (and a 20% version). Firm-years with no statement are flagged; the nearest year of the same firm may be used, marked "carried" |
| **Sector** | `ngx_census_frame.csv` `sector_provisional` (activity-based; not the NGX label). Noted as a limitation |
| **Document type** | From `outcomes_firm_year.csv` (`fs_only`) |

**2. Y5 and H4 (design f6, h).**
- **Y5 = 1** if a site is named (site dictionary, A17 rules R1–R3, exclude_phrases first) in any row of `paragraphs.csv` from the firm's documents 2020–2025: any section (including financial-statement notes, f1), any length, duplicates included ("any context").
- **H4:** the share of **main-analysis point sites** (site_set = main, main census) exposed on at least one hazard (river flood RP100, ERA5 heat, coastal RP100, water stress) with Y5 = 0. It is reported overall, by firm and by sector, with exact binomial 95% intervals. Main-census sites only; the robustness stratum is reported separately.
- **Hazard-specific gap tables:** for each exposed firm and hazard:
  - whether any scored narrative paragraph uses that hazard family's terms (river flood → flood family; coastal flood → flood or coastal family; heat → heat family; water stress → drought / water stress family);
  - whether any exposed site is named in a hazard-tagged scored paragraph.

**3. Exposure in H1/H2 (design e6, OD-8).**
- **Primary:** separate models for **river-flood E_share** and **heat E_share** (the primary hazards).
- **Secondary:** the four-hazard combined index.
- **Also reported:** coastal and water-stress E_share.
- **Robustness (labelled):** NASA POWER heat (`rob_nasa_heat_E_share`, `rob_nasa_heat_combined_index`), A7 500 m buffers and the A8 no-permanent-water flood variant.

**4. Estimators and intervals** (design h, with the details the design leaves open):
- **H1:**
  - **Main model:** fractional logit (GLM binomial, logit link) of Y4s on exposure, controls, year fixed effects and sector fixed effects. Fixed effects are dropped if the model does not converge or is separated; any drop is reported, never tuned.
  - **Interval for the main model:** cluster (firm) pairs bootstrap, 9,999 replications, percentile 95% interval. This is used because the wild cluster bootstrap is defined for linear models; CR1 cluster-robust intervals are shown alongside.
  - **OLS robustness:** wild cluster bootstrap (unrestricted, Webb six-point weights, 9,999 replications), percentile-t 95% interval.
  - **Secondary outcomes:** Y3d (fractional logit) and the Y4d binary (logit), with the same intervals.
  - **Instability flags:** the number of non-zero outcomes, separation or non-convergence, and bootstrap draws that fail. These are reported, not fixed.
- **H2:**
  - **Blocks:** (a) exposure only, (b) institutional only (log assets, foreign parent, external assurance, Big Four, sector), (c) both. Standardised variables, OLS.
  - **Reported:** the increase in R² from each block, and the standardised coefficients, with cluster pairs bootstrap 95% intervals (9,999 replications).
- **H3:**
  - **Sample:** firms with at least 2 main-analysis years (A16).
  - **Model:** OLS with firm fixed effects of standardised Y3d and Y4r (each divided by its standard deviation over the H3 firm-years) on t = year − 2020.
  - **Reported:** τ(Y3d), τ(Y4r) and their difference, from a joint (stacked) regression, with wild cluster bootstrap intervals (Webb, 9,999 replications).
  - **Robustness:** pre-listing years included (A16).
- **Seed:** 20261118 for all bootstrap draws.
- **No significance language:** results are reported only as effect sizes with 95% intervals.

**5. Software:** numpy 2.5.4, pandas 2.3.3, statsmodels 0.15.0, scipy 1.18.1 and matplotlib 3.11.2, installed 2026-11-18 for Phase 5.
- Outcome data seen before this decision? The firm-year outcomes were computed in Phase 4 (A21), and their summary descriptives are in `docs/phase4_corpus.md` 9.2. No model had been estimated and no control had been collected.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none; H1–H3 are already descriptive only (A21). This sets how they are estimated.
- Results to be reported both ways? Main and labelled robustness versions, as listed.

### A23: NNFM FY2020 file is Flour Mills of Nigeria's report; excluded (data correction)
- Date: 2026-11-18. Found during the Phase 5 control extraction; **logged before any H1–H3 estimate.**
- Decided by: the analyst. It is a data correction; the owner may supply the correct file.
- **What was found:** `data/raw/manual/nnfm/2020_AR.pdf` was recorded in owner batch 2 as Northern Nigeria Flour Mills' FY2020 annual report. It is **Flour Mills of Nigeria Plc's 2020 annual report**:
  - its auditor's report is addressed "To the Shareholders of Flour Mills of Nigeria Plc";
  - its pages are headed "FMN Annual Report 2020";
  - "Flour Mills of Nigeria Plc" appears 34 times, and NNFM only as a subsidiary;
  - its total assets are ₦432bn, against ₦30bn in NNFM's own FY2025 report.
- **Not used in the analysis:** FMN was delisted (c, rule 2), so the document is excluded from every Phase 5 analysis (`NNFM_2020_AR`). It stays on disk and in the Phase 4 outputs, marked here.
- **Consequences:**
  - NNFM has one year only (FY2025).
  - The H3 sample falls from 28 to **27 firms with ≥ 2 main-analysis years**.
  - The H1/H2 sample loses one firm-year.
- **Check of the other documents:** the auditor's-report addressee on the financial-statement start pages was checked for all 107 documents. No other document names a different company. Some documents have no addressee line in those pages (images or layout), so they were not checked this way.
- Effect on confirmatory hypotheses: none (H1–H3 are descriptive only); sample sizes change as above.

### A24: IFRS S2 paragraph anchors for policy code P5 (follow-up committed at the freeze)
- Date: 2026-11-18. **Logged before any Phase 6 policy coding.**
- Decided by: the analyst, completing the freeze follow-up "Add the IFRS S2 paragraph anchors for policy code P5, once the standard is supplied". The owner supplied the standard on 2026-11-18 (`docs/data_sources.md`, owner batch 6).
- Section(s) of design.md affected: i (policy coding scheme, P5: "pending — owner to supply IFRS S2 before Phase 6"). design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value):
  - `sociology_policy.ifrs_s2`: "pending" -> the supplied file, edition and effective dates.
  - New key `sociology_policy.p5_definition`.
  - The P5 label in `policy_codes`.
- **Source:** IFRS S2 *Climate-related Disclosures*, consolidated edition "ISSB-2026-A" (June 2023 Standard with the December 2025 greenhouse gas amendments). Effective for annual reporting periods beginning on or after 1 January 2024 (para C1); the amendments apply from 1 January 2027.
- **Anchors** (paragraph numbers only; the text is paraphrased, not quoted, under the personal non-commercial licence):
  - **Para 13(b):** an entity describes where in its business model and value chain climate-related risks and opportunities are concentrated, for example by geographical area, facility or type of asset.
  - **Para 29(c):** cross-industry metric; the amount and percentage of assets or business activities vulnerable to climate-related physical risks.
  - **Para B65(b):** when preparing the 29(b)–(g) metrics, the entity considers where risks are concentrated (refers back to para 13).
  - **Appendix A**, "climate-related physical risks": acute (event-driven) and chronic (longer-term shifts) physical risks.
- **P5 coding rule:** P5 = 1 if the firm-year's documents identify where climate-related physical risks are concentrated by geographical area, facility or type of asset (13(b)), or report the amount or percentage of assets or business activities vulnerable to physical risk (29(c), B65(b)). Otherwise P5 = 0.
  - **Definition of physical risk:** as in Appendix A.
  - **Limits:** P5 stays a policy-alignment code (section i). It is not an outcome measure and does not enter H1–H4.
- **IFRS S2 citations in outputs:** design i allowed IFRS S2 paragraph numbers only after the standard was supplied and read. They may now appear, as paragraph numbers.
- Reason: follow-up committed at the design freeze (2026-11-07).
- Outcome data seen before this decision? Yes, the Phase 4 outcomes and the Phase 5 descriptive results exist. P5 is anchored to the standard's text, not to any result, and no policy code has yet been applied to any firm-year.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none.
- Results to be reported both ways? No.
- parameters.json hash after change: `e8355364bd2c02e7c5444ac481413a280524216011fc9f990f1510c2154bb454` (SHA-256; previous hash after A21 was `9a10985b807c5c6767fd482a04aade59d79ef7e72befd1be28264382a5fb9f05`; A22 and A23 did not change parameters.json). design.md is unchanged since A20: `ed4bf262f4fd46b294ea27c72b815bbe744795cb396562290661c78688b7a534`.

### Owner decisions of 2026-11-18 on the Phase 5 open items (no amendment; no outcome changed)
1. **The 12 flagged control values** (`data/interim/controls_firm_year.csv`, `flag` column) will be re-verified against their page references in Phase 7. Until then they stay as collected.
2. **H4 is reported as designed**, with its caveat: Y5 is near-mechanical, because the site list was built from the same reports, so 1 of 51 exposed sites is never named.
   - **Post-hoc addition:** the "named in hazard text" gap (7 of 51 exposed main sites named in a hazard-tagged paragraph) is added as a **clearly labelled post-hoc descriptive**. It does **not** replace H4.
3. **NNFM FY2020 (A23):** no replacement report will be sought; NNFM stays a single-year firm.

**Phase 6 sources, Seplat:** the SEPLAT 2023 Sustainability Report and the 2025 Social Performance Report are held for Phase 6 policy coding only. They are **not** added to the Phase 4 corpus, and no paragraph, measure or outcome changes (owner instruction).

### A25: firm-year policy coding (P1–P7, design i) by documented rules, analyst-coded, descriptive
- Date: 2026-11-18. **Logged before any policy code was assigned.**
- Decided by: the project owner (decision of 2026-11-18): "do the design's firm-year policy coding now, as a DESCRIPTIVE, analyst-coded step".
- Section(s) of design.md affected: i (policy coding scheme). design.md is not edited.
- Parameter(s) in config/parameters.json affected (old value -> new value): new key `sociology_policy.policy_coding` (none -> the rules below).
- **Status: descriptive.**
  - **Coder:** the analyst (Claude). There was no second coder and no human validation, and no reliability statistic is claimed.
  - **Use:** the codes describe the documents held. They are **not** outcomes and do not enter H1–H4, and no Phase 5 outcome changes.
- **Scope:** every main-census firm-year with documents (99; NNFM FY2020 excluded under A23). The search covers all documents of the firm-year and all sections, including short rows (all rows of `paragraphs.csv`).
- **Procedure:**
  - **Search:** for each code, the sentences matching the search patterns below are extracted. **The analyst reads every match.**
  - **Coding:** a code is 1 only if a matched passage meets the rule. Every positive code is recorded with document, page, paragraph id and the passage. A firm-year with no qualifying passage is coded 0.
  - **Doubtful cases** are coded 0 and noted.
- **Rules and search patterns** (case-insensitive; a sentence must match all the listed parts):

| Code | Rule (1 if …) | Search pattern (sentence level) | Anchor |
|---|---|---|---|
| P1 | the resilience of the firm's strategy or business model to climate-related physical risks or climate hazards is discussed | `resilien*` AND (climate \| physical risk \| flood \| heat \| drought \| weather \| hazard) | FRC Roadmap PDF p23; IFRS S2 22 |
| P2 | climate-related scenario analysis was used (qualitative or quantitative) | `scenario analysis` \| `climate scenario` \| scenario with (RCP \| SSP \| NGFS \| IEA \| 1.5 °C \| 2 °C \| net zero \| warming) | FRC Roadmap PDF pp23–24; IFRS S2 22 |
| P3 | a physical-risk metric is reported: an amount or percentage of assets, sites or activities exposed or vulnerable to physical climate hazards | a number or % AND (physical risk \| flood \| heat \| drought \| water stress \| hazard \| extreme weather) AND (asset \| site \| facilit* \| operation \| location) | FRC Roadmap PDF p25; IFRS S2 29(c) |
| P4 | climate-related (physical) risks are identified or managed inside the risk-management process | (risk register \| enterprise risk \| ERM \| risk management framework \| risk map \| risk committee \| principal risk \| risk universe) AND (climate \| weather \| flood \| physical risk) | FRC Roadmap §7.4; IFRS S2 25 |
| P5 | locations or assets at physical risk are identified (A24) | (physical risk \| flood \| heat \| drought \| water stress \| sea level \| coastal \| storm \| extreme weather \| hazard) AND (site \| plant \| facility \| asset \| location \| terminal \| estate \| OML \| a site-dictionary term of the firm) | IFRS S2 13(b), 29(c), B65(b) |
| P6 | adoption status: **early** (applies IFRS S1/S2 for a period ending on or before 31 Dec 2023); **voluntary** (states it applies or reports in accordance with IFRS S1/S2 for a 2024–2027 period); **none** otherwise. Statements of readiness, plans or alignment only are recorded as "none (readiness stated)" | (IFRS S1 \| IFRS S2 \| ISSB) | FRC Roadmap §6.1; SEC circular |
| P7 | the NGX (or NSE) Sustainability Disclosure Guidelines are referred to | `Sustainability Disclosure Guidelines` \| (NGX \| NSE \| Nigerian Exchange \| Nigerian Stock Exchange) within 80 characters of `sustainability … guideline*` | NGX Guidelines (2018) |

- **Hazard terms in P1, P3 and P5:** read in context, not taken from the frozen dictionary. These codes are judgements about passages, not counts.
- **Outputs:**
  - `data/processed/policy_codes_firm_year.csv` (one row per firm-year, P1–P7);
  - `data/processed/policy_codes_evidence.csv` (one row per positive code: document, page, paragraph id, passage);
  - the candidate file `data/interim/policy_candidates.csv`;
  - code: `src/phase6_policy_codes.py`.
- **Phase 7:** every positive code, and a sample of zero codes with candidate matches, is re-checked against its page.
- Reason: owner decision. The design's policy coding (section i) had not been done.
- Outcome data seen before this decision? Yes: the Phase 4/5 outcomes and the Phase 6 draft (including the Seplat reading) exist. The rules are fixed before any code is assigned, and the codes do not feed any outcome.
- Effect on confirmatory hypotheses (none / H1 / H2 / H3): none.
- Results to be reported both ways? No.
- parameters.json hash after change: `e63b2689510dc47a07fa0fba2df410fdb23ee3490a664ec6df19221e9b33da80` (SHA-256; previous hash after A24 was `e8355364bd2c02e7c5444ac481413a280524216011fc9f990f1510c2154bb454`).

**A25 coding record (2026-11-18).**
- **Scope:** 403 candidate sentences were extracted and every one was read; 44 analyst decisions were recorded (positives, P6 values, and notes on doubtful zeros).
- **Result:** 99 firm-years coded.
  - **Firm-years coded 1:** P1 4, P2 5, P3 2, P4 7, P5 4, P7 7.
  - **P6:** voluntary 2 (MTN Nigeria and Seplat FY2025), readiness stated 7, none 90.
- **Files (SHA-256):**

| File | SHA-256 |
|---|---|
| `data/processed/policy_codes_firm_year.csv` | `0b58fd92d7c7f11e7f8f98aacfa072f6f69322b53ddeb10cce0f1bdb80d5f5ab` |
| `data/processed/policy_codes_evidence.csv` | `6415e522c82358442867078b7d1dd6286fb8e2c6ef2a80dbc4f78060d97c4ede` |
| `data/interim/policy_candidates.csv` | `01e9859f98d1c152a4a36783521043c4a6630f4176e221964662ec0348c19922` |
| `data/interim/policy_decisions.csv` | `f6661ad5367b51b7312933b2b65aac06b27c908dc0b90d7e5004e4888093c434` |
| `src/phase6_policy_codes.py` | `5c5605bcc3cf62bd3e7b39a5ef2ec2582d4957aa38550ea1c1f1e63fdc82404e` |

- **Unchanged:** no Phase 4 or Phase 5 output.

### A26: Phase 7 data correction: Vitafoam FY2025 total assets (control variable); flagged controls re-verified
- Date: 2026-11-18. **Logged before the affected models (H1, H2) were re-run.**
- Decided by: the analyst, as a data correction with page evidence (owner decision of 2026-11-18: flagged controls are re-verified in Phase 7). No design rule changes.
- Section(s) of design.md affected: none (the size control of h).
- **Correction:** Vitafoam FY2025 total assets were recorded as ₦43,693,181 thousand, taken from the five-year summary (p127). That summary's "Total assets" line is non-current assets plus **net** current assets, so it is net of current liabilities. The group statement of financial position (p57, image only) shows **₦65,275,389 thousand** (17,176,064 + 48,099,325). The value is corrected in `src/phase5_controls_build.py`, and `data/interim/controls_firm_year.csv` is rebuilt.
- **The other flagged values were verified against their pages, with no value change:**
  - Aradel FY2024 total assets: the FY2024 report's own statement, p77.
  - Okomu FY2021 total assets: the FY2021 report's own statement, p38.
  - Geregu FY2024 total assets: page image, p52.
  - Unilever FY2020 foreign parent: 75.97%, p133.
  - Guinness FY2025 foreign parent: ultimate parent Tolaram Group (p9), headquartered in Singapore (p45).
  - Japaul FY2021 Big Four = 0: no Big Four name anywhere in the file; the auditor's identity is still inferred.
- **Seplat FY2020:** the recorded foreign share is corrected from 20.07% to 20.46% (p142). The code is unchanged.
- **Still flagged:**
  - Beta Glass: indirect foreign parent, an interpretation of the rule; the quote is verified.
  - Seplat FY2025: whether Maurel & Prom's 20.07% was still held at year-end is ambiguous. This matters only for the 20% foreign-parent robustness check, which has not been run (see `docs/phase7_verification.md`).
  - NNFM FY2020: excluded (A23).
- **Re-run:** H1 and H2 are re-run with the corrected control, and their tables replace the previous ones. The changes are reported in `docs/phase7_verification.md`. H3, H4, Y5 and the gap tables use no controls and are unaffected.
- Outcome data seen before this decision? Yes, the Phase 5 results. The correction follows the page evidence, not the results.
- Effect on confirmatory hypotheses: none (H1–H3 are descriptive only). It changes the H1/H2 estimates.

**A26 re-run record and Phase 7 notes (2026-11-18; no design rule changed).**

**Outputs after the A26 correction (SHA-256):**

| File | SHA-256 |
|---|---|
| `data/interim/controls_firm_year.csv` | `85c86005…bf8d` |
| `data/processed/analysis_firm_year.csv` | `a23782a5…b4f2` |
| `outputs/tables/h1_results.csv` | `bad67215…615e` |
| `outputs/tables/h2_results.csv` | `f5bba54b…468c` |

**H3:** `h3_results.csv` (`b1301380…fd27`) reproduced byte-identical.

**Changes in the quoted numbers:**
- H2 Y3d size coefficient: +0.39 → +0.40.
- All other quoted H1/H2 figures are unchanged at two decimals.

**Site-named hazard paragraphs (Phase 7 re-read):**
- Of the 11 paragraphs behind the 8 firm-years with Y4d > 0, 10 are not statements about physical risk at a site. They are donation tables, biographies, community items and a drainage design study.
- 1 is genuine: Seplat FY2025, OML 40.
- The frozen rules (A17, A20) were applied correctly, so no data were changed.
- The interpretation of Y4d, Y4s and Y4r is restricted in the text of `docs/phase5_analysis.md` and `docs/phase6_policy.md`; see `docs/phase7_verification.md`.

**Text correction:** "68 of 98" → "68 of 97" (NNFM FY2020 excluded under A23).
