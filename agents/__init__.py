# agents package

from core.registry import Registry

registry = Registry()

def list_agents():
    return registry.discover("agents")
