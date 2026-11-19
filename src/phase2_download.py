"""Phase 2, Task 1: download the latest full-year report per census firm from permitted hosts.

Permitted automated hosts (Phase 2 brief): the firm's own site and doclib.ngxgroup.com. Registrar or
aggregator copies are NOT downloaded automatically; those firms go to docs/manual_download_list.md.
URLs below were found by web search on 2026-11-07. Measures access and text layers only.

usage: phase2_download.py TICKER [TICKER...]
Output: data/raw/phase2_reports/<ticker>/<fy>_<type>.pdf and data/interim/phase2_report_inventory.csv
"""
import csv
import hashlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import download_pilot as dp  # noqa: E402  (reuses measure(), available_ram_mb())
from polite_fetch import fetch  # noqa: E402

OUT = ROOT / "data" / "raw" / "phase2_reports"
INV = ROOT / "data" / "interim" / "phase2_report_inventory.csv"
N = "https://doclib.ngxgroup.com/Financial_NewsDocs"
FIELDS = ["ticker", "fiscal_year", "type", "host_class", "url", "status", "file", "bytes", "sha256", "pages",
          "text_pages", "text_page_share", "median_chars_per_page", "image_only_pages", "extractability",
          "mentions_chairman", "mentions_sustainab", "mentions_climate", "first_text"]
# ticker: (fiscal year, type, host class, url). FS = filing named as financial statements on NGX.
ITEMS = {
    # The annual-report URL (.../DANGOTE-SUGAR-REFINERY-PLC-2025-ANNUAL-REPORT.pdf) returned HTTP 404 on 2026-11-07;
    # the same site's FY 2025 accounts file is used instead.
    "DANGSUGAR": (2025, "FS", "company", "https://sugar.dangote.com/wp-content/uploads/2026/03/DSR-Plc-FY-2025-Accounts.pdf"),
    "FTNCOCOA": (2025, "FS", "ngx_doclib", f"{N}/FTN_COCOA_-_2025_AFS.pdf"),
    "CONOIL": (2025, "FS", "ngx_doclib", f"{N}/47162_CONOIL_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_JUNE_2026.pdf"),
    "NASCON": (2025, "FS", "ngx_doclib", f"{N}/46191_NASCON_ALLIED_INDUSTRIES_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MARCH_2026.pdf"),
    "VITAFOAM": (2025, "FS", "ngx_doclib", f"{N}/45601_VITAFOAM_NIG_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_DECEMBER_2025.pdf"),
    "NEIMETH": (2025, "FS", "ngx_doclib", f"{N}/46374_NEIMETH_INTERNATIONAL_PHARMACEUTICALS_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MARCH_2026.pdf"),
    "CUTIX": (2025, "FS", "ngx_doclib", f"{N}/44613_CUTIX_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_JULY_2025.pdf"),
    "BERGER": (2025, "FS", "ngx_doclib", f"{N}/46449_BERGER_PAINTS_NIGERIA_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MARCH_2026.pdf"),
    "PZ": (2025, "FS", "ngx_doclib", f"{N}/44952_P_Z_CUSSONS_NIGERIA_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_SEPTEMBER_2025.pdf"),
    "MAYBAKER": (2025, "FS", "ngx_doclib", f"{N}/46387_MAY_AND_BAKER-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MARCH_2026.pdf"),
    "MORISON": (2025, "FS", "ngx_doclib", f"{N}/46939_MORISON_INDUSTRIES_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MAY_2026.pdf"),
    "HONYFLOUR": (2025, "FS", "ngx_doclib", f"{N}/44197_HONEYWELL_FLOUR_MILL_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MAY_2025.pdf"),
    "TRANSCORP": (2025, "FS", "ngx_doclib", f"{N}/Transnational_Corporation_Plc_-_2025_AFS.pdf"),
    "ABCTRANS": (2025, "FS", "ngx_doclib", f"{N}/46506_ABC_TRANSPORT_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MARCH_2026.pdf"),
    "RTBRISCOE": (2025, "FS", "ngx_doclib", f"{N}/46407_R_T_BRISCOE_(NIGERIA)_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MARCH_2026.pdf"),
    # Owner decision 2026-11-07: registrar sites allowed if robots/terms permit; saved under data/raw/manual/<ticker>/
    "AIRTELAFRI": (2025, "AR", "company", "https://cdn-webportal.airtelstream.net/website/investor/main/pdf/AR2025/Airtel-Africa-plc-Annual-Report-and-Accounts-2025.pdf"),
    "LIVESTOCK": (2025, "AR", "registrar", "https://cardinalstoneregistrars.com/wp-content/uploads/2026/05/LSF%20REPORT%202025.pdf"),
    "THOMASWY": (2025, "AR", "manual", "LOCAL:data/raw/manual/thomaswy/ng-thomas-2025-ar-00.pdf"),
    # Owner browser downloads from africanfinancials.com document pages, 2026-11-07
    "ACADEMY": (2025, "AR", "manual", "LOCAL:data/raw/manual/academy/ng-academ-2025-ar-00.pdf"),
    "ARADEL": (2025, "AR", "manual", "LOCAL:data/raw/manual/aradel/ng-aradel-2025-ar-00.pdf"),
    "BUAFOODS": (2024, "AR", "manual", "LOCAL:data/raw/manual/buafoods/ng-buaf-2024-ar-00.pdf"),
    "ELLAHLAKES": (2024, "AR", "manual", "LOCAL:data/raw/manual/ellahlakes/ng-ellahl-2024-ar-00.pdf"),
    "ENAMELWA": (2025, "AR", "manual", "LOCAL:data/raw/manual/enamelwa/ng-enamel-2025-ar-00.pdf"),
    "FIDSON": (2025, "AR", "manual", "LOCAL:data/raw/manual/fidson/ng-fidson-2025-ar-00.pdf"),
    "MEYER": (2025, "AR", "manual", "LOCAL:data/raw/manual/meyer/ng-meyer-2025-ar-00.pdf"),
    "MULTIVERSE": (2025, "AR", "manual", "LOCAL:data/raw/manual/multiverse/ng-multiv-2025-ar-00.pdf"),
    "NNFM": (2025, "AR", "manual", "LOCAL:data/raw/manual/nnfm/ng-nnfm-2025-ar-00.pdf"),
}
MANUAL_DEST = {"AIRTELAFRI", "LIVESTOCK", "THOMASWY"}
BATCH_SECONDS = 8 * 60
import polite_fetch  # noqa: E402
polite_fetch.MIN_INTERVAL_S = 5.0  # owner rule for this round: at least 5 s between requests


def load() -> dict:
    if not INV.exists():
        return {}
    with INV.open(newline="", encoding="utf-8") as f:
        return {r["ticker"]: r for r in csv.DictReader(f)}


def save(rows: dict) -> None:
    tmp = INV.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows.values())
    tmp.replace(INV)


def main() -> None:
    deadline = time.monotonic() + BATCH_SECONDS
    rows = load()
    for t in sys.argv[1:]:
        if rows.get(t, {}).get("status") == "ok":
            continue
        fy, kind, host, url = ITEMS[t]
        row = {"ticker": t, "fiscal_year": fy, "type": kind, "host_class": host, "url": url}
        if dp.available_ram_mb() < dp.MIN_FREE_RAM_MB:
            row["status"] = "not tested — low memory"
        elif time.monotonic() > deadline:
            save(rows)
            sys.exit(f"STOPPED_DEADLINE before {t}")
        else:
            if url.startswith("LOCAL:"):
                dest = ROOT / url[6:]
            elif t in MANUAL_DEST:
                dest = ROOT / "data" / "raw" / "manual" / t.lower() / f"{fy}_{kind}.pdf"
            else:
                dest = OUT / t.lower() / f"{fy}_{kind}.pdf"
            resp = dest.exists() or fetch(url, dest=dest, max_bytes=dp.MAX_BYTES, deadline=deadline)
            if resp is None or (resp is not True and resp.status_code != 200):
                row["status"] = "not_fetched" if resp is None else f"http_{resp.status_code}"
            else:
                data = dest.read_bytes()
                row.update(status="ok" if data[:4] == b"%PDF" else "not_a_pdf",
                           file=str(dest.relative_to(ROOT)).replace("\\", "/"), bytes=len(data),
                           sha256=hashlib.sha256(data).hexdigest())
                if row["status"] == "ok":
                    row.update(dp.measure(dest))
        rows[t] = row
        save(rows)
        print(t, row["status"], row.get("pages"), row.get("extractability"), str(row.get("first_text", ""))[:90])


if __name__ == "__main__":
    main()
