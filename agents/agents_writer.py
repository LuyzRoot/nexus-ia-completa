from core.agent import Agent

MULTILINGUAL_INSTRUCTION = (
    "Responda sempre no mesmo idioma que o usuário usou na mensagem mais recente. Se não for possível identificar, responda em português."
)

AGENT = Agent(
    id="writer",
    label="Writer",
    description="Gera textos, e-mails, posts e documentação com tom ajustável.",
    system_prompt="Você é o Agente de Escrita: adapte tom e formato ao público e gere variações quando solicitado. " + MULTILINGUAL_INSTRUCTION,
    default_temperature=0.7,
    supports_tools=False,
    supports_streaming=False,
    tools_allowed=[],
    autonomy_level=1,
    safety_instructions=None,
)