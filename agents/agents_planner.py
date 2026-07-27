from core.agent import Agent

MULTILINGUAL_INSTRUCTION = (
    "Responda sempre no mesmo idioma que o usuário usou na mensagem mais recente. Se não for possível identificar, responda em português."
)

AGENT = Agent(
    id="planner",
    label="Planner",
    description="Divide objetivos em milestones e tarefas acionáveis; prioriza riscos e dependências.",
    system_prompt="Você é o Agente Planejador: produza planos acionáveis, milestones e próximos passos com responsáveis e riscos. " + MULTILINGUAL_INSTRUCTION,
    default_temperature=0.1,
    supports_tools=True,
    supports_streaming=False,
    tools_allowed=["calendar", "todo", "reminder"],
    autonomy_level=3,
    safety_instructions="Peça confirmação para ações que alterem sistemas externos.",
)