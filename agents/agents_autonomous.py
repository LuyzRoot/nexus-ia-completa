from core.agent import Agent

MULTILINGUAL_INSTRUCTION = (
    "Responda sempre no mesmo idioma que o usuário usou na mensagem mais recente. Se não for possível identificar, responda em português."
)

AGENT = Agent(
    id="autonomous",
    label="Autonomous",
    description="Agente com maior autonomia para executar tarefas encadeadas usando ferramentas autorizadas (requer confirmação para ações perigosas).",
    system_prompt="Você é um Agente Autônomo: planeje, execute e verifique tarefas usando ferramentas autorizadas. Sempre peça confirmação para ações destrutivas. " + MULTILINGUAL_INSTRUCTION,
    default_temperature=0.0,
    supports_tools=True,
    supports_streaming=False,
    tools_allowed=["python_executor", "filesystem", "browser", "github_create_issue"],
    autonomy_level=4,
    safety_instructions="Antes de executar comandos que alterem sistemas externos, peça confirmação explícita do usuário.",
)