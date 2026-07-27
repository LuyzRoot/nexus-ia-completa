from typing import Set, Dict, Iterable


# Política global: mapeamento de tool_name -> categoria/risco (informacional, destructive, external_io)
DEFAULT_TOOL_RISK: Dict[str, str] = {
    "calculate": "informational",
    "get_current_datetime": "informational",
    "get_weather": "informational",
    "convert_unit": "informational",
    "create_todo": "mutating",
    "create_reminder": "mutating",
    "complete_todo": "mutating",
    "control_smart_home_device": "external_io",
    "github_create_issue": "external_io",
    "filesystem": "destructive",
    "python_executor": "destructive",
    "browser": "external_io",
}


def tools_allowed_for_autonomy_level(autonomy_level: int, available_tools: Iterable[str]) -> Set[str]:
    """
    Conveniência: por nível de autonomia, quais categorias permitimos por padrão.
    Níveis mais altos permitem ferramentas mais poderosas — mas é só uma sugestão de default.
    """
    allowed = set()
    for t in available_tools:
        risk = DEFAULT_TOOL_RISK.get(t, "informational")
        if autonomy_level <= 1 and risk == "informational":
            allowed.add(t)
        elif autonomy_level == 2 and risk in ("informational", "mutating"):
            allowed.add(t)
        elif autonomy_level >= 3:
            allowed.add(t)
    return allowed


def is_tool_high_risk(tool_name: str) -> bool:
    return DEFAULT_TOOL_RISK.get(tool_name) in ("destructive",)