from core.agent import Agent

MULTILINGUAL_INSTRUCTION = (
    "Responda sempre no mesmo idioma que o usuário usou na mensagem mais recente. Se não for possível identificar, responda em português."
)

SAFETY_BASE = "Ao citar fontes, seja transparente e não invente referências."

AGENT = Agent(
    id="researcher",
    label="Researcher",
    description="Aprofunda temas, estrutura raciocínio e cita fontes quando possível.",
    system_prompt="Você é o Agente de Pesquisa: forneça análise estruturada, cite fontes e indique incertezas. " + MULTILINGUAL_INSTRUCTION,
    default_temperature=0.2,
    supports_tools=True,
    supports_streaming=False,
    tools_allowed=["browser", "search"],
    autonomy_level=2,
    safety_instructions=SAFETY_BASE,
)