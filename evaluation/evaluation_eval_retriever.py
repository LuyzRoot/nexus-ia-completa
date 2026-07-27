"""
Evaluate retriever performance.

Input JSONL lines format:
{
  "query": "text",
  "positive_ids": ["id1","id2"],
  "retrieved": ["docA","docB","docC"]
}

Outputs recall@k, precision@k, MRR and NDCG.

Usage:
python evaluation/eval_retriever.py --file retriever_results.jsonl --ks 1 3 5 10 --out retriever_metrics.json
"""
import argparse
import json
import logging
from typing import List
from evaluation.metrics import recall_at_k, precision_at_k, mrr_at_k, ndcg_at_k

logger = logging.getLogger("evaluation.eval_retriever")
logging.basicConfig(level=logging.INFO)


def load_retriever_file(path: str):
    queries = []
    positives = []
    retrieved = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            queries.append(obj.get("query"))
            positives.append(obj.get("positive_ids", []))
            retrieved.append(obj.get("retrieved", []))
    return queries, positives, retrieved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="input jsonl file")
    parser.add_argument("--ks", nargs="+", type=int, default=[1,3,5,10])
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    queries, positives, retrieved = load_retriever_file(args.file)
    results = {}
    for k in args.ks:
        results[f"recall@{k}"] = recall_at_k(retrieved, positives, k=k)
        results[f"precision@{k}"] = precision_at_k(retrieved, positives, k=k)
        results[f"mrr@{k}"] = mrr_at_k(retrieved, positives, k=k)
        results[f"ndcg@{k}"] = ndcg_at_k(retrieved, positives, k=k)

    logger.info("Retriever metrics: %s", results)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()