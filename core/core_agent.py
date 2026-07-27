from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Agent:
    """
    Abstração de um agente/persona.
    - tools_allowed: lista de skills/tools que o agente pode usar
    - autonomy_level: 0..5 (quanto de autonomia; níveis altos exigem confirmação antes de ações destrutivas)
    """
    id: str
    label: str
    description: str
    system_prompt: str
    default_temperature: float = 0.2
    max_tokens: int = 1024
    tools_allowed: List[str] = field(default_factory=list)
    supports_streaming: bool = False
    supports_tools: bool = False
    autonomy_level: int = 0
    safety_instructions: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def build_system_message(
        self,
        long_term_memory: Optional[Dict[str, str]] = None,
        extra_instructions: str = "",
        overrides: Optional[Dict[str, Any]] = None,
    ) -> str:
        parts = [self.system_prompt.strip()]
        if self.safety_instructions:
            parts.append(self.safety_instructions.strip())

        if long_term_memory:
            lines = [f"- {k}: {v}" for k, v in long_term_memory.items()]
            parts.append("Contexto persistente conhecido sobre o usuário:\n" + "\n".join(lines))

        if extra_instructions:
            parts.append(extra_instructions.strip())

        if overrides:
            ov_lines = [f"{k}: {v}" for k, v in overrides.items() if k.lower() not in ("jwt", "secret", "password")]
            if ov_lines:
                parts.append("Instruções temporárias:\n" + "\n".join(ov_lines))

        return "\n\n".join(parts)

    def to_system_role(self, long_term_memory: Optional[Dict[str, str]] = None, extra_instructions: str = "", overrides: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        return {"role": "system", "content": self.build_system_message(long_term_memory, extra_instructions, overrides)}

    def allows_tool(self, tool_name: str) -> bool:
        if not self.supports_tools:
            return False
        if not self.tools_allowed:
            return False
        return tool_name in self.tools_allowed

    def serialize(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        return cls(**data)