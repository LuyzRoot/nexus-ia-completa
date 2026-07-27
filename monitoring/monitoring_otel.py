"""
OpenTelemetry minimal initializer (optional).

Call setup_otel_if_configured() at app startup. If opentelemetry libraries are missing or
OTLP endpoint is not configured, this is a no-op.
"""
import logging
from app.config.settings import settings

logger = logging.getLogger("monitoring.otel")

def setup_otel_if_configured():
    otlp_endpoint = getattr(settings, "OTLP_ENDPOINT", None)
    if not otlp_endpoint:
        logger.debug("OTLP endpoint not configured; skipping OTEL init")
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        resource = Resource.create({"service.name": getattr(settings, "SERVICE_NAME", "nexus")})
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=getattr(settings, "OTLP_INSECURE", True))
        span_processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(span_processor)

        logger.info("OpenTelemetry initialized with endpoint %s", otlp_endpoint)
    except Exception as exc:
        logger.exception("Failed to initialize OpenTelemetry (continuing without it): %s", exc)