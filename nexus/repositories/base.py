from abc import ABC, abstractmethod
from typing import List, Optional

class BaseRepository(ABC):
    """Base repository pattern"""
    
    @abstractmethod
    async def create(self, **kwargs):
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str):
        pass
    
    @abstractmethod
    async def get_all(self):
        pass
    
    @abstractmethod
    async def update(self, id: str, **kwargs):
        pass
    
    @abstractmethod
    async def delete(self, id: str):
        pass
