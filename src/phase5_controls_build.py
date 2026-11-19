"""Phase 5: build data/interim/controls_firm_year.csv from analyst-confirmed values (A22), 2026-11-18.

Every value below was taken from data/interim/controls_candidates.csv (rule hits, src/phase5_controls.py) or, where the
rule failed or was ambiguous, read by the analyst on the page text or page image (method 'analyst', with the reason).
Values whose note contains 'flag' are listed for the owner to check.

usage: phase5_controls_build.py
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

from phase5_controls import I, sample

# total assets: doc -> (value, unit 'k' = thousands of naira, 'M' = naira million, page, method, note)
TA = {
    "ACADEMY_2020_AR": (2617764, "k", 24, "rule", ""), "ACADEMY_2025_AR": (3106287, "k", 39, "rule", ""),
    "ALEX_2020_AR": (2566564, "k", 24, "analyst", "'Total equity and liabilities' (OCR page; no 'Total assets' line)"),
    "ALEX_2024_FS": (4082372, "k", 14, "analyst", "'Total equity and liabilities' (OCR page)"),
    "ARADEL_2021_AR": (377433169, "k", 49, "analyst", "unit N'000 read on the page image"),
    "ARADEL_2024_AR": (1749835623, "k", 77, "analyst", "FY2024 report's own statement, p77 (word positions); Phase 7 verified (earlier taken from the FY2025 comparative, same value)"),
    "ARADEL_2025_AR": (9896139369, "k", 23, "analyst", "N'000 statement (page image); the report also has a US$'000 statement"),
    "BETAGLAS_2020_AR": (53963634, "k", 49, "rule", ""), "BETAGLAS_2023_AR": (106851898, "k", 47, "analyst", "word positions"),
    "BUACEMENT_2020_AR": (766302578, "k", 31, "rule", ""), "BUACEMENT_2021_AR": (728507473, "k", 66, "rule", ""),
    "BUACEMENT_2022_AR": (874011884, "k", 77, "rule", ""), "BUACEMENT_2023_AR": (1215686377, "k", 87, "rule", ""),
    "BUACEMENT_2024_AR": (1570351865, "k", 84, "rule", ""), "BUACEMENT_2025_AR": (1856127006, "k", 45, "rule", ""),
    "BUAFOODS_2022_AR": (607224625, "k", 121, "rule", ""), "BUAFOODS_2024_AR": (1095504241, "k", 23, "rule", ""),
    "CUTIX_2020_AR": (3627990, "k", 55, "rule", ""), "CUTIX_2025_FS": (8691668, "k", 42, "rule", ""),
    "DANGCEM_2020_AR": (2022451, "M", 163, "rule", "N million"), "DANGCEM_2022_AR": (2615655, "M", 112, "rule", "N million"),
    "DANGCEM_2023_AR": (3938725, "M", 112, "rule", "N million"), "DANGCEM_2024_AR": (6403238, "M", 153, "rule", "N million"),
    "DANGCEM_2025_AR": (6040727, "M", 123, "rule", "N million"),
    "DANGSUGAR_2020_AR": (278032389, "k", 132, "rule", ""), "DANGSUGAR_2025_FS": (965925567, "k", 31, "rule", ""),
    "ELLAHLAKES_2020_FS": (5630878, "k", 12, "rule", "OCR page"),
    "ELLAHLAKES_2024_FS": (24551842, "k", 12, "analyst", "read on the page image"),
    "FIDSON_2020_AR": (27242484, "k", 26, "analyst", "word positions (OCR page)"), "FIDSON_2025_AR": (80286939, "k", 21, "rule", ""),
    "GEREGU_2022_AR": (174030404, "k", 31, "rule", ""),
    "GEREGU_2024_AR": (243470423, "k", 52, "rule", "OCR; Phase 7 verified on the page image (72,669,749 + 170,800,674)"),
    "GUINNESS_2020_AR": (144145581, "k", 78, "rule", ""), "GUINNESS_2021_AR": (169406525, "k", 80, "rule", ""),
    "GUINNESS_2022_AR": (215660208, "k", 90, "rule", ""), "GUINNESS_2023_AR": (241748144, "k", 82, "rule", ""),
    "GUINNESS_2024_AR": (226130077, "k", 82, "rule", ""), "GUINNESS_2025_AR": (245176709, "k", 86, "rule", ""),
    "HBMNG_2020_FS": (507213975, "k", 16, "rule", ""), "HBMNG_2023_FS": (681371572, "k", 23, "rule", ""),
    "HONYFLOUR_2020_AR": (142261292, "k", 58, "rule", ""), "HONYFLOUR_2025_FS": (167446235, "k", 31, "rule", ""),
    "JAPAULGOLD_2021_FS": (13089217, "k", 12, "analyst", "no 'Total assets' line: non-current 9,241,851 + current 3,847,366 (page image)"),
    "JAPAULGOLD_2025_FS": (38046674, "k", 27, "analyst", "no 'Total assets' line: non-current 21,801,480 + current 16,245,194 (page image)"),
    "LIVESTOCK_2020_AR": (6474140, "k", 50, "rule", ""), "LIVESTOCK_2025_AR": (10136484, "k", 61, "rule", ""),
    "MAYBAKER_2020_AR": (14352163, "k", 40, "rule", ""), "MAYBAKER_2025_FS": (25615432, "k", 16, "rule", ""),
    "NB_2020_AR": (445857202, "k", 36, "rule", ""), "NB_2025_AR": (1066117729, "k", 73, "rule", ""),
    "NEIMETH_2020_AR": (6441360, "k", 75, "rule", ""), "NEIMETH_2025_FS": (14014101, "k", 19, "rule", ""),
    "NESTLE_2020_AR": (246184996, "k", 51, "analyst", "word positions"), "NESTLE_2025_AR": (846159936, "k", 56, "rule", ""),
    "NNFM_2025_AR": (30548937, "k", 39, "rule", ""),
    "OKOMUOIL_2020_AR": (55011848, "k", 32, "rule", ""),
    "OKOMUOIL_2021_AR": (65772444, "k", 38, "analyst", "FY2021 report's own statement, p38 (spaced digits in text layer); Phase 7 verified (same value as the FY2022 comparative)"),
    "OKOMUOIL_2022_AR": (72498290, "k", 37, "rule", ""), "OKOMUOIL_2023_AR": (95100383, "k", 37, "rule", ""),
    "OKOMUOIL_2024_AR": (117037938, "k", 44, "analyst", "page image: the rule took the 2023 column (95,100,383); the 2024 column is shaded"),
    "SEPLAT_2020_AR": (1310837, "M", 153, "analyst", "first column, N million (the report also presents US$'000)"),
    "SEPLAT_2025_IAR": (8729381, "M", 171, "analyst", "first column, N million (the report also presents US$'000)"),
    "TRANSPOWER_2020_FS": (171910325, "k", 13, "rule", ""), "TRANSPOWER_2024_AR": (396782267, "k", 36, "rule", ""),
    "TRANSPOWER_2025_AR": (563478957, "k", 33, "analyst", "word positions; its comparative equals the FY2024 value"),
    "UNILEVER_2020_AR": (91517538, "k", 70, "rule", ""), "UNILEVER_2025_AR": (180179325, "k", 77, "analyst", "word positions (OCR page)"),
    "VITAFOAM_2020_AR": (21635766, "k", 40, "rule", ""),
    "VITAFOAM_2025_FS": (65275389, "k", 57, "analyst", "Phase 7 correction (A26): group statement of financial position, p57 page image (17,176,064 + 48,099,325); the earlier value 43,693,181 was the five-year summary's 'total assets' net of current liabilities"),
}
# auditor: firm_year -> (Big Four 1/0, auditor, page, method)
AUD = {
    "ACADEMY_2020": (1, "Ernst & Young", 9, "analyst: directors' report"), "ACADEMY_2025": (1, "EY", 34, "rule"),
    "ALEX_2020": (0, "Madu, Onyekwena & Co", 17, "analyst"), "ALEX_2024": (0, "Madu, Onyekwena & Co", 4, "analyst"),
    "ARADEL_2021": (1, "Deloitte", 45, "rule"), "ARADEL_2024": (1, "Deloitte", 69, "rule"), "ARADEL_2025": (1, "Deloitte", 18, "rule"),
    "BETAGLAS_2020": (1, "EY", 43, "rule"), "BETAGLAS_2023": (1, "EY", 41, "rule"),
    "BUACEMENT_2020": (1, "PricewaterhouseCoopers", 23, "analyst: directors' report"),
    "BUACEMENT_2021": (1, "PricewaterhouseCoopers", 49, "analyst: directors' report"),
    "BUACEMENT_2022": (1, "PricewaterhouseCoopers", 33, "analyst: corporate information"),
    "BUACEMENT_2023": (1, "PricewaterhouseCoopers", 66, "analyst: directors' report"),
    "BUACEMENT_2024": (1, "PwC", 77, "rule"), "BUACEMENT_2025": (1, "PricewaterhouseCoopers", 34, "analyst: directors' report"),
    "BUAFOODS_2022": (1, "PricewaterhouseCoopers", 112, "analyst: audit committee report"), "BUAFOODS_2024": (1, "PwC", 18, "rule"),
    "CUTIX_2020": (0, "ANOC Professional Services", 42, "analyst"), "CUTIX_2025": (0, "Ngozi Monica Okonkwo & Co", 20, "analyst"),
    "DANGCEM_2020": (1, "KPMG", 160, "rule"), "DANGCEM_2022": (1, "KPMG", 109, "rule"), "DANGCEM_2023": (1, "KPMG", 107, "rule"),
    "DANGCEM_2024": (1, "KPMG", 144, "rule"), "DANGCEM_2025": (1, "KPMG", 115, "rule"),
    "DANGSUGAR_2020": (1, "PwC", 126, "rule"), "DANGSUGAR_2025": (1, "PwC", 26, "rule"),
    "ELLAHLAKES_2020": (0, "Olabode Akande & Co", 6, "analyst"), "ELLAHLAKES_2024": (0, "Olabode Akande & Co", 6, "analyst"),
    "FIDSON_2020": (1, "Deloitte", 22, "rule"), "FIDSON_2025": (1, "Deloitte & Touche", 12, "analyst: directors' report"),
    "GEREGU_2022": (1, "PricewaterhouseCoopers", 21, "analyst: directors' report"), "GEREGU_2024": (1, "PwC", 50, "rule"),
    "GUINNESS_2020": (1, "PwC", 73, "rule"), "GUINNESS_2021": (1, "PwC", 78, "rule"), "GUINNESS_2022": (1, "PwC", 84, "rule"),
    "GUINNESS_2023": (1, "PwC", 76, "rule"), "GUINNESS_2024": (1, "PwC", 74, "rule"), "GUINNESS_2025": (1, "PwC", 78, "rule"),
    "HBMNG_2020": (1, "KPMG", 14, "rule"), "HBMNG_2023": (1, "EY", 17, "rule"),
    "HONYFLOUR_2020": (0, "Baker Tilly", 52, "analyst"), "HONYFLOUR_2025": (1, "Ernst & Young", 18, "analyst: directors' report"),
    "JAPAULGOLD_2021": (0, "PKF (inferred)", 8, "analyst: no Big Four name anywhere in the file (Phase 7); auditor identity inferred from letterhead tagline, signature page missing"),
    "JAPAULGOLD_2025": (0, "SIAO Partners", 79, "analyst"),
    "LIVESTOCK_2020": (1, "Ernst & Young", 10, "analyst: EY resigned with effect from 31 March 2021, after the FY2020 audit"),
    "LIVESTOCK_2025": (1, "KPMG", 54, "rule"),
    "MAYBAKER_2020": (0, "PKF Professional Services", 20, "analyst"), "MAYBAKER_2025": (0, "Grant Thornton", 3, "analyst"),
    "NB_2020": (1, "Deloitte & Touche", 24, "analyst: directors' report"), "NB_2025": (1, "KPMG", 63, "rule"),
    "NEIMETH_2020": (0, "PKF Professional Services", 60, "analyst"), "NEIMETH_2025": (0, "BDO Professional Services", 9, "analyst"),
    "NESTLE_2020": (1, "EY", 46, "rule"), "NESTLE_2025": (1, "EY", 54, "rule"), "NNFM_2025": (1, "KPMG", 34, "rule"),
    "OKOMUOIL_2020": (0, "Crowe Dafinone", 20, "analyst"), "OKOMUOIL_2021": (1, "EY", 33, "rule"),
    "OKOMUOIL_2022": (1, "EY", 33, "rule"), "OKOMUOIL_2023": (1, "EY", 32, "rule"), "OKOMUOIL_2024": (1, "EY", 39, "rule"),
    "SEPLAT_2020": (1, "PwC", 150, "rule"), "SEPLAT_2025": (1, "PricewaterhouseCoopers", 109, "analyst: directors' report"),
    "TRANSPOWER_2020": (1, "Deloitte", 9, "rule"), "TRANSPOWER_2024": (1, "Deloitte", 29, "rule"),
    "TRANSPOWER_2025": (1, "Deloitte & Touche", 9, "analyst: directors' report"),
    "UNILEVER_2020": (1, "KPMG", 64, "rule"), "UNILEVER_2025": (0, "Forvis Mazars", 67, "analyst"),
    "VITAFOAM_2020": (1, "Deloitte", 35, "rule"), "VITAFOAM_2025": (1, "PwC", 52, "rule"),
}
# foreign parent: firm -> {year or 'all': (largest foreign holding %, holder, evidence)}
FP = {
    "GUINNESS": {"all": (58.02, "Diageo plc (UK) via Guinness Overseas Ltd 50.18% + Atalantaf Ltd 7.84%", "directors' report, substantial interests"),
                 2025: (70.86, "Tolaram Group (headquartered in Singapore) via N-Seven Nigeria Ltd", "p14/p19: 70.86% after the takeover offer; p9 'ultimate Parent Company Tolaram Group'; p45 Singapore headquarters (Phase 7 verified)")},
    "NB": {2020: (56.0, "Heineken N.V. (Netherlands)", "p15: 'subsidiary of Heineken N.V. ... approximately 56%'"),
           2025: (72.90, "Heineken Group", "p27: combined holding 72.90%")},
    "NESTLE": {2020: (66.50, "Nestle S.A. (Switzerland)", "p34, p116"), 2025: (70.81, "Societe des Produits Nestle S.A.", "p33")},
    "UNILEVER": {2025: (75.97, "Unilever Overseas Holdings B.V.", "p80"),
                 2020: (75.97, "Unilever Overseas Holdings B.V.", "FY2020 p133 shareholder table: 57.81% + 18.16% (Phase 7 verified)")},
    "HBMNG": {"all": (83.81, "Holcim via AIC UK 27.77% + CariCement BV 56.04%", "p4 directors' report")},
    "BETAGLAS": {"all": (61.9, "Frigoglass S.A.I.C. (Greece) via Frigoglass Industries Nigeria Ltd",
                         "p53 / p51: the Nigerian parent holds 61.9%; ultimate controlling party abroad; flag (indirect)")},
    "OKOMUOIL": {"all": (62.94, "Socfinaf S.A. (Luxembourg)", "shareholding section (62.69% in FY2020)")},
    "SEPLAT": {2020: (20.46, "Maurel & Prom (France) via MPI", "FY2020 p142 substantial interests: MPI 20.46% (Phase 7 verified)"),
               2025: (0.0, "none >= 20% at year-end: Maurel & Prom's 20.07% passed to Heirs Group on 31 Dec 2025",
                      "Phase 7b resolved: FY2025 IAR p107 substantial interests at 31 Dec 2025: Heirs Group (Heirs Energies & "
                      "Heirs Holdings) 20.07%, Petrolin Group 13.50%, Sustainable Capital 10.09%; p107 note 2: Heirs acquired "
                      "the 120,400,000 M&P shares on 31 Dec 2025, UBO Tony Elumelu. Heirs treated as Nigerian (Lagos-based "
                      "group; domicile not stated on the page, analyst). No foreign holder >= 20% at year-end")},
}


def foreign(firm, year):
    d = FP.get(firm, {})
    v = d.get(year) or d.get("all")
    return v or (0.0, "no foreign parent or substantial foreign holder identified", "analyst review of parent and shareholding statements")


def main():
    firms, docs = sample()
    fy = defaultdict(list)
    for d in docs:
        fy[(d["firm"], int(d["year"]))].append(d)
    rows = []
    for (firm, year), ds in sorted(fy.items()):
        main_docs = [d for d in ds if d["doc_type"] in ("AR", "IAR", "FS")]
        doc = (main_docs or ds)[0]["doc"]
        excluded = doc == "NNFM_2020_AR"  # A23
        ta = TA.get(doc)
        assets = ta[0] * (1e6 if ta[1] == "M" else 1e3) if ta else None
        aud = AUD.get(f"{firm}_{year}")
        fp = foreign(firm, year)
        flags = [("A23 excluded (wrong issuer)" if excluded else ""),
                 ("total assets: " + ta[4]) if ta and "flag" in ta[4] else "",
                 ("auditor: " + aud[3]) if aud and "flag" in aud[3] else "",
                 ("foreign parent: " + fp[2]) if "flag" in fp[2] else ""]
        rows.append({"firm": firm, "year": year, "doc": doc, "excluded_A23": int(excluded),
                     "total_assets_ngn": "" if assets is None or excluded else f"{assets:.0f}",
                     "log_total_assets": "" if assets is None or excluded else round(math.log(assets), 4),
                     "ta_page": ta[2] if ta else "", "ta_method": ta[3] if ta else "", "ta_note": ta[4] if ta else "missing",
                     "big4": "" if aud is None or excluded else aud[0], "auditor": aud[1] if aud else "",
                     "auditor_page": aud[2] if aud else "", "auditor_method": aud[3] if aud else "missing",
                     "assurance": int(firm == "DANGCEM"),
                     "assurance_evidence": "independent limited assurance report on selected sustainability information (every year held)"
                                           if firm == "DANGCEM" else "no hit (rule, plus analyst check of likely cases)",
                     "foreign_share": fp[0], "foreign_parent_50": int(fp[0] >= 50), "foreign_parent_20": int(fp[0] >= 20),
                     "foreign_holder": fp[1], "foreign_evidence": fp[2], "flag": "; ".join(x for x in flags if x)})
    with open(I / "controls_firm_year.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
    miss = [(r["firm"], r["year"]) for r in rows if not r["excluded_A23"] and (r["log_total_assets"] == "" or r["big4"] == "")]
    print("firm-years", len(rows), "| missing", miss, "| flagged", sum(bool(r["flag"]) for r in rows))


if __name__ == "__main__":
    main()
