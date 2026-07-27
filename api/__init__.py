# app/api/__init__.py
# Expose routers for easy import in app.main
from .auth import router as auth_router  # noqa: F401
from .users import router as users_router  # noqa: F401
from .conversations import router as conversations_router  # noqa: F401
from .chat import router as chat_router  # noqa: F401
from .memory import router as memory_router  # noqa: F401
from .voice import router as voice_router  # noqa: F401
from .reminders import router as reminders_router  # noqa: F401
from .todos import router as todos_router  # noqa: F401
from .whatsapp import router as whatsapp_router  # noqa: F401
from .home_assistant import router as ha_router  # noqa: F401
from .agents import router as agents_router  # noqa: F401
from .confirmations import router as confirmations_router  # noqa: F401

__all__ = [
    "auth_router", "users_router", "conversations_router", "chat_router", "memory_router",
    "voice_router", "reminders_router", "todos_router", "whatsapp_router", "ha_router",
    "agents_router", "confirmations_router",
]
