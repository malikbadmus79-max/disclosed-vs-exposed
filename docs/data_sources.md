# Data sources

Every source consulted in Phase 0. All access dates are **2026-11-07**. The request-by-request record (time, URL, HTTP status, bytes) is in `data/interim/fetch_log.csv`.

**Access rules applied.** Each automated request checked robots.txt first. Requests were spaced at least 2 seconds apart. The client used one generic user agent (`nigeria-disclosed-vs-exposed-feasibility-audit/0.1 (academic research; python-requests)`), which contains no personal details. There were no logins, and when a site refused access (HTTP 403, or robots.txt not available), no other route to the same content was tried. A licence entry of "not verified" means no licence statement was found on the pages actually read.

## Robots.txt exception (granted by the project owner, 2026-11-07)

Both `power.larc.nasa.gov` and `overpass-api.de` disallow `/api/` for all user agents in robots.txt. The project owner granted a written exception for these two services only.

- **Reason.** Both are official public APIs that are meant for programmatic use.
- **Conditions.** Each service's published usage policy had to be followed, requests had to stay small, and the user agent had to stay generic.
- **Requests made.**
  - NASA POWER: 1 request (one point).
  - Overpass: 2 queries. The first timed out on the server. The project owner then approved a second, narrower query. Neither query was retried.
- **Scope.** The exception is coded only in `src/test_api_access.py` and `src/test_overpass_narrow.py`. Every other site stayed subject to the robots.txt check in `src/polite_fetch.py`.

## 1. Regulation and standards

| Source | URL | Licence / terms | Access | Notes |
|---|---|---|---|---|
| SEC Nigeria, circular "Implementation of the IFRS Sustainability Disclosure Standards in Nigeria" (published 23 September 2026) | https://sec.gov.ng/for-investors/keep-track-of-circulars/implementation-of-the-ifrs-sustainability-disclosure-standards-in-nigeria/ | Public web page; licence not verified | Read in full | Primary source |
| FRC Nigeria, Roadmap Report for the Adoption of IFRS Sustainability Disclosure Standards in Nigeria (Amended 2026), PDF, 47 pages | https://frcnigeria.gov.ng/wp-content/uploads/2026/02/Roadmap-Report-for-the-Adoption-of-IFRS-Sustainability-Disclosure-Standards-in-Nigeria-Amended-2026-.pdf | Public document; licence not verified | Read (saved to scratch space, not to the repository) | Primary source |
| FRC Nigeria, press release on the amended roadmap and SRG 1 (26 February 2026) | https://frcnigeria.gov.ng/2026/02/26/frc-unveils-amended-roadmap-and-sustainability-reporting-guideline-to-strengthen-adoption-of-ifrs-sustainability-disclosure-standards-in-nigeria/ | Licence not verified | Read | Primary source |
| NGX, Sustainability Disclosure Guidelines, PDF, 21 pages | https://doclib.ngxgroup.com/regulation-site/IssuersRules/Sustainability%20Disclosure%20Guidelines.pdf | Marked "Authorised Use Only – PUBLIC" | Read | Primary source |
| IFRS Foundation, IFRS S2 Climate-related Disclosures (PDF) | https://www.ifrs.org/content/dam/ifrs/publications/pdf-standards-issb/english/2023/issued/part-a/issb-2023-a-ifrs-s2-climate-related-disclosures.pdf | Behind an IFRS account login | **Not accessed**: redirected to a login page | Pending — owner to supply before Phase 6 (non-blocking) |
| IFRS staff paper AP1, TIG March 2024, on paragraph 29 of IFRS S2 | https://cdn.ifrs.org/content/dam/ifrs/meetings/2024/march/tig/ap1-application-of-paragraph-29-a-c-of-ifrs-s2-using-issb-standards-and-related-materials.pdf | Not verified | **Not accessed**: host name did not resolve | |
| Nyakundi Report, article on the SEC circular | https://nyakundireport.com/a/334398/nigerias-sec-circular-on-ifrs-sustainability-standards-sparks-industry-concerns | Not verified | Redirected to the site's home page; article not read | |
| Streamline Feed, article on the SEC deadline | https://streamlinefeed.co.ke/news/nigeria-sets-october-deadline-public-companies-submit-mandatory-ifrs-sustainability-plans | Not verified | Fetched | Secondary source |
| XBRL International, "Nigeria asks companies to show their ISSB homework" | https://www.xbrl.org/news/nigeria-asks-companies-to-show-their-issb-homework/ | Not verified | Fetched | Secondary source |
| Nairametrics, "SEC issues deadline for public companies…" (24 September 2026) | https://nairametrics.com/2026/09/24/sec-issues-deadline-for-public-companies-to-submit-ifrs-sustainability-reporting-plans/ | Not verified | Fetched | Secondary source |

## 2. Company universe

| Source | URL | Licence / terms | Access | Notes |
|---|---|---|---|---|
| NGX equities price list | https://ngxgroup.com/exchange/data/equities-price-list/ | Not verified | My automated client was **blocked** (HTTP 403). **Supplied by the owner:** copied in a browser on 2026-11-07 (filters: All Market, All Sector; Show: All) and pasted into `data/raw/manual/ngx/ngx_equities_price_list_2026-11-06.csv`. That file has 146 tickers, trade date 06 Nov 2026, with provenance in `data/raw/manual/ngx/SOURCE.txt` | Tickers and prices only; no issuer names or sectors |
| NGX company profile directory | https://ngxgroup.com/exchange/data/company-profile/ | Not verified | **Blocked**: HTTP 403 | |
| NGX industry sector page | https://doclib.ngxgroup.com/issuers/listing-your-company/industry-sector | Not verified | Returned a SharePoint error page on both attempts, 2026-11-07. This is an error page, not a block | So no NGX sectors are available. In `data/interim/ngx_census_frame.csv`, sector labels and issuer identities are analyst identifications marked "not verified — confirm in Phase 2 from a primary source", and each row records the source of its assignment. Pilot issuers' classification as having physical operations comes from their own reports. HBMNG's identity comes from the NGX bulletin above |
| NGX Regulation, Market Bulletin NGXREG/IRD/MB76/26/07/09, "Lafarge Africa Plc – Change of Name to HBM Nigeria Plc" (09 July 2026), PDF, 1 page | https://doclib.ngxgroup.com/Listings-site/corporate-disclosure-site/Documents/Market%20Bulletin%20-%20Change%20of%20Name%20of%20Lafarge%20Africa%20Plc.pdf | Marked "Authorised Use Only – PUBLIC" | Read | Primary source. It confirms the change of name was "implemented by Nigerian Exchange Limited" and that the trading symbol "changed from WAPCO to HBMNG" |
| Nairametrics, "HBM Nigeria changes NGX trading symbol from WAPCO to HBMNG" (13 July 2026) | https://nairametrics.com/2026/07/13/hbm-nigeria-changes-ngx-trading-symbol-from-wapco-to-hbmng/ | Not verified | Fetched | Secondary source, cited by the owner |
| Nairametrics, "NGX delists Flour Mills of Nigeria from Daily Official List after December 16 suspension" (5 January 2025) | https://nairametrics.com/2025/01/05/ngx-delists-flour-mills-of-nigeria-from-daily-official-list-after-december-16-suspension/ | Not verified | Fetched | Secondary source, cited by the owner. According to a search summary of the article, the delisting was effective 30 December 2024 and announced in NGX's first weekly market report of 2025. That NGX weekly report itself was not read |
| NGX weekly market reports, checked for a legend to the board flags | https://mondovisione.com/_assets/files/NGX_Weekly-Report-20260522.pdf ; https://mondovisione.com/_assets/files/NGX_Weekly-Market-Report-for-the-Week-Ended-13-03-2026.pdf ; https://doclib.ngxgroup.com/market_data-site/other-market-information-site/Week%20Market%20Report/Weekly%20Market%20Report%20for%20the%20Week%20Ended%2001-03-2024.pdf | Not verified | Fetched (5, 5 and 6 pages) | **No legend found** for MRF, BMF, RST, DWL, DIP, BLS or MRS. A further targeted web search also found none. Flag meanings are recorded as "not verified" |
| Intelpoint, "About 3 out of every 10 (29.25%) listed companies in Nigeria are in the Financial Services sector" (2025) | https://intelpoint.co/insights/about-3-out-of-every-10-29-25-listed-companies-in-nigeria-are-in-the-financial-services-sector/ | Not verified | Fetched | Secondary source. Sector counts only; it cites NGX as its source |

## 3. Company reports (pilot of 15 firms)

The file-by-file inventory is `data/interim/pilot_report_inventory.csv`: URL, status, SHA-256, page count and text-layer measures. The 32 downloaded PDFs (547.3 MB) are in `data/raw/pilot_reports/`, and 6 owner-supplied PDFs are in `data/raw/manual/`. Neither folder is committed to git.

| Host | Robots / access result | Used for |
|---|---|---|
| cement.dangote.com (dangotecement.com redirects here) | Allowed | Dangote Cement annual reports and sustainability extracts |
| www.buacement.com | Allowed | BUA Cement annual reports |
| www.guinness-nigeria.com | Allowed | Guinness Nigeria annual reports |
| okomunigeria.com | Allowed; slow server | Okomu annual and sustainability reports |
| www.presco-plc.com | Allowed | Presco annual report |
| www.mtn.ng | Allowed; transfers failed twice (connection dropped, then the batch time limit was reached) | 2025 annual and sustainability reports supplied manually by the owner (see below) |
| www.betaglass.com | Allowed; no annual report link found on the pages read | — |
| greenwichregistrars.com (registrar) | Allowed | Beta Glass 2023 annual report |
| cardinalstoneregistrars.com (registrar) | Not requested | Lafarge 2022: listed, not downloaded in Phase 0 |
| doclib.ngxgroup.com/Financial_NewsDocs (NGX filings library) | Allowed | International Breweries, Lafarge, Flour Mills and Cadbury filings |
| www.nestle-cwa.com | **Blocked**: HTTP 403 | 2025 annual report supplied manually (see below) |
| www.unilevernigeria.com | **Blocked**: HTTP 403 | 2025 annual report supplied manually (see below) |
| www.nbplc.com | **Blocked**: robots.txt returned 403 | 2025 annual report supplied manually (see below) |
| www.seplatenergy.com | **Blocked**: robots.txt returned 403 | 2025 integrated annual report supplied manually (see below) |
| africanfinancials.com (third-party aggregator) | Allowed | Company listing pages only (see below) |
| www.lafarge.com.ng, lafarge.com.ng | Connection error (host did not respond) | — |
| www.intbrew.com, www.betaglassplc.com | Connection error. These were guessed domains, not known company sites | — |
| www.fmnplc.com, fmnplc.com | TLS certificate error. TLS checking was not turned off | — |
| www.cadburynigeria.com | Connection timeout | — |

### Files supplied manually by the project owner (`data/raw/manual/<firm>/`)

The owner downloaded these files by hand in a web browser on **2026-11-07**. The source pages below are as reported by the owner. The owner then placed copies in firm subfolders: `mtn/`, `nestle/`, `unilever/`, `nigerian_breweries/`, `seplat/` and `ngx/`. **The inventory now points only at the subfolder copies.** The file names in the table are the original download names; the subfolder copies are renamed but identical.

**Loose duplicates for the owner to remove.** I have deleted nothing. Each of these files in `data/raw/manual/` is identical (same SHA-256) to a subfolder copy:

| Loose file in `data/raw/manual/` | Identical subfolder copy |
|---|---|
| MTN-Nigeria-2025-Annual-Report.pdf | mtn/MTN-Nigeria-2025-Annual-Report.pdf |
| MTN-Nigeria-2025-Sustainability-Report-Final.pdf | mtn/MTN-Nigeria-2025-Sustainability-Report-Final.pdf |
| Nestle Nigeria PLC  2025 Annual Report.pdf | nestle/Nestle_Nigeria_2025_Annual_Report.pdf |
| ng-unilev-2025-ar-00.pdf | unilever/Unilever_Nigeria_2025_Annual_Report.pdf |
| NB-ANNUAL-REPORT-doc-1.pdf | nigerian_breweries/Nigerian_Breweries_2025_Annual_Report.pdf |
| seplat-2025-integrated-report-260420-compressed.pdf | seplat/Seplat_2025_Integrated_Annual_Report.pdf |

The originals in the owner's Downloads folder are untouched.

Each file's identity was checked from its own title or cover text, and each was measured with the same extractability test as the other reports. SHA-256 hashes are in `data/interim/pilot_report_inventory.csv`.

These firms' sites refused automated access: Nestlé, Nigerian Breweries and Seplat returned HTTP 403, and MTN's connection was too slow. The owner's browser downloads are a manual retrieval by the project owner. My client made no further automated attempts on those sites.

| File | Firm, year, type | Size | Pages | Text layer | Source (as reported by the owner) |
|---|---|---|---|---|---|
| MTN-Nigeria-2025-Annual-Report.pdf | MTN Nigeria, 2025, annual report | 17.7 MB | 167 | Extractable (100% of pages) | https://www.mtn.ng/wp-content/uploads/2026/05/MTN-Nigeria-2025-Annual-Report.pdf |
| MTN-Nigeria-2025-Sustainability-Report-Final.pdf | MTN Nigeria, 2025, sustainability report | 46.2 MB | 174 | Extractable (97.7%) | https://www.mtn.ng/wp-content/uploads/2026/04/MTN-Nigeria-2025-Sustainability-Report-Final.pdf |
| Nestle Nigeria PLC  2025 Annual Report.pdf | Nestlé Nigeria, 2025, annual report | 15.1 MB | 182 | Extractable (83.5%) | https://www.nestle-cwa.com/en/investors/nigeria (Full-Year Report section, "Nestle Nigeria PLC 2025 Annual Report") |
| ng-unilev-2025-ar-00.pdf | Unilever Nigeria, 2025, annual report | 9.6 MB | 176 | **Garbled.** Characters are present on 85.8% of pages, but the font encoding substitutes one glyph for each letter. Content was read from page images and from text decoded with a letter map checked against those images | https://africanfinancials.com/document/ng-unilev-2025-ar-00/ (third-party aggregator copy) |
| NB-ANNUAL-REPORT-doc-1.pdf | Nigerian Breweries, 2025, annual report | 16.9 MB | 179 | Mixed (77.1% of pages) | https://www.nbplc.com/investor-relations/financial-reports/ ("2025 Annual Report And Accounts") |
| seplat-2025-integrated-report-260420-compressed.pdf | Seplat Energy, 2025, integrated annual report | 25.5 MB | 350 | Extractable (99.7%) | https://www.seplatenergy.com/investors/results-and-presentations/ ("Annual Report and Account 2025", 20 April 2026) |
| ngx/ngx_equities_price_list_2026-11-06.csv (+ SOURCE.txt) | NGX equities price list, trade date 06 Nov 2026 | 10.8 KB | 146 tickers | CSV | https://ngxgroup.com/exchange/data/equities-price-list/ (owner browser copy, 2026-11-07) |
| Seplat 2023 Sustainability Report | — | — | — | — | Pending — owner to supply before Phase 6 (non-blocking) |
| Seplat 2025 Social Performance Report | — | — | — | — | Pending — owner to supply before Phase 6 (non-blocking) |
| IFRS S2 | — | — | — | — | Pending — owner to supply before Phase 6 (non-blocking) |

### Check for full annual reports at firms with only financial-statement filings (owner request, 2026-11-07)

Only the africanfinancials.com company pages were read. robots.txt allows them, and no documents were opened or downloaded. The result is in `data/interim/fs_firm_full_report_check.json`.

The NGX filings library (doclib.ngxgroup.com) has no browsable index, so its holdings could be checked only through filings already found in search results.

| Firm | africanfinancials.com page | "Annual report" entries for 2023–2025 |
|---|---|---|
| International Breweries | https://africanfinancials.com/company/ng-intbre/ | 2023, 2024, 2025 |
| Lafarge Africa | https://africanfinancials.com/company/ng-wapco/ (redirects to https://africanfinancials.com/company/ng-hbmng/) | 2023, 2024, 2025 |
| Flour Mills of Nigeria | https://africanfinancials.com/company/ng-flourm/ | 2023, 2024 (no 2025 entry) |
| Cadbury Nigeria | https://africanfinancials.com/company/ng-cadbur/ | 2023, 2024, 2025 |

These are listing entries only. **Whether they are full narrative annual reports or financial statements alone was not verified.** The owner will download the files by hand where needed. africanfinancials.com is a third-party aggregator, and its terms of use were not reviewed.

**OpenStreetMap attribution.** Location candidates from OSM carry the notice "© OpenStreetMap contributors", and the data are used under the Open Database License (ODbL). Facility records whose location comes from OSM are marked `location_source = osm` in `data/interim/facility_locatability.csv`.

**Copyright.** The company reports are copyright of the issuing companies. They are held only for research text extraction and are not redistributed.

**Policy for blocked firms.** For the four firms whose own sites refused access, I fetched no copies from registrars, NGX or aggregators. Their reports reached the project only as files the owner supplied. sustainabilityreports.com and marketscreener.com appeared only in search results and were never opened. africanfinancials.com company listing pages were read once, at the owner's request (see below), and no documents were downloaded from it.

## 4. Hazard and exposure data

| Dataset | URL | Licence | Resolution | Years | Size | Account |
|---|---|---|---|---|---|---|
| WRI Aqueduct 4.0 water risk (includes baseline water stress) | https://www.wri.org/data/aqueduct-global-maps-40-data ; data file https://files.wri.org/aqueduct/aqueduct-4-0-water-risk-data.zip | CC BY 4.0 (WRI FAQ and the wri/Aqueduct40 GitHub repository) | HydroBASIN level 6 sub-basins (WRI FAQ) | Baseline indicators plus projections for 2030, 2050 and 2080 (data page). The baseline period was not verified from a primary page | Not verified: robots.txt for files.wri.org disallows automated access | None for download. The FAQ asks users who adapt or share the data to register and give attribution |
| WRI Aqueduct Floods Hazard Maps v2.0 (riverine and coastal) | https://www.wri.org/data/aqueduct-floods-hazard-maps ; https://datasets.wri.org/datasets/aqueduct-floods-hazard-maps | Not verified on the pages read | Not verified | Baseline plus 2030, 2050 and 2080; temporal coverage 2010–2080; released 2020; modelled without flood protection (data page) | Not verified | Not verified. The data explorer shows a Login link |
| JRC Global river flood hazard maps v2.1.2 (GloFAS, Copernicus Emergency Management Service) | https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/ (README.txt in the same folder) | Open Data Commons Open Database License v1.0 (README) | 3 arc seconds, about 90 m (README) | Static hazard maps for return periods of 10, 20, 50, 75, 100, 200 and 500 years (folder listing) | 1-in-100-year depth tiles likely to cover Nigeria (N20_W0, N10_W0, N20_E10, N10_E10): 10 + 17 + 31 + 27 MB = 85 MB. The rule that tile names give the top-left corner is assumed, not verified | None |
| NASA POWER daily point API | https://power.larc.nasa.gov/api/temporal/daily/point ; docs at https://power.larc.nasa.gov/docs/ | No licence named on the pages read. The referencing guide asks for a citation and notification of publications | Meteorology on a 0.5° latitude grid; the longitude spacing was garbled in the extracted text, so not verified. MERRA-2 source (methodology page) | MERRA-2 from 1981. Test returned 1990-01-01 to 2025-12-31 | Test response 889,651 bytes (one point, 4 parameters, 36 years) | None. The test worked without one |
| Copernicus ERA5 hourly data on single levels (optional) | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels | CC-BY licence (dataset page) | 0.25° for the atmosphere | 1940 to present, hourly | Not checked | Free account required for download. Not needed now: NASA POWER covers Phases 0–2, and ERA5 is decided in Phase 1 (owner decision, 2026-11-07) |
| WorldPop Global2 R2025A population counts, Nigeria | https://hub.worldpop.org/project/categories?id=3 ; file https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/NGA/v1/100m/constrained/nga_pop_2025_CN_100m_R2025A_v1.tif | CC BY 4.0 (hub page footer) | 100 m (3 arc seconds) and 1 km | Annual, 2015–2030. The release statement calls R2025A an alpha version | Nigeria 2025, 100 m constrained: 157.0 MB. 1 km UN-adjusted: 4.4 MB (HTTP HEAD only; not downloaded) | None |
| OpenStreetMap via Overpass API | https://overpass-api.de/api/interpreter ; usage policy https://wiki.openstreetmap.org/wiki/Overpass_API | OpenStreetMap data: ODbL; attribution "© OpenStreetMap contributors" (licence not quoted from a page read) | Vector features | OSM snapshot 2026-11-07T08:18:50Z | Narrow query: 9,310 bytes, 41 features | None |

The WorldPop catalogue page `https://www.worldpop.org/datacatalog/` was not used, because its robots.txt returned HTTP 403.

### Optional for Phase 2 (not accessed in Phase 0)

| Dataset | Use | Status |
|---|---|---|
| Global Energy Monitor, oil and gas field data | Point coordinates for oil and gas fields, as an optional extra for dispersed assets | Not accessed. URL, licence and terms not verified. The owner describes the licence as open; to be verified before use |

Oil and gas licence-block boundaries are **out of scope** (owner decision, 2026-11-07).

**Location sources allowed from Phase 1 (owner decision, 2026-11-07).** Every source is subject to the same robots.txt and terms rules, and recorded in `location_source`:

- **Dispersed assets (state or area level), in order of preference:** the company's own reports, then Global Energy Monitor (once its licence is verified), then public regulator records such as NUPRC and NCC.
- **Point sites:** environmental impact assessments, company websites and regulator records are also in scope.

## Phase 2 sources (accessed 2026-11-07)

- **Company reports.** 14 full-year filings were downloaded from doclib.ngxgroup.com and one from sugar.dangote.com, the company's own site. Every URL and SHA-256 is in `data/interim/phase2_report_inventory.csv`. The Dangote Sugar annual-report URL found by search (`.../DANGOTE-SUGAR-REFINERY-PLC-2025-ANNUAL-REPORT.pdf`) returned HTTP 404, so the FY2025 accounts file on the same site was used instead.
- **Overpass API.** The owner authorised use "within its usage policy, in small queries" (Phase 2 brief), because robots.txt disallows `/api/`. Raw responses are in `data/raw/osm_phase2/`, under ODbL ("© OpenStreetMap contributors"). Queries made:

  | Query | Outcome |
  |---|---|
  | `places` | 88 elements |
  | `features` | 64 elements |
  | `states` | HTTP 400 (syntax error), then HTTP 502 (server at capacity); not retried |
  | `states_check` | 87 results |

- **Leaflet 1.9.4.** The review map (`data/processed/sites_map.html`) loads the library from unpkg.com and OSM tiles from tile.openstreetmap.org.
- **Web searches.** These supplied the leads in `docs/manual_download_list.md`. Third-party listing pages there were not opened.

## Owner-approved aggregator and registrar round (2026-11-07)

The owner allowed africanfinancials.com, sustainabilityreports.com and registrar sites, with automated download through Google Drive previews for africanfinancials.com, on condition that robots.txt and terms permit it. Requests were at least 5 s apart. The checks:

- **africanfinancials.com: not used.** Its terms (https://africanfinancials.com/terms/, read 2026-11-07) state: "You may not use any data mining tools, robots, or similar data gathering and extraction instruments on the Web Site or any part thereof". Its robots.txt also disallows Anthropic's agents by name. No document page and no Google Drive file was requested.
- **sustainabilityreports.com: not used.** The homepage returned HTTP 403.
- **cardinalstoneregistrars.com: used.** robots.txt allows general agents, with the same named-agent disallow list as africanfinancials.com. The terms page returned HTTP 404.
- **Airtel Africa: not fetched.** `www.airtel.africa/annual-reports` was readable, but the PDF host `cdn-webportal.airtelstream.net` returned HTTP 403 for robots.txt.

| Ticker | File | Host | Source page URL | File ID | Date | SHA-256 |
|---|---|---|---|---|---|---|
| LIVESTOCK | data/raw/manual/livestock/2025_AR.pdf (132 pages, text layer) | cardinalstoneregistrars.com (registrar) | https://cardinalstoneregistrars.com/wp-content/uploads/2026/05/LSF%20REPORT%202025.pdf | n/a (direct PDF) | 2026-11-07 | `8e6d5c1470d62250f2ce75b6bdc69018f9baa1492a8819f9fa1dafae2731e5d2` |
| THOMASWY | data/raw/manual/thomaswy/ng-thomas-2025-ar-00.pdf (57 pages, **no text layer**) | Owner-supplied (already in place; identical to the copy in the owner's Downloads folder) | Not recorded by the owner. The file name follows africanfinancials.com naming (ng-thomas-2025-ar-00), so that may be the source: not verified | n/a | file present 2026-11-07 | `c5c6205ada383e2e64173d24f7c268fbf0d3041681486fa121e7390727898a4d` |

## Owner-supplied files: africanfinancials.com document pages (browser downloads by the owner, 2026-11-07)

The owner downloaded these files in a browser from africanfinancials.com document pages. I made no automated request to that site.

| Ticker | File | Pages | Text layer | SHA-256 |
|---|---|---|---|---|
| ACADEMY | data/raw/manual/academy/ng-academ-2025-ar-00.pdf | 112 | Extractable | `d76f06a68f1f40c4a594f66610bc1b4fdd705efb397e24df2db4e502c6fd9cdc` |
| ARADEL | data/raw/manual/aradel/ng-aradel-2025-ar-00.pdf | 135 | Extractable | `5091add6c7ea67507e7e86079ae55cb2ae0c285a5378698ca7d43f73d8cce7ca` |
| BUAFOODS | data/raw/manual/buafoods/ng-buaf-2024-ar-00.pdf (FY2024) | 70 | Extractable | `4a91616f980427a32327fa63c0f0ab9ea47c78db40cdf37558f5e6ea3917a32a` |
| ELLAHLAKES | data/raw/manual/ellahlakes/ng-ellahl-2024-ar-00.pdf | 46 | **No usable text layer** (OCR pending) | `30561ce33882986c1773150cb275c7ea3ddf8a197220747831b9add17307f8d3` |
| ENAMELWA | data/raw/manual/enamelwa/ng-enamel-2025-ar-00.pdf | 47 | Extractable | `56e5ca94988791178e9dcc19b5cfff435b5ed11b25cc788b782e79beb11e7a9e` |
| FIDSON | data/raw/manual/fidson/ng-fidson-2025-ar-00.pdf | 87 | Extractable | `2ac3c80aa1b123eda12ef3ddf933f4decad68ebc6e337bfc3f06b49189ef86cf` |
| MEYER | data/raw/manual/meyer/ng-meyer-2025-ar-00.pdf | 66 | Extractable | `deb8cb66498cd44eed4b6c4c0aeabb630737b4df1cc36454f612bf6b8d00757b` |
| MULTIVERSE | data/raw/manual/multiverse/ng-multiv-2025-ar-00.pdf | 49 | **No text layer** (OCR pending) | `0c7b72d9bb3c3c15da2d958dd04947f76112675debe598eca04a284f4dab2b57` |
| NNFM | data/raw/manual/nnfm/ng-nnfm-2025-ar-00.pdf | 102 | Extractable | `4b47f569c435d6a5755a5ea9c07983c25206ced22c898186a100455faeb181ed` |

The source page for each file follows the pattern `https://africanfinancials.com/document/<file name without .pdf>/`, as stated by the owner.

**Overpass (same round).** Two small queries were made:

- `places2`: the names Lafiagi and Obanikoro; 3 elements.
- `states_check2`: the 2 points not covered earlier; 2 results.

## OCR tools (owner approval, 2026-11-07)

| Tool | Version | Status |
|---|---|---|
| Tesseract | v5.4.0.20240606 (leptonica 1.84.1), English (`eng`) data | Already installed at `C:\Program Files\Tesseract-OCR\`; not on PATH, so added to PATH for the session only |
| OCRmyPDF | 16.13.0 | Installed into the project `.venv` with pip, without admin rights |
| Ghostscript | 10.08.0 (`gswin64c`) | **Installed by the owner with admin rights before 2026-11-11** at `C:\Program Files\gs\gs10.08.0\`. Not on PATH, so added to PATH for the session only. Before that, the test run on Ellah Lakes failed with "Could not find program 'gswin64c' on the PATH" |

## Owner round 3: owner-supplied files (browser downloads by the owner, 2026-11-07; processed 2026-11-11)

The owner downloaded these files in a browser on 2026-11-07, from africanfinancials.com document pages, sustainabilityreports.com, or (Airtel Africa) the company's own site. I made no request to any of these sites. SHA-256 was computed on 2026-11-11 with `sha256sum`. "Pages" and "Text layer" come from PyMuPDF (pages with more than 50 characters of text).

| Ticker | File (in `data/raw/manual/`) | Site (owner) | Pages | Text layer | SHA-256 |
|---|---|---|---|---|---|
| AIRTELAFRI | airtelafri/Airtel-Africa-plc-Annual-Report-and-Accounts-2025.pdf (FY to 31 Mar 2025) | Company site (airtel.africa) | 268 | Extractable | `ac7b74ce7526c4e7551c3026ff410233b1e96da50498d47c7e2abbffe6b1b099` |
| ALEX | alex/ng-alex-2024-ar-00.pdf (FY2024) | africanfinancials.com | 60 | **None** (CamScanner scan); OCR copy made | `bc26717f8743660e36be5bba08a38f6bcadc8fbe1eda211c3cb46d86b95ba61a` |
| CAP | cap/ng-cap-2025-ar-00.pdf | africanfinancials.com | 87 | Extractable | `87a8eb05244671acd52c336682a2843c6f58e95bff166ae9ab8b3267375b7cf7` |
| CHAMPION | champion/Champion Breweries PLC - 2025 - Annual Report & Financial Statements (SustainabilityReports.com).pdf | sustainabilityreports.com | 105 | Extractable (88 pages) | `4637adc6fb3bf6dcd6e62080e56926d1719e5ef9e499e14ad501e79191bb17bc` |
| ETERNA | eterna/ng-eterna-2025-ar-00.pdf | africanfinancials.com | 73 | **None**; OCR copy made | `9c591056032bc89bd4ce1e05a0d0b3c3c223938cab602699a2f96a53cc31b27b` |
| EUNISELL | eunisell/ng-ensl-2025-ar-00.pdf (FY to 30 Jun 2025) | africanfinancials.com | 39 | Extractable | `88e19aa059696a5336677f1076e6326966bdb102485b6273b1dad450532a0cde` |
| GEREGU | geregu/Geregu Power PLC - 2024 - Annual Report and Financial Statements (SustainabilityReports.com).pdf (FY2024) | sustainabilityreports.com | 104 | **None** apart from the site's download watermark; OCR copy made | `a86f27a06a78456df5dc11d3d5bba74255a3265c38b5d28bf81863f1ad836588` |
| GOLDBREW | goldbrew/ng-goldbr-2024-ar-00.pdf (FY to 31 Mar 2024) | africanfinancials.com | 64 | Extractable | `721664264e588d57adc9b3ff05ee8f84c34cc88be4e374f789822437a45e5157` |
| IMG | img/ng-img-2025-ar-00.pdf | africanfinancials.com | 71 | Extractable (61 pages) | `8c658e8214bbedd7c5ac9f1e871086ea52fee64076c016873293d5d06da6fd68` |
| JAPAULGOLD | japaulgold/ng-japaul-2025-ar-00.pdf | africanfinancials.com | 84 | Extractable (78 pages) | `5bebf461d2fceb424649a1e197bd08a6e6e6cd5571c8a411bf6260c0681d2958` |
| JBERGER | jberger/Julius Berger Nigeria PLC - 2025 - Annual Reports (SustainabilityReports.com).pdf | sustainabilityreports.com | 89 | Extractable (85 pages) | `c902ecc14077fc4fdd938e7296e372db36ceb65f293b591655f92668426cb495` |
| MCNICHOLS | mcnichols/ng-mcnich-2025-ar-00.pdf | africanfinancials.com | 52 | **None**; OCR copy made | `95ba6db5edddc6a582069ea3330f54883677e8544d73f00320d23a71562d282b` |
| MECURE | mecure/ng-mecure-2025-ar-00.pdf | africanfinancials.com | 43 | Extractable | `4b57dfaaeb3b0bd1e75758cacb0cbf1070ab8a1490044e19dd85d2cdb9fbb23a` |
| MULTITREX | multitrex/ng-multix-2024-ar-00.pdf (FY to 30 Apr 2024) | africanfinancials.com | 57 | Partly: 37 pages with text, 20 image-only pages not OCR'd | `e1ed36cb80c62a6c0cb41387b98a83410b9abf5785e5be661d8640806a9b645a` |
| OANDO | oando/ng-oando-2025-ar-00.pdf | africanfinancials.com | 113 | Extractable | `c057da0d059cf1aa64de7dd0bf494679c7360b1b19b01d8b01ee34ec0584d79e` |
| TOTAL | total/ng-total-2025-ar-00.pdf | africanfinancials.com | 98 | Extractable | `f9798c6628a3ac7ae9bbff34c0b15c720b34e09e9f721734117787a4d829e251` |
| TRANSPOWER | transpower/ng-tpower-2025-ar-00.pdf | africanfinancials.com | 81 | Extractable | `2a98a0d0a61d25f18e04315a07468596d6f991a70e52ce67b1cea1709fd1d8da` |
| TRIPPLEG | trippleg/ng-trippl-2025-ar-00.pdf (FY to 31 Mar 2025) | africanfinancials.com | 57 | Extractable | `16dc14f3e4756e708384f8ead450a1bc5d3e10047485cd35a3f294b5f6ab4345` |
| UNIONDICON | uniondicon/ng-uds-2025-ar-00.pdf | africanfinancials.com | 29 | **None** (2 pages with a few words); OCR copy made | `c6c88525157ce20202344cf67afd12960f362eac226cb3764ee33c1da45fd44a` |

- **Source pages.** For the africanfinancials.com files, the source page follows the pattern `https://africanfinancials.com/document/<file name without .pdf>/` (the leads in `docs/manual_download_list.md`). For sustainabilityreports.com files, the leads are the pages listed in `docs/manual_download_list.md`; each file carries the site's watermark "Downloaded from SustainabilityReports.com" with a 2026-11-07 UTC time. The Airtel Africa lead page is https://www.airtel.africa/annual-reports.
- **PREMPAINTS:** no file was found in `data/raw/manual/` on 2026-11-11.

## OCR copies (2026-11-11)

Made with `src/phase2_ocr.py`: OCRmyPDF 16.13.0, Tesseract v5.4.0.20240606 (English, `eng`) and Ghostscript 10.08.0. Options: `--force-ocr -l eng --oversample 300 --jobs 4 --output-type pdf`. The originals are unchanged (SHA-256 checked before and after each run). Each copy sits next to its original, with `_ocr` added to the name. The full log, with both hashes, is `data/interim/phase2_ocr_log.csv`.

- **Why `--force-ocr`:** some scans carry a stray text object, such as Geregu's watermark, which would make OCRmyPDF skip the page.
- **Why `--oversample 300`:** most of these scans are stored at only 72 dpi (Union Dicon 120 dpi, Geregu 96 dpi). A first run at native resolution read badly ("quing", "efning" on Multiverse p16). A test on Multiverse pp6 and 16 at 300 dpi read the same text correctly, so all files were re-run at 300 dpi and the first-run copies were overwritten.

| Key | OCR copy | SHA-256 of the copy |
|---|---|---|
| THOMASWY | `data/raw/manual/thomaswy/ng-thomas-2025-ar-00_ocr.pdf` | `3406b01b3a96291d0c0bd5003317c571f8c038beb4bdf5b486c05748f460c7de` |
| ELLAHLAKES | `data/raw/manual/ellahlakes/ng-ellahl-2024-ar-00_ocr.pdf` | `ec025293be756c90f4260c71f51946894320a57a85e0502a13192c0108bba91c` |
| MULTIVERSE | `data/raw/manual/multiverse/ng-multiv-2025-ar-00_ocr.pdf` | `f156168fa8a62f0233b9979a47228123d30f837c0c614eab84bdcf94ffdbe711` |
| MCNICHOLS | `data/raw/manual/mcnichols/ng-mcnich-2025-ar-00_ocr.pdf` | `9b50e41bbca8019e3e7764fce8182db4030b86a41e7627a825095fff4fedc78b` |
| UNIONDICON | `data/raw/manual/uniondicon/ng-uds-2025-ar-00_ocr.pdf` | `2a015a6ffcb1fca5eeaf0b2e695a1b69d582ac0b888c837c48e40466bf144068` |
| ALEX | `data/raw/manual/alex/ng-alex-2024-ar-00_ocr.pdf` | `5eeff6dbdcdf71fd0eaa4e2084a3cd00f8110ea672d49c71e2570d0360a05e1d` |
| ETERNA | `data/raw/manual/eterna/ng-eterna-2025-ar-00_ocr.pdf` | `7889e1c666a8f710e0e2e1f9de1d4cd5c43418533d9b716af053ea6e1feb6ffe` |
| GEREGU | `data/raw/manual/geregu/Geregu Power PLC - 2024 - Annual Report and Financial Statements (SustainabilityReports.com)_ocr.pdf` | `2c28078647bf6527ca82a7a520f0cb6c99c5cdeb5aab89e3282617dcdea5fcc4` |
| OKOMUOIL_2023 | `data/raw/pilot_reports/okomu_oil/2023_AR_ocr.pdf` | `dcd7599da0024f7aa9aee44dbb3cc83d8cbdb5eeb99369be86c0f888ed9ee35e` |

## Owner decisions of 2026-11-12

- **Multi-Trex OCR.** Only the 20 image-only pages of `data/raw/manual/multitrex/ng-multix-2024-ar-00.pdf` were OCR'd, with the same tools and settings plus `--pages 8,9,10,11,12,13,14,16,20,22,48-57` (listed in full in the log). The other 37 pages keep their original text layer. The copy is `data/raw/manual/multitrex/ng-multix-2024-ar-00_ocr.pdf`, SHA-256 `2b1576cd0fa74e4848286e57dafd5fd676b3e7d2016dfb3310378adc5fe19ad8`; the original is unchanged.
- **wordfreq 3.1.1** (https://github.com/rspeer/wordfreq; installed from PyPI into `.venv` on 2026-11-12).
  - **Licence:** the code is Apache-2.0 and the data CC BY-SA 4.0, per the package metadata and README.
  - **Citation:** Robyn Speer (2022), *rspeer/wordfreq: v3.0 (v3.0.2)*, Zenodo, https://doi.org/10.5281/zenodo.7199437.
  - **Use:** `top_n_list('en', 1000)` is the word list for the readability check (amendment A1).
  - **Correction:** the 2026-11-11 summary said the code was MIT; the package states Apache-2.0.
- **Overpass `places3`** (the 18 new place names; owner-approved). Both attempts returned HTTP 502, "server at capacity", so the step was stopped as the owner instructed and the places stay pending. Both responses are kept, as `data/raw/osm_phase2/places3_attempt1_502.txt` and `places3_attempt2_502.txt`, and both are logged in `data/interim/fetch_log.csv`. No state-check query was made.

  | Attempt | Time (UTC, 2026-11-12) | Result |
  |---|---|---|
  | 1 | 05:58 | HTTP 502 |
  | 2 (retry about 2 minutes later, as the 502 response asks) | 06:02 | HTTP 502 |

## OSM place lookup and state check, second round (owner decision of 2026-11-12, option 4)

The data source stays OpenStreetMap (ODbL, "© OpenStreetMap contributors"). Only the access route changed.

1. **Alternative Overpass instance: failed.**
   - **Instance:** `overpass.private.coffee`, listed on the OSM wiki page "Overpass API" (https://wiki.openstreetmap.org/wiki/Overpass_API, read 2026-11-12) as "Previously known as overpass.kumi.systems … there is no rate limit in place. Please notify us in advance if you intend to use our service in a large scale project." `overpass.kumi.systems` itself did not respond, and private.coffee's robots.txt returned HTTP 404.
   - **Query:** one `places3` query (`https://overpass.private.coffee/api/interpreter`, 06:19 UTC, 2026-11-12) returned **HTTP 504** (gateway timeout). The response is kept as `data/raw/osm_phase2/places3_private_coffee_504.txt` and logged in `data/interim/fetch_log.csv`.
   - **No state check was sent,** because the places step had failed.
2. **Geofabrik Nigeria extract: used.**
   - **Download:** one download of `https://download.geofabrik.de/africa/nigeria-latest.osm.pbf` on 2026-11-12, with `src/phase2_osm_extract.py download`. Geofabrik's robots.txt request was redirected (HTTP 301) to a page that is not a robots file; the download page itself offers the file publicly.
   - **File:** `data/raw/osm/nigeria-latest.osm.pbf`, 714,991,104 bytes. SHA-256 `44dc394e928db6384723e6731ad193f40e744943991a691a4497ddf4e0012afa`. The MD5 `6cfd6f9cadd52a1a3e749c8440af47de` matches Geofabrik's published `.md5` file. Details are in `data/raw/osm/nigeria-latest.osm.pbf.json`.
   - **Extract date:** the download page says the file "contains all OSM data up to 2026-11-11T21:22:47Z"; HTTP Last-Modified was Thu, 12 Nov 2026 00:56:12 GMT.
   - **Tools:** pyosmium (`osmium` 4.3.2) and shapely 2.2.0, installed into `.venv`.
   - **Place lookup** (`places`): one streaming pass over **place nodes only**, matched on the exact `name` of the 18 requested names, with place=state excluded. Result: `data/raw/osm_phase2/places3.json`, 9 nodes, in the same JSON shape as the Overpass files. The earlier Overpass place queries also returned ways and relations; this lookup returns nodes only, as the owner specified.
   - **State check** (`states`): three streaming passes (relations, then ways, then nodes) read only `boundary=administrative` + `admin_level=4` relations and their outer ways. Polygons were assembled with shapely, and a point-in-polygon test was run for the 9 new points (`states_check3_index.json`). Result: `data/raw/osm_phase2/states_check3.json`. 52 admin_level-4 areas were assembled (including neighbouring countries' areas that are in the extract), and every point fell in exactly one Nigerian state.
   - **Matching rules:** the same as before (`src/phase2_coordinates.py`).
3. **Named ways and relations (owner decision of 2026-11-12, third round).** The same extract file was searched again, with no new download. `src/phase2_osm_extract.py named` read all ways and relations whose `name` exactly matches one of the 10 names still unmatched, in three streaming passes. Centroids were computed with shapely, and the OSM type and id are kept.
   - **Result:** `data/raw/osm_phase2/places4.json`, 1 element: Utako, `relation/12207339`, boundary=administrative.
   - **State check:** run locally on the same extract, giving `data/raw/osm_phase2/states_check4.json`: FCT.

## OCR copies made under the owner decisions of 2026-11-12 (Unilever; amendment A2)

All were made with the same tools and settings as before (OCRmyPDF 16.13.0, Tesseract 5.4.0, Ghostscript 10.08.0; `--force-ocr -l eng --oversample 300 --jobs 4 --output-type pdf`) using `src/phase2_ocr.py`. The originals are unchanged (checked by SHA-256). Full details are in `data/interim/phase2_ocr_log.csv`.

- **Unilever 2025:** fails the readability test (A1); OCR approved by the owner.
- **A2 copies:** the files caught by the page-level rule (`data/interim/readability_pages.csv`).
- **Academy:** OCRmyPDF could not read a DeviceN (spot-colour) image on page 17 (`PIL.UnidentifiedImageError`), so pages 1–16 and 18–112 were OCR'd and page 17 keeps its original text layer (page share 0.138).

| Key | OCR copy | SHA-256 |
|---|---|---|
| UNILEVER | `data/raw/manual/unilever/Unilever_Nigeria_2025_Annual_Report_ocr.pdf` | `be6402fe68b1a606ffaccb728aa4e746a6d56c6a4bd2d1ffd6ff0a976e7370bc` |
| A2_bua_cement_2024_AR | `data/raw/pilot_reports/bua_cement/2024_AR_ocr.pdf` | `3e94460867f86b8db6656b653bd68c0194f9d14de7de2511c3489e7750d17b36` |
| A2_guinness_nigeria_2020_AR | `data/raw/pilot_reports/guinness_nigeria/2020_AR_ocr.pdf` | `1fd5f22947f1b4c3fbb7787e9178f5eb3dc70d6eb8a3d7cd7f25159af49edef7` |
| A2_guinness_nigeria_2021_AR | `data/raw/pilot_reports/guinness_nigeria/2021_AR_ocr.pdf` | `1fef9d14ea04ab479ec4cb19cdf86e94df696a691f06dc6bced9a2febb9b26bb` |
| A2_guinness_nigeria_2022_AR | `data/raw/pilot_reports/guinness_nigeria/2022_AR_ocr.pdf` | `eb0c6ba8cc9781292b3b18820ea1fc03deabd9572530101e52af2e4d63cd9a7d` |
| A2_guinness_nigeria_2024_AR | `data/raw/pilot_reports/guinness_nigeria/2024_AR_ocr.pdf` | `1959f0452d3707e16aee06e06721b83dda94904ed9461875bd5cc7b25316057c` |
| A2_okomu_oil_2020_AR | `data/raw/pilot_reports/okomu_oil/2020_AR_ocr.pdf` | `578e233bd7b26e7354fff3d14fa803b9edc308b21bbbfa5cfdfc336fe8857a54` |
| A2_lafarge_africa_2023_FS | `data/raw/pilot_reports/lafarge_africa/2023_FS_ocr.pdf` | `d5a04983e1bdc89ac5eddf9ee2228ed2ae7917922fa07ee759efdff8e1ef9f07` |
| A2_nigerian_breweries_Nigerian_Breweries_2025_Annual_Report | `data/raw/manual/nigerian_breweries/Nigerian_Breweries_2025_Annual_Report_ocr.pdf` | `97c645075f5973f3150327481a2c9b75502ddefcb64eb0e3b81318735eef5f99` |
| A2_RTBRISCOE_2025_FS | `data/raw/phase2_reports/rtbriscoe/2025_FS_ocr.pdf` | `b0337f1e857f5cd92c35e57bd60c2573148c7ee0e13b6eb79b89480a8970c0a9` |
| A2_CHAMPION_Champion Breweries PLC - 2025 - Annual Report & Financial Statements (SustainabilityReports.com) | `data/raw/manual/champion/Champion Breweries PLC - 2025 - Annual Report & Financial Statements (SustainabilityReports.com)_ocr.pdf` | `20568bdde7a3f25d0eeb7503e97e2d4d681a93062aa2c5a52cf0c7506bd72726` |
| A2_IMG_ng-img-2025-ar-00 | `data/raw/manual/img/ng-img-2025-ar-00_ocr.pdf` | `aba9cba2a325649a3b8d3f7dfa988224bd0ed31cf2848590c401444eebf8c2b8` |
| A2_ACADEMY_ng-academ-2025-ar-00 | `data/raw/manual/academy/ng-academ-2025-ar-00_ocr.pdf` | `97d33480ac5b29810af516e22c7caa019f76e92acfc7300e8c9f498da69bd049` |

## Phase 3 hazard data (accessed 2026-11-12)

Every request used the project user agent and was spaced at least 6 s apart. Each is logged in `data/interim/fetch_log.csv`. File hashes and sizes are also in `data/interim/phase3_downloads.csv`, and the raw files are in `data/raw/hazards/` (gitignored). Downloads were by `src/phase3_download.py` and `src/phase3_heat.py fetch`.

### River flood: JRC Global river flood hazard maps v2.1.2 (used)

- **Source:** `https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/`. robots.txt returned an HTML "Page Not Found" page, so there is no robots file and no restriction.
- **README** (saved as `data/raw/hazards/jrc/README.txt`, last updated 12.01.2026): version 2.1.2; 3 arc seconds (about 90 m); WGS84; units are metres. Recommended citation: "Baugh, Calum; Colonese, Juan; D'Angelo, Claudia; Francesco, Dottori; Neal, Jeffrey; Prudhomme; Christe; Salamon, Peter (2024): Modelled flood inundation for different return period scenarios at the global scale. European Commission, Joint Research Centre (JRC)".
- **Licence (two statements that differ):** the README says "Open Data Commons Open Database License v1.0". The linked `copyright.txt` (`data/raw/hazards/jrc/copyright.txt`) says "(c) European Union, 1995-2026 ... licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence". Both require attribution. Which governs was not resolved.
- **Tiles:** four tiles intersect Nigeria, per `tile_extents.geojson` (saved): IDs 117 N20_W0, 118 N10_W0, 125 N20_E10 and 126 N10_E10. The raw-depth files (`*_depth.tif`, not `_reclass`) were downloaded for RP100 (main), RP10 and RP500 (robustness). The tiles are float32, nodata -9999, and the smallest wet depth is 0.1 m.

| File | Return period | Bytes | SHA-256 | Last-Modified |
|---|---|---|---|---|
| `ID117_N20_W0_RP100_depth.tif` | RP100 | 10,794,322 | `2c25a4c8ea792b3e1607d71e57d676d91192088e0988bf41e241b131b3d73878` | Thu, 18 Dec 2025 11:38:49 GMT |
| `ID118_N10_W0_RP100_depth.tif` | RP100 | 18,253,908 | `6ac00ff9236b5dfdd0177d5fb18fd7cbf897d0fbe314410eb742107f1f4d6529` | Thu, 18 Dec 2025 11:39:24 GMT |
| `ID125_N20_E10_RP100_depth.tif` | RP100 | 32,900,005 | `5adbd157e49b86628a23bf4704e8bb470d0ac174cc6f130fd34c4dcc288de208` | Thu, 18 Dec 2025 11:40:47 GMT |
| `ID126_N10_E10_RP100_depth.tif` | RP100 | 28,188,149 | `3b6fcc910bdc14c68824dfbbb125f9398d297d62344e2de912665b101f740535` | Thu, 18 Dec 2025 11:41:05 GMT |
| `ID117_N20_W0_RP10_depth.tif` | RP10 | 9,034,268 | `4879accab9886c33be23076781c88141fe081b79cb80b9997388920bc3d52bcd` | Thu, 18 Dec 2025 11:34:51 GMT |
| `ID118_N10_W0_RP10_depth.tif` | RP10 | 14,740,582 | `8e250e6cac53166582d8a6d64b98c80a82b8856b67fd0fd0d68d1f7c63f08006` | Thu, 18 Dec 2025 11:35:08 GMT |
| `ID125_N20_E10_RP10_depth.tif` | RP10 | 24,338,155 | `820ea70cfbf8f52045f272a6d62df369fa962250e1134283cd5b17e978cc6601` | Thu, 18 Dec 2025 11:36:29 GMT |
| `ID126_N10_E10_RP10_depth.tif` | RP10 | 21,362,384 | `36f86977e6c8c4715de3f8fbd482372a127c12029c942214794b5e4155a19b7a` | Thu, 18 Dec 2025 11:36:47 GMT |
| `ID117_N20_W0_RP500_depth.tif` | RP500 | 11,662,203 | `53fde71b39b689b35216b85c66ccf1eee08a4c0b098b3e1f13f4b4951fbb9e3e` | Wed, 17 Dec 2025 14:42:24 GMT |
| `ID118_N10_W0_RP500_depth.tif` | RP500 | 19,436,925 | `92c2930595a4f1ecb160d3685f8f12799c8089e279dcb779cb7418a6924c9177` | Wed, 17 Dec 2025 14:43:02 GMT |
| `ID125_N20_E10_RP500_depth.tif` | RP500 | 37,299,165 | `5152ab2629c44a6d1371fcf8165a8b569cfb29eb6c72b16f22303970a215c022` | Wed, 17 Dec 2025 14:46:03 GMT |
| `ID126_N10_E10_RP500_depth.tif` | RP500 | 31,986,852 | `f60195a7f76dbb17b463c8ed1721d69a67593bf84bcd1d1159b0a68138395417` | Wed, 17 Dec 2025 14:46:38 GMT |

- **Permanent-water mask (A8, robustness only):** downloaded on 2026-11-12 from `.../flood_hazard/Permanent_WaterBodies/`, the same source and rules. uint8; 1 = permanent water, 255 = nodata; the same grid as the depth tiles.

  | File | Bytes | SHA-256 |
  |---|---|---|
  | `ID117_N20_W0_permanent_water.tif` | 819,672 | `fb578a0017a965126b19ece1f785f3e484a0f37b4b5383c072914d516181fc84` |
  | `ID118_N10_W0_permanent_water.tif` | 997,240 | `a5c22cabdea62409a6bb253bf2295d19c1ce72a7b8dc7acbd54ffa9d0734bf9b` |
  | `ID125_N20_E10_permanent_water.tif` | 927,352 | `9994826016163ab0436f1d6892545e1a3ea350250522c814979f52b21c0f80b2` |
  | `ID126_N10_E10_permanent_water.tif` | 1,218,999 | `50c9cff2df8d27be9cd50bcfee396756ef1ea32855b32963d367dbc00454ec1d` |

- **Not used:** the `Spurious_Depths/` tiles. The design (e1) does not mention them, so depths are used as published. See the limitations in `docs/phase3_hazards.md`.

### Heat: ERA5 hourly time series on single levels, one point per 0.25° cell (amendment A11; used, main)

- **Dataset:** Copernicus Climate Data Store, "ERA5 hourly time-series data on single levels from 1940 to present" (`reanalysis-era5-single-levels-timeseries`), https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-timeseries. Licence CC-BY-4.0. Replaces the daily-statistics route of A10 for speed (A11); the heat method is unchanged.
- **Access:** `cdsapi` 0.7.7 (with `ecmwf-datastores-client` 0.6.0) on the owner's CDS account, key read by `cdsapi` from `~/.cdsapirc` (never opened or printed). Script: `src/phase3_era5_ts.py`. Requests were sent one at a time, never in parallel, on 2026-11-17 between 09:00 and 09:38 UTC. All 43 are logged in `data/interim/fetch_log.csv` with HTTP 200 and no errors. One transient DNS failure before the first request was retried automatically by `cdsapi`.
- **Request (each point):** variable `2m_temperature`; date `1991-01-01/2025-12-31` (UTC); location = the exact ERA5 0.25° grid point; `data_format` `csv`. Every file's `latitude`/`longitude` columns equal the requested point.
- **Points:** the 43 unique 0.25° grid points (A10 cell rule: nearest point, exact edges north/east) of the 125 point sites in `data/processed/site_hazards.csv` (71 main, 51 office, 3 R2). The busiest cell is 6.50 N, 3.25 E (Lagos: 38 sites).
- **Contents:** columns `valid_time,t2m,latitude,longitude`; `t2m` in K. Each file has 306,816 hourly values (12,784 days × 24), no missing values; checked for all 43 files.
- **Daily maximum:** shifted from UTC to fixed UTC+01:00 (West Africa Time), then the maximum per local calendar day, 1991-01-01 to 2025-12-31 (12,784 days). Local 1991-01-01 has 23 hours (the request starts at 00:00 UTC); the 1-hour local day 2026-01-01 is dropped.
- **Test point and validation gate (A11):** point 6.50 N, 3.25 E was downloaded first: 11,861,684 bytes in 56 s for the CDS request (3 min wall time including a 2-minute DNS retry). Its daily maxima were compared with the same cell of the two A10 daily-statistics files: 1991 (365 days) and 2025 (365 days) both gave a maximum absolute difference of 0.0003 °C and a mean absolute difference of 0.0001 °C. That is under the 0.5 °C gate, so the remaining 42 points were downloaded. A typical request took 30–125 s.
- **A10 daily-statistics files (kept; used only for the A11 cross-check):** `data/raw/hazards/era5/era5_t2m_dailymax_utc+01_1991.nc` (1,394,583 bytes, SHA-256 `5c09b435bba4d7765584ec3c1191cff66c63b7dd3829ab0e62244fc074ec9941`) and `..._2025.nc` (1,392,399 bytes, SHA-256 `d04a2c5e92f337e27e1c2414baf3b24b3a748400f264f4f71e2cf8db1b29af38`). They come from CDS `derived-era5-single-levels-daily-statistics` (DOI 10.24381/cds.4991cf48), downloaded on 2026-11-12. The other 33 years were never obtained (queue limit; see A11).
- **Files:** `data/raw/hazards/era5_timeseries/point_<lat>_<lon>.csv`. That is 43 files, 507,903,706 bytes in total, gitignored with the other raw hazard data. Hashes are also in `data/interim/phase3_downloads.csv`. SHA-256 computed on 2026-11-17 with Python `hashlib`:

  | File | Lat | Lon | Bytes | SHA-256 |
  |---|---|---|---|---|
  | `point_4.50_8.00.csv` | 4.50 | 8.00 | 11,554,600 | `729a64327c7b84fa808191e163b4145251949e13b0d903567dfe6dfa6ec621ac` |
  | `point_4.75_7.00.csv` | 4.75 | 7.00 | 11,861,385 | `15ed5c61870c5ad0ccce0ba8e1bb18affc9d67ba74b02b60b482a863978bb382` |
  | `point_4.75_7.25.csv` | 4.75 | 7.25 | 12,168,716 | `6ee68e0298c3c58517d51c2ab1624e4992dad6f69bf08bf7cddb2e3133796710` |
  | `point_5.00_7.25.csv` | 5.00 | 7.25 | 11,861,174 | `d49ec6874ff42714a474be7be3a99f01904e504343d97d660a307bee7d1d5dce` |
  | `point_5.00_8.00.csv` | 5.00 | 8.00 | 11,554,800 | `dd6b55a391a5115372e3c1fdf8cc3eed4e99e68a41cb3bb5d0fd242dbb6fb9dc` |
  | `point_5.00_8.50.csv` | 5.00 | 8.50 | 11,554,794 | `6d6c32ace56cce98d45e3c6ebd21779fc475c044bbaef78c5e878b7a73bd6db4` |
  | `point_5.50_6.00.csv` | 5.50 | 6.00 | 11,554,916 | `9ee1b75b5e24bb9aebd37331fe888aff2691f1bbc404b9dac0838c8c826371db` |
  | `point_5.50_7.00.csv` | 5.50 | 7.00 | 11,554,799 | `b0b1aad889d50256ff31a64c65cb4378002055ceede363ddda312a5f203e413d` |
  | `point_5.50_7.50.csv` | 5.50 | 7.50 | 11,554,489 | `44ea9d5f2df470d28a150c9e7cfb523ae87afb2b3191cff3dba7df4536624b68` |
  | `point_5.75_5.75.csv` | 5.75 | 5.75 | 12,168,122 | `beb0e7aed85ad6fb2bf99616bfeaf0a3242b30dbac86daf2cb055bc571c78b10` |
  | `point_6.00_5.75.csv` | 6.00 | 5.75 | 11,861,399 | `de95fce0b96f92a60e49966fe8da46ef8c9e9490a42f9bf5ece100970fea7208` |
  | `point_6.00_7.00.csv` | 6.00 | 7.00 | 11,555,078 | `224feaf112dfea705661e57e4e4f9da5b91dade40fa7fdfb16ee77e583708c16` |
  | `point_6.25_5.25.csv` | 6.25 | 5.25 | 12,168,492 | `4a46cb2331a48fc4b7b8c0ac2e5793dd9c889ea136c74c1530ad1854decd51e4` |
  | `point_6.25_5.50.csv` | 6.25 | 5.50 | 11,861,862 | `8c190b5e5539013722b97c17252dde24e76be8de27359e3bb98d7f1432d4f428` |
  | `point_6.25_6.75.csv` | 6.25 | 6.75 | 12,168,418 | `090035222a1a7290fcdedc2ee4bfe1a2066b5c701d87fe620dc334cf9b12251d` |
  | `point_6.50_3.00.csv` | 6.50 | 3.00 | 11,554,829 | `97ece469de98f45ca362dbaf45d55d75284574d883fc30b5bed4e974cefa6d59` |
  | `point_6.50_3.25.csv` | 6.50 | 3.25 | 11,861,684 | `583ceff1eb11692b1abcf986a83a00cac2ff62268d9a2c2705c0ec1c6f7b3a8b` |
  | `point_6.50_3.50.csv` | 6.50 | 3.50 | 11,554,516 | `0fd2aa14194e2ba3178af517f47d9508648c13195d9e2e2ffd828ba822ad1abd` |
  | `point_6.50_5.25.csv` | 6.50 | 5.25 | 11,861,769 | `584ce6cd4cd53dbd14cabae0da1147e25760abc9bfd0624e961c39f2003fc7ec` |
  | `point_6.50_7.50.csv` | 6.50 | 7.50 | 11,554,623 | `a973f07408fdc0be00ca82eb70699cc3d5061717df59ac2700a196c2851b430e` |
  | `point_6.75_3.25.csv` | 6.75 | 3.25 | 12,168,572 | `1d2c9bc69ac84280eb9dbd1258a55d7e0c11ff522194cbc873ceb5825dded554` |
  | `point_6.75_3.75.csv` | 6.75 | 3.75 | 12,168,770 | `e05b185e1bd9e0fd8d35bf741dd25265b1c385e7401a7a3c855d747cb6fe68ba` |
  | `point_6.75_4.00.csv` | 6.75 | 4.00 | 11,861,432 | `16f6c28b4378426db84f3e42c6fa890fc643a5e65ac06a7ab0f5eb37862159e1` |
  | `point_6.75_7.00.csv` | 6.75 | 7.00 | 11,861,383 | `98590ad7ff7c14a6a32ae29534eb52732f0d267174c7ab5b73d6041f9bba4203` |
  | `point_7.00_3.00.csv` | 7.00 | 3.00 | 11,555,458 | `f0888be4e7979f9ea050b78cca5ced0de162f4498922eec322abbba685b1f509` |
  | `point_7.00_3.25.csv` | 7.00 | 3.25 | 11,862,100 | `740450320a773ad8f49bf4d99c02e8afa70b8ddd293702c9bb52e03780f4948e` |
  | `point_7.25_6.50.csv` | 7.25 | 6.50 | 11,861,927 | `ff2f98328aa56e6f530dd145659ad18d34526703eba01fd61c9960996f13fa56` |
  | `point_7.50_4.00.csv` | 7.50 | 4.00 | 11,555,083 | `43e0ca6098771f60b945fbce80fda6b7b91c6d0203504975ba44b177d4601455` |
  | `point_7.50_6.25.csv` | 7.50 | 6.25 | 11,861,458 | `5c51997fe06d66db10260371cf97bb63d422b4e193aa0f584856aad82aaf29a8` |
  | `point_7.50_6.75.csv` | 7.50 | 6.75 | 11,861,346 | `67889ca4367699869e13ad21cb169b5c9b0e60d44661aaf221ba8bbc242cf4ec` |
  | `point_7.50_9.00.csv` | 7.50 | 9.00 | 11,555,379 | `c1d12fdc083393903bb2e9738a85583c5cf24216a8aeb6ac45ae84a3af702ef8` |
  | `point_7.75_4.75.csv` | 7.75 | 4.75 | 12,168,241 | `72e37c1d8b0df0ddc77beab8d1d2f5e44bf5bde3a5d26f512c68bd0747436209` |
  | `point_7.75_8.50.csv` | 7.75 | 8.50 | 11,861,700 | `7ff3db2e06eb36fac3268a70bd13d13f5cc0cc2db38445d82ac2101d06117b5b` |
  | `point_8.00_6.50.csv` | 8.00 | 6.50 | 11,554,988 | `81ae87bed05475448249717e937f5bab3d1e869f13d4180522a9430e158b92e7` |
  | `point_8.50_7.00.csv` | 8.50 | 7.00 | 11,554,692 | `21309725abd1ebfdf31844034fa955610bfc245c8f2fc6ff979a01aa8b22a578` |
  | `point_8.75_5.50.csv` | 8.75 | 5.50 | 11,861,498 | `7e14ab12d266710e444594677ff1b983eada39a43afd95f0ec4b87dd1234e2a4` |
  | `point_9.00_7.50.csv` | 9.00 | 7.50 | 11,554,858 | `7cff2aa1b0bdb3aaac1a2bfd66797587d6d534fdfa8b6588f29cbd3d1abff879` |
  | `point_9.25_7.25.csv` | 9.25 | 7.25 | 12,168,357 | `61504d1e314f0f2b4eb55de29c3718856bd505ba95dccae45cc8be5bdeecd65f` |
  | `point_9.50_12.00.csv` | 9.50 | 12.00 | 11,861,873 | `93c0578c1294a8f9c375805b989e53f1a636f137ac76f9275f3ca9b6159a1105` |
  | `point_10.00_9.00.csv` | 10.00 | 9.00 | 11,861,712 | `43441ba1b9dedc21c08fd4a347aed8fa0b837d37d7699a36788dc1a82761ebc6` |
  | `point_10.50_5.00.csv` | 10.50 | 5.00 | 11,861,719 | `ebbb241aacbebac5b73f469016282113abbbc5938a3ea1cc78060b9ba84e55cf` |
  | `point_12.00_8.50.csv` | 12.00 | 8.50 | 11,861,640 | `6c92589e8e7485394ac3fd39d4dfece2e19a8522c5a6949649a276499166a2fc` |
  | `point_13.00_5.25.csv` | 13.00 | 5.25 | 12,169,055 | `779418797748613ae7da18a02f8b1512d0cc130fd642f54ab4196b2862c668c3` |

### Heat: NASA POWER, owner manual download from the POWER Data Access Viewer (used)

- **Download:** by the owner in a browser on 2026-11-12 from the POWER Data Access Viewer (https://power.larc.nasa.gov/data-access-viewer/): Single Point, community Agroclimatology, temporal average Daily, 1991-01-01 to 2025-12-31, parameter T2M_MAX, format CSV. One file per cell in `docs/nasa_manual_download.md`.
- **Files:** saved by the owner in the owner's Downloads folder as `POWER_Point_Daily_19910101_20251231_<lat>N_<lon>E_LST.csv` (left in place) and copied to `data/raw/hazards/nasa_power_manual/bin_<i>_<j>.csv`. The copies are byte-identical to the originals.
- **Header (every file):** "NASA/POWER Source Native Resolution Daily Data"; dates 01/01/1991 through 12/31/2025 in LST; the requested latitude and longitude (checked against the bin centre for every file: all match); "elevation from MERRA-2: Average for **0.5 x 0.625 degree** lat/lon region"; fill value -999; parameter "T2M_MAX MERRA-2 Temperature at 2 Meters Maximum (C)". Columns `YEAR,DOY,T2M_MAX`; 12,784 days; no fill values.
- **Check against the API files:** `src/phase3_heat.py compare` found all 29 files identical to the API files, day by day: 12,784 common days in each and a maximum absolute difference of 0.0 °C in every bin.
- **Cells not downloaded:** the 4 cells with no main-analysis site (bins `10_15`, `11_14`, `12_15`, `15_9`: 5.25/7.75, 5.75/7.25, 6.25/7.75, 7.75/4.75). Owner decision: their sites are not scored for heat, and the API files for them are not used. Three of the four sites are offices (Champion, Golden Guinea and NB's Enugu sales office). The fourth, in bin `15_9`, is International Breweries' brewery at Ilesa, an OSM-sourced R2 site rather than an office; it is labelled accordingly.
- **Files ignored:** `..._006d75N_007d00E_LST.csv` (6.75 N, 7.00 E: a typo in the owner's longitude, not a bin centre) and `..._005d25N_008d75E_LST (1).csv` (a duplicate of the 5.25 N, 8.75 E file, with the same SHA-256 `61d9a6cd…`).
- **SHA-256 of the 29 files used:**

  | File | Lat | Lon | Original file name | Bytes | SHA-256 |
  |---|---|---|---|---|---|
  | `bin_9_14.csv` | 4.75 | 7.25 | `POWER_Point_Daily_19910101_20251231_004d75N_007d25E_LST.csv` | 199,967 | `5af9a4cdbc7d44105d123ba3493d39ee0da05fa2c951d1ce36e3f11cbd769e39` |
  | `bin_9_16.csv` | 4.75 | 8.25 | `POWER_Point_Daily_19910101_20251231_004d75N_008d25E_LST.csv` | 199,940 | `0e68408d01b94cdcf4a33c136b06f1dd7f66f70bb7dae158951e9d3dc7e11d1d` |
  | `bin_10_11.csv` | 5.25 | 5.75 | `POWER_Point_Daily_19910101_20251231_005d25N_005d75E_LST.csv` | 199,953 | `bcbb9060c54f93550bf91371375cac480005127c793fafff94dc298fe88f6f8b` |
  | `bin_10_14.csv` | 5.25 | 7.25 | `POWER_Point_Daily_19910101_20251231_005d25N_007d25E_LST.csv` | 199,992 | `becb86db31d6eafdcdaa7851cb3bc2f754c81c249b05b538a6e35e174f4973ca` |
  | `bin_10_17.csv` | 5.25 | 8.75 | `POWER_Point_Daily_19910101_20251231_005d25N_008d75E_LST.csv` | 200,045 | `61d9a6cd49bd9478bf97b0210163946948fa9e94b96188eb6ebb529356be7ec9` |
  | `bin_11_11.csv` | 5.75 | 5.75 | `POWER_Point_Daily_19910101_20251231_005d75N_005d75E_LST.csv` | 199,944 | `619ca4873621bdf75dcfa01d44dbd255314c0e20e8d9740ec4c50d1544f79e39` |
  | `bin_12_6.csv` | 6.25 | 3.25 | `POWER_Point_Daily_19910101_20251231_006d25N_003d25E_LST.csv` | 199,997 | `0a00ef57d540e3b50b5526c77dd157f15e1adb3c0cf8aa522e6b2b3333bdf5cf` |
  | `bin_12_10.csv` | 6.25 | 5.25 | `POWER_Point_Daily_19910101_20251231_006d25N_005d25E_LST.csv` | 199,988 | `d4eca12719f24463c1cf86921c82210bc00765a3eaf0860aeffc7ded130f21f2` |
  | `bin_12_11.csv` | 6.25 | 5.75 | `POWER_Point_Daily_19910101_20251231_006d25N_005d75E_LST.csv` | 199,997 | `d751bc8c0487861cdf5a05b707c7d3d501011349da601e00bfb30680527f5b75` |
  | `bin_12_13.csv` | 6.25 | 6.75 | `POWER_Point_Daily_19910101_20251231_006d25N_006d75E_LST.csv` | 199,927 | `e62fb8178c1e6360e92d4c6fdcfafb116ef49071e6fc69b9aa7ad5ffb5862ab2` |
  | `bin_12_14.csv` | 6.25 | 7.25 | `POWER_Point_Daily_19910101_20251231_006d25N_007d25E_LST.csv` | 199,912 | `c09a721ce9f0c6ef8ce3c8224dc7be4042280a477db75bb2be403abc38cae432` |
  | `bin_13_6.csv` | 6.75 | 3.25 | `POWER_Point_Daily_19910101_20251231_006d75N_003d25E_LST.csv` | 199,988 | `e1d5af8b57ce8efd6611735ca482cb44c334fbacf853a623c85a90b0adbfec21` |
  | `bin_13_7.csv` | 6.75 | 3.75 | `POWER_Point_Daily_19910101_20251231_006d75N_003d75E_LST.csv` | 199,965 | `f13965f728f838f26a0c639f7a26a78960b0fd9c43f6f3089e131c1fe29c1311` |
  | `bin_13_14.csv` | 6.75 | 7.25 | `POWER_Point_Daily_19910101_20251231_006d75N_007d25E_LST.csv` | 199,972 | `6aab4bf240f91d079d8b5207368c5307ffd67ccce60b841a64d857b151094110` |
  | `bin_14_6.csv` | 7.25 | 3.25 | `POWER_Point_Daily_19910101_20251231_007d25N_003d25E_LST.csv` | 199,963 | `58854eb8c023d6339c75bb4eae94c28e4de63817631cc25de2aa057ffd094f76` |
  | `bin_14_7.csv` | 7.25 | 3.75 | `POWER_Point_Daily_19910101_20251231_007d25N_003d75E_LST.csv` | 199,931 | `89e309cb149dc9800965c05436d7f0536109c64b44dee294d3bbc64dcae6c8c6` |
  | `bin_14_12.csv` | 7.25 | 6.25 | `POWER_Point_Daily_19910101_20251231_007d25N_006d25E_LST.csv` | 199,912 | `daaf4cf2b8340a9b1e03f23c8b771725cbdba86e0f1b348e0568b66185e9eb0f` |
  | `bin_14_17.csv` | 7.25 | 8.75 | `POWER_Point_Daily_19910101_20251231_007d25N_008d75E_LST.csv` | 199,943 | `7f80eb3f44a31bbab7d51f634602946a8a9a43339492b605e2fd4cc23f46eebc` |
  | `bin_15_12.csv` | 7.75 | 6.25 | `POWER_Point_Daily_19910101_20251231_007d75N_006d25E_LST.csv` | 200,029 | `496ca00f0a69530df0c6a1a7232cb141f4cfb390f61f77b120bde1d87290d666` |
  | `bin_15_13.csv` | 7.75 | 6.75 | `POWER_Point_Daily_19910101_20251231_007d75N_006d75E_LST.csv` | 199,939 | `86d02bb0ab7b65c9ad2a21fa99c23bff74357aaf33a1317d6fa18d700f06df3c` |
  | `bin_15_17.csv` | 7.75 | 8.75 | `POWER_Point_Daily_19910101_20251231_007d75N_008d75E_LST.csv` | 199,877 | `13638c3aa03bce62b1a56ea0783176c45969d8b2352e51c4f1316f7f5e65a520` |
  | `bin_16_13.csv` | 8.25 | 6.75 | `POWER_Point_Daily_19910101_20251231_008d25N_006d75E_LST.csv` | 199,987 | `d17e1fab996938f0ff8bd0b0064a1e14cd5bf27f808819b6754f5209511fa5c4` |
  | `bin_17_10.csv` | 8.75 | 5.25 | `POWER_Point_Daily_19910101_20251231_008d75N_005d25E_LST.csv` | 199,939 | `094db20f1beb99e5882fb34bf3c12481da8a1b90ec23372f959b8b4b87314b85` |
  | `bin_18_14.csv` | 9.25 | 7.25 | `POWER_Point_Daily_19910101_20251231_009d25N_007d25E_LST.csv` | 199,919 | `d36194aa76f41092ec7969369a9def3c2a7aeba6a60ac491888fbe7e5fdbd7ac` |
  | `bin_18_24.csv` | 9.25 | 12.25 | `POWER_Point_Daily_19910101_20251231_009d25N_012d25E_LST.csv` | 199,950 | `f8dd98f4719eb3573acd0e395b495bbba85ade3246afc6c0b0d9db2e90a950d9` |
  | `bin_19_17.csv` | 9.75 | 8.75 | `POWER_Point_Daily_19910101_20251231_009d75N_008d75E_LST.csv` | 199,975 | `00b2b644669a89fafb717a278c16e35c52f07317db1c054086c15a1133332f6d` |
  | `bin_21_9.csv` | 10.75 | 4.75 | `POWER_Point_Daily_19910101_20251231_010d75N_004d75E_LST.csv` | 199,977 | `2e5e29ff40c357d1445ffb3aff71f4ae00a79c65432d22a4be1fbcf39c14bb02` |
  | `bin_23_17.csv` | 11.75 | 8.75 | `POWER_Point_Daily_19910101_20251231_011d75N_008d75E_LST.csv` | 200,001 | `903c650e3e142965f99ac6bef77684e0777a3022df258ad3dc3ad60d95a2f4aa` |
  | `bin_26_10.csv` | 13.25 | 5.25 | `POWER_Point_Daily_19910101_20251231_013d25N_005d25E_LST.csv` | 199,886 | `aaf31f752c77c2c540954204c081200add802175f4c12d0afdeb1f950cc9e36f` |

### Heat: NASA POWER daily point API (superseded by the owner's manual download; not used)

**Status, 2026-11-12:** superseded. Heat is now scored from the owner's manual downloads above, which match these files exactly for the 29 cells with a main-analysis site. These files are kept as a record and are not used, including for the 4 cells the owner did not download.


**Owner decision, 2026-11-12:** "My earlier exception does NOT cover this. Make no further NASA POWER requests." `src/phase3_heat.py fetch` is disabled.


- **Access:** `https://power.larc.nasa.gov/api/temporal/daily/point`, under the owner's written robots.txt exception for this service (see the top of this file).
  - robots.txt (read 2026-11-12) disallows `/api/` for all agents. It also disallows the whole site, as "AI crawlers — block training data scraping", for named agents including "anthropic-ai" and "Claude-Web". The project user agent is generic and is not one of those names.
  - The requests serve this research, not model training. This is flagged for the owner in `docs/phase3_hazards.md`.
- **Usage policy:** the POWER daily-API documentation (read 2026-11-12) says: "with the 0.5° x 0.5° global grid you only need to submit one request per cell. If your application persists in requesting the same relative location, it will potentially be blocked."
  - **Requests:** one request per 0.5° bin, at the bin centre, for the 125 point sites with coordinates. That made 33 requests, each 6 s or more apart, all HTTP 200.
  - **Bin edges:** cell edges at multiples of 0.5° were assumed, not verified. The file headers later showed the native grid is MERRA-2 at 0.5° × 0.625°, so this assumption does not hold (see `docs/phase3_hazards.md`, section 1.4).
- **Request contents:** parameters T2M_MAX, T2M_MIN and RH2M; community AG; 1991-01-01 to 2025-12-31; JSON.
- **Response header:** "NASA/POWER Source Native Resolution Daily Data", API v2.10.3, sources MERRA2 and POWER, fill value -999, time standard LST.
- **Files:** `data/raw/hazards/nasa_power/bin_<i>_<j>.json` (33 files, about 21 MB). Per-file SHA-256 values are in `data/interim/phase3_nasa_power_files.csv`.
- **Licence:** none named on the pages read (as in Phase 0). The referencing guide asks for a citation and notification of publications.

### Population: WorldPop Global2 R2025A, Nigeria 2025, 100 m, constrained (used)

- **URL:** `https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/NGA/v1/100m/constrained/nga_pop_2025_CN_100m_R2025A_v1.tif`. robots.txt returned HTTP 404 (no robots file).
- **Licence:** CC BY 4.0 (hub page footer, Phase 0). The release statement calls R2025A an alpha version.
- **File:** `data/raw/hazards/worldpop/nga_pop_2025_CN_100m_R2025A_v1.tif`, 157,014,323 bytes (matches the Phase 0 size check), SHA-256 `abc7e897aff7de024d851a24613eebf28e710dbfe4dea9c3e02ee285d75d4f8b`, Last-Modified Fri, 08 Aug 2025 02:23:29 GMT, download completed 2026-11-12 12:22 UTC. float32, nodata -99999, 3 arc seconds.

### Coastal flood: WRI Aqueduct Floods Hazard Maps v2.0 (owner manual download; used)

- **Dataset page:** `https://datasets.wri.org/datasets/aqueduct-floods-hazard-maps` (read 2026-11-12).
  - **Licence:** `license_id` "cc-by", "Creative Commons Attribution". This is now verified.
  - **Page statements:** "This data was released in 2020"; the "hazard layers have been simulated without considering the presence of flood protection"; the future scenarios are "RCP 4.5" and "RCP 8.5".
- **Why the owner downloaded it:** the download link on that page (`https://aqueduct.wridata.org/AqueductFloods20/index.html`) is on a host whose robots.txt returned HTTP 403, so no automated request was made. The old Phase 0 S3 location returns HTTP 404.
- **File:** downloaded by the owner in a browser from WRI on 2026-11-12. `data/raw/hazards/aqueduct_floods/inuncoast_historical_nosub_hist_rp0100_0.tif`, 46,382,660 bytes, SHA-256 `03886accac54b4a6f7ebaff05e657aea115f05714d2376029edc3629ac871cb1`.
- **Read from the file:**
  - global; EPSG:4326; float32; nodata -9999; LZW, stripped (not tiled)
  - **30 arc seconds (0.008333°), about 922 m at 6°N.** This is the first time the resolution is verified. It is not coarser than about 1 km, so under e2 coastal flood is scored in the main analysis.
  - The file name gives historical (baseline), no subsidence ("nosub"), RP100.

### Water stress: WRI Aqueduct 4.0 (owner manual download; used)

- **Why the owner downloaded it:** `https://files.wri.org/robots.txt` (read 2026-11-12) disallows all agents except Twitterbot, so no automated request was made.
- **File:** downloaded by the owner in a browser from WRI on 2026-11-12, and copied from the owner's Downloads folder, which was left in place.
  - Copy: `data/raw/hazards/aqueduct40/aqueduct-4-0-water-risk-data.zip`, 261,527,511 bytes.
  - SHA-256 `bd3ed2bce88d6ff1b89191632ad134a2436e1e1d49599382f23a04d513624fc3`, identical for the original and the copy.
- **Contents:** folder `Aqueduct40_waterrisk_download_Y2023M07D05`, with a README (xlsx), CSV files (in a folder named `CVS`) and a File Geodatabase `GDB/Aq40_Y2023D07M05.gdb`. The GDB and README were extracted to `data/raw/hazards/aqueduct40/unzipped/`.
- **Layer used:** `baseline_annual`, 68,506 MultiPolygons, EPSG:4326. Fields include `string_id`, `aq30_id`, `pfaf_id`, `gid_0`, `name_0`, `bws_raw`, `bws_score`, `bws_cat` and `bws_label`. It was read with `pyogrio` 0.13.0 (installed into `.venv`).
- **Licence:** CC BY 4.0 (Phase 0: WRI FAQ and the wri/Aqueduct40 repository). Kuzma et al. (2023), DOI 10.46830/writn.23.00061.
- **Categories, read from the data (now verified):**

  | `bws_cat` | `bws_label` | `bws_raw` range |
  |---|---|---|
  | -9999 | No Data | |
  | -1 | Arid and Low Water Use | |
  | 0 | Low (<10%) | 0.0–0.0999 |
  | 1 | Low - Medium (10-20%) | 0.1–0.2 |
  | 2 | Medium - High (20-40%) | 0.2–0.3996 |
  | 3 | High (40-80%) | 0.4003–0.7992 |
  | 4 | Extremely High (>80%) | from 0.8035 |

### OSM geometries for Phase 3

From the Geofabrik extract already on disk (see above), with no new download. `src/phase2_osm_extract.py geoms` wrote two files, both © OpenStreetMap contributors, ODbL:

- `data/interim/osm_feature_polygons.geojson`: the 9 way and relation polygons used for "OSM polygon + 250 m" buffers.
- `data/interim/osm_states.geojson`: the 37 Nigerian admin_level=4 boundaries. Taraba's ring could not be assembled, so its geometry is empty.

### Software added in Phase 3

`rasterio` 1.5.2 (GDAL 3.12.2 bundled) and `pyogrio` 0.13.0, installed into `.venv`.

## Phase 4 report files

### OCR copy under amendment A12 (2026-11-17)

| Original | OCR copy | SHA-256 of the original (unchanged) | SHA-256 of the copy |
|---|---|---|---|
| `data/raw/manual/livestock/2025_AR.pdf` | `data/raw/manual/livestock/2025_AR_ocr.pdf` | `8e6d5c1470d62250f2ce75b6bdc69018f9baa1492a8819f9fa1dafae2731e5d2` | `6ea28e2d91545f56b24ac160a8fe3368c9ce4321534ef23ac6a36b045b60b292` |

The tools and settings are the same as for the earlier copies. The full record is in `data/interim/phase2_ocr_log.csv`.

### Owner batch 1 of the tier-1 minimum download list (browser downloads by the owner, 2026-11-17)

The owner downloaded these files in a browser on 2026-11-17 and named the source sites as greenwichregistrars.com, unilevernigeria.com and africanfinancials.com document pages. I made no request to any site.
- **Which site each file came from** was not stated per file. The `ng-<ticker>-<year>-ar-00.pdf` names follow the africanfinancials.com pattern seen in earlier owner rounds; this is an inference.
- **Copies:** each file was copied (not moved) into `data/raw/manual/<firm>/` under a new name. The originals in the owner's Downloads folder are untouched, and every copy is byte-identical to its original (SHA-256 checked).
- **Identity check:** firm and fiscal year were checked from the cover, contents and statement headings (PyMuPDF text layer).
- **Status:** **not yet processed into the corpus** (owner instruction).

| Ticker | FY | Copy | Original file name | Bytes | Pages | SHA-256 |
|---|---|---|---|---|---|---|
| NESTLE | 2020 | `data/raw/manual/nestle/2020_AR.pdf` | Nestle-Annual-Report-Accounts-2020.pdf | 8,040,718 | 177 | `f955b99e7499d56952d62d4c93e82d98ff9433e7debf0cabff5a97040f8fbe3d` |
| UNILEVER | 2020 | `data/raw/manual/unilever/2020_AR.pdf` | unilever-nigeria-plc-2020-annual-report.pdf | 24,900,405 | 169 | `504a6fce5ec2f6acc130f67b66d23209ca3afe3f3eb56ffd3054a77b1ef912ae` |
| NB | 2020 | `data/raw/manual/nb/2020_AR.pdf` | ng-nb-2020-ar-00.pdf | 2,727,331 | 110 | `e11e61543a45e4f3c5c3da4493db782ef5b2bfdb7d73698dbc811f5e6db28329` |
| SEPLAT | 2020 | `data/raw/manual/seplat/2020_AR.pdf` | ng-seplat-2020-ar-00.pdf | 15,825,272 | 312 | `28daec3ffac1718af96e66274fd2efe81a6d09ac3041f3e18eefbe4d63916da1` |
| HBMNG (Lafarge Africa) | 2020 | `data/raw/manual/hbmng/2020_AR.pdf` | ng-wapco-2020-ar-00.pdf | 1,722,057 | 72 | `d1b78eaa96756626fdc797d5057877c0dbd51f1b1db5da091b2b68cbdf87696a` |
| BUAFOODS | 2022 | `data/raw/manual/buafoods/2022_AR.pdf` | ng-buaf-2022-ar-00.pdf | 6,810,397 | 194 | `c3981401aa0e466b59c747b47c186063f20993f28a69f5aa8ec3607e11c8425c` |

**Content check** (all six have a text layer on almost every page):

- **Nestlé FY2020: full annual report.** Cover "2020 Annual Report and Accounts". Contents: chairman's statement (pp9–10), corporate governance report, directors' report, then the auditor's report and financial statements (year ended 31 December 2020).
- **Unilever FY2020: full annual report.** "Unilever Nigeria Plc Annual Report and Financial Statements 2020" (PDF title). Chairman's statement pp15–18 ("Esteemed Shareholders …"), the 2020 Sustainability Report pp50–58, then the financial statements. Cover and section headings are images, so pp1–2 carry no text.
- **NB FY2020: annual report and accounts in a plain, text-only format.** Cover "Nigerian Breweries Plc RC: 613 2020 Annual Report and Accounts" (year ended 31 December 2020).
  - **Narrative:** corporate profile, board profiles, notice of AGM, a **directors' report (report pp13–22)**, and the board evaluation / corporate governance audit report.
  - **No chairman's or managing director's statement.** The designed edition, if there is one, may carry these.
  - **Recorded type:** annual report (narrative limited to the directors' report and governance).
- **HBMNG (Lafarge Africa) FY2020: financial statements with a directors' report, not a full annual report.** The cover says "Lafarge Africa Plc Annual Report 31 December 2020", but the PDF title is "Lafarge Africa 2020 Financial Statements".
  - **Contents:** corporate information, **directors' report (report pp4–6)**, audit committee report, directors' responsibilities, auditor's report, statements, notes, value added and five-year summary.
  - **No chairman's statement or other narrative.**
  - **Recorded type:** FS filing (as for the other FS filings).
  - HBMNG is the current ticker of Lafarge Africa Plc (formerly WAPCO).
- **BUA Foods FY2022: full annual report.** "Expanding Frontiers: Annual Report & Financial Statements 2022". Chairman's statement, MD/CEO review, sustainability sections, corporate governance and directors' report, then the financial statements.

**Folder note for processing:** NB's earlier report is in `nigerian_breweries/` and Lafarge's in `pilot_reports/lafarge_africa/`. The new files are in `nb/` and `hbmng/`, as the owner named them. The inventory script's folder-to-ticker map will need these two folders added when the batch is processed.

### Owner batch 2 of the tier-1 minimum download list (browser downloads by the owner, 2026-11-17)

**Source:** downloaded by the owner in a browser on 2026-11-17, from africanfinancials.com document pages, except Dangote Sugar, which came from the company's own site (sugar.dangote.com). I made no request to any site.

**Copies:** each file was copied (not moved) into **the firm's existing folder** (owner instruction), under the name `<FY>_AR.pdf`. The originals in the owner's Downloads folder are untouched, and every copy is byte-identical to its original (SHA-256 checked). Three of these folders were created for automated downloads in earlier phases (`pilot_reports/`, `phase2_reports/`); the files placed there now are owner downloads, as recorded here.

**Status:** not yet processed into the corpus (owner instruction).

| Ticker | FY | Copy | Original file name | Bytes | Pages | SHA-256 |
|---|---|---|---|---|---|---|
| BETAGLAS | 2020 | `data/raw/pilot_reports/beta_glass/2020_AR.pdf` | ng-betagl-2020-ar-00.pdf | 2,969,340 | 120 | `029a5e0c67ad5aa85ac822513007f08080150f82caf720ea01e678999dca6166` |
| DANGSUGAR | 2020 | `data/raw/phase2_reports/dangsugar/2020_AR.pdf` | DSR-2020-AR-web-latest.pdf | 19,796,381 | 204 | `463c81cf6b72249342b7680276fa07a2c421f1fc783f358e074d6511f78081f0` |
| FIDSON | 2020 | `data/raw/manual/fidson/2020_AR.pdf` | ng-fidson-2020-ar-00.pdf | 4,371,104 | 88 | `3873d1c750da8c461bbd9d95992c50b6c166f9a97acae72871d9eb08de519714` |
| LIVESTOCK | 2020 | `data/raw/manual/livestock/2020_AR.pdf` | ng-livest-2020-ar-00.pdf | 63,898,707 | 106 | `2a53abf4bfd8746a1f4feb1ec3523ab69af6886107f02190ab6b09b39604dc7d` |
| MAYBAKER | 2020 | `data/raw/phase2_reports/maybaker/2020_AR.pdf` | ng-maybak-2020-ar-00.pdf | 27,330,970 | 111 | `99e14cb8b4732c7c1719bbcca4ba52e03097a43446ff01b79b4679e850ebb00e` |
| NEIMETH | 2020 | `data/raw/phase2_reports/neimeth/2020_AR.pdf` | ng-neimet-2020-ar-00.pdf | 6,861,688 | 124 | `0e72ca1aafb0aeeaf403a5748eec6dd6205fd0b9b246b1c492f03d3262330982` |

**Content check:**

- **Beta Glass FY2020: full annual report.** "Beta Glass Plc Annual Report 2020", year ended 31 December 2020. Chairman's statement (pp12–16), managing director's report (pp17–19), corporate governance, then the auditor's report and financial statements (from p43). Text layer on 109 of 120 pages.
- **Dangote Sugar FY2020: full annual report.** "Dangote Sugar 2020 Annual Report & Financial Statements". Chairman's statement (report pp14–17), MD/CEO review, sustainability sections, corporate governance and directors' report, then the financial statements. Text layer on 178 of 204 pages.
- **Fidson FY2020: annual report and accounts in a plain format, scanned with no text layer** (88 pages, all image).
  - **Checked from page images:** the cover reads "Fidson Healthcare Plc — Annual Report and Financial Statements for the year ended 31 December 2020". Contents: corporate information, results at a glance, **report of the directors (pp. v–viii)**, **corporate governance report (pp. ix–xvi)**, directors' responsibilities, audit committee report, auditor's report, statements, notes, value added, five-year summary.
  - **No chairman's statement.**
  - **Recorded type:** annual report (narrative: directors' report and corporate governance report).
  - **Will fail A1 readability (no text), so it will be OCR'd under A1/A2 when processed.**
- **Livestock Feeds FY2020: full annual report** ("2020 Annual Report & Financial Statements", year ended 31 December 2020). Chairman's statement (pp16–19), directors' report, then the financial statements.
  - **It is not a scan:** there is a text layer on 91 of 106 pages, despite the 64 MB size.
  - It has **the same text-layer quirks as Livestock FY2025**: about 16,800 U+0003 characters used as spaces (handled by A15) and 239 private-use glyphs (A13 maps U+F001/U+F002).
- **May & Baker FY2020: full annual report** (year ended 31 December 2020). Contents, chairman's statement, directors' report, sustainability section (pp27–28), corporate governance, then the auditor's report and financial statements (from p35). Pages 1–3 (cover) carry no text; 29 private-use glyphs.
- **Neimeth FY2020: full annual report**, "Neimeth International Pharmaceuticals Plc 2020 Annual Report".
  - **Fiscal year confirmed:** "year ended 30 September 2020" (48 mentions), so it is FY2020 under design b (the calendar year in which the fiscal year ends).
  - **Contents:** chairman's statement (pp17–20), MD/CEO report (pp21–29), corporate governance (from p30), then the auditor's report and financial statements (from p71).

**Folder-to-ticker map for processing:** no new folders were needed in batch 2.
- **Pilot and Phase 2 folders** (`beta_glass`, `dangsugar`, `maybaker`, `neimeth`): the inventory script takes the ticker from the folder, and the year and type from the file name. `2020_AR` gives type AR, which is correct for all four.
- **`manual/fidson` and `manual/livestock`:** already mapped from the census frame.
- **Still to add from batch 1:** the `nb/` and `hbmng/` folders. Batch 1's Lafarge FY2020 must also be recorded as type FS, not AR (it is financial statements with a directors' report).

### Owner batch 3 of the tier-1 minimum download list (browser downloads by the owner, 2026-11-17)

**Source:** downloaded by the owner in a browser on 2026-11-17, from africanfinancials.com document pages, except Cutix, which came from the company's own site (cutixplc.com.ng). I made no request to any site.

**Fiscal year was checked before naming:** each file is named `<FY>_AR.pdf`, with FY = the calendar year in which the fiscal year ends (design b). All six turned out to be FY2020.

**Copies:** copied (not moved) into each firm's existing folder. The originals in the owner's Downloads folder are untouched, and every copy is byte-identical to its original (SHA-256 checked).

**Status:** not yet processed into the corpus (owner instruction).

| Ticker | FY | Year-end (from the document) | Copy | Original file name | Bytes | Pages | SHA-256 |
|---|---|---|---|---|---|---|---|
| CUTIX | 2020 | 30 April 2020 | `data/raw/phase2_reports/cutix/2020_AR.pdf` | Cutix-Plc-2020-Annual-Report-Accounts.pdf | 21,439,045 | 96 | `746fff9b32ec693a755e388ffbeaee7a68ba9940cb1e7e8583399b8e0b8cb5fc` |
| HONYFLOUR | 2020 | 31 March 2020 | `data/raw/phase2_reports/honyflour/2020_AR.pdf` | ng-honyfl-2020-ar-00.pdf | 37,960,714 | 113 | `d3e871079b03ab030f5cd520b107f54cc19299c5479b5360a284fe802bfa1fa1` |
| VITAFOAM | 2020 | 30 September 2020 | `data/raw/phase2_reports/vitafoam/2020_AR.pdf` | ng-vitafo-2020-ar-00.pdf | 42,572,947 | 128 | `f09c92dd77418cccf2ed3e458280dd2ddcca63aef12f01dbaf4e7439c4bee71c` |
| NNFM | 2020 | 31 March 2020 | `data/raw/manual/nnfm/2020_AR.pdf` | ng-nnfm-2020-ar-00.pdf | 6,768,443 | 202 | `05dfce10279852b8e99213d42c20ff9077827caad620d9aa20cb308fddbd5f09` |
| ACADEMY | 2020 | 31 March 2020 | `data/raw/manual/academy/2020_AR.pdf` | ng-academ-2020-ar-00.pdf | 1,565,948 | 100 | `cf572d228db4564affeee89b442ff6cc28fbd5b0b1a12d29aa7ce45222f124db` |
| ALEX | 2020 | 31 December 2020 | `data/raw/manual/alex/2020_AR.pdf` | ng-alex-2020-ar-00.pdf | 15,278,821 | 102 | `b4f2997dd98d0e58ccab4c81b2bc75b98178030db48379a5d0d8590b8dc759ed` |

**Content check:**

- **Cutix FY2020** (year ended 30 April 2020): **full annual report** ("Cutix Plc Annual Report & Accounts 2020"). Chairman's statement (pp16–18), directors' report and corporate governance, then the auditor's report and financial statements. Text layer on 77 of 96 pages.
- **Honeywell Flour Mills FY2020** (year ended 31 March 2020): **full annual report** ("Annual Report 2020: Breaking Barriers").
  - **Contents:** strategic report (chairman's letter, managing director's Q&A), governance report (directors' profiles, corporate governance report, community and stakeholder sections), financial statements, and investor information.
  - Text layer on 99 of 113 pages; 128 private-use glyphs.
- **Vitafoam FY2020** (year ended 30 September 2020; the statement of financial position is "as at 30 September, 2020"): **full annual report** ("2020 Annual Reports & Account").
  - **Contents:** chairman's statement (p11), board profiles, report of the directors (p17), then the auditor's report (p33), statements and notes.
  - **Scanned/image layout:** only 5 of 128 pages have a text layer, so identity and FY were checked from page images.
  - **It will fail A1 readability and be OCR'd when processed.**
- **NNFM FY2020** (year ended 31 March 2020): **full annual report**. Chairman's statement (p17), report of the directors (p37), corporate governance report (p44), then the auditor's report and financial statements. Text layer on 184 of 202 pages; 75 private-use glyphs.
- **Academy Press FY2020** (year ended 31 March 2020): **annual report and accounts in a plain format** ("Report of the Directors; Consolidated and Separate Audited Financial Statements and Other National Disclosures").
  - **Narrative:** **report of the directors (pp5–9)** and **corporate governance report (pp10–14)**. **No chairman's statement.**
  - **Recorded type:** annual report (narrative: directors' report and corporate governance report).
- **Alex FY2020** (year ended 31 December 2020): **full annual report** ("ALEX Annual Report & Accounts 2020"). Contents: notice of AGM, company overview, financial highlights, **chairman's statement (p8)**, **report of directors (pp9–16)**, audit committee and auditor's reports, statements, notes, value added, five-year summary, proxy form and unclaimed dividend list. Text layer on 101 of 102 pages.

**For processing:**

- **Alex type:** in `src/phase4_corpus.py`, ALEX is in the `MANUAL_FS` set, because its FY2024 file is a financial-statement filing. That set assigns type FS to every ALEX file in `data/raw/manual/alex/`. **Alex FY2020 is a full annual report and must be typed AR**: the type rule needs a per-file exception.
- **Folders:** all six folders already exist and are mapped. The `nb/` and `hbmng/` folders from batch 1, and Lafarge FY2020 as type FS, are still to be added.
- **OCR:** Vitafoam FY2020 and Fidson FY2020 (batch 2) have essentially no text layer and will be OCR'd under A1/A2.

### Owner batch 4 of the tier-1 minimum download list (browser downloads by the owner, 2026-11-17; last tier-1 batch)

**Source:** downloaded by the owner in a browser on 2026-11-17 from africanfinancials.com document pages. I made no request to any site.

**Fiscal year was checked before naming;** each file is named `<FY>_AR.pdf` (FY per design b). **Two file names do not match their content:**
- `ng-japaul-2020-ar-00.pdf` is **FY2021**.
- `ng-aradel-2021-ar-00.pdf` is FY2021, as its name says.

**Copies:** copied (not moved) into each firm's existing folder. The originals are untouched, and every copy is byte-identical to its original (SHA-256 checked).

**Status:** not yet processed into the corpus.

| Ticker | FY | Year-end (from the document) | Copy | Original file name | Bytes | Pages | SHA-256 |
|---|---|---|---|---|---|---|---|
| ELLAHLAKES | 2020 | 31 July 2020 | `data/raw/manual/ellahlakes/2020_AR.pdf` | ng-ellahl-2020-ar-00.pdf | 3,708,405 | 46 | `db31b4eb2c41c682f1fefb92cc92888e7032e51d344b36ea969ec717dc629466` |
| JAPAULGOLD | **2021** | 31 December 2021 | `data/raw/manual/japaulgold/2021_AR.pdf` | ng-japaul-2020-ar-00.pdf | 2,380,342 | 88 | `b6d2c56a56ae53c546d4628b09d58034b33fd6bde115e4ec2834341bb2cca2d5` |
| TRANSPOWER | 2020 | 31 December 2020 | `data/raw/manual/transpower/2020_AR.pdf` | ng-tpower-2020-ar-00.pdf | 3,599,852 | 69 | `d323369362ab45df6a121c4b37dbff360efd154f0463e406d77ca948415c0b34` |
| ARADEL | 2021 | 31 December 2021 | `data/raw/manual/aradel/2021_AR.pdf` | ng-aradel-2021-ar-00.pdf | 9,211,174 | 129 | `a47818474c275e0ecd0aa6cd7decbcbe3ca2cee62bf6d16b79cd656c9c07e0bb` |
| GEREGU | 2022 | 31 December 2022 | `data/raw/manual/geregu/2022_AR.pdf` | ng-geregu-2022-ar-00.pdf | 4,264,449 | 72 | `665559d9af613b537d0127e6cc71dfe3168cf2606e026d62d2bdb63bf43ae774` |

**Content check:**

- **Ellah Lakes FY2020: financial statements with a directors' report; scanned (no text layer).**
  - **Checked from page images:** "Ellah Lakes Plc, Consolidated Financial Statements for the period ended 31 July 2020".
  - **Contents:** corporate information, results at a glance, report of the directors (pp4-5), certification, directors' responsibilities, audit committee, auditor's report, statements, notes, value added, five-year summary.
  - **Recorded type:** FS. It will be OCR'd under A1/A2.
- **Japaul Gold FY2021: financial statements only.** "Japaul Gold & Ventures Plc, Consolidated and Separate Financial Statements for the year ended 31 December 2021".
  - **Contents:** auditor's report, statements, notes, value added, financial summary, directors' responsibilities.
  - **No directors' report or other narrative.** The auditor's report says the chairman's statement, directors' report and corporate governance report were "expected to be made available ... after that date".
  - **Recorded type:** FS. It still counts as a document-year for H3 (h).
- **Transcorp Power FY2020: financial statements with a directors' report.** "Transcorp Power Limited, Annual Reports and Accounts for the year ended 31 December 2020".
  - **Contents:** corporate information, reports of the directors (pp ii-v), directors' responsibilities, auditor's report, statements, notes, value added, five-year summary.
  - **No chairman's or other narrative.** **Recorded type:** FS.
  - Note the issuer name: "Limited" in 2020; the listed entity is Transcorp Power Plc.
- **Aradel FY2021: full annual report** under the company's former name, **Niger Delta Exploration & Production Plc (NDEP)**: "Annual Report & Accounts 2021, Investing in Growth".
  - **Contents:** at a glance, strategic report, chairman's statement (pp10-14), health/safety/environment, directors' report, corporate governance (pp37-40), then the auditor's report (p43) and financial statements.
- **Geregu FY2022: annual report and accounts in a plain format.**
  - **Contents:** corporate information, **directors' report (p4)**, **corporate governance report (pp7-20)**, directors' and corporate responsibility statements, audit committee, auditor's report, statements, notes, value added, five-year summary.
  - **No chairman's statement.** **Recorded type:** annual report (narrative: directors' report and corporate governance report).

**Listing status (owner decision may be needed).** Two of these files predate the issuer's NGX listing as I understand it; this was not verified from a primary source in this step:
- **Transcorp Power** is understood to have listed on NGX in 2024. FY2020 is a "Limited" company report.
- **Aradel / NDEP** is understood to have listed on NGX in October 2024.

The design's RQ concerns "NGX-listed firms ... in 2020-2025" and says firms enter "only for years with documents" (h). **It does not say whether pre-listing years count.** If they do not, these two firm-years leave H3, and Transcorp Power and Aradel would still have only one year each. **Geregu** is understood to have listed in October 2022, during FY2022.

### Tier-1 minimum download list: complete (23 of 23 firms filed, 2026-11-17; not yet processed)

"Full AR" = chairman's/CEO statement and other narrative. "Plain AR" = annual report and accounts whose narrative is the directors' report and, where stated, the corporate governance report. "FS" = financial statements, with at most a short directors' report.

| Firm | Held before | New FY | New document | Scanned (no text layer)? |
|---|---|---|---|---|
| ACADEMY | FY2025 AR | 2020 | Plain AR (directors' report + corporate governance) | No |
| ALEX | FY2024 FS | 2020 | Full AR | No |
| ARADEL | FY2025 AR | 2021 | Full AR (as NDEP Plc; pre-listing year?) | No |
| BETAGLAS | FY2023 AR | 2020 | Full AR | No |
| BUAFOODS | FY2024 AR | 2022 | Full AR | No |
| CUTIX | FY2025 FS | 2020 | Full AR | No |
| DANGSUGAR | FY2025 FS | 2020 | Full AR | No |
| ELLAHLAKES | FY2024 FS | 2020 | FS with directors' report | **Yes** |
| FIDSON | FY2025 AR | 2020 | Plain AR (directors' report + corporate governance) | **Yes** |
| GEREGU | FY2024 AR | 2022 | Plain AR (directors' report + corporate governance) | No |
| HBMNG | FY2023 FS | 2020 | FS with directors' report | No |
| HONYFLOUR | FY2025 FS | 2020 | Full AR | No |
| JAPAULGOLD | FY2025 FS | **2021** | FS only (no narrative) | No |
| LIVESTOCK | FY2025 AR | 2020 | Full AR (U+0003 spaces, handled by A15) | No |
| MAYBAKER | FY2025 FS | 2020 | Full AR | No |
| NB | FY2025 AR | 2020 | Plain AR (directors' report + governance) | No |
| NEIMETH | FY2025 FS | 2020 | Full AR (year ended 30 Sept 2020) | No |
| NESTLE | FY2025 AR | 2020 | Full AR | No |
| NNFM | FY2025 AR | 2020 | Full AR | No |
| SEPLAT | FY2025 IAR | 2020 | Full AR | No |
| TRANSPOWER | FY2025 AR | 2020 | FS with directors' report (as Transcorp Power Limited; pre-listing year?) | No |
| UNILEVER | FY2025 AR | 2020 | Full AR | No |
| VITAFOAM | FY2025 FS | 2020 | Full AR (year ended 30 Sept 2020) | **Yes** (5 of 128 pages have text) |

**Totals:** 15 full AR, 4 plain AR, 4 FS (3 with a short directors' report, 1 FS only). 3 are scanned and will be OCR'd under A1/A2. By FY: 2020 for 19 firms, 2021 for 2 (Aradel, Japaul), 2022 for 2 (BUA Foods, Geregu).

**For processing (all batches):**
- **Folder map:** add `manual/nb/` -> NB and `manual/hbmng/` -> HBMNG.
- **Per-file type exceptions:**
  - `manual/hbmng/2020_AR.pdf` -> FS.
  - `manual/transpower/2020_AR.pdf` -> FS.
  - `manual/alex/2020_AR.pdf` -> AR (ALEX is in the `MANUAL_FS` set).
- **Correct by default:** `manual/ellahlakes/2020_AR.pdf` and `manual/japaulgold/2021_AR.pdf` are typed FS by the existing `MANUAL_FS` rule.

### Owner batch 5: post-listing replacement years for H3 (browser downloads by the owner, 2026-11-17; amendment A16)

**Why these files:** under A16, Transcorp Power FY2020 and Aradel FY2021 predate the firms' NGX listings (4 March 2024 and 14 October 2024), so they count for H3 only as a robustness check. These two files give each firm a post-listing year.

**Source:** downloaded by the owner in a browser on 2026-11-17:
- Transcorp Power from an africanfinancials.com document page (`ng-tpower-2024-ar-00`);
- Aradel from the company's own site.

**Copies:** copied (not moved), byte-identical (SHA-256 checked). The originals are untouched.

| Ticker | FY | Year-end | Copy | Original file name | Bytes | Pages | SHA-256 |
|---|---|---|---|---|---|---|---|
| TRANSPOWER | 2024 | 31 December 2024 | `data/raw/manual/transpower/2024_AR.pdf` | ng-tpower-2024-ar-00.pdf | 3,060,671 | 85 | `50402dd27348c4b894d71c26914807c3f80cd82513acaf1250900508a2dff361` |
| ARADEL | 2024 | 31 December 2024 | `data/raw/manual/aradel/2024_AR.pdf` | Aradel_2024_Annual_Report.pdf | 17,538,293 | 222 | `967d0d5a47a7caf31af01d9ff63c879ce543a615c30dc3ed83bde42095680c29` |

**Content check:**

- **Transcorp Power FY2024: annual report and accounts in a plain format.** "Transcorp Power Plc (Formerly Transcorp Power Limited), Annual Reports and Accounts for the year ended 31 December 2024".
  - **Narrative:** **reports of the directors (pp ii–vii)** and **corporate governance report (pp viii–xviii)**, then the audit committee, ICFR, auditor's reports and financial statements.
  - **No chairman's statement.** **Recorded type:** annual report.
  - Text layer on 83 of 85 pages.
- **Aradel FY2024: full annual report.** "Sustaining Momentum, 2024 Annual Report & Accounts", year ended 31 December 2024.
  - **Contents:** chairman's statement, sustainability section (pp28–30), corporate governance, directors' report (pp56–59), then the auditor's report (p61) and financial statements.
  - Text layer on 188 of 222 pages.
  - About 6,100 control characters in the text layer (handled by A15).
  - **A2 page rule: 30% of pages below 0.20, so the file is OCR'd** (see below).

### Readability and OCR of the Phase 4 tier-1 files (2026-11-17)

`src/readability.py` was extended to include owner files placed in the pilot/Phase 2 folders, then re-run. The 107 earlier A1 results and the 83 earlier A2 results are unchanged.

- **A1** (document common-word share ≥ 0.25): two files fail, Ellah Lakes FY2020 and Fidson FY2020 (both scans with no text layer, share 0). All others pass (0.40–0.60).
- **A2** (OCR if more than 10% of pages have a share below 0.20): **8 files are OCR'd** with the same tools and settings as before (`src/phase2_ocr.py`; full record in `data/interim/phase2_ocr_log.csv`):

| File | Pages | Pages below 0.20 |
|---|---|---|
| Ellah Lakes FY2020 | 46 | 46 (100%) |
| Fidson FY2020 | 88 | 88 (100%) |
| Vitafoam FY2020 | 128 | 123 (96%) |
| Aradel FY2024 | 222 | 66 (30%) |
| Alex FY2020 | 102 | 29 (28%) |
| Aradel FY2021 | 129 | 23 (18%) |
| Unilever FY2020 | 169 | 29 (17%) |
| May & Baker FY2020 | 111 | 15 (14%) |

All eight OCR copies were completed on 2026-11-17, one file at a time after a power loss interrupted the run (`docs/phase4_corpus.md` section 6). Originals were unchanged (SHA-256 checked before and after), and every copy is logged.

### Owner batch 6: Phase 6 policy and Seplat source files (browser downloads by the owner, 2026-11-18)

**Copies:** all three files were copied, not moved, from the owner's Downloads folder to `data/raw/manual/policy/`. They are byte-identical (SHA-256 checked) and the originals are untouched. `data/raw/` is gitignored, so none of these files is committed.

| File | Source | Bytes | Pages | SHA-256 |
|---|---|---|---|---|
| `issb-2026-a-ifrs-s2-climate-related-disclosures.pdf` | ifrs.org, IFRS S2 ("Standard 2026 Issued") | 301,513 | 48 | `0fb0856bba2342e9cb110ddf92f4522d270e7205c81d595114763586e27093d0` |
| `seplat-energy_sustainability-report_2023_screen.pdf` | seplatenergy.com | 46,340,282 | 122 | `0c473d8731927626af74d70c022ef8eee6ece790a419394f2bd1263d95b8a1b5` |
| `2025-social-performance-report-1.pdf` | seplatenergy.com | 46,131,580 | 111 | `0019a5dab4d86d474c758681d60a3e0c18389c596e46ddca00b1a3f4950656d9` |

**IFRS S2: full standard text, not an amendments document.**
- **Edition:** PDF title "ISSB-2026-A – Issued IFRS Standards", created 2026-04-23. The consolidated edition of IFRS S2 *Climate-related Disclosures* (issued June 2023), incorporating the *Amendments to Greenhouse Gas Emissions Disclosures* issued in December 2025.
- **Contents:** objective, scope, and the core content (per the contents page, governance from paragraph 5, strategy from 8, risk management from 24, metrics and targets from 27). Appendix A (defined terms), Appendix B (application guidance) and Appendix C (effective date and transition) are all present. Text layer on all pages.
- **Effective date (para C1):** annual reporting periods beginning on or after 1 January 2024, with earlier application permitted. The December 2025 amendments apply from 1 January 2027 (para C1B, listing the paragraphs changed in C1A).
- **Accompanying documents** (illustrative examples, industry-based guidance, basis for conclusions) are in Parts B and C of the edition and are **not** in this file.
- **Licence:** personal, non-commercial use. The file stays out of git. Project outputs cite paragraph numbers only and paraphrase; the standard's text is not quoted.

**Seplat reports (Phase 6 policy coding source only).**
- **SEPLAT 2023 Sustainability Report:** cover "Seplat Energy Plc Sustainability Report 2023"; contents include the 2023 highlights. Text layer on 120 of 122 pages. The PDF title metadata reads "Seplat Energy SR_2022_v20", a template label; the content is FY2023.
- **SEPLAT 2025 Social Performance Report:** "2025 Social Performance Report". Text layer on 110 of 111 pages.
- These are the two Seplat documents listed in Phase 4 as "requested from owner (pending before Phase 6)".
- **Not added to the Phase 4 corpus** (owner instruction, 2026-11-18). No paragraph, measure or outcome was changed. They are held for the Phase 6 policy coding only.

## 5. NLP models (Hugging Face)

All four models below are licensed Apache-2.0 according to the Hugging Face API tags, and none is gated. Weights were downloaded as `model.safetensors` into `data/raw/hf_cache/`, which is not committed.

| Model | URL | Labels | Input limit |
|---|---|---|---|
| climatebert/distilroberta-base-climate-detector | https://huggingface.co/climatebert/distilroberta-base-climate-detector | no, yes | 512 tokens (tokenizer `model_max_length`); `max_position_embeddings` 514 |
| climatebert/distilroberta-base-climate-specificity | https://huggingface.co/climatebert/distilroberta-base-climate-specificity | non, spec | 512 tokens |
| climatebert/distilroberta-base-climate-tcfd | https://huggingface.co/climatebert/distilroberta-base-climate-tcfd | governance, metrics, risk, strategy | 512 tokens |
| climatebert/distilroberta-base-climate-sentiment | https://huggingface.co/climatebert/distilroberta-base-climate-sentiment | neutral, opportunity, risk | 512 tokens |

Model list: https://huggingface.co/api/models?author=climatebert (16 models, accessed through the public API).

## 6. Literature and industry reviews

| Source | Identifier | How verified |
|---|---|---|
| Webersinke, Kraus, Bingler, Leippold, "ClimateBert: A Pretrained Language Model for Climate-Related Text" | arXiv:2110.12010 (dated 2021-10-22); SSRN DOI 10.2139/ssrn.4229146 | arXiv abstract page metadata; Crossref |
| Bingler, Kraus, Leippold, Webersinke (2022), "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures", *Finance Research Letters* 47, 102776 | DOI 10.1016/j.frl.2022.102776 | Crossref |
| Bingler, Kraus, Leippold, Webersinke (2024), "How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk", *Journal of Banking & Finance* 164, 107191 | DOI 10.1016/j.jbankfin.2024.107191 | Crossref |
| Meyer & Rowan (1977), "Institutionalized Organizations: Formal Structure as Myth and Ceremony", *American Journal of Sociology* 83(2), 340–363 | DOI 10.1086/226550 | Crossref |
| Bromley & Powell (2012), "From Smoke and Mirrors to Walking the Talk: Decoupling in the Contemporary World", *Academy of Management Annals* 6(1), 483–530 | DOI 10.5465/19416520.2012.684462 | Crossref |
| Marquis, Toffel & Zhou (2016), "Scrutiny, Norms, and Selective Disclosure: A Global Study of Greenwashing", *Organization Science* 27(2), 483–504 | DOI 10.1287/orsc.2015.1039 | Crossref |
| Marquis & Qian (2014), "Corporate Social Responsibility Reporting in China: Symbol or Substance?", *Organization Science* 25(1), 127–148 | DOI 10.1287/orsc.2013.0837 | Crossref |
| Doorasamy, Fapetu & Adewumi (2026), "Climate Finance, Environmental Risk Accounting and Firm Value: A Comparative Study of Nigeria and South Africa", *Journal of Risk and Financial Management* 19(8), 598 | DOI 10.3390/jrfm19080598 | Crossref. The description of its method comes from a search result |
| Yahaya (2026), "Climate Risk Governance and Firm Performance of Listed Nigerian Firms" | https://zenodo.org/records/19064530 | Zenodo record page (abstract read) |
| Kuzma et al. (2023), "Aqueduct 4.0: Updated Decision-Relevant Global Water Risk Indicators", WRI technical note | DOI 10.46830/writn.23.00061 | Crossref |
| "Asset-Level Physical Climate Risk Disclosure" (book chapter; pharmaceutical case study) | https://www.researchgate.net/publication/346407477_Asset-Level_Physical_Climate_Risk_Disclosure | Search result only. Authors and year not verified; no Crossref match found |
| IPMC ESG Ratings Report 2025 (press coverage only) | https://guardian.ng/?p=2724317 ; https://www.thisdaylive.com/2025/11/19/ipmc-zenith-access-bank-others-driving-esg-in-financial-sector | Guardian article read; primary report not obtained |
| Sustainable Stories Africa, NGX30 Sustainability Report Review 2024 (press coverage only) | https://nairametrics.com/2026/10/20/nigerias-largest-listed-companies-have-crossed-a-meaningful-esg-threshold/ | Article read; primary review not obtained. The 25 September 2026 Nairametrics URL from search returned this same 20 October article, so the earlier article was not read |

### Citation re-verification for the paper (Phase 8, 2026-11-18)

**Network attempt (this session).**
- **Unreachable:** api.crossref.org failed on DNS on every attempt, and journals.aom.org, mdpi.com, pubsonline.informs.org and journals.uchicago.edu were unreachable.
- **Refused:** www.sciencedirect.com's robots.txt returned 403, so it was not fetched.
- **Read:** pages whose robots.txt allows access, read through the web-fetch tool:
  - arXiv: https://arxiv.org/abs/2110.12010 (Webersinke, Kraus, Bingler, Leippold, with given names);
  - Zenodo: https://zenodo.org/records/19064530 (Yahaya, Onipe Adabenege; *Journal of Accounting, Finance and Auditing* 17(3), 10–44, 2026) and https://zenodo.org/records/7199437 (Speer, R., wordfreq v3.0.2, 2022);
  - WRI: https://www.wri.org/research/aqueduct-40-updated-decision-relevant-global-water-risk-indicators (Kuzma, Bierkens, Lakshman, Luo, Saccoccia, Sutanudjaja, Van Beek, 2023).

**Verified by the owner's assistant on 2026-11-18** (library, RePEc and repository records; reported to the analyst, not fetched in this session). The source records are named below as reported, and the owner supplied their URLs (added 2026-11-18, listed after the table).

| # | Citation as verified | Source records named | Agreement with the Phase 0 Crossref record (§6 above) |
|---|---|---|---|
| 1 | Meyer, J. W., & Rowan, B. (1977). *American Journal of Sociology* 83(2), 340–363 | econbiz.de record | Agrees |
| 2 | Bromley, P., & Powell, W. W. (2012). *Academy of Management Annals* 6(1) | econbiz.de; Stanford PACS page | Agrees. Pages 483–530 taken from the Phase 0 Crossref record |
| 3 | Marquis, C., Toffel, M. W., & Zhou, Y. (2016). *Organization Science* 27(2), 483–504; https://doi.org/10.1287/orsc.2015.1039 | RePEc EconPapers; INFORMS supplement page | Agrees |
| 4 | Marquis, C., & Qian, C. (2014). *Organization Science* 25(1), 127–148 | RePEc EconPapers | Agrees |
| 5 | Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). *Finance Research Letters* 47 (Part B) | RePEc IDEAS | Agrees. Article number 102776 taken from the Phase 0 record; "Part B" is not in the Phase 0 record |
| 6 | Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). "How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk", *Journal of Banking & Finance* 164, 107191 | Phase 0 Crossref record (§6 above); working-paper version: SFI page below | Agrees with Phase 0. **Changed on 2026-11-18 (owner instruction):** first cited as Swiss Finance Institute Research Paper No. 22-54 ("n.d."), now cited as the *Journal of Banking & Finance* version from the Phase 0 Crossref record. The SFI page below is the working-paper version, listed under a different title ("Cheap talk in corporate climate commitments: the effectiveness of climate initiatives") |

**Source URLs supplied by the owner (2026-11-18):**
1. **Meyer & Rowan:** https://econbiz.de/Record/institutionalized-organizations-formal-structure-as-myth-and-ceremony-meyer-john/10002494078
2. **Bromley & Powell:**
   - https://econbiz.de/Record/from-smoke-and-mirrors-to-walking-the-talk-decoupling-in-the-contemporary-world-bromley-patricia/10009614032
   - https://pacscenter.stanford.edu/publication/from-smoke-and-mirrors-to-walking-the-talk-characteristics-and-consequences-of-decoupling-in-the-contemporary-world
3. **Marquis, Toffel & Zhou:** https://econpapers.repec.org/RePEc:inm:ororsc:v:27:y:2016:i:2:p:483-504
4. **Marquis & Qian:** https://econpapers.repec.org/RePEc:inm:ororsc:v:25:y:2014:i:1:p:127-148
5. **Bingler et al. 2022:** https://ideas.repec.org/a/eee/finlet/v47y2022ipbs1544612322000897.html
6. **Bingler et al., cheap talk (working-paper version):** https://www.sfi.ch/en/publications/n-22-54-cheap-talk-in-corporate-climate-commitments-the-effectiveness-of-climate-initiatives

These URLs were supplied by the owner and were not fetched in this session.

**Removed from the paper:** Doorasamy, Fapetu & Adewumi (2026). The method description came from a search result, and the paper could not be re-verified.
