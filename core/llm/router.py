import logging
from typing import Optional
import anthropic
import openai
from core.config import settings

logger = logging.getLogger(__name__)

class LLMRouter:
    """Router com fallback: Anthropic → OpenAI → Gemini → Mock"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai
    
    async def chat(self, messages: list, provider: Optional[str] = None, **kwargs) -> str:
        if provider == "anthropic" and self.anthropic_client:
            return await self._call_anthropic(messages, **kwargs)
        
        if provider == "openai" and self.openai_client:
            return await self._call_openai(messages, **kwargs)
        
        if self.anthropic_client:
            try:
                logger.info("Using Anthropic (primary)")
                return await self._call_anthropic(messages, **kwargs)
            except Exception as e:
                logger.warning(f"Anthropic failed: {e}")
        
        if self.openai_client:
            try:
                logger.info("Fallback to OpenAI")
                return await self._call_openai(messages, **kwargs)
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")
        
        logger.warning("All providers failed, using mock response")
        return await self._call_mock(messages)
    
    async def _call_anthropic(self, messages: list, **kwargs) -> str:
        response = self.anthropic_client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=kwargs.get("max_tokens", 1024),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
        )
        return response.content[0].text
    
    async def _call_openai(self, messages: list, **kwargs) -> str:
        response = self.openai_client.ChatCompletion.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 1024),
            temperature=kwargs.get("temperature", 0.7),
        )
        return response.choices[0].message.content
    
    async def _call_mock(self, messages: list) -> str:
        return f"Mock response to: {messages[-1].get('content', 'no content')}"

_router = None

def get_llm_router() -> LLMRouter:
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router