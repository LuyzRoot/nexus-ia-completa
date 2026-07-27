"""
Auth package for NEXUS.

Exports:
- routes (FastAPI router)
- deps (get_current_user, require_admin)
- schemas (Pydantic models for auth)
"""
from .routes import router as router  # noqa: F401
from .deps import get_current_user, require_admin  # noqa: F401
from .schemas import Token, TokenPayload, UserCreate, UserOut  # noqa: F401

__all__ = ["router", "get_current_user", "require_admin", "Token", "UserOut"]