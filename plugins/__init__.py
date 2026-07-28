# Plugins package

from core.registry import Registry

registry = Registry()

def list_plugins():
    return registry.discover("plugins")
