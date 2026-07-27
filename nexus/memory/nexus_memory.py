import redis.asyncio as redis
import json
from typing import Optional, Dict, List
from core.config import settings

class RedisMemory:
    """Redis-based memory layer"""
    def __init__(self):
        self.client = None
    
    async def connect(self):
        self.client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def disconnect(self):
        if self.client:
            await self.client.close()
    
    async def set(self, key: str, value: dict, ttl: int = None):
        if not self.client:
            await self.connect()
        await self.client.set(key, json.dumps(value), ex=ttl)
    
    async def get(self, key: str) -> Optional[dict]:
        if not self.client:
            await self.connect()
        data = await self.client.get(key)
        return json.loads(data) if data else None
    
    async def delete(self, key: str):
        if not self.client:
            await self.connect()
        await self.client.delete(key)

class VectorStore:
    """Vector embedding store"""
    def __init__(self):
        self.vectors = {}
    
    async def add(self, id: str, embedding: List[float], metadata: dict = None):
        import numpy as np
        self.vectors[id] = {"embedding": np.array(embedding), "metadata": metadata or {}}
    
    async def search(self, embedding: List[float], top_k: int = 5):
        import numpy as np
        if not self.vectors:
            return []
        query = np.array(embedding)
        scores = []
        for id, data in self.vectors.items():
            sim = np.dot(query, data["embedding"]) / (np.linalg.norm(query) * np.linalg.norm(data["embedding"]) + 1e-10)
            scores.append((id, sim, data["metadata"]))
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]

class EmbeddingProvider:
    """Embedding provider"""
    async def embed_text(self, text: str) -> List[float]:
        import hashlib, random
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest(), 16)
        random.seed(seed)
        return [random.random() for _ in range(384)]
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(text) for text in texts]
