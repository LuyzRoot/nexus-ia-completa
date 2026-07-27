"""
Predictor abstraction that delegates to core.llm.llm_router and optional RAG Retriever.

API:
- generate(messages, temperature=None, max_tokens=None) -> ProviderResponse
- stream_generate(messages, temperature=None) -> async iterator[str]
- generate_with_retrieval(query, top_k=5, rerank=True) -> (retrieved_list, ProviderResponse)
"""
import logging
from typing import List, Dict, Optional, AsyncIterator, Tuple, Any

from core.llm import llm_router, ProviderResponse  # core.llm created earlier
from core.tokenizer import estimate_tokens_from_messages

logger = logging.getLogger("inference.predictor")

# Try to import RAG retriever
try:
    from rag.index import RAGIndex
    from rag.retriever import Retriever
    from rag.reranker import Reranker
    _HAS_RAG = True
except Exception:
    RAGIndex = Retriever = Reranker = None
    _HAS_RAG = False


class Predictor:
    def __init__(self, rag_index: Optional[RAGIndex] = None, reranker: Optional[Any] = None):
        self.llm = llm_router
        # if rag_index provided override, else attempt to build default if available
        if _HAS_RAG:
            try:
                self.rag_index = rag_index or RAGIndex()
                self.reranker = reranker or Reranker()
                self.retriever = Retriever(self.rag_index, reranker=self.reranker)
            except Exception:
                self.rag_index = None
                self.retriever = None
        else:
            self.rag_index = None
            self.retriever = None

    async def generate(self, messages: List[Dict[str, str]], temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> ProviderResponse:
        # quick token estimation and safety checks
        try:
            toks = estimate_tokens_from_messages(messages)
            logger.debug("Estimated tokens: %d", toks)
        except Exception:
            toks = None
        resp = await self.llm.generate(messages, temperature=temperature)
        return resp

    async def stream_generate(self, messages: List[Dict[str, str]], temperature: Optional[float] = None) -> AsyncIterator[str]:
        # Use llm_router.stream_generate which yields chunks
        async for chunk in self.llm.stream_generate(messages, temperature=temperature):
            yield chunk

    async def generate_with_retrieval(self, query: str, top_k: int = 5, rerank: bool = True) -> Tuple[List[Dict[str, Any]], ProviderResponse]:
        """
        Retrieves top_k passages, then builds a prompt combining retrieved passages and calls LLM.
        Returns (retrieved_list, provider_response)
        """
        retrieved_items = []
        if self.retriever:
            try:
                retrieved_items = await self.retriever.retrieve(query, top_k=top_k, rerank=rerank)
            except Exception as exc:
                logger.warning("Retriever failed: %s", exc)
                retrieved_items = []
        # Build system prompt and messages
        system_content_parts = ["You are an assistant that uses retrieved documents to answer the user's query. Use the documents when relevant. Cite source ids when appropriate."]
        if retrieved_items:
            doc_texts = []
            for i, it in enumerate(retrieved_items):
                excerpt = it.get("text") or it["metadata"].get("excerpt", "") or ""
                doc_texts.append(f"[{i+1}] {it.get('id')} - {excerpt[:400]}")
            system_content_parts.append("Retrieved documents:\n" + "\n\n".join(doc_texts))
        system_msg = {"role": "system", "content": "\n\n".join(system_content_parts)}
        user_msg = {"role": "user", "content": f"Query: {query}\n\nAnswer concisely and reference sources if used."}
        messages = [system_msg, user_msg]
        resp = await self.llm.generate(messages, temperature=0.0)
        return retrieved_items, resp