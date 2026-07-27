import redis.asyncio as redis
import json
from typing import Optional
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
    
    async def mget(self, *keys):
        if not self.client:
            await self.connect()
        values = await self.client.mget(*keys)
        return [json.loads(v) if v else None for v in values]
