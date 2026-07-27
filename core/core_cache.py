name=core/cache.py
"""
In-process TTL cache for small ephemeral caching needs.
Not shared between processes; for multi-instance use Redis or similar.
"""
import threading
import time
from typing import Any, Callable, Optional

class TTLCache:
    def __init__(self):
        self._store = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if time.monotonic() >= expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: float):
        with self._lock:
            self._store[key] = (time.monotonic() + ttl_seconds, value)

    def get_or_set(self, key: str, ttl_seconds: float, compute: Callable[[], Any]):
        val = self.get(key)
        if val is not None:
            return val
        v = compute()
        self.set(key, v, ttl_seconds)
        return v

    def clear(self):
        with self._lock:
            self._store.clear()


# shared instance
cache = TTLCache()