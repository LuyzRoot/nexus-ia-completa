import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

class VisionProvider(ABC):
    """Abstract vision provider"""
    
    @abstractmethod
    async def analyze_image(self, image_path: str) -> dict:
        pass
    
    @abstractmethod
    async def describe_image(self, image_path: str) -> str:
        pass

class MockVisionProvider(VisionProvider):
    """Mock vision provider for testing"""
    
    async def analyze_image(self, image_path: str) -> dict:
        return {
            "objects": [],
            "text": "",
            "description": "Mock image analysis"
        }
    
    async def describe_image(self, image_path: str) -> str:
        return "This is a mock image description"
