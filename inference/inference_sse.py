"""
Simple SSE helper: formats events for text/event-stream.

We use inline formatting in routes.py (simple), but keep helper here if you want structured events.
"""
import json
from typing import Dict

def format_sse_event(event: Dict) -> str:
    """
    event: a dict that will be JSON-encoded as the 'data' payload.
    returns a string like: data: {...}\n\n
    """
    payload = json.dumps(event, ensure_ascii=False)
    return f"data: {payload}\n\n"