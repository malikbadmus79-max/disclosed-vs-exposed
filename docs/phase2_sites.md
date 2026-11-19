# Phase 2: Site database

**Date:** 2026-11-07; updated 2026-11-11 (update 3) and 2026-11-12 (updates 4 to 8). This phase follows the frozen design (`docs/design.md`, version `frozen-2026-11-07`). **No hazard scores were computed.** Six amendments are logged in `docs/amendments.md`, all on 2026-11-12 and each before it was applied:

- **A1:** readability threshold 0.25, with wordfreq as the word list. Confirmed by the owner.
- **A2:** a page-level OCR trigger.
- **A3:** page-by-page text selection.
- **A4:** a refined page-selection rule that replaces A3's.
- **A5:** a share condition on A4's token-count rule.
- **A6:** a rule-based cross-check of grade-A locations, which replaces the owner's visual spot-check (OD-1).

**Text selection is now final for this study.** The implementation choices made within OD-1 are listed in section 4 for the owner to review.

**Update, 2026-11-07 (owner-approved aggregator and registrar round).**

- **africanfinancials.com: not used.** Its terms forbid "data mining tools, robots, or similar data gathering and extraction instruments".
- **sustainabilityreports.com: not used.** It returned HTTP 403.
- **Airtel Africa: not fetched.** Its PDF host returned 403 for robots.txt.
- **LIVESTOCK:** downloaded from its registrar.
- **THOMASWY:** the owner-supplied file was registered. It is scanned, with no text layer.
- **Failed the document test:** AUSTINLAZ (abridged only) and PHARMDEKO (none found), per the owner.

**Update 2, 2026-11-07 (nine owner-supplied reports).** The owner supplied reports for ACADEMY, ARADEL, BUAFOODS (FY2024), ELLAHLAKES, ENAMELWA, FIDSON, MEYER, MULTIVERSE and NNFM, downloaded in a browser from africanfinancials.com document pages. Seven had text layers and were processed. Ellah Lakes and Multiverse waited for OCR, which was blocked because Ghostscript was not installed.

**Update 3, 2026-11-11 (OCR, and 19 more owner-supplied reports).**

- **OCR is done.** The owner installed Ghostscript 10.08.0. Ten scanned files were OCR'd with OCRmyPDF 16.13.0, Tesseract 5.4.0 and Ghostscript 10.08.0: Okomu FY2023 and FY2024, Thomas Wyatt, Ellah Lakes, Multiverse, McNichols, Union Dicon, Alex, Eterna, and **Geregu**. Geregu was not on the owner's OCR list, but its file is a scan whose only text is the site's watermark. The originals are unchanged; each copy has `_ocr` in its name.
- **19 owner-supplied reports were processed:** TOTAL, CHAMPION, EUNISELL, GOLDBREW, IMG, JAPAULGOLD, MCNICHOLS, MECURE, MULTITREX, TRIPPLEG, UNIONDICON, ALEX, ETERNA, TRANSPOWER, CAP, OANDO, JBERGER, AIRTELAFRI and GEREGU. All pass the document test.
- **Ellah Lakes, Multiverse and Thomas Wyatt** were finished from their OCR copies. Okomu's facilities now cite its FY2024 annual report.
- **PREMPAINTS:** no file was in `data/raw/manual/`, so it stays pending.
- **The readability test was not run** (section 2a). The network was down during this session, so no list of the 1,000 most common English words could be obtained, and the threshold has not been calibrated yet (OD-9).
- **No new coordinates from OSM.** Overpass could not be reached (no network), so the new place names were not queried. Only places already in the cached OSM data got coordinates (section 4).

**Update 4, 2026-11-12 (owner decisions).**

- **Readability test calibrated and run.**
  - **Word list:** wordfreq 3.1.1's top 1,000 English words.
  - **Calibration:** on the 35 Phase 0 files with a text layer, 0.30 also failed BUA Cement 2024 (share 0.2807), so it broke the calibration rule. The threshold is set to **0.25** by amendment A1, logged before the corpus run.
  - **Corpus run:** 94 files, including all 11 OCR copies; 9 fail (section 2a).
- **Overpass: still pending.** The approved query for the 18 new place names returned HTTP 502 ("server at capacity") on the first attempt and on one retry about 2 minutes later. Following the owner's instruction, the step was stopped and the places are marked pending. No state check was run.
- **Multi-Trex:** its 20 image-only pages were OCR'd. No facility location was found on them.
- **PREMPAINTS:** no file had arrived, so it fails the document test ("report not obtainable, 2026-11-12").
- **Frozen files:**
  - `docs/design.md` is unchanged (SHA-256 `f563379e…714`, as frozen).
  - `config/parameters.json` matched its frozen hash (`0ca716a8…167f`) before A1. A1 changed it as amendment rule 4 requires; its new hash is `f3182d6e…26f2`, recorded in A1.

**Update 5, 2026-11-12 (second round of owner decisions).**

- **A1 confirmed** by the owner.
- **Unilever 2025 OCR'd** (same tools and settings). Its OCR copy scores 0.541, against 0.0095 for the original.
- **A2 (page-level OCR trigger) logged and applied.** A file is OCR'd if more than 10% of its pages have a share below 0.20. It catches 24 of the 83 original files (`data/interim/readability_pages.csv`):
  - **12 already OCR'd:** the 11 scans, plus Multi-Trex, whose low pages are exactly its image pages, OCR'd in update 4.
  - **Unilever:** OCR'd in this update.
  - **11 newly OCR'd:** BUA Cement 2024, Nigerian Breweries 2025, Guinness 2020, 2021, 2022 and 2024, Lafarge 2023, Champion 2025, IMG 2025, Academy 2025, RT Briscoe 2025, and Okomu 2020 (older than the 2023–2025 window).
  - **Academy page 17** keeps its original text layer: OCRmyPDF could not read a DeviceN image on it.
- **Forced OCR lost text on some born-digital pages.** On 42 pages, the OCR copy has less than half the original's text (`data/interim/a2_ocr_text_loss.csv`):

  | File | Pages affected |
  |---|---|
  | Guinness 2020 | 20 |
  | Champion 2025 | 16 |
  | Lafarge 2023 | 3 |
  | Academy 2025 | 1 |
  | Guinness 2022 | 1 |
  | Guinness 2024 | 1 |

  On Champion p63, OCRmyPDF returned 62 characters for a clean 3,980-character page. Tesseract alone and a Ghostscript render of the same page both read it correctly, so the loss happens inside the OCRmyPDF pipeline; the cause was not investigated further.
- **A3 (page-level text selection) logged and applied** in response. For each of the 24 reports with an OCR copy, `src/text_select.py` chooses each page's text from the original or the OCR copy, and writes `data/interim/text/<key>.txt` and `data/interim/text_sources.csv` (section 2b).
- **OSM lookup done through the Geofabrik extract.** The alternative Overpass instance (overpass.private.coffee) returned HTTP 504. The Geofabrik Nigeria extract (data up to 2026-11-11T21:22:47Z) was then downloaded once and searched locally with pyosmium. 9 of the 18 place names matched, giving 9 new coordinates, all consistent with the reported state (section 4).
- **Frozen files.** `docs/design.md` is unchanged (`f563379e…714`). `config/parameters.json` changed only by amendment, and each new hash is recorded in that amendment: A1 `f3182d6e…26f2`, A2 `bb6e2e88…e09c`, A3 `3c81a7c2…91a4`.

**Update 6, 2026-11-12 (third round of owner decisions).**

- **A4 logged and applied** (section 2b). It refines A3's page selection: the higher-share version wins, unless it has fewer than half the word tokens of the other version. 291 pages switched source. BUA Cement 2024's merged text rises from 0.382 to 0.541.
- **Named OSM ways and relations searched** in the extract already on disk, for the 10 place names with no place node. Only **Utako** matched (relation 12207339, an administrative area in FCT), which places Julius Berger's registered office (section 4).
- **The OCRmyPDF text-loss investigation was skipped,** per the owner.
- **Spot-check helper built:**
  - `data/processed/spotcheck_app.html` shows one grade-A site at a time, operational sites first.
  - `docs/spotcheck_guide.md` explains how to use it.
  - `src/merge_spotcheck.py` merges the exported CSV into `spotcheck_gradeA.csv`. Rebuilds of the spot-check file keep the merged columns.
- **Frozen files.** `docs/design.md` is unchanged (`f563379e…714`). `config/parameters.json` after A4 is `600bda84…7528`.

**Update 7, 2026-11-12 (A5; text selection final).**

- **A5 logged and applied.** A4's "fewer than half the word tokens" rule now applies only when the other version's share is at least 0.20, so a version scoring below 0.20 can never win through it.
- **Pages switched against A4: 10.**
  - **Unilever 2025, 7 pages** (pp. 12, 15, 108, 146–149): garbled original → OCR. The merged-text share rises from 0.530 to 0.541.
  - **Guinness, 3 pages** where A4 had taken a low-share OCR page through the same rule: 2021 p107 (OCR 0.09 → original 0.52), 2022 p17 (OCR 0.19 → original 0.25) and 2024 p113 (OCR 0.10 → original 0.58). Merged-text shares rise slightly: 2021 from 0.578 to 0.581, 2022 from 0.583 to 0.583, 2024 from 0.576 to 0.579.
- **The text-selection rules are final for this study** (owner decision; recorded in A5). They are the A2 trigger, plus A3 as refined by A4 and A5.
- **Frozen files.** `docs/design.md` is unchanged (`f563379e…714`). `config/parameters.json` after A5 is `abe2795a…eb86a`.

**Update 8, 2026-11-12 (A6: rule-based grade-A cross-check).**

- **A6 logged and applied.** The owner's visual spot-check (OD-1) is replaced by a documented rule applied to all 87 grade-A rows (`src/a6_crosscheck.py`).

  | Category | Rows | Operational | Offices | Phase 3 buffer |
  |---|---|---|---|---|
  | `correct (rule-based)` | 7 | 4 | 3 | 500 m (OD-2 grade-A buffer) |
  | `approximate (rule-based)` | 67 | 22 | 45 | `coord_precision_m`: 2,000 m (22 rows), 5,000 m (24), 10,000 m (21) |
  | `no coordinate` | 13 | 4 | 9 | Not scored in Phase 3; reported as a limitation |

  - **Correct:** an OSM feature that matches the firm by name and is consistent with the reported state. The 7 rows are F0001 Dangote head office, F0011 and F0012 BUA Cement Obu and Kalambaina, F0016 and F0017 Guinness Ogba HQ and brewery, F0042 Cadbury and F0059 NB Ibadan.
  - **Approximate:** a place centroid (46 osm_place, 21 osm_place_rank).
  - **No coordinate:** 12 rows have none and 1 was withdrawn (Conoil's "Marina").
- **Outputs.**
  - `spotcheck_gradeA.csv`: the owner columns hold the label, with the comment "A6 rule-based cross-check, 2026-11-12". New columns `a6_check` and `buffer_m`.
  - `facilities.csv` and the GeoJSON: new columns `a6_check` and `buffer_m`, filled for grade-A rows only. Grade B and C buffers follow OD-2 unchanged and are set in Phase 3.
  - A later manual owner entry in the spot-check file would be kept on rebuild, not overwritten.
- **Limitations note** (recorded in A6 for design section j): "Location accuracy was assessed by a documented rule-based cross-check rather than manual visual inspection."
- **The spot-check helper stays** (`spotcheck_app.html`, `docs/spotcheck_guide.md`, `src/merge_spotcheck.py`) but is no longer required.
- **Frozen files.** `docs/design.md` is unchanged (`f563379e…714`). `config/parameters.json` after A6 is `4d59d116…f1f4`.

All numbers below include updates 3 to 8. Details are in `docs/manual_download_list.md` and `docs/data_sources.md`.

## Outputs

| File | Content |
|---|---|
| `data/processed/facilities.csv` | 214 facilities, one row each. Each row holds the report quote and PDF page, asset type, A–D grade, location source, coordinates (where assigned), coordinate method, source and nominal precision, and the result of the state cross-check |
| `data/processed/facilities.geojson` | The 125 facilities with coordinates |
| `data/processed/spotcheck_gradeA.csv` | All 87 grade-A facilities, with the report quote, coordinates, an openstreetmap.org link and blank owner-check columns |
| `data/processed/sites_map.html` | A simple Leaflet map for review: points coloured by grade, with a circle for nominal precision |
| `data/processed/spotcheck_app.html` | The owner's spot-check helper: one grade-A site at a time, keyboard checks, autosave in the browser, CSV export (see `docs/spotcheck_guide.md`) |
| `data/interim/phase2_report_inventory.csv` | The 15 reports downloaded in Phase 2: URL, SHA-256 and text-layer measures |
| `data/interim/readability_calibration.csv` | Readability shares of the 35 Phase 0 calibration files (amendment A1) |
| `data/interim/readability.csv` | Readability share and pass/fail for all 107 report files, originals and OCR copies |
| `data/interim/readability_pages.csv` | A2: share of pages below 0.20 for each of the 83 original files, and whether A2 triggers OCR |
| `data/interim/a2_ocr_text_loss.csv` | The 42 pages where forced OCR lost text the original layer had |
| `data/interim/text/` | A3: one merged text file per report with an OCR copy (24), with a marker before each page |
| `data/interim/text_sources.csv` | A4 (earlier A3): one row per page (2,423), giving the original and OCR shares and token counts, the source used and any flag. The A3 versions are kept as `text_sources_a3.csv` and `readability_merged_a3.csv` |
| `data/interim/readability_merged.csv` | Readability of the 24 merged texts |
| `data/interim/phase2_ocr_log.csv` | The 24 OCR runs: original and OCR-copy SHA-256, options, run time and tool versions |
| `data/interim/phase2_ocr_qc.csv` | The OCR quality check: 2 random pages per OCR'd file, compared with the page image |
| `data/interim/ngx_census_frame.csv` | Updated with document-test results, report file, cover text and principal-activity quote with page |
| `docs/manual_download_list.md` | The 15 robustness firms still without a report, plus other files still needed |

**Scripts added in update 3:** `src/phase2_ocr.py` (OCR), `src/phase2_ocr_qc.py` (draws the QC pages, seed 20261111) and `src/phase2_identity_round3.py` (census-frame update). `src/phase2_build_facilities.py` and `src/phase2_coordinates.py` were extended. Update 4 added `src/readability.py` (`calibrate`, `run`). Update 5 added `readability.py pages` (A2), `src/text_select.py` (A3) and `src/phase2_osm_extract.py` (the Geofabrik lookup). `phase2_outputs.py` now keeps any owner checks already entered in `spotcheck_gradeA.csv` when it rebuilds the file. Run order: `readability.py pages`, `phase2_ocr.py`, `readability.py run`, `text_select.py`, `phase2_identity_round3.py`, `phase2_build_facilities.py`, `phase2_coordinates.py assign`, `phase2_coordinates.py finalize`, `phase2_outputs.py`. Do not re-run `phase2_verify_identity.py` after `phase2_identity_round3.py`: it predates the owner rounds and would reset their firms to "pending".

## 1. Document test (task 1)

Pass rule: a full-year report for 2023–2025 is in hand. Financial-statement-only filings pass, with document type recorded (owner decision).

| Stratum | Firms | Passed | Failed | Pending owner download |
|---|---|---|---|---|
| Main census | 59 | 56 | 3 (AUSTINLAZ, PHARMDEKO, PREMPAINTS) | 0 |
| Robustness stratum | 18 | 3 | 0 | 15 (skipped this round) |

**The main census has 56 firms with a report in hand.** PREMPAINTS failed by owner decision on 2026-11-12: "report not obtainable".

**Passed in update 3 (19 firms).** Document types and fiscal years, from the cover or directors' report:

| Ticker | Document | Fiscal year end |
|---|---|---|
| AIRTELAFRI | Annual report and accounts (UK plc; Nigerian operations through Airtel Networks Limited) | 31 Mar 2025 |
| ALEX | Financial statements (scan) | 31 Dec 2024 |
| CAP | Annual report | 31 Dec 2025 |
| CHAMPION | Annual report and financial statements | 31 Dec 2025 |
| ETERNA | Annual report and financial statements (scan) | 31 Dec 2025 |
| EUNISELL | Annual financial statements | 30 Jun 2025 |
| GEREGU | Annual report and financial statements (scan) | 31 Dec 2024 |
| GOLDBREW | Financial statements | 31 Mar 2024 |
| IMG | Annual report and financial statements | 31 Dec 2025 |
| JAPAULGOLD | Consolidated and separate financial statements | 31 Dec 2025 |
| JBERGER | Annual report | 31 Dec 2025 |
| MCNICHOLS | Financial statements (scan) | 31 Dec 2025 |
| MECURE | Annual report and financial statements | 31 Dec 2025 |
| MULTITREX | Reports and financial statements (20 of 57 pages are images without text) | 30 Apr 2024 |
| OANDO | Audited consolidated and separate financial statements | 31 Dec 2025 |
| TOTAL | Audited financial statements with directors' report | 31 Dec 2025 |
| TRANSPOWER | Annual reports and accounts | 31 Dec 2025 |
| TRIPPLEG | Financial statements | 31 Mar 2025 |
| UNIONDICON | Statements of audited accounts (scan) | 31 Dec 2025 |

**Okomu** now passes on its FY2024 annual report (OCR copy). Earlier it passed on FY2022, because FY2023 and FY2024 had no text layer.

**Earlier rounds:**

- **Downloaded in Phase 2 (15):** 14 from doclib.ngxgroup.com (FTNCOCOA, CONOIL, NASCON, VITAFOAM, NEIMETH, CUTIX, BERGER, PZ, MAYBAKER, MORISON, HONYFLOUR, TRANSCORP, ABCTRANS, RTBRISCOE) and DANGSUGAR from the company's own site. NASCON, PZ, HONYFLOUR and ABCTRANS are titled "annual report and financial statements"; the other 11 are financial statements with a directors' report. Fiscal years ending outside December: CUTIX (30 Apr 2025), PZ (31 May 2025), VITAFOAM (30 Sep 2025), HONYFLOUR (31 Mar 2025).
- **LIVESTOCK:** FY2025 annual report, 132 pages, with a text layer.
- **THOMASWY:** FY2025 report (year to 31 Mar 2025), 57 pages, scanned; now OCR'd.

## 2. Identity and sector (task 2)

For every firm with a report in hand, `ngx_census_frame.csv` records:

- the issuer name as printed on the report (for OCR'd files, from the OCR copy). Where the first page does not name the issuer, the first page that does is used, marked "(pN)"
- the first principal-activity statement, with its PDF page

**All 22 firms handled in update 3 have a principal-activity statement** (the 19 new firms, plus Ellah Lakes, Multiverse and Okomu). For the OCR'd files the quote was checked against the page image and is given as printed. For Thomas Wyatt it is unchanged from the page-image reading.

**Still flagged for a manual check:** five firms have identity confirmed from the cover page, but text search found no principal-activity sentence: DANGCEM, LIVESTOCK, MAYBAKER, MORISON and NESTLE.

**Sector:** no report read prints its NGX sector label. Sector is therefore recorded as "activity-based (report p.N); NGX sector label not stated in report".

### 2a. Readability test and OCR quality check

**Readability test: done (amendment A1).** Method: the share of word tokens that are among wordfreq's 1,000 most common English words, over the whole document (`src/readability.py`); a file passes at 0.25 or more.

**Calibration** (`data/interim/readability_calibration.csv`), on the 35 Phase 0 files with a text layer:

| File | Share |
|---|---|
| Unilever 2025 | 0.0095 |
| BUA Cement 2024 | 0.2807 |
| All other 33 files | 0.459 to 0.636 |

The proposed 0.30 would also fail BUA Cement 2024. That file's text layer is partly garbled: 36 of its 148 pages are below 0.20. The threshold was therefore set to 0.25, the highest multiple of 0.05 that fails Unilever and passes all the others.

**Corpus run** (`data/interim/readability.csv`, re-run in update 5): 107 files, of which 98 pass and 9 fail.

- **The failures** are 8 originals with no text layer (Okomu FY2020, FY2023 and FY2024; Thomas Wyatt; Multiverse; McNichols; Eterna; Alex) and Unilever 2025's garbled original. All 9 have OCR copies.
- **All 24 OCR copies pass,** with shares from 0.519 (Champion) to 0.591 (Geregu).
- **Garbled originals are fixed.** BUA Cement 2024 rises from 0.281 to 0.541, and Unilever 2025 from 0.0095 to 0.541.
- **Born-digital files caught by A2 score slightly lower after OCR.** Champion drops from 0.559 to 0.519, Academy from 0.581 to 0.551, and Guinness by about 0.01–0.02.
- **Close to the threshold:** BUA Cement 2024 (0.2807) and Geregu's original (0.25, on 4 watermark words).
- **Passes that mean nothing:** Geregu, Union Dicon and Ellah Lakes' originals pass on almost no text. Their OCR copies are used.

### 2b. Page-level text selection (A3, refined by A4 and A5; final)

**A4 rule** (`src/text_select.py`), for each page of the 24 reports with an OCR copy:

1. Use the version (original or OCR) with the higher common-word share; on equal shares, the original.
2. If that version has fewer than half the word tokens of the other version, use the other one, but only if the other version's share is at least 0.20 (A5).
3. If both shares are below 0.20, use the higher-share version and flag the page.

**Results:**

- **Pages:** 2,423 in all; 1,029 use the original text and 1,394 the OCR text.
- **Flags:** 82 pages have both versions below 0.20 (26 with no text in either). 9 pages were decided by the token-count rule. No page uses a version scoring below 0.20 when the other version scores 0.20 or more.
- **Readability:** all 24 merged texts pass the A1 threshold, with shares from 0.524 (Eterna) to 0.591 (Union Dicon and Geregu). The A3 and A4 versions are kept as `text_sources_a3.csv`/`_a4.csv` and `readability_merged_a3.csv`/`_a4.csv`.
- **Text-loss pages:** 41 of the 42 pages in `a2_ocr_text_loss.csv` use the original text. The exception is Lafarge p25, where OCR lost only figures: its word-token counts are 115 (original) and 108 (OCR), and its OCR share is slightly higher.

**Changes from A3 to A4** (291 pages switched; shares are for the merged text):

| Report | Pages switched | Share A3 → A4 |
|---|---|---|
| BUA Cement 2024 | 88 original → OCR | 0.382 → 0.541 |
| Academy 2025 | 39 original → OCR | 0.583 → 0.586 |
| Guinness 2022 | 32 original → OCR | 0.582 → 0.583 |
| Champion 2025 | 28 original → OCR | 0.547 → 0.549 |
| Guinness 2021 | 20 original → OCR | 0.581 → 0.578 |
| Guinness 2020 | 19 original → OCR | 0.586 → 0.586 |
| Guinness 2024 | 17 original → OCR | 0.579 → 0.576 |
| Nigerian Breweries 2025 | 16 original → OCR | 0.563 → 0.565 |
| Unilever 2025 | 3 original → OCR, 7 OCR → original | 0.538 → 0.530 |
| Lafarge 2023 | 8 original → OCR | 0.585 → 0.585 |
| IMG 2025 | 6 original → OCR | 0.584 → 0.585 |
| RT Briscoe 2025 | 5 original → OCR | 0.581 → 0.581 |
| Ellah Lakes, Union Dicon, Geregu | 1 original → OCR each | essentially unchanged |
| The other 8 reports | 0 | unchanged |

**Unilever 2025 under A4, resolved by A5.** Under A4, the token-count rule selected Unilever's garbled original on 7 pages, because its junk tokens inflated its token count. A5 removed this: those pages now use the OCR text.

**OCR quality check: done** (design f2: 2 random pages per OCR'd document, read against the page image). The pages were drawn with `src/phase2_ocr_qc.py` (seed 20261111); 48 pages across the 24 OCR copies. Results are in `data/interim/phase2_ocr_qc.csv`:

| Result | Pages | Files |
|---|---|---|
| Good | 38 | All files except as listed below |
| Fair | 6 | Multiverse (2: digit errors), McNichols (1: separators), Eterna (1: letter errors), Okomu 2020 (1: table values partly missed), Nigerian Breweries (1: chart numbers) |
| Poor | 3 | Eterna p24 (small-font table); Multi-Trex p22 (photographed balance sheet); Champion p63 (a clean digital page lost: 62 of 3,980 characters) |
| No text on page | 1 | Thomas Wyatt p57 (blank back page) |

- **Eterna is the weakest OCR copy.** Its quotes used here were read from the page image.
- **Multiverse is usable for words but not for numbers.** Its scan is 72 dpi.
- **Settings.** A first OCR run at native resolution read badly. Most scans are 72 dpi, and the Multiverse text came out as "quing", "efning". All files were re-run with `--oversample 300` (see `docs/data_sources.md`).

## 3. Facilities (task 3)

There are 214 facilities across 59 firms: 14 pilot firms, 15 Phase 2 firms, LIVESTOCK, THOMASWY, 9 firms from update 2 and 19 from update 3. Flour Mills is excluded and kept as a methods note.

| | All | Operational (offices excluded) |
|---|---|---|
| Facilities | 214 | 153 |
| Grade A | 87 | 30 |
| Grade B | 62 | 58 |
| Grade C | 14 | 14 |
| Grade D | 51 | 51 |
| Point sites | 195 | 134 |
| Dispersed assets | 19 | 19 |
| Main census / robustness stratum | 203 / 11 | |

**Operational facilities by firm (A / B / C / D).** RTBRISCOE has only its registered office, so it is not listed.

| Firm | A | B | C | D |
|---|---|---|---|---|
| ABCTRANS (robustness) | 2 | 1 | 0 | 1 |
| ACADEMY | 1 | 0 | 0 | 0 |
| AIRTELAFRI | 0 | 0 | 0 | 2 |
| ALEX | 0 | 2 | 0 | 0 |
| ARADEL | 0 | 1 | 0 | 3 |
| BERGER | 0 | 0 | 0 | 1 |
| BETAGLAS | 0 | 2 | 0 | 0 |
| BUACEMENT | 2 | 2 | 0 | 1 |
| BUAFOODS | 6 | 1 | 0 | 0 |
| CADBURY | 0 | 0 | 0 | 1 |
| CAP | 0 | 0 | 0 | 1 |
| CHAMPION | 0 | 0 | 0 | 1 |
| CONOIL | 0 | 0 | 1 | 1 |
| CUTIX | 1 | 0 | 0 | 0 |
| DANGCEM | 0 | 7 | 0 | 1 |
| DANGSUGAR | 0 | 1 | 3 | 0 |
| ELLAHLAKES | 0 | 2 | 1 | 0 |
| ENAMELWA | 0 | 0 | 0 | 1 |
| ETERNA | 0 | 1 | 1 | 1 |
| EUNISELL | 0 | 0 | 0 | 1 |
| FIDSON | 1 | 0 | 0 | 0 |
| FTNCOCOA | 1 | 0 | 0 | 0 |
| GEREGU | 0 | 1 | 0 | 0 |
| GOLDBREW | 0 | 0 | 0 | 1 |
| GUINNESS | 2 | 1 | 0 | 0 |
| HBMNG | 0 | 4 | 0 | 0 |
| HONYFLOUR | 1 | 2 | 0 | 0 |
| IMG | 0 | 0 | 0 | 1 |
| INTBREW | 0 | 0 | 0 | 1 |
| JAPAULGOLD | 0 | 1 | 0 | 0 |
| JBERGER | 0 | 0 | 0 | 1 |
| LIVESTOCK | 0 | 2 | 0 | 1 |
| MAYBAKER | 0 | 3 | 0 | 1 |
| MCNICHOLS | 0 | 0 | 0 | 1 |
| MECURE | 0 | 0 | 0 | 1 |
| MEYER | 0 | 0 | 0 | 1 |
| MORISON | 0 | 0 | 0 | 1 |
| MTNN | 0 | 0 | 0 | 3 |
| MULTITREX | 0 | 0 | 0 | 1 |
| MULTIVERSE | 0 | 2 | 0 | 0 |
| NASCON | 0 | 0 | 0 | 1 |
| NB | 10 | 2 | 0 | 0 |
| NEIMETH | 0 | 2 | 0 | 0 |
| NESTLE | 0 | 3 | 0 | 0 |
| NNFM | 1 | 0 | 0 | 0 |
| OANDO | 0 | 1 | 0 | 1 |
| OKOMUOIL | 0 | 1 | 1 | 2 |
| PRESCO | 1 | 0 | 6 | 1 |
| PZ | 0 | 0 | 0 | 2 |
| SEPLAT | 0 | 4 | 0 | 7 |
| THOMASWY | 0 | 0 | 0 | 1 |
| TOTAL | 0 | 0 | 1 | 2 |
| TRANSCORP (robustness) | 0 | 3 | 0 | 1 |
| TRANSPOWER | 1 | 0 | 0 | 0 |
| TRIPPLEG | 0 | 0 | 0 | 1 |
| UNILEVER | 0 | 2 | 0 | 1 |
| UNIONDICON | 0 | 0 | 0 | 1 |
| VITAFOAM | 0 | 4 | 0 | 0 |

**Notes on update 3:**

- **Plant locations not stated (grade D).** Eleven new firms give an office address but do not say where the plant is: CHAMPION, GOLDBREW, EUNISELL, IMG, MECURE, MULTITREX, TRIPPLEG, CAP, MCNICHOLS, UNIONDICON, and the lubricant plant of TOTAL. In several, the plant is probably at the registered office (for example, Champion's at "Industrial Layout, Aka Offot, Uyo"), but the report does not say so. Under the frozen rules that is grade D, with the office recorded separately.
- **Located plants:**
  - **Transcorp Power:** grade A, at "KM 20 Warri/Patani Expressway Ughelli Delta State". This is the same plant as TRANSCORP's grade-D row, whose parent filing gives no location; both rows are kept, one per firm.
  - **Geregu:** grade B, at "Itobe-Ajaokuta Expressway … Ajaokuta, Kogi State" (no street number).
  - **Alex:** grade B, plants at Inyishi near Owerri (Imo) and a leased powder-coating plant at Suleja (Niger).
  - **Multiverse:** grade B, a quarry at Alagunten (Ogun) and lead-zinc mines at Abuni (Nasarawa). These are named only in the auditor's key audit matter.
  - **Ellah Lakes:** grade B, farms at Iguelaba (Edo), with a CPO mill being installed, and Adani (Enugu). Its 5,000 ha in Ondo State is grade C.
  - **Japaul:** grade B, a gold mining site at Libeli, Kontagora LGA (Niger), where mining is due to start in 2026.
  - **Oando:** grade B, the Kwale-Okpai power plant; the town is taken from the plant name.
  - **Eterna:** grade B, tank farms at "Ibru Jetty, Ibafon, Apapa".
- **TotalEnergies' station network.** The "List of major distributors" (pp. 92–96) has a STATE column for 129 stations. It is recorded as one dispersed asset (grade C) with 35 states as written: every state except Bayelsa and Sokoto, plus FCT. The report gives 511 stations in all, so the list is a subset.
- **Not entered:**
  - Julius Berger's construction project sites, which are temporary client works. Its site yards are not named (one dispersed D row).
  - Total's seven sales area offices.
  - Oando's Alausa Power, which was disposed of in 2017.
  - Lubricants that Eterna Industries, a related company, blends for Eterna.
- **Okomu.** The FY2024 annual report states the same four sites as before, so the grades are unchanged and the rows now cite FY2024. The rows are the main estate at Okomu-Udo (B), Extension 1 (D), Extension 2 in Ovia NE/Uhunmwonde LGAs (C) and the rubber factory (D).

**Notes from earlier rounds** (unchanged): BERGER, PZ, NASCON, MORISON and MAYBAKER give no plant location. Conoil's dealer stations are one dispersed asset with nine states. Dangote Sugar's three estates are grade C. Cutix's registered office and factory share one grade-A address. Transcorp's Afam Power and Port Harcourt hotel take the town from the subsidiary name (grade B).

## 4. Coordinates (task 4, OD-1)

There is no web geocoding service. Coordinates come only from OpenStreetMap. Before update 3, they came from Overpass queries made within its usage policy, at least 10 seconds apart:

| Query | Result |
|---|---|
| Places matching the 61 place names in the location text | 88 elements |
| Company-named features (30 name patterns) | 64 elements |
| State check: the state for each assigned point | 87 results. A first, larger version returned HTTP 502; a version with a syntax error returned HTTP 400 and was corrected |
| Update 2: places Lafiagi and Obanikoro; state check for 2 points | 3 elements; 2 results |
| Update 4: `places3` on overpass-api.de (and one retry) | HTTP 502 twice |
| Update 5: `places3` on overpass.private.coffee | HTTP 504 |

**Update 3: no Overpass query.** The network was down on 2026-11-11, so no query was made.

**Update 4: query attempted but not completed.** The owner-approved `places3` query for the 18 names returned HTTP 502 ("server at capacity") at 05:58 UTC on 2026-11-12, and again on one retry at 06:02. The step was stopped as instructed, and no state check was made. New facilities got a coordinate only when their place name was already in the cached OSM data: Victoria Island, Ikeja, Ikoyi, Apapa, Banana Island, Benin City and Ughelli. That gave 11 new points, all consistent with the reported state.

**Update 5: Geofabrik extract (place nodes).** After the alternative instance failed, the owner's fallback was used. The Geofabrik Nigeria extract (`nigeria-latest.osm.pbf`, data up to 2026-11-11T21:22:47Z, SHA-256 `44dc394e…2afa`) was downloaded once. Place nodes and admin_level=4 boundaries were read locally with pyosmium (`src/phase2_osm_extract.py`), and the same matching rules were applied.

- **Matched (9 points; all consistent with the reported state):**

  | Place | Facilities | OSM tag |
  |---|---|---|
  | Uyo | Champion office | city |
  | Umuahia | Golden Guinea office | city |
  | Oshodi | IMG and Mecure offices | town |
  | Agidingbi | Japaul office | suburb |
  | Libeli | Japaul gold site | village |
  | Adani | Ellah Lakes farm | town |
  | Suleja | Alex plant | village |
  | Ajaokuta | Geregu plant | town; the only town among 2 places with that name |

  OSM tags Suleja as a village, so its nominal precision is 2 km.
- **No place node with these names (10 names):** Warewa, Abule Oshun, Okpai, Utako, Iguelaba, Alagunten, Abuni, Arepo, Inyishi and Ibafon.

**Update 6: named ways and relations** (owner decision; `src/phase2_osm_extract.py named`, same extract). The 10 names were searched among all OSM ways and relations with an exact `name` match. Each match's centroid comes from its assembled geometry, and its OSM type and id are recorded. Candidates went through the same matching rules and then a local state check (`states_check4.json`).

- **Utako:** one match, `relation/12207339`, an administrative-area relation (boundary=administrative) in FCT. It is unique, so it was assigned to Julius Berger's registered office (F0191), with nominal precision 2 km (a new class, "admin_area"). It is consistent with FCT.
- **No OSM feature of any type** with these names: Warewa, Abule Oshun, Okpai, Iguelaba, Alagunten, Abuni, Arepo, Inyishi and Ibafon. Their sites stay without coordinates.

**Rules applied.** These are implementation choices within OD-1 and are recorded per row:

1. **`osm_feature` (17 facilities):** an OSM feature checked by the analyst as matching the firm and site.
2. **`osm_place` (73):** the only OSM place with the name in the location text, or several same-named places all within 5 km of each other.
3. **`osm_place_rank` (35):** the only city or town among several same-named places.
4. **No coordinate (88):** grade C or D, dispersed assets, or an ambiguous or missing OSM match.
5. **State cross-check:** 89 assigned points are consistent with the state named in the report, and 36 have no state in the report to check against. **One was withdrawn:** Conoil's "Bull Plaza 38/39 Marina Lagos" had matched the only OSM place named "Marina", which is in Kebbi State.

**Precision values** (feature 250 m, suburb 2 km, town 5 km, city 10 km) are nominal classes, not measured errors.

**Most grade-A addresses are located only to a suburb or town centroid.** The grade describes the report's wording, not coordinate accuracy. Under A6, such sites are labelled `approximate (rule-based)` and get a Phase 3 buffer equal to their nominal precision instead of 500 m.

**States of the 74 operational sites with coordinates** (the OSM state of each point): Lagos 14, Ogun 10, Rivers 8, Edo 5, Abia 5, Delta 4, FCT 4, Kano 4, Anambra 3, Kogi 2, Benue 2, Sokoto 2, Enugu 2, Niger 2, and one each in Osun, Cross River, Oyo, Akwa Ibom, Adamawa, Plateau and Kwara.

## 5. Dispersed assets (task 5)

There are 19 dispersed assets. States were assigned in the frozen priority order:

1. **The company's own reports.**
   - **Conoil:** the dealer network covers nine states (pp. 8–9).
   - **TotalEnergies (new):** the major-distributor table covers 35 states (pp. 92–96).
   - **No states found:** Seplat's licences, MTN's base stations and switching centres, Oando's producing licences (OML 56, OML 13, OML 60–63), Aradel's Ogbele Field and OML 17, Airtel's Nigerian network, Julius Berger's site yards, Eterna's owned stations, and the depots or terminals of Dangote, PZ, Conoil, TotalEnergies and ABC Transport.
2. **Global Energy Monitor: not used.** Its licence has not been verified yet.
3. **Regulator records (NUPRC, NCC): not yet checked.**

**Status:** 2 of 19 dispersed assets have states assigned. The other 17 are **pending**.

## 6. Coverage gaps

- **15 robustness firms have no report in hand.** PREMPAINTS failed the document test.
- **Forced OCR lost text on 42 born-digital pages.** A3 avoids using those OCR pages, but the cause inside OCRmyPDF is unexplained.
- **Grade A or B point sites without a coordinate: 27** (17 operational, 10 offices). Nine update-3 place names have no OSM feature at all: Warewa, Abule Oshun, Okpai, Iguelaba, Alagunten, Abuni, Arepo, Inyishi and Ibafon.
- **Many filings do not say where the plant is.** Grade D rows come mostly from financial-statement filings, and in update 3 also from short annual reports.
- **Multi-Trex:** its 20 image-only pages are now OCR'd, and no plant address is on them. Its photographed balance sheet (p22) did not OCR.
- **Dispersed assets have almost no state information.**

## 7. Documents and decisions still needed from the owner

- **Sites without coordinates:** for the 9 place names with no OSM feature, the owner can place the sites by hand with `M` in the spot-check helper (grade-A sites only). Grade-B sites have no such tool yet.
- **Pending before Phase 6:** IFRS S2, Seplat's 2023 Sustainability Report and Seplat's 2025 Social Performance Report.
- **Grade-A location check:** done by rule (A6); no owner spot-check is needed. The 13 grade-A sites without a coordinate are not scored in Phase 3.
- **Sensitivity check:** A6 does not say whether Phase 3 should also report results with the original 500 m buffer for all grade-A sites with a coordinate. This is optional.
