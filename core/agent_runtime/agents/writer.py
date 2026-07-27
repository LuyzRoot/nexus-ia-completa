"""Writer Agent - Content creation and writing"""
import logging
from typing import AsyncIterator
import time

from core.agent_runtime.base import BaseAgent, AgentResponse, Message
from infrastructure.llm.router import llm_router

logger = logging.getLogger(__name__)


WRITER_SYSTEM_PROMPT = """
You are an expert writer and content creator. Your role is to:
- Write engaging, well-structured content
- Adapt writing style to different audiences and formats
- Create blogs, articles, stories, and marketing copy
- Ensure clarity, grammar, and coherence
- Maintain consistent tone and voice
- Provide creative and original ideas

When writing:
1. Understand the target audience
2. Structure content logically
3. Use compelling language
4. Edit for clarity and impact
5. Maintain consistency throughout

Always prioritize quality and engagement in your writing.
"""


class WriterAgent(BaseAgent):
    """Agent specialized in content writing and creation"""

    def __init__(self):
        super().__init__(
            name="Writer",
            description="Content creation and writing expert",
            system_prompt=WRITER_SYSTEM_PROMPT,
        )

    async def process(self, message: str) -> AgentResponse:
        """Process writing request"""
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
                temperature=0.8,  # Higher temperature for more creative writing
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
            logger.error(f"Writer agent error: {e}")
            raise

    async def stream_process(self, message: str) -> AsyncIterator[str]:
        """Stream writing response"""
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
                temperature=0.8,
            ):
                full_response += chunk
                yield chunk
            
            assistant_msg = Message(role="assistant", content=full_response)
            self.add_to_history(assistant_msg)
        except Exception as e:
            logger.error(f"Writer agent streaming error: {e}")
            raise
