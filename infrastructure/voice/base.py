"""Base voice service abstraction"""
from abc import ABC, abstractmethod
from typing import AsyncIterator


class TextToSpeechProvider(ABC):
    """Abstract TTS provider"""

    @abstractmethod
    async def synthesize(self, text: str, voice_id: str = None, speed: float = 1.0) -> bytes:
        """Convert text to speech"""
        pass

    @abstractmethod
    async def synthesize_stream(self, text: str, voice_id: str = None, speed: float = 1.0) -> AsyncIterator[bytes]:
        """Stream TTS output"""
        pass


class SpeechToTextProvider(ABC):
    """Abstract STT provider"""

    @abstractmethod
    async def transcribe(self, audio_data: bytes, language: str = None) -> str:
        """Convert speech to text"""
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes], language: str = None) -> AsyncIterator[str]:
        """Stream STT output"""
        pass
