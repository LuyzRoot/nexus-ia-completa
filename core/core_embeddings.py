name=core/embeddings.py
"""
Embeddings wrapper with provider selection.
Tries OpenAI via 'openai' package if OPENAI_API_KEY is present; otherwise returns mock vectors.
"""
from typing import List
import logging
from app.config.settings import settings

logger = logging.getLogger("core.embeddings")

try:
    import openai  # type: ignore
    _HAS_OPENAI = True
except Exception:
    openai = None
    _HAS_OPENAI = False

async def embed_text(text: str) -> List[float]:
    """
    Return a vector embedding for `text`.
    If no provider configured, return a deterministic mock vector (hash-based).
    """
    if getattr(settings, "OPENAI_API_KEY", "") and _HAS_OPENAI:
        try:
            openai.api_key = settings.OPENAI_API_KEY
            # adjust model name as needed
            model = getattr(settings, "OPENAI_MODEL", "text-embedding-3-small")
            resp = openai.Embedding.create(model=model, input=text)
            return resp["data"][0]["embedding"]
        except Exception as exc:
            logger.warning("OpenAI embedding call failed: %s", exc)

    # mock deterministic embedding (not useful for real RAG but OK for dev)
    import hashlib
    h = hashlib.sha256(text.encode()).digest()
    # convert bytes to floats in [0,1)
    vec = [b / 255.0 for b in h]
    return vec