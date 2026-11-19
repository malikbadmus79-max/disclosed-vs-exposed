"""Amendments A3, A4 and A5 (final): page-level text selection for every report that has an OCR copy.

A4 rule (see choose()): higher common-word share wins (original on a tie), unless the winner has fewer than half the
word tokens of the other version; if both shares are below 0.20, the higher share is used and the page is flagged.
Shares use the A1 word list and tokens (src/readability.py). No PDF is modified.

Outputs:
  data/interim/text/<key>.txt        one file per report, NFKC text, with a marker line before each page
  data/interim/text_sources.csv      one row per page: shares, token counts, source used, flag
  data/interim/readability_merged.csv  readability of each merged text (A1 threshold; A2 page statistic for information)

usage: text_select.py
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf
import wordfreq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import readability as R  # noqa: E402

MIN_SHARE = 0.20  # A3/A4: both-below threshold (same value as the A2 page threshold)
MIN_TOKEN_RATIO = 0.5  # A4: token-count override
OUT_DIR = ROOT / "data" / "interim" / "text"


def page_texts(path: Path):
    """[(text, word_tokens, common_tokens, share)] per page."""
    out = []
    with pymupdf.open(path) as d:
        for pg in d:
            t = unicodedata.normalize("NFKC", pg.get_text())
            toks = [x for x in wordfreq.tokenize(t, "en") if R.LETTER.search(x)]
            hit = sum(x in R.COMMON for x in toks)
            out.append((t, len(toks), hit, hit / len(toks) if toks else 0.0))
    return out


def key_for(original: str) -> str:
    p = Path(original)
    return re.sub(r"[^A-Za-z0-9]+", "_", f"{p.parent.name}__{p.stem}").strip("_")[:80]


def choose(o, c):
    """(source, flag) for one page from (original, ocr) page tuples: (text, word_tokens, common_tokens, share).

    A4 (replaces the A3 order): if both shares are below 0.20, use the higher share (original on a tie) and flag.
    Otherwise use the version with the higher share (original on a tie), unless it has fewer than half the word
    tokens of the other version, in which case use the other one. A5: that guard applies only if the other version's
    share is >= 0.20, so a version with share < 0.20 never wins through it. Final for this study.
    """
    if o[3] < MIN_SHARE and c[3] < MIN_SHARE:
        if c[3] > o[3]:
            return "ocr", "both_below_0.20"
        return "original", "both_below_0.20" + ("; no_text_either" if o[1] == 0 and c[1] == 0 else "")
    best, other = ("ocr", "original") if c[3] > o[3] else ("original", "ocr")
    tok = {"original": o[1], "ocr": c[1]}
    shr = {"original": o[3], "ocr": c[3]}
    if tok[best] < MIN_TOKEN_RATIO * tok[other] and shr[other] >= MIN_SHARE:  # A5: guard needs other share >= 0.20
        return other, "token_override"
    return best, ""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log = [r for r in csv.DictReader((ROOT / "data" / "interim" / "phase2_ocr_log.csv").open(encoding="utf-8")) if r["status"] == "ok"]
    src_rows, merged_rows = [], []
    for r in log:
        key = key_for(r["original_file"])
        orig, ocr = page_texts(ROOT / r["original_file"]), page_texts(ROOT / r["ocr_file"])
        assert len(orig) == len(ocr), f"page count differs: {key}"
        parts, n_tok, n_hit, low = [], 0, 0, 0
        for i, (o, c) in enumerate(zip(orig, ocr), 1):
            source, flag = choose(o, c)
            t = o if source == "original" else c
            parts.append(f"=== page {i} | source: {source}{' | FLAG: ' + flag if flag else ''} ===\n{t[0].strip()}\n")
            n_tok += t[1]; n_hit += t[2]; low += t[3] < MIN_SHARE
            src_rows.append({"key": key, "original_file": r["original_file"], "ocr_file": r["ocr_file"], "pdf_page": i,
                             "original_tokens": o[1], "original_share": f"{o[3]:.4f}", "ocr_tokens": c[1],
                             "ocr_share": f"{c[3]:.4f}", "source": source, "flag": flag})
        (OUT_DIR / f"{key}.txt").write_text("\n".join(parts), encoding="utf-8")
        share = n_hit / n_tok if n_tok else 0.0
        merged_rows.append({"key": key, "text_file": f"data/interim/text/{key}.txt", "pages": len(orig),
                            "pages_original": sum(1 for x in src_rows if x["key"] == key and x["source"] == "original"),
                            "pages_ocr": sum(1 for x in src_rows if x["key"] == key and x["source"] == "ocr"),
                            "pages_flagged": sum(1 for x in src_rows if x["key"] == key and x["flag"]),
                            "word_tokens": n_tok, "common_share": f"{share:.4f}", "threshold": R.THRESHOLD,
                            "result": "pass" if share >= R.THRESHOLD else "fail",
                            "share_of_pages_below_0.20": f"{low / len(orig):.4f}"})
        m = merged_rows[-1]
        print(f"{m['result']} {m['common_share']} orig {m['pages_original']:>3} ocr {m['pages_ocr']:>3} flagged {m['pages_flagged']:>3} "
              f"/{m['pages']:<3} low {m['share_of_pages_below_0.20']} {key}", flush=True)
    R.write(src_rows, ROOT / "data" / "interim" / "text_sources.csv")
    R.write(merged_rows, ROOT / "data" / "interim" / "readability_merged.csv")


if __name__ == "__main__":
    main()
