import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceProvider(ABC):
    """Abstract voice provider"""
    
    @abstractmethod
    async def text_to_speech(self, text: str, language: str = "en") -> bytes:
        pass
    
    @abstractmethod
    async def speech_to_text(self, audio: bytes) -> str:
        pass

class MockVoiceProvider(VoiceProvider):
    """Mock voice provider for testing"""
    
    async def text_to_speech(self, text: str, language: str = "en") -> bytes:
        return f"[Audio: {text}]".encode()
    
    async def speech_to_text(self, audio: bytes) -> str:
        return "[Transcribed audio]"
