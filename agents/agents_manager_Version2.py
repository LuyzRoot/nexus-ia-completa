from typing import List, Dict, Optional
from app.agents.registry import get_agent
from app.memory import get_long_term_memory, get_short_term_context
from app.services.orchestrator import orchestrator  # seu orquestrador existente
from app.database import SessionLocal


class AgentManager:
    """
    Wrapper que prepara as mensagens (system + contexto) para o orquestrador,
    escolhe o agente apropriado, aplica overrides e dispara a chamada.
    Também suporta 'chaining' simples: pedir a um agente que gere um plano e outro que execute partes.
    """

    def __init__(self, db=None):
        self.db = db

    async def respond_with_agent(self, agent_id: str, user_id: str, conversation_id: str, user_message: str, overrides: Optional[Dict] = None):
        agent = get_agent(agent_id)
        if agent is None:
            raise ValueError("Agent não encontrado")

        # recuperar memórias
        # se o seu get_long_term_memory precisa de session, adapte: aqui assumimos que
        # será passado um objeto db ou o método lida sem ele.
        long_term = get_long_term_memory(self.db, user_id) if self.db else {}
        short_term = get_short_term_context(self.db, conversation_id) if self.db else [{"role": "user", "content": user_message}]

        system_msg = agent.to_system_role(long_term_memory=long_term, extra_instructions="", overrides=overrides)
        messages = [system_msg] + short_term
        # ajusta parâmetros do orquestrador conforme agente
        response = await orchestrator.complete(messages, temperature=agent.default_temperature)
        return response

    async def chain_agents(self, chain: List[str], user_id: str, conversation_id: str, user_message: str):
        """
        Exemplo de chaining:
        - primeiro agente (planner) gera um plano
        - segundo agente (coder) recebe o plano como contexto e tenta executar/gerar artefatos
        - devolve resumo consolidado
        """
        if not chain:
            raise ValueError("Chain vazio")
        # 1) run first agent
        first_resp = await self.respond_with_agent(chain[0], user_id, conversation_id, user_message)
        plan_text = getattr(first_resp, "text", "") or first_resp.get("text", "") if isinstance(first_resp, dict) else str(first_resp)
        # 2) run subsequent agents with plan as extra instruction
        results = {chain[0]: plan_text}
        for agent_id in chain[1:]:
            agent = get_agent(agent_id)
            if not agent:
                results[agent_id] = {"error": "agent not found"}
                continue
            long_term = get_long_term_memory(self.db, user_id) if self.db else {}
            system_msg = agent.to_system_role(long_term_memory=long_term, extra_instructions=f"Use o plano a seguir:\n{plan_text}")
            messages = [system_msg, {"role": "user", "content": user_message}]
            resp = await orchestrator.complete(messages, temperature=agent.default_temperature)
            results[agent_id] = resp
        return results