"""
Simple client helpers for calling the inference service.
Provides sync and async convenience wrappers using httpx.
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional

DEFAULT_URL = "http://localhost:8001/inference"

def predict_sync(messages: List[Dict[str,str]], url: str = DEFAULT_URL, timeout: int = 30):
    payload = {"messages": messages}
    with httpx.Client(timeout=timeout) as client:
        r = client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

async def predict_async(messages: List[Dict[str,str]], url: str = DEFAULT_URL, timeout: int = 30):
    payload = {"messages": messages}
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

def stream_sync(messages: List[Dict[str,str]], url: str = DEFAULT_URL + "/stream", timeout: int = 60):
    with httpx.Client(timeout=timeout) as client:
        with client.stream("POST", url, json={"messages": messages}) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                # SSE lines: may include "data: " prefix
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.startswith("data:"):
                    yield text.replace("data:","",1).strip()