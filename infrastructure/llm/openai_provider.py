"""OpenAI Provider - GPT-4, GPT-4o integration"""
import logging
from typing import List, Dict, Any, AsyncIterator, Optional
import openai
from openai import AsyncOpenAI

from infrastructure.llm.base import BaseLLMProvider, LLMResponse
from config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM Provider - GPT-4, GPT-4o"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        org_id: Optional[str] = None,
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL_CHAT
        self.org_id = org_id or settings.OPENAI_ORG_ID
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            organization=self.org_id,
        )
        self.name = "openai"

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate completion using OpenAI API"""
        try:
            temperature = temperature or settings.OPENAI_TEMPERATURE
            max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=settings.OPENAI_TOP_P,
                frequency_penalty=settings.OPENAI_FREQUENCY_PENALTY,
                presence_penalty=settings.OPENAI_PRESENCE_PENALTY,
                **kwargs,
            )

            return LLMResponse(
                text=response.choices[0].message.content,
                provider_name=self.name,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
            )
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion from OpenAI"""
        try:
            temperature = temperature or settings.OPENAI_TEMPERATURE
            max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS

            with await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                top_p=settings.OPENAI_TOP_P,
                frequency_penalty=settings.OPENAI_FREQUENCY_PENALTY,
                presence_penalty=settings.OPENAI_PRESENCE_PENALTY,
                **kwargs,
            ) as stream:
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        except openai.APIError as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise

    async def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate completion with function calling"""
        try:
            temperature = temperature or settings.OPENAI_TEMPERATURE
            max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            content = response.choices[0].message.content or ""
            tools_used = []

            if response.choices[0].message.tool_calls:
                tools_used = [call.function.name for call in response.choices[0].message.tool_calls]

            return LLMResponse(
                text=content,
                provider_name=self.name,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                tools_used=tools_used,
                finish_reason=response.choices[0].finish_reason,
            )
        except openai.APIError as e:
            logger.error(f"OpenAI tools error: {e}")
            raise

    async def is_configured(self) -> bool:
        """Check if OpenAI API is configured"""
        return bool(self.api_key)

    @property
    def supports_vision(self) -> bool:
        """OpenAI supports vision"""
        return True
