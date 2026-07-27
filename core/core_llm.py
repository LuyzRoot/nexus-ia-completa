name=core/llm.py
"""
Abstração LLM leve e roteador local de provedores.
Tenta usar os provedores reais em app.services.providers (Anthropic/OpenAI/Gemini/Mock)
Se não existirem, cai em MockProvider local.
API principal:
- async generate(messages, temperature=None) -> {"text": str, "provider": str}
- async stream_generate(messages, temperature=None) -> async iterator of chunks (str)
- async complete_with_tools(messages, tools, executor, ...) -> ProviderResponse-like dict
"""
import asyncio
import logging
from typing import List, Dict, Any, AsyncIterator

from app.config.settings import settings

logger = logging.getLogger("core.llm")


class ProviderError(Exception):
    pass


class ProviderResponse:
    def __init__(self, text: str, provider_name: str, model: str = None, tools_used: List[str] = None):
        self.text = text
        self.provider_name = provider_name
        self.model = model
        self.tools_used = tools_used or []


# Try to import providers from app.services.providers (the Nexus style). If not present,
# fall back to a lightweight mock provider implemented here.
try:
    from app.services.providers.anthropic_provider import AnthropicProvider  # type: ignore
    from app.services.providers.openai_provider import OpenAIProvider  # type: ignore
    from app.services.providers.gemini_provider import GeminiProvider  # type: ignore
    from app.services.providers.mock_provider import MockProvider  # type: ignore

    _PROVIDERS_AVAILABLE = True
except Exception:
    AnthropicProvider = OpenAIProvider = GeminiProvider = None
    # lightweight mock provider class
    class MockProvider:
        name = "mock"
        supports_streaming = False
        supports_tools = False

        async def is_configured(self):
            return True

        async def complete(self, messages, **kwargs):
            # Echo user last message
            last = ""
            for m in reversed(messages):
                if m.get("role") == "user":
                    last = m.get("content", "")
                    break
            return ProviderResponse(text=f"(mock) {last}", provider_name="mock", model="mock-model")

        async def complete_stream(self, messages, **kwargs):
            # simple stream yielding small chunks
            resp = await self.complete(messages, **kwargs)
            text = resp.text
            for i in range(0, len(text), 40):
                await asyncio.sleep(0)  # allow event loop to cycle
                yield text[i : i + 40]

        async def complete_with_tools(self, messages, tools, executor, **kwargs):
            # no tool support in mock
            return await self.complete(messages, **kwargs)

    _PROVIDERS_AVAILABLE = False


# Instantiate provider objects lazily
def _make_registry():
    registry: Dict[str, Any] = {}
    if _PROVIDERS_AVAILABLE:
        try:
            registry["anthropic"] = AnthropicProvider()
        except Exception:
            pass
        try:
            registry["openai"] = OpenAIProvider()
        except Exception:
            pass
        try:
            registry["gemini"] = GeminiProvider()
        except Exception:
            pass
    # always provide mock
    registry["mock"] = MockProvider()
    return registry


_PROVIDER_REGISTRY = _make_registry()


class LLMRouter:
    def __init__(self, providers: Dict[str, Any] = None, priority: List[str] = None):
        self.providers = providers or _PROVIDER_REGISTRY
        self.priority = priority or getattr(settings, "MODEL_PROVIDER_PRIORITY", list(self.providers.keys()))

    async def generate(self, messages: List[Dict[str, str]], temperature: float = None, retries_per_provider: int = 2) -> ProviderResponse:
        last_error = None
        for provider_name in self.priority:
            provider = self.providers.get(provider_name)
            if provider is None:
                continue
            if not await self._is_provider_configured(provider):
                logger.info("Provider %s not configured, skipping", provider_name)
                continue
            for attempt in range(1, retries_per_provider + 1):
                try:
                    if getattr(provider, "complete", None):
                        resp = await provider.complete(messages, temperature=temperature)
                    else:
                        raise ProviderError(f"Provider {provider_name} has no 'complete' method")
                    if isinstance(resp, ProviderResponse):
                        return resp
                    # adapt to dicts with text, provider_name
                    return ProviderResponse(text=resp.get("text", str(resp)), provider_name=provider_name, model=resp.get("model"))
                except Exception as exc:
                    last_error = exc
                    logger.warning("Provider %s failed (attempt %d/%d): %s", provider_name, attempt, retries_per_provider, exc)
                    if attempt < retries_per_provider:
                        await asyncio.sleep(0.5 * attempt)
            logger.warning("Provider %s exhausted retries, falling back", provider_name)
        raise ProviderError(f"All providers failed. Last error: {last_error}")

    async def stream_generate(self, messages: List[Dict[str, str]], temperature: float = None) -> AsyncIterator[str]:
        """
        Try providers that support streaming in priority order.
        If a provider fails before emitting the first chunk, try next.
        If it fails after emitting any chunk, propagate error.
        """
        last_error = None
        for provider_name in self.priority:
            provider = self.providers.get(provider_name)
            if provider is None or not getattr(provider, "supports_streaming", False):
                continue
            if not await self._is_provider_configured(provider):
                logger.info("Provider %s not configured (stream), skipping", provider_name)
                continue
            first_emitted = False
            try:
                async for chunk in provider.complete_stream(messages, temperature=temperature):
                    first_emitted = True
                    yield chunk
                return
            except Exception as exc:
                last_error = exc
                logger.warning("Provider %s stream failed: %s", provider_name, exc)
                if first_emitted:
                    # already emitted some data; cannot switch providers
                    raise
                # else try next provider
        raise ProviderError(f"All streaming providers failed. Last error: {last_error}")

    async def complete_with_tools(self, messages, tools, executor, temperature: float = None, retries_per_provider: int = 2):
        """
        Providers that support tools: attempt in priority order.
        """
        last_error = None
        any_tool_provider = False
        for provider_name in self.priority:
            provider = self.providers.get(provider_name)
            if provider is None or not getattr(provider, "supports_tools", False):
                continue
            if not await self._is_provider_configured(provider):
                logger.info("Provider %s not configured for tools, skipping", provider_name)
                continue
            any_tool_provider = True
            for attempt in range(1, retries_per_provider + 1):
                try:
                    resp = await provider.complete_with_tools(messages, tools, executor, temperature=temperature)
                    if isinstance(resp, ProviderResponse):
                        return resp
                    return ProviderResponse(text=resp.get("text", str(resp)), provider_name=provider_name)
                except Exception as exc:
                    last_error = exc
                    logger.warning("Provider %s tools failed (attempt %d/%d): %s", provider_name, attempt, retries_per_provider, exc)
                    if attempt < retries_per_provider:
                        await asyncio.sleep(0.5 * attempt)
        if not any_tool_provider:
            # Fallback: call generate normally
            return await self.generate(messages, temperature=temperature, retries_per_provider=retries_per_provider)
        raise ProviderError(f"All providers with tools failed. Last error: {last_error}")

    async def _is_provider_configured(self, provider) -> bool:
        try:
            if getattr(provider, "is_configured", None):
                return await provider.is_configured()
            # default to True
            return True
        except Exception:
            return False


# Singleton router
llm_router = LLMRouter()