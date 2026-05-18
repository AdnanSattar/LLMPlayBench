"""
Application configuration.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import json
import os
from typing import Any, List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "LLMPlayBench"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "admin-dev-key")
    READ_API_KEY: str = os.getenv("READ_API_KEY", "read-dev-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Security - CORS
    BACKEND_CORS_ORIGINS: Any = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # Backend (for development)
        "https://llmplaybench.example.com",  # Production domain
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        # Accept JSON array or comma-separated string
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [item.strip() for item in text.split(",") if item.strip()]
        return value

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data.db")

    # Model Settings
    CACHE_DIR: str = os.getenv("CACHE_DIR", "./models")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "google/flan-t5-small")
    MAX_NEW_TOKENS: int = int(os.getenv("MAX_NEW_TOKENS", 128))
    RESPONSE_BENCH: bool = os.getenv("RESPONSE_BENCH", "false").lower() == "true"
    # Generation defaults for causal LMs
    REPETITION_PENALTY: float = float(os.getenv("REPETITION_PENALTY", 1.2))
    NO_REPEAT_NGRAM_SIZE: int = int(os.getenv("NO_REPEAT_NGRAM_SIZE", 3))
    TOP_P: float = float(os.getenv("TOP_P", 0.9))
    TOP_K: int = int(os.getenv("TOP_K", 50))

    # Redis (for optional caching)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    USE_REDIS_CACHE: bool = os.getenv("USE_REDIS_CACHE", "true").lower() == "true"
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", 3600))  # 1 hour default

    model_config = {"case_sensitive": True}


settings = Settings()
