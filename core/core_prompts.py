name=core/prompts.py
"""
Reusable prompt builders for agents and system messages.
"""

from typing import Dict, Optional

def build_system_prompt(base_prompt: str, safety_instructions: Optional[str] = None, long_term_memory: Optional[Dict[str, str]] = None, extra: Optional[str] = None) -> str:
    parts = [base_prompt.strip()]
    if safety_instructions:
        parts.append(safety_instructions.strip())
    if long_term_memory:
        lines = [f"- {k}: {v}" for k, v in long_term_memory.items()]
        parts.append("Contexto persistente:\n" + "\n".join(lines))
    if extra:
        parts.append(extra.strip())
    return "\n\n".join(parts)