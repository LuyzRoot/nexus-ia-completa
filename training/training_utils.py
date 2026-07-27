import random
import os
import logging
import json
from typing import Tuple, List, Dict
from pathlib import Path

logger = logging.getLogger("training.utils")
logging.basicConfig(level=logging.INFO)


def set_seed(seed: int):
    random.seed(seed)
    try:
        import numpy as np
        import torch
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def ensure_dir(path: str):
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def train_val_split(items: List[Dict], val_ratio: float = 0.1, seed: int = 42) -> Tuple[List[Dict], List[Dict]]:
    random = __import__("random")
    random.seed(seed)
    items_copy = items.copy()
    random.shuffle(items_copy)
    n_val = int(len(items_copy) * val_ratio)
    return items_copy[n_val:], items_copy[:n_val]


def read_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def write_jsonl(items: List[Dict], path: str):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")