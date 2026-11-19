# Grade-A spot-check guide

> **Superseded by amendment A6 (2026-11-12).** The grade-A locations are now checked by a documented rule (`src/a6_crosscheck.py`), and `spotcheck_gradeA.csv` already holds the rule-based labels. This helper is kept for optional manual review. A manual entry merged with `src/merge_spotcheck.py` replaces the A6 label for that row.

The design (OD-1) requires the owner to check every grade-A site location by hand before Phase 3. A helper page makes this a keyboard task.

## Open it

Open `data/processed/spotcheck_app.html` in a browser by double-clicking it. It needs an internet connection for the map library (unpkg.com) and the OpenStreetMap tiles.

## Check each site

The page shows one grade-A site at a time: operational sites first, then offices. For each site you see:

- the firm and facility
- the report quote and its PDF page
- the assigned coordinates, with the method, nominal precision and state check
- a map centred on the point, with a circle showing the nominal precision
- a link to the same spot on openstreetmap.org

Compare the point with the quoted address, then press one key:

| Key | Meaning |
|---|---|
| `1` | **Correct**: the point is at the site |
| `2` | **Approximate**: the right area (for example the town or suburb centroid), but not the exact site |
| `3` | **Wrong**: the point is not at the site and you don't know where it is |
| `M` | **Moved**: you know where the site is. Press `M`, then click the map at the right spot (`Esc` cancels) |
| `N` | **Note**: type a comment; it saves as you type (`Esc` leaves the box) |
| `←` / `→` | Previous or next site |

**Sites without coordinates.** Some grade-A sites (13 at present) have no coordinate yet. The map opens on Nigeria; use `M` to place the site if you can find it.

**Saving.** Your checks save in this browser after every key or click, and the progress bar counts checked sites. You can close the page and come back later on the same browser and computer.

Browser storage is not a backup. Clearing site data or using a private window loses the checks, so export from time to time.

## Hand the results over

1. Click **Export CSV**. This downloads `spotcheck_export_<date>.csv` with the columns `facility_id`, `owner_check`, `owner_lat`, `owner_lon`, `owner_note` and `checked_at`.
2. Merge the export into the project file:

   ```
   .venv/Scripts/python src/merge_spotcheck.py path/to/spotcheck_export_<date>.csv
   ```

   This fills the owner columns of `data/processed/spotcheck_gradeA.csv` and keeps the previous version as `spotcheck_gradeA.csv.bak`. Later rebuilds of the spot-check file (`src/phase2_outputs.py`) keep these entries.

To rebuild the helper page after the facilities change, run `src/phase2_spotcheck_app.py`.
