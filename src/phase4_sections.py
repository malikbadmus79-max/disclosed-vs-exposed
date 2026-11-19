"""Phase 4: section tagging (design f1) by the A14 rule. Reads data/interim/paragraphs.csv, writes
data/interim/section_tags.csv and adds a `section` column to paragraphs.csv (narrative / financial_statements).

A14 rule (see docs/amendments.md):
  evidence headings, case-insensitive, at the start of a heading-like block (<= 20 words) among the first 6 blocks of a page:
    A = independent auditor's report;  S = primary statements;  N = notes to the financial statements
  contents pages ignored (a "contents" heading, >= 4 evidence headings on the page, or a heading ending in a page number)
  start = first page with A or S evidence; last evidence = last page with A, S or N evidence
  end = page before the first later page headed by a post-statement section, else the document's last page
  flags for analyst review: no A/S evidence (AR/IAR/FS); range < 15% of an AR/IAR's pages; > 10 pages between last
  evidence and end; a narrative heading inside the range.
Analyst decisions for flagged documents are applied from OVERRIDES below, each with page + heading evidence.

usage: phase4_sections.py tag | headings <doc> [from] [to] | apply
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I = ROOT / "data" / "interim"
PARA = I / "paragraphs.csv"
OUT = I / "section_tags.csv"
csv.field_size_limit(10 ** 8)

PRE = r"^(?:the\s+)?(?:(?:consolidated|separate|group|company)(?:\s+and\s+(?:separate|company))?\s+)?"
EVID = {
    "A": re.compile(r"^(?:\d+\s*\.?\s*)?(?:independent\s+auditor['’]?s?['’]?\s+report|report\s+of\s+the\s+independent\s+auditors?)", re.I),
    "S": re.compile(PRE + r"(?:statements?\s+of\s+(?:financial\s+position|profit\s+or\s+loss|(?:other\s+)?comprehensive\s+income|"
                    r"changes\s+in\s+equity|cash\s*flows?)|balance\s+sheets?|income\s+statements?|cash\s*flow\s+statements?)", re.I),
    "N": re.compile(PRE + r"notes\s+to\s+the\s+(?:consolidated\s+(?:and\s+separate\s+)?)?(?:and\s+separate\s+)?financial\s+statements", re.I),
}
POST = re.compile(r"^(?:other\s+national\s+disclosures|(?:statements?\s+of\s+)?value\s+added(?:\s+statement)?|"
                  r"(?:five|5)[\s-]*year\s+(?:financial\s+)?summary|financial\s+summary|shareholder(?:s['’]?)?\s+information|"
                  r"proxy\s+form|notice\s+of\s+(?:the\s+)?(?:\d+\w*\s+)?annual\s+general\s+meeting|e[\s-]*dividend|unclaimed\s+dividend)", re.I)
NARR = re.compile(r"^(?:chairman['’]?s\s+statement|report\s+of\s+the\s+directors|directors['’]?\s+report|sustainability\s+report|"
                  r"corporate\s+governance(?:\s+report)?)\b", re.I)
CONTENTS = re.compile(r"^(?:table\s+of\s+)?contents?\b|^in\s+this\s+report\b", re.I)
PAGENUM = re.compile(r"\s\d{1,3}$")

# analyst review decisions (A14), 2026-11-17: doc -> start, end, evidence, note. Reviewed from page headings only.
def _o(start, end, se, ee, note):
    return {"start": start, "end": end, "start_evidence": se, "end_evidence": ee, "note": note}


OVERRIDES = {
    "AIRTELAFRI_2025_AR": _o(179, 253, "p179: 'Financial statements' divider; p180: Independent Auditor's report to the Members of Airtel Africa plc",
                             "p254: 'Other information' (alternative performance measures, glossary)",
                             "rule start p55 was a summary 'Consolidated statement of financial position' in the financial review"),
    "ARADEL_2025_AR": _o(18, 135, "p18: INDEPENDENT AUDITOR'S REPORT To the Shareholders (Deloitte)", "document end (notes to p135)",
                         "rule missed the auditor's report and the statements on pp22-23"),
    "GUINNESS_2022_AR": _o(84, 154, "p84: Report on the audit of the financial statements / Our opinion", "p155: SHAREHOLDERS' INFORMATION",
                           "auditor's report has no 'independent auditor's report' heading in its first blocks"),
    "GUINNESS_2023_AR": _o(76, 148, "p76: Report on the audit of the financial statements / Our opinion", "p149: SHAREHOLDERS' INFORMATION",
                           "as Guinness 2022"),
    "GUINNESS_2024_AR": _o(74, 147, "p74: Report on the audit of the financial statements / Our opinion", "p148: Shareholders' Information",
                           "as Guinness 2022; pp79-80 (assurance on internal control) fall inside the range"),
    "OKOMUOIL_2020_AR": _o(29, 60, "p29: Report on the financial statements (auditor's report, OCR page)", "p61: Distribution of value added",
                           "rule start p31 missed the auditor's report; pp63-69 are photo pages and proxy form"),
    "OKOMUOIL_2022_AR": _o(33, 76, "p33: INDEPENDENT AUDITORS' REPORT TO THE MEMBERS (rule)", "p77: value added / p78 five-year summary; community pages from p79",
                           "five-year summary headings extended the rule's range over narrative pages"),
    "OKOMUOIL_2023_AR": _o(32, 83, "p32: REPORT ON THE AUDIT OF THE FINANCIAL STATEMENTS", "p84-85: value added statement; photo and proxy pages follow",
                           "as Okomu 2022"),
    "OKOMUOIL_2024_AR": _o(39, 103, "p39: REPORT ON THE AUDIT OF THE FINANCIAL STATEMENTS (EY)", "p104: VALUE ADDED STATEMENT; community pages from p106",
                           "as Okomu 2022"),
    "NNFM_2025_AR": _o(34, 87, "p34: INDEPENDENT AUDITOR'S REPORT (heading below the internal-control assurance text at the top of p34)",
                       "p88: OTHER NATIONAL DISCLOSURES; employee-engagement pages and proxy form follow",
                       "five-year summary headings extended the rule's range over narrative pages"),
    "THOMASWY_2025_FS": _o(15, 57, "p15: REPORT OF THE INDEPENDENT AUDITORS TO THE SHAREHOLDERS", "document end (rule)",
                           "rule start p23 missed the auditor's report and two statements"),
    "MEYER_2025_AR": _o(11, 66, "p11: auditor's letterhead (PKF Professional Services); p14: Key audit matters", "document end (rule)",
                        "rule start p17 missed the auditor's report"),
    "MULTIVERSE_2025_AR": _o(5, 46, "p5: auditor's letterhead (Olukayode Aina & Co., Chartered Accountants)", "p47: FINANCIAL SUMMARY (rule)",
                             "rule start p11; pp8-9 (internal-control report) fall inside the range"),
    "CUTIX_2025_FS": _o(37, 78, "p37: auditor's letterhead (Chartered Accountants & Fraud Examiner); p39: ISA wording", "p79: Other National Disclosures (rule)",
                        "rule start p45 missed the auditor's report and the first statements (p41)"),
    "CHAMPION_2025_AR": _o(43, 92, "p43: Deloitte & Touche letterhead; p44: Key Audit Matter", "p93: OTHER NATIONAL DISCLOSURES (rule)",
                           "rule start p47 missed the auditor's report"),
    "JBERGER_2025_AR": _o(29, 78, "p29: two-up report pages 53-60 under the running header 'Annual Reports and Audited Consolidated and Separate ...' "
                          "with no text layer in the body, between the audit committee report (p28) and the statements (p33)",
                          "p79: OTHER NATIONAL DISCLOSURES AND ADDITIONAL INFORMATION (rule)", "auditor's report pages carry no text; start inferred from position"),
    "EUNISELL_2025_FS": _o(16, 36, "p16: Report of the Independent Auditors To the Members", "p37: Statement of Value Added (rule)",
                           "rule start p4 was 'Result at a glance'; pp13-15 are the internal-control assurance report"),
    "DANGCEM_2023_AR": _o(103, 172, "p103: INDEPENDENT AUDITOR'S REPORT To the Shareholders",
                          "p173: five-year summary ('Balance sheet 2023 2022 2021 ...'), then value added, share capital history, GRI index (p177)",
                          "rule found no heading: headings are fused with other text in the first blocks"),
    "MULTITREX_2024_AR": _o(17, 54, "p17: INDEPENDENT AUDITORS' REPORT TO THE MEMBERS (pp15-16: auditor's report on internal control)",
                            "p55: OTHER NATIONAL DISCLOSURES", "rule found no heading"),
    "ELLAHLAKES_2024_FS": _o(10, 46, "p10: auditor's letterhead (OA Professionals); p13: consolidated statement of profit or loss", "document end (notes pp35-42, summarised statements pp43-46)",
                             "rule found only p46 (OCR text)"),
    "TRIPPLEG_2025_FS": _o(27, 55, "p27: Statement of Financial Position (rule)", "p56: Value Added Statement (heading merged with table)",
                           "rule end ran over the value added statement and five-year summary"),
    "ETERNA_2025_AR": _o(14, 69, "p14: Independent auditor's report (rule)", "p70: 'Other National Disclosure' (singular, not matched by the rule)",
                         "end corrected"),
    "NB_2025_AR": _o(63, 162, "p63: INDEPENDENT AUDITOR'S REPORT (rule)", "p163: shareholder information (substantial interests, share capital history, dividends, major customers)",
                     "end corrected"),
    "HONYFLOUR_2025_FS": _o(31, 112, "p31: consolidated and separate statement of financial position (heading merged with table); pp26-30 have no text layer",
                            "p113: Other National Disclosures (rule)", "rule start p34 missed three statements"),
    # Phase 4 tier-1 files (owner batches 1-5), reviewed 2026-11-17 from page headings and page text
    "ACADEMY_2020_AR": _o(17, 96, "p17: INDEPENDENT AUDITOR'S REPORT (rule)", "p97: ACADEMY PRESS PLC VALUE ADDED STATEMENT",
                          "post-statement headings carry a company-name prefix, so the rule ran to the document end"),
    "ALEX_2020_AR": _o(20, 69, "p20: INDEPENDENT AUDITOR'S REPORT (Madu, Onyekwena & Co.)", "p70: OTHER NATIONAL DISCLOSURES (rule)",
                       "rule start p8 was a summary statement under 'Financial highlights'; pp10-19 are the directors' report, governance, audit committee"),
    "ARADEL_2021_AR": _o(45, 103, "p45 (two-up): audit committee report (left) and start of the Deloitte auditor's report (right; basis for opinion, key audit matter)",
                         "p104: notice of annual general meeting; unclaimed-dividend lists follow",
                         "two-up spreads; rule start p50 missed the auditor's report and first statements"),
    "BUAFOODS_2022_AR": _o(116, 171, "p116: Independent Auditors' Report", "p172: Value Added Statement - Group",
                           "rule found no heading: every page starts with a navigation bar"),
    "GEREGU_2022_AR": _o(26, 70, "pp26-29: no text layer (signature lines only), between the audit committee report (p25) and the statement of financial position (p31)",
                         "p71: value added statement; p72: five-year summary", "auditor's report pages carry no text; start inferred from position"),
    "HONYFLOUR_2020_AR": _o(54, 98, "p54: auditor's report (going concern, basis for opinion; p57 'Report of the Independent Auditors ... cont'd')",
                            "p99: 'Other Notional Disclosures' (sic)", "rule start p57 was the auditor's report's last page; end heading misspelt"),
    "LIVESTOCK_2020_AR": _o(43, 96, "p43: Report On The Audit Of The Financial Statements", "p97: value added statement; p98 five-year summary",
                            "headings fused with other text; rule range 81-100 covered notes only and ran over shareholder forms"),
    "NNFM_2020_AR": _o(57, 174, "p57: INDEPENDENT AUDITOR'S REPORT (rule)", "p175: Other National Disclosures (value added, five-year summary, CSR report follow)",
                       "rule end ran over value added, five-year summary and CSR pages"),
    "SEPLAT_2020_AR": _o(148, 295, "p148: Independent auditor's report (rule)", "p296: ADDITIONAL INFORMATION divider (payments to governments, AGM notice)",
                         "rule end ran over the additional-information section"),
    "TRANSPOWER_2024_AR": _o(29, 82, "p29: Deloitte auditor's report (pp26-28: assurance report on internal control, treated as narrative)",
                             "p83: OTHER NATIONAL DISCLOSURES (rule)", "rule start p35 missed the auditor's report"),
    "NEIMETH_2020_AR": _o(71, 114, "p71: REPORT OF THE INDEPENDENT AUDITORS", "p115: STATEMENT OF VALUE ADDED",
                          "rule start p61 was 'BALANCE SHEET RESTRUCTURING' inside the directors' report"),
    "ELLAHLAKES_2020_FS": _o(10, 43, "p10: auditor's letterhead (Olabode Akande & Co.), TO THE MEMBERS OF ELLAH LAKES PLC (OCR page)",
                             "p44: value added statement; pp45-46 two- and five-year summaries", "rule start p14 missed the auditor's report and two statements"),
    "NB_2020_AR": _o(30, 103, "pp30-33: no text layer, between the audit committee report (p29) and the statement of profit or loss (p34)",
                     "p104: Additional information - Value Added Statement", "auditor's report pages carry no text; start inferred from position"),
    "TRANSPOWER_2020_FS": _o(9, 66, "p9: Deloitte auditor's report", "p67: OTHER NATIONAL DISCLOSURES (rule)",
                             "rule start p13 missed the auditor's report and the first statement"),
    "VITAFOAM_2020_AR": _o(35, 115, "p35: INDEPENDENT AUDITOR'S REPORT (rule)", "p116: Value Added (OCR heading); five-year summary and proxy form follow",
                           "OCR headings for value added and five-year summary not matched"),
}
# flagged by the rule, reviewed, boundaries kept
REVIEWED_OK = {
    "BUACEMENT_2023_AR": "'CORPORATE GOVERNANCE' is a navigation tab on alternate pages, not a section heading",
    "ABCTRANS_2025_FS": "notes pages carry no running header; p42 heading is a note; ends at 'Other National Disclosures'",
    "BETAGLAS_2020_AR": "p43: EY letterhead starts the auditor's report; notes headings follow a running header; ends before p111 'Value Added Statement'",
    "CUTIX_2020_AR": "notes headed 'NOTE TO THE FINANCIAL STATEMENT' (singular, not matched); ends before p83 'OTHER NATIONAL DISCLOSURES'",
    "HBMNG_2020_FS": "notes headings carry a company-name prefix; ends before p69 'Other National Disclosures'",
    **{d: "notes pages carry no running header; the range ends at a post-statement heading or the document end"
       for d in ("BETAGLAS_2023_AR", "CAP_2025_AR", "DANGCEM_2024_AR", "DANGCEM_2025_AR", "ENAMELWA_2025_AR", "FTNCOCOA_2025_FS",
                 "HBMNG_2023_FS", "IMG_2025_AR", "MECURE_2025_AR", "MORISON_2025_FS", "NESTLE_2025_AR", "OANDO_2025_FS",
                 "SEPLAT_2025_IAR", "TRANSCORP_2025_FS", "UNIONDICON_2025_FS")},
}


def read_pages():
    """{doc: {page: [first 6 block texts (parents, in order)]}} and doc metadata."""
    pages, meta = {}, {}
    with open(PARA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["piece"] not in ("", "1"):
                continue
            d = pages.setdefault(r["doc"], {})
            lst = d.setdefault(int(r["page"]), [])
            if len(lst) < 6:
                lst.append(r["text"])
            meta[r["doc"]] = r["doc_type"]
    return pages, meta


def heads(blocks):
    return [b for b in blocks if len(b.split()) <= 20]


def tag_doc(doc, typ, pg, npages):
    ev = {}  # page -> list of (kind, heading)
    post, narr = {}, {}
    for p in sorted(pg):
        hs = heads(pg[p])
        if any(CONTENTS.match(h) for h in hs):
            continue
        found = [(k, h) for h in hs for k, rx in EVID.items() if rx.match(h)]
        if len(found) >= 4 or any(PAGENUM.search(h) for _, h in found):
            continue
        if found:
            ev[p] = found
        for h in hs:
            if POST.match(h):
                post.setdefault(p, h)
            if NARR.match(h):
                narr.setdefault(p, h)
    a_s = [p for p in ev if any(k in "AS" for k, _ in ev[p])]
    row = {"doc": doc, "doc_type": typ, "pages": npages}
    if not a_s:
        row.update({"fs_start": "", "fs_end": "", "method": "rule", "start_evidence": "", "end_evidence": "",
                    "flag": "" if typ in ("SR", "SRX") else "unsure",
                    "flag_reason": "no FS section (sustainability document)" if typ in ("SR", "SRX") else "no auditor's report or primary-statement heading found"})
        return row
    start = min(a_s)
    last = max(ev)
    later_post = [p for p in post if p > last]
    end = min(later_post) - 1 if later_post else npages
    first = lambda k: min([p for p in ev if any(x == k for x, _ in ev[p])], default="")
    sh = next(h for k, h in ev[start] if k in "AS")
    row.update({"fs_start": start, "fs_end": end, "method": "rule",
                "start_evidence": f"p{start}: {sh}",
                "end_evidence": (f"p{min(later_post)}: next section '{post[min(later_post)]}'" if later_post else "document end")
                + f"; last FS heading p{last}: {ev[last][0][1]}",
                "auditor_report_page": first("A"), "first_statement_page": first("S"), "first_notes_page": first("N"),
                "last_evidence_page": last})
    reasons = []
    if typ in ("AR", "IAR") and (end - start + 1) / npages < 0.15:
        reasons.append(f"range covers {(end - start + 1) / npages:.0%} of pages")
    if end - last > 10:
        reasons.append(f"{end - last} pages between last FS heading (p{last}) and end (p{end})")
    inside = [f"p{p}: {h}" for p, h in narr.items() if start <= p <= end]
    if inside:
        reasons.append("narrative heading inside range: " + "; ".join(inside[:3]))
    row["flag"] = "unsure" if reasons else ""
    row["flag_reason"] = "; ".join(reasons)
    return row


def tag():
    docs = {r["doc"]: r for r in csv.DictReader(open(I / "phase4_documents.csv", newline="", encoding="utf-8"))}
    pages, meta = read_pages()
    rows = []
    for doc, d in docs.items():
        r = tag_doc(doc, d["doc_type"], pages.get(doc, {}), int(d["pages"]))
        r.update({"firm": d["firm"], "year": d["year"]})
        if doc in OVERRIDES:
            o = OVERRIDES[doc]
            r.update({"fs_start": o["start"], "fs_end": o["end"], "method": "analyst review", "start_evidence": o["start_evidence"],
                      "end_evidence": o["end_evidence"], "flag": o.get("flag", "reviewed"),
                      "flag_reason": (r["flag_reason"] + " | " if r["flag_reason"] else "") + "analyst: " + o["note"]})
        elif doc in REVIEWED_OK and r["flag"] == "unsure":
            r.update({"method": "rule (analyst-reviewed)", "flag": "reviewed", "flag_reason": r["flag_reason"] + " | analyst: kept; " + REVIEWED_OK[doc]})
        rows.append(r)
    cols = ["doc", "firm", "year", "doc_type", "pages", "fs_start", "fs_end", "method", "start_evidence", "end_evidence",
            "auditor_report_page", "first_statement_page", "first_notes_page", "last_evidence_page", "flag", "flag_reason"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows({c: r.get(c, "") for c in cols} for r in rows)
    print("docs", len(rows), "| with FS range", sum(r["fs_start"] != "" for r in rows), "| flagged", sum(r["flag"] == "unsure" for r in rows),
          "| analyst-reviewed", sum(r["method"] == "analyst review" for r in rows))
    for r in rows:
        if r["flag"]:
            print(f"  {r['doc']:<20} {r['fs_start']}-{r['fs_end']}/{r['pages']} [{r['method']}] {r['flag']}: {r['flag_reason'][:180]}")


def headings(doc, a=1, b=10 ** 6):
    pages, _ = read_pages()
    for p in sorted(pages[doc]):
        if a <= p <= b:
            print(p, " | ".join(h[:60] for h in heads(pages[doc][p])[:4]))


def apply():
    """Add `section` to paragraphs.csv from section_tags.csv (rewrite in place via a temp file)."""
    tags = {r["doc"]: r for r in csv.DictReader(open(OUT, newline="", encoding="utf-8"))}
    tmp = PARA.with_suffix(".tmp")
    n = {"narrative": 0, "financial_statements": 0}
    with open(PARA, newline="", encoding="utf-8") as fi, open(tmp, "w", newline="", encoding="utf-8") as fo:
        rd = csv.DictReader(fi)
        cols = [c for c in rd.fieldnames if c != "section"] + ["section"]
        w = csv.DictWriter(fo, cols); w.writeheader()
        for r in rd:
            t = tags[r["doc"]]
            fs = t["fs_start"] != "" and int(t["fs_start"]) <= int(r["page"]) <= int(t["fs_end"])
            r["section"] = "financial_statements" if fs else "narrative"
            n[r["section"]] += 1
            w.writerow({c: r.get(c, "") for c in cols})
    tmp.replace(PARA)
    print(n)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "tag":
        tag()
    elif cmd == "headings":
        headings(sys.argv[2], *(int(x) for x in sys.argv[3:5]))
    elif cmd == "apply":
        apply()
