"""
Prepare dataset files for training.

- Input JSONL/CSV where each record contains an 'id' and one or more text fields.
- For LM fine-tuning, output JSONL with {"id":..., "text": ...}
- For embedding/reranker training, will optionally create TSV with pairs/labels.
"""
import argparse
import json
import logging
from typing import List, Dict
import os

from training.utils import read_jsonl, write_jsonl, ensure_dir, train_val_split, set_seed

logger = logging.getLogger("training.prepare_data")
logging.basicConfig(level=logging.INFO)


def prepare_for_lm(input_path: str, out_dir: str, text_field: str = "text", id_field: str = "id", val_ratio: float = 0.1, seed: int = 42):
    items = []
    if input_path.lower().endswith(".jsonl"):
        for obj in read_jsonl(input_path):
            text = obj.get(text_field) or obj.get("content") or obj.get("body")
            if not text:
                continue
            items.append({"id": obj.get(id_field) or obj.get("uid") or str(len(items)), "text": text})
    else:
        raise RuntimeError("Only jsonl supported by this helper for now")

    set_seed(seed)
    train, val = train_val_split(items, val_ratio=val_ratio, seed=seed)
    ensure_dir(out_dir)
    write_jsonl(train, os.path.join(out_dir, "train.jsonl"))
    write_jsonl(val, os.path.join(out_dir, "val.jsonl"))
    logger.info("Prepared LM dataset: train=%d val=%d -> %s", len(train), len(val), out_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--out-dir", default="training/data/processed")
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    prepare_for_lm(args.input, args.out_dir, text_field=args.text_field, id_field=args.id_field, val_ratio=args.val_ratio, seed=args.seed)


if __name__ == "__main__":
    main()