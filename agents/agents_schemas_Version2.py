from pydantic import BaseModel, Field
from typing import List, Optional


class AgentCreate(BaseModel):
    id: str = Field(..., description="Identificador único do agente (ex: 'coder')")
    label: str
    description: Optional[str] = ""
    system_prompt: str
    default_temperature: float = 0.2
    max_tokens: int = 1024
    tools_allowed: Optional[List[str]] = None
    supports_streaming: bool = False
    supports_tools: bool = False
    autonomy_level: int = 0
    safety_instructions: Optional[str] = None
    metadata: Optional[dict] = None


class AgentUpdate(BaseModel):
    label: Optional[str]
    description: Optional[str]
    system_prompt: Optional[str]
    default_temperature: Optional[float]
    tools_allowed: Optional[List[str]]
    supports_streaming: Optional[bool]
    supports_tools: Optional[bool]
    autonomy_level: Optional[int]
    safety_instructions: Optional[str]
    metadata: Optional[dict]