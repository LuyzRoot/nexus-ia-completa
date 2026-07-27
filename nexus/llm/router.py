import logging
from typing import Optional
from nexus.llm.openai import OpenAIProvider
from nexus.llm.anthropic import AnthropicProvider
from nexus.llm.ollama import OllamaProvider
from nexus.llm.gemini import GeminiProvider

logger = logging.getLogger(__name__)

class LLMRouter:
    """Smart LLM router with fallback"""
    
    def __init__(self):
        self.providers = []
        self.setup_providers()
    
    def setup_providers(self):
        # Add providers in priority order
        try:
            self.providers.append(("anthropic", AnthropicProvider()))
        except:
            logger.warning("Anthropic provider not available")
        
        try:
            self.providers.append(("openai", OpenAIProvider()))
        except:
            logger.warning("OpenAI provider not available")
        
        try:
            self.providers.append(("ollama", OllamaProvider()))
        except:
            logger.warning("Ollama provider not available")
        
        try:
            self.providers.append(("gemini", GeminiProvider()))
        except:
            logger.warning("Gemini provider not available")
    
    async def chat(self, messages: list, provider: Optional[str] = None, **kwargs) -> str:
        """Route chat request with automatic fallback"""
        
        # Try specific provider first
        if provider:
            for name, prov in self.providers:
                if name == provider:
                    try:
                        logger.info(f"Using {provider}")
                        return await prov.chat(messages, **kwargs)
                    except Exception as e:
                        logger.error(f"{provider} failed: {e}")
        
        # Try providers in order
        for name, prov in self.providers:
            try:
                logger.info(f"Trying {name}")
                return await prov.chat(messages, **kwargs)
            except Exception as e:
                logger.warning(f"{name} failed: {e}")
        
        return "Mock response: All LLM providers failed"

_router = None

def get_llm_router() -> LLMRouter:
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router
