"""LLM Router - Intelligent orchestrator with automatic fallback"""
import logging
import asyncio
from typing import List, Dict, Any, AsyncIterator, Optional

from infrastructure.llm.base import BaseLLMProvider, LLMResponse
from infrastructure.llm.openai_provider import OpenAIProvider
from infrastructure.llm.anthropic_provider import AnthropicProvider
from config.settings import settings, LLMProvider

logger = logging.getLogger(__name__)


class LLMRouterError(Exception):
    """LLM Router exception"""
    pass


class LLMRouter:
    """
    Intelligent LLM Router with fallback mechanism
    Priority: OpenAI -> Anthropic -> Gemini -> Mock
    """

    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()
        self.priority = settings.MODEL_PROVIDER_PRIORITY

    def _initialize_providers(self):
        """Initialize all available providers"""
        # OpenAI
        try:
            if settings.OPENAI_API_KEY:
                self.providers[LLMProvider.OPENAI] = OpenAIProvider()
                logger.info("✓ OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {e}")

        # Anthropic
        try:
            if settings.ANTHROPIC_API_KEY:
                self.providers[LLMProvider.ANTHROPIC] = AnthropicProvider()
                logger.info("✓ Anthropic provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic: {e}")

        # Gemini - TODO: Implement GeminiProvider
        # try:
        #     if settings.GEMINI_API_KEY:
        #         self.providers[LLMProvider.GEMINI] = GeminiProvider()
        #         logger.info("✓ Gemini provider initialized")
        # except Exception as e:
        #     logger.warning(f"Failed to initialize Gemini: {e}")

    async def complete(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retries: int = 3,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate completion with automatic fallback

        Args:
            messages: Conversation messages
            provider: Specific provider to use (if None, uses priority order)
            temperature: Model temperature (0-1)
            max_tokens: Max tokens in response
            retries: Retry attempts per provider
            **kwargs: Additional provider-specific arguments

        Returns:
            LLMResponse with generated text and metadata
        """
        last_error = None
        providers_to_try = [provider] if provider else self.priority

        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                logger.debug(f"Provider {provider_name} not available")
                continue

            provider_obj = self.providers[provider_name]

            for attempt in range(1, retries + 1):
                try:
                    logger.debug(
                        f"Attempting {provider_name} (attempt {attempt}/{retries})"
                    )
                    response = await provider_obj.complete(
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    )
                    logger.info(f"✓ {provider_name} completed successfully")
                    return response

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Provider {provider_name} failed "
                        f"(attempt {attempt}/{retries}): {str(e)}"
                    )
                    if attempt < retries:
                        await asyncio.sleep(0.5 * attempt)

            logger.warning(f"Provider {provider_name} exhausted all retries")

        raise LLMRouterError(
            f"All providers failed. Last error: {str(last_error)}"
        )

    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Stream completion with fallback

        Args:
            messages: Conversation messages
            provider: Specific provider to use
            temperature: Model temperature
            max_tokens: Max tokens in response
            **kwargs: Additional arguments

        Yields:
            Streamed text chunks
        """
        last_error = None
        providers_to_try = [provider] if provider else self.priority
        first_chunk_emitted = False

        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue

            provider_obj = self.providers[provider_name]

            if not provider_obj.supports_streaming:
                logger.debug(f"Provider {provider_name} doesn't support streaming")
                continue

            try:
                logger.debug(f"Streaming with {provider_name}")
                async for chunk in provider_obj.stream_complete(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                ):
                    first_chunk_emitted = True
                    yield chunk

                logger.info(f"✓ {provider_name} streaming completed")
                return

            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_name} streaming failed: {e}")

                if first_chunk_emitted:
                    # Already started streaming, cannot fallback
                    raise

        raise LLMRouterError(
            f"All streaming providers failed. Last error: {str(last_error)}"
        )

    async def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retries: int = 3,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate completion with tool/function calling

        Args:
            messages: Conversation messages
            tools: Tool definitions (OpenAI format)
            provider: Specific provider to use
            temperature: Model temperature
            max_tokens: Max tokens in response
            retries: Retry attempts
            **kwargs: Additional arguments

        Returns:
            LLMResponse with generated text and tool calls
        """
        last_error = None
        providers_to_try = [provider] if provider else self.priority

        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue

            provider_obj = self.providers[provider_name]

            if not provider_obj.supports_tools:
                logger.debug(f"Provider {provider_name} doesn't support tools")
                continue

            for attempt in range(1, retries + 1):
                try:
                    logger.debug(
                        f"Attempting {provider_name} with tools "
                        f"(attempt {attempt}/{retries})"
                    )
                    response = await provider_obj.complete_with_tools(
                        messages=messages,
                        tools=tools,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    )
                    logger.info(f"✓ {provider_name} completed with tools")
                    return response

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Provider {provider_name} tools failed "
                        f"(attempt {attempt}/{retries}): {e}"
                    )
                    if attempt < retries:
                        await asyncio.sleep(0.5 * attempt)

        # Fallback to regular completion if no tool-capable provider works
        logger.warning("Falling back to regular completion (tools not available)")
        return await self.complete(
            messages=messages,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    async def get_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-large",
    ) -> List[List[float]]:
        """
        Get embeddings using OpenAI (can be extended to other providers)

        Args:
            texts: List of texts to embed
            model: Embedding model to use

        Returns:
            List of embedding vectors
        """
        if LLMProvider.OPENAI not in self.providers:
            raise LLMRouterError("OpenAI provider not available for embeddings")

        # TODO: Implement embeddings call
        raise NotImplementedError("Embeddings not yet implemented")


# Global LLM Router instance
llm_router = LLMRouter()
