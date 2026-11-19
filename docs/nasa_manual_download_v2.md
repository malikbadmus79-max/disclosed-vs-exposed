# NASA POWER: manual download list, version 2 (A9, MERRA-2 native cells)

**Why.** Amendment A9 (`docs/amendments.md`, owner decision 2026-11-12): each site's heat series comes from the MERRA-2 native grid cell that contains it. The first download used 0.5° × 0.5° bins whose centres fall exactly on native cell edges (`docs/phase3_hazards.md`, section 1.4). This list replaces `docs/nasa_manual_download.md` for heat scoring.

## Settings (same as before)

In the **POWER Data Access Viewer** (https://power.larc.nasa.gov/data-access-viewer/), make one download per row below:

- **Data type:** Single Point
- **Community:** Agroclimatology
- **Temporal average:** Daily
- **Latitude / longitude:** the **bold** cell centre, typed exactly as shown, in decimal degrees (north and east are positive). Several longitudes have three decimals (for example 3.125). Please type all three.
- **Time extent:** 1991-01-01 to 2025-12-31
- **Parameter:** Temperature at 2 Meters Maximum (**T2M_MAX**)
- **Format:** CSV

Leave the files in your Downloads folder with NASA's names, as before, or save them in `data/raw/hazards/nasa_power_manual_v2/`. I will copy and rename them to the cell name (`m2_<i>_<j>.csv`) and check that the location in each file header is the cell centre.

## Grid

- **MERRA-2 native grid:** 0.5° latitude × 0.625° longitude (the "0.5 x 0.625 degree" region in the POWER file headers).
- **Cell centres:** latitude −90 + 0.5 × i (every multiple of 0.5°) and longitude −180 + 0.625 × j (…, 3.125, 3.75, 4.375, 5.0, 5.625, 6.25, 6.875, 7.5, 8.125, 8.75, …). This alignment is MERRA-2's published grid definition. It is consistent with the identical series seen in the first download, but was not read from the files.
- **A cell** covers latitude centre ± 0.25° and longitude centre ± 0.3125°. A centre is 0.25° from the nearest latitude edge, so the request is never on an edge.
- **Sites:** all 125 point sites with a coordinate (71 main, 51 office, 3 R2) were assigned (`data/interim/phase3_heat_cells_v2.csv`). None lies exactly on a cell edge. They fall in 34 native cells.

## What to download: 29 cells

Every native cell that contains at least one main-analysis site, ordered by the number of main sites (most first). These 29 cells hold all 71 main sites, plus 46 offices and 2 R2 sites.

| # | Cell | Latitude (centre) | Longitude (centre) | Cell latitude range | Cell longitude range | Main sites | Office + R2 sites | Firms (main sites) | Expected NASA file name |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `m2_193_293` | **6.50** | **3.125** | 6.25 to 6.75 | 2.8125 to 3.4375 | 18 | 41 | ABCTRANS, ACADEMY, BETAGLAS, BUAFOODS, DANGCEM, FIDSON, GUINNESS, HONYFLOUR, LIVESTOCK, NB, NEIMETH, NESTLE, UNILEVER, VITAFOAM | `POWER_Point_Daily_19910101_20251231_006d50N_003d125E_LST.csv` |
| 2 | `m2_190_299` | **5.00** | **6.875** | 4.75 to 5.25 | 6.5625 to 7.1875 | 6 | 0 | ABCTRANS, ARADEL, BUAFOODS, TRANSCORP | `POWER_Point_Daily_19910101_20251231_005d00N_006d875E_LST.csv` |
| 3 | `m2_190_300` | **5.00** | **7.50** | 4.75 to 5.25 | 7.1875 to 7.8125 | 6 | 1 | GUINNESS, LIVESTOCK, NB, TRANSCORP, VITAFOAM | `POWER_Point_Daily_19910101_20251231_005d00N_007d50E_LST.csv` |
| 4 | `m2_204_302` | **12.00** | **8.75** | 11.75 to 12.25 | 8.4375 to 9.0625 | 4 | 0 | BUAFOODS, MAYBAKER, NNFM, VITAFOAM | `POWER_Point_Daily_19910101_20251231_012d00N_008d75E_LST.csv` |
| 5 | `m2_192_299` | **6.00** | **6.875** | 5.75 to 6.25 | 6.5625 to 7.1875 | 3 | 0 | CUTIX, HONYFLOUR, NB | `POWER_Point_Daily_19910101_20251231_006d00N_006d875E_LST.csv` |
| 6 | `m2_194_294` | **7.00** | **3.75** | 6.75 to 7.25 | 3.4375 to 4.0625 | 3 | 0 | HBMNG, HONYFLOUR, NB | `POWER_Point_Daily_19910101_20251231_007d00N_003d75E_LST.csv` |
| 7 | `m2_198_300` | **9.00** | **7.50** | 8.75 to 9.25 | 7.1875 to 7.8125 | 3 | 2 | MAYBAKER, TRANSCORP | `POWER_Point_Daily_19910101_20251231_009d00N_007d50E_LST.csv` |
| 8 | `m2_191_298` | **5.50** | **6.25** | 5.25 to 5.75 | 5.9375 to 6.5625 | 2 | 0 | BETAGLAS, TRANSPOWER | `POWER_Point_Daily_19910101_20251231_005d50N_006d25E_LST.csv` |
| 9 | `m2_192_297` | **6.00** | **5.625** | 5.75 to 6.25 | 5.3125 to 5.9375 | 2 | 0 | SEPLAT | `POWER_Point_Daily_19910101_20251231_006d00N_005d625E_LST.csv` |
| 10 | `m2_194_293` | **7.00** | **3.125** | 6.75 to 7.25 | 2.8125 to 3.4375 | 2 | 0 | DANGCEM, HBMNG | `POWER_Point_Daily_19910101_20251231_007d00N_003d125E_LST.csv` |
| 11 | `m2_195_298` | **7.50** | **6.25** | 7.25 to 7.75 | 5.9375 to 6.5625 | 2 | 0 | BUACEMENT | `POWER_Point_Daily_19910101_20251231_007d50N_006d25E_LST.csv` |
| 12 | `m2_195_302` | **7.50** | **8.75** | 7.25 to 7.75 | 8.4375 to 9.0625 | 2 | 0 | DANGCEM, NB | `POWER_Point_Daily_19910101_20251231_007d50N_008d75E_LST.csv` |
| 13 | `m2_206_296` | **13.00** | **5.00** | 12.75 to 13.25 | 4.6875 to 5.3125 | 2 | 0 | BUACEMENT | `POWER_Point_Daily_19910101_20251231_013d00N_005d00E_LST.csv` |
| 14 | `m2_189_299` | **4.50** | **6.875** | 4.25 to 4.75 | 6.5625 to 7.1875 | 1 | 0 | DANGCEM | `POWER_Point_Daily_19910101_20251231_004d50N_006d875E_LST.csv` |
| 15 | `m2_189_301` | **4.50** | **8.125** | 4.25 to 4.75 | 7.8125 to 8.4375 | 1 | 0 | SEPLAT | `POWER_Point_Daily_19910101_20251231_004d50N_008d125E_LST.csv` |
| 16 | `m2_190_302` | **5.00** | **8.75** | 4.75 to 5.25 | 8.4375 to 9.0625 | 1 | 0 | HBMNG | `POWER_Point_Daily_19910101_20251231_005d00N_008d75E_LST.csv` |
| 17 | `m2_193_296` | **6.50** | **5.00** | 6.25 to 6.75 | 4.6875 to 5.3125 | 1 | 1 | OKOMUOIL | `POWER_Point_Daily_19910101_20251231_006d50N_005d00E_LST.csv` |
| 18 | `m2_193_297` | **6.50** | **5.625** | 6.25 to 6.75 | 5.3125 to 5.9375 | 1 | 2 | GUINNESS | `POWER_Point_Daily_19910101_20251231_006d50N_005d625E_LST.csv` |
| 19 | `m2_193_299` | **6.50** | **6.875** | 6.25 to 6.75 | 6.5625 to 7.1875 | 1 | 0 | ELLAHLAKES | `POWER_Point_Daily_19910101_20251231_006d50N_006d875E_LST.csv` |
| 20 | `m2_193_300` | **6.50** | **7.50** | 6.25 to 6.75 | 7.1875 to 7.8125 | 1 | 1 | NB | `POWER_Point_Daily_19910101_20251231_006d50N_007d50E_LST.csv` |
| 21 | `m2_195_294` | **7.50** | **3.75** | 7.25 to 7.75 | 3.4375 to 4.0625 | 1 | 0 | NB | `POWER_Point_Daily_19910101_20251231_007d50N_003d75E_LST.csv` |
| 22 | `m2_195_299` | **7.50** | **6.875** | 7.25 to 7.75 | 6.5625 to 7.1875 | 1 | 0 | GEREGU | `POWER_Point_Daily_19910101_20251231_007d50N_006d875E_LST.csv` |
| 23 | `m2_196_298` | **8.00** | **6.25** | 7.75 to 8.25 | 5.9375 to 6.5625 | 1 | 0 | DANGCEM | `POWER_Point_Daily_19910101_20251231_008d00N_006d25E_LST.csv` |
| 24 | `m2_197_299` | **8.50** | **6.875** | 8.25 to 8.75 | 6.5625 to 7.1875 | 1 | 0 | NESTLE | `POWER_Point_Daily_19910101_20251231_008d50N_006d875E_LST.csv` |
| 25 | `m2_198_297` | **9.00** | **5.625** | 8.75 to 9.25 | 5.3125 to 5.9375 | 1 | 0 | BUAFOODS | `POWER_Point_Daily_19910101_20251231_009d00N_005d625E_LST.csv` |
| 26 | `m2_198_299` | **9.00** | **6.875** | 8.75 to 9.25 | 6.5625 to 7.1875 | 1 | 0 | ALEX | `POWER_Point_Daily_19910101_20251231_009d00N_006d875E_LST.csv` |
| 27 | `m2_199_307` | **9.50** | **11.875** | 9.25 to 9.75 | 11.5625 to 12.1875 | 1 | 0 | DANGSUGAR | `POWER_Point_Daily_19910101_20251231_009d50N_011d875E_LST.csv` |
| 28 | `m2_200_302` | **10.00** | **8.75** | 9.75 to 10.25 | 8.4375 to 9.0625 | 1 | 0 | VITAFOAM | `POWER_Point_Daily_19910101_20251231_010d00N_008d75E_LST.csv` |
| 29 | `m2_201_296` | **10.50** | **5.00** | 10.25 to 10.75 | 4.6875 to 5.3125 | 1 | 0 | JAPAULGOLD | `POWER_Point_Daily_19910101_20251231_010d50N_005d00E_LST.csv` |

**Expected file names** follow the pattern of your first download (`004d75N_007d25E`: three-digit degrees, "d", then the decimals). For three-decimal longitudes such as 3.125, I have not verified the exact name or whether the Viewer keeps the third decimal. If it rounds, for example to 3.13, the point is still well inside the same cell; I will report any such header as a deviation and check it against the cell range instead of the exact centre.

## Already covered by an existing download? None

None of these 29 cell centres was downloaded before. Every earlier request (the 29 manual files, the 33 API files and the 6.75 N 7.00 E typo file) has a latitude ending in .25 or .75. Those values are native cell **edges**, never centres, so no earlier file can be matched to one native cell with certainty. **All 29 cells need a new download.**

## Not to download: 5 cells with no main-analysis site

As under your earlier decision, their sites will be marked "not scored — no owner download".

| Cell | Latitude (centre) | Longitude (centre) | Sites |
|---|---|---|---|
| `m2_190_301` | 5.00 | 8.125 | F0168 CHAMPION (office) |
| `m2_191_299` | 5.50 | 6.875 | F0132 ABCTRANS (office) |
| `m2_191_300` | 5.50 | 7.50 | F0172 GOLDBREW (office) |
| `m2_193_294` | 6.50 | 3.75 | F0035 INTBREW (office); F0193 AIRTELAFRI (office) |
| `m2_195_296` | 7.50 | 5.00 | F0036 INTBREW (R2) |

## What happens when the files arrive

1. Copy them to `data/raw/hazards/nasa_power_manual_v2/` as `m2_<i>_<j>.csv`, and record their SHA-256 in `docs/data_sources.md`.
2. Check that the header location of each file is its cell centre, and that the header states the 0.5 x 0.625 degree region.
3. Re-score heat from these files (A9), then re-run `phase3_firms.py` and `phase3_map.py`.
4. Report how many sites' heat exposure changed relative to the old 0.5° bins (main, office and R2 separately), and the firms affected.
