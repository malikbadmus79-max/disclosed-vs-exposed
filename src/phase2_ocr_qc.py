"""Phase 2: OCR quality check (design f2: read 2 random pages per OCR'd document against the page image).

Pages are drawn with a fixed seed so the draw can be repeated. For each drawn page this script renders the page
image to OUTDIR and prints the OCR text; the analyst compares the two and records the result in
data/interim/phase2_ocr_qc.csv (written by hand from the printed output; see docs/phase2_sites.md).

usage: phase2_ocr_qc.py OUTDIR
"""
import csv
import random
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SEED = 20261111
PAGES_PER_DOC = 2


def main() -> None:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    rows = [r for r in csv.DictReader((ROOT / "data" / "interim" / "phase2_ocr_log.csv").open(newline="", encoding="utf-8"))
            if r["status"] == "ok"]
    rng = random.Random(SEED)
    for r in rows:
        with pymupdf.open(ROOT / r["ocr_file"]) as d:
            opts = r["options"].split()
            pool = list(range(1, len(d) + 1))
            if "--pages" in opts:  # only the OCR'd pages, e.g. "8,9,48-57"
                pool = []
                for part in opts[opts.index("--pages") + 1].split(","):
                    a, _, b = part.partition("-")
                    pool += list(range(int(a), int(b or a) + 1))
            pages = sorted(rng.sample(pool, PAGES_PER_DOC))
            for p in pages:
                pix = d[p - 1].get_pixmap(dpi=110, colorspace=pymupdf.csGRAY)
                img = out / f"{r['key']}_p{p}.png"
                pix.save(img)
                text = " ".join(d[p - 1].get_text().split())
                print(f"### {r['key']} p{p} ({len(text)} chars) {img}\n{text[:700]}\n")


if __name__ == "__main__":
    main()
