from nexus.agents.planner.agent import Agent

class VisionAgent(Agent):
    """Processes and analyzes images"""
    
    async def think(self, input_text: str) -> str:
        return f"Analyzing vision task: {input_text}"
    
    async def act(self, action: str) -> str:
        return f"Vision result: {action}"
