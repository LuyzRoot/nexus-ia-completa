from typing import Optional, Dict, Any
from agents.registry import get_agent
# Tente integrar com suas funções de memória; se não existir, os imports falham silenciosamente
try:
    from memory.short_term import get_short_term_context
except Exception:
    def get_short_term_context(db, conversation_id, max_messages=20):
        # fallback simples
        return []

try:
    from memory.long_term import get_long_term_memory
except Exception:
    def get_long_term_memory(db, user_id):
        return {}

# NOTE: onde chamar seu LLM/orquestrador real, adapte abaixo (core/llm.py, executor, etc.)


class AgentManager:
    """
    Prepara mensagens (system + contexto) para um agente e retorna o payload pronto.
    A chamada ao LLM deve ser feita pelo seu pipeline (ex: core/llm, core.executor).
    """

    def __init__(self, db=None):
        self.db = db

    def prepare_messages_for_agent(
        self,
        agent_id: str,
        user_id: str,
        conversation_id: str,
        user_message: str,
        extra_instructions: str = "",
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        agent = get_agent(agent_id)
        if agent is None:
            raise ValueError("Agent não encontrado")

        long_term = get_long_term_memory(self.db, user_id) if self.db else {}
        short_term = get_short_term_context(self.db, conversation_id) if self.db else []
        # Inserir a nova mensagem como última do short term
        if user_message:
            short_term = short_term + [{"role": "user", "content": user_message}]

        system_msg = agent.to_system_role(long_term_memory=long_term, extra_instructions=extra_instructions, overrides=overrides)
        messages = [system_msg] + short_term

        # Retorna payload pronto para ser usado pelo seu LLM/orquestrador
        return {
            "agent_id": agent_id,
            "agent_label": agent.label,
            "temperature": agent.default_temperature,
            "messages": messages,
        }

    # Exemplo de stub para executar: adapte para chamar seu core/llm
    async def respond(self, payload: Dict) -> Dict:
        """
        Chamaria o LLM real. Aqui retornamos o payload para que você conecte ao core/llm.
        Integre com core/llm.generate(...) ou com seu executor de orquestração.
        """
        # Exemplo: import core.llm; resp = await core.llm.generate(payload['messages'], temperature=payload['temperature'])
        return {"note": "Integre AgentManager.respond ao seu core/llm", "payload": payload}