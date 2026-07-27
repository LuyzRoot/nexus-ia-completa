# monitoring (NEXUS)

This folder provides a minimal, robust observability stack for NEXUS:

Contents
- prometheus.py  : Prometheus registry and setup helper
- middleware.py  : FastAPI middleware to collect HTTP metrics
- health.py      : liveness/readiness endpoints
- sentry.py      : optional Sentry initializer
- otel.py        : optional OpenTelemetry initializer
- alerts/        : example Prometheus alert rules
- prometheus.yml : example Prometheus scrape config
- docker-compose.yml : quick stack (Prometheus + Grafana)
- grafana/       : example dashboard JSON
- tests/         : smoke test for metrics

Integration (FastAPI)
1. Install dependencies:
   pip install -r monitoring/requirements.txt

2. In your app startup (app/main.py or app/startup.py):
   from monitoring.sentry import setup_sentry_if_configured
   from monitoring.otel import setup_otel_if_configured
   from monitoring.prometheus import setup_prometheus
   from monitoring.middleware import MetricsMiddleware
   from monitoring.health import router as health_router

   setup_sentry_if_configured()
   setup_otel_if_configured()
   setup_prometheus(app)          # mounts /metrics
   app.add_middleware(MetricsMiddleware)
   app.include_router(health_router, prefix="/health")

Notes
- Protect /metrics and /health endpoints in production (network ACLs, auth proxy).
- If using multiple worker processes (gunicorn), read prometheus_client multiprocess docs and adapt registry accordingly.
- Tune alert thresholds in alerts/rules.yaml to match your traffic.