"""LLM router skeleton

This module provides a simple router that can call discovered provider clients
under apis/ (for example apis.openai, apis.anthropic, apis.local).
"""
from typing import Optional
import logging
import importlib

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        self.providers = {}

    def load_provider(self, name: str):
        module_name = f"apis.{name}"
        try:
            module = importlib.import_module(module_name)
            client = getattr(module, "Client", None) or getattr(module, list(module.__all__)[0], None)
            self.providers[name] = module
            logger.info("Loaded provider %s", name)
        except Exception as e:
            logger.warning("Could not load provider %s: %s", name, e)

    def chat(self, prompt: str, provider: Optional[str] = None) -> str:
        if provider and provider in self.providers:
            module = self.providers[provider]
            # provider should expose a client with predict()
            client = getattr(module, "LocalClient", None) or getattr(module, "Client", None)
            if client:
                inst = client() if callable(client) else client
                return inst.predict(prompt)
        # fallback: try 'local'
        try:
            local = importlib.import_module("apis.local")
            inst = getattr(local, "LocalClient")()
            return inst.predict(prompt)
        except Exception as e:
            logger.error("LLM chat fallback failed: %s", e)
            return ""


router = LLMRouter()
