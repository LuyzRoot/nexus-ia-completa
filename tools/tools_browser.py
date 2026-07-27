"""
Simple browser / HTTP fetch helpers.
Uses httpx for async requests. Provides:
- fetch_url(url, timeout=10) -> dict(status_code, headers, text)
- fetch_title(url) -> str | None (attempts HTML title extraction)
"""
import httpx
import logging
import re
from typing import Optional, Dict

logger = logging.getLogger("tools.browser")


async def fetch_url(url: str, timeout: int = 10) -> Dict:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, follow_redirects=True)
            return {"status_code": resp.status_code, "headers": dict(resp.headers), "text": resp.text}
    except httpx.RequestError as exc:
        logger.warning("fetch_url request error: %s", exc)
        return {"status_code": 0, "headers": {}, "text": "", "error": str(exc)}


async def fetch_title(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetches the page and tries to extract the <title>.
    """
    data = await fetch_url(url, timeout=timeout)
    text = data.get("text", "")
    if not text:
        return None
    # quick regex for <title>
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if m:
        title = m.group(1).strip()
        # remove inner tags
        title = re.sub(r"<[^>]+>", "", title).strip()
        return title
    # fallback: first h1
    m2 = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.IGNORECASE | re.DOTALL)
    if m2:
        return re.sub(r"<[^>]+>", "", m2.group(1)).strip()
    return None