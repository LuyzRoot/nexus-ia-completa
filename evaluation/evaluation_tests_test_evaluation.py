import os
import json
import tempfile
from evaluation.metrics import compute_generation_metrics, recall_at_k, mrr_at_k

def test_generation_metrics_basic():
    preds = ["hello world", "foo bar"]
    refs = ["hello world", "foo baz"]
    res = compute_generation_metrics(preds, refs, metrics=["rouge","bleu"], lang="en")
    assert "rouge" in res
    assert "bleu" in res

def test_retriever_metrics_basic():
    retrieved = [["d1","d2","d3"], ["d4","d5"]]
    positives = [["d2"], ["d6"]]
    r1 = recall_at_k(retrieved, positives, k=1)
    r3 = recall_at_k(retrieved, positives, k=3)
    assert r1 <= r3
    mrr = mrr_at_k(retrieved, positives, k=3)
    assert 0.0 <= mrr <= 1.0