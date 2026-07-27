import logging
from typing import List, Dict
import httpx

logger = logging.getLogger(__name__)

class Provider:
    """Ollama Local LLM Provider"""
    
    name = "ollama"
    version = "1.0.0"
    description = "Ollama Local LLM Provider"
    endpoints = ["chat", "embeddings"]
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """Chat with Ollama"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                    },
                    timeout=kwargs.get("timeout", 30),
                )
                data = response.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise