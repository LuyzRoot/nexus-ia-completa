import logging
from typing import List, Dict
from core.config import settings

logger = logging.getLogger(__name__)

class Provider:
    """Google Gemini API Provider"""
    
    name = "gemini"
    version = "1.0.0"
    description = "Google Gemini Models Provider"
    endpoints = ["chat", "generativeContent"]
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """Chat with Google Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(messages[-1].get("content", ""))
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise
