"""Phase 2, owner round 3 (files downloaded by the owner on 2026-11-07, processed 2026-11-11): document test and
identity check in data/interim/ngx_census_frame.csv.

For each firm: the report file, the issuer name as printed on the first page (from the text layer, or from the OCR
copy for scanned files), and the first principal-activity statement with its PDF page. Activity quotes were found by
text search and checked by the analyst; for OCR'd files they were checked against the page image and are given as
read from the image. NGX sector labels are not printed in these reports.
"""
import csv
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "data" / "interim" / "ngx_census_frame.csv"
M = "data/raw/manual/"
# ticker: (file used for identity (OCR copy for scans), original file, document, page, activity quote or "", note)
FIRMS = {
    "TOTAL": (M + "total/ng-total-2025-ar-00.pdf", None, "FY2025 audited financial statements with directors' report", 17,
              "[sentence from a company report removed in the public copy]", ""),
    "CHAMPION": (M + "champion/Champion Breweries PLC - 2025 - Annual Report & Financial Statements (SustainabilityReports.com).pdf", None,
                 "FY2025 annual report and financial statements", 51,
                 "[text from a company report removed in the public copy]",
                 "file from sustainabilityreports.com carries a download watermark"),
    "EUNISELL": (M + "eunisell/ng-ensl-2025-ar-00.pdf", None, "FY to 30 Jun 2025 annual financial statements", 5,
                 "[sentence from a company report removed in the public copy]", ""),
    "GOLDBREW": (M + "goldbrew/ng-goldbr-2024-ar-00.pdf", None, "FY to 31 Mar 2024 financial statements", 5,
                 "[sentence from a company report removed in the public copy]",
                 "p39: no revenue earned in the year while reactivating operations"),
    "IMG": (M + "img/ng-img-2025-ar-00.pdf", None, "FY2025 annual report and financial statements", 5,
            "[text from a company report removed in the public copy]", ""),
    "JAPAULGOLD": (M + "japaulgold/ng-japaul-2025-ar-00.pdf", None, "FY2025 consolidated and separate financial statements", 32,
                   "[sentence from a company report removed in the public copy]",
                   "p32 also reports gold mining to start in 2026 at Libeli, Niger State"),
    "MECURE": (M + "mecure/ng-mecure-2025-ar-00.pdf", None, "FY2025 annual report and financial statements", 4,
               "[sentence from a company report removed in the public copy]", ""),
    "MULTITREX": (M + "multitrex/ng-multix-2024-ar-00.pdf", None, "FY to 30 Apr 2024 reports and financial statements", 25,
                  "[sentence from a company report removed in the public copy]",
                  "20 of 57 pages are images without text; OCR'd on 2026-11-12 (ng-multix-2024-ar-00_ocr.pdf). p10 prints 'year ended 30th April 2025', apparently a typo"),
    "TRIPPLEG": (M + "trippleg/ng-trippl-2025-ar-00.pdf", None, "FY to 31 Mar 2025 financial statements", 7,
                 "[sentence from a company report removed in the public copy]", ""),
    "TRANSPOWER": (M + "transpower/ng-tpower-2025-ar-00.pdf", None, "FY2025 annual reports and accounts", 4,
                   "[sentence from a company report removed in the public copy]", ""),
    "CAP": (M + "cap/ng-cap-2025-ar-00.pdf", None, "FY2025 annual report", 5, "The Company is involved in the manufacturing and sale of paints.",
            "first page of the file is a notes page; issuer name from p3"),
    "OANDO": (M + "oando/ng-oando-2025-ar-00.pdf", None, "FY2025 audited consolidated and separate financial statements", 4,
              "[text from a company report removed in the public copy]", ""),
    "JBERGER": (M + "jberger/Julius Berger Nigeria PLC - 2025 - Annual Reports (SustainabilityReports.com).pdf", None, "FY2025 annual report", 13,
                "[sentence from a company report removed in the public copy]",
                "file from sustainabilityreports.com carries a download watermark"),
    "AIRTELAFRI": (M + "airtelafri/Airtel-Africa-plc-Annual-Report-and-Accounts-2025.pdf", None, "FY to 31 Mar 2025 annual report and accounts", 195,
                   "[sentence from a company report removed in the public copy]",
                   "UK-incorporated group; Nigerian operations through Airtel Networks Limited (p245)"),
}
# Firms whose first text page does not print the issuer name: use the first page that does, and say which page
COVER_KEY = {"OKOMUOIL": "OKOMU OIL PALM COMPANY PLC", "MECURE": "MeCure Industries Plc", "OANDO": "Oando PLC", "CAP": "Chemical and Allied Products", "JBERGER": "Julius Berger Nigeria Plc",
             "GEREGU": "GEREGU POWER PLC", "MULTIVERSE": "MULTIVERSE MINING", "THOMASWY": "THOMAS WYATT"}
# Scanned files: (OCR copy, original, document, page, quote as read from the page image, note)
OCR = {
    "THOMASWY": (M + "thomaswy/ng-thomas-2025-ar-00_ocr.pdf", M + "thomaswy/ng-thomas-2025-ar-00.pdf", "FY to 31 Mar 2025 financial statements (scan; OCR copy)", 5,
                 "[sentence from a company report removed in the public copy]", ""),
    "ELLAHLAKES": (M + "ellahlakes/ng-ellahl-2024-ar-00_ocr.pdf", M + "ellahlakes/ng-ellahl-2024-ar-00.pdf", "FY to 31 Jul 2024 consolidated financial statements (scan; OCR copy)", 5,
                   "It engages in the business of palm oil plantation and cassava plantation.", ""),
    "MULTIVERSE": (M + "multiverse/ng-multiv-2025-ar-00_ocr.pdf", M + "multiverse/ng-multiv-2025-ar-00.pdf", "FY2025 reports and financial statements (scan; OCR copy)", 16,
                   "[text from a company report removed in the public copy]", ""),
    "MCNICHOLS": (M + "mcnichols/ng-mcnich-2025-ar-00_ocr.pdf", M + "mcnichols/ng-mcnich-2025-ar-00.pdf", "FY2025 financial statements (scan; OCR copy)", 20,
                  "[sentence from a company report removed in the public copy]", ""),
    "UNIONDICON": (M + "uniondicon/ng-uds-2025-ar-00_ocr.pdf", M + "uniondicon/ng-uds-2025-ar-00.pdf", "FY2025 statements of audited accounts (scan; OCR copy)", 12,
                   "[sentence from a company report removed in the public copy]", ""),
    "ALEX": (M + "alex/ng-alex-2024-ar-00_ocr.pdf", M + "alex/ng-alex-2024-ar-00.pdf", "FY2024 financial statements (scan; OCR copy)", 17,
             "[sentence from a company report removed in the public copy]", ""),
    "ETERNA": (M + "eterna/ng-eterna-2025-ar-00_ocr.pdf", M + "eterna/ng-eterna-2025-ar-00.pdf", "FY2025 annual report and financial statements (scan; OCR copy)", 4,
               "[text from a company report removed in the public copy]", ""),
    "GEREGU": (M + "geregu/Geregu Power PLC - 2024 - Annual Report and Financial Statements (SustainabilityReports.com)_ocr.pdf",
               M + "geregu/Geregu Power PLC - 2024 - Annual Report and Financial Statements (SustainabilityReports.com).pdf",
               "FY2024 annual report and financial statements (scan; OCR copy)", 16,
               "[sentence from a company report removed in the public copy]",
               "scanned file from sustainabilityreports.com; no text layer except the watermark"),
    "OKOMUOIL": ("data/raw/pilot_reports/okomu_oil/2024_AR_ocr.pdf", "data/raw/pilot_reports/okomu_oil/2024_AR.pdf",
                 "FY2024 annual report (no text layer; OCR copy). FY2023 annual report also OCR'd", 17,
                 "[sentence from a company report removed in the public copy]",
                 "latest readable report now FY2024 (OCR copy, 2026-11-11)"),
}
# Owner decision 2026-11-12: firms with no report file by then fail the document test
FAILED = {"PREMPAINTS": "failed — report not obtainable, 2026-11-12 (owner decision; no file in data/raw/manual/prempaints/)"}
# Notes that later rounds make obsolete
DROP_NOTES = {"OKOMUOIL": "latest readable report FY2022", "MULTITREX": "20 of 57 pages are images without text (not OCR'd)"}


def cover(path: Path, key: str = "") -> str:
    with pymupdf.open(path) as d:
        for i, pg in enumerate(d, 1):
            t = " ".join(pg.get_text().split()).replace("Downloaded from SustainabilityReports.com", "").strip(" |")
            if key and key.lower() in t.lower():
                j = t.lower().index(key.lower())
                return f"(p{i}) " + t[max(0, j - 30): j + 90]
            if not key and len(t) > 20:
                return t[:120]
    return ""


def main() -> None:
    rows = list(csv.DictReader(FRAME.open(newline="", encoding="utf-8")))
    by = {r["ticker"]: r for r in rows}
    for t, status in FAILED.items():
        if not (ROOT / "data" / "raw" / "manual" / t.lower()).exists():
            by[t]["document_test"] = status
    for t, (f, orig, doc, page, quote, note) in {**FIRMS, **OCR}.items():
        r = by[t]
        cov = cover(ROOT / f, COVER_KEY.get(t, ""))
        r.update(report_file=orig or f, report_cover_text=(f"(OCR copy {Path(f).name}) " if orig else "") + cov,
                 principal_activity_page=page if quote else "", principal_activity_quote=quote,
                 document_test=f"passed (report in hand: {doc})")
        r["identity_status"] = ("verified from report cover and principal-activity statement" if quote
                                else "report in hand; principal-activity statement not found (check manually)")
        r["sector_status"] = (f"activity-based (report p.{page}); NGX sector label not stated in report" if quote
                              else "not verified — confirm in Phase 2 from a primary source")
        if t in DROP_NOTES:
            r["note"] = "; ".join(x for x in r["note"].split("; ") if x and x != DROP_NOTES[t])
        if note and note not in r["note"]:
            r["note"] = (r["note"] + "; " if r["note"] else "") + note
        print(t, "|", r["report_cover_text"][:90])
    tmp = FRAME.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    tmp.replace(FRAME)
    for s in ("main", "robustness_stratum"):
        sel = [r for r in rows if r["census_stratum"] == s]
        print(s, len(sel), {k: sum(r["document_test"].startswith(k) for r in sel) for k in ("passed", "failed", "pending")})


if __name__ == "__main__":
    main()
