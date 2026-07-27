"""
Database package exports for NEXUS.

Exports:
- Base: declarative_base() used by ORM models (import this from app.models or app.database)
- engine: sync SQLAlchemy Engine
- SessionLocal: sync session factory
- get_db: dependency generator for FastAPI
- async_engine: async engine (if async driver configured)
- AsyncSessionLocal: async session factory
- get_async_db: async dependency for FastAPI
- utils: convenience helpers in database.utils
"""
from .session import engine, SessionLocal, Base, get_db
from .async_session import async_engine, AsyncSessionLocal, get_async_db
from . import utils

__all__ = [
    "engine", "SessionLocal", "Base", "get_db",
    "async_engine", "AsyncSessionLocal", "get_async_db",
    "utils",
]