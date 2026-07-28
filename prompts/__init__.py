# prompts package

from core.registry import Registry

registry = Registry()

def list_prompts():
    return registry.discover("prompts")
