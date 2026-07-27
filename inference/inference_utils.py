"""
Utilities for inference service.
- basic payload validation
- token estimation wrapper (calls core.tokenizer)
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("inference.utils")

try:
    from core.tokenizer import estimate_tokens_from_messages
    _HAS_TOKENIZER = True
except Exception:
    _HAS_TOKENIZER = False

def estimate_tokens(messages: List[Dict[str, str]], model: Optional[str] = None) -> Optional[int]:
    if not _HAS_TOKENIZER:
        return None
    try:
        return estimate_tokens_from_messages(messages, model=model)
    except Exception:
        return None