# Manual download list (Phase 2)

These are census firms for which no full-year report for 2023–2025 was found on the firm's own site or on doclib.ngxgroup.com, the two hosts permitted for automated download in Phase 2. Searches ran on 2026-11-07.

Please download the **latest full annual report (FY2023–2025)** for each firm in a browser and save it to `data/raw/manual/<ticker_lowercase>/`. The pages below are leads found by web search. Most are third-party listings (africanfinancials.com, sustainabilityreports.com), which I did not open or download from. "Not located" means the searches found no lead at all.

When a file is added, the firm's document test can be completed and its facilities extracted.

## Update after the owner's decision of 2026-11-07 (aggregator and registrar sites)

Before any download, each newly allowed site's robots.txt and terms were checked, as the owner's rule requires:

| Site | robots.txt | Terms | Result |
|---|---|---|---|
| africanfinancials.com | Allows general agents, but disallows Anthropic's agents by name (ClaudeBot, anthropic-ai, Claude-Web). Content-Signal "ai-train=no, use=reference" | https://africanfinancials.com/terms/ says: "You may not use any data mining tools, robots, or similar data gathering and extraction instruments on the Web Site or any part thereof" | **Not used.** The terms forbid automated access, so the Google Drive route was not used either |
| www.sustainabilityreports.com | Allows general agents | Not read: the homepage returned HTTP 403 to this client | **Not used** (blocked) |
| cardinalstoneregistrars.com (registrar) | Allows general agents, with the same named-agent disallow list as africanfinancials.com | The terms page (/terms-and-conditions) returned HTTP 404, so no terms forbidding downloads were found | **Used** for one file (LIVESTOCK) |
| airtel.africa / cdn-webportal.airtelstream.net (Airtel's own site) | airtel.africa allowed; the PDF host's robots.txt returned HTTP 403 | Not checked | **Not fetched** (blocked) |

**Completed in this round:**

- **LIVESTOCK:** downloaded from the registrar site.
- **THOMASWY:** already in `data/raw/manual/thomaswy/`, identical by SHA-256 to the copy in the owner's Downloads folder. It is a scanned file with no text layer.

**Failed the document test** (owner instructions of 2026-11-07, and of 2026-11-12 for PREMPAINTS):

- **AUSTINLAZ:** only an abridged version was found.
- **PHARMDEKO:** no annual report for 2023–2025 was found.
- **PREMPAINTS:** report not obtainable, 2026-11-12.

## Main census: still to download by hand (none)

- **PREMPAINTS: failed the document test.** The report was not obtainable (owner decision, 2026-11-12). No file was in `data/raw/manual/prempaints/`. The lead was https://africanfinancials.com/company/ng-prempa/.

**Received from the owner and processed (update 3, 2026-11-11).** These 19 were downloaded by the owner in a browser on 2026-11-07, and all pass the document test: AIRTELAFRI (company site), ALEX, CAP, CHAMPION (sustainabilityreports.com), ETERNA, EUNISELL, GEREGU (sustainabilityreports.com), GOLDBREW, IMG, JAPAULGOLD, JBERGER (sustainabilityreports.com), MCNICHOLS, MECURE, MULTITREX, OANDO, TOTAL, TRANSPOWER, TRIPPLEG and UNIONDICON. The others are from africanfinancials.com. File names and SHA-256 are in `docs/data_sources.md`.

## Robustness stratum (15 firms; skipped for now per the owner's instruction)

| Ticker | Issuer (not verified) | Lead found by search |
|---|---|---|
| CAVERTON | Caverton Offshore Support Group | Not located |
| CHELLARAM | Chellarams | Not located |
| EKOCORP | Ekocorp | Not located |
| IKEJAHOTEL | Ikeja Hotel | Not located (doclib holds only Q1 2025 interim statements) |
| JOHNHOLT | John Holt | Not located |
| JULI | Juli | Not located |
| NAHCO | Nigerian Aviation Handling Company | Not located |
| REDSTAREX | Red Star Express | Not located (doclib holds only unaudited statements for the year to 31 Mar 2025) |
| SCOA | SCOA Nigeria | Not located |
| SKYAVN | Skyway Aviation Handling | Not located |
| TANTALIZER | Tantalizers | Not located |
| TRANSCOHOT | Transcorp Hotels | Not located (doclib holds only Q3 2025 interim statements) |
| TRANSEXPR | Trans-Nationwide Express | Not located (doclib holds only unaudited Q4 2025 statements) |
| UACN | UAC of Nigeria | Not located (doclib holds only H1 2025 interim statements) |
| UPDC | UPDC | Not located (doclib holds only unaudited FY2024 statements) |

## Other files still needed

- **Received from the owner (2026-11-07) and processed:** ACADEMY, ARADEL, BUAFOODS (FY2024), ELLAHLAKES, ENAMELWA, FIDSON, MEYER, MULTIVERSE, NNFM (update 2), and the 19 firms listed above (update 3).
- **OCR: done (2026-11-11)** for Okomu FY2023 and FY2024, Thomas Wyatt FY2025, Ellah Lakes FY2024, Multiverse FY2025, McNichols, Union Dicon, Alex, Eterna and Geregu, after the owner installed Ghostscript. Copies have `_ocr` in the name (see `docs/data_sources.md`). Multi-Trex FY2024's 20 image-only pages were OCR'd on 2026-11-12 (owner decision); no facility location was found on them.
- **Pending before Phase 6:** IFRS S2, Seplat's 2023 Sustainability Report and Seplat's 2025 Social Performance Report.
