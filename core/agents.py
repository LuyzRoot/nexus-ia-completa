"""
Sistema multiagente simplificado para o MVP: cada "agente" é, por enquanto,
um perfil de system prompt + parâmetros aplicados sobre o Model Orchestrator.
Evolução futura: agentes com estado próprio, ferramentas e execução autônoma (ver README).
"""

# Aplicada a TODOS os agentes: a IA responde no idioma em que o usuário
# escreveu/falou, sem assumir português. Detecção é feita pelo próprio
# modelo a partir da mensagem — não há lista fixa de idiomas suportados.
MULTILINGUAL_INSTRUCTION = (
    "Responda sempre no MESMO idioma que o usuário usou na mensagem mais recente, "
    "mesmo que o histórico da conversa esteja em outro idioma. Se não for possível "
    "identificar o idioma com confiança, responda em português."
)

AGENT_PROFILES = {
    "executive": {
        "label": "Executive",
        "system_prompt": (
            "Você é o agente Executivo do NEXUS SYSTEM AI: coordena tarefas, prioriza "
            "e responde de forma direta e objetiva, delegando implicitamente para outros "
            f"domínios quando necessário. {MULTILINGUAL_INSTRUCTION}"
        ),
    },
    "research": {
        "label": "Research",
        "system_prompt": (
            "Você é o agente de Pesquisa do NEXUS SYSTEM AI: aprofunda temas, cita "
            f"raciocínio estruturado e é rigoroso com evidências. {MULTILINGUAL_INSTRUCTION}"
        ),
    },
    "coding": {
        "label": "Coding",
        "system_prompt": (
            "Você é o agente de Engenharia de Software do NEXUS SYSTEM AI: escreve código "
            f"correto, testável e explica decisões técnicas de forma sucinta. {MULTILINGUAL_INSTRUCTION}"
        ),
    },
}

DEFAULT_AGENT = "executive"


def get_system_prompt(agent_type: str) -> str:
    profile = AGENT_PROFILES.get(agent_type, AGENT_PROFILES[DEFAULT_AGENT])
    return profile["system_prompt"]


def list_agents():
    return [{"id": k, "label": v["label"]} for k, v in AGENT_PROFILES.items()]
