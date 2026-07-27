import asyncio
import logging
from typing import Callable, List
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    USER_MESSAGE = "user_message"
    AGENT_STARTED = "agent_started"
    AGENT_FINISHED = "agent_finished"
    TOOL_EXECUTED = "tool_executed"
    ERROR_OCCURRED = "error_occurred"
    TASK_COMPLETED = "task_completed"

class Event:
    def __init__(self, event_type: EventType, data: dict = None):
        self.type = event_type
        self.data = data or {}

class EventBus:
    """Simple event bus for agent communication"""
    
    def __init__(self):
        self.subscribers: dict[EventType, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to {event_type}")
    
    async def emit(self, event: Event):
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Event callback error: {e}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
