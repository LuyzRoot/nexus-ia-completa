"""
Vector store abstraction with two implementations:
- PostgreSQL + pgvector (if available)
- In-memory fallback (simple list + cosine similarity)

API:
- VectorStore.add_document(id, text, metadata)
- VectorStore.search(query, top_k=5) -> list of (id, score, metadata)
- get_default_vector_store() -> VectorStore instance
"""
from typing import List, Tuple, Dict, Optional
import logging
import math

logger = logging.getLogger("memory.vector_store")

# Try optional dependencies
try:
    from pgvector.sqlalchemy import Vector  # type: ignore
    _HAS_PGVECTOR = True
except Exception:
    _HAS_PGVECTOR = False

try:
    import numpy as np  # optional for faster ops
    _HAS_NUMPY = True
except Exception:
    np = None
    _HAS_NUMPY = False

from app.config.settings import settings
from core.embeddings import embed_text

class BaseVectorStore:
    async def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None):
        raise NotImplementedError

    async def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        raise NotImplementedError

# Simple in-memory store
class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self._items: List[Tuple[str, List[float], Dict]] = []

    async def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None):
        vec = await embed_text(text)
        self._items.append((doc_id, vec, metadata or {}))

    def _cosine(self, a: List[float], b: List[float]) -> float:
        # simple cosine similarity
        if _HAS_NUMPY:
            return float(np.dot(np.array(a), np.array(b)) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
        # pure python
        dot = sum(x*y for x,y in zip(a,b))
        norm_a = math.sqrt(sum(x*x for x in a))
        norm_b = math.sqrt(sum(x*x for x in b))
        denom = (norm_a * norm_b) if norm_a and norm_b else 1e-12
        return dot / denom

    async def search(self, query: str, top_k: int = 5):
        qv = await embed_text(query)
        scores = []
        for doc_id, vec, meta in self._items:
            # if vector sizes mismatch, use min length
            n = min(len(vec), len(qv))
            score = self._cosine(vec[:n], qv[:n])
            scores.append((doc_id, score, meta))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# Factory
_default_store: Optional[BaseVectorStore] = None

def get_default_vector_store() -> BaseVectorStore:
    global _default_store
    if _default_store is None:
        # For now always use in-memory; you may switch to PGVector if installed and configured
        _default_store = InMemoryVectorStore()
    return _default_store