# Phase 0 feasibility audit

**Project:** Disclosed vs exposed: physical climate risk at Nigeria's listed companies
**Date:** 2026-11-07
**Scope:** This document records access and feasibility only. No hazard scores, models or content results were produced.

Sources and licences are listed in `docs/data_sources.md`. The supporting files are in `data/interim/`:

- `fetch_log.csv`: every request made
- `pilot_report_inventory.csv`: one row per report file
- `facility_locatability.csv`: one row per facility
- `api_access_tests.json`: NASA POWER and Overpass tests
- `nlp_smoke_test.json`: ClimateBERT smoke test
- `extraction_comparison.json`: PyMuPDF versus pdfplumber
- `fs_firm_full_report_check.json`: listing check for full annual reports at firms with financial-statement filings only
- `ngx_census_frame.csv`: census frame, one row per ticker in the 06 Nov 2026 NGX list, with stratum, board flag and the source of each assignment
- `firm_ticker_map.csv`: pilot firm identifiers mapped to NGX tickers, including the Lafarge-to-HBMNG rename and Flour Mills' delisting, with sources

Two terms are used throughout:

- **"Not verified"** means the fact could not be confirmed from a primary page that was actually read.
- **"Not tested — file not supplied"** means the item depended on a file the owner planned to add to `data/raw/manual/`, and that file was not there.

**Update (2026-11-07, second pass).** This version records three owner decisions on scope:

1. The sample is defined as a census.
2. Firms with financial-statement filings only are kept.
3. OpenStreetMap may supply locations.

It also adds six owner-supplied files, which extend Tasks 3 and 4 to MTN, Nestlé, Unilever, Nigerian Breweries and Seplat.

---

## (a) Results by task

### Task 1: Project setup

| Item | Status |
|---|---|
| Folders `docs/`, `data/raw/`, `data/interim/`, `src/`, `notebooks/` | Present |
| `README.md` (one paragraph), `.gitignore` (includes `data/raw/`), `requirements.txt` | Present. `requirements.txt` was extended with pymupdf, pdfplumber, torch (CPU) and transformers |
| `.venv` | Python 3.12.10; torch 2.15.0+cpu and transformers 4.57.6 import correctly |
| Scripts | `src/polite_fetch.py` (robots-aware, at least 2 s between requests), `src/download_pilot.py`, `src/test_api_access.py`, `src/test_overpass_narrow.py`, `src/compare_extractors.py`, `src/smoke_test_climatebert.py`, `src/register_manual.py` (adds owner-supplied files to the inventory), `src/classify_asset_type.py` (point or dispersed), `src/build_ngx_frame.py` (census frame and strata), `src/relink_manual.py` (points the inventory at the subfolder copies and lists loose duplicates), `src/apply_estate_rule.py` (rule C1), `src/add_ticker_to_facilities.py` (ticker and census status) |
| Git | No git commands were run |

### Task 2: Company universe

| Item | Result |
|---|---|
| Official NGX list of equities | **Supplied by the owner:** `data/raw/manual/ngx/ngx_equities_price_list_2026-11-06.csv`. It holds 146 tickers, with trade date 06 Nov 2026. The owner copied it in a browser from https://ngxgroup.com/exchange/data/equities-price-list/ on 2026-11-07; provenance is in `SOURCE.txt`. The list has tickers and prices only: **no issuer names and no sectors**. My own automated requests to `ngxgroup.com` had returned HTTP 403 |
| NGX sectors | **Not available from NGX.** The industry-sector page on doclib (https://doclib.ngxgroup.com/issuers/listing-your-company/industry-sector) returned a SharePoint error on both attempts, 2026-11-07. No official list of equities by sector was found in searches. **All sector labels below are therefore provisional** |
| Secondary sector counts | Intelpoint (2025), citing NGX, reports 147 listed companies: Financial Services 44, Services 20, Consumer Goods 20, Industrial Goods 13, Construction/Real Estate 10, ICT 8, Oil and Gas 8, Healthcare 7, Agriculture 5, Utilities 2 |
| Consistency of the secondary counts | **These sector counts add up to 137, not 147.** The same page also gives two different shares for Financial Services (29.25% and 29.93%). Treat the figures as indicative only |
| Sectors with significant physical assets in Nigeria (secondary counts) | Consumer Goods 20, Industrial Goods 13, Construction/Real Estate 10, Oil and Gas 8, ICT 8, Agriculture 5 = **64**. This is an upper bound: it includes real estate and non-telecom ICT firms. Breweries fall under Consumer Goods. A firm-by-firm marking was not possible without the official list |

**Sample definition (owner decision, 2026-11-07): a census, expected to contain 50–60 firms.** The sample includes every NGX-listed firm that meets both tests:

1. **Physical operations test.** The firm has physical operations in Nigeria: at least one production, processing, plantation, terminal or network site, according to its own report.
2. **Document test.** A full annual report is available for at least one year from 2023 to 2025.

Unlisted firms are excluded. Banks, insurers, other financial firms, real estate investment trusts and pure holding companies have no physical operations and drop out under test 1.

**Census frame.** The frame was built from the supplied list by `src/build_ngx_frame.py`, with one row per ticker in `data/interim/ngx_census_frame.csv`. That file records each ticker's identified issuer, provisional sector, classification and the source of each assignment.

**Sources of the assignments:**

- **Pilot issuers (14 tickers, including HBMNG):** whether a firm has physical operations comes from its own report, which is in the project.
- **All other tickers:** an analyst identification of the ticker, marked "not verified — confirm in Phase 2 from a primary source".
- **Sector labels:** provisional for every ticker, because no NGX sector source was available and no report read states its NGX sector.
- **Unidentified tickers:** marked unresolved rather than guessed.

| Step | Tickers | Detail |
|---|---|---|
| NGX list, 06 Nov 2026 | 146 | |
| Removed: funds, REITs and other non-operating instruments | 8 | AVAIF, CNIF, MOFIREIF, NIDF, NREIT, SFSREIT, UHREIT, UPDCREIT. Reason: listed as non-operating issuers in the owner's `SOURCE.txt` |
| Operating issuers | 138 | |
| Financial or services, no significant physical sites | 51 | Banks, insurers, mortgage and microfinance banks, other financial firms, ICT and software, media, publishing |
| **Main census: core firms with physical operations in Nigeria** | **59** | **50 mainly point sites, 9 mainly dispersed assets** |
| Borderline (robustness stratum, not in the main census) | 18 | ABCTRANS, CAVERTON, CHELLARAM, EKOCORP, IKEJAHOTEL, JOHNHOLT, JULI, NAHCO, REDSTAREX, RTBRISCOE, SCOA, SKYAVN, TANTALIZER, TRANSCOHOT, TRANSCORP, TRANSEXPR, UACN, UPDC. These are hotels, aviation handling, logistics, hospitals, restaurants, property development, and conglomerates or holding companies with operating subsidiaries |
| Unresolved: issuer not identified with confidence | 10 | AFRINSURE, AVACAP, BAPLC, CMFC, FTGINSURE, HMCALL, NSLTECH, OMATEK, RONCHESS, ZICHIS |

**Dispersed-asset firms (9):** AIRTELAFRI, ARADEL, CONOIL, ETERNA, JBERGER, MTNN, OANDO, SEPLAT, TOTAL. These are telecom networks, oil and gas licences, fuel retail networks and construction project sites. MTN and Seplat also have point sites.

**Provisional sectors of the 59 core firms:** Industrial Goods 17, Consumer Goods 17, Oil and Gas 6, Agriculture 6, Healthcare (pharmaceutical manufacturing) 6, ICT 2, Utilities (power plants) 2, Natural Resources 2, Construction/Real Estate 1.

**Final census count (owner decisions, 2026-11-07).** The census has two strata, recorded in the `census_stratum` column of `data/interim/ngx_census_frame.csv`:

| Stratum | Firms | Rule |
|---|---|---|
| **Main census** | **59** | Core firms with physical operations in Nigeria: 50 mainly point sites, 9 mainly dispersed assets |
| Robustness stratum | 18 | The borderline firms, excluded from the main census |
| Excluded | 69 | 51 with no significant physical sites, 8 funds and REITs, 10 unresolved tickers (until identified) |
| **Total** | **146** | |

**Document test in the main census.** It has passed for 14 firms, the pilot firms with reports in hand (including HBMNG, through Lafarge Africa's reports), and is pending for the other 45. The main census will shrink by however many of those 45 fail the test.

**Board flags (owner rule).** A firm is excluded only if its flag means suspended or delisting. **No legend was found:** three NGX weekly market reports were checked (two hosted on mondovisione.com, one on doclib.ngxgroup.com), and a targeted search turned up nothing. Every flag's meaning is therefore recorded as "not verified", and **no firm was excluded on its flag**. The flag stays as a variable (`board_flag`, with `board_flag_meaning` set to "not verified").

**Main-census firms carrying a flag (10):** ALEX [BMF], AUSTINLAZ [RST], FTNCOCOA [RST], GOLDBREW [BMF], MORISON [BLS], MULTITREX [DWL], PHARMDEKO [MRS], PREMPAINTS [RST], THOMASWY [RST] and UNIONDICON [DWL]. If a flag such as DWL turns out to mean delisting, the firms carrying it would leave the census.

**Sector and issuer labels.** All analyst identifications are marked "not verified — confirm in Phase 2 from a primary source".

**Pilot firms in the list.** 14 of the 15 pilot firms appear:

- **Present:** DANGCEM, BUACEMENT, GUINNESS, OKOMUOIL, PRESCO, BETAGLAS, INTBREW, CADBURY, MTNN, NESTLE, UNILEVER, NB and SEPLAT.
- **Lafarge Africa = HBMNG.** Lafarge Africa Plc was renamed HBM Nigeria Plc, and its trading symbol changed from WAPCO to HBMNG. Sources:
  - The NGX Regulation Market Bulletin NGXREG/IRD/MB76/26/07/09 of 09 July 2026 states: "the change of name of Lafarge Africa Plc (the Company) to HBM Nigeria Plc has been implemented by Nigerian Exchange Limited… the Company's trading symbol has also been changed from WAPCO to HBMNG."
  - Nairametrics reported the symbol change on 13 July 2026.

  The rename followed Huaxin's acquisition of the majority stake, according to your account and press coverage seen in search. Lafarge's files and facilities are mapped to HBMNG in `data/interim/firm_ticker_map.csv` and `facility_locatability.csv`.
- **Flour Mills of Nigeria: removed from the census, being delisted.** NGX suspended trading on 16 December 2024, and the shares were delisted from the Daily Official List effective 30 December 2024 (Nairametrics, 5 January 2025, citing NGX's first weekly market report of 2025). The stock is absent from the 06 Nov 2026 list. Its pilot evidence (one report, five facility rows) is kept only as a methods note. The secondary upper bound is 64 firms in physical-asset sectors, so a census of about 50–60 is plausible but not verified.

**Pilot firms.** All 15 appear to pass the document test:

- **Full 2025 or 2024 reports in hand:** 11 firms (Dangote, BUA, Guinness, Okomu, Presco, MTN, Nestlé, Unilever, Nigerian Breweries, Seplat, Beta Glass). Beta Glass's latest report in hand is for 2023.
- **Listing entries only:** for International Breweries, Lafarge, Flour Mills and Cadbury, the evidence is africanfinancials.com annual-report entries for 2023–2025 (Flour Mills: 2023–2024). Their content is not verified (see `docs/data_sources.md`).

**Firms with financial-statement filings only (owner decision).** These firms are kept. The Phase 1 data will record whether a full annual report exists on africanfinancials.com or doclib.ngxgroup.com, and the owner will download such reports by hand. Where only financial statements exist, the firm stays in the sample with document type as a control variable. "No narrative disclosure" is recorded as a finding in its own right.

### Task 3: Report availability (pilot of 15 firms)

Key to the tables:

- **D** = downloaded and tested
- **L** = link found on a permitted source but, by owner decision, not downloaded in Phase 0
- **S** = appears only in search results or third-party listings; not verified
- **—** = not located
- **NT** = not tested — file not supplied, or download failed

All downloaded files are PDF. "Text" means a text layer was found on at least 80% of pages.

**Annual reports.** Each Fiscal Year column is the year the company's financial year ends. Guinness's year ends in June and Flour Mills' in March.

| Firm | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | Source of downloaded files |
|---|---|---|---|---|---|---|---|
| Dangote Cement | D text | — (report exists per the 2022 report, p14; only chairman and CEO extracts found) | D text | D text | D text | D text | Company site |
| BUA Cement | D text | D text | D text | D text | D text | D text | Company site |
| Guinness Nigeria | D text | D text | D text | D text | D text | D text | Company site |
| Okomu Oil | D **no text layer** | D text | D text | D **no text layer** | D **no text layer** | L | Company site |
| Presco | — | L | — | L | L | D text | Company site |
| MTN Nigeria | L | L | L | L | L | D text (supplied manually; automated download failed twice) | Company site / owner |
| Beta Glass | — | S | S | D text | S | S | Registrar (Greenwich) |
| International Breweries | — | — | L | D text (FS) | — | S | NGX filings library |
| Lafarge Africa | L | — | L | D text (FS) | S | S | NGX filings library |
| Flour Mills of Nigeria | — | — | — | L (FY to Mar 2023) | D text (FS, FY to Mar 2024) | — | NGX filings library |
| Cadbury Nigeria | — | S | D text (unaudited) | S | S | D text (unaudited) | NGX filings library |
| Nestlé Nigeria | NT | NT | NT | NT (S) | NT (S) | D text (supplied manually) | Site blocked (HTTP 403); owner-supplied |
| Unilever Nigeria | NT | NT | NT | NT (S) | NT (S) | D **garbled text layer** (supplied manually) | Site blocked (HTTP 403); owner-supplied |
| Nigerian Breweries | NT | NT | NT | NT (S) | NT (S) | D mixed, 77% of pages with text (supplied manually) | Site blocked (robots.txt HTTP 403); owner-supplied |
| Seplat Energy | NT | NT | NT | NT | NT (S) | D text: integrated annual report (supplied manually) | Site blocked (robots.txt HTTP 403); owner-supplied |

"FS" marks filings that the NGX library names "financial statements". Lafarge's and Flour Mills' filings are titled "Annual Report", but the share of narrative in them was not assessed. Both Cadbury files describe themselves as "Un-audited" year-end statements. The Cadbury 2022 file name says "AUDITED", but its title page says "Un-audited Interim Financial Information".

**Separate sustainability reports.**

| Firm | Status |
|---|---|
| Dangote Cement | The 2022 report says "we have combined our Annual Report and our Sustainability Report" (p2). It also records that a "2021 combined Annual and Sustainability Report" was released (p14), but no PDF of that 2021 report was located. The 2024 and 2025 "Sustainability Report" PDFs are extracts of the annual report (D text, 72 and 52 pages) |
| BUA Cement | None found on the company's sustainability page |
| Guinness Nigeria | S only: third-party listings for 2020–2023. None found on the company pages read |
| Okomu Oil | 2022: L (company site). 2024: D text (48 pages) |
| Presco | None found |
| MTN Nigeria | 2020–2024: L, with iXBRL versions for 2023–2025 also listed. 2025: D text (174 pages, supplied manually) |
| Beta Glass | None found. The company site links a "Socio Economic Impact Assessment Report 2025", which was not downloaded |
| International Breweries, Lafarge, Flour Mills, Cadbury | Lafarge 2022 and 2023, and Flour Mills 2020/21 and 2021/22: S only. The others: none found |
| Nestlé, Unilever | S only: sustainability reports are listed on the company pages, according to search snippets. Not tested — file not supplied |
| Nigerian Breweries | No separate report supplied. The 2025 annual report's contents list a "2025 Corporate Social Responsibility and Sustainability Report" section (p3) |
| Seplat Energy | **Shift from standalone sustainability reports to an integrated annual report.** The owner reports that standalone Sustainability Reports ran up to 2023, followed by an Integrated Annual Report for 2024–2025. The 2025 file confirms part of this: it is titled "Seplat Energy Plc Integrated Annual Report 2025", and its contents list a "Sustainability Report" section (p2). The 2024 integrated report and the 2023 standalone report were not in hand, and Seplat's site refused automated access, so those parts of the sequence are not verified. A search snippet seen earlier described Seplat's sustainability-reports page as listing a 2023 Sustainability Report and older TCFD reports, which is consistent with the owner's account. The 2023 Sustainability Report and the 2025 Social Performance Report: pending — owner to supply before Phase 6 (non-blocking) |

**Text extraction.** All 38 files (32 downloaded and 6 supplied manually) were measured with PyMuPDF.

- **33 files have a usable text layer.** Text-page shares range from 0.82 (Guinness) to 1.00.
- **3 files have no text layer: Okomu's 2020, 2023 and 2024 annual reports.** In those files, 69 of 69, 25 of 96 and 28 of 115 pages contain images. The remaining pages carry no extractable text either. **Okomu therefore needs OCR or manual reading.**
- **Nigerian Breweries' 2025 report is mixed:** 138 of 179 pages (77%) have text.
- **Unilever's 2025 report has a garbled text layer.** The test counts it as "extractable" because 85.8% of pages contain characters. But the font maps each letter to an unrelated glyph: for example, "ŬľśċǕċƙdľĩċƙľÒ" reads as "nileverNigeria". **A character-count test cannot catch this.** Phase 1 should add a readability check, such as the share of common English words, and should treat files like this as needing OCR. Unilever's facility entries were read from page images, with letters decoded using a map checked against those images.

PyMuPDF and pdfplumber were also compared on a 10-page sample from each of three reports:

| Report | PyMuPDF characters | pdfplumber characters | Ligature or odd glyphs (PyMuPDF / pdfplumber) | Note |
|---|---|---|---|---|
| Dangote 2025 sustainability extract | 26,156 | 25,692 | 0 / 0 | Clean text from both |
| Guinness 2025 annual report | 24,804 | 23,565 | 46 / 0 | PyMuPDF keeps ligature characters such as "ﬁ". Unicode NFKC normalisation fixes this |
| Okomu 2024 annual report | 0 | 0 | 0 / 0 | No text layer: OCR or manual reading needed |

Ligature characters also appear in Okomu's 2022 report (for example "oﬃce"), and the 2021 report contains odd glyphs (for example "MarkeƟng"). Two-column layouts, such as Guinness's corporate information page, run the columns together in reading order. Addresses on such pages had to be matched to headings by hand (see Task 4).

### Task 4: Facility locatability

**Sources used**, as the latest readable report per firm:

- Dangote 2025 annual report, BUA 2025 annual report, Guinness 2025 annual report
- Okomu 2022 annual report and 2024 sustainability report (its 2023 and 2024 annual reports have no text layer)
- Presco 2025 annual report, Beta Glass 2023 annual report
- International Breweries 2023, Lafarge 2023, Flour Mills FY2024 and Cadbury FY2025 filings
- Owner-supplied 2025 reports: MTN annual report and sustainability report, Nestlé annual report, Unilever annual report (read from page images), Nigerian Breweries annual report, and Seplat integrated annual report

**Method.** Each facility named in these reports was recorded with its location as written and the page number. Every row is in `data/interim/facility_locatability.csv`. Ratings:

- **A** = exact coordinates or full address
- **B** = town or industrial estate
- **C** = state only
- **D** = location not stated

**Grading rule C1 (owner decision, 2026-11-07):**

- A location given only by local government area is grade **C**.
- An estate name without a town is grade **B** only if the estate can be matched to a unique location, either in the report text or in OSM. Otherwise it is grade **C**.

Under this rule, Presco's six estates (Cowan, Ologbo, ATO, Elele, Ubima, Sakponba) moved from B to C, because no unique match was found in the report text read or in the OSM results. Okomu Extension 2 stays C, being located only by local government area.

| Firm | Facilities listed | A | B | C | D |
|---|---|---|---|---|---|
| Dangote Cement | 9 | 1 | 7 | 0 | 1 |
| BUA Cement | 6 | 3 | 2 | 0 | 1 |
| Guinness Nigeria | 4 | 3 | 1 | 0 | 0 |
| Okomu Oil | 4 | 0 | 1 | 1 | 2 |
| Presco | 8 | 1 | 0 | 6 | 1 |
| Beta Glass | 3 | 1 | 2 | 0 | 0 |
| International Breweries | 2 | 1 | 0 | 0 | 1 |
| Lafarge Africa (now HBM Nigeria, HBMNG) | 5 | 1 | 4 | 0 | 0 |
| Flour Mills of Nigeria (delisted; methods note only) | 5 | 1 | 3 | 0 | 1 |
| Cadbury Nigeria | 2 | 1 | 0 | 0 | 1 |
| MTN Nigeria | 5 | 2 | 0 | 0 | 3 |
| Nestlé Nigeria | 4 | 1 | 3 | 0 | 0 |
| Unilever Nigeria | 4 | 1 | 2 | 0 | 1 |
| Nigerian Breweries | 21 | 17 | 4 | 0 | 0 |
| Seplat Energy | 12 | 1 | 4 | 0 | 7 |
| **All 15 firms** | **94** | **35 (37.2%)** | **33 (35.1%)** | **7 (7.4%)** | **19 (20.2%)** |
| **Operational sites only** (excluding 22 offices: registered, corporate and sales) | **72** | **15 (20.8%)** | **31 (43.1%)** | **7 (9.7%)** | **19 (26.4%)** |
| First 10 firms only, operational sites (first pass, before rule C1, for comparison) | 40 | 5 (12.5%) | 26 (65.0%) | 1 (2.5%) | 8 (20.0%) |

**Main census only.** Flour Mills is a methods note. That leaves 14 pilot firms with 68 operational sites, graded A 15 (22.1%), B 28 (41.2%), C 7 (10.3%) and D 18 (26.5%). Of these, 61 are point sites, graded A 15 (24.6%), B 28 (45.9%), C 7 (11.5%) and D 11 (18.0%). Lafarge's sites are now counted under HBMNG.

Nigerian Breweries alone accounts for 10 of the 15 grade A operational sites. Its report lists every brewery, malting plant and distribution centre with a road-level address (p8). Without Nigerian Breweries, grade A falls to 5 of 60 operational sites.

**Points that affect the ratings:**

- **Grade A operational sites.** Among the first 10 firms, only five operational sites have a full address. Nigerian Breweries adds 10 more:
  - BUA Obu plant: "Km 164, Benin-Okene Expressway Okpella Edo State"
  - BUA Sokoto plant: "Km 10, Kalambaina Road Sokoto State"
  - Guinness Ogba and Benin breweries (road and industrial estate)
  - Presco's Obaretin Estate: "Km 22, Benin-Sapele Road"
- **No coordinates.** None of the reports read gives coordinates.
- **Little site detail in financial-statement filings.** These name a registered office and few or no sites. The International Breweries filing names no brewery locations.
- **Location description varies within one report.** Dangote's 2025 report names its export terminals as "Apapa and Onne" (p19) and as "Apapa and Port Harcourt" (p16). Its depots are mentioned but not named.
- **Okomu.** Okomu's Extension 1 has no location in the pages read. Extension 2 is located only by local government area: "Ovia NE LGA/Uhunmwonde LGA".
- **Seplat.** 7 of Seplat's 12 entries are D. Its licence areas (OMLs 4, 38, 41, 40, 53, 56, 67, 68, 70 and 104), the ANOH gas plant and the offshore Yoho platform carry no town, state or geometry in the passages read. Licence areas are classed as dispersed assets (see below). Licence-block boundaries are out of scope.
- **MTN.** MTN's network (base stations, switching centres and the Dabengwa Tier III data centre) is counted or named but not located.
- **Nestlé.** Nestlé names its three factories by town (Agbara, Flowergate, Abaji) but gives no addresses.

**OpenStreetMap check.**

- **First query** (case-insensitive, on name, operator and brand tags): timed out on the server after 114 seconds and returned 0 features.
- **Second query** (approved by the owner; case-sensitive, name tags only, 14 firm names): returned 41 features (OSM snapshot 2026-11-07T08:18:50Z).

The name matches were compared with the facility list by hand:

- **First pass: 10 of the 40 operational sites have a candidate OSM feature:**
  - Dangote: Obajana, Gboko, and Ibese (only as "Dangote Ibese Cement Power Station")
  - BUA: Okpella and Sokoto
  - Guinness: Ogba
  - Okomu: the main estate and the rubber plant
  - International Breweries: Ilesa
  - Cadbury: Ikeja works
- **OSM locates sites the reports don't.** For two firms, International Breweries and Cadbury, OSM has a named feature for a site the report doesn't locate.
- **Noise in the results.** Many of the 41 features are unrelated, such as sports courts, a road, a hall and a canal.
- **Previously blocked firms.** OSM features also appeared for Nigerian Breweries, Unilever and Nestlé. They are matched below, now that their reports have been supplied.

These matches are by name only and were not checked against imagery or company sources.

**After adding the five new firms:** 13 of 72 operational sites have a candidate OSM feature. The three new candidates are:

- Nigerian Breweries' Ibadan brewery
- Unilever's Agbara site, which OSM tags as an office
- Nestlé's Agbara factory, where the matching feature is a staff clinic

MTN was not among the names queried, so it has no OSM candidates.

**Location source (owner decision).** OSM may supply locations that reports don't give. The facility table now has a `location_source` column, set to `report` or `osm`, and keeps the A–D grade, which always describes the report. Three operational sites currently take their location from OSM: International Breweries' brewery (Ilesa), Cadbury's factory (Ikeja) and Okomu's rubber factory. Attribution: "© OpenStreetMap contributors", ODbL.

**Asset-type classification (owner decision, 2026-11-07).** The facility table now has an `asset_type` column. Two kinds of asset are distinguished:

- **Point sites:** plants, breweries, factories, mills, terminals, flow stations, platforms, distribution centres, data centres and plantation estates. Each is a single site that can be located.
- **Dispersed assets:** oil and gas licence areas, telecom networks, and unnamed networks of many small sites, such as Dangote's depots.

Dispersed assets will be measured at state or area level and analysed separately from point sites. Licence-block boundaries are out of scope. Global Energy Monitor oil and gas field coordinates are an optional extra for Phase 2; their licence is described as open, but this is to be verified and the data were not accessed in Phase 0. Plantation estates (10 sites) count as point sites but are bounded areas, flagged in `asset_note`, so a polygon is preferable to a single point.

| Operational sites (offices excluded) | Total | A | B | C | D |
|---|---|---|---|---|---|
| Point sites | 65 | 15 (23.1%) | 31 (47.7%) | 7 (10.8%) | 12 (18.5%) |
| Dispersed assets | 7 | 0 | 0 | 0 | 7 (100%) |
| All operational | 72 | 15 (20.8%) | 31 (43.1%) | 7 (9.7%) | 19 (26.4%) |

The 7 dispersed assets are:

- Dangote's depots
- MTN's switching centres and base stations
- Four groups of Seplat licence areas (OML 4, 38, 41; OML 53, 56; OML 40; OML 67, 68, 70, 104)

**Grades for dispersed assets.** All seven are D, because the passages read give no state or area.

**Where state or area for dispersed assets may come from (owner decision, 2026-11-07).** In this order:

1. Other parts of the company's own reports
2. Global Energy Monitor, once its licence has been verified
3. Public regulator records, for example NUPRC and NCC

The source of each assignment will be recorded in `location_source`, and the same access rules apply as for everything else.

**Extra location sources for point sites (owner decision, 2026-11-07).** Environmental impact assessments, company websites and regulator records are in scope under the same access rules, with `location_source` recorded.

**Planned robustness check (Phase 1 onward).** Every exposure result will be run twice:

- (i) with all locations, from both reports and OSM
- (ii) with report-only locations, dropping sites whose location comes only from OSM

Differences between the two runs will be reported.

**Verdict on site-level analysis.** Feasible in a narrowed form:

- **Location quality.** The largest group of operational sites is located to town or industrial-estate level (grade B, 43% after rule C1). Grade A addresses are concentrated in one firm (Nigerian Breweries). About a quarter of operational sites are not located at all (grade D), and most of those are oil and gas licence areas and telecoms networks.
- **What works at that precision.** Analysis is feasible for the coarser hazards: Aqueduct sub-basins, NASA POWER and ERA5 grids.
- **What doesn't.** The roughly 90 m JRC flood maps need each grade B site to be located more precisely first, for example from OSM polygons. Otherwise scores need an explicit uncertainty buffer.

### Task 5: Hazard data access

| Dataset | Access tested | Resolution | Years | Licence | Size | Account |
|---|---|---|---|---|---|---|
| WRI Aqueduct 4.0 (baseline water stress and other water risk indicators) | Data pages read. Zip file not checked: robots.txt for `files.wri.org` disallows it | HydroBASIN level 6 | Baseline plus 2030, 2050, 2080 (baseline period not verified) | CC BY 4.0 | Not verified | None for download. WRI asks users who adapt or share the data to register |
| WRI Aqueduct Floods v2.0 (riverine and coastal) | Data page read | Not verified | 2010–2080; baseline plus 2030, 2050, 2080; released 2020; no flood protection modelled | Not verified | Not verified | Not verified (data explorer shows a Login link) |
| JRC Global river flood hazard maps v2.1.2 | README and folder listing read | 3 arc seconds (about 90 m) | Return periods of 10, 20, 50, 75, 100, 200 and 500 years | ODbL v1.0 | About 85 MB for the 1-in-100-year depth tiles covering Nigeria (tile-naming rule assumed) | None |
| NASA POWER daily point API | **Test passed** (robots.txt exception granted): Ota, Ogun State (6.68 N, 3.23 E); T2M, T2M_MAX, T2M_MIN, RH2M | 0.5° latitude; longitude spacing not verified; MERRA-2 meteorology | 1990-01-01 to 2025-12-31 returned; 13,149 days per parameter; 0 missing values | No licence named; citation and notification requested | 889,651 bytes for the test point | None |
| Copernicus ERA5 single levels (optional) | Dataset page read; not downloaded. **Not needed now:** NASA POWER covers Phases 0–2, and ERA5 is decided in Phase 1 (owner decision) | 0.25° | 1940 to present, hourly | CC-BY | Not checked | Free account required (the owner may create one later) |
| WorldPop Global2 R2025A, Nigeria | File size checked with HTTP HEAD | 100 m and 1 km | Annual, 2015–2030 (alpha release) | CC BY 4.0 | 157.0 MB (100 m constrained, 2025); 4.4 MB (1 km) | None |

### Task 6: NLP tools (ClimateBERT)

The smoke test ran on 20 evenly spaced text blocks of at least 40 words each, taken from Dangote's 2025 sustainability extract (155 candidate blocks). Each model ran in its own process, one paragraph at a time, on CPU with 2 threads. **As instructed, predicted labels and scores were not recorded.**

| Model | Licence | Labels | Input limit | Loaded | Valid outputs | Truncated inputs | CPU time |
|---|---|---|---|---|---|---|---|
| climatebert/distilroberta-base-climate-detector | Apache-2.0 | no, yes | 512 tokens | Yes | 20 / 20 | 0 | 5.87 s |
| climatebert/distilroberta-base-climate-specificity | Apache-2.0 | non, spec | 512 tokens | Yes | 20 / 20 | 0 | 5.35 s |
| climatebert/distilroberta-base-climate-tcfd | Apache-2.0 | governance, metrics, risk, strategy | 512 tokens | Yes | 20 / 20 | 0 | 6.18 s |
| climatebert/distilroberta-base-climate-sentiment | Apache-2.0 | neutral, opportunity, risk | 512 tokens | Yes | 20 / 20 | 0 | 9.60 s |

The test paragraphs had a median length of 80 tokens and a maximum of 182. Only models in the `climatebert` Hugging Face account were checked. That account also publishes `transition-physical`, whose labels appear only as `LABEL_0`–`LABEL_2` in its configuration file.

### Task 7: Literature and regulation scan

**Reviews and studies of Nigerian and African disclosure.** The question for each was whether it assesses physical risk at actual company sites.

| Study / review | What it covers (as read) | Physical risk at company sites? |
|---|---|---|
| IPMC ESG Ratings Report 2025 | Guardian coverage: more than 120 companies in manufacturing, financial services, oil and gas, telecoms and professional services. It flags weak climate-risk disclosure under IFRS S2, including financed emissions | No indication in the coverage read. Primary report not obtained, so not verified. A BusinessDay item seen in search attributes the release to PwC, which conflicts with the Guardian and ThisDay coverage |
| Sustainable Stories Africa, NGX30 Sustainability Report Review 2024 | Nairametrics coverage (20 October 2026): a 25-point framework across Framework Alignment, Materiality, Data Quality, Transparency and Impact Orientation | No indication in the coverage read. Primary review not obtained, so not verified. The article refers to both 15 companies and a "13-company cohort" |
| FRC Roadmap (Amended 2026), Readiness Test Assessment | Entities must submit documents including a materiality assessment of climate-related risks and a description of the models used for scenario analysis (PDF pp. 20–21) | No. In the sections read, the FRC collects entities' own documents and does not assess the hazards at their sites |
| Doorasamy, Fapetu & Adewumi (2026), *JRFM* 19(8) 598 | Text-based index for Nigeria and South Africa that includes a physical-risk dimension (description from a search result) | No: it is based on the text of disclosures |
| Yahaya (2026), Zenodo | 151 NGX firms, 2010–2024: climate risk disclosure, governance and firm performance (abstract read) | No: according to the abstract |
| "Asset-Level Physical Climate Risk Disclosure" (chapter; authors not verified) | Compares facility-level exposure from a commercial facility database with risks reported in filings and CDP responses, using pharmaceutical firms | Yes, but not for Nigeria. This is the closest method precedent found |

**Conclusion on the gap:** none found in my searches, not yet a confirmed gap. No Nigerian study comparing disclosure with site-level exposure appeared in the searches run. That does not establish that none exists, because the scan relied on web search and did not cover Scopus, Web of Science or African journal databases.

**Decoupling literature** (verified through Crossref):

- Meyer & Rowan (1977)
- Bromley & Powell (2012), which distinguishes means–ends decoupling from policy–practice decoupling
- Marquis, Toffel & Zhou (2016)
- Marquis & Qian (2014)

**ClimateBERT papers:**

- Webersinke et al., arXiv:2110.12010
- Bingler et al. (2022), *Finance Research Letters* 47, 102776
- Bingler et al. (2024), *Journal of Banking & Finance* 164, 107191

**IFRS S2 on physical risk.** The standard itself is **pending — owner to supply before Phase 6**, because the IFRS PDF requires a login. This does not block earlier phases. **No IFRS S2 text is quoted, and no paragraph numbers are given.** The FRC Roadmap (Amended 2026) paraphrases the requirements. Verified quotes from it:

- **Strategy disclosures** include the "Climate resilience of strategy and business model to both transition and physical risks." (PDF p23, printed p20)
- **Cross-industry metrics** include "Climate-related physical risks;" (PDF p25, printed p22)
- **Scenario analysis:** "An entity shall use scenario analysis for this assessment." (PDF p23)

**Regulatory timeline** (verified from primary documents):

| Instrument | Verified content |
|---|---|
| SEC circular, published 23 September 2026 | Every public company and significant public-interest capital market operator must submit an Implementation Plan "on or before 15 October 2026". Mandatory IFRS S1/S2 reporting applies for accounting periods beginning on or after 1 January 2028, and for SMEs from 1 January 2030. Voluntary adoption runs from 1 January 2024 through periods ending on or before 31 December 2027 |
| FRC Roadmap (Amended 2026) and SRG 1 2026 | Unveiled 23 February 2026, according to the FRC press release. Phases: Phase 1, early adopters, for periods ending on or before 31 December 2023. Phase 2, voluntary adopters, for 2024–2027. Phase 3, mandatory for all public-interest entities from periods beginning on or after 1 January 2028, and for SMEs from 1 January 2030. The readiness test is compulsory before an entity's first sustainability report. Assurance is required from the third year of reporting (phases PDF p19; assurance PDF p30) |
| NGX Sustainability Disclosure Guidelines | Approved by the SEC on 9 November 2018 (rule-making history, p1). The guidelines say risk management "begins with detecting key risks of operational disruptions from climate change, resource scarcity, or community issues" (p8) |

**Inconsistencies noted in sources:**

- **The figure "41".** The FRC press release says the 2024 Roadmap "positioned 41 Nigerian entities on the verge of full compliance", while the Roadmap itself says "The ARWG comprises 41 members". The two may refer to different things.
- **Phase timing.** Secondary coverage reports a possible mismatch between the timing of the SEC circular and the FRC's phase documents. The SEC text read does not itself refer to FRC phase documents.

---

## (b) Feasibility verdict per component

| Component | Verdict | Reason |
|---|---|---|
| (1) Geodatabase of company facilities | **NARROW** | **Point sites:** 46 of 65 are located to town, estate or full-address level (A or B), after rule C1. 15 have a full address (10 of them at Nigerian Breweries), and none has coordinates. **Dispersed assets:** all 7 (oil licence areas, telecom networks, depots) are ungraded D, and will be measured at state or area level and analysed separately. OSM can supply locations for point sites, with a report-only robustness check |
| (2) Hazard scoring per site | **GO** | JRC, WorldPop and NASA POWER are confirmed openly accessible, with licences and sizes known. Aqueduct 4.0's licence is confirmed, but its size is not verified. ERA5 is optional and decided in Phase 1, with NASA POWER sufficient for Phases 0–2. Grade B and C sites need uncertainty buffers for the 90 m flood maps |
| (3) NLP of reports 2020–2025 with ClimateBERT, validated by hand-coding | **GO (tooling) / NARROW (corpus)** | All 4 models run on CPU, under Apache-2.0. The corpus is uneven: some firms publish only financial-statement filings, Okomu's reports have no text layer, Unilever's has a garbled one, and Nigerian Breweries' is mixed. Blocked firms' reports depend on manual download. Hand-coding validation has not been tested |
| (4) Regression of disclosure specificity on exposure and firm characteristics | **NARROW** | Depends on sample size, which is not fixed until the official list is obtained. With roughly 50–60 firms over 6 years, firm-level clustering limits how many covariates the model can hold |
| (5) Decoupling theory | **GO** | Core literature verified |
| (6) Policy review against IFRS S2 and the FRC roadmap | **NARROW** | FRC, SEC and NGX texts verified. IFRS S2 text pending (owner to supply before Phase 6; login required) |

---

## (c) Recommended final sample and scope

**Sample.**

- **Census rule (owner decision):** all NGX-listed firms with physical operations in Nigeria that have a full annual report for at least one year from 2023 to 2025. Unlisted firms are excluded.
- **Main census: 59 firms** from the NGX list of 06 Nov 2026, before the document test. 14 have passed it and 45 are pending.
- **Robustness stratum: 18 borderline firms,** analysed separately.
- **Pilot firms:** 14 stay, with Lafarge Africa now HBMNG. Flour Mills is delisted and kept only as a methods note. Firms with financial-statement filings only stay, with document type as a control.

**Documents.**

- Annual reports and separate sustainability reports for fiscal years 2020–2025, recording the type of each document.
- Analyse financial-statement-only filings separately, or exclude them from the specificity measure, because they contain little narrative.
- Okomu's scanned reports need OCR or manual reading.

**Facilities.** Each facility record would carry:

- the location as written, its A–D grade, the asset type (point or dispersed), the location source (report or OSM), an OSM candidate and the page reference
- a geocode precision field, so that town-level sites can carry a buffer

Sites in Nigeria only. Point sites are scored at site level. Dispersed assets (oil licence areas, telecom networks) are scored at state or area level and analysed separately. Licence-block boundaries are out of scope, and Global Energy Monitor field coordinates are optional for Phase 2, once their licence is verified.

**Hazards.** Riverine flood (JRC 90 m, Aqueduct Floods), coastal flood (Aqueduct Floods), baseline water stress (Aqueduct 4.0), heat and humidity (NASA POWER for Phases 0–2; ERA5 optional, decided in Phase 1), and population around each site (WorldPop).

**NLP.** The four ClimateBERT classifiers, plus a hand-coded validation sample. Run them in Google Colab or on a machine with more memory if the full corpus is too large for local memory.

---

## (d) Top 5 risks and how to handle them

| # | Risk | Handling |
|---|---|---|
| 1 | **Location precision.** 43% of operational sites are town or estate level, 10% are state or local-government level, 26% aren't located at all, and none has coordinates. 90 m flood scores could misplace sites | Record a geocode precision for every site. Use OSM where a name matches (`location_source = osm`) and check it by hand. Apply buffers that reflect the uncertainty, and test whether the results hold across buffer sizes. Rerun every result with report-only locations. Treat dispersed assets separately, at state or area level |
| 2 | **Access to reports and lists.** Four company sites and the NGX list refused automated access, and MTN's server was too slow | Owner downloads these by hand into `data/raw/manual/`, with each file's source and date logged. Never route around a block |
| 3 | **Uneven documents.** The corpus mixes full annual reports, integrated reports (Seplat from 2024, per the owner), financial-statement-only filings, sustainability extracts, scanned files and garbled text layers (Unilever 2025) | Record the document type for each firm-year. Normalise text (NFKC). Add a readability check alongside the character count. Run OCR on scanned or garbled files. Keep financial-statement-only firms with document type as a control, and record "no narrative disclosure" as a finding |
| 4 | **NLP validity and compute.** ClimateBERT was not trained on Nigerian reports, and this machine has about 1 GB of free memory | Validate with a stratified hand-coded sample (two coders, agreement statistics) before using model outputs. Run the full corpus in Colab |
| 5 | **Regulatory text and timing.** IFRS S2 needs a login, and timelines have been amended | Owner obtains IFRS S2 under a free account. Quote paragraphs only after checking them. Re-check the SEC and FRC pages before the final write-up |

---

## (e) Open questions for the owner

**Answered on 2026-11-07:**

- **Sample:** a census of 50–60 NGX-listed firms with physical operations in Nigeria and a full annual report for at least one year from 2023 to 2025. Unlisted firms are excluded.
- **Financial-statement-only firms:** kept, with document type as a control. Whether a full report exists elsewhere is recorded first.
- **OSM locations:** allowed, with a `location_source` column and a report-only robustness check, and ODbL attribution kept.

- **Sources of the manual files:** recorded in `docs/data_sources.md`.
- **Licence-block boundaries:** out of scope. Facilities are now classed as point sites or dispersed assets, and dispersed assets will be measured at state or area level and analysed separately. Global Energy Monitor field coordinates are optional for Phase 2, once their licence is verified.

- **Grading (rule C1):** a location given only by local government area is grade C. An estate name without a town is grade B only if it can be uniquely matched in report text or OSM, and grade C otherwise. Applied: Presco's six estates moved from B to C.
- **State or area for dispersed assets:** sources in this order: the company's own reports, then Global Energy Monitor (once its licence is verified), then public regulator records such as NUPRC and NCC. The source of each is recorded.
- **ERA5:** not needed now. NASA POWER covers heat and humidity for Phases 0–2. Whether to use ERA5 is decided in Phase 1.
- **Extra location sources:** environmental impact assessments, company websites and regulator records are in scope, under the same access rules, with `location_source` recorded.
- **IFRS S2, Seplat's 2023 Sustainability Report and Seplat's 2025 Social Performance Report:** non-blocking, marked "pending — owner to supply before Phase 6".
- **NGX list:** supplied. The census is counted under Task 2: a main census of 59 firms and a robustness stratum of 18.

- **Borderline firms:** excluded from the main census and kept as a robustness stratum (18 firms).
- **Flour Mills:** delisted, so removed from the census. Its pilot evidence stays as a methods note.
- **HBMNG:** this is Lafarge Africa Plc, renamed HBM Nigeria Plc. Sources: NGX market bulletin of 09 July 2026, and Nairametrics, 13 July 2026.
- **Board flags:** exclude a firm only if its flag means suspended or delisting. No legend was found, so the meanings are "not verified", no firm was excluded, and the flag is stored as a variable.
- **Own identifications:** marked "not verified — confirm in Phase 2 from a primary source".

**Still open:**

1. **Flag meanings.** These still need a primary NGX source, especially DWL, which is carried by MULTITREX and UNIONDICON in the main census.
2. **Phase 2 verification.** Confirm the sector and issuer identity of every main-census and robustness-stratum firm from a primary source, and resolve the 10 unresolved tickers.
3. **Loose duplicates.** Six loose files in `data/raw/manual/` are identical (same SHA-256) to files in its subfolders. They are listed in `docs/data_sources.md` for you to remove. I have deleted nothing.
