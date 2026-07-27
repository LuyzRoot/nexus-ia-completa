"""Planner Agent - Task planning and orchestration"""
import logging
from typing import AsyncIterator
import time

from core.agent_runtime.base import BaseAgent, AgentResponse, Message
from infrastructure.llm.router import llm_router

logger = logging.getLogger(__name__)


PLANNER_SYSTEM_PROMPT = """
You are an expert project planner and strategist. Your role is to:
- Break down complex tasks into manageable steps
- Create detailed project plans and timelines
- Identify dependencies and potential issues
- Provide strategic recommendations
- Optimize workflows and processes
- Set realistic milestones and deadlines

When planning:
1. Analyze the overall objective
2. Identify key tasks and subtasks
3. Determine dependencies and sequencing
4. Estimate time and resources
5. Create contingency plans

Always provide structured, actionable plans.
"""


class PlannerAgent(BaseAgent):
    """Agent specialized in planning and orchestration"""

    def __init__(self):
        super().__init__(
            name="Planner",
            description="Project planning and orchestration expert",
            system_prompt=PLANNER_SYSTEM_PROMPT,
        )

    async def process(self, message: str) -> AgentResponse:
        """Process planning request"""
        start_time = time.time()
        
        user_msg = Message(role="user", content=message)
        self.add_to_history(user_msg)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        for msg in self.get_history():
            messages.append({"role": msg.role, "content": msg.content})
        
        try:
            response = await llm_router.complete(
                messages=messages,
                temperature=0.6,  # Lower temperature for more structured output
            )
            
            assistant_msg = Message(role="assistant", content=response.text)
            self.add_to_history(assistant_msg)
            
            execution_time = (time.time() - start_time) * 1000
            
            return AgentResponse(
                text=response.text,
                agent_name=self.name,
                model_used=response.model,
                tokens_used=response.tokens_used,
                execution_time_ms=execution_time,
            )
        except Exception as e:
            logger.error(f"Planner agent error: {e}")
            raise

    async def stream_process(self, message: str) -> AsyncIterator[str]:
        """Stream planning response"""
        user_msg = Message(role="user", content=message)
        self.add_to_history(user_msg)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        for msg in self.get_history():
            messages.append({"role": msg.role, "content": msg.content})
        
        try:
            full_response = ""
            async for chunk in llm_router.stream_complete(
                messages=messages,
                temperature=0.6,
            ):
                full_response += chunk
                yield chunk
            
            assistant_msg = Message(role="assistant", content=full_response)
            self.add_to_history(assistant_msg)
        except Exception as e:
            logger.error(f"Planner agent streaming error: {e}")
            raise
