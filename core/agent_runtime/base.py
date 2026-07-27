"""Base agent abstraction"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Chat message"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Agent response with metadata"""
    text: str
    agent_name: str
    model_used: str
    tokens_used: Optional[int] = None
    tools_used: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.conversation_history: List[Message] = []

    @abstractmethod
    async def process(self, message: str) -> AgentResponse:
        """Process user message and return response"""
        pass

    @abstractmethod
    async def stream_process(self, message: str) -> AsyncIterator[str]:
        """Stream agent response"""
        pass

    def add_to_history(self, message: Message) -> None:
        """Add message to conversation history"""
        self.conversation_history.append(message)

    def get_history(self, limit: int = None) -> List[Message]:
        """Get conversation history"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
