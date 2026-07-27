"""Researcher Agent - Web research and information gathering"""
import logging
from typing import AsyncIterator, Optional
import time

from core.agent_runtime.base import BaseAgent, AgentResponse, Message
from infrastructure.llm.router import llm_router
from infrastructure.search.tavily import TavilySearchProvider

logger = logging.getLogger(__name__)


RESEARCHER_SYSTEM_PROMPT = """
You are an expert researcher assistant. Your role is to:
- Conduct thorough research on various topics
- Gather and synthesize information from multiple sources
- Provide fact-based, well-sourced answers
- Identify reliable sources and cross-reference information
- Present findings in a clear, organized manner
- Highlight key insights and conclusions

When asked to research:
1. Search for relevant information
2. Evaluate source credibility
3. Synthesize findings
4. Cite sources appropriately
5. Provide balanced perspectives

Always be thorough and accurate in your research.
"""


class ResearcherAgent(BaseAgent):
    """Agent specialized in research and information gathering"""

    def __init__(self):
        super().__init__(
            name="Researcher",
            description="Research and information gathering expert",
            system_prompt=RESEARCHER_SYSTEM_PROMPT,
        )
        self.search_provider = TavilySearchProvider()

    async def process(self, message: str) -> AgentResponse:
        """Process research request"""
        start_time = time.time()
        
        # Add user message to history
        user_msg = Message(role="user", content=message)
        self.add_to_history(user_msg)
        
        # Perform web search if needed
        search_results = None
        if any(keyword in message.lower() for keyword in ["research", "search", "find", "latest", "current"]):
            try:
                search_results = await self.search_provider.search(message, max_results=5)
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        # Add search results to context
        if search_results:
            search_context = "Recent search results:\n"
            for result in search_results:
                search_context += f"- {result.title}: {result.snippet}\n"
            messages.append({"role": "system", "content": search_context})
        
        # Add conversation history
        for msg in self.get_history():
            messages.append({"role": msg.role, "content": msg.content})
        
        try:
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
                metadata={"search_performed": search_results is not None},
            )
        except Exception as e:
            logger.error(f"Researcher agent error: {e}")
            raise

    async def stream_process(self, message: str) -> AsyncIterator[str]:
        """Stream researcher response"""
        # Add user message to history
        user_msg = Message(role="user", content=message)
        self.add_to_history(user_msg)
        
        # Perform web search
        search_results = None
        if any(keyword in message.lower() for keyword in ["research", "search", "find"]):
            try:
                search_results = await self.search_provider.search(message, max_results=5)
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        if search_results:
            search_context = "Recent search results:\n"
            for result in search_results:
                search_context += f"- {result.title}: {result.snippet}\n"
            messages.append({"role": "system", "content": search_context})
        
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
            
            assistant_msg = Message(role="assistant", content=full_response)
            self.add_to_history(assistant_msg)
        except Exception as e:
            logger.error(f"Researcher agent streaming error: {e}")
            raise
