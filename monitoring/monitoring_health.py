"""
Health endpoints (liveness/readiness) for the NEXUS app.

- /health/live  : basic liveness check
- /health/ready : readiness checks for DB, Redis and example provider config

Include in your FastAPI app:
  from monitoring.health import router as health_router
  app.include_router(health_router, prefix="/health")
"""
import logging
from fastapi import APIRouter
from typing import Dict

router = APIRouter()
logger = logging.getLogger("monitoring.health")

@router.get("/live", include_in_schema=False)
def liveness():
    return {"status": "alive"}

@router.get("/ready", include_in_schema=False)
def readiness():
    results: Dict[str, bool] = {}

    # Database check (sync engine)
    try:
        from app.database.session import engine as sync_engine
        with sync_engine.connect() as conn:
            conn.execute("SELECT 1")
        results["database"] = True
    except Exception as exc:
        logger.exception("Database readiness check failed: %s", exc)
        results["database"] = False

    # Redis check (optional)
    try:
        from app.config.settings import settings
        redis_url = getattr(settings, "REDIS_URL", None)
        if redis_url:
            import redis as redis_lib
            r = redis_lib.from_url(redis_url)
            r.ping()
            results["redis"] = True
        else:
            results["redis"] = True  # not configured -> treat as OK
    except Exception as exc:
        logger.exception("Redis readiness check failed: %s", exc)
        results["redis"] = False

    # Example provider config check (e.g., OpenAI key presence)
    try:
        from app.config.settings import settings
        results["openai_key_present"] = bool(getattr(settings, "OPENAI_API_KEY", None))
    except Exception:
        results["openai_key_present"] = False

    overall = all(v for v in results.values())
    return {"ready": overall, "checks": results}