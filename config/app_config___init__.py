# Exports convenient defaults used across the app
from .settings import settings  # pydantic settings instance
from .logging import configure_logging

__all__ = ["settings", "configure_logging"]