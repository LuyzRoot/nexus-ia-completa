"""
Convenience helpers for database initialization and utilities.

Functions:
- init_db(create_tables=True): run create_all() using models' metadata (development convenience)
- create_all_tables(): wrapper around Base.metadata.create_all
- drop_all_tables(): wrapper around Base.metadata.drop_all
- run_raw_sql(sql): execute raw SQL on sync engine (use with care)
- alembic_migration_command_hint(): returns a shell command hint to run alembic (user still needs alembic.ini)
"""
import logging
from sqlalchemy import text
from typing import Optional
from .session import engine, Base
from .async_session import async_engine

logger = logging.getLogger("database.utils")

def create_all_tables(bind_engine = None):
    """
    Create all tables defined on Base metadata.
    Note: for production prefer Alembic migrations instead of create_all().
    """
    be = bind_engine or engine
    if be is None:
        raise RuntimeError("Sync engine not configured")
    Base.metadata.create_all(bind=be)
    logger.info("create_all() completed")


def drop_all_tables(bind_engine = None):
    be = bind_engine or engine
    if be is None:
        raise RuntimeError("Sync engine not configured")
    Base.metadata.drop_all(bind=be)
    logger.info("drop_all() completed")


def init_db(create_tables: bool = True):
    """
    Called at app startup in development. In production, prefer migrations.
    """
    if create_tables:
        create_all_tables()
    logger.info("Database initialized (create_tables=%s)", create_tables)


def run_raw_sql(sql: str, params: Optional[dict] = None):
    """
    Execute read/write SQL using sync engine. Return ResultProxy-like object.
    Use only with trusted SQL.
    """
    with engine.connect() as conn:
        res = conn.execute(text(sql), params or {})
        # commit if modifying
        try:
            conn.commit()
        except Exception:
            pass
        return res


def alembic_migration_command_hint():
    """
    Returns a suggested shell command to run alembic migrations.
    You still need an alembic.ini and alembic env.py configured to import app.models.Base.
    """
    return "alembic upgrade head  # run from repo root where alembic.ini is present"