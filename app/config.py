"""
Configuração central da aplicação.
Todos os valores sensíveis vêm de variáveis de ambiente (.env) — nunca hardcoded.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
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

    # Model Orchestrator — ordem de fallback entre provedores
    MODEL_PROVIDER_PRIORITY: List[str] = ["openai", "anthropic", "gemini", "mock"]

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Voice Engine — síntese de voz (ElevenLabs)
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # voz padrão ("Rachel"), trocável no .env
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"  # suporta pt-BR

    # Voice Engine — transcrição (Deepgram)
    DEEPGRAM_API_KEY: str = ""
    DEEPGRAM_MODEL: str = "nova-2"  # multi-idioma

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # WhatsApp (Meta Cloud API) — canal de comandos por voz/texto
    WHATSAPP_VERIFY_TOKEN: str = ""       # string arbitrária escolhida por você, usada só na verificação do webhook
    WHATSAPP_ACCESS_TOKEN: str = ""       # token permanente do app na Meta (System User)
    WHATSAPP_PHONE_NUMBER_ID: str = ""    # ID do número no WhatsApp Business
    WHATSAPP_APP_SECRET: str = ""         # usado pra validar a assinatura de cada webhook recebido
    WHATSAPP_ALLOWED_NUMBERS: str = ""    # números permitidos, separados por vírgula, formato E.164 sem "+" (ex: 5511999998888). Vazio = ninguém passa.
    WHATSAPP_REPLY_WITH_VOICE: bool = True  # se True e a mensagem recebida foi áudio, responde também em áudio (ElevenLabs)

    # Home Assistant — controle de casa inteligente via REST API local
    HOME_ASSISTANT_URL: str = ""          # ex: http://192.168.1.10:8123 ou https://SEU-DOMINIO (Nabu Casa)
    HOME_ASSISTANT_TOKEN: str = ""        # Long-Lived Access Token gerado no perfil do Home Assistant


settings = Settings()
