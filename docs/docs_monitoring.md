# Monitoring & Observability

Inclui:
- métricas Prometheus (endpoint `/metrics`)
- middleware FastAPI para instrumentação (`monitoring.middleware.MetricsMiddleware`)
- health endpoints: `/health/live` e `/health/ready`
- exemplos de alertas em `monitoring/alerts/rules.yaml`
- dashboard exemplo em `monitoring/grafana/dashboard.json`

Integração (resumida)
1. Instale dependências:
```bash
pip install -r monitoring/requirements.txt