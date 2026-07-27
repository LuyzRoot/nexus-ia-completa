from core.config import settings

class GeminiProvider:
    """Google Gemini provider"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
    
    async def chat(self, messages: list, **kwargs) -> str:
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(messages[-1].get("content", ""))
        return response.text
