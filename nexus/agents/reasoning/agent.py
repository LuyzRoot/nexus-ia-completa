from nexus.agents.planner.agent import Agent

class ReasoningAgent(Agent):
    """Multi-step reasoning and problem solving"""
    
    async def think(self, input_text: str) -> str:
        return f"Reasoning about: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Reasoning result: {action}"
