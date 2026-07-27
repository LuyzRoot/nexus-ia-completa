"""
Lightweight DB tool for read-only queries.
- read_query(sql, max_rows=100) -> list[dict]
Only allows SELECT queries by simple validation (checks beginswith SELECT).
Use with caution — do not expose to untrusted users without sanitization.
"""
from typing import List, Dict
import logging
from sqlalchemy import create_engine, text
from app.config import settings

logger = logging.getLogger("tools.database")

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(settings.DATABASE_URL)
    return _engine

def _is_select_query(q: str) -> bool:
    q = q.strip().lower()
    return q.startswith("select") or q.startswith("with")  # allow CTEs with WITH

def read_query(sql: str, max_rows: int = 100) -> List[Dict]:
    if not _is_select_query(sql):
        raise PermissionError("Only SELECT/READ queries are allowed")
    eng = _get_engine()
    with eng.connect() as conn:
        res = conn.execute(text(sql))
        cols = res.keys()
        rows = []
        for i, r in enumerate(res):
            if i >= max_rows:
                break
            rows.append({c: r[idx] for idx, c in enumerate(cols)})
        return rows