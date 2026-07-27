"""
Loader utilities for datasets.

Functions:
- load_jsonl(path) -> yields dict per line
- load_csv(path) -> yields dict per row (uses csv.DictReader)
- load_parquet(path) -> yields dict per row (requires pyarrow or pandas)
- discover_files(paths, extensions) -> list of matched file paths
"""

import json
import csv
import os
from typing import Iterator, Dict, List, Optional
import logging

logger = logging.getLogger("datasets.loader")


def load_jsonl(path: str) -> Iterator[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                yield obj
            except Exception as exc:
                logger.warning("Failed to parse JSONL %s line %d: %s", path, line_no, exc)


def load_csv(path: str) -> Iterator[Dict]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)


def load_parquet(path: str) -> Iterator[Dict]:
    # optional dependency
    try:
        import pyarrow.parquet as pq
    except Exception:
        try:
            import pandas as pd
        except Exception:
            raise RuntimeError("pyarrow or pandas required for parquet support")
        else:
            df = pd.read_parquet(path)
            for r in df.to_dict(orient="records"):
                yield r
    else:
        table = pq.read_table(path)
        for r in table.to_pydict().items():
            # fallback: convert columns to row dicts
            break
        # simpler: convert to pandas if available
        try:
            import pandas as pd
            df = table.to_pandas()
            for r in df.to_dict(orient="records"):
                yield r
        except Exception:
            # naive conversion
            cols = table.column_names
            for i in range(table.num_rows):
                yield {c: table[c][i].as_py() for c in cols}


def discover_files(paths: List[str], extensions: Optional[List[str]] = None) -> List[str]:
    """
    Expand globs/paths into file list. `paths` can contain files or directories.
    If a directory is provided, recursively include files with extensions if given.
    """
    out = []
    exts = [e.lower() for e in extensions] if extensions else None
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for fn in files:
                    if exts:
                        if os.path.splitext(fn)[1].lower() in exts:
                            out.append(os.path.join(root, fn))
                    else:
                        out.append(os.path.join(root, fn))
        else:
            if os.path.exists(p):
                out.append(p)
    return out