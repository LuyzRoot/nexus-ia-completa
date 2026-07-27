name=core/tokenizer.py
"""
Tokenizer helpers: token counting estimation.
Attempts to use tiktoken if available; otherwise falls back to a conservative heuristic.
"""
try:
    import tiktoken  # type: ignore
    _HAS_TIKTOKEN = True
except Exception:
    tiktoken = None
    _HAS_TIKTOKEN = False

from typing import List, Dict


def estimate_tokens_from_messages(messages: List[Dict[str, str]], model: str = None) -> int:
    """
    Roughly estimate token usage for a list of messages.
    If tiktoken is available, use it with an appropriate encoding.
    """
    text = ""
    for m in messages:
        text += f"{m.get('role','')}: {m.get('content','')}\n"
    return estimate_tokens_from_text(text, model=model)


def estimate_tokens_from_text(text: str, model: str = None) -> int:
    if _HAS_TIKTOKEN:
        try:
            enc = tiktoken.encoding_for_model(model or "gpt-4o-mini")
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    # fallback heuristic: 1 token ~= 4 chars
    return max(1, int(len(text) / 4))