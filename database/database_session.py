"""
Synchronous SQLAlchemy engine + session factory.

- Uses settings.DATABASE_URL from app.config.settings
- Exposes Base (declarative_base) so models can import `from app.database import Base`.
- Exposes get_db() generator for FastAPI dependencies.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

# DATABASE_URL example: postgresql://user:pass@host:5432/dbname
DATABASE_URL = getattr(settings, "DATABASE_URL", "sqlite:///./nexus_dev.db")

# Create sync engine
# echo is controlled by settings.DEBUG; future=True recommended for 2.0 style
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)

# Declarative base (exported)
Base = declarative_base()

# FastAPI dependency
def get_db() -> Generator:
    """
    Dependency that yields a SQLAlchemy Session and closes it afterwards.
    Usage:
        from app.database import get_db
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            pass