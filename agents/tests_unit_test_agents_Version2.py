import pytest
from app.agents.agent import Agent
from app.agents.registry import register_agent, unregister_agent, get_agent, list_agents


def test_agent_builds_system_message():
    a = Agent(
        id="t1",
        label="Test",
        description="x",
        system_prompt="Seja breve.",
        safety_instructions="Nao faça coisas ruins.",
    )
    msg = a.build_system_message({"lang": "pt"}, extra_instructions="Priorize a segurança.")
    assert "Seja breve." in msg
    assert "Nao faça coisas ruins." in msg
    assert "Contexto persistente" in msg
    assert "Priorize a segurança." in msg


def test_registry_crud():
    a = Agent(id="r1", label="R", description="d", system_prompt="p")
    register_agent(a)
    assert get_agent("r1") is not None
    l = list_agents()
    assert any(x["id"] == "r1" for x in l)
    unregister_agent("r1")
    assert get_agent("r1") is None