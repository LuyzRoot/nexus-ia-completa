from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger(__name__)

class Plugin(ABC):
    """Base plugin class"""
    
    name: str
    version: str
    description: str
    
    @abstractmethod
    async def initialize(self):
        pass
    
    @abstractmethod
    async def shutdown(self):
        pass
    
    @abstractmethod
    async def execute(self, action: str, **kwargs) -> Any:
        pass

class PluginManager:
    """Manage plugins"""
    
    def __init__(self):
        self.plugins = {}
    
    def register(self, plugin: Plugin):
        self.plugins[plugin.name] = plugin
        logger.info(f"Plugin registered: {plugin.name}")
    
    async def execute(self, plugin_name: str, action: str, **kwargs):
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin not found: {plugin_name}")
        return await self.plugins[plugin_name].execute(action, **kwargs)
    
    async def shutdown_all(self):
        for plugin in self.plugins.values():
            await plugin.shutdown()
