from nexus.agents.planner.agent import Agent

class CoderAgent(Agent):
    """Generates and executes code"""
    
    async def think(self, input_text: str) -> str:
        return f"Planning code for: {input_text}"
    
    async def act(self, action: str) -> str:
        # Execute code safely
        return f"Code executed: {action}"
