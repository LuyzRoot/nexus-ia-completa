from core.agent import Agent

MULTILINGUAL_INSTRUCTION = (
    "Responda sempre no mesmo idioma que o usuário usou na mensagem mais recente. Se não for possível identificar, responda em português."
)

SAFETY_BASE = (
    "Priorize segurança: não execute código inseguro, não exponha chaves ou credenciais nos snippets gerados."
)

AGENT = Agent(
    id="coder",
    label="Coding Agent",
    description="Focado em engenharia de software: escreve código seguro, com testes e explicações sucintas.",
    system_prompt="Você é um engenheiro de software: gere código correto, testável e explique em 2-3 linhas. " + MULTILINGUAL_INSTRUCTION,
    default_temperature=0.0,
    supports_tools=True,
    supports_streaming=True,
    tools_allowed=["python_executor", "filesystem", "calculator"],
    autonomy_level=1,
    safety_instructions=SAFETY_BASE,
)