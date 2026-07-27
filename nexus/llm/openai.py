import os
from core.config import settings

class OpenAIProvider:
    """OpenAI API provider"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    async def chat(self, messages: list, **kwargs) -> str:
        import openai
        openai.api_key = self.api_key
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1024),
        )
        return response.choices[0].message.content
