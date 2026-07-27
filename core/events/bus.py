"""Event system and pub/sub messaging"""
import logging
from typing import Callable, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types in the system"""
    # Agent events
    AGENT_REQUEST = "agent.request"
    AGENT_RESPONSE = "agent.response"
    AGENT_ERROR = "agent.error"
    
    # Memory events
    MEMORY_SAVED = "memory.saved"
    MEMORY_RETRIEVED = "memory.retrieved"
    
    # LLM events
    LLM_REQUEST = "llm.request"
    LLM_RESPONSE = "llm.response"
    LLM_ERROR = "llm.error"
    
    # User events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


@dataclass
class Event:
    """Event object"""
    type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    user_id: str = None


class EventBus:
    """Central event bus for pub/sub messaging"""

    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe to events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type}")

    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """Unsubscribe from events"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            logger.debug(f"Unsubscribed from {event_type}")

    async def publish(self, event: Event) -> None:
        """Publish event to all subscribers"""
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify subscribers
        handlers = self.subscribers.get(event.type, [])
        for handler in handlers:
            try:
                if hasattr(handler, '__call__'):
                    result = handler(event)
                    if hasattr(result, '__await__'):
                        await result
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    def get_event_history(self, event_type: EventType = None, limit: int = 100) -> List[Event]:
        """Get event history"""
        if event_type:
            history = [e for e in self.event_history if e.type == event_type]
        else:
            history = self.event_history
        
        return history[-limit:]


# Global event bus instance
event_bus = EventBus()
