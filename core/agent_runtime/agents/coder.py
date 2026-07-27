"""Coder Agent - Specialized in programming and code generation"""
import logging
from typing import AsyncIterator, Optional
import time

from core.agent_runtime.base import BaseAgent, AgentResponse, Message
from infrastructure.llm.router import llm_router

logger = logging.getLogger(__name__)


CODER_SYSTEM_PROMPT = """
You are an expert programmer assistant. Your role is to:
- Write clean, efficient, and well-documented code
- Explain programming concepts clearly
- Debug code issues and suggest improvements
- Follow best practices (SOLID, DRY, KISS principles)
- Support multiple programming languages
- Provide code reviews and optimization suggestions

Always provide:
1. Working code examples
2. Clear explanations
3. Testing suggestions
4. Performance considerations

Format code in markdown blocks with language specification.
"""


class CoderAgent(BaseAgent):
    """Agent specialized in coding tasks"""

    def __init__(self):
        super().__init__(
            name="Coder",
            description="Programming and code generation expert",
            system_prompt=CODER_SYSTEM_PROMPT,
        )

    async def process(self, message: str) -> AgentResponse:
        """Process coding request"""
        start_time = time.time()
        
        # Add user message to history
        user_msg = Message(role="user", content=message)
        self.add_to_history(user_msg)
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        # Add conversation history
        for msg in self.get_history():
            messages.append({"role": msg.role, "content": msg.content})
        
        try:
            # Get response from LLM router
            response = await llm_router.complete(
                messages=messages,
                temperature=0.7,
            )
            
            # Add assistant response to history
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
            logger.error(f"Coder agent error: {e}")
            raise

    async def stream_process(self, message: str) -> AsyncIterator[str]:
        """Stream coding response"""
        # Add user message to history
        user_msg = Message(role="user", content=message)
        self.add_to_history(user_msg)
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        for msg in self.get_history():
            messages.append({"role": msg.role, "content": msg.content})
        
        try:
            full_response = ""
            async for chunk in llm_router.stream_complete(
                messages=messages,
                temperature=0.7,
            ):
                full_response += chunk
                yield chunk
            
            # Add complete response to history
            assistant_msg = Message(role="assistant", content=full_response)
            self.add_to_history(assistant_msg)
        except Exception as e:
            logger.error(f"Coder agent streaming error: {e}")
            raise
