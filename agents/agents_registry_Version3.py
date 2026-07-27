from typing import Dict, List, Optional
from importlib import import_module
from core.agent import Agent

_REGISTRY: Dict[str, Agent] = {}


def register_agent(agent: Agent) -> None:
    _REGISTRY[agent.id] = agent


def unregister_agent(agent_id: str) -> None:
    _REGISTRY.pop(agent_id, None)


def get_agent(agent_id: str) -> Optional[Agent]:
    return _REGISTRY.get(agent_id)


def list_agents() -> List[dict]:
    return [{"id": a.id, "label": a.label, "description": a.description, "autonomy_level": a.autonomy_level} for a in _REGISTRY.values()]


def load_default_agents():
    """
    Tenta importar módulos de agents/ com nomes conhecidos e registrar AGENT neles.
    Ajuste a lista se criar/remover arquivos.
    """
    modules = [
        "agents.assistant",
        "agents.coder",
        "agents.researcher",
        "agents.writer",
        "agents.planner",
        "agents.autonomous",
    ]
    for m in modules:
        try:
            mod = import_module(m)
            agent = getattr(mod, "AGENT", None)
            if isinstance(agent, Agent):
                register_agent(agent)
        except Exception:
            # não interrompe o startup caso falte algum agente
            continue