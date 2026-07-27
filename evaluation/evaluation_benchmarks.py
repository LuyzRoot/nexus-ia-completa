"""
Run benchmark comparisons across multiple models/strategies.

Example usage (pseudo):
- generate predictions from different model configs and save predictions_{model}.jsonl
- run this script to compute metrics for each and output a summary CSV

Features:
- Accepts a mapping file (YAML/JSON) listing label/pred files
- Computes generation metrics or retriever metrics depending on type
"""
import argparse
import json
import csv
import logging
import os
from typing import Dict, List

from evaluation.eval_generation import load_jsonl_to_map
from evaluation.metrics import compute_generation_metrics

logger = logging.getLogger("evaluation.benchmarks")
logging.basicConfig(level=logging.INFO)


def run_generation_benchmark(mapping: Dict[str, Dict[str, str]], out_csv: str, metrics: List[str] = None):
    """
    mapping: { 'model_name': { 'pred': 'path', 'refs': 'path' }, ... }
    """
    rows = []
    for model_name, files in mapping.items():
        pred_path = files.get("pred")
        ref_path = files.get("refs")
        if not pred_path or not ref_path:
            logger.warning("Skipping %s: pred or refs missing", model_name)
            continue
        preds_map = load_jsonl_to_map(pred_path, value_field="prediction")
        refs_map = load_jsonl_to_map(ref_path, value_field="reference")
        ids = [i for i in preds_map.keys() if i in refs_map]
        preds = [preds_map[i] for i in ids]
        refs = [refs_map[i] for i in ids]
        res = compute_generation_metrics(preds, refs, metrics=metrics)
        # flatten results into single row (stringify nested dicts)
        flat = {"model": model_name, "num_examples": len(ids)}
        flat.update({k: json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v for k, v in res.items()})
        rows.append(flat)
    # write CSV
    keys = set()
    for r in rows:
        keys.update(r.keys())
    keys = ["model", "num_examples"] + sorted([k for k in keys if k not in ("model","num_examples")])
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in keys})
    logger.info("Benchmark CSV written to %s", out_csv)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", required=True, help="JSON mapping file pointing models to pred/ref files")
    parser.add_argument("--out", required=True, help="output CSV path")
    args = parser.parse_args()
    with open(args.mapping, "r", encoding="utf-8") as fh:
        mapping = json.load(fh)
    run_generation_benchmark(mapping, args.out)


if __name__ == "__main__":
    main()