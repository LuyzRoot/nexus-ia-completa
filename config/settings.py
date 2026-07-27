"""
NEXUS SYSTEM AI - Configuração Centralizada
Stack: OpenAI + Anthropic + Pinecone + Supabase + ElevenLabs + Deepgram + Tavily
Todas as integrações configuráveis via variáveis de ambiente (.env)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from enum import Enum


class Environment(str, Enum):
    """Ambientes suportados"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LLMProvider(str, Enum):
    """Provedores de LLM disponíveis"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    MOCK = "mock"


class Settings(BaseSettings):
    """Configuração centralizada da aplicação"""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ============================================================================
    # APP CONFIG
    # ============================================================================
    APP_NAME: str = "NEXUS SYSTEM AI - World Class Stack"
    APP_VERSION: str = "1.0.0"
    ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ============================================================================
    # AUTHENTICATION & SECURITY
    # ============================================================================
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_WITH_STRONG_SECRET"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Clerk (Modern Auth Platform)
    CLERK_API_KEY: str = ""
    CLERK_FRONTEND_API_URL: str = ""

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_CHAT: str = "30/minute"
    RATE_LIMIT_AUTH: str = "5/minute"

    # ============================================================================
    # DATABASE - SUPABASE (PostgreSQL)
    # ============================================================================
    SUPABASE_URL: str = "postgresql://user:password@localhost:5432/nexus_db"
    SUPABASE_API_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ============================================================================
    # VECTOR DB - PINECONE (Memória Vetorial)
    # ============================================================================
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east1-aws"
    PINECONE_INDEX_NAME: str = "nexus-vectors"
    PINECONE_DIMENSION: int = 1536  # OpenAI embeddings
    PINECONE_METRIC: str = "cosine"

    # ============================================================================
    # LLM - OPENAI (IA Principal)
    # ============================================================================
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: Optional[str] = None
    OPENAI_MODEL_CHAT: str = "gpt-4o"  # Latest GPT-4 with vision
    OPENAI_MODEL_MINI: str = "gpt-4o-mini"  # Fast and cheap
    OPENAI_MODEL_VISION: str = "gpt-4-vision"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TOP_P: float = 0.9
    OPENAI_FREQUENCY_PENALTY: float = 0.0
    OPENAI_PRESENCE_PENALTY: float = 0.0

    # ============================================================================
    # LLM - ANTHROPIC (IA Alternativa)
    # ============================================================================
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"  # Latest Claude
    ANTHROPIC_TEMPERATURE: float = 0.7
    ANTHROPIC_MAX_TOKENS: int = 4096

    # ============================================================================
    # LLM - GOOGLE GEMINI (Terceira opção)
    # ============================================================================
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_TEMPERATURE: float = 0.7

    # ============================================================================
    # LLM ROUTER - Orquestrador de Modelos
    # ============================================================================
    # Ordem de fallback: OpenAI -> Anthropic -> Gemini -> Mock
    MODEL_PROVIDER_PRIORITY: List[LLMProvider] = [
        LLMProvider.OPENAI,
        LLMProvider.ANTHROPIC,
        LLMProvider.GEMINI,
        LLMProvider.MOCK,
    ]
    LLM_RETRY_ATTEMPTS: int = 3
    LLM_TIMEOUT_SECONDS: int = 30

    # ============================================================================
    # VOICE - ELEVENLABS (Text-to-Speech)
    # ============================================================================
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Default: Rachel
    ELEVENLABS_STABILITY: float = 0.5
    ELEVENLABS_SIMILARITY_BOOST: float = 0.75
    ELEVENLABS_STYLE: float = 0.0
    ELEVENLABS_USE_SPEAKER_BOOST: bool = True

    # ============================================================================
    # VOICE - DEEPGRAM (Speech-to-Text)
    # ============================================================================
    DEEPGRAM_API_KEY: str = ""
    DEEPGRAM_MODEL: str = "nova-2"
    DEEPGRAM_LANGUAGE: str = "pt-BR"  # Português Brasil
    DEEPGRAM_ENCODING: str = "linear16"
    DEEPGRAM_SAMPLE_RATE: int = 16000

    # ============================================================================
    # WEB SEARCH - TAVILY
    # ============================================================================
    TAVILY_API_KEY: str = ""
    TAVILY_MAX_RESULTS: int = 10
    TAVILY_INCLUDE_ANSWER: bool = True
    TAVILY_INCLUDE_RAW_CONTENT: bool = False

    # ============================================================================
    # STORAGE - AMAZON S3
    # ============================================================================
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_NAME: str = "nexus-ai-storage"
    AWS_S3_URL_EXPIRATION: int = 3600  # 1 hour

    # ============================================================================
    # EMAIL - RESEND
    # ============================================================================
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "noreply@nexus-ai.com"
    RESEND_FROM_NAME: str = "NEXUS AI"

    # ============================================================================
    # PAYMENTS - STRIPE
    # ============================================================================
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_MONTHLY: str = ""
    STRIPE_PRICE_ID_YEARLY: str = ""

    # ============================================================================
    # MONITORING - SENTRY
    # ============================================================================
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # ============================================================================
    # WHATSAPP - Meta Business Platform
    # ============================================================================
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_SECRET: str = ""
    WHATSAPP_ALLOWED_NUMBERS: str = ""  # E.164 format, comma separated
    WHATSAPP_REPLY_WITH_VOICE: bool = True

    # ============================================================================
    # HOME ASSISTANT
    # ============================================================================
    HOME_ASSISTANT_URL: str = ""
    HOME_ASSISTANT_TOKEN: str = ""
    HOME_ASSISTANT_ENABLED: bool = False

    # ============================================================================
    # AUTOMATION - N8N
    # ============================================================================
    N8N_BASE_URL: str = ""
    N8N_API_KEY: str = ""
    N8N_WEBHOOK_SECRET: str = ""

    # ============================================================================
    # MAPS - GOOGLE MAPS PLATFORM
    # ============================================================================
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_MAPS_LANGUAGE: str = "pt-BR"

    # ============================================================================
    # CORS & SECURITY
    # ============================================================================
    CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    TRUSTING_PROXIES: List[str] = ["*"]

    # ============================================================================
    # CACHING - REDIS
    # ============================================================================
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 10
    CACHE_DEFAULT_TTL: int = 3600  # 1 hour

    # ============================================================================
    # BACKGROUND JOBS - CELERY (Optional)
    # ============================================================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]

    # ============================================================================
    # DEPLOYMENT - RAILWAY
    # ============================================================================
    RAILWAY_ENVIRONMENT: Optional[str] = None
    RAILWAY_STATIC_URL: Optional[str] = None

    # ============================================================================
    # EXTERNAL SERVICES
    # ============================================================================
    GITHUB_API_TOKEN: Optional[str] = None
    GITHUB_REPO_OWNER: str = "LuyzRoot"
    GITHUB_REPO_NAME: str = "nexus-ia-completa"


# Singleton instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings
