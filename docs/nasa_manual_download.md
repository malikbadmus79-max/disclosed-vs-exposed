# NASA POWER: manual download list (owner)

> **Superseded for heat scoring by A9 (2026-11-12):** see `docs/nasa_manual_download_v2.md` (MERRA-2 native cells). This first list used 0.5° bins whose centres lie on native cell edges. It is kept as a record.

**Why.** On 2026-11-12 the owner decided that the robots.txt exception does not cover further NASA POWER requests: power.larc.nasa.gov's robots.txt now names Anthropic agents. No further API requests will be made. The 33 files fetched earlier (`data/raw/hazards/nasa_power/`) are **provisional** and are to be replaced by your manual downloads. The heat scores in `site_hazards.csv` and `firm_exposure.csv` are marked provisional until then.

## What to download

In the **POWER Data Access Viewer** (https://power.larc.nasa.gov/data-access-viewer/), make one download per row of the table below:

- **Data type:** Single Point
- **Community:** Agroclimatology (AG), which the API files used
- **Temporal average:** Daily
- **Latitude / longitude:** the cell centre in the table, in decimal degrees (north and east are positive)
- **Time extent:** 1991-01-01 to 2025-12-31
- **Parameter:** Temperature at 2 Meters Maximum (**T2M_MAX**). T2M_MIN and RH2M are optional; the design lists them, but the heat metric uses only T2M_MAX.
- **Format:** CSV or JSON

**Save each file** as `data/raw/hazards/nasa_power_manual/bin_<i>_<j>.csv` (or `.json`), using the bin name from the table. The bins are 0.5° cells: lat = i × 0.5 + 0.25 and lon = j × 0.5 + 0.25. That cell edges fall on multiples of 0.5° is assumed, not verified.

| # | File name | Latitude (centre) | Longitude (centre) | Sites | Firms |
|---|---|---|---|---|---|
| 1 | `bin_9_14` | 4.75 | 7.25 | 8 | ABCTRANS, ARADEL, BUAFOODS, DANGCEM, TRANSCORP |
| 2 | `bin_9_16` | 4.75 | 8.25 | 1 | SEPLAT |
| 3 | `bin_10_11` | 5.25 | 5.75 | 2 | BETAGLAS, TRANSPOWER |
| 4 | `bin_10_14` | 5.25 | 7.25 | 7 | ABCTRANS, GUINNESS, LIVESTOCK, NB, VITAFOAM |
| 5 | `bin_10_15` | 5.25 | 7.75 | 1 | CHAMPION |
| 6 | `bin_10_17` | 5.25 | 8.75 | 1 | HBMNG |
| 7 | `bin_11_11` | 5.75 | 5.75 | 2 | SEPLAT |
| 8 | `bin_11_14` | 5.75 | 7.25 | 1 | GOLDBREW |
| 9 | `bin_12_6` | 6.25 | 3.25 | 28 | ABCTRANS, AIRTELAFRI, ARADEL, BETAGLAS, BUACEMENT, BUAFOODS, DANGCEM, DANGSUGAR, ETERNA, GEREGU, HBMNG, HONYFLOUR, INTBREW, MTNN, NB, OANDO, SEPLAT, THOMASWY, TOTAL, TRANSCORP, TRANSPOWER, UNIONDICON |
| 10 | `bin_12_10` | 6.25 | 5.25 | 2 | OKOMUOIL |
| 11 | `bin_12_11` | 6.25 | 5.75 | 3 | ELLAHLAKES, GUINNESS, NB |
| 12 | `bin_12_13` | 6.25 | 6.75 | 3 | CUTIX, HONYFLOUR, NB |
| 13 | `bin_12_14` | 6.25 | 7.25 | 1 | NB |
| 14 | `bin_12_15` | 6.25 | 7.75 | 1 | NB |
| 15 | `bin_13_6` | 6.75 | 3.25 | 34 | ABCTRANS, ACADEMY, BERGER, BETAGLAS, BUAFOODS, CADBURY, CAP, EUNISELL, FIDSON, FTNCOCOA, GUINNESS, HBMNG, IMG, JAPAULGOLD, LIVESTOCK, MAYBAKER, MECURE, MEYER, MORISON, NASCON, NB, NEIMETH, NESTLE, PZ, UNILEVER, VITAFOAM |
| 16 | `bin_13_7` | 6.75 | 3.75 | 3 | HBMNG, HONYFLOUR, NB |
| 17 | `bin_13_14` | 6.75 | 7.25 | 1 | ELLAHLAKES |
| 18 | `bin_14_6` | 7.25 | 3.25 | 1 | DANGCEM |
| 19 | `bin_14_7` | 7.25 | 3.75 | 1 | NB |
| 20 | `bin_14_12` | 7.25 | 6.25 | 2 | BUACEMENT |
| 21 | `bin_14_17` | 7.25 | 8.75 | 1 | DANGCEM |
| 22 | `bin_15_9` | 7.75 | 4.75 | 1 | INTBREW |
| 23 | `bin_15_12` | 7.75 | 6.25 | 1 | DANGCEM |
| 24 | `bin_15_13` | 7.75 | 6.75 | 1 | GEREGU |
| 25 | `bin_15_17` | 7.75 | 8.75 | 1 | NB |
| 26 | `bin_16_13` | 8.25 | 6.75 | 1 | NESTLE |
| 27 | `bin_17_10` | 8.75 | 5.25 | 1 | BUAFOODS |
| 28 | `bin_18_14` | 9.25 | 7.25 | 6 | ALEX, JBERGER, MAYBAKER, NB, TRANSCORP |
| 29 | `bin_18_24` | 9.25 | 12.25 | 1 | DANGSUGAR |
| 30 | `bin_19_17` | 9.75 | 8.75 | 1 | VITAFOAM |
| 31 | `bin_21_9` | 10.75 | 4.75 | 1 | JAPAULGOLD |
| 32 | `bin_23_17` | 11.75 | 8.75 | 4 | BUAFOODS, MAYBAKER, NNFM, VITAFOAM |
| 33 | `bin_26_10` | 13.25 | 5.25 | 2 | BUACEMENT |

## What happens when the files arrive

1. **Compare:** `src/phase3_heat.py compare` checks each manual file against the provisional API file and prints the maximum absolute daily difference in T2M_MAX per bin. They should match; any difference will be reported.
2. **Re-score from your files:** `src/phase3_heat.py score manual`, then `src/phase3_firms.py` and `src/phase3_map.py`. The heat source column in `site_hazards.csv` then reads "NASA POWER Data Access Viewer, owner manual download".
3. **Record:** the files are logged in `docs/data_sources.md` with SHA-256.
