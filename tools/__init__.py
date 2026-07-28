# tools package

from core.registry import Registry

registry = Registry()

def list_tools():
    return registry.discover("tools")
