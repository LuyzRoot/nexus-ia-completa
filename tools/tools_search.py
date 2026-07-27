"""
Web search helper.
Tries to use `duckduckgo_search` package if installed for programmatic search.
If not available, attempts a bare-bones HTTP scrape (fragile) or returns an explanatory error.
Function:
- search_web(query, max_results=5) -> list[{"title","href","snippet"}]
"""
import logging
from typing import List, Dict

logger = logging.getLogger("tools.search")

try:
    from duckduckgo_search import ddg  # type: ignore
    _HAS_DDG = True
except Exception:
    _HAS_DDG = False

import httpx
import re

async def _scrape_ddg_html(query: str, max_results: int = 5) -> List[Dict]:
    """
    Simple fallback scraping from DuckDuckGo HTML results page.
    This is fragile and not recommended for production.
    """
    url = "https://duckduckgo.com/html/"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, data={"q": query})
            text = resp.text
    except Exception as exc:
        logger.warning("Scrape DDG failed: %s", exc)
        return []

    # find result blocks
    items = []
    # extremely naive extraction
    for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', text, re.IGNORECASE | re.DOTALL):
        href = m.group(1)
        title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        items.append({"title": title, "href": href, "snippet": ""})
        if len(items) >= max_results:
            break
    return items

async def search_web(query: str, max_results: int = 5) -> List[Dict]:
    if _HAS_DDG:
        try:
            # ddg is sync; run in thread if needed
            from concurrent.futures import ThreadPoolExecutor
            import asyncio
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as tp:
                results = await loop.run_in_executor(tp, lambda: ddg(query, max_results))
            out = []
            for r in results or []:
                out.append({"title": r.get("title"), "href": r.get("href"), "snippet": r.get("body")})
            return out
        except Exception as exc:
            logger.warning("duckduckgo_search failed: %s", exc)
    # fallback scraping
    return await _scrape_ddg_html(query, max_results=max_results)