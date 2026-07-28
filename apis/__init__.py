# apis package: helpers for discovery

from core.registry import Registry

registry = Registry()

def list_apis():
    return registry.discover("apis")
