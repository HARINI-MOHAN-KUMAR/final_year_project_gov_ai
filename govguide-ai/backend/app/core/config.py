"""
Core application configuration loaded from environment variables / .env file.
Uses pydantic-settings for type-safe configuration management.
"""

import json
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """All configurable settings for GovGuide AI."""

    # Application
    APP_NAME: str = "GovGuide AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "default-insecure-secret-key-change-in-production"

    # Database
    DATABASE_URL: str = "sqlite:///./govguide.db"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # LLM Provider (gemini | openai | anthropic | mock)
    LLM_PROVIDER: str = "mock"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"

    # Email / SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "govguide@example.com"
    EMAIL_ENABLED: bool = False

    # Frontend / CORS
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # OCR
    TESSERACT_CMD: str = "/usr/bin/tesseract"

    # RAG
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"

    # ML
    ML_MODEL_PATH: str = "./data/rf_model.joblib"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# Singleton settings object
settings = Settings()
