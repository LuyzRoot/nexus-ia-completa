from typing import Dict, List, Optional
from app.agents.agent import Agent
from app.agents.policies import tools_allowed_for_autonomy_level

# Instância de registry em memória por padrão. Pode ser substituída por persistência no DB.
_AGENTS: Dict[str, Agent] = {}


def register_agent(agent: Agent) -> None:
    _AGENTS[agent.id] = agent


def unregister_agent(agent_id: str) -> None:
    _AGENTS.pop(agent_id, None)


def get_agent(agent_id: str) -> Optional[Agent]:
    return _AGENTS.get(agent_id)


def list_agents() -> List[Dict]:
    return [{"id": a.id, "label": a.label, "description": a.description, "autonomy_level": a.autonomy_level} for a in _AGENTS.values()]


def create_agent_from_spec(spec: Dict) -> Agent:
    """
    Cria um Agent a partir de um dict (por exemplo payload da API) e aplica defaults de tools
    com base no autonomy_level caso tools_allowed não venha preenchido.
    """
    if "tools_allowed" not in spec or not spec.get("tools_allowed"):
        # derive default from autonomy_level and available tools registry (caller should pass available_tools)
        available = spec.get("_available_tools", [])
        spec["tools_allowed"] = list(tools_allowed_for_autonomy_level(spec.get("autonomy_level", 0), available))
    agent = Agent.from_dict(spec)
    register_agent(agent)
    return agent


# --- carregar alguns agentes padrão (exemplo pronto) ---
def load_defaults(default_agents: List[Agent]) -> None:
    for a in default_agents:
        register_agent(a)