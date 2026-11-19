"""Phase 2, Tasks 2-3: pull identity, principal-activity and facility-candidate passages (with PDF page) from
the Phase 2 reports, for analyst review. Writes data/interim/phase2_candidates/<ticker>.txt and prints a
short digest. Extracts text only; it assigns no grades and no coordinates.

usage: phase2_candidates.py TICKER [TICKER...]
"""
import csv
import re
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "data" / "interim" / "phase2_report_inventory.csv"
OUT = ROOT / "data" / "interim" / "phase2_candidates"
ACT = re.compile(r"principal activit|nature of business|is engaged in|are engaged in|is principally engaged", re.I)
FAC = re.compile(r"\b(registered office|head office|factory|factories|plant|plants|mill|mills|refiner(y|ies)|depot|depots|"
                 r"warehouse|terminal|estate|farm|plantation|mine|quarry|station|located at|situated at|site at)\b", re.I)
PLACE = re.compile(r"\b(Road|Street|Avenue|Way|Close|Expressway|Industrial|Estate|Km\s?\d+|State|Lagos|Ogun|Ikeja|Kano|Kaduna|"
                   r"Abuja|Port Harcourt|Rivers|Oyo|Ibadan|Ondo|Edo|Delta|Enugu|Anambra|Abia|Kwara|Ilorin|Benue|Niger|Plateau|"
                   r"Akwa Ibom|Cross River|Kogi|Bauchi|Sokoto|Zamfara|Kebbi|Katsina|Jigawa|Yobe|Borno|Adamawa|Taraba|Gombe|"
                   r"Nasarawa|Ekiti|Osun|Imo|Ebonyi|Bayelsa|Agbara|Ota|Apapa|Ikorodu|Sagamu|Owode|Akure)\b")


def sentences(text: str):
    for s in re.split(r"(?<=[.;:])\s+|\n{2,}", text):
        s = " ".join(s.split())
        if 20 <= len(s) <= 400:
            yield s


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with INV.open(newline="", encoding="utf-8") as f:
        inv = {r["ticker"]: r for r in csv.DictReader(f)}
    for t in sys.argv[1:]:
        row = inv[t]
        lines, act, fac = [], [], []
        with pymupdf.open(ROOT / row["file"]) as doc:
            for i, page in enumerate(doc, 1):
                for s in sentences(page.get_text()):
                    if ACT.search(s):
                        act.append((i, s))
                    if FAC.search(s) and PLACE.search(s):
                        fac.append((i, s))
        seen = set()
        fac = [x for x in fac if not (x[1][:60] in seen or seen.add(x[1][:60]))]
        lines.append(f"# {t} | {row['file']} | pages {row['pages']}")
        lines.append(f"COVER p1: {row['first_text'][:200]}")
        lines += [f"ACT p{p}: {s}" for p, s in act[:4]]
        lines += [f"FAC p{p}: {s}" for p, s in fac]
        (OUT / f"{t}.txt").write_text("\n".join(lines), encoding="utf-8")
        print("\n".join(lines[:2] + [l[:230] for l in lines[2:] if l.startswith("ACT")][:2]
                        + [l[:230] for l in lines if l.startswith("FAC")][:9]))
        print(f"  [{len(act)} activity, {len(fac)} facility candidates]\n")


if __name__ == "__main__":
    main()
