"""Phase 8 (owner review, 2026-11-18): heat-silence count (safe claim 3) with NASA POWER heat exposure instead of ERA5.
Descriptive only. Same rule as phase7b_robustness.desc() claim 3: main census, main point sites, firms with documents
(NNFM FY2020 excluded, A23); a firm "uses heat terms" if any narrative scored paragraph in any year matches a heat-family
term of the frozen dictionary (Phase 7b paragraph cache). Only the site exposure flag changes (heat_nasa_exposed).
Writes outputs/tables/robustness_8_nasa_heat_silence.csv.
"""
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase5_sites import HAZ  # noqa: E402

P, I, TAB = ROOT / "data" / "processed", ROOT / "data" / "interim", ROOT / "outputs" / "tables"

o = pd.read_csv(P / "outcomes_firm_year.csv")
o = o[~((o.firm == "NNFM") & (o.year == 2020))]
m = o[o.stratum == "main"]
c = pd.read_csv(I / "phase7b_paragraph_cache.csv", dtype={"families": str, "sites": str}).fillna("")
c = c[~((c.firm == "NNFM") & (c.year == 2020))]
sh = pd.read_csv(P / "site_hazards.csv")
s = sh[(sh.site_set == "main") & (sh.census_stratum == "main") & sh.ticker.isin(m.firm.unique())].copy()
# heat_nasa_exposed is stored as text (sites in cells not downloaded carry a label), so compare numerically
for col in ("heat_exposed", "heat_nasa_exposed"):
    s[col] = pd.to_numeric(s[col], errors="coerce")

famfirm = defaultdict(set)
for _, r in c[c.families != ""].iterrows():
    for g in r.families.split("|"):
        famfirm[g].add(r.firm)
fams = HAZ["heat"][1]
users_all = {f for g in fams for f in famfirm[g]}

rows = []
for src, col in (("ERA5 (main)", "heat_exposed"), ("NASA POWER (robustness)", "heat_nasa_exposed")):
    ss = s[s[col].notna()]
    ef = set(ss[ss[col] == 1].ticker)
    users = sorted(ef & users_all)
    rows.append({"heat_source": src, "sites_scored": len(ss), "sites_exposed": int((ss[col] == 1).sum()),
                 "firms_with_heat_exposed_site": len(ef), "of_which_use_heat_terms": len(users),
                 "firms_using_heat_terms": "; ".join(users)})
both = set(s[s.heat_exposed == 1].ticker) & set(s[s.heat_nasa_exposed == 1].ticker)
out = pd.DataFrame(rows)
out.to_csv(TAB / "robustness_8_nasa_heat_silence.csv", index=False)
print(out.to_string(index=False))
print("firms heat-exposed under both sources:", len(both), sorted(both))
print("all firms (main census) ever using heat terms:", sorted(f for f in users_all if f in set(m.firm)))
