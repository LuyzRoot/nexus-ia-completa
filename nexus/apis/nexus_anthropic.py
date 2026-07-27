import logging
from typing import List, Dict
from core.config import settings

logger = logging.getLogger(__name__)

class Provider:
    """Anthropic Claude API Provider"""
    
    name = "anthropic"
    version = "1.0.0"
    description = "Anthropic Claude Models Provider"
    endpoints = ["chat", "messages"]
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """Chat with Anthropic Claude"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1024),
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            raise
