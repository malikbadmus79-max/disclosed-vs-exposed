"""Phase 0: build the provisional census frame from the owner-supplied NGX equities price list (06 Nov 2026).

Inputs: data/raw/manual/ngx/ngx_equities_price_list_2026-11-06.csv (146 tickers; no names or sectors).
Output: data/interim/ngx_census_frame.csv

Sources of each assignment:
- NGX's industry-sector page (doclib.ngxgroup.com/issuers/listing-your-company/industry-sector) returned a
  SharePoint error on 2026-11-07, so NO sector comes from NGX. All sector labels are provisional.
- physical_ops for the 14 listed pilot issuers is based on their own reports (files in this project).
- Every other assignment is a provisional analyst identification of the ticker, NOT verified; Phase 1 must
  check each against the issuer's own annual report. Tickers not identified with confidence are "unresolved".
- Removed instruments are those named as non-operating in data/raw/manual/ngx/SOURCE.txt.

physical_ops classes:
  point        physical operations in Nigeria, mainly point sites (plants, breweries, factories, plantations, power plants)
  dispersed    physical operations mainly as dispersed assets (oil and gas licences, retail fuel networks,
               telecom networks, construction project sites)
  borderline   services with physical sites (hotels, aviation handling, logistics, hospitals, restaurants,
               real estate development, conglomerates/holding companies with operating subsidiaries)
  non_physical financial services, insurance, ICT/software, media and other services with no significant sites
  unresolved   issuer not identified with confidence
  removed      fund, REIT or other non-operating instrument
"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "manual" / "ngx" / "ngx_equities_price_list_2026-11-06.csv"
OUT = ROOT / "data" / "interim" / "ngx_census_frame.csv"

PROV = "analyst identification; not verified — confirm in Phase 2 from a primary source"
FLAG_MEANING = "not verified (no legend found in NGX weekly reports or price-list sources checked 2026-11-07)"
RENAME_SOURCES = ("NGX Regulation Market Bulletin NGXREG/IRD/MB76/26/07/09, 09 July 2026, 'Lafarge Africa Plc – Change of "
                  "Name to HBM Nigeria Plc' (doclib.ngxgroup.com); Nairametrics, 13 July 2026")
REMOVED_REASON = "listed as a non-operating issuer (fund/REIT/ETF-like) in data/raw/manual/ngx/SOURCE.txt"
PILOT = {  # ticker: (file in this project supporting physical_ops)
    "DANGCEM": "data/raw/pilot_reports/dangote_cement/2025_AR.pdf",
    "BUACEMENT": "data/raw/pilot_reports/bua_cement/2025_AR.pdf",
    "GUINNESS": "data/raw/pilot_reports/guinness_nigeria/2025_AR.pdf",
    "OKOMUOIL": "data/raw/pilot_reports/okomu_oil/2024_SR.pdf",
    "PRESCO": "data/raw/pilot_reports/presco/2025_AR.pdf",
    "BETAGLAS": "data/raw/pilot_reports/beta_glass/2023_AR.pdf",
    "INTBREW": "data/raw/pilot_reports/international_breweries/2023_FS.pdf",
    "CADBURY": "data/raw/pilot_reports/cadbury_nigeria/2025_FS.pdf",
    "MTNN": "data/raw/manual/mtn/MTN-Nigeria-2025-Annual-Report.pdf",
    "NESTLE": "data/raw/manual/nestle/Nestle_Nigeria_2025_Annual_Report.pdf",
    "UNILEVER": "data/raw/manual/unilever/Unilever_Nigeria_2025_Annual_Report.pdf",
    "NB": "data/raw/manual/nigerian_breweries/Nigerian_Breweries_2025_Annual_Report.pdf",
    "SEPLAT": "data/raw/manual/seplat/Seplat_2025_Integrated_Annual_Report.pdf",
    "HBMNG": "data/raw/pilot_reports/lafarge_africa/2023_FS.pdf (as Lafarge Africa Plc)",
}
# ticker: (issuer as identified, provisional NGX sector, physical_ops, note)
T = {
    "ABBEYBANK": ("Abbey Mortgage Bank", "Financial Services", "non_physical", ""),
    "ABCTRANS": ("Associated Bus Company (ABC Transport)", "Services", "borderline", "road transport network"),
    "ACADEMY": ("Academy Press", "Industrial Goods", "point", "printing plant"),
    "ACCESSCORP": ("Access Holdings", "Financial Services", "non_physical", ""),
    "AFRINSURE": ("", "", "unresolved", ""),
    "AFRIPRUD": ("Afriprudential", "Financial Services", "non_physical", ""),
    "AFROMEDIA": ("Afromedia", "Services", "non_physical", "outdoor advertising"),
    "AIICO": ("AIICO Insurance", "Financial Services", "non_physical", ""),
    "AIRTELAFRI": ("Airtel Africa", "ICT", "dispersed", "telecom network; operations in several countries"),
    "ALEX": ("Aluminium Extrusion Industries", "Industrial Goods", "point", ""),
    "ARADEL": ("Aradel Holdings", "Oil and Gas", "dispersed", "upstream licences"),
    "AUSTINLAZ": ("Austin Laz & Company", "Industrial Goods", "point", ""),
    "AVACAP": ("", "", "unresolved", ""),
    "AVAIF": ("", "", "removed", ""),
    "BAPLC": ("", "", "unresolved", ""),
    "BERGER": ("Berger Paints Nigeria", "Industrial Goods", "point", ""),
    "BETAGLAS": ("Beta Glass", "Industrial Goods", "point", ""),
    "BUACEMENT": ("BUA Cement", "Industrial Goods", "point", ""),
    "BUAFOODS": ("BUA Foods", "Consumer Goods", "point", ""),
    "CADBURY": ("Cadbury Nigeria", "Consumer Goods", "point", ""),
    "CAP": ("Chemical and Allied Products", "Industrial Goods", "point", "paints"),
    "CAVERTON": ("Caverton Offshore Support Group", "Services", "borderline", "aviation and marine services"),
    "CHAMPION": ("Champion Breweries", "Consumer Goods", "point", ""),
    "CHAMS": ("Chams", "ICT", "non_physical", ""),
    "CHELLARAM": ("Chellarams", "Conglomerates", "borderline", ""),
    "CILEASING": ("C & I Leasing", "Services", "non_physical", "leasing"),
    "CMFC": ("", "", "unresolved", ""),
    "CNIF": ("", "", "removed", ""),
    "CONHALLPLC": ("Consolidated Hallmark Holdings", "Financial Services", "non_physical", ""),
    "CONOIL": ("Conoil", "Oil and Gas", "dispersed", "downstream fuel retail network and depots"),
    "CORNERST": ("Cornerstone Insurance", "Financial Services", "non_physical", ""),
    "CUSTODIAN": ("Custodian Investment", "Financial Services", "non_physical", ""),
    "CUTIX": ("Cutix", "Industrial Goods", "point", "cable manufacturer"),
    "CWG": ("CWG", "ICT", "non_physical", ""),
    "DAARCOMM": ("Daar Communications", "Services", "non_physical", "media"),
    "DANGCEM": ("Dangote Cement", "Industrial Goods", "point", "also has an unnamed depot network (dispersed)"),
    "DANGSUGAR": ("Dangote Sugar Refinery", "Consumer Goods", "point", ""),
    "EKOCORP": ("Ekocorp", "Healthcare", "borderline", "hospitals"),
    "ELLAHLAKES": ("Ellah Lakes", "Agriculture", "point", ""),
    "ENAMELWA": ("Nigerian Enamelware", "Consumer Goods", "point", ""),
    "ETERNA": ("Eterna", "Oil and Gas", "dispersed", "downstream fuel retail network"),
    "ETI": ("Ecobank Transnational", "Financial Services", "non_physical", ""),
    "ETRANZACT": ("eTranzact International", "ICT", "non_physical", ""),
    "EUNISELL": ("Eunisell Interlinked", "Industrial Goods", "point", ""),
    "FCMB": ("FCMB Group", "Financial Services", "non_physical", ""),
    "FIDELITYBK": ("Fidelity Bank", "Financial Services", "non_physical", ""),
    "FIDSON": ("Fidson Healthcare", "Healthcare", "point", "pharmaceutical manufacturing"),
    "FIRSTHOLDCO": ("FirstHoldCo", "Financial Services", "non_physical", ""),
    "FTGINSURE": ("", "", "unresolved", ""),
    "FTNCOCOA": ("FTN Cocoa Processors", "Agriculture", "point", ""),
    "GEREGU": ("Geregu Power", "Utilities", "point", "power plant"),
    "GOLDBREW": ("Golden Guinea Breweries", "Consumer Goods", "point", ""),
    "GTCO": ("Guaranty Trust Holding", "Financial Services", "non_physical", ""),
    "GUINEAINS": ("Guinea Insurance", "Financial Services", "non_physical", ""),
    "GUINNESS": ("Guinness Nigeria", "Consumer Goods", "point", ""),
    "HBMNG": ("HBM Nigeria Plc (formerly Lafarge Africa Plc; symbol changed from WAPCO)", "Industrial Goods", "point",
              "identity confirmed: " + "NGX market bulletin 09 July 2026; Nairametrics 13 July 2026"),
    "HMCALL": ("", "", "unresolved", ""),
    "HONYFLOUR": ("Honeywell Flour Mills", "Consumer Goods", "point", ""),
    "IKEJAHOTEL": ("Ikeja Hotel", "Services", "borderline", "hotels"),
    "IMG": ("Industrial and Medical Gases Nigeria", "Industrial Goods", "point", ""),
    "INFINITY": ("Infinity Trust Mortgage Bank", "Financial Services", "non_physical", ""),
    "INTBREW": ("International Breweries", "Consumer Goods", "point", ""),
    "INTENEGINS": ("International Energy Insurance", "Financial Services", "non_physical", ""),
    "JAIZBANK": ("Jaiz Bank", "Financial Services", "non_physical", ""),
    "JAPAULGOLD": ("Japaul Gold & Ventures", "Natural Resources", "point", "mining; sites not verified"),
    "JBERGER": ("Julius Berger Nigeria", "Construction/Real Estate", "dispersed", "construction project sites"),
    "JOHNHOLT": ("John Holt", "Conglomerates", "borderline", ""),
    "JULI": ("Juli", "Healthcare", "borderline", "pharmacy retail"),
    "LASACO": ("LASACO Assurance", "Financial Services", "non_physical", ""),
    "LEARNAFRCA": ("Learn Africa", "Services", "non_physical", "publishing"),
    "LEGENDINT": ("Legend Internet", "ICT", "non_physical", ""),
    "LINKASSURE": ("Linkage Assurance", "Financial Services", "non_physical", ""),
    "LIVESTOCK": ("Livestock Feeds", "Agriculture", "point", ""),
    "LIVINGTRUST": ("Living Trust Mortgage Bank", "Financial Services", "non_physical", ""),
    "MANSARD": ("AXA Mansard Insurance", "Financial Services", "non_physical", ""),
    "MAYBAKER": ("May & Baker Nigeria", "Healthcare", "point", "pharmaceutical manufacturing"),
    "MBENEFIT": ("Mutual Benefits Assurance", "Financial Services", "non_physical", ""),
    "MCNICHOLS": ("McNichols", "Consumer Goods", "point", ""),
    "MECURE": ("Mecure Industries", "Healthcare", "point", "pharmaceutical manufacturing"),
    "MEYER": ("Meyer", "Industrial Goods", "point", "paints"),
    "MOFIREIF": ("", "", "removed", ""),
    "MORISON": ("Morison Industries", "Healthcare", "point", "pharmaceutical manufacturing"),
    "MTNN": ("MTN Nigeria Communications", "ICT", "dispersed", "telecom network; also point sites (offices, data centre)"),
    "MULTITREX": ("Multi-Trex Integrated Foods", "Agriculture", "point", "operating status not verified"),
    "MULTIVERSE": ("Multiverse Mining and Exploration", "Natural Resources", "point", "mining; sites not verified"),
    "NAHCO": ("Nigerian Aviation Handling Company", "Services", "borderline", "airport ground handling"),
    "NASCON": ("NASCON Allied Industries", "Consumer Goods", "point", ""),
    "NB": ("Nigerian Breweries", "Consumer Goods", "point", ""),
    "NCR": ("NCR (Nigeria)", "ICT", "non_physical", ""),
    "NEIMETH": ("Neimeth International Pharmaceuticals", "Healthcare", "point", "pharmaceutical manufacturing"),
    "NEM": ("NEM Insurance", "Financial Services", "non_physical", ""),
    "NESTLE": ("Nestle Nigeria", "Consumer Goods", "point", ""),
    "NGXGROUP": ("Nigerian Exchange Group", "Financial Services", "non_physical", ""),
    "NIDF": ("", "", "removed", ""),
    "NNFM": ("Northern Nigeria Flour Mills", "Consumer Goods", "point", ""),
    "NPFMCRFBK": ("NPF Microfinance Bank", "Financial Services", "non_physical", ""),
    "NREIT": ("", "", "removed", ""),
    "NSLTECH": ("", "", "unresolved", ""),
    "OANDO": ("Oando", "Oil and Gas", "dispersed", "upstream licences"),
    "OKOMUOIL": ("Okomu Oil Palm", "Agriculture", "point", ""),
    "OMATEK": ("", "", "unresolved", "identity not verified"),
    "PHARMDEKO": ("Pharma-Deko", "Healthcare", "point", "pharmaceutical manufacturing"),
    "PREMPAINTS": ("Premier Paints", "Industrial Goods", "point", ""),
    "PRESCO": ("Presco", "Agriculture", "point", ""),
    "PRESTIGE": ("Prestige Assurance", "Financial Services", "non_physical", ""),
    "PZ": ("PZ Cussons Nigeria", "Consumer Goods", "point", ""),
    "REDSTAREX": ("Red Star Express", "Services", "borderline", "logistics"),
    "REGALINS": ("Regency Alliance Insurance", "Financial Services", "non_physical", ""),
    "RONCHESS": ("", "", "unresolved", ""),
    "ROYALEX": ("Royal Exchange", "Financial Services", "non_physical", ""),
    "RTBRISCOE": ("R.T. Briscoe", "Services", "borderline", "vehicle dealership"),
    "SCOA": ("SCOA Nigeria", "Conglomerates", "borderline", ""),
    "SEPLAT": ("Seplat Energy", "Oil and Gas", "dispersed", "licences; also point sites (gas plants, terminals)"),
    "SFSREIT": ("", "", "removed", ""),
    "SKYAVN": ("Skyway Aviation Handling Company", "Services", "borderline", "airport ground handling"),
    "SOVRENINS": ("Sovereign Trust Insurance", "Financial Services", "non_physical", ""),
    "STANBIC": ("Stanbic IBTC Holdings", "Financial Services", "non_physical", ""),
    "STERLINGNG": ("Sterling Financial Holdings", "Financial Services", "non_physical", ""),
    "SUNUASSUR": ("SUNU Assurances Nigeria", "Financial Services", "non_physical", ""),
    "TANTALIZER": ("Tantalizers", "Services", "borderline", "restaurants"),
    "THOMASWY": ("Thomas Wyatt Nigeria", "Industrial Goods", "point", ""),
    "TIP": ("The Initiates", "Services", "non_physical", ""),
    "TOTAL": ("TotalEnergies Marketing Nigeria", "Oil and Gas", "dispersed", "downstream fuel retail network and depots"),
    "TRANSCOHOT": ("Transcorp Hotels", "Services", "borderline", "hotels"),
    "TRANSCORP": ("Transnational Corporation", "Conglomerates", "borderline", "holding company with power and hotel subsidiaries"),
    "TRANSEXPR": ("Trans-Nationwide Express", "Services", "borderline", "logistics"),
    "TRANSPOWER": ("Transcorp Power", "Utilities", "point", "power plant"),
    "TRIPPLEG": ("Tripple Gee and Company", "Industrial Goods", "point", ""),
    "UACN": ("UAC of Nigeria", "Conglomerates", "borderline", ""),
    "UBA": ("United Bank for Africa", "Financial Services", "non_physical", ""),
    "UCAP": ("United Capital", "Financial Services", "non_physical", ""),
    "UHREIT": ("", "", "removed", ""),
    "UNILEVER": ("Unilever Nigeria", "Consumer Goods", "point", ""),
    "UNIONDICON": ("Union Dicon Salt", "Industrial Goods", "point", ""),
    "UNITYBNK": ("Unity Bank", "Financial Services", "non_physical", ""),
    "UNIVINSURE": ("Universal Insurance", "Financial Services", "non_physical", ""),
    "UPDC": ("UPDC", "Construction/Real Estate", "borderline", "property development"),
    "UPDCREIT": ("", "", "removed", ""),
    "UPL": ("University Press", "Services", "non_physical", "publishing"),
    "VERITASKAP": ("Veritas Kapital Assurance", "Financial Services", "non_physical", ""),
    "VFDGROUP": ("VFD Group", "Financial Services", "non_physical", ""),
    "VITAFOAM": ("Vitafoam Nigeria", "Consumer Goods", "point", ""),
    "WAPIC": ("Wapic Insurance", "Financial Services", "non_physical", ""),
    "WEMABANK": ("Wema Bank", "Financial Services", "non_physical", ""),
    "ZENITHBANK": ("Zenith Bank", "Financial Services", "non_physical", ""),
    "ZICHIS": ("", "", "unresolved", ""),
}

with SRC.open(newline="", encoding="utf-8") as f:
    listed = list(csv.DictReader(f))
tickers = [r["ticker"] for r in listed]
missing = [t for t in tickers if t not in T]
extra = [t for t in T if t not in tickers]
if missing or extra:
    raise SystemExit(f"ticker mismatch: missing={missing} extra={extra}")

rows = []
for r in listed:
    t = r["ticker"]
    issuer, sector, ops, note = T[t]
    if ops == "removed":
        src_ops, src_sector = REMOVED_REASON, ""
    elif ops == "unresolved":
        src_ops, src_sector = "issuer not identified with confidence", ""
    elif t in PILOT:
        src_ops, src_sector = f"issuer report: {PILOT[t]}", PROV
    else:
        src_ops, src_sector = PROV, PROV
    identity_source = RENAME_SOURCES if t == "HBMNG" else (f"issuer report: {PILOT[t]}" if t in PILOT else (PROV if issuer else ""))
    stratum = {"point": "main", "dispersed": "main", "borderline": "robustness_stratum"}.get(ops, "excluded")
    rows.append({"ticker": t, "board_flag": r["board_flag"],
                 "board_flag_meaning": FLAG_MEANING if r["board_flag"] else "",
                 "issuer_identified": issuer, "issuer_source": identity_source, "sector_provisional": sector,
                 "sector_source": src_sector, "physical_ops": ops, "physical_ops_source": src_ops,
                 "census_stratum": stratum,
                 "document_test": "passed (report in hand)" if t in PILOT else ("pending" if stratum != "excluded" else ""),
                 "note": note})

tmp = OUT.with_suffix(".csv.tmp")
with tmp.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, list(rows[0]))
    w.writeheader()
    w.writerows(rows)
tmp.replace(OUT)

c = Counter(r["physical_ops"] for r in rows)
print("total tickers", len(rows), dict(c))
print("strata:", dict(Counter(r["census_stratum"] for r in rows)))
frame = [r for r in rows if r["census_stratum"] == "main"]
print("main census:", len(frame), "| flagged in main:", [(r["ticker"], r["board_flag"]) for r in frame if r["board_flag"]])
print("document test in main:", dict(Counter(r["document_test"] for r in frame)))
print("sectors in core frame:", dict(Counter(r["sector_provisional"] for r in frame)))
print("removed:", [r["ticker"] for r in rows if r["physical_ops"] == "removed"])
print("unresolved:", [r["ticker"] for r in rows if r["physical_ops"] == "unresolved"])
print("borderline:", [r["ticker"] for r in rows if r["physical_ops"] == "borderline"])
print("dispersed:", [r["ticker"] for r in rows if r["physical_ops"] == "dispersed"])
print("board flags:", dict(Counter(r["board_flag"] for r in rows if r["board_flag"])))
print("pilot tickers present:", [t for t in PILOT if t in tickers], "| FLOURMILL present:", "FLOURMILL" in tickers)
