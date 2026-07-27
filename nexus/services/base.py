from abc import ABC, abstractmethod

class BaseService(ABC):
    """Base service class"""
    
    @abstractmethod
    async def initialize(self):
        pass
    
    @abstractmethod
    async def shutdown(self):
        pass
