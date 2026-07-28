from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    DATABASE_URL: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
