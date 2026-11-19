"""Phase 4, step 3: validation sample (design g; amendments A18, A19). Predictions are used ONLY to form strata.

predict detector [n]     -> appends P(yes) for frame paragraphs not yet scored, at most n per run
                            (data/interim/validation_predictions.csv; resumable)
predict specificity [n]  -> appends P(spec) for frame paragraphs with P(yes) >= 0.5 not yet scored
draw                     -> data/interim/validation_sample.csv        id, firm, year, text (pass-1 order; for the coder)
                            data/interim/validation_sample_pass2.csv  same rows, new random order (seed + 1)
                            data/interim/validation_strata.csv        id, cell, predictions, tag, weight (NOT for the coder)

No corpus-level share, count or outcome is computed or printed from the predictions.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I = ROOT / "data" / "interim"
PARA = I / "paragraphs.csv"
PRED = I / "validation_predictions.csv"
CACHE = ROOT / "data" / "raw" / "hf_cache"
EXCLUDE_DOCS = {"DANGCEM_2025_SRX"}  # Phase 0 test document: coding-guide examples
PARAMS = json.load(open(ROOT / "config" / "parameters.json", encoding="utf-8"))
SEED = PARAMS["validation"]["random_seed"]["value"]
N = PARAMS["validation"]["n_paragraphs"]["value"]
FIRM_CAP = PARAMS["validation"]["max_per_firm"]["value"]
FS_CAP = int(round(PARAMS["validation"]["fs_only_cap_share"]["value"] * N))
THR = 0.5  # OD-10
MODELS = {"detector": ("climatebert/distilroberta-base-climate-detector", "yes"),
          "specificity": ("climatebert/distilroberta-base-climate-specificity", "spec")}
csv.field_size_limit(10 ** 8)


def frame():
    docs = {d["doc"]: d for d in csv.DictReader(open(I / "phase4_documents.csv", encoding="utf-8"))}
    out = []
    with open(PARA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = docs[r["doc"]]
            if (r["model_eligible"] == "1" and r["section"] == "narrative" and d["stratum"] == "main"
                    and r["doc"] not in EXCLUDE_DOCS):
                out.append({"id": r["paragraph_id"], "firm": r["firm"], "year": r["year"], "doc": r["doc"],
                            "doc_type": r["doc_type"], "text": r["text"]})
    return out


def load_pred():
    p = {}
    if PRED.exists():
        for r in csv.DictReader(open(PRED, encoding="utf-8")):
            p.setdefault(r["id"], {})[r["model"]] = r
    return p


def predict(which, limit):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    torch.set_num_threads(4)
    repo, label = MODELS[which]
    tok = AutoTokenizer.from_pretrained(repo, cache_dir=CACHE, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(repo, cache_dir=CACHE, local_files_only=True).eval()
    li = {v: int(k) for k, v in model.config.id2label.items()}[label]
    rev = (CACHE / f"models--{repo.replace('/', '--')}" / "refs" / "main").read_text().strip()
    done = load_pred()
    todo = [r for r in frame() if which not in done.get(r["id"], {})]
    if which == "specificity":
        todo = [r for r in todo if float(done.get(r["id"], {}).get("detector", {}).get("p", -1)) >= THR]
    todo = sorted(todo[:limit], key=lambda r: len(r["text"]))
    new = not PRED.exists()
    with open(PRED, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["id", "model", "p", "revision"])
        if new:
            w.writeheader()
        for i in range(0, len(todo), 16):
            batch = todo[i:i + 16]
            enc = tok([r["text"] for r in batch], truncation=True, max_length=512, padding=True, return_tensors="pt")
            with torch.no_grad():
                pr = torch.softmax(model(**enc).logits, -1)[:, li].tolist()
            w.writerows({"id": r["id"], "model": which, "p": f"{p:.6f}", "revision": rev} for r, p in zip(batch, pr))
            f.flush()
    left = len([r for r in frame() if which not in load_pred().get(r["id"], {})]) if which == "detector" else "n/a"
    print(f"{which}: scored {len(todo)} this run; detector rows still to score: {left}")


def draw():
    import numpy as np
    sys.path.insert(0, str(ROOT / "src"))
    H = json.load(open(ROOT / "config" / "dictionary_hazard.json", encoding="utf-8"))
    pats = [re.compile(p, re.I) for t in H["terms"] for p in t["patterns"]]
    fr, pred = frame(), load_pred()
    cells = {}
    for r in fr:
        pd = pred[r["id"]]
        pc = float(pd["detector"]["p"])
        if pc >= THR:
            ps = float(pd["specificity"]["p"])
            cls = "climate_specific" if ps >= THR else "climate_nonspecific"
        else:
            ps, cls = "", "not_climate"
        tag = "tagged" if any(p.search(r["text"]) for p in pats) else "untagged"
        r.update({"p_climate": pc, "p_spec": ps, "hazard_tag": tag, "cell": f"{cls}|{tag}"})
        cells.setdefault(r["cell"], []).append(r)
    order = ["not_climate|untagged", "not_climate|tagged", "climate_specific|untagged", "climate_specific|tagged",
             "climate_nonspecific|untagged", "climate_nonspecific|tagged"]
    target = dict(zip(order, [34, 33, 33, 33, 34, 33]))
    rng = np.random.default_rng(SEED)
    queues = {}
    for c in order:  # seeded random order within each cell (frame order is stable: paragraphs.csv order)
        lst = sorted(cells.get(c, []), key=lambda r: r["id"])
        queues[c] = [lst[i] for i in rng.permutation(len(lst))]
    # shortfall: move unmet target to the sibling cell of the same class, then to any cell
    for c in order:
        short = target[c] - len(queues[c])
        if short > 0:
            target[c] -= short
            sib = [x for x in order if x.split("|")[0] == c.split("|")[0] and x != c] + order
            for s in sib:
                room = len(queues[s]) - target[s]
                add = min(room, short)
                if add > 0:
                    target[s] += add; short -= add
                if short == 0:
                    break
    picked, firm_n, fs_n, got = [], {}, 0, {c: 0 for c in order}
    pos = {c: 0 for c in order}
    while len(picked) < N:
        progress = False
        for c in order:
            if got[c] >= target[c]:
                continue
            q = queues[c]
            while pos[c] < len(q):
                r = q[pos[c]]; pos[c] += 1
                if firm_n.get(r["firm"], 0) >= FIRM_CAP or (r["doc_type"] == "FS" and fs_n >= FS_CAP):
                    continue
                picked.append(r); got[c] += 1; firm_n[r["firm"]] = firm_n.get(r["firm"], 0) + 1
                fs_n += r["doc_type"] == "FS"; progress = True
                break
            if len(picked) >= N:
                break
        if not progress:
            # a cell ran out under the caps: give its remaining target to any cell that still has candidates
            # (A19: the sibling cell of the same prediction class first, then any cell, in cell order)
            if not any(pos[c] < len(queues[c]) for c in order):
                break
            for c in order:
                if got[c] < target[c] and pos[c] >= len(queues[c]):
                    sib = [x for x in order if x.split("|")[0] == c.split("|")[0] and x != c] + order
                    s = next(x for x in sib if pos[x] < len(queues[x]))
                    target[s] += target[c] - got[c]; target[c] = got[c]
    p1 = [picked[i] for i in rng.permutation(len(picked))]
    p2 = [picked[i] for i in np.random.default_rng(SEED + 1).permutation(len(picked))]
    for path, rows in ((I / "validation_sample.csv", p1), (I / "validation_sample_pass2.csv", p2)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, ["id", "firm", "year", "text"], extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    with open(I / "validation_strata.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["id", "firm", "year", "doc", "doc_type", "cell", "p_climate", "p_spec", "hazard_tag",
                               "frame_cell_size", "sampled_cell_size", "weight"], extrasaction="ignore")
        w.writeheader()
        for r in p1:
            nc, sc = len(cells[r["cell"]]), got[r["cell"]]
            w.writerow({**r, "frame_cell_size": nc, "sampled_cell_size": sc, "weight": f"{nc / sc:.4f}"})
    print("sampled", len(picked), "| per cell", got, "| FS rows", fs_n, "| firms", len(firm_n), "| max per firm", max(firm_n.values()))


if __name__ == "__main__":
    if sys.argv[1] == "predict":
        predict(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9)
    elif sys.argv[1] == "draw":
        draw()
