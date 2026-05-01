"""
Application Configuration using Pydantic Settings
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "OmniGrowth OS"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="info")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://omnigrowth:omnigrowth_dev_pass@localhost:5432/omnigrowth_db"
    )
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = Field(default=300)  # 5 minutes

    # Security
    SECRET_KEY: str = Field(default="dev_secret_key_change_in_production")
    JWT_SECRET_KEY: str = Field(default="jwt_secret_key_change_in_production")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    ENCRYPTION_KEY: str = Field(default="")  # Base64 encoded 32-byte key

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        return [origin.strip() for origin in v.split(",")]

    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100)

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    # Google Ads
    GOOGLE_ADS_DEVELOPER_TOKEN: str = Field(default="")
    GOOGLE_ADS_CLIENT_ID: str = Field(default="")
    GOOGLE_ADS_CLIENT_SECRET: str = Field(default="")

    # Meta Ads
    META_APP_ID: str = Field(default="")
    META_APP_SECRET: str = Field(default="")

    # OpenAI (for AI Copilot)
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview")

    # Anthropic Claude
    ANTHROPIC_API_KEY: str = Field(default="")
    ANTHROPIC_MODEL: str = Field(default="claude-3-opus-20240229")

    # Sentry (Error Tracking)
    SENTRY_DSN: str = Field(default="")

    # Feature Flags
    ENABLE_AI_COPILOT: bool = Field(default=True)
    ENABLE_ML_OPTIMIZER: bool = Field(default=True)
    ENABLE_AUTO_EXECUTION: bool = Field(default=False)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
