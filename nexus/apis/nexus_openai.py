import logging
from typing import Optional, List, Dict
from core.config import settings

logger = logging.getLogger(__name__)

class Provider:
    """OpenAI API Provider"""
    
    name = "openai"
    version = "1.0.0"
    description = "OpenAI GPT Models Provider"
    endpoints = ["chat", "completions", "embeddings"]
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """Chat with OpenAI"""
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1024),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise
