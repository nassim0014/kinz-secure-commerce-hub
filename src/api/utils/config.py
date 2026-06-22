"""Application configuration loaded from environment variables."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


class Settings:
    """Strongly-typed settings. Defaults match .env.example."""

    APP_NAME: str = os.getenv("APP_NAME", "KINZ Secure Commerce Hub")
    APP_VERSION: str = "1.0.0"

    # Server
    PORT_API: int = int(os.getenv("PORT_API", "8000"))
    NODE_ENV: str = os.getenv("NODE_ENV", "development")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://kinz_app:change_me@localhost:5432/kinz_commerce",
    )

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-only-change-me-in-production-please")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,https://kinz.vercel.app",
    )

    # Audit / logging
    AUDIT_LOG_PATH: str = os.getenv("AUDIT_LOG_PATH", "/tmp/kinz-audit.log")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ETL — file is src/api/utils/config.py, repo root is parents[3]
    ETL_CRON_SCHEDULE: str = os.getenv("ETL_CRON_SCHEDULE", "0 2 * * *")
    ETL_RAW_DIR: str = os.getenv("ETL_RAW_DIR", str(Path(__file__).resolve().parents[3] / "data" / "raw"))
    ETL_PROCESSED_DIR: str = os.getenv(
        "ETL_PROCESSED_DIR",
        str(Path(__file__).resolve().parents[3] / "data" / "processed"),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
