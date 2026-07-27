"""
Minimal Sentry initializer (optional).

Call setup_sentry_if_configured() at app startup. If SENTRY_DSN is not set or sentry-sdk
is not installed, this is a no-op.
"""
import logging
from typing import Optional
from app.config.settings import settings

logger = logging.getLogger("monitoring.sentry")

def setup_sentry_if_configured():
    dsn = getattr(settings, "SENTRY_DSN", "") or None
    if not dsn:
        logger.debug("Sentry DSN not configured; skipping Sentry init")
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        logging_integration = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        sentry_sdk.init(dsn=dsn, integrations=[logging_integration], traces_sample_rate=getattr(settings, "SENTRY_TRACES_SAMPLE_RATE", 0.0))
        logger.info("Sentry initialized")
    except Exception as exc:
        logger.exception("Failed to initialize Sentry (continuing without it): %s", exc)