import redis.asyncio as redis
from typing import Optional
import json
from core.config import settings

class MemoryManager:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.redis_client = None
    
    async def connect(self):
        self.redis_client = await redis.from_url(self.redis_url, decode_responses=True)
    
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
    
    async def store_context(self, user_id: str, key: str, data: dict, ttl: int = 3600):
        if not self.redis_client:
            await self.connect()
        full_key = f"context:{user_id}:{key}"
        await self.redis_client.setex(full_key, ttl, json.dumps(data))
    
    async def get_context(self, user_id: str, key: str) -> Optional[dict]:
        if not self.redis_client:
            await self.connect()
        full_key = f"context:{user_id}:{key}"
        data = await self.redis_client.get(full_key)
        if data:
            return json.loads(data)
        return None
    
    async def delete_context(self, user_id: str, key: str):
        if not self.redis_client:
            await self.connect()
        full_key = f"context:{user_id}:{key}"
        await self.redis_client.delete(full_key)

_memory_manager = None

async def get_memory_manager() -> MemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
        await _memory_manager.connect()
    return _memory_manager