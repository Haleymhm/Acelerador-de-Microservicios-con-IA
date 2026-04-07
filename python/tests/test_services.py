"""Tests for service layer — BedrockService and RiskAnalyzerService."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.aws_provider import AWSProvider
from app.core.config import Settings
from app.services.bedrock_service import BedrockService
from app.services.risk_analyzer import RiskAnalyzerService


@pytest.fixture
def settings() -> Settings:
    """Test settings."""
    return Settings(
        aws_region="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        bedrock_model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        s3_bucket_name="test-bucket",
        dynamodb_table_name="test-table",
    )


@pytest.fixture
def mock_provider(settings: Settings) -> AWSProvider:
    """AWS provider with mocked session."""
    with patch("app.core.aws_provider.aioboto3"):
        return AWSProvider(settings=settings)


# ── BedrockService Tests ──────────────────────────────────────────────


class TestBedrockService:
    """Tests for the low-level Bedrock invocation service."""

    def test_build_system_prompt_contains_schema(self) -> None:
        """System prompt should embed the response schema."""
        schema = {"type": "object", "properties": {"foo": {"type": "string"}}}
        prompt = BedrockService._build_system_prompt(schema)

        assert "JSON Schema" in prompt
        assert '"foo"' in prompt
        assert "valid JSON" in prompt

    def test_build_payload_structure(self) -> None:
        """Payload should have anthropic_version, system, messages, and max_tokens."""
        payload = BedrockService._build_payload(
            system_prompt="You are an analyst.",
            user_prompt="Analyze this text.",
            max_tokens=2048,
        )

        assert payload["anthropic_version"] == "bedrock-2023-05-31"
        assert payload["max_tokens"] == 2048
        assert payload["system"] == "You are an analyst."
        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"
        assert payload["messages"][0]["content"] == "Analyze this text."

    @pytest.mark.asyncio
    async def test_invoke_claude_parses_response(
        self, mock_provider: AWSProvider, settings: Settings
    ) -> None:
        """invoke_claude should parse Claude's JSON text block from response."""
        expected_data = {"risks": [], "summary": "No risks found"}

        # Mock the Bedrock client
        mock_client = AsyncMock()
        mock_body = AsyncMock()
        mock_body.read.return_value = json.dumps({
            "content": [
                {"type": "text", "text": json.dumps(expected_data)}
            ]
        }).encode()
        mock_client.invoke_model.return_value = {"body": mock_body}

        # Patch the context manager
        mock_provider.get_bedrock_client = MagicMock()
        mock_provider.get_bedrock_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_provider.get_bedrock_client.return_value.__aexit__ = AsyncMock(
            return_value=False
        )

        service = BedrockService(aws_provider=mock_provider, settings=settings)
        result = await service.invoke_claude(
            prompt="Analyze this",
            response_schema={"type": "object"},
        )

        assert result == expected_data
        mock_client.invoke_model.assert_called_once()


# ── RiskAnalyzerService Tests ────────────────────────────────────────


class TestRiskAnalyzerService:
    """Tests for the orchestrator service."""

    @pytest.mark.asyncio
    async def test_analyze_calls_bedrock_twice(
        self, mock_provider: AWSProvider, settings: Settings
    ) -> None:
        """Analyze should make 2 separate Bedrock calls: dependencies + risks."""
        dependency_response = {
            "nodes": [
                {"id": "1", "name": "Auth Service", "type": "service"},
                {"id": "2", "name": "Payment Service", "type": "service"},
            ],
            "edges": [
                {"source_id": "2", "target_id": "1", "relationship": "depends_on"},
            ],
        }
        risk_response = {
            "risks": [
                {
                    "title": "DB Migration Failure",
                    "description": "Migration may fail during peak hours",
                    "category": "technical",
                    "level": "high",
                    "probability": 0.7,
                    "impact": 0.9,
                    "mitigation": "Run during maintenance window",
                }
            ],
            "summary": "One high-severity technical risk identified",
        }

        # Mock bedrock service to return different responses for each call
        call_count = 0

        async def mock_invoke(prompt: str, response_schema: dict, max_tokens: int = 4096) -> dict:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return dependency_response
            return risk_response

        # Mock DynamoDB persistence
        mock_table = AsyncMock()
        mock_table.put_item = AsyncMock()

        mock_dynamodb = AsyncMock()
        mock_dynamodb.Table = AsyncMock(return_value=mock_table)

        mock_provider.get_dynamodb_resource = MagicMock()
        mock_provider.get_dynamodb_resource.return_value.__aenter__ = AsyncMock(
            return_value=mock_dynamodb
        )
        mock_provider.get_dynamodb_resource.return_value.__aexit__ = AsyncMock(
            return_value=False
        )

        analyzer = RiskAnalyzerService(aws_provider=mock_provider, settings=settings)

        with patch.object(analyzer._bedrock, "invoke_claude", side_effect=mock_invoke):
            result = await analyzer.analyze(
                text="Payment service depends on auth. DB migration is risky.",
                source_filename="test.md",
            )

        # Verify 2 calls were made (dependencies + risks)
        assert call_count == 2

        # Verify dependency graph
        assert len(result.dependency_graph.nodes) == 2
        assert len(result.dependency_graph.edges) == 1
        assert result.dependency_graph.edges[0].relationship == "depends_on"

        # Verify risk report
        assert len(result.risk_report.risks) == 1
        assert result.risk_report.risks[0].title == "DB Migration Failure"
        assert result.risk_report.risks[0].probability == 0.7
        assert result.risk_report.summary == "One high-severity technical risk identified"

        # Verify status
        assert result.status == "completed"
        assert result.source_filename == "test.md"
