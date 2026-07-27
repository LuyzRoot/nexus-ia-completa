"""Deepgram Speech-to-Text Provider"""
import logging
from typing import AsyncIterator, Optional
import aiohttp

from infrastructure.voice.base import SpeechToTextProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class DeepgramProvider(SpeechToTextProvider):
    """Deepgram STT Provider"""

    API_URL = "https://api.deepgram.com/v1/listen"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.DEEPGRAM_API_KEY
        self.model = settings.DEEPGRAM_MODEL
        self.language = settings.DEEPGRAM_LANGUAGE
        self.name = "deepgram"

    async def transcribe(self, audio_data: bytes, language: str = None) -> str:
        """Transcribe audio to text"""
        language = language or self.language
        headers = {"Authorization": f"Token {self.api_key}"}
        params = {
            "model": self.model,
            "language": language,
            "punctuate": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.API_URL,
                    data=audio_data,
                    headers=headers,
                    params=params,
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Deepgram error: {error_text}")
                        raise Exception(f"Deepgram API error: {resp.status}")
                    
                    result = await resp.json()
                    transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
                    return transcript
        except Exception as e:
            logger.error(f"Deepgram transcription error: {e}")
            raise

    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes], language: str = None) -> AsyncIterator[str]:
        """Stream transcription"""
        language = language or self.language
        headers = {"Authorization": f"Token {self.api_key}"}
        params = {
            "model": self.model,
            "language": language,
            "punctuate": True,
            "interim_results": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Deepgram websocket for streaming
                async with session.ws_connect(
                    self.API_URL.replace("http", "ws"),
                    headers=headers,
                    params=params,
                ) as ws:
                    async for chunk in audio_stream:
                        await ws.send_bytes(chunk)
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            result = msg.json()
                            transcript = result.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
                            if transcript:
                                yield transcript
        except Exception as e:
            logger.error(f"Deepgram streaming error: {e}")
            raise
