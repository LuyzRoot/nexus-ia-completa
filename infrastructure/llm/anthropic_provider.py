"""Anthropic Provider - Claude integration"""
import logging
from typing import List, Dict, Any, AsyncIterator, Optional
import anthropic

from infrastructure.llm.base import BaseLLMProvider, LLMResponse
from config.settings import settings

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM Provider"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        self.name = "anthropic"

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate completion using Anthropic API"""
        try:
            temperature = temperature or settings.ANTHROPIC_TEMPERATURE
            max_tokens = max_tokens or settings.ANTHROPIC_MAX_TOKENS

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                temperature=temperature,
                **kwargs,
            )

            return LLMResponse(
                text=response.content[0].text,
                provider_name=self.name,
                model=self.model,
                tokens_used=response.usage.output_tokens + response.usage.input_tokens,
                finish_reason=response.stop_reason,
            )
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion from Anthropic"""
        try:
            temperature = temperature or settings.ANTHROPIC_TEMPERATURE
            max_tokens = max_tokens or settings.ANTHROPIC_MAX_TOKENS

            with await self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                temperature=temperature,
                **kwargs,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except anthropic.APIError as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise

    async def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate completion with tool use"""
        try:
            temperature = temperature or settings.ANTHROPIC_TEMPERATURE
            max_tokens = max_tokens or settings.ANTHROPIC_MAX_TOKENS

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                tools=tools,
                temperature=temperature,
                **kwargs,
            )

            content = ""
            tools_used = []

            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text
                elif hasattr(block, "type") and block.type == "tool_use":
                    tools_used.append(block.name)

            return LLMResponse(
                text=content,
                provider_name=self.name,
                model=self.model,
                tokens_used=response.usage.output_tokens + response.usage.input_tokens,
                tools_used=tools_used,
                finish_reason=response.stop_reason,
            )
        except anthropic.APIError as e:
            logger.error(f"Anthropic tools error: {e}")
            raise

    async def is_configured(self) -> bool:
        """Check if Anthropic API is configured"""
        return bool(self.api_key)
