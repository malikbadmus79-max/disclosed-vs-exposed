"""Phase 2: OCR copies of reports with no usable text layer (design f2: OCRmyPDF + Tesseract, English).

Originals are never modified. Each OCR copy is written next to its original with "_ocr" before ".pdf".
`--force-ocr` is used because some files carry a stray text object (a site watermark or a few characters)
that would make OCRmyPDF skip the page; the copy is rasterised and OCR'd in full.
`--oversample 300`: most of these scans are stored at 72-120 dpi, and a test on Multiverse pp6 and 16 showed that
Tesseract misreads much of the text at native resolution ("quing", "efning") but reads it correctly at 300 dpi.
Tool versions and per-file results are written to data/interim/phase2_ocr_log.csv.

usage: phase2_ocr.py [path ...]  (all files in FILES; files whose _ocr copy already exists are skipped;
                                  with paths given, only those originals are processed: one file per run when memory is low)
Needs gswin64c and tesseract on PATH (Ghostscript 10.08.0 and Tesseract 5.4.0 on this machine).
"""
import csv
import hashlib
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "data" / "interim" / "phase2_ocr_log.csv"
FILES = {
    "THOMASWY": "data/raw/manual/thomaswy/ng-thomas-2025-ar-00.pdf",
    "ELLAHLAKES": "data/raw/manual/ellahlakes/ng-ellahl-2024-ar-00.pdf",
    "MULTIVERSE": "data/raw/manual/multiverse/ng-multiv-2025-ar-00.pdf",
    "MCNICHOLS": "data/raw/manual/mcnichols/ng-mcnich-2025-ar-00.pdf",
    "UNIONDICON": "data/raw/manual/uniondicon/ng-uds-2025-ar-00.pdf",
    "ALEX": "data/raw/manual/alex/ng-alex-2024-ar-00.pdf",
    "ETERNA": "data/raw/manual/eterna/ng-eterna-2025-ar-00.pdf",
    "GEREGU": "data/raw/manual/geregu/Geregu Power PLC - 2024 - Annual Report and Financial Statements (SustainabilityReports.com).pdf",
    "OKOMUOIL_2023": "data/raw/pilot_reports/okomu_oil/2023_AR.pdf",
    "OKOMUOIL_2024": "data/raw/pilot_reports/okomu_oil/2024_AR.pdf",
    "MULTITREX": "data/raw/manual/multitrex/ng-multix-2024-ar-00.pdf",  # owner decision 2026-11-12: image-only pages only
    "UNILEVER": "data/raw/manual/unilever/Unilever_Nigeria_2025_Annual_Report.pdf",  # fails readability (A1); owner 2026-11-12
    "A12_LIVESTOCK": "data/raw/manual/livestock/2025_AR.pdf",  # A12 (2026-11-17): run-together text (no word spaces)
}
# Academy: page 17 holds a DeviceN (spot-colour) image that OCRmyPDF cannot read (PIL.UnidentifiedImageError, 2026-11-12),
# so every page except 17 is OCR'd; page 17 keeps its original text layer.
EXTRA = {"A2_ACADEMY_ng-academ-2025-ar-00": ["--pages", "1-16,18-112"]}
# Files added by amendment A2 (page-level rule) are appended from data/interim/readability_pages.csv
A2_LIST = Path(__file__).resolve().parents[1] / "data" / "interim" / "readability_pages.csv"
# Files OCR'd only on some pages (the pages with no text layer); the other pages keep their original text layer.
PAGES = {"MULTITREX": "8,9,10,11,12,13,14,16,20,22,48,49,50,51,52,53,54,55,56,57"}

OPTIONS = ["--force-ocr", "-l", "eng", "--oversample", "300", "--jobs", "4", "--output-type", "pdf"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def version(cmd) -> str:
    out = subprocess.run(cmd, capture_output=True, text=True)
    return (out.stdout or out.stderr).strip().splitlines()[0]


def main() -> None:
    for tool in ("gswin64c", "tesseract"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not on PATH")
    ocrmypdf = str(Path(sys.executable).with_name("ocrmypdf.exe"))
    versions = {"ocrmypdf": version([ocrmypdf, "--version"]), "tesseract": version(["tesseract", "--version"]),
                "ghostscript": version(["gswin64c", "--version"])}
    print(versions, flush=True)
    rows = list(csv.DictReader(LOG.open(newline="", encoding="utf-8"))) if LOG.exists() else []
    done = {r["ocr_file"] for r in rows if r["status"] == "ok" and r["options"].startswith(" ".join(OPTIONS))}
    files = dict(FILES)
    if A2_LIST.exists():
        for r in csv.DictReader(A2_LIST.open(newline="", encoding="utf-8")):
            if r["a2_ocr"] == "yes" and r["file"] not in files.values():
                files[f"A2_{r['key']}_{Path(r['file']).stem}"] = r["file"]
    only = {a.replace("\\", "/") for a in sys.argv[1:]}
    for key, rel in files.items():
        if only and rel not in only:
            continue
        src = ROOT / rel
        dst = src.with_name(src.stem + "_ocr.pdf")
        rel_dst = str(dst.relative_to(ROOT)).replace("\\", "/")
        if rel_dst in done and dst.exists():
            print("skip (done)", key, flush=True)
            continue
        before = sha(src)
        t0 = time.time()
        opts = OPTIONS + (["--pages", PAGES[key]] if key in PAGES else []) + EXTRA.get(key, [])
        proc = subprocess.run([ocrmypdf, *opts, str(src), str(dst)], capture_output=True, text=True)
        status = "ok" if proc.returncode == 0 and dst.exists() else f"error (exit {proc.returncode})"
        if sha(src) != before:
            status += "; ORIGINAL CHANGED"
        rows = [r for r in rows if r["ocr_file"] != rel_dst]
        rows.append({"key": key, "original_file": rel, "original_sha256": before, "ocr_file": rel_dst,
                     "ocr_sha256": sha(dst) if dst.exists() else "", "status": status,
                     "seconds": f"{time.time() - t0:.0f}", "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                     "options": " ".join(opts), **versions,
                     "stderr_tail": " | ".join(proc.stderr.strip().splitlines()[-3:])[:400]})
        with LOG.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(key, status, f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
