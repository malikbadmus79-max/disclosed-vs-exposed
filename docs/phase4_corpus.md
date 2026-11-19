# Phase 4, steps 1–2: Corpus inventory, segmentation, text repairs and section tagging

**Date:** 2026-11-17. Step 1 (sections 1–4) follows `docs/design.md` (sections b, c, f1–f3) and `config/parameters.json`, with no amendment. **Step 2 (section 5)** logged amendments **A12–A15**, each before it was applied:
- **A12:** an OCR trigger for run-together text (LIVESTOCK).
- **A13:** ligature repair.
- **A14:** rule-based section tagging with analyst review.
- **A15:** control characters read as spaces.

Sections 1–4 keep the step-1 figures; section 5 gives the step-2 figures and corrects two step-1 statements. **Step 3 (section 6)** processed the 25 tier-1 files from owner batches 1–5 under the same rules and A16; **section 6 gives the current figures** (107 documents).

**Not done in steps 1–3.** ClimateBERT was not run. No dictionary was applied, no climate term was counted and no disclosure measure (Y1–Y5) was computed. The ClimateBERT *tokenizer* was loaded from the local cache (`data/raw/hf_cache/`, `local_files_only`) only to count tokens for the f3 512-token split; the model weights were not loaded. No file was downloaded.

**Code:** `src/phase4_corpus.py` (`inventory`, `segment`, `summary`) and `src/phase4_sections.py` (`tag`, `apply`, `headings`). LIVESTOCK's OCR used `src/phase2_ocr.py`; its page selection used `src/text_select.py`.

## Outputs

| File | Content |
|---|---|
| `data/interim/phase4_documents.csv` | One row per report document held for a census firm (107 after step 3; 82 in steps 1–2): firm, stratum, fiscal year, document type, file, OCR copy, text route, pages, listing date and `h3_main` (A16) |
| `data/interim/phase4_firm_year.csv` | Firm × fiscal year (FY2020–FY2025) table of the document types held, for the 59 main and 18 robustness firms; `years_h3_main` counts A16 main-analysis years |
| `data/interim/phase4_download_list.csv` | Firm-years and documents the design still needs, with priority and lead URL |
| `data/interim/paragraphs.csv` | One row per paragraph (or split piece): `firm, year, doc, doc_type, page, page_source, paragraph_id, parent_paragraph_id, piece, font_size, n_words, n_tokens, model_eligible, duplicate_of, text` |
| `data/interim/phase4_doc_stats.csv` | Per-document segmentation statistics and broken-text checks (current, after step 2) |
| `data/interim/phase4_minimum_download_list.csv` | Step 2: the minimum download list for the confirmatory tests (section 5.1) |
| `data/interim/ligature_repairs.csv` | Step 2 (A13): every ligature repair (document, page, before, after) |
| `data/interim/section_tags.csv` | Step 2 (A14): the financial-statement page range per document, with start and end evidence, method and flag |

Step 2 also added a `section` column to `paragraphs.csv` (`narrative` or `financial_statements`).

## 1. Inventory

**Which documents count.** Every report PDF on disk for a census firm: `data/raw/pilot_reports/`, `data/raw/phase2_reports/` and the firm subfolders of `data/raw/manual/`.
- The six loose files at the top of `data/raw/manual/` are excluded; `docs/data_sources.md` records them as byte-identical duplicates of subfolder copies.
- `flour_mills/2024_FS.pdf` is excluded: Flour Mills was delisted and is kept only as a methods note (c, rule 2).
- **Text route.** The 24 documents with an OCR copy take each page from the source chosen under A3–A5 (`text_sources.csv`, which feeds `data/interim/text/`). The other 58 use the original text layer; all passed the A1 readability check.

**Fiscal year** is the label in the Phase 0/2 inventories and the census notes, which follow design b: the calendar year in which the fiscal year ends. Examples: Airtel's year to 31 March 2025 is FY2025; Ellah Lakes' year to 31 July 2024 is FY2024.

**Document types** (f1):

| Code | Meaning | Documents |
|---|---|---|
| AR | Full annual report | 47 |
| IAR | Integrated report | 1 |
| SR | Sustainability report | 2 |
| SRX | Sustainability extract | 2 |
| FS | Financial-statement filing, as labelled at download or in the census note | 30 |

Many FS filings include a directors' report. Whether a filing is "FS-only" in the f1 sense (no narrative) is settled during section tagging, which is still to do.

**Totals:** 82 documents, 8,904 pages. By fiscal year: FY2020 4, FY2021 3, FY2022 5, FY2023 7, FY2024 12, FY2025 51.

### Firm × year table

`·` = no document. `AR+SRX` = an annual report and a sustainability extract for that year. Test = the c document test.

**Main census (59 firms)**

| Firm | Test | FY2020 | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---|---|---|---|---|---|---|
| ACADEMY | passed | · | · | · | · | · | AR |
| AIRTELAFRI | passed | · | · | · | · | · | AR |
| ALEX | passed | · | · | · | · | FS | · |
| ARADEL | passed | · | · | · | · | · | AR |
| AUSTINLAZ | failed | · | · | · | · | · | · |
| BERGER | passed | · | · | · | · | · | FS |
| BETAGLAS | passed | · | · | · | AR | · | · |
| BUACEMENT | passed | AR | AR | AR | AR | AR | AR |
| BUAFOODS | passed | · | · | · | · | AR | · |
| CADBURY | passed | · | · | FS | · | · | FS |
| CAP | passed | · | · | · | · | · | AR |
| CHAMPION | passed | · | · | · | · | · | AR |
| CONOIL | passed | · | · | · | · | · | FS |
| CUTIX | passed | · | · | · | · | · | FS |
| DANGCEM | passed | AR | · | AR | AR | AR+SRX | AR+SRX |
| DANGSUGAR | passed | · | · | · | · | · | FS |
| ELLAHLAKES | passed | · | · | · | · | FS | · |
| ENAMELWA | passed | · | · | · | · | · | AR |
| ETERNA | passed | · | · | · | · | · | AR |
| EUNISELL | passed | · | · | · | · | · | FS |
| FIDSON | passed | · | · | · | · | · | AR |
| FTNCOCOA | passed | · | · | · | · | · | FS |
| GEREGU | passed | · | · | · | · | AR | · |
| GOLDBREW | passed | · | · | · | · | FS | · |
| GUINNESS | passed | AR | AR | AR | AR | AR | AR |
| HBMNG | passed | · | · | · | FS | · | · |
| HONYFLOUR | passed | · | · | · | · | · | FS |
| IMG | passed | · | · | · | · | · | AR |
| INTBREW | passed | · | · | · | FS | · | · |
| JAPAULGOLD | passed | · | · | · | · | · | FS |
| JBERGER | passed | · | · | · | · | · | AR |
| LIVESTOCK | passed | · | · | · | · | · | AR |
| MAYBAKER | passed | · | · | · | · | · | FS |
| MCNICHOLS | passed | · | · | · | · | · | FS |
| MECURE | passed | · | · | · | · | · | AR |
| MEYER | passed | · | · | · | · | · | AR |
| MORISON | passed | · | · | · | · | · | FS |
| MTNN | passed | · | · | · | · | · | AR+SR |
| MULTITREX | passed | · | · | · | · | AR | · |
| MULTIVERSE | passed | · | · | · | · | · | AR |
| NASCON | passed | · | · | · | · | · | FS |
| NB | passed | · | · | · | · | · | AR |
| NEIMETH | passed | · | · | · | · | · | FS |
| NESTLE | passed | · | · | · | · | · | AR |
| NNFM | passed | · | · | · | · | · | AR |
| OANDO | passed | · | · | · | · | · | FS |
| OKOMUOIL | passed | AR | AR | AR | AR | AR+SR | · |
| PHARMDEKO | failed | · | · | · | · | · | · |
| PREMPAINTS | failed | · | · | · | · | · | · |
| PRESCO | passed | · | · | · | · | · | AR |
| PZ | passed | · | · | · | · | · | FS |
| SEPLAT | passed | · | · | · | · | · | IAR |
| THOMASWY | passed | · | · | · | · | · | FS |
| TOTAL | passed | · | · | · | · | · | FS |
| TRANSPOWER | passed | · | · | · | · | · | AR |
| TRIPPLEG | passed | · | · | · | · | · | FS |
| UNILEVER | passed | · | · | · | · | · | AR |
| UNIONDICON | passed | · | · | · | · | · | FS |
| VITAFOAM | passed | · | · | · | · | · | FS |

**Robustness stratum (18 firms)**

| Firm | Test | FY2020 | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---|---|---|---|---|---|---|
| ABCTRANS | passed | · | · | · | · | · | FS |
| CAVERTON | pending | · | · | · | · | · | · |
| CHELLARAM | pending | · | · | · | · | · | · |
| EKOCORP | pending | · | · | · | · | · | · |
| IKEJAHOTEL | pending | · | · | · | · | · | · |
| JOHNHOLT | pending | · | · | · | · | · | · |
| JULI | pending | · | · | · | · | · | · |
| NAHCO | pending | · | · | · | · | · | · |
| REDSTAREX | pending | · | · | · | · | · | · |
| RTBRISCOE | passed | · | · | · | · | · | FS |
| SCOA | pending | · | · | · | · | · | · |
| SKYAVN | pending | · | · | · | · | · | · |
| TANTALIZER | pending | · | · | · | · | · | · |
| TRANSCOHOT | pending | · | · | · | · | · | · |
| TRANSCORP | passed | · | · | · | · | · | FS |
| TRANSEXPR | pending | · | · | · | · | · | · |
| UACN | pending | · | · | · | · | · | · |
| UPDC | pending | · | · | · | · | · | · |

### Gaps

| Group | Firms | Firm-years (×6) | With any document | With AR/IAR | FS filing only | **No document** |
|---|---|---|---|---|---|---|
| Main, passed the document test | 56 | 336 | 75 | 48 | 27 | **261** |
| Main, failed the document test (excluded, c rule 3) | 3 | 18 | 0 | 0 | 0 | 18 |
| Robustness, passed | 3 | 18 | 3 | 0 | 3 | 15 |
| Robustness, pending (owner: skipped for now) | 15 | 90 | 0 | 0 | 0 | 90 |

- **Main census:** 51 of the 56 firms that passed the document test have a single year. Two have 5 years (Dangote Cement, Okomu Oil) and two have all 6 (BUA Cement, Guinness). Years held: FY2020 4, FY2021 3, FY2022 5, FY2023 7, FY2024 10, FY2025 46.
- **Separate sustainability documents** are held for 3 firms only: Dangote Cement (extracts, FY2024–2025), MTN (FY2025) and Okomu (FY2024).
- The design says "Firms enter only for years with documents" (h). The gaps therefore do not block the analysis, but with one year for most firms the panel for the H3 year trend is thin, especially for 2020–2022.

## 2. Download list (for the owner)

The full list, with one row per firm-year, is `data/interim/phase4_download_list.csv`. It contains 404 rows:
- **Priority 1:** 105 main-census annual reports for FY2023–2025.
- **Priority 2:** 156 main-census annual reports for FY2020–2022, and 8 sustainability documents known to exist.
- **Priority 3:** 105 robustness-stratum annual reports.
- **Priority 4 (optional):** 30 firm-years where only an FS filing is held and a full annual report may exist.

**Lead URLs** are only those already recorded in earlier phases (the Phase 0 inventory), on the firm's own site, NGX doclib or a registrar. No new search was run. No africanfinancials.com URL is listed: its terms forbid automated access, and the earlier leads there are not repeated. "Not known" means no lead was recorded; the firm's investor-relations page and doclib.ngxgroup.com are the places to look.

### Main census: annual reports still needed

| Firm | Annual reports needed (FY) | Lead URL |
|---|---|---|
| ACADEMY | 2020, 2021, 2022, 2023, 2024 | not known |
| AIRTELAFRI | 2020, 2021, 2022, 2023, 2024 | not known |
| ALEX | 2020, 2021, 2022, 2023, 2025 | not known |
| ARADEL | 2020, 2021, 2022, 2023, 2024 | not known |
| BERGER | 2020, 2021, 2022, 2023, 2024 | not known |
| BETAGLAS | 2020, 2021, 2022, 2024, 2025 | not known |
| BUAFOODS | 2020, 2021, 2022, 2023, 2025 | not known |
| CADBURY | 2020, 2021, 2023, 2024 | not known |
| CAP | 2020, 2021, 2022, 2023, 2024 | not known |
| CHAMPION | 2020, 2021, 2022, 2023, 2024 | not known |
| CONOIL | 2020, 2021, 2022, 2023, 2024 | not known |
| CUTIX | 2020, 2021, 2022, 2023, 2024 | not known |
| DANGCEM | 2021 | not known |
| DANGSUGAR | 2020, 2021, 2022, 2023, 2024 | not known |
| ELLAHLAKES | 2020, 2021, 2022, 2023, 2025 | not known |
| ENAMELWA | 2020, 2021, 2022, 2023, 2024 | not known |
| ETERNA | 2020, 2021, 2022, 2023, 2024 | not known |
| EUNISELL | 2020, 2021, 2022, 2023, 2024 | not known |
| FIDSON | 2020, 2021, 2022, 2023, 2024 | not known |
| FTNCOCOA | 2020, 2021, 2022, 2023, 2024 | not known |
| GEREGU | 2020, 2021, 2022, 2023, 2025 | not known |
| GOLDBREW | 2020, 2021, 2022, 2023, 2025 | not known |
| HBMNG | 2020, 2021, 2022, 2024, 2025 | https://cardinalstoneregistrars.com/wp-content/uploads/2023/01/LAFARGE%202022%20ANNUAL%20REPORT%20AND%20ACCOUNTS.pdf; https://doclib.ngxgroup.com/Financial_NewsDocs/32658_LAFARGE_AFRICA_PLC%20_AUDITED_FINANCIAL_STATEMENT_FOR_2.pdf |
| HONYFLOUR | 2020, 2021, 2022, 2023, 2024 | not known |
| IMG | 2020, 2021, 2022, 2023, 2024 | not known |
| INTBREW | 2020, 2021, 2022, 2024, 2025 | https://doclib.ngxgroup.com/Financial_NewsDocs/38066_INTERNATIONAL_BREWERIES_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2022_FINANCIAL_STATEMENTS_MARCH_2023.pdf |
| JAPAULGOLD | 2020, 2021, 2022, 2023, 2024 | not known |
| JBERGER | 2020, 2021, 2022, 2023, 2024 | not known |
| LIVESTOCK | 2020, 2021, 2022, 2023, 2024 | not known |
| MAYBAKER | 2020, 2021, 2022, 2023, 2024 | not known |
| MCNICHOLS | 2020, 2021, 2022, 2023, 2024 | not known |
| MECURE | 2020, 2021, 2022, 2023, 2024 | not known |
| MEYER | 2020, 2021, 2022, 2023, 2024 | not known |
| MORISON | 2020, 2021, 2022, 2023, 2024 | not known |
| MTNN | 2020, 2021, 2022, 2023, 2024 | https://www.mtn.ng/wp-content/uploads/2022/11/MTN-Nigeria-Annual-Report-2020-2.pdf; https://www.mtn.ng/wp-content/uploads/2022/11/MTN-Nigeria-Annual-Report-2021-2.pdf; https://www.mtn.ng/wp-content/uploads/2023/07/MTN-Nigeria-Annual-Report-2022.pdf; https://www.mtn.ng/wp-content/uploads/2024/04/MTN-Nigeria-2023-Annual-Report.pdf; https://www.mtn.ng/wp-content/uploads/2025/04/MTN-Nigeria-2024-Annual-Report-3.pdf |
| MULTITREX | 2020, 2021, 2022, 2023, 2025 | not known |
| MULTIVERSE | 2020, 2021, 2022, 2023, 2024 | not known |
| NASCON | 2020, 2021, 2022, 2023, 2024 | not known |
| NB | 2020, 2021, 2022, 2023, 2024 | not known |
| NEIMETH | 2020, 2021, 2022, 2023, 2024 | not known |
| NESTLE | 2020, 2021, 2022, 2023, 2024 | not known |
| NNFM | 2020, 2021, 2022, 2023, 2024 | not known |
| OANDO | 2020, 2021, 2022, 2023, 2024 | not known |
| OKOMUOIL | 2025 | https://okomunigeria.com/wp-content/uploads/2026/05/2025-Annual-reports-and-accounts.pdf |
| PRESCO | 2020, 2021, 2022, 2023, 2024 | https://www.presco-plc.com/financial-reports/reports-20231/presco-plc-annual-report-and-accounts-2023/; https://www.presco-plc.com/financial-reports/reports-2024/presco-plc-2024-annual-reports-and-accounts/; https://www.presco-plc.com/investor-relations/2022-annual-general-meeting/presco-plc-annual-report-and-notice-of-annual-general-meeting/ |
| PZ | 2020, 2021, 2022, 2023, 2024 | not known |
| SEPLAT | 2020, 2021, 2022, 2023, 2024 | not known |
| THOMASWY | 2020, 2021, 2022, 2023, 2024 | not known |
| TOTAL | 2020, 2021, 2022, 2023, 2024 | not known |
| TRANSPOWER | 2020, 2021, 2022, 2023, 2024 | not known |
| TRIPPLEG | 2020, 2021, 2022, 2023, 2024 | not known |
| UNILEVER | 2020, 2021, 2022, 2023, 2024 | not known |
| UNIONDICON | 2020, 2021, 2022, 2023, 2024 | not known |
| VITAFOAM | 2020, 2021, 2022, 2023, 2024 | not known |

### Sustainability documents known to exist and not held

| Firm | FY | Document | Lead URL |
|---|---|---|---|
| MTNN | 2020 | sustainability report | https://www.mtn.ng/wp-content/uploads/2024/12/MTN-Nigeria-2020-Sustainability-Report-1.pdf |
| MTNN | 2021 | sustainability report | https://www.mtn.ng/wp-content/uploads/2024/12/MTN-Nigeria-2021-Sustainability-Report-1.pdf |
| MTNN | 2022 | sustainability report | https://www.mtn.ng/wp-content/uploads/2024/12/MTN-Nigeria-2022-Sustainability-Report-1.pdf |
| MTNN | 2023 | sustainability report | https://www.mtn.ng/wp-content/uploads/2024/12/MTN-Nigeria-2023-Sustainability-Report-1.pdf |
| MTNN | 2024 | sustainability report | https://www.mtn.ng/wp-content/uploads/2025/04/MTN-Nigeria-2024-Sustainability-Report.pdf |
| OKOMUOIL | 2022 | sustainability report | https://okomunigeria.com/wp-content/uploads/2024/07/2024-03-19-Sustainability-report_compressed.pdf |
| SEPLAT | 2023 | sustainability report | requested from owner (pending before Phase 6) |
| SEPLAT | 2025 | social performance report | requested from owner (pending before Phase 6) |

### Robustness stratum: annual reports still needed

| Firm | Annual reports needed (FY) | Note |
|---|---|---|
| ABCTRANS | 2020, 2021, 2022, 2023, 2024 |  |
| CAVERTON | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| CHELLARAM | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| EKOCORP | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| IKEJAHOTEL | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| JOHNHOLT | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| JULI | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| NAHCO | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| REDSTAREX | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| RTBRISCOE | 2020, 2021, 2022, 2023, 2024 |  |
| SCOA | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| SKYAVN | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| TANTALIZER | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| TRANSCOHOT | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| TRANSCORP | 2020, 2021, 2022, 2023, 2024 |  |
| TRANSEXPR | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| UACN | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |
| UPDC | 2020, 2021, 2022, 2023, 2024, 2025 | document test pending (owner: skipped for now) |

## 3. Paragraph segmentation (f3)

**Rule as implemented** (design f3; the thresholds below are not set in the design and are fixed here):

1. **Blocks:** PyMuPDF text blocks from `page.get_text("dict")`, dehyphenated, in the PDF's own block order. Lines are joined with spaces and the text is NFKC-normalised (f2). A block's font size is the character-weighted median of its span sizes, rounded to 0.5 pt.
2. **Merge** ("adjacent blocks with the same font size and no blank line between them are merged"). A block joins the previous one if all three hold:
   - **Same font size:** within 0.5 pt on original text layers, or within 1.0 pt on OCR pages, where Tesseract's sizes are estimates that vary line to line.
   - **No blank line:** the vertical gap is less than 0.8 × the font size. A blank line is about 1.2 × the font size; ordinary line spacing is 0.2–0.6 ×.
   - **Same column:** the two blocks overlap horizontally by at least half the narrower block.

   Merging never crosses a page boundary.
3. **Words:** whitespace tokens containing a letter or digit.
4. **Minimum length, 40 words:** shorter paragraphs are kept with `model_eligible = 0`, for the site-mention dictionary.
5. **Deduplication:** within a document, a repeat of an earlier paragraph (same text after lower-casing and collapsing spaces) gets `duplicate_of` set and `model_eligible = 0`. It stays in the file.
6. **Long paragraphs:** an eligible paragraph over 512 tokens (ClimateBERT tokenizer, special tokens included) is split at sentence ends (`. ! ?` followed by a space) into pieces of at most 512 tokens. A single sentence over the limit is split at word boundaries. Each piece is its own row (`piece` = 1, 2, …; `parent_paragraph_id` = the unsplit id).
7. **Not yet done (f1):** the hand-tagged section table that excludes the audited financial statements. All pages are kept, with page numbers, so that table can be applied before scoring.

**Calibration note.** The first trial used a 0.5 × gap and a 0.5 pt size tolerance everywhere. That left OCR pages broken into line-sized fragments: in Academy Press FY2025, 318 short blocks started mid-sentence and 53% of words were in eligible paragraphs. With the thresholds above, the figures are 120 and 69%. The thresholds were chosen by inspecting block geometry, before any climate content was looked at.

### Results (step 1; current figures in section 5.5)

| Measure | Value |
|---|---|
| Documents | 82 (8,904 pages) |
| Paragraph rows in `paragraphs.csv` | 138,738 |
| Model-eligible rows (≥ 40 words, not duplicates; split pieces counted separately) | **26,439** |
| Duplicate rows (repeated headers, footers and similar) | 25,401 |
| Short rows kept for the dictionary (< 40 words, not duplicates) | 86,898 |
| Eligible paragraphs over 512 tokens that were split | 758 (into 1,601 pieces) |
| **Median length, eligible rows** | **67 words** (IQR 51–98; maximum 433) |
| Median length, all rows | 8 words (headings, table cells, page furniture) |
| Share of words that fall in eligible paragraphs (per document) | median 69% (range 26–94%) |

### Documents that look broken or need attention

- **[Resolved in step 2: A12, A15; see 5.2]** **LIVESTOCK FY2025 AR: broken text layer.** The text has no spaces between words ("expansionoftheCompany'smarketposition…"); 2.9% of tokens are runs of 25 or more letters. Only 61 eligible paragraphs come from 132 pages, and 26% of words fall in eligible paragraphs. The file passed A1 at document level, and the A2 page rule did not trigger OCR. **Owner decision needed:** OCR it (A2-style) or accept it. As it stands, it would undercount this firm's narrative paragraphs.
- **[Resolved in step 2: A13; see 5.3. The private-use counts below are corrected there: only U+F001/U+F002 in Academy and LIVESTOCK are ligatures; the rest are bullets and check marks.]** **Lost ligatures (affects the dictionary step later).** f2 assumes NFKC fixes ligatures, but NFKC cannot help in two cases:
  - **Missing glyphs:** in some files the "fi" glyph is absent from the text layer. Academy Press FY2025 has about 58 such broken words, such as "nancial" for "financial".
  - **Private-use glyphs:** some files map the ligature to a private-use code point. Counts by document: AIRTELAFRI_2025_AR 814, MTNN_2025_AR 557, ACADEMY_2025_AR 299, DANGCEM_2020_AR 253, DANGCEM_2022_AR 192, LIVESTOCK_2025_AR 75, NASCON_2025_FS 71, VITAFOAM_2025_FS 65, ENAMELWA_2025_AR 37, DANGCEM_2024_AR 29, DANGSUGAR_2025_FS 25, DANGCEM_2025_AR 21, DANGCEM_2025_SRX 15, OANDO_2025_FS 14, DANGCEM_2023_AR 11, MORISON_2025_FS 6, FTNCOCOA_2025_FS 4, TRIPPLEG_2025_FS 4, NEIMETH_2025_FS 3.

  If an "fl" ligature is affected, words such as "flood" or "flooding" would be missed by the f4 hazard dictionary. This should be checked, and fixed if needed, before the dictionary is applied. **Any fix is a change to the f2 extraction step and may need an amendment;** nothing was changed here.
- **MTN FY2025 sustainability report:** a heavily designed layout. Only 48% of words fall in eligible paragraphs, because of text boxes, captions and infographics. It is not broken, but it yields fewer full paragraphs than its 174 pages suggest.
- **Financial-statement content.** Many eligible paragraphs are accounting notes or tables flattened into text. **[Done in step 2: A14; see 5.4.]**
- **No other flags:** none of the 82 documents has fewer than 20 eligible paragraphs, a common-word share below the A1 threshold (0.25) in its eligible text, more than 10% of pages without text, or a paragraph over 1,500 words.

### Per-document statistics (step 1)

| Document | Pages | Text route | Paragraph rows | Model-eligible | Median words (eligible) | Words in eligible paragraphs | Flags |
|---|---|---|---|---|---|---|---|
| ABCTRANS_2025_FS | 90 | original | 1,504 | 313 | 61 | 66% |  |
| ACADEMY_2025_AR | 112 | A3–A5 page selection | 1,679 | 329 | 65 | 69% |  |
| AIRTELAFRI_2025_AR | 268 | original | 5,610 | 1,257 | 66 | 73% |  |
| ALEX_2024_FS | 60 | A3–A5 page selection | 785 | 170 | 70 | 71% |  |
| ARADEL_2025_AR | 135 | original | 1,005 | 272 | 143 | 93% |  |
| BERGER_2025_FS | 80 | original | 1,290 | 208 | 59 | 57% |  |
| BETAGLAS_2023_AR | 108 | original | 1,898 | 317 | 61 | 64% |  |
| BUACEMENT_2020_AR | 66 | original | 1,794 | 386 | 62 | 71% |  |
| BUACEMENT_2021_AR | 142 | original | 1,950 | 383 | 62 | 70% |  |
| BUACEMENT_2022_AR | 152 | original | 1,664 | 370 | 71 | 81% |  |
| BUACEMENT_2023_AR | 160 | original | 1,876 | 450 | 66 | 77% |  |
| BUACEMENT_2024_AR | 148 | A3–A5 page selection | 3,538 | 465 | 58 | 59% |  |
| BUACEMENT_2025_AR | 79 | original | 1,046 | 361 | 87 | 87% |  |
| BUAFOODS_2024_AR | 70 | original | 1,357 | 224 | 57 | 60% |  |
| CADBURY_2022_FS | 26 | original | 400 | 99 | 65 | 71% |  |
| CADBURY_2025_FS | 28 | original | 470 | 116 | 70 | 71% |  |
| CAP_2025_AR | 87 | original | 1,429 | 305 | 63 | 67% |  |
| CHAMPION_2025_AR | 105 | A3–A5 page selection | 1,951 | 291 | 63 | 61% |  |
| CONOIL_2025_FS | 73 | original | 1,088 | 197 | 70 | 67% |  |
| CUTIX_2025_FS | 82 | original | 680 | 164 | 104 | 88% |  |
| DANGCEM_2020_AR | 260 | original | 3,787 | 680 | 106 | 83% |  |
| DANGCEM_2022_AR | 207 | original | 3,059 | 539 | 108 | 81% |  |
| DANGCEM_2023_AR | 208 | original | 2,960 | 544 | 105 | 81% |  |
| DANGCEM_2024_AR | 272 | original | 4,622 | 790 | 75 | 72% |  |
| DANGCEM_2024_SRX | 72 | original | 1,037 | 197 | 78 | 76% |  |
| DANGCEM_2025_AR | 236 | original | 4,605 | 811 | 68 | 71% |  |
| DANGCEM_2025_SRX | 52 | original | 996 | 159 | 71 | 68% |  |
| DANGSUGAR_2025_FS | 88 | original | 1,892 | 365 | 61 | 65% |  |
| ELLAHLAKES_2024_FS | 46 | A3–A5 page selection | 605 | 96 | 66 | 65% |  |
| ENAMELWA_2025_AR | 47 | original | 325 | 73 | 133 | 87% |  |
| ETERNA_2025_AR | 73 | A3–A5 page selection | 1,198 | 229 | 61 | 62% |  |
| EUNISELL_2025_FS | 39 | original | 606 | 85 | 64 | 58% |  |
| FIDSON_2025_AR | 87 | original | 1,472 | 213 | 64 | 60% |  |
| FTNCOCOA_2025_FS | 55 | original | 460 | 104 | 94 | 82% |  |
| GEREGU_2024_AR | 104 | A3–A5 page selection | 1,385 | 289 | 59 | 60% |  |
| GOLDBREW_2024_FS | 64 | original | 664 | 121 | 66 | 72% |  |
| GUINNESS_2020_AR | 152 | A3–A5 page selection | 1,434 | 459 | 68 | 80% |  |
| GUINNESS_2021_AR | 156 | A3–A5 page selection | 1,488 | 457 | 63 | 74% |  |
| GUINNESS_2022_AR | 170 | A3–A5 page selection | 1,766 | 515 | 66 | 73% |  |
| GUINNESS_2023_AR | 164 | original | 1,541 | 515 | 66 | 74% |  |
| GUINNESS_2024_AR | 163 | A3–A5 page selection | 1,716 | 509 | 64 | 73% |  |
| GUINNESS_2025_AR | 162 | original | 1,532 | 520 | 62 | 74% |  |
| HBMNG_2023_FS | 105 | A3–A5 page selection | 2,175 | 314 | 60 | 61% |  |
| HONYFLOUR_2025_FS | 118 | original | 1,637 | 298 | 60 | 64% |  |
| IMG_2025_AR | 71 | A3–A5 page selection | 1,385 | 223 | 68 | 65% |  |
| INTBREW_2023_FS | 57 | original | 1,127 | 237 | 64 | 69% |  |
| JAPAULGOLD_2025_FS | 84 | original | 1,275 | 212 | 61 | 61% |  |
| JBERGER_2025_AR | 89 | original | 2,438 | 488 | 60 | 68% |  |
| LIVESTOCK_2025_AR | 132 | original | 1,623 | 61 | 48 | 26% | missing word spaces: 2.9% of tokens are 25+ letters run together |
| MAYBAKER_2025_FS | 74 | original | 1,099 | 149 | 59 | 54% |  |
| MCNICHOLS_2025_FS | 52 | A3–A5 page selection | 1,134 | 119 | 69 | 57% |  |
| MECURE_2025_AR | 43 | original | 706 | 110 | 59 | 58% |  |
| MEYER_2025_AR | 66 | original | 988 | 167 | 63 | 59% |  |
| MORISON_2025_FS | 45 | original | 583 | 148 | 70 | 70% |  |
| MTNN_2025_AR | 167 | original | 4,910 | 878 | 63 | 65% |  |
| MTNN_2025_SR | 174 | original | 4,194 | 266 | 59 | 48% |  |
| MULTITREX_2024_AR | 57 | A3–A5 page selection | 355 | 101 | 81 | 86% |  |
| MULTIVERSE_2025_AR | 49 | A3–A5 page selection | 797 | 88 | 62 | 58% |  |
| NASCON_2025_FS | 73 | original | 1,160 | 204 | 58 | 64% |  |
| NB_2025_AR | 179 | A3–A5 page selection | 1,893 | 510 | 61 | 72% |  |
| NEIMETH_2025_FS | 66 | original | 801 | 222 | 66 | 69% |  |
| NESTLE_2025_AR | 182 | original | 2,135 | 339 | 80 | 78% |  |
| NNFM_2025_AR | 102 | original | 1,150 | 332 | 64 | 72% |  |
| OANDO_2025_FS | 113 | original | 3,067 | 637 | 73 | 70% |  |
| OKOMUOIL_2020_AR | 69 | A3–A5 page selection | 1,527 | 215 | 63 | 58% |  |
| OKOMUOIL_2021_AR | 46 | original | 2,063 | 258 | 64 | 63% |  |
| OKOMUOIL_2022_AR | 88 | original | 1,880 | 257 | 67 | 74% |  |
| OKOMUOIL_2023_AR | 96 | A3–A5 page selection | 1,514 | 289 | 62 | 62% |  |
| OKOMUOIL_2024_AR | 115 | A3–A5 page selection | 1,584 | 338 | 61 | 66% |  |
| OKOMUOIL_2024_SR | 48 | original | 582 | 115 | 58 | 72% |  |
| PRESCO_2025_AR | 119 | original | 2,338 | 380 | 64 | 66% |  |
| PZ_2025_FS | 84 | original | 1,427 | 338 | 64 | 73% |  |
| RTBRISCOE_2025_FS | 79 | A3–A5 page selection | 1,355 | 260 | 65 | 63% |  |
| SEPLAT_2025_IAR | 350 | original | 5,371 | 1,041 | 105 | 84% |  |
| THOMASWY_2025_FS | 57 | A3–A5 page selection | 721 | 178 | 56 | 67% |  |
| TOTAL_2025_FS | 98 | original | 1,766 | 344 | 68 | 70% |  |
| TRANSCORP_2025_FS | 138 | original | 917 | 253 | 140 | 94% |  |
| TRANSPOWER_2025_AR | 81 | original | 507 | 144 | 146 | 93% |  |
| TRIPPLEG_2025_FS | 57 | original | 326 | 118 | 60 | 75% |  |
| UNILEVER_2025_AR | 176 | A3–A5 page selection | 3,584 | 384 | 57 | 51% |  |
| UNIONDICON_2025_FS | 29 | A3–A5 page selection | 592 | 83 | 57 | 58% |  |
| VITAFOAM_2025_FS | 128 | original | 1,888 | 394 | 60 | 70% |  |

## 4. Next steps (superseded; see section 5.6)

## 5. Step 2 (2026-11-17)

### 5.1 Minimum downloads for the confirmatory tests (A)

**What the design needs** (`docs/design.md` h). The data are "the firm-year panel of the main census, 2020–2025. Firms enter only for years with documents."

- **H1 and H2** regress Y2 (and Y1–Y3 for H2) on firm exposure `E_i`, with year and sector fixed effects. A firm can enter only if it has an exposure score. Of the 56 main-census firms that passed the document test, **27 have a score** (29 scored firms in all; ABC Transport and Transcorp are robustness stratum).
  - All 27 already hold at least one firm-year with a document, so **no download is needed for any firm to enter H1/H2.**
  - Extra years add observations to those firms but do not change which firms enter.
  - The other 29 main firms have no main-analysis site with a coordinate, so they cannot enter H1/H2 whatever is downloaded.
- **H3** is `Y_it = α_i + τ·t + ε_it` with firm fixed effects. τ is identified only from within-firm change, so **a firm contributes only if it has documents for at least two fiscal years.**
  - Today only **5 firms** qualify: BUA Cement (6 years), Guinness (6), Dangote Cement (5), Okomu (5) and Cadbury (2, both FS filings).
  - The other **51** main firms have one year each, so H3 currently rests on 5 firms.

**Where the design is unclear (owner decision needed; no amendment logged):**

1. **H3 sample.** The design gives the "main census" panel, which is all 56 firms that passed the document test. It does not say whether H3 is limited to the exposure-scored firms used in H1/H2.
2. **Which second year.** The design sets no minimum number of years or span for H3. H3's claim is a change "from 2020 to 2025", so the earliest year is the most informative.

**Proposed amendment (for your decision):** "H3 is estimated on main-census firms with documents for at least two fiscal years in 2020–2025. Collection target: for each firm with one year only, one additional annual report, the earliest available of FY2020, then FY2021, then FY2022. A firm without one is listed as not contributing to H3."
- **Option A (the design as written):** the H3 sample is all main-census firms. **Minimum list: 51 reports**, one per single-year firm.
- **Option B (shorter, needs the amendment to restrict the H3 sample):** H3 is limited to the 27 exposure-scored firms, the same firms as H1/H2. **Minimum list: 23 reports** (tier 1 below).

**Recommendation:** Option A, collecting the 23 tier-1 firms first. That keeps the design's sample, and if collection stops early the tier-1 set is exactly Option B.

**Owner decision (2026-11-17): Option A**, the design as written: H3 covers all main-census firms. The owner collects tier 1 (23 firms) first. No amendment was logged, and Option B was not adopted.

**Minimum download list** (`data/interim/phase4_minimum_download_list.csv`; one annual report per firm, FY2020 preferred, else FY2021, else FY2022). Tier 1 = exposure-scored (also in H1/H2); tier 2 = H3 only. Leads are only those already recorded; there are none from africanfinancials.com.

| Tier | Firm | Held now | Lead URL (FY) |
|---|---|---|---|
| 1 | ACADEMY | FY2025 AR | not known |
| 1 | ALEX | FY2024 FS | not known |
| 1 | ARADEL | FY2025 AR | not known |
| 1 | BETAGLAS | FY2023 AR | not known |
| 1 | BUAFOODS | FY2024 AR | not known |
| 1 | CUTIX | FY2025 FS | not known |
| 1 | DANGSUGAR | FY2025 FS | not known |
| 1 | ELLAHLAKES | FY2024 FS | not known |
| 1 | FIDSON | FY2025 AR | not known |
| 1 | GEREGU | FY2024 AR | not known |
| 1 | HBMNG | FY2023 FS | FY2020: https://doclib.ngxgroup.com/Financial_NewsDocs/32658_LAFARGE_AFRICA_PLC%20_AUDITED_FINANCIAL_STATEMENT_FOR_2.pdf |
| 1 | HONYFLOUR | FY2025 FS | not known |
| 1 | JAPAULGOLD | FY2025 FS | not known |
| 1 | LIVESTOCK | FY2025 AR | not known |
| 1 | MAYBAKER | FY2025 FS | not known |
| 1 | NB | FY2025 AR | not known |
| 1 | NEIMETH | FY2025 FS | not known |
| 1 | NESTLE | FY2025 AR | not known |
| 1 | NNFM | FY2025 AR | not known |
| 1 | SEPLAT | FY2025 IAR | not known |
| 1 | TRANSPOWER | FY2025 AR | not known |
| 1 | UNILEVER | FY2025 AR | not known |
| 1 | VITAFOAM | FY2025 FS | not known |
| 2 | AIRTELAFRI | FY2025 AR | not known |
| 2 | BERGER | FY2025 FS | not known |
| 2 | CAP | FY2025 AR | not known |
| 2 | CHAMPION | FY2025 AR | not known |
| 2 | CONOIL | FY2025 FS | not known |
| 2 | ENAMELWA | FY2025 AR | not known |
| 2 | ETERNA | FY2025 AR | not known |
| 2 | EUNISELL | FY2025 FS | not known |
| 2 | FTNCOCOA | FY2025 FS | not known |
| 2 | GOLDBREW | FY2024 FS | not known |
| 2 | IMG | FY2025 AR | not known |
| 2 | INTBREW | FY2023 FS | FY2022: https://doclib.ngxgroup.com/Financial_NewsDocs/38066_INTERNATIONAL_BREWERIES_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2022_FINANCIAL_STATEMENTS_MARCH_2023.pdf |
| 2 | JBERGER | FY2025 AR | not known |
| 2 | MCNICHOLS | FY2025 FS | not known |
| 2 | MECURE | FY2025 AR | not known |
| 2 | MEYER | FY2025 AR | not known |
| 2 | MORISON | FY2025 FS | not known |
| 2 | MTNN | FY2025 AR+SR | FY2020: https://www.mtn.ng/wp-content/uploads/2022/11/MTN-Nigeria-Annual-Report-2020-2.pdf |
| 2 | MULTITREX | FY2024 AR | not known |
| 2 | MULTIVERSE | FY2025 AR | not known |
| 2 | NASCON | FY2025 FS | not known |
| 2 | OANDO | FY2025 FS | not known |
| 2 | PRESCO | FY2025 AR | FY2021: https://www.presco-plc.com/investor-relations/2022-annual-general-meeting/presco-plc-annual-report-and-notice-of-annual-general-meeting/ |
| 2 | PZ | FY2025 FS | not known |
| 2 | THOMASWY | FY2025 FS | not known |
| 2 | TOTAL | FY2025 FS | not known |
| 2 | TRIPPLEG | FY2025 FS | not known |
| 2 | UNIONDICON | FY2025 FS | not known |

Everything else in `data/interim/phase4_download_list.csv` is **nice-to-have**: further years, sustainability reports, full reports replacing FS filings, and the robustness stratum (never pooled into the main tests). None of it changes which firms enter H1–H3.

### 5.2 LIVESTOCK FY2025 (B; A12, then A15)

- **A12 (logged first):** OCR'd with the same tools and settings as every earlier copy (OCRmyPDF 16.13.0, Tesseract 5.4.0, Ghostscript 10.08.0; `--force-ocr -l eng --oversample 300 --jobs 4 --output-type pdf`; 909 s).
  - **Files:** the original `data/raw/manual/livestock/2025_AR.pdf` is unchanged (SHA-256 `8e6d5c14…e5d2`, checked before and after). The copy is `2025_AR_ocr.pdf` (SHA-256 `6ea28e2d…b292`), logged in `data/interim/phase2_ocr_log.csv`.
  - **Page selection:** `src/text_select.py` was re-run. The A3–A5 rule chose the original on 83 pages and the OCR on 49 (12 pages flagged). The other 24 OCR'd documents' text and page selections came out byte-identical.
- **Why A12 alone did not fix it:** the original pages still had run-together text (1.3% of tokens). The cause is that the file's font encodes the space as the control character **U+0003**, which `wordfreq` treats as a separator. So the original and OCR page shares were almost equal (p22: 0.589 against 0.584) and the A3–A5 rule kept the original.
- **A15 (logged before applying; confirmed by the owner on 2026-11-17):** every C0 control character is read as a space, across the whole corpus. This touches 18 documents; almost all occurrences are in LIVESTOCK.

| LIVESTOCK FY2025 | Eligible paragraphs | Words in eligible paragraphs | Run-together tokens |
|---|---|---|---|
| Step 1 (before) | 61 | 26% | 2.9% |
| After A12 (OCR + page selection) | 106 | 28% | 1.3% |
| **After A15 (control characters)** | **262** | 58% | 0.02% |

Elsewhere, A13 and A15 together changed eligible counts only in BUA Cement FY2025 (361 → 364) and Dangote FY2022 (539 → 538).

### 5.3 Ligatures (C; A13)

**Correction to step 1.** Only two private-use code points are ligatures: **U+F001 = "fi" and U+F002 = "fl"**, found in Academy FY2025 and LIVESTOCK FY2025 only. The large private-use counts reported in step 1 for Airtel, MTN, Dangote and others are standalone bullets and check marks (U+F0FC, U+F0B7, U+F0A7, U+F053 …), not ligatures. Academy's "nancial" is U+F001 + "nancial", not a dropped glyph. Genuinely dropped ligatures are rare.

**Repairs made (rule A13; all logged in `data/interim/ligature_repairs.csv`):**
- **Private-use code points mapped:** ACADEMY_2025_AR 299, LIVESTOCK_2025_AR 43.
- **Dropped glyphs repaired (original text layers only):** GUINNESS_2025_AR: 'AMINGO' → 'Flamingo' (1); GUINNESS_2025_AR: 'a ected' → 'affected' (2); GUINNESS_2025_AR: 'con dentiality' → 'confidentiality' (1); GUINNESS_2025_AR: 'e ective' → 'effective' (3); GUINNESS_2025_AR: 'e icient' → 'efficient' (2); GUINNESS_2025_AR: 'e iciently' → 'efficiently' (2); GUINNESS_2025_AR: 'ndings' → 'findings' (1); JBERGER_2025_AR: 'ination' → 'inflation' (1); OKOMUOIL_2022_AR: 'nancial' → 'financial' (1).

"AMINGO" → "Flamingo" is probably a word printed in capitals ("FLAMINGO"); the rule keeps the case of the first letter only. A known limit of the rule: a split where the second half is itself a frequent string (e.g. "o ce" for "office") is not repaired.

**Check on common non-climate words** (counts in non-duplicate paragraphs, before → after; "=" means unchanged; no climate or hazard term was counted):

| Document | Private-use fi/fl | "financial" | "profit" | "office" | "benefit" | "significant" | "flows" | "inflation" | "effective" | "efficient" | "affected" |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AIRTELAFRI_2025_AR | 0→0 | = | = | = | = | = | = | = | = | = | = |
| MTNN_2025_AR | 0→0 | = | = | = | = | = | = | = | = | = | = |
| ACADEMY_2025_AR | 293→0 | 285→340 | 40→121 | 9→17 | 27→40 | 44→56 | 26→50 | 3→6 | = | = | = |
| DANGCEM_2020_AR | 0→0 | = | = | = | = | = | = | = | = | = | = |
| DANGCEM_2022_AR | 0→0 | = | = | = | = | = | = | = | = | = | = |
| DANGCEM_2023_AR | 0→0 | = | = | = | = | = | = | = | = | = | = |
| DANGCEM_2024_AR | 0→0 | = | = | = | = | = | = | = | = | = | = |
| DANGCEM_2025_AR | 0→0 | = | = | = | = | = | = | = | = | = | = |
| GUINNESS_2025_AR | 0→0 | = | = | = | = | = | = | = | 85→88 | 1→3 | 3→5 |
| LIVESTOCK_2025_AR | 74→0 | 360→417 | 64→103 | 11→20 | 25→42 | 32→39 | 33→40 | = | 23→26 | = | = |

Academy and LIVESTOCK gain many standard words ("financial", "profit", "office"), and Guinness FY2025 gains "efficient" and "affected". Airtel, MTN and Dangote are unchanged, which confirms they had no ligature defect.

### 5.4 Section tagging (D; A14)

The rule (A14) finds the audited financial statements and notes from the headings "Independent auditor's report", the primary statements and "Notes to the financial statements". Contents pages are ignored. The range ends at the first post-statement section (other national disclosures, value added, five-year summary, shareholder information, proxy, AGM notice) or at the document end. All 82 documents are tagged in `data/interim/section_tags.csv`:
- **41** by the rule alone.
- **17** flagged by the rule, then reviewed and kept. Most of these are flagged only because their notes pages carry no running header.
- **24** with boundaries set by analyst review, with evidence recorded.
- **Unresolved flags: none.**
- The four sustainability documents (SR, SRX) have no financial-statement section.

**Analyst-set boundaries** (from page headings only; the reason is in `flag_reason`):
- **Rule start missed the auditor's report**, which has no "independent auditor's report" heading among its first blocks: Guinness FY2022–24 ("Report on the audit of the financial statements"), Okomu FY2020/2023/2024, NNFM, Thomas Wyatt, Meyer, Multiverse, Cutix, Champion, Aradel, Eunisell, Julius Berger and Honeywell.
- **Rule start was a summary statement** in a narrative section: Airtel (financial review, p55).
- **Rule found nothing** (headings fused with other text): Dangote FY2023, Multi-Trex.
- **OCR text, only one page found:** Ellah Lakes.
- **End corrected:**
  - Okomu FY2020/2022/2023/2024 and NNFM: five-year summaries repeat statement headings and pushed the end over later narrative pages.
  - Tripple Gee: heading merged with a table.
  - Eterna: singular "Other National Disclosure".
  - NB: shareholder information.

**Uncertain items, kept as tagged:**
- Julius Berger's auditor's report pages (pp29–32) have no text layer; the start is inferred from their position.
- Honeywell pp26–30 have no text at all.
- In a few documents the internal-control assurance report (ICFR) sits inside the range (Guinness FY2024 pp79–80, Multiverse pp8–9).
- ICFR attestations and sustainability limited-assurance reports outside the range are treated as narrative.

**Result:** financial statements make up a median 48% of an annual report's pages (range 27–87%) and 72% of an FS filing's (51–92%).

| Document | Pages | FS range | Method | Start evidence | End evidence | Narrative eligible | FS eligible |
|---|---|---|---|---|---|---|---|
| ABCTRANS_2025_FS | 90 | 16–86 | rule (analyst-reviewed) | p16: Independent Auditor's Report | p87: next section 'Other National Disclosures'; last FS heading p23: CONSOLIDATED AND SEPARATE STATEMENT OF CA | 41 | 272 |
| ACADEMY_2025_AR | 112 | 34–97 | rule | p34: INDEPENDENT AUDITOR’S REPORT | p98: next section 'OTHER NATIONAL DISCLOSURES'; last FS heading p97: NOTES TO THE CONSOLIDATED AND SEPARATE FI | 134 | 195 |
| AIRTELAFRI_2025_AR | 268 | 179–253 | analyst review | p179: 'Financial statements' divider; p180: Independent Auditor's report to the Members of Airtel Africa plc | p254: 'Other information' (alternative performance measures, glossary) | 935 | 322 |
| ALEX_2024_FS | 60 | 10–58 | rule | p10: INDEPENDENT AUDITOR'S REPORT | p59: next section 'OTHER NATIONAL DISCLOSURES'; last FS heading p57: NOTES TO THE FINANCIAL STATEMENTS (CONT'D | 21 | 149 |
| ARADEL_2025_AR | 135 | 18–135 | analyst review | p18: INDEPENDENT AUDITOR'S REPORT To the Shareholders (Deloitte) | document end (notes to p135) | 25 | 247 |
| BERGER_2025_FS | 80 | 27–79 | rule | p27: CONSOLIDATED AND SEPARATE STATEMENT OF FINANCIAL POSITION AS AT 31 DECEMBER 2025 | p80: next section 'FINANCIAL SUMMARY 31 DECEMBER 2025 2024 2023 2022 2021 N'000 N'000 N'000 N'000 N'000'; last | 32 | 176 |
| BETAGLAS_2023_AR | 108 | 41–98 | rule (analyst-reviewed) | p41: Independent Auditors’ Report | p99: next section 'Other National Disclosures'; last FS heading p44: Independent Auditors’ Report To the Membe | 153 | 164 |
| BUACEMENT_2020_AR | 66 | 29–61 | rule | p29: Independent Auditor’s Report (Cont.) | p62: next section 'Shareholder Information'; last FS heading p60: Notes to the Financial Statements (Cont.) No | 190 | 196 |
| BUACEMENT_2021_AR | 142 | 61–123 | rule | p61: Independent Auditor’s Report | p124: next section 'Statement of Value Added'; last FS heading p123: Notes to the Financial Statements (Cont.) | 187 | 196 |
| BUACEMENT_2022_AR | 152 | 72–131 | rule | p72: Independent Auditor’s Report | p132: next section 'Statement of Value Added'; last FS heading p131: Notes to the Financial Statements (Cont.) | 182 | 188 |
| BUACEMENT_2023_AR | 160 | 80–141 | rule (analyst-reviewed) | p80: Independent Auditor’s Report | p142: next section 'Statement of Value Added'; last FS heading p141: Notes to the Financial Statements (Cont.) | 265 | 185 |
| BUACEMENT_2024_AR | 148 | 77–130 | rule | p77: Independent Auditor's Report | p131: next section 'Statement of Value Added'; last FS heading p130: Notes to the Financial Statements Cont'd. | 289 | 176 |
| BUACEMENT_2025_AR | 79 | 42–71 | rule | p42: Independent Auditor’s Report | p72: next section 'Shareholder Information'; last FS heading p70: Statement of Financial Position | 179 | 185 |
| BUAFOODS_2024_AR | 70 | 18–70 | rule | p18: Independent auditor’s report To the Members of BUA Foods Plc | document end; last FS heading p70: Statement of financial position | 39 | 185 |
| CADBURY_2022_FS | 26 | 4–26 | rule | p4: Statement of financial position In thousands of naira | document end; last FS heading p20: Notes to the financial statements (Continued) | 0 | 99 |
| CADBURY_2025_FS | 28 | 4–28 | rule | p4: Statement of financial position As at 31 December 2025 | document end; last FS heading p23: Notes to the financial statements (Continued) | 0 | 116 |
| CAP_2025_AR | 87 | 30–84 | rule (analyst-reviewed) | p30: Independent Auditor's Report | p85: next section 'Other National Disclosures'; last FS heading p67: Notes to the Financial Statements | 110 | 195 |
| CHAMPION_2025_AR | 105 | 43–92 | analyst review | p43: Deloitte & Touche letterhead; p44: Key Audit Matter | p93: OTHER NATIONAL DISCLOSURES (rule) | 118 | 173 |
| CONOIL_2025_FS | 73 | 33–73 | rule | p33: STATEMENT OF PROFIT OR LOSS AND OTHER COMPREHENSIVE INCOME FOR THE PERIOD ENDED 31 DECEMBER 2025 | document end; last FS heading p73: Statement of financial position | 75 | 122 |
| CUTIX_2025_FS | 82 | 37–78 | analyst review | p37: auditor's letterhead (Chartered Accountants & Fraud Examiner); p39: ISA wording | p79: Other National Disclosures (rule) | 56 | 108 |
| DANGCEM_2020_AR | 260 | 156–226 | rule | p156: INDEPENDENT AUDITOR’S REPORT | p227: next section 'Five-Year Financial Summary – Other National Disclosure Group balance sheet'; last FS head | 482 | 198 |
| DANGCEM_2022_AR | 207 | 105–173 | rule | p105: INDEPENDENT AUDITOR’S REPORT | p174: next section 'Five-year financial summary – other national disclosure Group'; last FS heading p172: Note | 350 | 188 |
| DANGCEM_2023_AR | 208 | 103–172 | analyst review | p103: INDEPENDENT AUDITOR'S REPORT To the Shareholders | p173: five-year summary ('Balance sheet 2023 2022 2021 ...'), then value added, share capital history, GRI ind | 361 | 183 |
| DANGCEM_2024_AR | 272 | 144–231 | rule (analyst-reviewed) | p144: Independent Auditor's Report | p232: next section 'FIVE -YEAR FINANCIAL SUMMARY Other National Disclosure'; last FS heading p157: Notes to th | 486 | 304 |
| DANGCEM_2024_SRX | 72 | none | rule |  |  | 197 | 0 |
| DANGCEM_2025_AR | 236 | 115–194 | rule (analyst-reviewed) | p115: Independent Auditor’s Report | p195: next section 'Five -Year Financial Summary'; last FS heading p121: Consolidated and separate statements  | 484 | 327 |
| DANGCEM_2025_SRX | 52 | none | rule |  |  | 159 | 0 |
| DANGSUGAR_2025_FS | 88 | 26–84 | rule | p26: Independent auditor’s report To the Members of Dangote Sugar Refinery Plc | p85: next section 'Other National Disclosures'; last FS heading p84: Notes to the Consolidated and Separate Fi | 101 | 264 |
| ELLAHLAKES_2024_FS | 46 | 10–46 | analyst review | p10: auditor's letterhead (OA Professionals); p13: consolidated statement of profit or loss | document end (notes pp35-42, summarised statements pp43-46) | 10 | 86 |
| ENAMELWA_2025_AR | 47 | 16–44 | rule (analyst-reviewed) | p16: Independent Auditor's Report | p45: next section 'OTHER NATIONAL DISCLOSURES'; last FS heading p16: Independent Auditor's Report | 25 | 48 |
| ETERNA_2025_AR | 73 | 14–69 | analyst review | p14: Independent auditor's report (rule) | p70: 'Other National Disclosure' (singular, not matched by the rule) | 40 | 189 |
| EUNISELL_2025_FS | 39 | 16–36 | analyst review | p16: Report of the Independent Auditors To the Members | p37: Statement of Value Added (rule) | 33 | 52 |
| FIDSON_2025_AR | 87 | 21–85 | rule | p21: Statement of Financial Position As at 31 December 2025 | p86: next section 'Statement of value added'; last FS heading p83: Notes to the financial statements | 57 | 156 |
| FTNCOCOA_2025_FS | 55 | 20–53 | rule (analyst-reviewed) | p20: REPORT OF THE INDEPENDENT AUDITOR TO THE MEMBERS OF FTN COCOA PROCESSORS PLC | p54: next section 'STATEMENT OF VALUE ADDED FOR THE YEAR ENDED 31 DECEMBER 2025'; last FS heading p29: NOTES T | 34 | 70 |
| GEREGU_2024_AR | 104 | 47–92 | rule | p47: Independent auditor's report | p93: next section 'STATEMENT OF VALUE ADDED'; last FS heading p84: NOTES TO THE FINANCIAL STATEMENTS ANNUAL RE | 161 | 128 |
| GOLDBREW_2024_FS | 64 | 22–62 | rule | p22: REPORT OF THE INDEPENDENT AUDITORS | p63: next section 'STATEMENT OF VALUE ADDED FOR THE YEAR ENDED 31ST MARCH, 2024'; last FS heading p62: NOTES T | 26 | 95 |
| GUINNESS_2020_AR | 152 | 72–135 | rule | p72: Independent auditor’s report TO THE MEMBERS OF GUINNESS NIGERIA PLC | p136: next section 'SHAREHOLDERS’ INFORMATION'; last FS heading p135: Income Statement 2020 2019 2018 2017 201 | 240 | 219 |
| GUINNESS_2021_AR | 156 | 74–140 | rule | p74: Independent Auditor's Report | p141: next section 'SHAREHOLDERS’ INFORMATION'; last FS heading p139: Income Statement 2021 2020 2019 2018 201 | 234 | 223 |
| GUINNESS_2022_AR | 170 | 84–154 | analyst review | p84: Report on the audit of the financial statements / Our opinion | p155: SHAREHOLDERS' INFORMATION | 283 | 232 |
| GUINNESS_2023_AR | 164 | 76–148 | analyst review | p76: Report on the audit of the financial statements / Our opinion | p149: SHAREHOLDERS' INFORMATION | 261 | 254 |
| GUINNESS_2024_AR | 163 | 74–147 | analyst review | p74: Report on the audit of the financial statements / Our opinion | p148: Shareholders' Information | 253 | 256 |
| GUINNESS_2025_AR | 162 | 78–142 | rule | p78: Independent Auditor’s Report TO THE MEMBERS OF GUINNESS NIGERIA PLC | p143: next section 'OTHER NATIONAL DISCLOSURES>'; last FS heading p141: NOTES TO THE FINANCIAL STATEMENTS | 273 | 247 |
| HBMNG_2023_FS | 105 | 17–101 | rule (analyst-reviewed) | p17: Independent Auditor’s Report | p102: next section 'Other National Disclosures'; last FS heading p53: Notes to the Consolidated and Separate F | 54 | 260 |
| HONYFLOUR_2025_FS | 118 | 31–112 | analyst review | p31: consolidated and separate statement of financial position (heading merged with table); pp26-30 have no te | p113: Other National Disclosures (rule) | 65 | 233 |
| IMG_2025_AR | 71 | 21–68 | rule (analyst-reviewed) | p21: INDEPENDENT AUDITOR'S REPORT | p69: next section 'Other National Disclosures'; last FS heading p53: Notes to the Financial Statements | 53 | 170 |
| INTBREW_2023_FS | 57 | 18–54 | rule | p18: Statement of profit or loss for the year ended 31 December 2023 | p55: next section 'Other National Disclosures'; last FS heading p54: Notes to the financial statements | 55 | 182 |
| JAPAULGOLD_2025_FS | 84 | 7–83 | rule | p7: Independent Auditor's Report | p84: next section 'FINANCIAL SUMMARY - GROUP 31 DECEMBER 2025 2024 2023 2022 2021 N'000 N'000 N'000 N'000 N'00 | 18 | 194 |
| JBERGER_2025_AR | 89 | 29–78 | analyst review | p29: two-up report pages 53-60 under the running header 'Annual Reports and Audited Consolidated and Separate  | p79: OTHER NATIONAL DISCLOSURES AND ADDITIONAL INFORMATION (rule) | 185 | 303 |
| LIVESTOCK_2025_AR | 132 | 54–125 | rule | p54: Independent Auditor's Report | p126: next section 'UNCLAIMED DIVIDENDS'; last FS heading p119: Statement of Profit or Loss and Other Comprehe | 134 | 128 |
| MAYBAKER_2025_FS | 74 | 15–67 | rule | p15: CONSOLIDATED AND SEPARATE STATEMENTS OF PROFIT OR LOSS AND OTHER COMPREHENSIVE INCOME FOR THE YEAR ENDED  | p68: next section 'Other National Disclosures'; last FS heading p67: NOTES TO THE CONSOLIDATED AND SEPARATE FI | 27 | 122 |
| MCNICHOLS_2025_FS | 52 | 8–50 | rule | p8: REPORT OF THE INDEPENDENT AUDITORS TO THE MEMBERS OF McNICHOLS CONSOLIDATED PLC | p51: next section 'Other National Disclosures'; last FS heading p50: Notes to the Financial Statements - (Cont | 10 | 109 |
| MECURE_2025_AR | 43 | 11–41 | rule (analyst-reviewed) | p11: Independent Auditor’s report To the Shareholders of Mecure Industries Plc. Report on the Audit of the Fin | p42: next section 'Value added 23,170,892 100 12,965,943 100'; last FS heading p11: Independent Auditor’s repo | 22 | 88 |
| MEYER_2025_AR | 66 | 11–66 | analyst review | p11: auditor's letterhead (PKF Professional Services); p14: Key audit matters | document end (rule) | 20 | 147 |
| MORISON_2025_FS | 45 | 12–43 | rule (analyst-reviewed) | p12: INDEPENDENT AUDITOR'S REPORT TO THE SHAREHOLDERS OF MORISON INDUSTRIES PLC REPORT ON THE AUDIT OF THE FIN | p44: next section 'Value added as a percentage of revenue 30% 23%'; last FS heading p12: INDEPENDENT AUDITOR'S | 28 | 120 |
| MTNN_2025_AR | 167 | 93–154 | rule | p93: Independent Auditor’s Report Independent Auditor’s Report | p155: next section 'Notice of Annual General Meeting'; last FS heading p153: Statement of financial position | 455 | 423 |
| MTNN_2025_SR | 174 | none | rule |  |  | 266 | 0 |
| MULTITREX_2024_AR | 57 | 17–54 | analyst review | p17: INDEPENDENT AUDITORS' REPORT TO THE MEMBERS (pp15-16: auditor's report on internal control) | p55: OTHER NATIONAL DISCLOSURES | 27 | 74 |
| MULTIVERSE_2025_AR | 49 | 5–46 | analyst review | p5: auditor's letterhead (Olukayode Aina & Co., Chartered Accountants) | p47: FINANCIAL SUMMARY (rule) | 1 | 87 |
| NASCON_2025_FS | 73 | 22–73 | rule | p22: Independent auditor’s report To the Members of Nascon Allied Industries Plc | document end; last FS heading p73: Statement of Financial Position | 56 | 148 |
| NB_2025_AR | 179 | 63–162 | analyst review | p63: INDEPENDENT AUDITOR'S REPORT (rule) | p163: shareholder information (substantial interests, share capital history, dividends, major customers) | 199 | 311 |
| NEIMETH_2025_FS | 66 | 15–66 | rule | p15: INDEPENDENT AUDITOR'S REPORT TO THE SHAREHOLDERS OF NEIMETH INTERNATIONAL PHARMACEUTICALS PLC REPORT ON T | document end; last FS heading p66: Statement of financial position | 44 | 178 |
| NESTLE_2025_AR | 182 | 51–113 | rule (analyst-reviewed) | p51: Independent Auditor’s Report To the Members of Nestlé Nigeria Plc Report on the Audit of the Financial St | p114: next section 'Other National Disclosures'; last FS heading p59: Statement of Cash Flows - continued | 203 | 136 |
| NNFM_2025_AR | 102 | 34–87 | analyst review | p34: INDEPENDENT AUDITOR'S REPORT (heading below the internal-control assurance text at the top of p34) | p88: OTHER NATIONAL DISCLOSURES; employee-engagement pages and proxy form follow | 126 | 206 |
| OANDO_2025_FS | 113 | 12–109 | rule (analyst-reviewed) | p12: INDEPENDENT AUDITOR’S REPORT | p110: next section 'Other National Disclosures'; last FS heading p12: INDEPENDENT AUDITOR’S REPORT | 60 | 577 |
| OKOMUOIL_2020_AR | 69 | 29–60 | analyst review | p29: Report on the financial statements (auditor's report, OCR page) | p61: Distribution of value added | 109 | 106 |
| OKOMUOIL_2021_AR | 46 | 33–46 | rule | p33: INDEPENDENT AUDITORS’ REPORT ANNUAL REPORT & ACCOUNTS | document end; last FS heading p40: STATEMENT OF CASH FLOWS | 134 | 124 |
| OKOMUOIL_2022_AR | 88 | 33–76 | analyst review | p33: INDEPENDENT AUDITORS' REPORT TO THE MEMBERS (rule) | p77: value added / p78 five-year summary; community pages from p79 | 90 | 167 |
| OKOMUOIL_2023_AR | 96 | 32–83 | analyst review | p32: REPORT ON THE AUDIT OF THE FINANCIAL STATEMENTS | p84-85: value added statement; photo and proxy pages follow | 110 | 179 |
| OKOMUOIL_2024_AR | 115 | 39–103 | analyst review | p39: REPORT ON THE AUDIT OF THE FINANCIAL STATEMENTS (EY) | p104: VALUE ADDED STATEMENT; community pages from p106 | 135 | 203 |
| OKOMUOIL_2024_SR | 48 | none | rule |  |  | 115 | 0 |
| PRESCO_2025_AR | 119 | 21–119 | rule | p21: Independent Auditor's Report | document end; last FS heading p119: Statement of Comprehensive Income | 61 | 319 |
| PZ_2025_FS | 84 | 20–80 | rule | p20: Independent auditor’s report | p81: next section 'OTHER NATIONAL DISCLOSURES'; last FS heading p80: Notes to the consolidated and separate fi | 57 | 281 |
| RTBRISCOE_2025_FS | 79 | 17–75 | rule | p17: REPORT OF THE INDEPENDENT AUDITORS TO THE SHAREHOLDERS OF R.T. BRISCOE (NIGERIA) PLC | p76: next section 'Other National Disclosures'; last FS heading p75: NOTES TO THE CONSOLIDATED AND SEPARATE FI | 55 | 205 |
| SEPLAT_2025_IAR | 350 | 164–308 | rule (analyst-reviewed) | p164: Independent auditor’s report | p309: next section 'Statement of value added'; last FS heading p278: Separate statement of cash flows For the  | 653 | 388 |
| THOMASWY_2025_FS | 57 | 15–57 | analyst review | p15: REPORT OF THE INDEPENDENT AUDITORS TO THE SHAREHOLDERS | document end (rule) | 44 | 134 |
| TOTAL_2025_FS | 98 | 37–87 | rule | p37: Independent auditor’s report To the Members of TotalEnergies Marketing Nigeria Plc | p88: next section 'Other national disclosures'; last FS heading p87: NOTES TO THE FINANCIAL STATEMENTS | 115 | 229 |
| TRANSCORP_2025_FS | 138 | 32–134 | rule (analyst-reviewed) | p32: Consolidated and Separate Statements of Profit or Loss and Other Comprehensive Income Group Company | p135: next section 'OTHER NATIONAL DISCLOSURES'; last FS heading p112: Notes to the Consolidated and Separate  | 53 | 200 |
| TRANSPOWER_2025_AR | 81 | 34–78 | rule | p34: Statement of Changes in Equity For the year ended 31 December 2025 Share capital (Note 24) | p79: next section 'OTHER NATIONAL DISCLOSURES'; last FS heading p76: Notes to the Financial Statements 27 Part | 59 | 85 |
| TRIPPLEG_2025_FS | 57 | 27–55 | analyst review | p27: Statement of Financial Position (rule) | p56: Value Added Statement (heading merged with table) | 45 | 73 |
| UNILEVER_2025_AR | 176 | 72–143 | rule | p72: Independent auditor's report To the Members of Unilever Nigeria Pic | p144: next section 'Other National Disclosures'; last FS heading p143: Notes to the financial statements (cont | 199 | 185 |
| UNIONDICON_2025_FS | 29 | 4–24 | rule (analyst-reviewed) | p4: INDEPENDENT AUDITOR'S REPORT TO THE SHAREHOLDERS OF UNION DICON SALT PLC | p25: next section 'VALUE ADDED'; last FS heading p9: STATEMENT OF CASH FLOW | 9 | 74 |
| VITAFOAM_2025_FS | 128 | 52–128 | rule | p52: Independent auditor’s report To the Members of Vitafoam Nigeria Plc | document end; last FS heading p128: Statement of Financial Position | 95 | 299 |

### 5.5 Current totals (after A12–A15 and A14 tagging)

| Measure | Value |
|---|---|
| Paragraph rows | 139,262 |
| Model-eligible rows (≥ 40 words, not duplicates) | 26,642 (step 1: 26,439) |
| **Model-eligible narrative rows** (outside the financial statements) | **11,827** (median 67 words, IQR 51–100) |
| Model-eligible rows inside the financial statements (kept for the site-mention measure, f1) | 14,815 |
| Duplicate rows | 25,376 |
| Split long paragraphs | 753 (into 1,591 pieces) |
| Documents flagged by the broken-text checks | **0** (step 1: LIVESTOCK) |

- **Narrative eligible paragraphs per document:** median 105.
- **Fewest:** Multiverse FY2025 has 1, because its statements start on p5. Union Dicon has 9, McNichols 10, Ellah Lakes 10, Japaul Gold 18 and Meyer 20.
- These low counts reflect FS-type filings with a short directors' report; they are not text faults.

### 5.6 Next steps (step 1 of this list done for tier 1: see section 6)

1. **Owner (tier 1 received and processed, section 6; tier 2 not started):** downloading the minimum list, tier 1 first (H3: Option A, decided 2026-11-17). When the files arrive: inventory, OCR/readability checks, segmentation, section tagging and repairs (A12–A15) for the new documents.
2. Build and freeze the site-mention dictionary (f5).
3. Run validation (g) on the narrative paragraphs before any outcome is computed.

## 6. Step 3: tier-1 files (2026-11-17)

**Input:** the 25 files from owner batches 1–5 (`docs/data_sources.md`): one earlier year for each of the 23 tier-1 firms, plus post-listing years for Transcorp Power (FY2024) and Aradel (FY2024) under **A16** (logged before any of these files was processed). The rules are those of steps 1–2 (A1–A5, A12–A15, A14), unchanged. No ClimateBERT model was run, no dictionary was applied, nothing was counted and no measure was computed. The tokenizer was used only for the 512-token split.

**Interruption.** The laptop lost power during the OCR of the eight A2 files. On resumption:
- **ALEX FY2020** was complete. Its copy matched the logged SHA-256 and opened with all 102 pages.
- **The other seven** had no `_ocr` copy on disk and no log row.
- **Removed:** only OCRmyPDF's temporary work folder from the interrupted run (715 MB in the user temp directory). No project file or original was deleted.
- **The other seven were then OCR'd one at a time.** Same tools and settings: OCRmyPDF 16.13.0, Tesseract 5.4.0, Ghostscript 10.08.0; `--force-ocr -l eng --oversample 300 --jobs 4 --output-type pdf`.
- `src/phase2_ocr.py` gained an optional path argument so that it processes one file per run. Its options did not change.
- **Checks:** every original's SHA-256 was the same before and after OCR, and every copy matches its log row.

| File | Pages | OCR time |
|---|---|---|
| ALEX FY2020 (before the interruption) | 102 | 503 s |
| Ellah Lakes FY2020 | 46 | 103 s |
| Fidson FY2020 | 88 | 112 s |
| May & Baker FY2020 | 111 | 321 s |
| Vitafoam FY2020 | 128 | 361 s |
| Aradel FY2021 | 129 | 794 s |
| Unilever FY2020 | 169 | 517 s |
| Aradel FY2024 | 222 | 778 s |

### 6.1 Text selection (A3–A5)

`src/text_select.py` was re-run. The 24 earlier OCR'd documents came out byte-identical (text files and all 2,555 page rows of `text_sources.csv`). All eight new merged texts pass A1 (common-word share 0.40–0.58).

Three files have many pages where both versions score below 0.20, so the higher share is used and the page is flagged (A4):

| File | Flagged pages | Pages |
|---|---|---|
| ALEX FY2020 | 28 | pp74–101 |
| Aradel FY2021 | 24 | mostly pp105–126 |
| Aradel FY2024 | 56 | mostly pp172–219 |

These pages are shareholder and unclaimed-dividend name lists. They have hundreds of tokens each, but almost all are personal names. This is not a text fault.

### 6.2 Inventory and A16

**Inventory code** (in `src/phase4_corpus.py`):
- **Folder map:** `nb/` → NB and `hbmng/` → HBMNG.
- **Type fixes**, as recorded in `docs/data_sources.md`:
  - Lafarge (HBMNG) FY2020 = FS;
  - Transcorp Power FY2020 = FS;
  - ALEX FY2020 = AR (ALEX's FY2024 filing stays FS);
  - Seplat FY2020 = AR.
- Ellah Lakes FY2020 and Japaul Gold FY2021 are FS, as recorded.

**Totals:** 107 documents and 12,143 pages:
- By type: AR 68, FS 34, SR 2, SRX 2, IAR 1.
- By fiscal year: FY2020 23, FY2021 5, FY2022 7, FY2023 7, FY2024 14, FY2025 51.

**A16 (H3 main versus robustness).** `phase4_documents.csv` now carries `listing_date` and `h3_main`. All five late-listed firms have 31 December year-ends.
- **Robustness only:** two documents predate listing, ARADEL_2021_AR (listed 14 October 2024) and TRANSPOWER_2020_FS (listed 4 March 2024).
- **Count in the main analysis:** every other document, including BUA Foods FY2022 (listed 5 January 2022) and Geregu FY2022 (listed 5 October 2022).

### 6.3 Segmentation, repairs and broken-text checks

The 25 documents were appended to `paragraphs.csv` (`segment_new`, five documents per run). The 82 earlier documents were not re-segmented, and their rows are unchanged.

- **A13:** 239 private-use ligature code points mapped in LIVESTOCK FY2020, the same U+F001/U+F002 pattern as LIVESTOCK FY2025. There were no dropped-glyph repairs in the new files.
- **A15** (control characters → space) applied as before.
- **Broken-text checks** (`summary`):
  - **None of the 107 documents is flagged.** No document has fewer than 20 eligible paragraphs, a common-word share below 0.25, more than 10% of pages without text, more than 95% short blocks, a paragraph over 1,500 words, or more than 1% run-together tokens.

### 6.4 Section tagging (A14)

The rule was re-run on all 107 documents. The 82 earlier documents' tags are unchanged. Of the 25 new ones:
- **8 by the rule alone.**
- **2 flagged and kept** after review:
  - Beta Glass FY2020: its notes headings follow a running header.
  - Cutix FY2020: its notes are headed "NOTE TO THE FINANCIAL STATEMENT", singular.
- **15 with analyst-set boundaries**, evidence recorded in `section_tags.csv`.
- **Lafarge FY2020** (HBMNG_2020_FS) is also flagged and kept: its notes headings carry a company-name prefix.

**Unresolved flags: none.**

**Analyst-set boundaries.** The reasons are below; all 15 are in `src/phase4_sections.py` `OVERRIDES`.
- **Rule start missed the auditor's report:**
  - ALEX FY2020: the rule start was a summary statement under "Financial highlights".
  - Aradel FY2021: two-up spreads; the auditor's report begins on the right half of p45.
  - Honeywell FY2020.
  - Transcorp Power FY2020 and FY2024: in FY2024, pp26–28 are an internal-control assurance report and are treated as narrative, as before.
  - Ellah Lakes FY2020 (OCR).
  - Neimeth FY2020: the rule took "BALANCE SHEET RESTRUCTURING" in the directors' report as a balance-sheet heading.
- **Auditor's report pages have no text layer; start inferred from position:**
  - Geregu FY2022 (pp26–29);
  - NB FY2020 (pp30–33).
- **Rule found no heading:** BUA Foods FY2022. Every page starts with a navigation bar.
- **End corrected:**
  - Academy FY2020 and Vitafoam FY2020: post-statement headings have a company-name prefix or are OCR'd.
  - Honeywell FY2020: "Other Notional Disclosures" (sic).
  - Livestock FY2020: headings fused with other text.
  - NNFM FY2020: ran over value added, five-year summary and CSR pages.
  - Seplat FY2020: ran over "Additional information".
  - NB FY2020: value added statement.
  - Ellah Lakes FY2020: value added statement, p44. This is the rule's end. The FY2024 file was tagged to the document end in step 2, so its summary pages count as FS there. That affects only a few short rows.

| Document | Pages | Text route | Paragraph rows | Model-eligible | Median words (eligible) | Words in eligible paragraphs | FS range | Method | Narrative eligible | FS eligible | H3 main (A16) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ACADEMY_2020_AR | 100 | original | 702 | 173 | 129 | 89% | 17–96 | analyst review | 26 | 147 | yes |
| ALEX_2020_AR | 102 | A3–A5 page selection | 1,407 | 334 | 77 | 77% | 20–69 | analyst review | 192 | 142 | yes |
| ARADEL_2021_AR | 129 | A3–A5 page selection | 7,257 | 511 | 61 | 54% | 45–103 | analyst review | 251 | 260 | **no (pre-listing; robustness)** |
| ARADEL_2024_AR | 222 | A3–A5 page selection | 5,348 | 695 | 74 | 71% | 69–156 | rule | 438 | 257 | yes |
| BETAGLAS_2020_AR | 120 | original | 2,240 | 291 | 66 | 63% | 43–110 | rule (analyst-reviewed) | 144 | 147 | yes |
| BUAFOODS_2022_AR | 194 | original | 4,014 | 430 | 57.5 | 56% | 116–171 | analyst review | 269 | 161 | yes |
| CUTIX_2020_AR | 96 | original | 958 | 251 | 71 | 72% | 51–82 | rule (analyst-reviewed) | 125 | 126 | yes |
| DANGSUGAR_2020_AR | 204 | original | 2,755 | 352 | 94.5 | 78% | 126–184 | rule | 231 | 121 | yes |
| ELLAHLAKES_2020_FS | 46 | A3–A5 page selection | 802 | 101 | 63 | 62% | 10–43 | analyst review | 17 | 84 | yes |
| FIDSON_2020_AR | 88 | A3–A5 page selection | 1,326 | 244 | 62 | 66% | 21–86 | rule | 45 | 199 | yes |
| GEREGU_2022_AR | 72 | original | 950 | 193 | 65 | 68% | 26–70 | analyst review | 73 | 120 | yes |
| HBMNG_2020_FS | 72 | original | 2,240 | 291 | 61 | 59% | 10–68 | rule (analyst-reviewed) | 33 | 258 | yes |
| HONYFLOUR_2020_AR | 113 | original | 2,128 | 262 | 65 | 57% | 54–98 | analyst review | 125 | 137 | yes |
| JAPAULGOLD_2021_FS | 88 | original | 1,186 | 197 | 63 | 60% | 4–88 | rule | 4 | 193 | yes |
| LIVESTOCK_2020_AR | 106 | original | 1,850 | 274 | 70 | 71% | 43–96 | analyst review | 117 | 157 | yes |
| MAYBAKER_2020_AR | 111 | A3–A5 page selection | 1,712 | 274 | 64 | 64% | 35–93 | rule | 119 | 155 | yes |
| NB_2020_AR | 110 | original | 641 | 202 | 144.5 | 97% | 30–103 | analyst review | 65 | 137 | yes |
| NEIMETH_2020_AR | 124 | original | 1,406 | 257 | 84 | 75% | 71–114 | analyst review | 142 | 115 | yes |
| NESTLE_2020_AR | 177 | original | 4,050 | 425 | 62 | 55% | 46–119 | rule | 212 | 213 | yes |
| NNFM_2020_AR | 202 | original | 3,175 | 564 | 61 | 62% | 57–174 | analyst review | 198 | 366 | yes |
| SEPLAT_2020_AR | 312 | original | 5,449 | 981 | 104 | 86% | 148–295 | analyst review | 548 | 433 | yes |
| TRANSPOWER_2020_FS | 69 | original | 507 | 108 | 110 | 86% | 9–66 | analyst review | 13 | 95 | **no (pre-listing; robustness)** |
| TRANSPOWER_2024_AR | 85 | original | 536 | 149 | 131 | 92% | 29–82 | analyst review | 45 | 104 | yes |
| UNILEVER_2020_AR | 169 | A3–A5 page selection | 1,637 | 398 | 68 | 73% | 64–128 | rule | 223 | 175 | yes |
| VITAFOAM_2020_AR | 128 | A3–A5 page selection | 3,274 | 398 | 68 | 65% | 35–115 | analyst review | 119 | 279 | yes |

### 6.5 Current totals (107 documents)

| Measure | Step 2 (82 docs) | New (25 docs) | **Now (107 docs)** |
|---|---|---|---|
| Pages | 8,904 | 3,239 | **12,143** |
| Paragraph rows | 139,262 | 57,550 | **196,812** |
| Model-eligible rows | 26,642 | 8,355 | **34,997** |
| **Model-eligible narrative rows** | 11,827 | 3,774 | **15,601** |
| Model-eligible rows in the financial statements | 14,815 | 4,581 | **19,396** |
| Duplicate rows | 25,376 | 14,132 | **39,508** |
| Documents flagged by the broken-text checks | 0 | 0 | **0** |

Narrative eligible rows have a median of 68 words (IQR 51–103). The new documents' median is 73.

**Documents to watch (not faults; no action taken):**
- **Very little narrative:**
  - Japaul Gold FY2021 FS has 4 narrative eligible paragraphs. It has no directors' report, as recorded at download.
  - Transcorp Power FY2020 FS has 13, Ellah Lakes FY2020 FS 17, Academy FY2020 26 and Lafarge FY2020 FS 33.
  - These are financial-statement filings or plain-format reports. Their firm-years count for H3, but each rests on few paragraphs.
- **Aradel FY2021:** 7,257 rows, 54% of words in eligible paragraphs, because of long shareholder lists in two-up spreads. It is a pre-listing year, so robustness only.

### 6.6 H3 sample (A16 main analysis)

**H3 sample:** 56 main-census firms passed the document test. A firm contributes to H3 only with documents for at least two fiscal years.

| | Before step 3 | **Now** |
|---|---|---|
| Firms with ≥ 2 main-analysis years | 5 | **28** |
| Firms with one year only | 51 | 28 |

- **All 23 tier-1 firms now have two or more main-analysis years.**
  - Aradel: FY2024 and FY2025 count; FY2021 is robustness only.
  - Transcorp Power: FY2024 and FY2025 count; FY2020 is robustness only.
- **H3 main firms (years):**
  - Six years: BUA Cement and Guinness.
  - Five years: Dangote Cement and Okomu.
  - Two years: Academy, Alex, Aradel, Beta Glass, BUA Foods, Cadbury, Cutix, Dangote Sugar, Ellah Lakes, Fidson, Geregu, Lafarge (HBMNG), Honeywell, Japaul Gold, Livestock, May & Baker, NB, Neimeth, Nestlé, NNFM, Seplat, Transcorp Power, Unilever and Vitafoam.
- **The H3 robustness sample** (pre-listing years included) has the same 28 firms. Aradel and Transcorp Power each gain a third year.
- **Still one year (tier 2, H3 only):** the 28 firms listed in section 5.1 tier 2. This includes Mecure, whose FY2025 is its only document.
- **Fiscal-year spread of main-analysis documents:** most tier-1 second years are FY2020. The exceptions are BUA Foods FY2022, Geregu FY2022, Japaul Gold FY2021 and Aradel/Transcorp Power FY2024.

### 6.7 Next steps (not started)

1. Owner: tier-2 downloads (28 firms, H3 only), when wanted.
2. Build and freeze the site-mention dictionary (f5).
3. Validation (g) on the narrative paragraphs before any outcome is computed.

## 7. Step 4: dictionaries, codebook and validation sample (2026-11-17)

**Not done:** no dictionary count on the corpus, no Y measure. ClimateBERT was not run to score the corpus. The detector and specificity models were run on the validation frame **only to form the sample strata** (owner decision, A19). No corpus-level share was computed or reported from them.

**Amendments logged before each step:**

| Amendment | What it covers |
|---|---|
| A17 | Dictionary matching rules and site-dictionary source |
| A18 | One external coder replaces the owner |
| A19 | Sample frame, allocation and caps |

The freeze record with all hashes is in `docs/amendments.md`.

### 7.1 Dictionaries (frozen before any count)

- **`config/dictionary_hazard.json`:** the design's 16 terms, unchanged.
  - **Matching:** case-insensitive whole words, regular plurals, hyphen or space.
  - **Not matched:** forms such as "flooded" and "water-stressed". Validation item (iii) checks what this misses.
  - **Bare "heat"** is kept until validation (OD-11).
- **`config/dictionary_sites.json`:** 214 sites of 59 tickers, from `data/processed/facilities.csv`.
  - **Coverage:** 173 sites carry 165 distinct proper-name terms. 41 sites have no nameable term (mostly dispersed or generic records).
  - **Ambiguity:** 52 terms are flagged (shared by 2 or more firms, major place, common word, other sense, or firm-name collision).
  - **Rules R1–R3** are in A17. A term flagged as ambiguous needs a facility word in the same sentence; the others need one in the same paragraph.
- **Builder:** `src/phase4_dictionaries.py` (deterministic).

### 7.2 Codebook

`docs/coding_guide.md` is the codebook of design g.
- **Items:** the five items of g in plain English, each with inclusion and exclusion rules and worked examples.
- **Practice:** five practice paragraphs with answers.
- **Source of all examples:** the Phase 0 test document (DANGCEM_2025_SRX), which is excluded from the sample.
- **Status:** frozen before coding.

### 7.3 Validation sample

**Frame:** 15,293 model-eligible narrative paragraphs of main-census firms, without DANGCEM_2025_SRX.

**Sample:** 200 paragraphs from 37 firms, with at most 10 per firm and 19 from FS-type documents.

**By cell** (equal allocation of about 33 per cell, A19):

| Detector prediction | Hazard-tagged | Untagged |
|---|---|---|
| Not climate | 17 | 50 |
| Climate, specific | 14 | 52 |
| Climate, non-specific | 19 | 48 |

The tagged cells are below target: one has too few paragraphs in the frame, and the other two were cut by the per-firm cap.

| File | Content | Who sees it |
|---|---|---|
| `data/interim/validation_sample.csv` | id, firm, year, text; pass-1 order | the coder |
| `data/interim/validation_sample_pass2.csv` | the same 200 rows in a new random order (seed + 1); for the second pass, at least 7 days later | the coder |
| `data/interim/validation_strata.csv` | cell, model probabilities, hazard tag, inclusion weight | not the coder |

### 7.4 Next steps

1. **Owner:** give the external coder `docs/coding_guide.md` and `validation_sample.csv`, with a coding sheet. Record the coder's identity and dates outside the repository.
2. **Coder:** do pass 2 at least 7 days after pass 1, using `validation_sample_pass2.csv`.
3. **Then:** compute intra-coder alpha and the model-against-human kappa/F1, unweighted and weighted. Take the OD-11 decision on bare "heat". Only then score the corpus.

## 8. A20: human validation dropped; dictionary outcomes (2026-11-17)

**Not done:** no count, measure or corpus-level share was computed.

- **Status:** section 7's validation plan (A18, A19) is **superseded and not used**. These are kept as records:
  - `docs/coding_guide.md` (now marked "not used");
  - `validation_sample.csv`, `validation_sample_pass2.csv` and `validation_strata.csv`;
  - `validation_predictions.csv`.
- **No codes:** no paragraph was coded by a person or by AI, and no AI codes are stored.
- **Main outcomes (dictionary only, no climate filter):**
  - Y3d: hazard-tagged ÷ scored narrative paragraphs.
  - Y4d: hazard-tagged paragraphs naming a firm site.
  - Y4s: Y4d ÷ hazard-tagged paragraphs.
  - Y4r: Y4d ÷ scored paragraphs.
- **Hypotheses:**
  - H1: primary Y4s; secondary Y3d and the Y4d binary.
  - H2: primary Y3d; secondary Y4s.
  - H3: τ(Y3d) vs τ(Y4r).
  - The ClimateBERT outcomes and the ClimateBERT version of H3 are exploratory and unvalidated.
- **OD-11:** bare "heat" dropped and "extreme heat" added, by a pre-set rule. The hazard dictionary is re-frozen (SHA-256 `8d7456ab…8574`).
- **Precision check (A20):** one external person answers one yes/no question per snippet. Precision is reported overall and per family with exact 95% intervals.
  - If overall precision is below 0.80, H1–H3 are reported as descriptive only.
  - Terms with precision below 0.50 (n ≥ 5) are listed as limitations.
- **Sample:** the draw under the A20 caps yielded 46 snippets, not 100, from 17 firms, at most 5 each.
  - **By family:** flood 14, storm 8, drought / water stress 10, heat 3, coastal / erosion / sea level 11, wildfire 0.
  - **Owner decision (before any count):** keep the 46 as drawn. Heat and wildfire precision cannot be estimated and are listed as limitations.
  - **Files:** `data/interim/precision_sample.csv` (id, firm, year, term, snippet) and `src/phase4_precision_sample.py`.
- **Next:**
  1. The owner gives the 46 snippets to one external person, together with the question.
  2. Then compute precision and apply the A20 rule.
  3. Only then compute the outcome measures.

## 9. Precision results, outcome measures and Phase 4 close (2026-11-17/18; A21)

### 9.1 Precision check (A20) and its consequence

**Precision:** one external helper (C1) checked 46 snippets.
- **Overall: 30/46 = 0.65.** Exact 95% interval 0.50–0.79; Wilson 0.51–0.77.
- **By family:**

  | Family | Correct / checked |
  |---|---|
  | Flood | 13/14 |
  | Storm | 1/8 |
  | Drought / water stress | 9/10 |
  | Heat | 3/3 |
  | Coastal / erosion / sea level | 4/11 |
  | Wildfire | 0/0 |

- **Full table:** `data/interim/precision_results.csv`.

**The A20 rule applied:**
- **Overall precision is below 0.80, so H1–H3 are reported as descriptive only.**
- **Limitations** (terms below 0.50 with n ≥ 5): **storm** (1/8) and **erosion** (2/6).
- **Noted:** coastal (1/4, n < 5).
- **Not estimable:** heat and wildfire.

**Exploratory refined dictionary (A21, post hoc):**
- The frozen dictionary minus storm, erosion and coastal (13 terms), in `config/dictionary_hazard_refined.json`.
- It was chosen after seeing the precision results, so its precision on the same sample (26/28) is optimistic.
- The frozen dictionary stays the main one; both are reported.

### 9.2 Outcome measures

`data/processed/outcomes_firm_year.csv` has one row per firm-year: 103 in all, 100 main census and 3 robustness. Each row carries:
- **Identifiers:** stratum, the A16 `h3_main` flag, document types, `fs_only` and `n_scored`.
- **Dictionary measures**, frozen (main) and `_refined`: Y3d, Y4d (count and `_any`), Y4s and Y4r.
- **Exploratory, unvalidated ClimateBERT measures (`_cb`):** Y1, Y2, TCFD-category shares and sentiment shares.

**Main census descriptives (the 98 firm-years with scored paragraphs; Cadbury FY2022 and FY2025 have none):**

| Measure | Frozen dictionary | Refined (exploratory) |
|---|---|---|
| Firm-years with no hazard-tagged paragraph | 68 of 98 | 74 of 98 |
| Y3d, mean (max) | 0.003 (0.026) | 0.002 (0.026) |
| Firm-years with any site-named hazard paragraph (Y4d > 0) | 8 | 8 |
| Y4s defined (firm-years with ≥ 1 tagged paragraph) | 30 (mean 0.13) | 24 (mean 0.20) |

| ClimateBERT (exploratory, unvalidated) | Value |
|---|---|
| Y1, median (max) | 0.08 (0.46) |
| Y2, median, over the 77 firm-years with any climate paragraph | 0.43 |

**Reading these figures:**
- Hazard language is rare in the narrative text, and site-named hazard paragraphs are rarer still: 8 firm-years.
- That leaves little variation for H1 (Y4s) and the Y4 side of H3.
- These descriptives are not tests. H1–H3 are descriptive only (A20 rule) and are estimated in Phase 5.

### 9.3 Phase 4 summary

| Item | Result |
|---|---|
| Corpus | 107 documents, 12,143 pages, 103 firm-years (100 main census) |
| Paragraphs | 196,812 rows; 15,601 scored narrative paragraphs |
| Text fixes | OCR A2/A12; page selection A3–A5; ligatures A13; control characters A15; section tagging A14 |
| Main dictionaries | hazard dictionary (16 terms, OD-11 by rule) and site dictionary (214 sites, R1–R3), frozen before any count (A17, A20) |
| Validation | human validation dropped (A20); dictionary precision 0.65, so H1–H3 are descriptive only (A21) |
| Outcomes | dictionary measures (main, plus refined exploratory) and ClimateBERT measures (exploratory, unvalidated) per firm-year |
| Not done | Y5 (site ever named, H4); any H1–H3 model |

**Open limitations to carry into the paper:**
- The dictionary has low precision for storm, erosion and coastal; heat and wildfire precision is unknown.
- Recall is not measured.
- The site dictionary was not validated, and its ambiguity rule (R2) was the analyst's proposal.
- The ClimateBERT outcomes are unvalidated.
- 28 main-census firms have one year only (tier 2 not collected), so they do not contribute to H3 (section 6.6).

### 9.4 Next (Phase 5)

1. Compute Y5 (site ever named) for H4.
2. Estimate H1–H3 as descriptive analyses on the frozen-dictionary outcomes, with refined and ClimateBERT versions as exploratory, under the A16 sample rule. Use the specifications in design h, with no confirmatory claim (A21).
3. H4 (descriptive).
