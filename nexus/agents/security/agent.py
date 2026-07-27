from nexus.agents.planner.agent import Agent

class SecurityAgent(Agent):
    """Handles security and validation"""
    
    async def think(self, input_text: str) -> str:
        return f"Security check: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Security validated: {action}"
