from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from pydantic import BaseModel
from agents import registry
from agents.manager import AgentManager

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


class AgentCreateSchema(BaseModel):
    id: str
    label: str
    description: Optional[str] = ""
    system_prompt: str
    default_temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 1024
    tools_allowed: Optional[list] = []
    supports_streaming: Optional[bool] = False
    supports_tools: Optional[bool] = False
    autonomy_level: Optional[int] = 0
    safety_instructions: Optional[str] = None
    metadata: Optional[dict] = {}


class AgentUpdateSchema(BaseModel):
    label: Optional[str]
    description: Optional[str]
    system_prompt: Optional[str]
    default_temperature: Optional[float]
    max_tokens: Optional[int]
    tools_allowed: Optional[list]
    supports_streaming: Optional[bool]
    supports_tools: Optional[bool]
    autonomy_level: Optional[int]
    safety_instructions: Optional[str]
    metadata: Optional[dict]


@router.get("", summary="List all agents (public)")
def list_agents():
    return registry.list_agents()


@router.get("/{agent_id}", summary="Get agent details (public)")
def get_agent(agent_id: str):
    a = registry.get_agent(agent_id)
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return a.serialize()


# ---- Admin endpoints ----
# Substitua 'Depends(...)' abaixo pela sua dependência de admin (ex: require_admin) vinda de api/auth.py
def _fake_admin_dep():
    # apagar/alterar: apenas placeholder para evitar erro de import se você não tiver require_admin pronto
    return True


@router.post("", summary="Create agent (admin only)", status_code=status.HTTP_201_CREATED)
def create_agent(payload: AgentCreateSchema, admin=Depends(_fake_admin_dep)):
    spec = payload.model_dump()
    # criar Agent programaticamente e registrar
    try:
        from core.agent import Agent as CoreAgent

        agent = CoreAgent.from_dict(spec)
        registry.register_agent(agent)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return agent.serialize()


@router.put("/{agent_id}", summary="Update agent (admin only)")
def update_agent(agent_id: str, payload: AgentUpdateSchema, admin=Depends(_fake_admin_dep)):
    existing = registry.get_agent(agent_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    data = payload.model_dump(exclude_unset=True)
    obj = existing.serialize()
    obj.update(data)
    registry.unregister_agent(agent_id)
    from core.agent import Agent as CoreAgent

    agent = CoreAgent.from_dict(obj)
    registry.register_agent(agent)
    return agent.serialize()


@router.delete("/{agent_id}", summary="Delete agent (admin only)", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str, admin=Depends(_fake_admin_dep)):
    existing = registry.get_agent(agent_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    registry.unregister_agent(agent_id)
    return {"ok": True}


# ---- Invocation endpoint (uses conversation/context) ----
# Substitua 'Depends(...)' por sua dependência de usuário autenticado (ex: get_current_user)
def _fake_user_dep():
    return {"id": "anonymous"}


class InvokeSchema(BaseModel):
    conversation_id: str
    message: str
    extra_instructions: Optional[str] = ""
    overrides: Optional[dict] = None


@router.post("/{agent_id}/invoke", summary="Invoke agent with conversation context")
async def invoke_agent(agent_id: str, payload: InvokeSchema, user=Depends(_fake_user_dep)):
    manager = AgentManager(db=None)  # se tiver DB, passe aqui
    try:
        prepared = manager.prepare_messages_for_agent(
            agent_id=agent_id,
            user_id=user.get("id"),
            conversation_id=payload.conversation_id,
            user_message=payload.message,
            extra_instructions=payload.extra_instructions or "",
            overrides=payload.overrides or {},
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    # AQUI: conecte ao seu LLM/orquestrador real e retorne a resposta.
    # Exemplo (adaptar ao seu core/llm):
    # from core.llm import generate
    # resp = await generate(prepared["messages"], temperature=prepared["temperature"])
    # return {"reply": resp}
    resp = await manager.respond(prepared)  # stub: devolve payload com instrução de integração
    return resp