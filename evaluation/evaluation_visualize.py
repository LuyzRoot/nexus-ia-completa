"""
Plotting helpers to visualize evaluation results.

Requires matplotlib and seaborn (optional). Functions:
- plot_recall_curve(ks, recalls, labels, out_file)
- plot_metric_bar(metrics_dict, out_file)
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("evaluation.visualize")

try:
    import matplotlib.pyplot as plt  # type: ignore
    import seaborn as sns  # type: ignore
    _HAS_PLOT = True
except Exception:
    _HAS_PLOT = False

def plot_recall_curve(ks: List[int], recalls: List[List[float]], labels: List[str], out_file: Optional[str] = None):
    if not _HAS_PLOT:
        raise RuntimeError("matplotlib/seaborn required for plotting")
    sns.set(style="whitegrid")
    plt.figure(figsize=(6,4), dpi=120)
    for rec, label in zip(recalls, labels):
        plt.plot(ks, rec, marker="o", label=label)
    plt.xlabel("k")
    plt.ylabel("Recall@k")
    plt.legend()
    plt.tight_layout()
    if out_file:
        plt.savefig(out_file)
    else:
        plt.show()

def plot_metric_bar(metrics_dict: Dict[str, float], title: str = "Metrics", out_file: Optional[str] = None):
    if not _HAS_PLOT:
        raise RuntimeError("matplotlib/seaborn required for plotting")
    import pandas as pd  # type: ignore
    df = pd.DataFrame(list(metrics_dict.items()), columns=["metric","value"])
    sns.barplot(data=df, x="metric", y="value")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    if out_file:
        plt.savefig(out_file)
    else:
        plt.show()