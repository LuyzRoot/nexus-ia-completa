from typing import Dict, Optional
from .calculator import CalculatorSkill

_registry: Dict[str, object] = {}

def register(skill):
    _registry[skill.name] = skill

def get(name: str) -> Optional[object]:
    return _registry.get(name)

# Register defaults
register(CalculatorSkill())
