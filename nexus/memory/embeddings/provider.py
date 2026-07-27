from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """Abstract embedding provider"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class MockEmbeddings(EmbeddingProvider):
    """Mock embeddings for testing"""
    
    async def embed_text(self, text: str) -> List[float]:
        # Return mock 384-dim embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest(), 16)
        import random
        random.seed(seed)
        return [random.random() for _ in range(384)]
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(text) for text in texts]
