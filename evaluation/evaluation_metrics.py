"""
Common metric wrappers used by evaluation scripts.
Uses the `evaluate` package when available, else falls back to simple implementations.
"""
import json
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger("evaluation.metrics")

# optional libs
try:
    import evaluate as hf_evaluate  # type: ignore
    _HAS_EVALUATE = True
except Exception:
    hf_evaluate = None
    _HAS_EVALUATE = False

try:
    import numpy as np  # type: ignore
    _HAS_NUMPY = True
except Exception:
    np = None
    _HAS_NUMPY = False

# ROUGE wrapper
def compute_rouge(preds: List[str], refs: List[str]) -> Dict:
    if _HAS_EVALUATE:
        rouge = hf_evaluate.load("rouge")
        res = rouge.compute(predictions=preds, references=refs)
        return res
    # fallback: naive approximate rouge-l by longest common substring ratio (very rough)
    def lcs(a: str, b: str) -> int:
        # dynamic programming lcs of tokens
        at = a.split()
        bt = b.split()
        m = len(at); n = len(bt)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(m-1,-1,-1):
            for j in range(n-1,-1,-1):
                if at[i] == bt[j]:
                    dp[i][j] = dp[i+1][j+1] + 1
                else:
                    dp[i][j] = max(dp[i+1][j], dp[i][j+1])
        return dp[0][0]
    scores = {"rouge-l": 0.0}
    total = 0.0
    for p,r in zip(preds, refs):
        l = lcs(p, r)
        denom = max(1, len(r.split()))
        total += l/denom
    scores["rouge-l"] = total / max(1, len(preds))
    return scores

def compute_bleu(preds: List[str], refs: List[str]) -> Dict:
    if _HAS_EVALUATE:
        bleu = hf_evaluate.load("bleu")
        return bleu.compute(predictions=preds, references=[[r] for r in refs])
    # fallback: use sacrebleu package if available
    try:
        import sacrebleu  # type: ignore
        refs_list = [refs]
        res = sacrebleu.corpus_bleu(preds, refs_list)
        return {"bleu": res.score}
    except Exception:
        return {"bleu": 0.0}

def compute_bertscore(preds: List[str], refs: List[str], lang: str = "en") -> Dict:
    try:
        from bert_score import score as bertscore  # type: ignore
        P, R, F = bertscore(preds, refs, lang=lang, rescale_with_baseline=True)
        return {"precision": float(P.mean().item()), "recall": float(R.mean().item()), "f1": float(F.mean().item())}
    except Exception as exc:
        logger.warning("bert-score unavailable: %s", exc)
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

def compute_sacrebleu(preds: List[str], refs: List[str]) -> Dict:
    try:
        import sacrebleu  # type: ignore
        res = sacrebleu.corpus_bleu(preds, [refs])
        return {"sacrebleu": res.score}
    except Exception:
        return {"sacrebleu": 0.0}

def compute_generation_metrics(preds: List[str], refs: List[str], metrics: Optional[List[str]] = None, lang: str = "en") -> Dict:
    metrics = metrics or ["rouge", "bleu", "sacrebleu", "bertscore"]
    out = {}
    if "rouge" in metrics:
        out.update({"rouge": compute_rouge(preds, refs)})
    if "bleu" in metrics:
        out.update({"bleu": compute_bleu(preds, refs)})
    if "sacrebleu" in metrics:
        out.update({"sacrebleu": compute_sacrebleu(preds, refs)})
    if "bertscore" in metrics:
        out.update({"bertscore": compute_bertscore(preds, refs, lang=lang)})
    return out

# Retriever metrics
def recall_at_k(retrieved_lists: List[List[str]], positives: List[List[str]], k: int = 10) -> float:
    """
    retrieved_lists: list per query of retrieved doc ids (ordered)
    positives: list per query of positive doc ids (list or set)
    returns recall@k averaged over queries
    """
    total = 0
    hits = 0
    for retrieved, pos in zip(retrieved_lists, positives):
        total += 1
        topk = set(retrieved[:k])
        if any(p in topk for p in pos):
            hits += 1
    return hits / total if total else 0.0

def precision_at_k(retrieved_lists: List[List[str]], positives: List[List[str]], k: int = 10) -> float:
    total = 0
    scores = 0.0
    for retrieved, pos in zip(retrieved_lists, positives):
        total += 1
        topk = retrieved[:k]
        if not topk:
            continue
        scores += sum(1 for r in topk if r in pos) / len(topk)
    return scores / total if total else 0.0

def mrr_at_k(retrieved_lists: List[List[str]], positives: List[List[str]], k: int = 10) -> float:
    """
    Mean Reciprocal Rank @k
    """
    total = 0
    score = 0.0
    for retrieved, pos in zip(retrieved_lists, positives):
        total += 1
        rr = 0.0
        for i, r in enumerate(retrieved[:k], start=1):
            if r in pos:
                rr = 1.0 / i
                break
        score += rr
    return score / total if total else 0.0

def ndcg_at_k(retrieved_lists: List[List[str]], positives: List[List[str]], k: int = 10) -> float:
    try:
        import numpy as np  # type: ignore
    except Exception:
        return 0.0
    total = 0.0
    for retrieved, pos in zip(retrieved_lists, positives):
        gains = [1.0 if r in pos else 0.0 for r in retrieved[:k]]
        discounts = [1.0 / (np.log2(i + 2)) for i in range(len(gains))]
        dcg = sum(g * d for g, d in zip(gains, discounts))
        ideal_gains = sorted(gains, reverse=True)
        idcg = sum(g * d for g, d in zip(ideal_gains, discounts))
        total += (dcg / idcg) if idcg > 0 else 0.0
    return float(total / len(retrieved_lists)) if retrieved_lists else 0.0