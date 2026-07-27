"""
Simple evaluation utilities.

- evaluate_lm: compute perplexity (approx) or use evaluate package (rouge/sacrebleu)
- evaluate_retriever: compute recall@k by checking if ground-truth doc id appears in top_k
"""
import argparse
import logging
import json
from typing import List, Dict
from datasets import load_dataset
import evaluate
import os

logger = logging.getLogger("training.evaluate")
logging.basicConfig(level=logging.INFO)


def evaluate_generation(predictions_file: str, references_file: str):
    """
    predictions_file and references_file: JSONL with {'id','text'} - compare texts by rouge/sacrebleu
    """
    preds = [p for p in load_jsonl(predictions_file)]
    refs = {r['id']: r for r in load_jsonl(references_file)}
    hyps = []
    refs_texts = []
    for p in preds:
        ref = refs.get(p['id'])
        if not ref:
            continue
        hyps.append(p['text'])
        refs_texts.append(ref['text'])

    rouge = evaluate.load("rouge")
    rouge_res = rouge.compute(predictions=hyps, references=refs_texts)
    sacre = evaluate.load("sacrebleu")
    # sacrebleu expects tokenized references; this is simplistic
    try:
        sacre_res = sacre.compute(predictions=hyps, references=[[r] for r in refs_texts])
    except Exception:
        sacre_res = {}
    return {"rouge": rouge_res, "sacrebleu": sacre_res}


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def evaluate_retriever(prediction_queries_file: str, rerank=False):
    """
    prediction_queries_file: JSONL where each record {'query':..., 'positive_ids':[...]}.
    This assumes you query the index externally and collect top_k results; this helper just computes recall over provided results.
    Expected format per line: {'query':..., 'positive_ids':[...], 'retrieved':[id1,id2,...]}
    """
    total = 0
    hit = 0
    for r in load_jsonl(prediction_queries_file):
        total += 1
        positives = set(r.get("positive_ids", []))
        retrieved = r.get("retrieved", [])
        if any(d in positives for d in retrieved[:10]):
            hit += 1
    recall_at_10 = hit / total if total else 0.0
    return {"recall@10": recall_at_10}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", help="predictions jsonl")
    parser.add_argument("--references", help="references jsonl")
    args = parser.parse_args()
    if args.predictions and args.references:
        res = evaluate_generation(args.predictions, args.references)
        print(json.dumps(res, indent=2))