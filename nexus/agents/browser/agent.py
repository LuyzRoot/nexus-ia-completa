from nexus.agents.planner.agent import Agent

class BrowserAgent(Agent):
    """Navigates and interacts with web browsers"""
    
    async def think(self, input_text: str) -> str:
        return f"Planning browser task: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Browser action: {action}"
