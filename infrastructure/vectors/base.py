"""Base vector database abstraction"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class VectorStoreProvider(ABC):
    """Abstract vector database provider"""

    @abstractmethod
    async def upsert(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict[str, Any]],
    ) -> None:
        """Store vectors in database"""
        pass

    @abstractmethod
    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Query similar vectors"""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete vectors by ID"""
        pass


class EmbeddingProvider(ABC):
    """Abstract embedding provider"""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Convert text to embedding vector"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to embeddings"""
        pass
