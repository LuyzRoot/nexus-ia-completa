"""Base LLM Provider - Abstract class for all LLM implementations"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standard LLM response format"""
    text: str
    provider_name: str
    model: str
    tokens_used: Optional[int] = None
    tools_used: List[str] = None
    finish_reason: str = "stop"


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.name = self.__class__.__name__.replace("Provider", "").lower()

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate a completion from messages"""
        pass

    @abstractmethod
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion chunks"""
        pass

    @abstractmethod
    async def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate completion with tool/function calling"""
        pass

    @abstractmethod
    async def is_configured(self) -> bool:
        """Check if provider is properly configured"""
        pass

    @property
    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming"""
        return True

    @property
    def supports_tools(self) -> bool:
        """Whether this provider supports function calling"""
        return True

    @property
    def supports_vision(self) -> bool:
        """Whether this provider supports vision/images"""
        return False
