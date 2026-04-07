"""Shared test fixtures for the Risk Analysis Accelerator test suite."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.aws_provider import AWSProvider
from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Return a Settings instance for testing (no real AWS required)."""
    return Settings(
        aws_region="us-east-1",
        aws_access_key_id="test-key",
        aws_secret_access_key="test-secret",
        bedrock_model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        s3_bucket_name="test-bucket",
        dynamodb_table_name="test-table",
        app_env="test",
        app_debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
def mock_aws_provider(test_settings: Settings) -> AWSProvider:
    """Return an AWSProvider with mocked session."""
    with patch("app.core.aws_provider.aioboto3") as mock_aioboto3:
        mock_session = MagicMock()
        mock_aioboto3.Session.return_value = mock_session
        provider = AWSProvider(settings=test_settings)
        return provider


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Return a FastAPI TestClient with mocked AWS dependencies.

    Sets up a DynamoDB mock that returns empty results for get_item,
    so endpoints that fall through to DynamoDB work correctly.
    """
    with patch("app.main.get_settings", return_value=test_settings):
        with patch("app.core.aws_provider.aioboto3"):
            app = create_app()
            provider = AWSProvider(settings=test_settings)

            # Set up DynamoDB mock chain: resource → Table → get_item
            mock_table = AsyncMock()
            mock_table.get_item = AsyncMock(return_value={})
            mock_table.put_item = AsyncMock()

            mock_dynamodb = AsyncMock()
            mock_dynamodb.Table = AsyncMock(return_value=mock_table)

            provider.get_dynamodb_resource = MagicMock()
            provider.get_dynamodb_resource.return_value.__aenter__ = AsyncMock(
                return_value=mock_dynamodb
            )
            provider.get_dynamodb_resource.return_value.__aexit__ = AsyncMock(
                return_value=False
            )

            app.state.aws_provider = provider
            yield TestClient(app)
