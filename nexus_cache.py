from abc import ABC, abstractmethod
from typing import Optional, Any

class CacheProvider(ABC):
    """Abstract cache provider"""
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None):
        pass
    
    @abstractmethod
    async def delete(self, key: str):
        pass

class InMemoryCache(CacheProvider):
    """In-memory cache"""
    def __init__(self):
        self.cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = None):
        self.cache[key] = value
    
    async def delete(self, key: str):
        self.cache.pop(key, None)
    
    async def clear(self):
        self.cache.clear()