"""Phase 4, step 1: corpus inventory and paragraph segmentation (design f1, f3). No model is run, no dictionary is applied,
no climate term is counted and no disclosure measure is computed.

inventory  -> data/interim/phase4_documents.csv   one row per report document on disk for a census firm (main + robustness)
              data/interim/phase4_firm_year.csv   firm x fiscal year (FY2020-FY2025) table of document types held
              data/interim/phase4_download_list.csv  firm-years / documents the design (f1) still needs
segment [start] [n] -> appends to data/interim/paragraphs.csv (documents in phase4_documents.csv order)
summary    -> data/interim/phase4_doc_stats.csv and printed totals

Text route (A1-A5): documents with an OCR copy (phase2_ocr_log.csv) take each page from the source chosen in
data/interim/text_sources.csv (original or OCR PDF); all other documents use the original PDF text layer (all passed A1).

Segmentation (f3), as implemented:
  * blocks: PyMuPDF page.get_text("dict") text blocks (dehyphenated), in the PDF's own block order; lines joined with
    spaces; Unicode NFKC (f2). Block font size = character-weighted median span size, rounded to 0.5 pt.
  * merge: a block is merged into the previous one when (a) same font size (difference <= 0.5 pt on original text
    layers; <= 1.0 pt on OCR pages, where Tesseract's sizes are estimates that vary line to line), (b) "no blank line
    between them": vertical gap between the previous block's bottom and this block's top is below 0.8 x font size
    (a blank line is about 1.2 x font size; ordinary line spacing 0.2-0.6 x) and not negative by more than one font
    size, and (c) same column: their horizontal extents overlap by at least 50% of the narrower block. Merging never
    crosses a page.
  * n_words: whitespace-separated tokens containing at least one letter or digit.
  * min length (f3: 40 words): shorter paragraphs are kept (site-mention dictionary) with model_eligible = 0.
  * dedup (f3): within a document, a paragraph whose normalised text (lower case, collapsed spaces) repeats an earlier
    one gets duplicate_of = that paragraph's id and model_eligible = 0; it stays in the file.
  * long paragraphs (f3: > 512 tokens): token counts use the cached ClimateBERT tokenizer (detector repo,
    local_files_only; the model itself is not loaded). Eligible paragraphs above 512 tokens (incl. special tokens) are
    split at sentence boundaries (. ! ? followed by space) into pieces of <= 512 tokens; a sentence longer than that is
    split at word boundaries. Each piece is its own row (piece = 1..k, parent_paragraph_id = the unsplit id).
  * section tagging (f1: financial statements excluded, by hand) is NOT done here; every page is kept.

usage: phase4_corpus.py inventory | segment [start] [n] | segment_new [n] | summary
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
I = ROOT / "data" / "interim"
YEARS = list(range(2020, 2026))
PARA = I / "paragraphs.csv"
DOCS = I / "phase4_documents.csv"
REPAIRS = I / "ligature_repairs.csv"  # A13
COLS = ["firm", "year", "doc", "doc_type", "page", "page_source", "paragraph_id", "parent_paragraph_id", "piece",
        "font_size", "n_words", "n_tokens", "model_eligible", "duplicate_of", "text"]

# manual folder documents whose census note describes a financial-statement filing (not a full annual report)
MANUAL_FS = {"ALEX", "ELLAHLAKES", "EUNISELL", "GOLDBREW", "JAPAULGOLD", "MCNICHOLS", "OANDO", "THOMASWY", "TRIPPLEG",
             "UNIONDICON", "TOTAL"}
# per-file document-type exceptions (checked from the documents; docs/data_sources.md, owner batches 1-4, 2026-11-17)
TYPE_OVERRIDE = {
    "data/raw/manual/hbmng/2020_AR.pdf": "FS",       # Lafarge Africa FY2020: financial statements + directors' report
    "data/raw/manual/transpower/2020_AR.pdf": "FS",  # Transcorp Power Limited FY2020: financial statements + directors' report
    "data/raw/manual/alex/2020_AR.pdf": "AR",        # Alex FY2020: full annual report (ALEX is in MANUAL_FS for FY2024)
    "data/raw/manual/seplat/2020_AR.pdf": "AR",      # Seplat FY2020: "Annual Report and Accounts" (not an integrated report)
}
# A16: NGX listing dates of main-census firms listed after 2020-01-01 (all have 31 December year-ends);
# a firm-year counts in the H3 main analysis only if its fiscal year ends on or after the listing date
LISTING = {"TRANSPOWER": "2024-03-04", "ARADEL": "2024-10-14", "BUAFOODS": "2022-01-05", "GEREGU": "2022-10-05",
           "MECURE": "2023-11-07"}
TYPE_NAME = {"AR": "annual report", "IAR": "integrated report", "SR": "sustainability report",
             "SRX": "sustainability extract", "FS": "financial-statement filing (as labelled; narrative content checked at section tagging)"}


def key_for(original):  # same as text_select.key_for
    p = Path(original)
    return re.sub(r"[^A-Za-z0-9]+", "_", f"{p.parent.name}__{p.stem}").strip("_")[:80]


def read(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))


def write(rows, path, cols=None):
    cols = cols or list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(rows)


def census():
    c = [r for r in read(I / "ngx_census_frame.csv") if r["census_stratum"] in ("main", "robustness_stratum")]
    return {r["ticker"]: r for r in c}


def documents():
    cen = census()
    pilot = {r["firm"]: r["ngx_ticker"] for r in read(I / "firm_ticker_map.csv")}
    folder_ticker = {Path(r["report_file"]).parent.name: t for t, r in cen.items() if r["report_file"]}
    folder_ticker.update({"mtn": "MTNN", "nigerian_breweries": "NB", "nb": "NB", "hbmng": "HBMNG"})
    ocr = {r["original_file"]: r["ocr_file"] for r in read(I / "phase2_ocr_log.csv") if r["status"] == "ok"}
    docs = []
    for base in ("pilot_reports", "phase2_reports", "manual"):
        for f in sorted((ROOT / "data" / "raw" / base).rglob("*.pdf")):
            rel = f.relative_to(ROOT).as_posix()
            if f.stem.endswith("_ocr") or f.parent.name == "manual":  # OCR copies; loose duplicates in data/raw/manual/
                continue
            if base == "pilot_reports":
                t = pilot.get(f.parent.name, "none"); y, typ = f.stem.split("_")
            elif base == "phase2_reports":
                t = f.parent.name.upper(); y, typ = f.stem.split("_")
            else:
                t = folder_ticker.get(f.parent.name, "?")
                y = re.search(r"20[12]\d", f.name).group(0)
                typ = ("SR" if "Sustainability-Report" in f.name else "IAR" if t == "SEPLAT"
                       else "FS" if t in MANUAL_FS else "AR")
            typ = TYPE_OVERRIDE.get(rel, typ)
            if t not in cen:
                print("skip (not in census):", rel, t); continue
            docs.append({"doc": f"{t}_{y}_{typ}", "firm": t, "stratum": cen[t]["census_stratum"], "year": int(y), "doc_type": typ,
                         "doc_type_name": TYPE_NAME[typ], "file": rel, "ocr_file": ocr.get(rel, ""),
                         "text_route": "A3-A5 page selection (text_sources.csv)" if rel in ocr else "original text layer (A1 pass)",
                         "listing_date": LISTING.get(t, "before 2020"),
                         "h3_main": int(t not in LISTING or f"{y}-12-31" >= LISTING[t])})  # A16 (Dec year-ends)
    assert len({d["doc"] for d in docs}) == len(docs)
    return sorted(docs, key=lambda d: (d["firm"], d["year"], d["doc_type"]))


def inventory():
    import pymupdf
    docs = documents()
    for d in docs:
        with pymupdf.open(ROOT / d["file"]) as p:
            d["pages"] = p.page_count
    write(docs, DOCS)
    cen = census()
    have = {}
    for d in docs:
        have.setdefault((d["firm"], d["year"]), []).append(d["doc_type"])
    rows = []
    for t, r in sorted(cen.items(), key=lambda x: (x[1]["census_stratum"] != "main", x[0])):
        row = {"firm": t, "stratum": r["census_stratum"], "document_test": r["document_test"].split(" (")[0].split(" —")[0]}
        for y in YEARS:
            row[f"FY{y}"] = "+".join(sorted(have.get((t, y), []))) or "-"
        row["years_with_any_document"] = sum(row[f"FY{y}"] != "-" for y in YEARS)
        row["years_with_annual_report"] = sum(any(x in ("AR", "IAR") for x in have.get((t, y), [])) for y in YEARS)
        row["years_with_sustainability_report"] = sum(any(x in ("SR", "SRX") for x in have.get((t, y), [])) for y in YEARS)
        row["years_h3_main"] = sum(1 for y in YEARS if have.get((t, y)) and (t not in LISTING or f"{y}-12-31" >= LISTING[t]))  # A16
        rows.append(row)
    write(rows, I / "phase4_firm_year.csv")
    # download list (f1: every firm-year 2020-2025; annual report plus any separate sustainability report)
    leads = {}
    for r in read(I / "pilot_report_inventory.csv"):
        if r["status"] != "ok" and r["url"].startswith("http") and "africanfinancials" not in r["url"]:
            t = {x["firm"]: x["ngx_ticker"] for x in read(I / "firm_ticker_map.csv")}.get(r["firm"])
            leads[(t, int(r["fiscal_year"]), r["type"])] = r["url"]
    dl = []
    for row in rows:
        t = row["firm"]
        if row["document_test"].startswith("failed"):
            continue
        pending = row["document_test"].startswith("pending")
        for y in YEARS:
            held = have.get((t, y), [])
            if not any(x in ("AR", "IAR", "FS") for x in held):
                typ = "FS" if (t, y, "FS") in leads and (t, y, "AR") not in leads else "AR"
                dl.append({"firm": t, "stratum": row["stratum"], "year": y, "report_type": "annual report",
                           "priority": "3 (robustness stratum)" if row["stratum"] != "main" else
                           ("1 (2023-2025 year)" if y >= 2023 else "2 (2020-2022 year)"),
                           "lead_url": leads.get((t, y, "AR")) or leads.get((t, y, typ)) or "",
                           "note": "; ".join(x for x in ("lead is the FS filing on doclib" if typ == "FS" else "",
                                                         "document test pending (owner: skipped for now)" if pending else "") if x)})
            elif "FS" in held and not any(x in ("AR", "IAR") for x in held):
                dl.append({"firm": t, "stratum": row["stratum"], "year": y, "report_type": "full annual report (only an FS filing held)",
                           "priority": "4 (optional: replaces an FS filing)", "lead_url": leads.get((t, y, "AR"), ""), "note": ""})
        for (lt, ly, ltyp), url in leads.items():
            if lt == t and ltyp in ("SR", "SPR") and ltyp not in have.get((t, ly), []):
                dl.append({"firm": t, "stratum": row["stratum"], "year": ly, "report_type": "sustainability report", "priority": "2 (known to exist)",
                           "lead_url": url, "note": ""})
    for x in dl:
        if not x["lead_url"]:
            x["lead_url"] = "not known"
    dl.append({"firm": "SEPLAT", "stratum": "main", "year": 2023, "report_type": "sustainability report", "priority": "2 (known to exist)",
               "lead_url": "requested from owner (pending before Phase 6)", "note": ""})
    dl.append({"firm": "SEPLAT", "stratum": "main", "year": 2025, "report_type": "social performance report", "priority": "2 (known to exist)",
               "lead_url": "requested from owner (pending before Phase 6)", "note": ""})
    dl.sort(key=lambda x: (x["priority"], x["firm"], x["year"]))
    write(dl, I / "phase4_download_list.csv")
    print(f"documents {len(docs)} | firms with any document {sum(r['years_with_any_document'] > 0 for r in rows)} / {len(rows)} | "
          f"download rows {len(dl)}")


# ---------------------------------------------------------------- segmentation
_tok = None


def tokenizer():
    global _tok
    if _tok is None:
        from transformers import AutoTokenizer
        _tok = AutoTokenizer.from_pretrained("climatebert/distilroberta-base-climate-detector",
                                             cache_dir=ROOT / "data" / "raw" / "hf_cache", local_files_only=True)
    return _tok


def ntok(text):
    return len(tokenizer()(text, truncation=False)["input_ids"])


WORD = re.compile(r"[A-Za-z0-9]")
CTRL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")  # A15


def nwords(t):
    return sum(1 for w in t.split() if WORD.search(w))


def blocks(page, original=True, log=None):
    import pymupdf
    out = []
    d = page.get_text("dict", flags=pymupdf.TEXTFLAGS_DICT | pymupdf.TEXT_DEHYPHENATE)
    for b in d["blocks"]:
        if b.get("type") != 0:
            continue
        lines, sizes = [], []
        for ln in b["lines"]:
            s = "".join(sp["text"] for sp in ln["spans"])
            if s.strip():
                lines.append(s.strip())
            sizes += [(sp["size"], len(sp["text"].strip())) for sp in ln["spans"] if sp["text"].strip()]
        text = CTRL.sub(" ", " ".join(lines))  # A15: control characters (e.g. U+0003 used as space) -> space
        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        text = repair_ligatures(text, original, log)
        sizes.sort()
        tot, acc, med = sum(n for _, n in sizes), 0, sizes[0][0]
        for s, n in sizes:
            acc += n
            if acc >= tot / 2:
                med = s; break
        out.append({"text": text, "size": round(med * 2) / 2, "bbox": b["bbox"]})
    return out


# ---------------------------------------------------------------- A13: ligature repair (f2)
LIG_CODEPOINTS = {"": "fi", "": "fl"}  # Adobe/Apple private-use ligature convention
LIGS = ("ffi", "ffl", "ff", "fi", "fl")
NONWORD, WORD_OK = 1.5, 3.0  # wordfreq zipf thresholds (A13)
_zcache = {}


def _z(w):
    if w not in _zcache:
        from wordfreq import zipf_frequency
        _zcache[w] = zipf_frequency(w, "en")
    return _zcache[w]


def _case(src, new):
    return new[:1].upper() + new[1:] if src[:1].isupper() else new


def _single(m):
    tok = m.group(0); low = tok.lower()
    if _z(low) >= NONWORD:
        return None
    cands = {low[:k] + g + low[k:] for k in range(len(low) + 1) for g in LIGS}
    ok = [c for c in cands if _z(c) >= WORD_OK]
    return _case(tok, ok[0]) if len(ok) == 1 else None


def _pair(m):
    a, b = m.group(1), m.group(2)
    if _z(b) >= NONWORD:
        return None
    ok = {(a + g + b).lower() for g in LIGS if _z((a + g + b).lower()) >= WORD_OK}
    return _case(a, ok.pop()) if len(ok) == 1 else None


def repair_ligatures(text, original, log=None):
    """A13: private-use ligature code points everywhere; dropped glyphs on original text-layer pages only."""
    for cp, lig in LIG_CODEPOINTS.items():
        if cp in text:
            if log is not None:
                log.append(("codepoint", f"U+{ord(cp):04X}", lig, text.count(cp)))
            text = text.replace(cp, lig)
    if not original:
        return text

    def sub_pair(m):
        r = _pair(m)
        if r and log is not None:
            log.append(("split", m.group(0), r, 1))
        return r or m.group(0)

    def sub_single(m):
        r = _single(m)
        if r and log is not None:
            log.append(("single", m.group(0), r, 1))
        return r or m.group(0)

    text = re.sub(r"\b([A-Za-z]{1,6}) ([a-z]{2,})\b", sub_pair, text)
    return re.sub(r"\b[A-Za-z]{3,}\b", sub_single, text)


def merge(bl, tol=0.5):
    out = []
    for b in bl:
        if out:
            p = out[-1]
            x0, y0, x1, y1 = p["bbox"]; a0, b0, a1, b1 = b["bbox"]
            same = abs(p["size"] - b["size"]) <= tol
            gap = b0 - y1
            overlap = min(x1, a1) - max(x0, a0)
            narrow = max(1e-6, min(x1 - x0, a1 - a0))
            if same and -b["size"] <= gap < 0.8 * b["size"] and overlap >= 0.5 * narrow:
                p["text"] += " " + b["text"]
                p["bbox"] = (min(x0, a0), min(y0, b0), max(x1, a1), max(y1, b1))
                continue
        out.append(dict(b))
    return out


PUA = re.compile("[-]")  # private-use glyphs (e.g. unmapped fi/fl ligatures)
LONG = re.compile(r"\S{25,}")  # with long_word(): 25+ characters, >= 85% letters, no space (words run together)


def long_word(w):
    return bool(LONG.fullmatch(w)) and sum(c.isalpha() for c in w) >= 0.85 * len(w) and "http" not in w and "@" not in w
SENT = re.compile(r"(?<=[.!?])\s+")


def split_long(text):
    """Pieces of <= 512 tokens (incl. special tokens), at sentence boundaries; over-long sentences at word boundaries."""
    units = []
    for s in SENT.split(text):
        if ntok(s) <= 512:
            units.append(s); continue
        cur = []
        for w in s.split():
            if cur and ntok(" ".join(cur + [w])) > 512:
                units.append(" ".join(cur)); cur = []
            cur.append(w)
        if cur:
            units.append(" ".join(cur))
    pieces, cur = [], ""
    for u in units:
        cand = (cur + " " + u).strip()
        if cur and ntok(cand) > 512:
            pieces.append(cur); cur = u
        else:
            cur = cand
    if cur:
        pieces.append(cur)
    return pieces


def segment_doc(d, src):
    import pymupdf
    pages = src.get(d["file"], {})
    orig = pymupdf.open(ROOT / d["file"])
    ocr = pymupdf.open(ROOT / d["ocr_file"]) if d["ocr_file"] else None
    rows, seen, reps = [], {}, []
    for i in range(orig.page_count):
        source = pages.get(i + 1, "original")
        pg = (ocr if source == "ocr" else orig)[i]
        lg = []
        bl = blocks(pg, source != "ocr", lg)
        for kind, before, after, n in lg:
            reps.append({"doc": d["doc"], "page": i + 1, "page_source": source, "kind": kind, "before": before, "after": after, "n": n})
        for k, p in enumerate(merge(bl, 1.0 if source == "ocr" else 0.5), 1):
            pid = f"{d['doc']}_p{i + 1:03d}_{k:03d}"
            n = nwords(p["text"])
            norm = re.sub(r"\s+", " ", p["text"].lower()).strip()
            dup = seen.get(norm, "")
            if not dup:
                seen[norm] = pid
            elig = int(n >= 40 and not dup)
            base = {"firm": d["firm"], "year": d["year"], "doc": d["doc"], "doc_type": d["doc_type"], "page": i + 1,
                    "page_source": source, "parent_paragraph_id": pid, "font_size": p["size"], "duplicate_of": dup}
            if elig:
                t = ntok(p["text"])
                if t > 512:
                    for j, piece in enumerate(split_long(p["text"]), 1):
                        rows.append({**base, "paragraph_id": f"{pid}_{j}", "piece": j, "n_words": nwords(piece),
                                     "n_tokens": ntok(piece), "model_eligible": 1, "text": piece})
                    continue
            else:
                t = ""
            rows.append({**base, "paragraph_id": pid, "piece": "", "n_words": n, "n_tokens": t, "model_eligible": elig, "text": p["text"]})
    orig.close()
    if ocr:
        ocr.close()
    return rows, reps


def segment_new(limit=10 ** 6):
    """Segment only documents in phase4_documents.csv that are not yet in paragraphs.csv; append with the existing header.
    `limit`: at most this many documents per run (short runs when memory is low)."""
    docs = read(DOCS)
    with open(PARA, newline="", encoding="utf-8") as f:
        rd = csv.reader(f); header = next(rd); have = {r[header.index("doc")] for r in rd}
    src = {}
    for r in read(I / "text_sources.csv"):
        src.setdefault(r["original_file"], {})[int(r["pdf_page"])] = r["source"]
    todo = [d for d in docs if d["doc"] not in have][:limit]
    print("new documents:", len(todo), flush=True)
    for d in todo:
        rows, reps = segment_doc(d, src)
        with open(PARA, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, header, restval="", extrasaction="ignore").writerows(rows)
        if reps:
            with open(REPAIRS, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, ["doc", "page", "page_source", "kind", "before", "after", "n"]).writerows(reps)
        print(f"{d['doc']:<28} pages {d['pages']:>4} paragraphs {len(rows):>6} eligible {sum(r['model_eligible'] for r in rows):>5}", flush=True)


def segment(start, n):
    docs = read(DOCS)
    src = {}
    for r in read(I / "text_sources.csv"):
        src.setdefault(r["original_file"], {})[int(r["pdf_page"])] = r["source"]
    if start == 0:
        for f in (PARA, REPAIRS):
            if f.exists():
                f.unlink()
    for d in docs[start:start + n]:
        rows, reps = segment_doc(d, src)
        if reps:
            new = not REPAIRS.exists()
            with open(REPAIRS, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, ["doc", "page", "page_source", "kind", "before", "after", "n"])
                if new:
                    w.writeheader()
                w.writerows(reps)
        new = not PARA.exists()
        with open(PARA, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, COLS)
            if new:
                w.writeheader()
            w.writerows(rows)
        print(f"{d['doc']:<28} pages {d['pages']:>4} paragraphs {len(rows):>6} eligible {sum(r['model_eligible'] for r in rows):>5}", flush=True)
    print("next start:", start + n, "of", len(docs))


def summary():
    import numpy as np
    import readability as R
    import wordfreq
    docs = {d["doc"]: d for d in read(DOCS)}
    st = {k: {"rows": 0, "elig": 0, "words": [], "pages": set(), "dups": 0, "pieces": 0, "maxw": 0, "hit": 0, "tok": 0, "short": 0,
              "allw": 0, "longw": 0, "words_all": 0, "words_elig": 0, "pua": 0}
          for k in docs}
    with open(PARA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            s = st[r["doc"]]; s["rows"] += 1; s["pages"].add(int(r["page"]))
            s["dups"] += bool(r["duplicate_of"]); s["pieces"] += r["piece"] not in ("", "1")
            s["pua"] += len(PUA.findall(r["text"]))
            if not r["duplicate_of"]:
                ws = r["text"].split(); s["allw"] += len(ws); s["longw"] += sum(1 for w in ws if long_word(w))
                s["words_all"] += int(r["n_words"]); s["words_elig"] += int(r["n_words"]) * (r["model_eligible"] == "1")
            if r["model_eligible"] == "1":
                n = int(r["n_words"]); s["elig"] += 1; s["words"].append(n); s["maxw"] = max(s["maxw"], n)
                toks = [x for x in wordfreq.tokenize(r["text"], "en") if R.LETTER.search(x)]
                s["tok"] += len(toks); s["hit"] += sum(x in R.COMMON for x in toks)
            else:
                s["short"] += not r["duplicate_of"]
    out = []
    for k, s in st.items():
        d = docs[k]; pages = int(d["pages"])
        share = s["hit"] / s["tok"] if s["tok"] else 0
        flags = []
        if s["elig"] < 20: flags.append("fewer than 20 eligible paragraphs")
        if share < R.THRESHOLD: flags.append(f"common-word share of eligible text {share:.2f} < {R.THRESHOLD}")
        if (pages - len(s["pages"])) / pages > 0.10: flags.append(f"{pages - len(s['pages'])} of {pages} pages without text blocks")
        if s["rows"] and s["short"] / s["rows"] > 0.95: flags.append("over 95% of blocks under 40 words (fragmented)")
        if s["maxw"] > 1500: flags.append(f"a paragraph of {s['maxw']} words (possible merge failure)")
        lw = s["longw"] / s["allw"] if s["allw"] else 0
        if lw > 0.01: flags.append(f"missing word spaces: {lw:.1%} of tokens are 25+ letters run together")
        we = s["words_elig"] / s["words_all"] if s["words_all"] else 0
        out.append({"doc": k, "firm": d["firm"], "year": d["year"], "doc_type": d["doc_type"], "pages": pages,
                    "pages_with_text": len(s["pages"]), "rows": s["rows"], "eligible": s["elig"], "duplicates": s["dups"],
                    "split_pieces_extra": s["pieces"], "median_words_eligible": float(np.median(s["words"])) if s["words"] else "",
                    "max_words_eligible": s["maxw"], "common_share_eligible": round(share, 4),
                    "share_words_in_eligible": round(we, 3), "share_long_tokens": round(lw, 4),
                    "private_use_glyphs": s["pua"], "flags": "; ".join(flags)})
    write(out, I / "phase4_doc_stats.csv")
    allw = [w for s in st.values() for w in s["words"]]
    print(f"docs {len(out)} | rows {sum(o['rows'] for o in out)} | eligible {len(allw)} | median words (eligible) {np.median(allw)} | "
          f"duplicates {sum(o['duplicates'] for o in out)} | flagged docs {sum(bool(o['flags']) for o in out)}")
    for o in out:
        if o["flags"]:
            print(" ", o["doc"], "|", o["flags"])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "inventory":
        inventory()
    elif cmd == "segment":
        segment(int(sys.argv[2]) if len(sys.argv) > 2 else 0, int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 6)
    elif cmd == "segment_new":
        segment_new(int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6)
    elif cmd == "summary":
        summary()
