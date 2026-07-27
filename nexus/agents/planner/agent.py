from abc import ABC, abstractmethod

class Agent(ABC):
    """Base agent"""
    
    @abstractmethod
    async def think(self, input_text: str) -> str:
        pass
    
    @abstractmethod
    async def act(self, action: str) -> str:
        pass

class PlannerAgent(Agent):
    """Plans and orchestrates tasks"""
    
    async def think(self, input_text: str) -> str:
        # Uses LLM to create plan
        return f"Plan for: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Executing: {action}"
