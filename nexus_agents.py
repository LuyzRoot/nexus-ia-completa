from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class Agent(ABC):
    """Base agent class"""
    
    @abstractmethod
    async def think(self, input_text: str) -> str:
        pass
    
    @abstractmethod
    async def act(self, action: str) -> str:
        pass

class PlannerAgent(Agent):
    """Planner Agent - Plans and orchestrates tasks"""
    
    async def think(self, input_text: str) -> str:
        return f"Planning: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Plan executed: {action}"

class CoderAgent(Agent):
    """Coder Agent - Generates and executes code"""
    
    async def think(self, input_text: str) -> str:
        return f"Analyzing code task: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Code executed: {action}"

class VisionAgent(Agent):
    """Vision Agent - Processes images"""
    
    async def think(self, input_text: str) -> str:
        return f"Analyzing image: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Vision result: {action}"

class BrowserAgent(Agent):
    """Browser Agent - Web automation"""
    
    async def think(self, input_text: str) -> str:
        return f"Browser task: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Browser action: {action}"

class SecurityAgent(Agent):
    """Security Agent - Validation and security"""
    
    async def think(self, input_text: str) -> str:
        return f"Security check: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Security validated: {action}"

class ReasoningAgent(Agent):
    """Reasoning Agent - Complex problem solving"""
    
    async def think(self, input_text: str) -> str:
        return f"Reasoning about: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Reasoning result: {action}"