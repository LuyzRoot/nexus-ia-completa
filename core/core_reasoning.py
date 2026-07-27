name=core/reasoning.py
"""
Small utilities for reasoning chains (placeholder helpers).
These functions help to transform LLM outputs into structured internal representations.
"""

from typing import List, Dict, Any

def extract_action_items(text: str) -> List[Dict[str, str]]:
    """
    Heuristic parser that extracts lines that look like action items (start with dash or number).
    Returns list of {"action": "..."}.
    """
    items = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("-") or s[0].isdigit():
            # strip leading bullet/number
            cleaned = s.lstrip("-0123456789. ").strip()
            items.append({"action": cleaned})
    return items


def consolidate_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Simple normalization: ensure each step has 'title' and 'detail' keys.
    """
    out = []
    for i, s in enumerate(steps):
        title = s.get("title") if isinstance(s, dict) else f"Step {i+1}"
        detail = s.get("detail") if isinstance(s, dict) else str(s)
        out.append({"title": title, "detail": detail})
    return out