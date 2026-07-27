"""
Configuração central da aplicação (melhorada).
Valida listas e exige JWT_SECRET_KEY em produção.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "NEXUS SYSTEM AI"
    ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://nexus:nexus@localhost:5432/nexus_db"

    # Auth / JWT
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # Rate limiting
    RATE_LIMIT_DEFAULT: str = "60/minute"

    MODEL_PROVIDER_PRIORITY: List[str] = Field(default_factory=lambda: ["openai", "anthropic", "gemini", "mock"])

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"

    DEEPGRAM_API_KEY: str = ""
    DEEPGRAM_MODEL: str = "nova-2"

    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_APP_SECRET: str = ""
    WHATSAPP_ALLOWED_NUMBERS: List[str] = Field(default_factory=list)
    WHATSAPP_REPLY_WITH_VOICE: bool = True

    HOME_ASSISTANT_URL: str = ""
    HOME_ASSISTANT_TOKEN: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    def _parse_cors(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("WHATSAPP_ALLOWED_NUMBERS", mode="before")
    def _parse_whatsapp(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("JWT_SECRET_KEY")
    def secret_must_change(cls, v, values):
        if values.get("ENV") == "production" and (not v or v == "CHANGE_ME_IN_PRODUCTION"):
            raise ValueError("JWT_SECRET_KEY must be set to a secure value in production")
        return v

settings = Settings()
