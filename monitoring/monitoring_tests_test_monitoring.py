import pytest
from monitoring.prometheus import REGISTRY, REQUEST_COUNT, REQUEST_LATENCY, IN_FLIGHT, EXCEPTIONS

def test_metrics_smoke():
    # Ensure registry exists and metrics accept labels/operations
    assert REGISTRY is not None
    REQUEST_COUNT.labels(method="GET", endpoint="/test", http_status="200").inc()
    REQUEST_LATENCY.labels(method="GET", endpoint="/test").observe(0.01)
    IN_FLIGHT.inc()
    IN_FLIGHT.dec()
    EXCEPTIONS.labels(exception_type="ValueError").inc()
    assert True