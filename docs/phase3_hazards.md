# Phase 3: Hazard exposure

**Date:** 2026-11-12, updated the same day after the owner's second round of decisions, and again when the owner's NASA POWER manual downloads arrived. **Updated 2026-11-17:** heat (main) is now scored from ERA5 (method A10, data source A11: hourly point time series), with NASA POWER kept side by side as robustness (section 3.5); water-stress projections for 2030 and 2050 were added as descriptive-only columns (section 3.6). This phase follows the frozen design (`docs/design.md`, section e) and amendments A1–A11. **No report text was read or scored, and no disclosure-versus-exposure analysis was run.** Nothing in this document is a result about disclosure.

**Two amendments were logged in this phase, each before it was applied:**

- **A7:** the owner's 500 m robustness version for grade-A sites, and how the e5, A6 and OD-2 buffer rules combine.
- **A8:** the JRC permanent-water mask as a river-flood robustness check.

Later heat amendments: A9 (MERRA-2 native cells; superseded, never applied), A10 (ERA5 as the main heat source, under OD-7) and A11 (ERA5 hourly point time series as the data route; method unchanged).

**Hashes:**

| File | SHA-256 | Status |
|---|---|---|
| `docs/design.md` | `f563379eb468ca318bc53b1f1dda3d7f687b15759eab5b9acedc9655a7ab1714` | Unchanged since the freeze (re-checked after the heat re-score) |
| `config/parameters.json` | `255e924607910fbb22f9f1206f24c6f545f10119125fee53b91c2d969857bfc2` | Matches the hash recorded in A11, the latest amendment (re-checked 2026-11-17 after the ERA5 heat score) |

## Summary

| Hazard | Status | Data |
|---|---|---|
| River flood (primary) | **Scored** | JRC Global river flood hazard maps v2.1.2: RP100 (main), RP10 and RP500 (robustness); permanent-water mask (A8, robustness) |
| Heat (primary) | **Scored** | **Main:** ERA5 hourly 2 m temperature, 1991–2025, one point series per 0.25° cell (CDS `reanalysis-era5-single-levels-timeseries`; A10 method, A11 source); all 125 sites scored. **Robustness:** NASA POWER (MERRA-2) daily T2M_MAX on the old 0.5° bins (owner manual downloads); 121 sites scored. See 1.4 and 3.5 |
| Coastal flood | **Scored** | WRI Aqueduct Floods v2.0, coastal, baseline, RP100 (owner download) |
| Water stress | **Scored** | WRI Aqueduct 4.0 baseline annual, `bws_cat` (owner download). 2030 and 2050 business-as-usual projections added as **descriptive-only** columns (3.6) |
| Population (OD-16) | **Computed** | WorldPop Global2 R2025A, Nigeria 2025, 100 m, constrained |

- **Sites:** 125 point sites with a coordinate were scored. 71 are in the main analysis set, 51 are offices (descriptive only) and 3 are OSM-sourced (robustness set R2).
- **Firms:** 29 of the 59 census firms that passed the document test get firm scores. The other 30 have no main-analysis site and are listed in `firm_exposure.csv` with the reason.
- **Combined index:** uses all four hazards (OD-8), with heat from ERA5. The same index with NASA POWER heat is kept as `rob_nasa_heat_combined_index`.
- **ERA5 and NASA POWER heat disagree strongly** at site level (section 3.5): the ERA5 exposed tercile lies in the south-west (Lagos, Ogun), the NASA POWER one mainly in the south-east; only 1 of 71 main sites is exposed under both.

## Outputs

| File | Content |
|---|---|
| `data/processed/site_hazards.csv` | One row per scored point site (125). Site set, buffer rule and area. River flood: RP100 main; RP10, RP500, depth ≥ 0.5 m; robustness buffers (A7 and OD-2 separately); permanent water excluded (A8). **Heat, main (ERA5):** `heat_cell_lat/lon`, `heat_tx_p90_c`, `heat_tx90_days_1991_2020`, `heat_tx90_days_2020_2025`, `heat_score`, `heat_tercile_cut`, `heat_exposed`, `heat_source` ("ERA5 hourly time series, CDS (A11)"). **Heat, robustness (NASA POWER):** the same fields prefixed `heat_nasa_` (`heat_nasa_source` says why a site is not scored). Coastal flood: exposure, share, maximum depth, ≥ 0.5 m. Water stress: `pfaf_id`, `bws_raw`, `bws_cat`, `bws_label`, exposure; **descriptive only:** `water_stress_future_bau2030_*` and `_bau2050_*` (raw, cat, label) and `water_stress_future_note`. Population |
| `data/processed/firm_exposure.csv` | One row per census firm (59). E_share, E_any and E_max for river flood, heat (ERA5), coastal flood and water stress; the four-hazard combined index and the river-flood-plus-heat index; robustness E_share and E_any, including NASA POWER heat (`rob_nasa_heat_*`, `rob_nasa_heat_combined_index`); population near exposed sites; dispersed-asset descriptive state shares; and the reason a firm is not scored. Future water stress is not aggregated to firms |
| `data/processed/hazard_map.html` | Leaflet map of the scored sites and their main buffers, coloured by river-flood and heat exposure; the popups give all four hazards |
| `data/interim/phase3_flood.csv`, `phase3_flood_permwater.csv`, `phase3_heat_era5.csv` (ERA5, main), `phase3_heat.csv` (NASA POWER, robustness), `phase3_coastal.csv`, `phase3_water.csv`, `phase3_water_future.csv` (descriptive), `phase3_pop.csv`, `phase3_states.csv` | Intermediate tables |
| `docs/nasa_manual_download.md` | The 33 NASA POWER cells listed for the owner's manual download (29 downloaded) |
| `src/phase3_download.py`, `phase3_era5_ts.py`, `phase3_era5.py`, `phase3_heat.py`, `phase3_hazards.py`, `phase3_firms.py`, `phase3_map.py` | Code. Run order: `phase3_download.py jrc` and `worldpop`; `phase3_era5_ts.py download all` (ERA5 point files, A11) and `phase3_era5.py score` (ERA5 heat, main); `phase3_heat.py compare` (manual vs API files) and `score manual` (NASA POWER, robustness); `phase2_osm_extract.py geoms …`; `phase3_hazards.py flood`, `states`, `pop`, `permwater`, `coastal`, `water` and `water_future`; `phase3_firms.py`; `phase3_map.py`. `phase3_heat.py fetch` is disabled |

## 1. Methods

### 1.1 Site sets

- **Main:** grade A and B point sites with a coordinate, located from the reports, that are not offices. Design d lists point sites as "plants, breweries, factories, mills, terminals, flow stations, platforms, distribution centres, data centres and plantation estates"; offices are not on that list. 71 sites: 26 grade A and 45 grade B.
- **Office:** 51 registered or head offices with a coordinate. They are scored but enter no firm score.
- **R2 (robustness):** 3 grade-D sites whose only location is OSM: Okomu's rubber factory, International Breweries' breweries and Cadbury's factory.
- **Not scored:** grade C point sites (no coordinate; state-level measure in section 3.4), grade D sites without a coordinate, and the 13 grade-A sites labelled "no coordinate" under A6. They are reported as a limitation.

### 1.2 Buffers (river and coastal flood; e5, A6, A7)

| Grade | Main | Robustness | Sites (main set) |
|---|---|---|---|
| A, A6 "correct" | 500 m circle | 500 m (A7) | 4 |
| A, A6 "approximate" | A circle with the site's nominal precision: 2, 5 or 10 km | 500 m (A7) | 22 |
| B, located from an OSM way or relation | The OSM polygon plus 250 m (e5) | The same | 6 (Dangote Obajana, Gboko and Ibese; Okomu main estate; Qua Iboe terminal; Transcorp Hilton) |
| B, other | 2 km circle (OD-2) | 5 km circle (OD-2) | 39 |
| R2 (OSM-sourced, grade D) | The OSM polygon plus 250 m | The same | 3 |

Circles and polygon buffers are built in a local metric frame around each site (an equirectangular approximation; error under 1% at these distances). Heat and water stress use no buffer (e3, e4).

### 1.3 River flood (e1, OD-3, A8)

- **Data:** JRC v2.1.2 raw depth tiles (`*_depth.tif`), 3 arc seconds; the four tiles that cover Nigeria.
- **Cells:** every cell whose centre falls inside the buffer is read. Nodata cells (-9999) count as dry.
- **Exposure (main):** a site is exposed if any cell has RP100 depth > 0 m. The smallest wet value in the tiles is 0.1 m.
- **Continuous scores:** the share of the buffer's cells with depth > 0 m, and the maximum depth in the buffer.
- **Robustness:** RP10; RP500; RP100 with depth ≥ 0.5 m (the OD-3 check); the robustness buffers (A7 and OD-2 separately); and **A8**.
- **A8 (permanent water excluded):** the JRC permanent-water tiles are on the same grid as the depth tiles; 1 = permanent water, 255 = nodata. Cells with value 1 are removed from both the flooded count and the buffer total before the share and the exposure flag are computed.

### 1.4 Heat (e3, OD-5, OD-6, OD-7; A10, A11)

**Main: ERA5 (A10 method, A11 data source).**

- **Data:** ERA5 hourly 2 m temperature, 1991-01-01 to 2025-12-31 (UTC), from the CDS dataset `reanalysis-era5-single-levels-timeseries`: one point series per ERA5 0.25° grid point, requested at the exact grid-point coordinates (`data/raw/hazards/era5_timeseries/`; SHA-256 in `docs/data_sources.md`). Each of the 43 files has 306,816 hourly values and no gaps.
- **Cell of a site (A10):** the nearest 0.25° grid point (cell = point ± 0.125°; exact edges go north/east). The 125 sites fall in 43 cells; the 71 main sites in 37.
- **Daily maximum:** hourly values shifted to UTC+01:00 (West Africa Time) and the maximum taken per local calendar day: 12,784 days per cell, none missing (local 1991-01-01 has 23 hours). A11 validated this against the A10 daily-statistics files for one cell (6.50 N, 3.25 E): maximum absolute difference 0.0003 °C in 1991 and 2025.
- **Metric (unchanged):** per cell, the 90th percentile of all daily maxima 1991–2020 pooled; each year's count is the days above it. **Score** = mean count 2020–2025 minus mean count 1991–2020, in days per year. Because the percentile is pooled over the base period, the base mean is about 36.5 days/yr in every cell (36.50–36.53).
- **Exposure:** the top tercile of the 71 main-set sites (OD-5), score ≥ the 2/3 quantile. **The cut-off is 58.80 days per year**; 25 of 71 main sites are exposed (two sites score exactly 58.80, so the tercile holds 25, not 24).
- **Check of the series:** yearly exceedance counts and annual mean daily maxima were inspected in four cells (Lagos 6.50/3.25, Port Harcourt 4.75/7.00, Enugu area 6.50/7.50, Kano area 12.00/8.50). The increase is gradual over 1991–2025 with no step change; Lagos' annual mean daily maximum rises from about 28.6 °C in the early 1990s to 29.3–30.0 °C in 2020–2025.

**Robustness: NASA POWER (the earlier main source).**

- **Data:** NASA POWER daily T2M_MAX for 1991–2025 (source MERRA-2), from the owner's POWER Data Access Viewer downloads of 2026-11-12: one file per 0.5° bin, at the bin centre, for the 29 bins that contain main-analysis sites (`data/raw/hazards/nasa_power_manual/`; SHA-256 in `docs/data_sources.md`). All 2020–2025 years are complete, with no missing days.
- **Check against the API files:** `phase3_heat.py compare` found every one of the 29 manual files identical to the earlier API file for the same bin: 12,784 days each, **maximum absolute daily difference 0.0 °C in every bin**. The scores are therefore unchanged.
- **Cells not downloaded (owner decision):** the 4 bins with no main-analysis site (5.25/7.75, 5.75/7.25, 6.25/7.75, 7.75/4.75). Their sites are marked "not scored — no owner download"; the API files are **not** used for them. Three are offices (Champion and Golden Guinea registered offices; NB Enugu sales office). The fourth, bin 7.75/4.75, holds International Breweries' Ilesa brewery, which is an OSM-sourced **R2** site, not an office; its label says so. Neither set enters the heat tercile or any firm score, so firm results do not change.
- **Metric:** for each cell, the 90th percentile of daily T2M_MAX over 1991–2020, pooling all days, which is what the design wording says. Each year's count is the number of days above that percentile.
  - **Score:** the mean count for 2020–2025 minus the mean for 1991–2020, in days per year.
- **Exposure:** the top tercile of the 71 main-set sites on the NASA POWER score, with its own cut-off (OD-5 applied to this source). **The cut-off is 16.06 days per year.** 24 of 71 main sites are exposed. These are the `heat_nasa_*` columns.
- **No fixed heat-index threshold** (OD-6) for either source. ERA5 replaced NASA POWER as the main source under OD-7 (A10).

#### Grid note: the native grid is 0.5° × 0.625°, not the assumed 0.5° × 0.5°

Every manual file's header says the data are "NASA/POWER Source Native Resolution" and gives the MERRA-2 elevation as an "Average for 0.5 x 0.625 degree lat/lon region". The bins were built on the POWER API page's statement of a "0.5° x 0.5° global grid", with cell edges assumed at multiples of 0.5°. **The bin mapping does need a note:**

- **Evidence in the data.** Two pairs of requests 0.5° apart in longitude returned identical series: 5.25 N at 7.25 E and 7.75 E, and 6.25 N at 7.25 E and 7.75 E. Both longitudes fall in one 0.625°-wide MERRA-2 column (centre 7.5°, edges 7.1875–7.8125°). All other neighbouring requests differ, including the owner's typo file at 6.75 N 7.00 E versus 6.75 N 7.25 E (different columns; different header elevations, 140.4 m and 220.4 m).
- **Grid alignment used below.** MERRA-2 cell centres at multiples of 0.5° in latitude and at −180° + k × 0.625° in longitude. This is the published MERRA-2 grid definition, not something read from these files; the longitude evidence above is consistent with it.
- **Latitude: every request sits on a cell edge.** The bin centres (x.25° and x.75°) are exactly the MERRA-2 latitude edges. Which neighbour POWER returns at an edge is not stated in what was read, and the files cannot show it (every pair of requests 0.5° apart in latitude differs, which both tie rules predict).
- **Longitude: 13 of 71 main sites are in a different MERRA-2 column from their bin's request point.** Port Harcourt area at about 7.02 E (7 sites, among them BUA Foods ×4, Aradel, Transcorp hotel, ABC Eliozu), Onne (Dangote Cement), Ellah Lakes' Adani farm, Alex's Suleja plant, Ughelli (Beta Glass, Transcorp Power), LASUCO (BUA Foods) and Numan (Dangote Sugar).
- **Combined:** the series used comes from the MERRA-2 cell that contains the site for **26 of 71 main sites if POWER resolves edge ties northwards, or 32 of 71 if southwards**. For the rest it comes from an adjacent MERRA-2 cell (one cell away in latitude, longitude or both).
- **Lagos:** 18 main Lagos-area sites lie in one MERRA-2 cell (centre 6.5 N, 3.125 E), but the 0.5° bins split them between the 6.25 N and 6.75 N requests, which return different series. At most one of those two requests can be that cell.
- **Not changed.** The NASA POWER robustness scores follow the bin mapping as downloaded. The re-download at native cell centres (A9) was superseded by A10 and never done, so this grid caveat applies to the robustness scores only.

### 1.5 Coastal flood (e2, OD-3, OD-4)

- **Data:** Aqueduct Floods v2.0, `inuncoast_historical_nosub_hist_rp0100_0.tif`: baseline, no subsidence, RP100.
- **Resolution:** 30 arc seconds, about 922 m (now verified). That is not coarser than about 1 km, so coastal flood is scored in the main analysis for every grade-A and B point site (e2). There is no separate coastal zone (OD-4): inland sites score zero.
- **Cells:** the cells are larger than many buffers, so every cell touching the main buffer counts (rasterio `all_touched`). Nodata counts as dry. This is an implementation choice.
- **Exposure:** a site is exposed if any such cell has depth > 0 m. The OD-3 robustness check uses ≥ 0.5 m. The share of touching cells and the maximum depth are also reported.

### 1.6 Water stress (e4)

- **Data:** Aqueduct 4.0 `baseline_annual` layer. Each site takes the polygon that contains its point (no buffer). Every scored site falls in exactly one polygon.
- **Exposure:** the dataset's two highest categories: `bws_cat` 3, "High (40-80%)", and 4, "Extremely High (>80%)". The labels and cut-offs were read from the data (see `docs/data_sources.md`).
- **"Arid and Low Water Use"** (`bws_cat` -1) is not one of the 0–4 ordered categories, so it does not count as exposed. No site falls in it.
- **Future projections (descriptive only):** 2030 and 2050 under the business-as-usual scenario (design e4), from the `future_annual` layer of the same file: fields `bau30_ws_x_r/_c/_l` and `bau50_ws_x_r/_c/_l` (water stress, raw value, category, label). Each site takes the row for the HydroBASINS level-6 `pfaf_id` of its baseline polygon; all 125 sites match. **They are not used in the exposure index, any firm measure or any hypothesis** (design: "Future scenarios are reported descriptively only"). Results are in section 3.6.

### 1.7 Firm scores (e6, OD-8)

- **Measures:** for each hazard, over a firm's main-analysis sites: `E_share` (main measure) = share of sites exposed; `E_any`; and `E_max` = the largest continuous score. The continuous score is the flooded share of the buffer for river and coastal flood, the heat score for heat, and `bws_raw` for water stress.
- **Weights:** none.
- **Combined index (secondary, OD-8)** = the mean of the four hazard-specific `E_share` values. The river-flood-plus-heat mean is also kept (`combined_index_primary2`). Heat comes from ERA5 (A10/A11); the index with NASA POWER heat is `rob_nasa_heat_combined_index`.
- **Dispersed assets:** descriptive only, with no scoring rule (owner decision, 2026-11-12).

### 1.8 Population (OD-16)

- **Per site:** WorldPop people within the main buffer and within 5 km.
- **Per firm:** the same two figures for the firm's exposed sites, computed on the union of their circles, so overlapping buffers are not double counted. Versions are computed for river flood, heat, either of those two, coastal flood and water stress.

## 2. Counts

**Main sites** (71) exposed, by grade:

| Hazard | Grade A (26) | Grade B (45) | **All 71** |
|---|---|---|---|
| River flood RP100 (main) | 18 | 25 | **43** |
| River flood RP100, permanent water excluded (A8) | 12 | 18 | 30 |
| River flood RP10 | 18 | 22 | 40 |
| River flood RP500 | 19 | 25 | 44 |
| River flood RP100, depth ≥ 0.5 m | 18 | 23 | 41 |
| River flood, A7 500 m (grade A) / OD-2 5 km (grade-B circles) | 9 | 37 | |
| Heat, top tercile (ERA5, main) | 12 | 13 | **25** |
| Heat, top tercile (NASA POWER, robustness) | 9 | 15 | 24 |
| Coastal flood RP100 | 3 | 2 | **5** |
| Water stress, High or Extremely High | 9 | 9 | **18** |

- **Coastal flood:** the 5 exposed main sites are all in Port Harcourt: BUA Foods' industrial complex, sugar refinery and flour mill (maximum depth 3.35 m), Aradel's Ever Oil depot and Transcorp's Port Harcourt hotel (0.55 m). All 5 are also river-flood exposed. No Lagos main site is exposed in the coastal layer.
- **Water stress:** the 18 exposed main sites are in Lagos (13), Kano (4) and Sokoto (1). Of the 71 main sites, 52 are "Low (<10%)", 1 "Low - Medium", 13 "High" and 5 "Extremely High".
- **Permanent water:** 39 of the 71 main buffers contain JRC permanent-water cells. Excluding them removes river-flood exposure from 13 main sites, among them Gboko, the Aba plants (Guinness, NB ×2, Vitafoam, Livestock), the Ughelli plants (Beta Glass, Transcorp Power), Cutix (Nnewi), NNFM (Kano) and Afam Power.
- **Offices** (51; descriptive): river flood 43, coastal flood 13, water stress 33, heat (ERA5) 42. Under NASA POWER, 2 of the 48 scored offices are heat-exposed; 3 offices are not scored (cells not downloaded). The ERA5 office count is high because most offices are in Lagos, whose cells are in the ERA5 top tercile.
- **R2 sites:** none of the 3 is exposed to river flood. Heat (ERA5): 2 of 3 exposed (International Breweries' Ilesa brewery and the third R2 factory; not the rubber factory). Under NASA POWER, 2 are scored and neither is exposed; the Ilesa brewery is not scored.

**Firms:**

| | Firms |
|---|---|
| Census firms that passed the document test | 59 (56 main census, 3 robustness stratum) |
| Scored (at least one main site) | **29** (27 main, 2 robustness) |
| Not scored: no main-analysis point site with a coordinate | 30 |

| Hazard | `E_any` = 1 | `E_share` = 1 |
|---|---|---|
| River flood | 23 | 12 |
| Heat (ERA5, main) | 16 | 4 |
| Heat (NASA POWER, robustness) | 15 | 4 |
| Coastal flood | 3 (Aradel, BUA Foods, Transcorp) | 1 |
| Water stress | 14 | 3 |

## 3. Distributions

### 3.1 Sites (main set, 71)

| Measure | Min | Q1 | Median | Q3 | Max |
|---|---|---|---|---|---|
| RP100 share of buffer flooded | 0.000 | 0.000 | 0.004 | 0.221 | 0.775 |
| RP100 share flooded, permanent water excluded (A8) | | | 0.000 | 0.155 | 0.718 |
| RP100 maximum depth in buffer (m) | | | 1.00 | 5.08 | 11.02 (2 sites > 10 m) |
| Heat score, ERA5 (days/yr, 2020–2025 vs 1991–2020) | −2.87 | 35.47 | 49.47 | 64.55 | 66.80 |
| Heat score, NASA POWER (robustness) | −9.23 | 7.03 | 11.67 | 37.07 | 94.77 |

Coastal cells touching a main buffer: usually 23–25 for 2 km circles; 4 for 500 m circles.

### 3.2 Firms (29 scored)

| Firm measure | Mean | Firms > 0 | Firms = 1 |
|---|---|---|---|
| River flood `E_share` (main) | 0.615 | 23 | 12 |
| Heat `E_share` (ERA5) | 0.329 | 16 | 4 |
| Heat `E_share` (NASA POWER, robustness) | 0.297 | 15 | 4 |
| Coastal flood `E_share` | 0.061 | 3 | 1 |
| Water stress `E_share` | 0.247 | 14 | 3 |
| **Combined index, four hazards (OD-8)** | **0.313** (median 0.250, range 0.000–0.750) | 26 | 0 |
| Combined index with NASA POWER heat (robustness) | 0.305 (median 0.300) | 26 | 0 |
| River flood + heat index | 0.472 | 25 | 2 |

### 3.3 Robustness comparison (firm river-flood `E_share`, 29 firms)

| Version | Mean | Firms > 0 | Firms = 1 |
|---|---|---|---|
| **Main (A6 / OD-2 buffers, RP100, > 0 m)** | **0.615** | **23** | **12** |
| **A8: permanent water excluded** | 0.408 | 18 | 7 |
| **A7: grade-A sites at 500 m** (owner robustness check) | 0.471 | 20 | 8 |
| OD-2: grade-B circles at 5 km | 0.767 | 25 | 19 |
| Both robustness buffers | 0.623 | 22 | 14 |
| RP10 | 0.546 | 21 | 10 |
| RP500 | 0.650 | 24 | 13 |
| RP100, depth ≥ 0.5 m | 0.564 | 22 | 10 |
| R2 (adds OSM-sourced sites) | 0.598 | 23 | 11 |

**A8 changes 11 firms' river-flood `E_share`.** Five lose all river-flood exposure: Cutix, Livestock, NNFM, Transcorp Power and Vitafoam.

| Firm | Main | Permanent water excluded |
|---|---|---|
| ABCTRANS | 1.0 | 0.333 |
| BETAGLAS | 1.0 | 0.5 |
| CUTIX | 1.0 | 0.0 |
| DANGCEM | 0.6 | 0.4 |
| GUINNESS | 0.667 | 0.333 |
| LIVESTOCK | 0.5 | 0.0 |
| NB | 0.556 | 0.333 |
| NNFM | 1.0 | 0.0 |
| TRANSCORP | 0.667 | 0.333 |
| TRANSPOWER | 1.0 | 0.0 |
| VITAFOAM | 0.25 | 0.0 |

**A7 changes 7 firms' river-flood `E_share`.** Three lose all river-flood exposure: Cutix, NNFM and Transcorp Power.

| Firm | Main | A7 (500 m) |
|---|---|---|
| ABCTRANS | 1.0 | 0.667 |
| BUAFOODS | 0.857 | 0.571 |
| CUTIX | 1.0 | 0.0 |
| GUINNESS | 0.667 | 0.333 |
| NB | 0.556 | 0.333 |
| NNFM | 1.0 | 0.0 |
| TRANSPOWER | 1.0 | 0.0 |

**Coastal flood at depth ≥ 0.5 m** gives the same result as the main coastal measure: mean `E_share` 0.061, with the same 3 firms.

### 3.4 State-level measures (descriptive only)

- **Data:** the share of each state's area with RP100 depth > 0 m, for 36 of 37 states (`data/interim/phase3_states.csv`). Taraba's OSM boundary could not be assembled.
- **Range:** from 0.9% (Ekiti) to 79.9% (Bayelsa).
- **Grade-C point sites (robustness R1, e5):** only those whose state is written in the report have a value:

  | Site | State | Flooded area share |
  |---|---|---|
  | Dangote Sugar, Nasarawa estate | Nasarawa | 0.068 |
  | Dangote Sugar, Adamawa estate | Adamawa | 0.053 |
  | Ellah Lakes, Ondo land | Ondo | 0.133 |
  | Eterna, JUHI-2 tank farm | Lagos | 0.236 |
  | Dangote Sugar, Taraba estate | Taraba | No value (boundary not assembled) |

  Okomu's Extension 2 and Presco's six estates have no state in the report text, so they are not scored.
- **Dispersed assets: descriptive only** (owner decision, 2026-11-12: no scoring rule, no amendment). Only Conoil's (9 states) and TotalEnergies' (35 states) station networks have state lists. Their states' flooded-area shares are in `firm_exposure.csv`.

### 3.5 Heat: ERA5 (main) versus NASA POWER (robustness)

| | ERA5 (main; A10/A11) | NASA POWER (robustness) |
|---|---|---|
| Grid | 0.25°; 37 cells for the 71 main sites | 0.5° bins (MERRA-2 0.5° × 0.625° underneath; see 1.4); 29 bins for the 71 main sites |
| Sites scored | 125 | 121 (4 in cells not downloaded) |
| Main-site score, median (range) | 49.47 (−2.87 to 66.80) | 11.67 (−9.23 to 94.77) |
| **Tercile cut-off** (2/3 quantile of 71 main scores) | **58.80 days/yr** | **16.06 days/yr** |
| Main sites exposed | 25 (12 grade A, 13 grade B) | 24 (9 grade A, 15 grade B) |
| Where the exposed main sites are | Lagos 13, Ogun 10, Oyo 1, Akwa Ibom 1 | Rivers 8, Abia 5, Anambra 3, Benue 2, Enugu 2, Cross River 1, Akwa Ibom 1, Adamawa 1, Kwara 1 |

**Sites (71 main).**

| | NASA POWER not exposed | NASA POWER exposed | Total |
|---|---|---|---|
| ERA5 not exposed | 23 | 23 | 46 |
| ERA5 exposed | 24 | 1 | 25 |
| Total | 47 | 24 | 71 |

- **47 of 71 main sites change heat exposure** between the two sources: 24 are exposed only under ERA5 (all in Lagos, Ogun and Oyo) and 23 only under NASA POWER (Port Harcourt area, Aba, Onitsha, Enugu, Benue, Numan, LASUCO and others). Only Seplat's Qua Iboe Terminal (Akwa Ibom) is exposed under both.
- **Correlation of site scores:** main sites (n = 71): Pearson 0.09, Spearman −0.01. All sites scored by both (n = 121): Pearson −0.02, Spearman 0.05. The two scores are essentially unrelated across sites.
- **Near the ERA5 cut-off:** the Port Harcourt cells score 53.63–53.80 days/yr under ERA5, below the 58.80 cut; the exposed Lagos, Ogun and Oyo cells score 58.80–66.80. All 8 Rivers main sites (Port Harcourt area, Onne, Afam) are exposed under NASA POWER but not ERA5.
- **Offices** (descriptive): 42 of 51 exposed under ERA5, against 2 of 48 scored under NASA POWER.

**Firms (29 scored).**

- **Heat `E_share` differs for 16 of 29 firms**; heat `E_any` differs for 11. Correlation of firm heat `E_share` between the sources: Pearson −0.30.
- **Heat-exposed (`E_any` = 1) under ERA5 only (6):** Academy Press, Beta Glass, Fidson, Neimeth, Nestlé, Unilever. **Under NASA POWER only (5):** Aradel, Cutix, Dangote Sugar, Ellah Lakes, Transcorp.
- **Combined index (four hazards):** differs for 16 firms; mean 0.313 with ERA5 heat, 0.305 with NASA POWER heat.

**Reading this comparison.** The tercile rule ranks sites within each source, so the gap in absolute scores (ERA5 scores are larger) does not by itself change exposure; the change comes from the two sources ranking regions differently. Known differences: grid size (0.25° against 0.5° bins), the NASA POWER bin-to-cell mismatch (1.4), and the different reanalyses (ERA5 against MERRA-2). This is a comparison of exposure inputs only; no disclosure measure was used or computed.

**Why the sources differ (diagnostic, not used).** Computed on 2026-11-17 from the files already on disk. Nothing below changes any score, method, exposure column or `config/parameters.json`. Cells: the five ERA5 cells with the most main sites, plus Ogun 6.50/3.00, which ties for fifth place with FCT. Each ERA5 cell is set against the NASA POWER bin(s) used for the same main sites. The trend is an OLS slope of the annual mean daily maximum, 1991–2025. Sea share is the part of the ERA5 cell (± 0.125°) outside the OSM state polygons (`data/interim/osm_states.geojson`), which end at the coastline. Lagoon/estuary share is JRC permanent water (value 1) inside them. ERA5's own land-sea mask is not on disk and was not checked.

| ERA5 cell (main sites) | Source and grid point | p90 1991–2020 (°C) | Exceedance days/yr, 2020–2025 | Trend (°C/decade) | ERA5 cell: sea / lagoon or estuary |
|---|---|---|---|---|---|
| Lagos 6.50/3.25 (13) | ERA5 6.50/3.25 | 30.89 | 102.2 | +0.28 | 9.6% / 4.9% |
| | NASA 6.25/3.25 (5 sites) | 30.38 | 48.8 | +0.05 | |
| | NASA 6.75/3.25 (8 sites) | 31.77 | 43.3 | +0.00 | |
| Port Harcourt 4.75/7.00 (6) | ERA5 4.75/7.00 | 32.42 | 90.3 | +0.42 | 0% / 46.0% |
| | NASA 4.75/7.25 | 31.62 | 73.5 | +0.28 | |
| Aba 5.00/7.25 (5) | ERA5 5.00/7.25 | 33.56 | 83.5 | +0.44 | 0% / 1.5% |
| | NASA 5.25/7.25 | 31.12 | 81.3 | +0.29 | |
| Kano 12.00/8.50 (4) | ERA5 12.00/8.50 | 38.43 | 51.8 | +0.32 | 0% / 0.5% |
| | NASA 11.75/8.75 | 39.82 | 48.2 | +0.38 | |
| FCT 9.00/7.50 (3) | ERA5 9.00/7.50 | 35.86 | 52.7 | +0.33 | 0% / 0.3% |
| | NASA 9.25/7.25 | 36.11 | 32.8 | +0.51 | |
| Ogun 6.50/3.00 (3) | ERA5 6.50/3.00 | 30.93 | 103.3 | +0.29 | 8.1% / 6.6% |
| | NASA 6.75/3.25 | 31.77 | 43.3 | +0.00 | |

The 1991–2020 exceedance mean is about 36.5 days/yr in every row, by construction of the pooled percentile.

- **Lagos and Ogun drive the disagreement.** NASA POWER's two Lagos-area bins show almost no warming in mean daily maximum over 1991–2025 (+0.00 to +0.05 °C/decade); ERA5's Lagos and Ogun cells warm by about +0.28. This explains most of the gap in 2020–2025 exceedances: 43–49 days/yr under NASA POWER against 102–103 under ERA5.
- **Spread of daily maxima.** In both sources, the coastal south has a narrow 1991–2020 distribution of daily maxima: the 90th percentile is about 1.8–3.1 °C above the mean (standard deviation about 1.4–2.4 °C). In Kano and FCT the gap is 4.4–5.5 °C (standard deviation about 3.4–3.8 °C). With a narrow distribution, a small warming adds many exceedance days. So ERA5's modest Lagos warming puts its south-western cells at the top of the ranking, and the inland cells score low under both sources despite similar or larger trends. The spreads are similar between the sources for the same place, so they do not explain the disagreement. The trends do.
- **Port Harcourt and Aba** warm in both sources (ERA5 +0.42 to +0.44, NASA +0.28 to +0.29). Under NASA POWER they top the ranking because Lagos is flat. Under ERA5 they rank below Lagos/Ogun, whose distribution is narrower (standard deviation 1.6 °C against 2.0–2.4 °C).
- **Coastal cells.** The ERA5 Lagos and Ogun cells are partly sea (9.6% and 8.1%) and partly lagoon (4.9% and 6.6%). The Port Harcourt cell has no open sea but 46% estuary and creek water (JRC permanent water). Whether ERA5's land-sea mask treats these fractions as water, and whether that affects the trend, was not checked. The NASA POWER bins' sea share was not computed.
- **Not established:** which source is closer to station observations. No station data were used.

### 3.6 Water-stress projections, 2030 and 2050 (descriptive only)

**Descriptive only.** These columns are not used in the water-stress exposure measure, the combined index, any firm measure or any hypothesis. They are reported because the design (e4) asks for future scenarios to be described.

- **Data:** Aqueduct 4.0 `future_annual`, business-as-usual scenario, water stress (`bau30_ws_x_*`, `bau50_ws_x_*`). The README describes 2030 as the period 2015–2045 and 2050 as 2035–2065, each the median of 5 global climate models. The SSP/RCP behind "business-as-usual" is not stated in the README and was not verified.
- **Not directly comparable with the baseline.** The baseline is `bws` on a finer polygon (basin × province × aquifer); the projection is `ws` at HydroBASINS level 6 and comes from a different model run. Raw values differ in scale: for Lagos, `bws_raw` 0.75 at baseline against `ws` raw 2.02 in 2030.
- **Main sites (71) by category:**

  | Category | Baseline (`bws`) | 2030 BAU (`ws`) | 2050 BAU (`ws`) |
  |---|---|---|---|
  | Low (<10%) | 52 | 45 | 41 |
  | Low-medium (10–20%) | 1 | 8 | 4 |
  | Medium-high (20–40%) | 0 | 0 | 1 |
  | High (40–80%) | 13 | 1 | 7 |
  | Extremely high (>80%) | 5 | 17 | 18 |
  | High or Extremely high | 18 | 18 | 25 |

- **Sites in the two highest categories in 2050 but not at baseline (7):** six Ogun sites (Dangote Cement Ibese; Beta Glass, Nestlé and Unilever at Agbara; NB Ota; Fidson) and BUA Cement's Sokoto plant. Lagos and Kano sites are in the two highest categories in all three columns.

## 4. Population near exposed sites

WorldPop R2025A, 2025, 100 m, constrained. Each figure is the population inside a circle or buffer, so it includes everyone living near a site, not only workers.

- **Per main site** (71 sites):

  | Area | Min | Median | Max |
  |---|---|---|---|
  | Within 5 km | 3,053 | 524,909 | 1,353,399 |
  | Within the main buffer | 1,000 | 116,212 | 4,542,083 |

  The main-buffer figure exceeds the 5 km figure where an A6 "approximate" site has a 10 km city-centroid circle.
- **Per firm** (29 scored), the population within 5 km of the firm's exposed sites, taken as the union of circles with no double counting within a firm:

  | Sites exposed to | Firms with any | Median (firms with any) | Max |
  |---|---|---|---|
  | River flood | 23 | 728,473 | 3,499,756 |
  | Heat (ERA5) | 16 | 1,187,277 | 3,402,246 |
  | Either | 25 | 944,090 | 5,075,682 |

- **Largest (either hazard):** Nigerian Breweries 5.08 m, ABC Transport 3.50 m, BUA Foods 2.71 m, Guinness 2.35 m, Livestock Feeds 1.80 m.
- **Heat source:** these figures use ERA5 heat exposure. They are higher than the NASA POWER version (heat: 15 firms, median 613,334) because the ERA5 heat-exposed sites are mostly in Lagos and Ogun, which are densely populated. Population figures are not computed for NASA POWER heat.
- **Sums across firms are not reported:** circles of different firms overlap (for example in Lagos), so a sum would double count people.
- **Coastal flood and water stress:** the same union figures are in `firm_exposure.csv` (`pop5km_exposed_coastal`, `pop5km_exposed_water`).
- **Workers:** employee numbers by site were not compiled in this phase. They are a report-text item for Phase 4.

## 5. Missing data

| Item | Count | Reason |
|---|---|---|
| Heat (ERA5, main) | 0 | All 125 sites scored |
| Heat (NASA POWER, robustness) | 4 sites (3 offices, 1 R2) | In the 4 cells with no main-analysis site, which the owner did not download |
| Grade-A sites with no coordinate (A6) | 13 (4 operational) | No OSM match, or the coordinate was withdrawn |
| Grade-B point sites with no coordinate | 14 | No OSM match |
| Grade-C point sites with no state in the report | 7 | Okomu Extension 2 and Presco's 6 estates |
| Grade-D point sites | 31 without a coordinate | Location not stated |
| Dispersed assets | 19 | Descriptive only (owner decision); 17 have no state list |
| Firms not scored | 30 of 59 | No main-analysis point site with a coordinate |

## 6. Limitations

- **Location accuracy.** "Location accuracy was assessed by a documented rule-based cross-check rather than manual visual inspection" (A6). 22 of 26 main grade-A sites are only town or suburb centroids.
- **Buffer size and permanent water drive river-flood exposure.** With 2–10 km circles, almost any site near a river is "exposed".
  - **Permanent water (A8):** 39 of 71 main buffers contain permanent water. Excluding it cuts firm river-flood `E_share` from 0.615 to 0.408 on average, and 5 firms lose all exposure.
  - **Grade-A buffers (A7):** at 500 m, the average falls to 0.471.
  - **Grade-B buffers (OD-2):** at 5 km, results move the other way.
- **Spurious depths.** The JRC `Spurious_Depths` tiles are not used. Two sites have maximum depths over 10 m, which the README warns may be model artefacts.
- **Coastal resolution.** The coastal layer is about 922 m, so a 500 m buffer touches about 4 cells. Counting touching cells makes coastal exposure generous for small buffers.
- **Coastal model.** The layer was "simulated without considering the presence of flood protection" (WRI), and no coastal subsidence scenario is used ("nosub").
- **Water stress.** The value is at sub-basin level, so one polygon covers many sites; all 13 Lagos main sites share one category. Exposure is a property of the basin, not of the site's own water use.
- **Heat:**
  - **Source sensitivity (section 3.5):** ERA5 (main) and NASA POWER (robustness) give almost unrelated site rankings (Spearman −0.01 over 71 main sites), and 47 of 71 main sites change heat exposure between them. Heat exposure therefore depends strongly on the reanalysis used.
  - **Why the sources differ (diagnostic, not used; section 3.5):** NASA POWER shows almost no 1991–2025 warming in mean daily maximum at its Lagos-area bins (+0.00 to +0.05 °C/decade), while ERA5 shows about +0.28 °C/decade there. Combined with the narrow spread of daily maxima on the coast, this puts Lagos and Ogun at the top under ERA5 and Port Harcourt and Aba at the top under NASA POWER. The ERA5 Lagos and Ogun cells are partly sea (about 8–10%) and lagoon (5–7%); the Port Harcourt cell is 46% estuary and creek water. ERA5's land-sea mask and station observations were not checked, so which source is more accurate is not established.
  - **ERA5 clustering:** the middle half of main-site ERA5 scores lies between 35 and 65 days/yr; the cut-off (58.80) separates Lagos/Ogun from Port Harcourt (53.6–53.8) by about 5 days/yr. Shared cells also produce ties (two sites at exactly the cut-off).
  - **ERA5 daily maximum** is the maximum of hourly values, not ERA5's separate "maximum temperature since previous post-processing" field, so it can sit slightly below the true peak (A10). The pooled-percentile metric absorbs a constant offset.
  - **NASA POWER grid mismatch (robustness only; section 1.4):** the native grid is MERRA-2 at 0.5° × 0.625° (file headers), not the 0.5° × 0.5° grid the bins assume. Every request latitude lies on a MERRA-2 cell edge, and the series used comes from the cell containing the site for only 26–32 of 71 main sites; the rest take an adjacent cell.
  - **Shared cells:** sites in the same cell share one score. Under ERA5, 38 sites (all sets) share the Lagos cell 6.50/3.25; under NASA POWER, 14 Lagos-area sites share one bin, and two pairs of neighbouring 0.5° bins returned identical series.
  - **Percentile definition:** the 90th percentile pools all 1991–2020 days, as the design states. ETCCDI's TX90p (Zhang et al. 2011) uses calendar-day percentiles; the two can differ where seasonality is strong.
- **Population data.** WorldPop R2025A is labelled an alpha release.
- **JRC licence.** The README (ODbL v1.0) and `copyright.txt` (CC BY 4.0) differ; both require attribution.

## 7. Still to do or decide

1. **Heat grid: resolved.** A9 (MERRA-2 native cells) was superseded by A10 before it was applied; heat main is ERA5 (A10 method, A11 data source), scored 2026-11-17. The NASA POWER 0.5° bin scores remain as robustness.
2. **Water-stress future scenarios: done** (2030 and 2050, business-as-usual; descriptive only, section 3.6).
3. **For the owner:** the strong disagreement between ERA5 and NASA POWER heat (section 3.5). No method change is proposed here; any change would need an amendment.
