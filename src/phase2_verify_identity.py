"""Phase 2, Tasks 1-2: update data/interim/ngx_census_frame.csv with document-test results and identity checks.

For every firm with a report in hand, records the issuer name as printed on the report's first page and the
first 'principal activity' statement with its PDF page. NGX sector labels are not printed in these reports,
so the sector is recorded as 'activity-based (report p.N); NGX label not stated in report'.
"""
import csv
import re
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "data" / "interim" / "ngx_census_frame.csv"
ACT = re.compile(r"(principal activit(y|ies)[^.]{0,30}(is|are|of the (company|group)[^.]{0,20}(is|are|include|remained))|is principally engaged in|nature of business)[^.]{10,300}\.", re.I)
PILOT_FILES = {
    "DANGCEM": "data/raw/pilot_reports/dangote_cement/2025_AR.pdf", "BUACEMENT": "data/raw/pilot_reports/bua_cement/2025_AR.pdf",
    "GUINNESS": "data/raw/pilot_reports/guinness_nigeria/2025_AR.pdf", "OKOMUOIL": "data/raw/pilot_reports/okomu_oil/2022_AR.pdf",
    "PRESCO": "data/raw/pilot_reports/presco/2025_AR.pdf", "BETAGLAS": "data/raw/pilot_reports/beta_glass/2023_AR.pdf",
    "INTBREW": "data/raw/pilot_reports/international_breweries/2023_FS.pdf", "CADBURY": "data/raw/pilot_reports/cadbury_nigeria/2025_FS.pdf",
    "MTNN": "data/raw/manual/mtn/MTN-Nigeria-2025-Annual-Report.pdf", "NESTLE": "data/raw/manual/nestle/Nestle_Nigeria_2025_Annual_Report.pdf",
    "NB": "data/raw/manual/nigerian_breweries/Nigerian_Breweries_2025_Annual_Report.pdf",
    "SEPLAT": "data/raw/manual/seplat/Seplat_2025_Integrated_Annual_Report.pdf",
    "HBMNG": "data/raw/pilot_reports/lafarge_africa/2023_FS.pdf",
}
GARBLED = {"UNILEVER": ("data/raw/manual/unilever/Unilever_Nigeria_2025_Annual_Report.pdf", 31,
                        "[text from a company report removed in the public copy]"),
           "THOMASWY": ("data/raw/manual/thomaswy/ng-thomas-2025-ar-00.pdf", 5,
                        "[sentence from a company report removed in the public copy]")}
FAILED = {"AUSTINLAZ": "failed — only an abridged version found (owner, 2026-11-07)",
          "PHARMDEKO": "failed — no 2023-2025 annual report found (owner, 2026-11-07)"}
LATEST_FY = {"OKOMUOIL": "2022 (2023-2025 reports have no text layer)", "BETAGLAS": "2023", "INTBREW": "2023", "HBMNG": "2023"}


def scan(path: Path):
    with pymupdf.open(path) as doc:
        cover = " ".join(doc[0].get_text().split())[:120] if len(doc) else ""
        for i, page in enumerate(doc, 1):
            m = ACT.search(" ".join(page.get_text().split()))
            if m:
                return cover, i, m.group(0)[:300]
    return cover, "", ""


def main() -> None:
    rows = list(csv.DictReader(FRAME.open(newline="", encoding="utf-8")))
    with (ROOT / "data" / "interim" / "phase2_report_inventory.csv").open(newline="", encoding="utf-8") as f:
        p2 = {r["ticker"]: r for r in csv.DictReader(f) if r["status"] == "ok"}
    files = {**PILOT_FILES, **{t: r["file"] for t, r in p2.items()}}
    new_cols = [c for c in ("report_file", "report_cover_text", "principal_activity_page", "principal_activity_quote",
                            "identity_status", "sector_status") if c not in rows[0]]
    fields = list(rows[0]) + new_cols
    for r in rows:
        t = r["ticker"]
        for c in new_cols:
            r.setdefault(c, "")
        if t in FAILED:
            r["document_test"] = FAILED[t]
            continue
        if t in GARBLED:
            f, page, quote = GARBLED[t]
            r.update(report_file=f, report_cover_text="(no usable text layer; read from page images)", principal_activity_page=page,
                     principal_activity_quote=quote, document_test="passed (report in hand)")
        elif t in files:
            cover, page, quote = scan(ROOT / files[t])
            r.update(report_file=files[t], report_cover_text=cover, principal_activity_page=page, principal_activity_quote=quote,
                     document_test="passed (report in hand)" if t not in LATEST_FY or not LATEST_FY[t].startswith("2022") else
                     "passed (report in hand: FY2023 and FY2024 reports exist but lack a text layer, OCR pending; identity read from FY2022)")
        else:
            if r["census_stratum"] in ("main", "robustness_stratum"):
                r["document_test"] = "pending — not found on own site or doclib; see docs/manual_download_list.md"
            continue
        r["identity_status"] = "verified from report cover and principal-activity statement" if r["principal_activity_quote"] \
            else "report in hand; principal-activity statement not found by text search (check manually)"
        r["sector_status"] = (f"activity-based (report p.{r['principal_activity_page']}); NGX sector label not stated in report"
                              if r["principal_activity_quote"] else "not verified — confirm in Phase 2 from a primary source")
        if t in LATEST_FY and LATEST_FY[t].startswith("2022"):
            r["note"] = (r["note"] + "; " if r["note"] else "") + "latest readable report FY2022"
    tmp = FRAME.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)
    tmp.replace(FRAME)
    for s in ("main", "robustness_stratum"):
        sel = [r for r in rows if r["census_stratum"] == s]
        print(s, len(sel), {k: sum(r["document_test"].startswith(k) for r in sel) for k in ("passed (report", "failed", "pending")})
    for r in rows:
        if r["report_file"] and not r["principal_activity_quote"]:
            print("  no activity quote:", r["ticker"])


if __name__ == "__main__":
    main()
