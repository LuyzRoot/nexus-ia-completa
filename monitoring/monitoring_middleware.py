"""
FastAPI middleware to instrument HTTP requests and populate Prometheus metrics.

Add to FastAPI with:
  app.add_middleware(MetricsMiddleware)

Notes:
- Normalizes path segments that look like numeric ids or long hex ids to avoid cardinality explosion.
- Uses metrics from monitoring.prometheus.
"""
import time
import re
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from monitoring.prometheus import REQUEST_COUNT, REQUEST_LATENCY, IN_FLIGHT, EXCEPTIONS

logger = logging.getLogger("monitoring.middleware")

# precompile regexes
_RE_HEX_ID = re.compile(r"/[0-9a-fA-F]{8,}")
_RE_NUM_ID = re.compile(r"/\d+")
_RE_UUID = re.compile(r"/[0-9a-fA-F\-]{36,}")

def _normalize_path(path: str) -> str:
    """
    Replace likely variable path segments with :id to reduce label cardinality.
    This is intentionally conservative.
    """
    p = _RE_UUID.sub("/:id", path)
    p = _RE_HEX_ID.sub("/:id", p)
    p = _RE_NUM_ID.sub("/:id", p)
    return p

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path or "/"
        endpoint = _normalize_path(path)
        IN_FLIGHT.inc()
        start = time.time()
        try:
            response = await call_next(request)
            status = getattr(response, "status_code", 500)
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=str(status)).inc()
            elapsed = time.time() - start
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)
            return response
        except Exception as exc:
            # count exception and re-raise
            EXCEPTIONS.labels(exception_type=exc.__class__.__name__).inc()
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status="500").inc()
            elapsed = time.time() - start
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)
            logger.exception("Unhandled exception in request: %s", exc)
            raise
        finally:
            IN_FLIGHT.dec()