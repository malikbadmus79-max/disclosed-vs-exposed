"""Phase 4, step 3: build the two text dictionaries (design f4 and f5) as frozen JSON files. No corpus text is read and
nothing is counted here; the files are frozen (SHA-256 in docs/amendments.md) before any count.

config/dictionary_hazard.json  physical-risk hazard terms (f4, Y3): the 16 terms of the design (OD-11), unchanged,
                               with the matching rule of amendment A17
config/dictionary_sites.json   site-mention dictionary (f5, Y4/Y5): per firm and site, the town/estate names, facility
                               proper names and licence names, built from data/processed/facilities.csv (A17), with the
                               facility-context terms and the ambiguity rule of A17

usage: phase4_dictionaries.py          (writes both files and prints their SHA-256)
"""
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from wordfreq import zipf_frequency

ROOT = Path(__file__).resolve().parents[1]
FAC = ROOT / "data" / "processed" / "facilities.csv"
OUT_H = ROOT / "config" / "dictionary_hazard.json"
OUT_S = ROOT / "config" / "dictionary_sites.json"
FROZEN = "2026-11-17"

B0, B1 = r"(?<![A-Za-z0-9])", r"(?![A-Za-z0-9])"  # whole-word boundaries (letters and digits)


def words_pattern(term, plural=False):
    """Whole-word pattern; a space or hyphen in the term matches one or more spaces/hyphens; optional plural s/es."""
    body = r"[\s\-‐‑–]+".join(re.escape(w) for w in re.split(r"[\s\-]+", term))
    return B0 + body + (r"(?:e?s)?" if plural else "") + B1


# ------------------------------------------------------------------ hazard dictionary (f4, OD-11)
# term -> (hazard group, plural form allowed). The term list is the design's, in the design's order; nothing is added.
HAZARD = [
    ("flood", "flood", True), ("flooding", "flood", False), ("inundation", "flood", True), ("rainfall", "flood", True),
    ("storm", "storm", True), ("drought", "drought / water stress", True), ("water scarcity", "drought / water stress", False),
    ("water stress", "drought / water stress", False), ("heatwave", "heat", True),
    ("extreme temperature", "heat", True), ("extreme heat", "heat", False), ("erosion", "coastal / erosion / sea level", False),
    ("sea level", "coastal / erosion / sea level", True), ("coastal", "coastal / erosion / sea level", False),
    ("desertification", "drought / water stress", False), ("wildfire", "wildfire", True),
]
EXTRA_SPELLINGS = {"heatwave": ["heat wave"]}  # the two-word spelling of the same term (hyphen/space handled by the pattern)


def hazard_json():
    terms = []
    for t, g, pl in HAZARD:
        pats = [words_pattern(t, pl)] + [words_pattern(x, pl) for x in EXTRA_SPELLINGS.get(t, [])]
        terms.append({"term": t, "hazard_group": g, "plural_matched": pl, "patterns": pats})
    return {
        "name": "Physical-risk hazard dictionary (design f4; main outcomes Y3d, Y4d, Y4s, Y4r under A20)",
        "frozen_on": FROZEN,
        "source": "docs/design.md f4 and config/parameters.json text.physical_risk_dictionary (OD-11, decided 2026-11-07). "
                  "The design's 16 terms in the design's order, minus bare 'heat', plus 'extreme heat' (A20).",
        "amendment": "A17 (matching rule); A20 (OD-11 decided by a pre-set rule: 'heat' dropped, 'extreme heat' added)",
        "terms": terms,
        "matching_rule": {
            "case": "case-insensitive",
            "unit": "the paragraph (or split piece) text as stored in data/interim/paragraphs.csv",
            "boundaries": "whole words: the character before and after a match is not a letter or digit",
            "plurals": "regular plural -s/-es only, for count nouns (floods, storms, droughts, heatwaves, wildfires, "
                       "inundations, rainfalls, extreme temperatures, sea levels); no other inflection",
            "multi_word_terms": "a space in a term matches one or more spaces or hyphens (sea-level, water-stress); "
                                "'heatwave' also matches 'heat wave' and 'heat-wave'",
            "not_matched": "verb and adjective forms that are not in the list, e.g. 'flooded', 'floodplain', 'stormwater', "
                           "'water-stressed', 'heated', 'heating', 'eroded'. Recall is not measured (A20); adding any "
                           "form requires an amendment",
            "tag": "a paragraph is hazard-tagged if at least one term matches; Y3d = tagged / all scored narrative "
                   "paragraphs, with no climate filter (A20)",
        },
        "od11_bare_heat": "Decided by a pre-set rule without looking at any count (A20, 2026-11-17): bare 'heat' is dropped "
                          "(mostly process heat in kiln, furnace, brewery and power-plant reports, e.g. 'waste heat "
                          "recovery'); 'extreme heat' is added; 'heatwave' and 'extreme temperature' are kept; "
                          "'high temperature' is not added (mostly process language).",
        "precision_check": "A20: 100 tagged snippets checked by one external person; see docs/amendments.md",
        "regex_flavour": "Python re; apply with re.IGNORECASE",
    }


# ------------------------------------------------------------------ site dictionary (f5)
# Curated per site from facilities.csv (facility, location_as_written, geocode_place). kind: place = town, district or
# estate area; facility_name = proper name of the facility itself; licence = oil licence or field.
# Rule for inclusion: a term must be a proper name. Generic descriptions ("Head office", "Depots", "rubber factory")
# are never terms (f5: generic words are never used alone). Street names and P.O. boxes are not used.
P, N, L = "place", "facility_name", "licence"
SITES = {
    "F0001": [("Ikoyi", P)], "F0002": [("Obajana", P)], "F0003": [("Gboko", P)], "F0004": [("Ibese", P)],
    "F0005": [("Okpella", P)], "F0006": [("Itori", P)], "F0007": [("Apapa", P)], "F0008": [("Onne", P)], "F0009": [],
    "F0010": [("Victoria Island", P)], "F0011": [("Obu", P), ("Okpella", P)], "F0012": [("Kalambaina", P), ("Sokoto", P)],
    "F0013": [("Sokoto", P)], "F0014": [("Ososo", P)], "F0015": [],
    "F0016": [("Ogba", P)], "F0017": [("Ogba", P)], "F0018": [("Benin City", P), ("Oregbeni", P), ("Ikpoba Hill", P), ("Benin Brewery", N)],
    "F0019": [("Aba", P), ("Osisioma", P)],
    "F0020": [("Okomu", P), ("Okomu-Udo", P)], "F0021": [("Extension 1", N), ("Extension I", N)],
    "F0022": [("Extension 2", N), ("Extension II", N)], "F0023": [],
    "F0024": [("Obaretin", P)], "F0025": [("Cowan", P)], "F0026": [("Ologbo", P)], "F0027": [("ATO", P)], "F0028": [("Elele", P)],
    "F0029": [("Ubima", P)], "F0030": [("Sakponba", P)], "F0031": [],
    "F0032": [("Iddo", P)], "F0033": [("Agbara", P)], "F0034": [("Ughelli", P)],
    "F0035": [("Banana Island", P), ("Ikoyi", P)], "F0036": [],
    "F0037": [("Ikoyi", P)], "F0038": [("Ewekoro", P)], "F0039": [("Sagamu", P)], "F0040": [("Mfamosing", P)], "F0041": [("Ashaka", P)],
    "F0042": [("Ikeja", P)], "F0043": [],
    "F0044": [("Ikoyi", P)], "F0045": [("MTN Plaza", N), ("Ikoyi", P)], "F0046": [("Dabengwa", N)], "F0047": [], "F0048": [],
    "F0049": [("Ilupeju", P)], "F0050": [("Agbara", P)], "F0051": [("Flowergate", P)], "F0052": [("Abaji", P)],
    "F0053": [("Oregun", P)], "F0054": [("Oregun", P)], "F0055": [("Agbara", P)], "F0056": [],
    "F0057": [("Iganmu House", N), ("Iganmu", P)], "F0058": [("Lagos Brewery", N), ("Iganmu", P)], "F0059": [("Ibadan Brewery", N), ("Ibadan", P)],
    "F0060": [("Kudenda", P), ("Kaduna Brewery", N)], "F0061": [("Ogbor Hill", P), ("Obingwa", P), ("Aba", P)], "F0062": [("Aba Brewery", N), ("Aba", P)],
    "F0063": [("Ama Brewery", N), ("Amaeke", P), ("Ngwo", P)], "F0064": [("Awo-Omamma", P)], "F0065": [("Kakuri", P)],
    "F0066": [("Ota", P), ("Sango Ota", P)], "F0067": [("Ijebu-Ode", P), ("Imagbon", P)], "F0068": [("Onitsha", P)], "F0069": [("Makurdi", P)],
    "F0070": [("Iganmu", P)], "F0071": [("Ibadan", P)], "F0072": [("Benin City", P)], "F0073": [("Abuja", P), ("Idu", P)],
    "F0074": [("Kakuri", P), ("Kaduna", P)], "F0075": [("Port Harcourt", P), ("Woji", P)], "F0076": [("Enugu", P), ("Nsude", P)], "F0077": [("Aba", P)],
    "F0078": [("Seplat House", N), ("Victoria Island", P)], "F0079": [("Oben", P)], "F0080": [("Sapele", P)], "F0081": [("ANOH", N)],
    "F0082": [("Amukpe", P)], "F0083": [("Qua Iboe", N), ("QIT", N)], "F0084": [],
    "F0085": [("OML 4", L), ("OML 38", L), ("OML 41", L)], "F0086": [("OML 53", L), ("OML 56", L)], "F0087": [("OML 40", L)],
    "F0088": [("OML 67", L), ("OML 68", L), ("OML 70", L), ("OML 104", L)], "F0089": [("Yoho", N)],
    "F0090": [("Apapa", P)], "F0091": [("Numan", P)], "F0092": [("Nasarawa Sugar", N)], "F0093": [("Taraba Sugar", N)], "F0094": [("Adamawa Sugar", N)],
    "F0095": [("Magodo", P)], "F0096": [("Olodo", P), ("Monatan", P)],
    "F0097": [("Bull Plaza", N), ("Marina", P)], "F0098": [], "F0099": [],
    "F0100": [("Oregun", P)], "F0101": [],
    "F0102": [("Ikeja", P)], "F0103": [("Aba", P)], "F0104": [("Ikeja", P)], "F0105": [("Jos", P)], "F0106": [("Kano", P)],
    "F0107": [("Oregun", P)], "F0108": [("Oregun", P)], "F0109": [("Amawbia", P)], "F0110": [("Nnewi", P)],
    "F0111": [("Ikeja", P)], "F0112": [], "F0113": [("Ilupeju", P)], "F0114": [], "F0115": [],
    "F0116": [("Ikeja", P)], "F0117": [("Kano", P)], "F0118": [("Abuja", P)], "F0119": [("Abuja", P)], "F0120": [],
    "F0121": [("Oregun", P)], "F0122": [],
    "F0123": [("Golden Penny Place", N), ("Apapa", P)], "F0124": [("Apapa", P), ("Tin Can", P)], "F0125": [("Sagamu", P)], "F0126": [("Onitsha", P)],
    "F0127": [("Ikoyi", P)], "F0128": [("Transcorp Hilton", N), ("Abuja", P)], "F0129": [("Transcorp Hotels Port Harcourt", N), ("Port Harcourt", P)],
    "F0130": [("Afam", P)], "F0131": [],
    "F0132": [("Owerri", P), ("Uratta", P)], "F0133": [("Amuwo-Odofin", P)], "F0134": [("Eliozu", P)], "F0135": [("Jibowu", P)], "F0136": [],
    "F0137": [("Matori", P), ("Oshodi", P)],
    "F0138": [("Ikeja", P)], "F0139": [("Aba", P)], "F0140": [("Northern Rice and Oil Mill", N)],
    "F0141": [("Iganmu", P)], "F0142": [], "F0143": [("Ilupeju", P)],
    "F0144": [("Victoria Island", P)], "F0145": [("Ogbele", L)], "F0146": [("OML 17", L)], "F0147": [], "F0148": [("Ever Oil", N), ("Port Harcourt", P)],
    "F0149": [("Victoria Island", P)], "F0150": [("Apapa", P), ("Tin Can", P)], "F0151": [("Ikeja", P)],
    "F0152": [("BUA Foods Industrial Complex", N), ("Port Harcourt", P)], "F0153": [("BUA Sugar Refinery", N), ("Bundu", P), ("Port Harcourt", P)],
    "F0154": [("LASUCO", N), ("Lafiagi", P)], "F0155": [("Flour Mills Plants II", N), ("Port Harcourt", P)], "F0156": [("Sharada", P), ("Kano", P)],
    "F0157": [("Ogba", P)], "F0158": [], "F0159": [("Obanikoro", P)], "F0160": [("Ota", P)], "F0161": [("Oregun", P)], "F0162": [],
    "F0163": [("Kano", P)], "F0164": [("Eko Tower", N), ("Victoria Island", P)], "F0165": [], "F0166": [], "F0167": [],
    "F0168": [("Uyo", P)], "F0169": [], "F0170": [("Ikeja", P)], "F0171": [], "F0172": [("Umuahia", P)], "F0173": [],
    "F0174": [("Oshodi", P)], "F0175": [], "F0176": [("Japaul House", N), ("Agidingbi", P)], "F0177": [("Libeli", P)],
    "F0178": [("Debo Industrial Compound", N), ("Oshodi", P)], "F0179": [], "F0180": [("Warewa", P)], "F0181": [],
    "F0182": [("Abule Oshun", P)], "F0183": [], "F0184": [("Ikoyi", P)], "F0185": [("Ughelli", P)],
    "F0186": [("Ikeja", P)], "F0187": [], "F0188": [("Wings Complex", N), ("Victoria Island", P)],
    "F0189": [("OML 56", L), ("OML 13", L), ("OML 60", L), ("OML 61", L), ("OML 62", L), ("OML 63", L)],
    "F0190": [("Kwale", P), ("Okpai", P), ("Kwale IPP", N)],
    "F0191": [("Utako", P)], "F0192": [], "F0193": [("Banana Island", P)], "F0194": [], "F0195": [],
    "F0196": [("Benin City", P)], "F0197": [("Iguelaba", P)], "F0198": [("Adani", P)], "F0199": [("Ondo", P)],
    "F0200": [("Alagunten", P)], "F0201": [("Abuni", P)], "F0202": [("Arepo", P)], "F0203": [],
    "F0204": [("Kirikiri", P), ("Apapa", P)], "F0205": [], "F0206": [("Inyishi", P)], "F0207": [("Inyishi", P)], "F0208": [("Suleja", P)],
    "F0209": [("Ikoyi", P)], "F0210": [("Ibru Jetty", N), ("Ibafon", P)], "F0211": [], "F0212": [("JUHI-2", N), ("JUHI", N)],
    "F0213": [("Victoria Island", P)], "F0214": [("Ajaokuta", P), ("Itobe", P)],
}
SPELLINGS = {"Ota": ["Otta"], "Sagamu": ["Shagamu"], "Sango Ota": ["Sango-Otta", "Sango Otta"], "Port Harcourt": ["Portharcourt"],
             "Abule Oshun": ["Abule-Osun"]}
# Nigerian state names, the FCT, and state capitals / major cities (all occur as general geography in reports)
MAJOR = {"Lagos", "Abuja", "Kano", "Kaduna", "Ibadan", "Port Harcourt", "Enugu", "Aba", "Jos", "Onitsha", "Owerri", "Uyo",
         "Umuahia", "Benin City", "Makurdi", "Sokoto", "Ondo", "Warri", "Ikeja", "Apapa", "Victoria Island", "Ikoyi"}
# terms that are also another organisation, a person's name, an acronym or an ordinary word (analyst list)
OTHER_SENSE = {"Adani": "also the name of an Indian conglomerate", "ATO": "acronym in other uses", "Cowan": "a surname",
               "Marina": "an ordinary word (marina) and a Lagos street/district", "QIT": "acronym", "Tin Can": "ordinary words",
               "Extension 1": "ordinary phrase", "Extension I": "ordinary phrase", "Extension 2": "ordinary phrase",
               "Extension II": "ordinary phrase", "Kwale": "also a county in Kenya", "Numan": "also a personal name",
               "ANOH": "acronym", "JUHI": "acronym", "Yoho": "also a national park in Canada",
               "Nasarawa Sugar": "contains a state name", "Taraba Sugar": "contains a state name", "Adamawa Sugar": "contains a state name"}
# the firm's own name contains the site term: these phrases are removed from the text before site terms are matched
FIRM_NAME_PHRASES = {"OKOMUOIL": ["Okomu Oil Palm Company", "Okomu Oil Palm Plc", "Okomu Oil Palm Co", "Okomu Oil"],
                     "TRANSCORP": ["Transcorp Hotels Plc", "Transnational Corporation"],
                     "HBMNG": ["Ashaka Cement", "Ashaka Cem"]}
CONTEXT = ["plant", "factory", "factories", "facility", "facilities", "site", "mill", "brewery", "breweries", "malting",
           "refinery", "refineries", "depot", "terminal", "warehouse", "estate", "plantation", "farm", "quarry", "quarries",
           "mine", "mining", "flow station", "field", "operations", "operation", "office", "headquarters", "head office", "premises",
           "complex", "station", "power station", "tank farm", "jetty", "hotel", "distribution centre", "distribution center",
           "data centre", "data center", "works", "kiln", "project", "production", "manufacturing", "processing", "concession",
           "licence", "license", "location", "branch", "port"]
PLURAL_CONTEXT = {"plant", "facility", "site", "mill", "refinery", "depot", "terminal", "warehouse", "estate", "plantation",
                  "farm", "mine", "field", "office", "station", "tank farm", "jetty", "hotel", "distribution centre",
                  "distribution center", "data centre", "data center", "kiln", "project", "concession", "licence", "license",
                  "location", "branch", "port", "flow station", "power station"}


def term_pattern(term, kind):
    if kind == L and term.startswith("OML "):
        return B0 + r"OMLs?[\s\-]*" + re.escape(term.split()[1]) + r"(?![0-9])"
    return words_pattern(term)


def sites_json():
    rows = list(csv.DictReader(open(FAC, encoding="utf-8")))
    firms_of = defaultdict(set)
    for r in rows:
        for t, k in SITES[r["facility_id"]]:
            firms_of[t.lower()].add(r["ticker"])
    missing = {r["facility_id"] for r in rows} ^ set(SITES)
    assert not missing, missing
    flags_all = {}
    firms = {}
    for r in rows:
        terms = []
        for t, k in SITES[r["facility_id"]]:
            flags = []
            if len(firms_of[t.lower()]) >= 2:
                flags.append(f"shared: named for {len(firms_of[t.lower()])} firms ({', '.join(sorted(firms_of[t.lower()]))})")
            if t in MAJOR:
                flags.append("major place: a state, state capital or major city/district that occurs as general geography")
            if k != L and not re.search(r"[\s\-]", t) and zipf_frequency(t.lower(), "en") >= 3.0:  # single words only
                flags.append(f"common word (wordfreq zipf {zipf_frequency(t.lower(), 'en'):.1f} >= 3.0)")
            if t in OTHER_SENSE:
                flags.append("other sense: " + OTHER_SENSE[t])
            if any(t.lower() in ph.lower() for ph in FIRM_NAME_PHRASES.get(r["ticker"], [])):
                flags.append("firm-name collision: firm-name phrases removed before matching")
            amb = bool([f for f in flags if not f.startswith("firm-name")])
            rule = ("R2" if amb else "R1") if k == P else ("R3" if not amb else "R3+R2")
            if k == L:
                rule = "R3"
            pats = [term_pattern(t, k)] + [words_pattern(v) for v in SPELLINGS.get(t, [])]
            terms.append({"term": t, "kind": k, "spellings": SPELLINGS.get(t, []), "patterns": pats,
                          "case_sensitive": amb or k in (N, L) or t.isupper(), "ambiguity_flags": flags, "match_rule": rule})
            if flags:
                flags_all.setdefault(t, flags)
        f = firms.setdefault(r["ticker"], {"census_stratum": r["census_stratum"], "exclude_phrases": FIRM_NAME_PHRASES.get(r["ticker"], []), "sites": []})
        f["sites"].append({"facility_id": r["facility_id"], "facility": r["facility"], "facility_type": r["facility_type"],
                           "rating": r["rating"], "asset_type": r["asset_type"], "is_office": r["is_office"],
                           "location_as_written": r["location_as_written"], "geocode_place": r["geocode_place"],
                           "terms": terms,
                           "note": "" if terms else "no proper name in facilities.csv (generic or unnamed site): cannot be named by the dictionary; Y5 = 0 by construction"})
    ctx = [{"term": c, "pattern": words_pattern(c, c in PLURAL_CONTEXT)} for c in CONTEXT]
    return {
        "name": "Site-mention dictionary (design f5; outcomes Y4 and Y5)",
        "frozen_on": FROZEN,
        "source": "data/processed/facilities.csv (Phase 2, 214 sites, 59 tickers), which supersedes the Phase 0 file "
                  "data/interim/facility_locatability.csv named in f5 (amendment A17). Terms curated by the analyst from "
                  "the facility, location_as_written and geocode_place columns; no corpus text was searched or counted.",
        "amendment": "A17",
        "rules": {
            "unit": "one paragraph (or split piece) of the firm's own documents; only that firm's sites are matched",
            "preprocessing": "the firm's exclude_phrases (its own name where it contains a site term) are deleted from the "
                             "text before matching",
            "R1": "place term (not ambiguous): case-insensitive whole-word match of the term, together with at least one "
                  "facility-context term anywhere in the same paragraph (f5: 'town or estate name together with that firm's "
                  "facility context within the same paragraph')",
            "R2": "ambiguous place term (any ambiguity flag except firm-name collision): case-sensitive match, and a "
                  "facility-context term in the same sentence (sentences split at . ! ? followed by a space)",
            "R3": "facility proper name or licence (e.g. 'MTN Plaza', 'Qua Iboe', 'OML 40'): the name is itself the facility, "
                  "so it counts on its own, case-sensitive. 'R3+R2': an ambiguous facility name also needs a facility-context "
                  "term in the same sentence",
            "generic_words": "generic words such as 'plant' or 'factory' are never terms on their own (f5); they are only "
                             "context terms",
            "site_named": "a paragraph names site S if any term of S matches under its rule. Y4: physical-risk climate "
                          "paragraphs naming at least one of the firm's sites. Y5: site S named in any of the firm's "
                          "documents 2020-2025, in any context (any section, including notes that name sites, f1)",
            "shared_terms_within_firm": "where one term belongs to several sites of the same firm (e.g. NB 'Aba': brewery, "
                                        "malting plant and sales office), a match names all of them; the site-level Y5 "
                                        "therefore cannot separate such sites",
        },
        "facility_context_terms": ctx,
        "ambiguous_terms": flags_all,
        "firms": firms,
    }


def main():
    for path, obj in ((OUT_H, hazard_json()), (OUT_S, sites_json())):
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(path.relative_to(ROOT).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
