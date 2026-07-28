# skills package

from core.registry import Registry

registry = Registry()

def list_skills():
    return registry.discover("skills")
