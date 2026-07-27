"""Tavily Search Provider"""
import logging
from typing import List, Dict, Any, Optional
import aiohttp

from infrastructure.search.base import SearchProvider, SearchResult
from config.settings import settings

logger = logging.getLogger(__name__)


class TavilySearchProvider(SearchProvider):
    """Tavily Search API Provider"""

    API_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.max_results = settings.TAVILY_MAX_RESULTS
        self.include_answer = settings.TAVILY_INCLUDE_ANSWER
        self.name = "tavily"

    async def search(self, query: str, max_results: int = None) -> List[SearchResult]:
        """Search the web using Tavily"""
        max_results = max_results or self.max_results
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": self.include_answer,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.API_URL, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Tavily error: {error_text}")
                        raise Exception(f"Tavily API error: {resp.status}")
                    
                    result = await resp.json()
                    results = []
                    
                    for item in result.get("results", []):
                        results.append(SearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=item.get("content", ""),
                            source="tavily",
                        ))
                    
                    return results
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            raise

    async def deep_search(self, query: str, max_results: int = None) -> Dict[str, Any]:
        """Deep search with answer generation"""
        max_results = max_results or self.max_results
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.API_URL, json=payload) as resp:
                    if resp.status != 200:
                        raise Exception(f"Tavily API error: {resp.status}")
                    
                    return await resp.json()
        except Exception as e:
            logger.error(f"Tavily deep search error: {e}")
            raise
