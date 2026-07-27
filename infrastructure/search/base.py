"""Base search provider abstraction"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Search result from any provider"""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.0


class SearchProvider(ABC):
    """Abstract search provider"""

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search the web"""
        pass

    @abstractmethod
    async def deep_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Deep search with additional context"""
        pass
