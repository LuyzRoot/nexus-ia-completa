"""
Reranker: optionally call the LLM to re-score or filter candidates.
Tries to use core.llm.llm_router.generate; falls back to preserving similarity scores if not available.
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger("rag.reranker")

try:
    from core.llm import llm_router  # type: ignore
    _HAS_LLM = True
except Exception:
    llm_router = None
    _HAS_LLM = False


class Reranker:
    def __init__(self, max_context_chars: int = 1500):
        self.max_context_chars = max_context_chars

    async def rerank(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Send a prompt to the LLM asking to reorder/rerank the candidates by relevance and return the new list.
        Prompt format is intentionally simple; adapt for your LLM's preferred schema.
        """
        if not _HAS_LLM or llm_router is None:
            logger.debug("No LLM available for reranking; returning original candidates")
            return candidates

        # Build a compact prompt containing query and candidate excerpts (truncate to fit)
        lines = [f"Query: {query}\n\nCandidates:"]
        for i, c in enumerate(candidates):
            text = c.get("text", "") or c["metadata"].get("excerpt", "")
            excerpt = (text[:self.max_context_chars] + "...") if len(text) > self.max_context_chars else text
            lines.append(f"{i+1}. {excerpt}")
        lines.append("\nTask: Rank the candidates from most relevant to least relevant. "
                     "Return a JSON array of indices in the new order, e.g. [2,0,1].")
        prompt = "\n".join(lines)

        system = {"role": "system", "content": "You are a relevance-ranking assistant."}
        user = {"role": "user", "content": prompt}

        try:
            resp = await llm_router.generate([system, user], temperature=0.0)
            text = getattr(resp, "text", None) or (resp.get("text") if isinstance(resp, dict) else str(resp))
            import json
            try:
                order = json.loads(text.strip())
                if isinstance(order, list) and all(isinstance(i, int) for i in order):
                    ordered = [candidates[i] for i in order if 0 <= i < len(candidates)]
                    # Append any not mentioned preserving original order
                    remaining = [c for i, c in enumerate(candidates) if i not in order]
                    return ordered + remaining
            except Exception:
                # fallback: attempt to parse simple numbered list or plain text; if fails, ignore
                logger.debug("Reranker parse failed; resp: %s", text)
        except Exception as exc:
            logger.warning("Reranker LLM call failed: %s", exc)

        return candidates