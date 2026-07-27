"""
Summarization helpers backed by the LLM router when available.
- summarize_text(text, max_chars=1000) -> str
- summarize_messages(messages: List[dict], max_chars=1000) -> str
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("memory.summarizer")

# Try to use core.llm.llm_router if present
try:
    from core.llm import llm_router  # type: ignore
    _HAS_LLM = True
except Exception:
    llm_router = None
    _HAS_LLM = False


async def summarize_text(text: str, max_chars: int = 800) -> str:
    """
    Summarize arbitrary text using the LLM if available; otherwise fallback heuristic.
    """
    if _HAS_LLM and llm_router:
        prompt_system = {"role": "system", "content": "You are a concise summarizer. Produce a brief summary."}
        prompt_user = {"role": "user", "content": f"Summarize the following text in up to {max_chars} characters:\n\n{text}"}
        try:
            resp = await llm_router.generate([prompt_system, prompt_user], temperature=0.2)
            # resp may be ProviderResponse
            summary = getattr(resp, "text", None) or resp.get("text", str(resp)) if isinstance(resp, dict) else str(resp)
            return summary.strip()[:max_chars]
        except Exception as exc:
            logger.warning("LLM summarization failed: %s", exc)

    # Fallback trivial summarizer: take first N characters/first sentences
    if not text:
        return ""
    # simple heuristic: first 2 sentences or up to max_chars
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    out = ""
    for s in sentences:
        if len(out) + len(s) <= max_chars:
            out += (" " + s) if out else s
        else:
            break
    return out[:max_chars]


async def summarize_messages(messages: List[Dict[str, str]], max_chars: int = 800) -> str:
    """
    messages: [{"role": "...", "content": "..."}]
    Concatenate and call summarize_text.
    """
    text = "\n".join([f"{m.get('role','')}: {m.get('content','')}" for m in messages])
    return await summarize_text(text, max_chars=max_chars)