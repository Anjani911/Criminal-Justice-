from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SCRB AI Crime Intelligence Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./crime_intelligence.db"

    # JWT
    JWT_SECRET_KEY: str = "development-only-secret-key-scrb-crime-platform"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # AI
    GEMINI_API_KEY: str = ""

    # Zoho Catalyst
    ZOHO_CATALYST_PROJECT_ID: str = ""
    ZOHO_CATALYST_CLIENT_ID: str = ""
    ZOHO_CATALYST_CLIENT_SECRET: str = ""

    # Reports
    REPORT_STORAGE_PROVIDER: str = "catalyst"
    REPORTS_LOCAL_DIR: str = "storage/reports"

    # Production hardening
    CORS_ALLOWED_ORIGINS: str = "*"
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
