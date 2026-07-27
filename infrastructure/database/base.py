"""Base repository pattern implementation"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Generic, TypeVar

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for all entities"""

    @abstractmethod
    async def create(self, obj: T) -> T:
        """Create a new entity"""
        pass

    @abstractmethod
    async def read(self, id: Any) -> Optional[T]:
        """Read entity by ID"""
        pass

    @abstractmethod
    async def update(self, id: Any, obj: T) -> T:
        """Update entity"""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete entity"""
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 10) -> List[T]:
        """List entities with pagination"""
        pass
