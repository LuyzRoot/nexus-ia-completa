import logging
import logging.config
from typing import Dict
from app.config.settings import settings

DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"


def _build_config(level: str = "INFO") -> Dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": DEFAULT_LOG_FORMAT},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            },
        },
        "root": {"handlers": ["console"], "level": level},
        "loggers": {
            "uvicorn": {"level": level, "handlers": ["console"], "propagate": False},
            "uvicorn.error": {"level": level, "handlers": ["console"], "propagate": False},
            "uvicorn.access": {"level": "INFO", "handlers": ["console"], "propagate": False},
        },
    }


def configure_logging():
    level = getattr(settings, "LOG_LEVEL", "INFO").upper()
    config = _build_config(level)
    logging.config.dictConfig(config)
    logging.getLogger("app.config.logging").debug("Logging configured at level %s", level)