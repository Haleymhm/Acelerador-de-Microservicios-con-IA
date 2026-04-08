"""Centralized application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings backed by environment variables and .env file.

    All fields map 1:1 to an uppercase env var with the same name.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── AWS ───────────────────────────────────────────────────────────
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # ── Amazon Bedrock ────────────────────────────────────────────────
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # ── Amazon S3 ─────────────────────────────────────────────────────
    s3_bucket_name: str = "risk-analysis-docs"

    # ── Amazon DynamoDB ───────────────────────────────────────────────
    dynamodb_table_name: str = "risk-analysis-results"

    # ── Application ───────────────────────────────────────────────────
    app_env: str = "development"
    app_debug: bool = True
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
