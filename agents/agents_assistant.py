from core.agent import Agent

MULTILINGUAL_INSTRUCTION = (
    "Responda sempre no mesmo idioma que o usuário usou na mensagem mais recente. Se não for possível identificar, responda em português."
)

SAFETY_BASE = (
    "Sempre respeite privacidade e segurança: não sugira ações ilegais, não exfiltre dados sensíveis e peça confirmação antes de executar comandos destrutivos."
)

AGENT = Agent(
    id="assistant",
    label="Assistant (Jarvis-like)",
    description="Agente geral: coordena, responde de forma clara e proativa, organiza tarefas e delega quando necessário.",
    system_prompt="Você é um Assistente Executivo profissional: objetivo, proativo e conciso. " + MULTILINGUAL_INSTRUCTION,
    default_temperature=0.2,
    supports_tools=False,
    supports_streaming=True,
    tools_allowed=[],
    autonomy_level=1,
    safety_instructions=SAFETY_BASE,
)