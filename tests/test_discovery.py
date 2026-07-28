import pytest
from core.registry import Registry

def test_discover_all():
    reg = Registry()
    reg.discover_all()
    summary = reg.summary()
    # Ensure keys exist
    assert isinstance(summary, dict)
    assert "apis" in summary
    assert "plugins" in summary
