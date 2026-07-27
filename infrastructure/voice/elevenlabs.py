"""ElevenLabs Text-to-Speech Provider"""
import logging
from typing import AsyncIterator, Optional
import aiohttp

from infrastructure.voice.base import TextToSpeechProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class ElevenLabsProvider(TextToSpeechProvider):
    """ElevenLabs TTS Provider"""

    API_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ELEVENLABS_API_KEY
        self.model = settings.ELEVENLABS_MODEL
        self.default_voice_id = settings.ELEVENLABS_VOICE_ID
        self.stability = settings.ELEVENLABS_STABILITY
        self.similarity_boost = settings.ELEVENLABS_SIMILARITY_BOOST
        self.name = "elevenlabs"

    async def synthesize(self, text: str, voice_id: str = None, speed: float = 1.0) -> bytes:
        """Generate speech from text"""
        voice_id = voice_id or self.default_voice_id
        url = f"{self.API_URL}/text-to-speech/{voice_id}"
        
        headers = {"xi-api-key": self.api_key}
        payload = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
            },
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"ElevenLabs error: {error_text}")
                        raise Exception(f"ElevenLabs API error: {resp.status}")
                    return await resp.read()
        except Exception as e:
            logger.error(f"ElevenLabs synthesis error: {e}")
            raise

    async def synthesize_stream(self, text: str, voice_id: str = None, speed: float = 1.0) -> AsyncIterator[bytes]:
        """Stream TTS output"""
        voice_id = voice_id or self.default_voice_id
        url = f"{self.API_URL}/text-to-speech/{voice_id}/stream"
        
        headers = {"xi-api-key": self.api_key}
        payload = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
            },
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        raise Exception(f"ElevenLabs API error: {resp.status}")
                    async for chunk in resp.content.iter_chunked(1024):
                        yield chunk
        except Exception as e:
            logger.error(f"ElevenLabs streaming error: {e}")
            raise
