"""
Retriever orchestrates retrieval + optional reranking.
- retrieve(query, top_k, rerank=True) -> list of passages (text, metadata, score)
"""
from typing import List, Dict, Any, Tuple, Optional
import logging

from rag.index import RAGIndex
from rag.reranker import Reranker

logger = logging.getLogger("rag.retriever")


class Retriever:
    def __init__(self, index: RAGIndex, reranker: Optional[Reranker] = None):
        self.index = index
        self.reranker = reranker

    async def retrieve(self, query: str, top_k: int = 5, rerank: bool = True) -> List[Dict[str, Any]]:
        raw = await self.index.search(query, top_k=top_k)
        # raw: list of (doc_id, score, metadata)
        candidates = []
        for doc_id, score, metadata in raw:
            text = await self.index.get_document_text(doc_id) or metadata.get("text") or metadata.get("excerpt") or ""
            candidates.append({"id": doc_id, "score": score, "metadata": metadata or {}, "text": text})

        if rerank and self.reranker:
            try:
                reranked = await self.reranker.rerank(query, candidates)
                return reranked
            except Exception as exc:
                logger.warning("Reranker failed: %s", exc)
                # fallback to original ordering
        # sort by score desc
        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        return candidates