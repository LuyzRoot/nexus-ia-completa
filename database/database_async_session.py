"""
Async SQLAlchemy engine + session factory.

- Attempts to convert a sync DATABASE_URL into an async one (common case: postgresql -> postgresql+asyncpg).
- If settings.DATABASE_URL already has an async driver (asyncpg), it will be used directly.
- Exposes get_async_db() async dependency for FastAPI.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config.settings import settings
import re
import logging

logger = logging.getLogger("database.async_session")

SYNC_URL = getattr(settings, "DATABASE_URL", "sqlite:///./nexus_dev.db")

def _to_async_url(sync_url: str) -> Optional[str]:
    """
    Convert common sync DSNs to async equivalents when possible.
    Examples:
      - postgresql:// -> postgresql+asyncpg://
      - mysql:// -> mysql+asyncmy:// (user must install driver) - we won't attempt many conversions
    If conversion not possible, return None.
    """
    if sync_url.startswith("postgresql://") and "asyncpg" not in sync_url:
        return sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if sync_url.startswith("postgres://") and "asyncpg" not in sync_url:
        return sync_url.replace("postgres://", "postgresql+asyncpg://", 1)
    # SQLite local file can be used with aiosqlite (sqlite+aiosqlite:///./db.sqlite)
    if sync_url.startswith("sqlite:///") and "aiosqlite" not in sync_url:
        return sync_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    # Unknown; return None to skip async engine creation
    return None

ASYNC_DATABASE_URL = _to_async_url(SYNC_URL)

if ASYNC_DATABASE_URL:
    try:
        async_engine = create_async_engine(ASYNC_DATABASE_URL, future=True, echo=False)
        AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
    except Exception as exc:
        logger.warning("Failed to create async engine: %s", exc)
        async_engine = None
        AsyncSessionLocal = None
else:
    async_engine = None
    AsyncSessionLocal = None

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency for FastAPI endpoints.
    Yields an AsyncSession if the async engine is available; else raises RuntimeError.
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("Async engine not configured. Ensure you have an async DB driver (asyncpg/aiosqlite) and DATABASE_URL set accordingly.")
    async with AsyncSessionLocal() as session:
        yield session