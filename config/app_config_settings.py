from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator, AnyUrl
import os
import json


class Settings(BaseSettings):
    """
    Application settings loaded from environment (or .env).
    Use: from app.config import settings
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "NEXUS SYSTEM AI"
    ENV: str = "development"  # development | staging | production
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://nexus:nexus@localhost:5432/nexus_db"

    # JWT / Auth
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # Rate limiting
    RATE_LIMIT_DEFAULT: str = "60/minute"

    # Model Router / Providers
    MODEL_PROVIDER_PRIORITY: List[str] = ["anthropic", "openai", "gemini", "mock"]
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Voice (ElevenLabs) / STT (Deepgram)
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"
    DEEPGRAM_API_KEY: str = ""
    DEEPGRAM_MODEL: str = "nova-2"

    # CORS: list of origins. You can provide JSON array in env or comma-separated string.
    CORS_ORIGINS: List[str] = ["*"]

    # WhatsApp
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_APP_SECRET: str = ""
    WHATSAPP_ALLOWED_NUMBERS: str = ""  # comma-separated E.164 without +
    WHATSAPP_REPLY_WITH_VOICE: bool = True

    # Home Assistant
    HOME_ASSISTANT_URL: Optional[AnyUrl] = None
    HOME_ASSISTANT_TOKEN: str = ""

    # Observability
    LOG_LEVEL: str = "INFO"

    # Misc
    SENTRY_DSN: Optional[str] = None

    @validator("CORS_ORIGINS", pre=True)
    def _parse_cors_origins(cls, v):
        # Accept JSON array or comma-separated string
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("[") or v.startswith("{"):
                try:
                    parsed = json.loads(v)
                    return parsed
                except Exception:
                    # fall back to comma split
                    return [o.strip() for o in v.split(",") if o.strip()]
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @validator("WHATSAPP_ALLOWED_NUMBERS", pre=True)
    def _parse_whatsapp_allowed(cls, v):
        if not v:
            return ""
        if isinstance(v, str):
            return ",".join([p.strip() for p in v.split(",") if p.strip()])
        return v

    def validate_production(self):
        """
        Call at startup to enforce production-safe defaults.
        Raises RuntimeError if something critical is missing.
        """
        if self.ENV == "production":
            if self.DEBUG:
                raise RuntimeError("DEBUG must be False in production")
            if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY == "CHANGE_ME_IN_PRODUCTION":
                raise RuntimeError("JWT_SECRET_KEY must be set to a secure value in production")
            if not self.DATABASE_URL:
                raise RuntimeError("DATABASE_URL must be set in production")

    class Config:
        env_file_encoding = "utf-8"


# Create a singleton settings instance
settings = Settings()