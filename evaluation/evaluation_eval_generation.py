"""
Evaluate generation outputs.

Inputs:
- --pred: predictions.jsonl OR a file where each line has {"id","prediction"}
- --refs: references.jsonl OR a file where each line has {"id","reference"}
  If one JSONL contains both fields, pass it as --both

Outputs JSON metrics (or print to stdout).

Usage:
python evaluation/eval_generation.py --pred predictions.jsonl --refs references.jsonl --out results.json
"""
import argparse
import json
import logging
from typing import List, Dict
from evaluation.metrics import compute_generation_metrics

logger = logging.getLogger("evaluation.eval_generation")
logging.basicConfig(level=logging.INFO)


def load_jsonl_to_map(path: str, key_field="id", value_field=None) -> Dict[str, Dict]:
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            if value_field:
                out[obj[key_field]] = obj.get(value_field, "")
            else:
                out[obj[key_field]] = obj
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", help="predictions jsonl (each line: {'id','prediction'})")
    parser.add_argument("--refs", help="references jsonl (each line: {'id','reference'})")
    parser.add_argument("--both", help="single file with both prediction and reference per line (fields 'prediction' and 'reference')")
    parser.add_argument("--metrics", nargs="+", default=None)
    parser.add_argument("--lang", default="en")
    parser.add_argument("--out", help="output JSON file", default=None)
    args = parser.parse_args()

    preds = {}
    refs = {}
    if args.both:
        with open(args.both, "r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                o = json.loads(line)
                _id = o.get("id")
                if not _id:
                    continue
                preds[_id] = o.get("prediction","")
                refs[_id] = o.get("reference","")
    else:
        if not args.pred or not args.refs:
            raise RuntimeError("Either --both or both --pred and --refs must be provided")
        preds = load_jsonl_to_map(args.pred, value_field="prediction")
        refs = load_jsonl_to_map(args.refs, value_field="reference")

    # align by id
    ids = [i for i in preds.keys() if i in refs]
    pred_list = [preds[i] for i in ids]
    ref_list = [refs[i] for i in ids]

    metrics = compute_generation_metrics(pred_list, ref_list, metrics=args.metrics, lang=args.lang)
    logger.info("Generation metrics computed: %s", metrics)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()