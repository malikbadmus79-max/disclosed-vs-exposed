"""Phase 0, Task 3: download pilot-firm PDFs reachable by permitted routes and measure extractability.

Measures access and text-layer quality only. Does not analyse report content.

Excluded by design: Nestle Nigeria, Unilever Nigeria, Nigerian Breweries and Seplat Energy. Their
own sites refused this client (HTTP 403), so no copies are fetched from other hosts.

Output: data/raw/pilot_reports/<firm>/<year>_<type>.pdf and data/interim/pilot_report_inventory.csv
"""
import csv
import ctypes
import hashlib
import re
import statistics
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polite_fetch import fetch  # noqa: E402

import pymupdf  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = ROOT / "data" / "raw" / "pilot_reports"
INVENTORY = ROOT / "data" / "interim" / "pilot_report_inventory.csv"
MAX_BYTES = 250 * 1024 * 1024
MIN_CHARS_TEXT_PAGE = 100
MIN_FREE_RAM_MB = 500
BATCH_SECONDS = 8 * 60
NOT_DOWNLOADED = "listed, not downloaded in Phase 0"
# Phase 0 scope set by the project owner: latest report per remaining firm. Other years wait for Phase 4.
LATEST_ONLY = {
    ("presco", 2025, "AR"), ("beta_glass", 2023, "AR"), ("international_breweries", 2023, "FS"),
    ("lafarge_africa", 2023, "FS"), ("flour_mills", 2024, "FS"), ("okomu_oil", 2024, "SR"),
    ("cadbury_nigeria", 2022, "FS"), ("cadbury_nigeria", 2025, "FS"),
}
MTN_FAILED = "not tested — download failed (slow server); owner to supply manually"
MANUAL_ONLY = {("mtn_nigeria", "2025", "AR"), ("mtn_nigeria", "2025", "SR")}

D = "https://cement.dangote.com/wp-content/uploads"
B = "https://www.buacement.com/documents"
G = "https://www.guinness-nigeria.com/wp-content/uploads"
O = "https://okomunigeria.com/wp-content/uploads"
M = "https://www.mtn.ng/wp-content/uploads"
N = "https://doclib.ngxgroup.com/Financial_NewsDocs"
P = "https://www.presco-plc.com/financial-reports"

# (firm, fiscal-year label, type, host class, URL). AR = annual report, SR = sustainability report,
# SRX = sustainability section published as an extract of the AR, FS = filing named as financial statements.
# PAGE: the URL is a page on which the PDF link must be resolved.
ITEMS = [
    ("dangote_cement", 2020, "AR", "company", f"{D}/2021/05/Dangote-Cement-Plc-Annual-Report-20201.pdf"),
    ("dangote_cement", 2022, "AR", "company", f"{D}/2023/04/DCP-2022-Annual-Report-UPDATED.pdf"),
    ("dangote_cement", 2023, "AR", "company", f"{D}/2024/04/DCP-Annual-Report_AR23_full.pdf"),
    ("dangote_cement", 2024, "AR", "company", f"{D}/2025/05/Dangote-Cement-FY-2024-Annual-Report.pdf"),
    ("dangote_cement", 2024, "SRX", "company", f"{D}/2025/05/Dangote-Cement-2024-Sustainability-Report.pdf"),
    ("dangote_cement", 2025, "AR", "company", f"{D}/2026/06/Dangote-Cememt-Plc-2025-Annual-Report.pdf"),
    ("dangote_cement", 2025, "SRX", "company", f"{D}/2026/07/Dangote-Cement-Plc-AR-2025-Sustainability-Report.pdf"),
    ("bua_cement", 2020, "AR", "company", f"{B}/2020-BUA-Cement-Annual-Report-DIGITAL20241010093515.pdf"),
    ("bua_cement", 2021, "AR", "company", f"{B}/Download%20Audited%20Annual%20Report%20&%20Accounts%20FY%20202120241010043006.pdf"),
    ("bua_cement", 2022, "AR", "company", f"{B}/Download%20Annual%20Report%20and%20Accounts%20FY%20202220241010041946.pdf"),
    ("bua_cement", 2023, "AR", "company", f"{B}/BUA-Cement-Annual-Report-and-Accounts-2023-WEB20241105083027.pdf"),
    ("bua_cement", 2024, "AR", "company", f"{B}/BUA%20Cement%20Plc%202024%20-%20compressed20260302033844.pdf"),
    ("bua_cement", 2025, "AR", "company", f"{B}/20260514_BUA%20CEMENT%20AR25_VF_update%20(INTERACTIVE)20260514091939.pdf"),
    ("guinness_nigeria", 2020, "AR", "company", f"{G}/2020/09/annual-report-2020_guinness-nigeria-plc.pdf"),
    ("guinness_nigeria", 2021, "AR", "company", f"{G}/2026/08/gnar-21.pdf"),
    ("guinness_nigeria", 2022, "AR", "company", f"{G}/2026/08/gnar-22.pdf"),
    ("guinness_nigeria", 2023, "AR", "company", f"{G}/2026/07/gn-annual-report-and-accounts-2023.pdf"),
    ("guinness_nigeria", 2024, "AR", "company", f"{G}/2024/09/guinness-nigeria-annual-report-2024.pdf"),
    ("guinness_nigeria", 2025, "AR", "company", f"{G}/2026/03/guinness-nigeria-annual-report-2025-3.pdf"),
    ("okomu_oil", 2020, "AR", "company", f"{O}/2021/12/2020-Annual-report-and-accounts.pdf"),
    ("okomu_oil", 2021, "AR", "company", f"{O}/2022/05/2021-Annual-report-and-accounts.pdf"),
    ("okomu_oil", 2022, "AR", "company", f"{O}/2023/05/2022-Annual-reports-and-accounts.pdf"),
    ("okomu_oil", 2023, "AR", "company", f"{O}/2024/05/Annual-reports-and-accounts.pdf"),
    ("okomu_oil", 2024, "AR", "company", f"{O}/2025/05/2024-Annual-reports-and-accounts.pdf"),
    ("okomu_oil", 2025, "AR", "company", f"{O}/2026/05/2025-Annual-reports-and-accounts.pdf"),
    ("okomu_oil", 2022, "SR", "company", f"{O}/2024/07/2024-03-19-Sustainability-report_compressed.pdf"),
    ("okomu_oil", 2024, "SR", "company", f"{O}/2025/06/Sustainability-report.pdf"),
    ("mtn_nigeria", 2020, "AR", "company", f"{M}/2022/11/MTN-Nigeria-Annual-Report-2020-2.pdf"),
    ("mtn_nigeria", 2021, "AR", "company", f"{M}/2022/11/MTN-Nigeria-Annual-Report-2021-2.pdf"),
    ("mtn_nigeria", 2022, "AR", "company", f"{M}/2023/07/MTN-Nigeria-Annual-Report-2022.pdf"),
    ("mtn_nigeria", 2023, "AR", "company", f"{M}/2024/04/MTN-Nigeria-2023-Annual-Report.pdf"),
    ("mtn_nigeria", 2024, "AR", "company", f"{M}/2025/04/MTN-Nigeria-2024-Annual-Report-3.pdf"),
    ("mtn_nigeria", 2025, "AR", "company", f"{M}/2026/05/MTN-Nigeria-2025-Annual-Report.pdf"),
    ("mtn_nigeria", 2020, "SR", "company", f"{M}/2024/12/MTN-Nigeria-2020-Sustainability-Report-1.pdf"),
    ("mtn_nigeria", 2021, "SR", "company", f"{M}/2024/12/MTN-Nigeria-2021-Sustainability-Report-1.pdf"),
    ("mtn_nigeria", 2022, "SR", "company", f"{M}/2024/12/MTN-Nigeria-2022-Sustainability-Report-1.pdf"),
    ("mtn_nigeria", 2023, "SR", "company", f"{M}/2024/12/MTN-Nigeria-2023-Sustainability-Report-1.pdf"),
    ("mtn_nigeria", 2024, "SR", "company", f"{M}/2025/04/MTN-Nigeria-2024-Sustainability-Report.pdf"),
    ("mtn_nigeria", 2025, "SR", "company", f"{M}/2026/04/MTN-Nigeria-2025-Sustainability-Report-Final.pdf"),
    ("presco", 2023, "AR", "company", f"PAGE:{P}/reports-20231/presco-plc-annual-report-and-accounts-2023/"),
    ("presco", 2024, "AR", "company", f"PAGE:{P}/reports-2024/presco-plc-2024-annual-reports-and-accounts/"),
    ("presco", 2025, "AR", "company", f"PAGE:{P}/reports-2025/presco-plc-annual-report-for-the-year-ended-31-december-2025/"),
    ("presco", 2021, "AR", "company", "PAGE:https://www.presco-plc.com/investor-relations/2022-annual-general-meeting/presco-plc-annual-report-and-notice-of-annual-general-meeting/"),
    ("beta_glass", 2023, "AR", "registrar", "https://greenwichregistrars.com/wp-content/uploads/2024/06/BETA-GLASS-ANNUAL-REPORT-AND-AUDITED-FINANCIAL-STATEMENT-2023.pdf"),
    ("international_breweries", 2022, "FS", "ngx_doclib", f"{N}/38066_INTERNATIONAL_BREWERIES_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2022_FINANCIAL_STATEMENTS_MARCH_2023.pdf"),
    ("international_breweries", 2023, "FS", "ngx_doclib", f"{N}/40765_INTERNATIONAL_BREWERIES_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2023_FINANCIAL_STATEMENTS_MARCH_2024.pdf"),
    ("lafarge_africa", 2020, "FS", "ngx_doclib", f"{N}/32658_LAFARGE_AFRICA_PLC%20_AUDITED_FINANCIAL_STATEMENT_FOR_2.pdf"),
    ("lafarge_africa", 2022, "AR", "registrar", "https://cardinalstoneregistrars.com/wp-content/uploads/2023/01/LAFARGE%202022%20ANNUAL%20REPORT%20AND%20ACCOUNTS.pdf"),
    ("lafarge_africa", 2023, "FS", "ngx_doclib", f"{N}/40402_LAFARGE_AFRICA_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2023_FINANCIAL_STATEMENTS_FEBRUARY_2024.pdf"),
    ("flour_mills", 2023, "FS", "ngx_doclib", f"{N}/39345_FLOUR_MILLS_OF_NIGERIA_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2023_FINANCIAL_STATEMENTS_AUGUST_2023.pdf"),
    ("flour_mills", 2024, "FS", "ngx_doclib", f"{N}/41402_FLOUR_MILLS_OF_NIGERIA_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2024_FINANCIAL_STATEMENTS_JUNE_2024.pdf"),
    ("cadbury_nigeria", 2022, "FS", "ngx_doclib", f"{N}/37448_CADBURY_NIGERIA_PLC%20_AUDITED_FINANCIAL_STATEMENT_FOR_.pdf"),
    ("cadbury_nigeria", 2025, "FS", "ngx_doclib", f"{N}/45800_CADBURY_NIGERIA_PLC.-_YEAR_END_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_JANUARY_2026.pdf"),
]

FIELDS = ["firm", "fiscal_year", "type", "host_class", "url", "status", "file", "bytes", "sha256", "pages",
          "text_pages", "text_page_share", "median_chars_per_page", "image_only_pages", "extractability",
          "mentions_chairman", "mentions_sustainab", "mentions_climate", "first_text"]


def available_ram_mb() -> int:
    """Available physical memory on Windows, from GlobalMemoryStatusEx."""
    class Status(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    status = Status()
    status.dwLength = ctypes.sizeof(Status)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    return status.ullAvailPhys // (1024 * 1024)


def resolve_page(url: str) -> str | None:
    resp = fetch(url)
    if resp is None or resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup.find_all(["a", "iframe", "embed", "object"]):
        target = tag.get("href") or tag.get("src") or tag.get("data") or ""
        if ".pdf" in target.lower():
            return urljoin(resp.url, target)
    return None


def measure(path: Path) -> dict:
    doc = pymupdf.open(path)
    counts, image_only, text = [], 0, []
    for page in doc:
        page_text = page.get_text()
        counts.append(len(page_text.strip()))
        text.append(page_text)
        if len(page_text.strip()) < MIN_CHARS_TEXT_PAGE and page.get_images():
            image_only += 1
    text_pages = sum(c >= MIN_CHARS_TEXT_PAGE for c in counts)
    share = text_pages / max(len(counts), 1)
    joined = " ".join(text).lower()
    label = "extractable" if share >= 0.8 else "mixed" if share >= 0.2 else "scanned_or_image"
    return {
        "pages": len(counts), "text_pages": text_pages, "text_page_share": round(share, 3),
        "median_chars_per_page": int(statistics.median(counts)) if counts else 0, "image_only_pages": image_only,
        "extractability": label, "mentions_chairman": "chairman" in joined, "mentions_sustainab": "sustainab" in joined,
        "mentions_climate": "climate" in joined, "first_text": re.sub(r"\s+", " ", " ".join(text[:2]))[:160],
    }


def load_inventory() -> dict:
    if not INVENTORY.exists():
        return {}
    with INVENTORY.open(newline="", encoding="utf-8") as f:
        return {(r["firm"], str(r["fiscal_year"]), r["type"]): r for r in csv.DictReader(f)}


def save_inventory(rows: dict) -> None:
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    tmp = INVENTORY.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, FIELDS)
        writer.writeheader()
        writer.writerows(rows.values())
    tmp.replace(INVENTORY)


def process(item: tuple, deadline: float) -> dict:
    firm, year, kind, host, url = item
    row = {"firm": firm, "fiscal_year": year, "type": kind, "host_class": host, "url": url}
    if url.startswith("PAGE:"):
        resolved = resolve_page(url[5:])
        if resolved is None:
            row["status"] = "no_pdf_link_on_page"
            return row
        url = row["url"] = resolved
    dest = OUT / firm / f"{year}_{kind}.pdf"
    if not dest.exists():
        resp = fetch(url, dest=dest, max_bytes=MAX_BYTES, deadline=deadline)
        if resp is None or resp.status_code != 200:
            row["status"] = "not_fetched" if resp is None else f"http_{resp.status_code}"
            return row
    data = dest.read_bytes()
    row.update(status="ok", file=str(dest.relative_to(ROOT)).replace("\\", "/"), bytes=len(data),
               sha256=hashlib.sha256(data).hexdigest())
    if data[:4] != b"%PDF":
        row["status"] = "not_a_pdf"
        dest.unlink()
        return row
    try:
        row.update(measure(dest))
    except Exception as exc:  # corrupt PDFs must not stop the audit
        row["status"] = f"parse_error:{type(exc).__name__}"
    return row


def main() -> None:
    """usage: download_pilot.py FIRM [FIRM...]  Downloads only LATEST_ONLY items for the named firms."""
    firms = sys.argv[1:]
    deadline = time.monotonic() + BATCH_SECONDS
    rows = load_inventory()
    for item in ITEMS:  # everything else stays recorded as listed
        key = (item[0], str(item[1]), item[2])
        if key not in rows:
            rows[key] = {"firm": item[0], "fiscal_year": item[1], "type": item[2], "host_class": item[3],
                         "url": item[4].removeprefix("PAGE:"), "status": NOT_DOWNLOADED}
    for key in MANUAL_ONLY:
        rows[key]["status"] = MTN_FAILED
    for item in ITEMS:
        firm, year, kind = item[0], item[1], item[2]
        if firm not in firms or (firm, year, kind) not in LATEST_ONLY:
            continue
        key = (firm, str(year), kind)
        if rows[key].get("status") == "ok":
            continue
        if available_ram_mb() < MIN_FREE_RAM_MB:  # owner's rule for this run: mark and move on
            rows[key]["status"] = "not tested — low memory"
            save_inventory(rows)
            print(*key, rows[key]["status"], f"({available_ram_mb()} MB available)")
            continue
        if time.monotonic() > deadline:
            save_inventory(rows)
            sys.exit(f"STOPPED_DEADLINE before {key}")
        rows[key] = process(item, deadline)
        save_inventory(rows)
        print(*key, rows[key]["status"], rows[key].get("pages"), rows[key].get("extractability"), rows[key].get("bytes"))
        if rows[key]["status"] == "not_fetched" and time.monotonic() > deadline:
            sys.exit(f"STOPPED_DEADLINE during {key}")
    save_inventory(rows)


if __name__ == "__main__":
    main()
