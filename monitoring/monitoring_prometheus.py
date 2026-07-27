"""
Prometheus integration helpers for NEXUS.

- REGISTRY: CollectorRegistry used by the app
- Core metrics registered on REGISTRY
- setup_prometheus(app, path="/metrics") mounts a /metrics route exposing the registry
- metrics_asgi_app() returns the prometheus_client ASGI app if you prefer mounting it directly
"""
import logging
from typing import Optional

from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST, make_asgi_app
from prometheus_client import Counter, Histogram, Gauge, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
from fastapi import FastAPI
from starlette.responses import Response

logger = logging.getLogger("monitoring.prometheus")

# One registry per process (default). If you run multiple Python processes (gunicorn),
# consider using prometheus_client multiprocess mode instead.
REGISTRY = CollectorRegistry(auto_describe=True)

# Register standard collectors (process / platform). They are instances exported by the library.
try:
    REGISTRY.register(PROCESS_COLLECTOR)
except Exception:
    # may already be registered; it's safe to ignore
    logger.debug("PROCESS_COLLECTOR already registered or failed to register")

try:
    REGISTRY.register(PLATFORM_COLLECTOR)
except Exception:
    logger.debug("PLATFORM_COLLECTOR already registered or failed to register")

# Core HTTP metrics
REQUEST_COUNT = Counter(
    "nexus_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
    registry=REGISTRY,
)

REQUEST_LATENCY = Histogram(
    "nexus_http_request_duration_seconds",
    "HTTP request latency seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY,
)

IN_FLIGHT = Gauge(
    "nexus_in_flight_requests",
    "In-flight HTTP requests",
    registry=REGISTRY,
)

EXCEPTIONS = Counter(
    "nexus_exceptions_total",
    "Total exceptions raised while handling requests",
    ["exception_type"],
    registry=REGISTRY,
)


def metrics_asgi_app():
    """
    Return the official prometheus_client ASGI app mounted against REGISTRY.
    Use this if you prefer to mount the complete ASGI app.
    """
    return make_asgi_app(registry=REGISTRY)


def setup_prometheus(app: FastAPI, path: str = "/metrics"):
    """
    Mount a simple metrics endpoint on the FastAPI app that serves REGISTRY.
    Usage:
      from monitoring.prometheus import setup_prometheus
      setup_prometheus(app)
    """
    @app.get(path, include_in_schema=False)
    async def _metrics():
        try:
            data = generate_latest(REGISTRY)
            return Response(content=data, media_type=CONTENT_TYPE_LATEST)
        except Exception as exc:
            logger.exception("Failed to generate metrics: %s", exc)
            return Response(content=b"", media_type="text/plain")