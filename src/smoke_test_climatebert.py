"""Phase 0, Task 6: operational smoke test of one ClimateBERT classifier on 20 paragraphs of one report.

Run once per model, each in its own process, so memory is released between models. Records whether the
model loads and returns valid output. Predicted labels and scores are checked but deliberately never
printed or saved: this is an access test, not an analysis.

usage: smoke_test_climatebert.py PATH_TO_PDF MODEL_INDEX(0-3)
Output: data/interim/nlp_smoke_test.json (one entry per model)
"""
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "hf_cache"
OUT = ROOT / "data" / "interim" / "nlp_smoke_test.json"
MODELS = [
    "climatebert/distilroberta-base-climate-detector",
    "climatebert/distilroberta-base-climate-specificity",
    "climatebert/distilroberta-base-climate-tcfd",
    "climatebert/distilroberta-base-climate-sentiment",
]
N_PARAGRAPHS = 20
MIN_WORDS = 40
MAX_LENGTH = 512

import pymupdf  # noqa: E402
import torch  # noqa: E402
from huggingface_hub import HfApi, hf_hub_download  # noqa: E402
from transformers import AutoModelForSequenceClassification, AutoTokenizer  # noqa: E402


def paragraphs(pdf: Path) -> tuple[list[str], int]:
    """Take N evenly spaced text blocks, so selection does not depend on their content."""
    blocks = []
    with pymupdf.open(pdf) as doc:
        for page in doc:
            for block in page.get_text("blocks"):
                text = " ".join(block[4].split())
                if block[6] == 0 and len(text.split()) >= MIN_WORDS:
                    blocks.append(text)
    if len(blocks) < N_PARAGRAPHS:
        sys.exit(f"Only {len(blocks)} candidate paragraphs in {pdf}")
    step = len(blocks) / N_PARAGRAPHS
    return [blocks[int(i * step)] for i in range(N_PARAGRAPHS)], len(blocks)


def fetch_model(model_id: str) -> list[str]:
    """Download one file at a time, at least 2 s apart. Prefer safetensors over pickled weights."""
    names = [s.rfilename for s in HfApi().model_info(model_id).siblings]
    weights = [n for n in names if n.endswith(".safetensors")] or [n for n in names if n == "pytorch_model.bin"]
    support = [n for n in names if n in ("config.json", "tokenizer.json", "tokenizer_config.json", "vocab.json",
                                         "merges.txt", "special_tokens_map.json")]
    for name in support + weights:
        time.sleep(2.0)
        hf_hub_download(model_id, name, cache_dir=CACHE)
    return weights


def test_model(model_id: str, texts: list[str]) -> dict:
    result = {"model": model_id, "loaded": False, "works": False}
    try:
        weights = fetch_model(model_id)
        result["weights_file"] = weights
        tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=CACHE, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_id, cache_dir=CACHE, local_files_only=True, trust_remote_code=False,
            use_safetensors=weights[0].endswith(".safetensors"),
        ).eval()
        result["loaded"] = True
        labels = model.config.id2label
        lengths = [len(tokenizer(t, truncation=False)["input_ids"]) for t in texts]
        valid, finite = 0, True
        start = time.perf_counter()
        with torch.no_grad():
            for text in texts:  # one paragraph at a time to keep peak memory low
                batch = tokenizer(text, truncation=True, max_length=MAX_LENGTH, return_tensors="pt")
                probs = torch.softmax(model(**batch).logits, dim=-1)
                finite = finite and bool(torch.isfinite(probs).all())
                valid += int(probs.argmax(dim=-1).item() in labels)
        result.update(
            n_inputs=len(texts), n_valid_outputs=valid, probabilities_finite=finite,
            label_set=sorted(labels.values()), max_position_embeddings=model.config.max_position_embeddings,
            tokens_median=int(statistics.median(lengths)), tokens_max=max(lengths),
            inputs_truncated=sum(n > MAX_LENGTH for n in lengths),
            cpu_seconds=round(time.perf_counter() - start, 2),
            works=valid == len(texts) and finite,
        )
    except Exception as exc:  # a failing model is itself the audit result
        result["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
    return result


def main() -> None:
    pdf, index = Path(sys.argv[1]), int(sys.argv[2])
    torch.set_num_threads(2)
    texts, candidates = paragraphs(pdf)
    report = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"models": {}}
    report.update(
        source_pdf=str(pdf).replace("\\", "/"),
        selection=f"{N_PARAGRAPHS} evenly spaced PyMuPDF text blocks of at least {MIN_WORDS} words",
        candidate_blocks=candidates,
        note="Predicted labels and scores are intentionally not recorded.",
        torch=torch.__version__,
    )
    entry = test_model(MODELS[index], texts)
    report["models"][MODELS[index]] = entry
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(entry, indent=2))
    sys.exit(0 if entry["works"] else 1)


if __name__ == "__main__":
    main()
