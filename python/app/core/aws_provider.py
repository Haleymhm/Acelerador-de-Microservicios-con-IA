"""Centralized AWS client provider using aioboto3 with retry configuration."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aioboto3
from botocore.config import Config as BotoConfig

from app.core.config import Settings, get_settings

# Adaptive retry strategy to handle AWS throttling gracefully
_RETRY_CONFIG = BotoConfig(
    retries={
        "max_attempts": 3,
        "mode": "adaptive",
    }
)


class AWSProvider:
    """Manages aioboto3 sessions and provides async context-manager clients.

    Usage::
        provider = AWSProvider()
        async with provider.get_bedrock_client() as client:
            response = await client.invoke_model(...)
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._session = aioboto3.Session(
            region_name=self._settings.aws_region,
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
        )

    # ── Client factories ──────────────────────────────────────────────

    @asynccontextmanager
    async def get_bedrock_client(self) -> AsyncGenerator[Any, None]:
        """Yield an async Bedrock Runtime client."""
        async with self._session.client(
            "bedrock-runtime",
            config=_RETRY_CONFIG,
        ) as client:
            yield client

    @asynccontextmanager
    async def get_textract_client(self) -> AsyncGenerator[Any, None]:
        """Yield an async Textract client."""
        async with self._session.client(
            "textract",
            config=_RETRY_CONFIG,
        ) as client:
            yield client

    @asynccontextmanager
    async def get_s3_client(self) -> AsyncGenerator[Any, None]:
        """Yield an async S3 client."""
        async with self._session.client(
            "s3",
            config=_RETRY_CONFIG,
        ) as client:
            yield client

    @asynccontextmanager
    async def get_dynamodb_resource(self) -> AsyncGenerator[Any, None]:
        """Yield an async DynamoDB resource (table-level API)."""
        async with self._session.resource(
            "dynamodb",
            config=_RETRY_CONFIG,
        ) as resource:
            yield resource
