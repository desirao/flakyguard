"""Configuration management for FlakyGuard-AI."""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "FlakyGuard-AI"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "default-dev-secret-key-32chars-min-len"

    # Git & Webhooks
    GITHUB_WEBHOOK_SECRET: str = "flakyguard-ci-hmac-secret-test"
    GITHUB_TOKEN: str = ""
    DEFAULT_REPO: str = "desirao/flakyguard"

    # Code Intelligence
    SOURCEGRAPH_URL: str = "http://localhost:7080"
    SOURCEGRAPH_TOKEN: str = ""
    SOURCEGRAPH_FALLBACK_GIT: bool = True

    # Datastores
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql://flakyguard:flakyguard_dev_password@localhost:5432/flakyguard_db"

    # LLM Settings
    DEFAULT_LLM_PROVIDER: Literal["heuristic", "ollama", "hosted"] = "heuristic"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Observability
    PROMETHEUS_METRICS_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
