"""Low-level Amazon Bedrock (Claude 3) invocation service with structured JSON output."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from botocore.exceptions import ClientError

from app.core.aws_provider import AWSProvider
from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

# Maximum retry attempts for throttling / quota errors
_MAX_RETRIES = 3
_BASE_BACKOFF_SECONDS = 1.0


class BedrockService:
    """Invokes Amazon Bedrock (Anthropic Claude 3) with structured JSON prompts.

    The service enforces a JSON-only output by embedding the expected response
    schema in the system prompt, following the AGENT.md rule of always
    requesting a JSON schema from the LLM.
    """

    def __init__(
        self,
        aws_provider: AWSProvider,
        settings: Settings | None = None,
    ) -> None:
        self._aws = aws_provider
        self._settings = settings or get_settings()

    async def invoke_claude(
        self,
        prompt: str,
        response_schema: dict[str, Any],
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Send a prompt to Claude 3 via Bedrock and return parsed JSON.

        Args:
            prompt: The user-facing prompt text.
            response_schema: JSON Schema dict describing the expected output.
            max_tokens: Maximum tokens for the response.

        Returns:
            Parsed JSON dict matching the requested schema.

        Raises:
            RuntimeError: If invocation fails after all retries.
        """
        system_prompt = self._build_system_prompt(response_schema)
        payload = self._build_payload(system_prompt, prompt, max_tokens)

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                return await self._invoke(payload)
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code", "")
                if error_code in (
                    "ThrottlingException",
                    "LimitExceededException",
                    "TooManyRequestsException",
                    "ServiceQuotaExceededException",
                ):
                    wait_time = _BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                    logger.warning(
                        "AWS throttling (%s) on attempt %d/%d — retrying in %.1fs",
                        error_code,
                        attempt,
                        _MAX_RETRIES,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Bedrock invocation failed: %s", exc)
                    raise

        error_message = f"Bedrock invocation failed after {_MAX_RETRIES} retries"
        raise RuntimeError(error_message)

    # ── Private helpers ───────────────────────────────────────────────

    async def _invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute a single Bedrock InvokeModel call and parse the response."""
        async with self._aws.get_bedrock_client() as client:
            response = await client.invoke_model(
                modelId=self._settings.bedrock_model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload),
            )
            response_body = await response["body"].read()
            result: dict[str, Any] = json.loads(response_body)

        # Claude 3 returns content as a list; extract the text block
        content_blocks: list[dict[str, Any]] = result.get("content", [])
        text_content = ""
        for block in content_blocks:
            if block.get("type") == "text":
                text_content = block["text"]
                break

        parsed: dict[str, Any] = json.loads(text_content)
        logger.info("Bedrock response parsed successfully")
        return parsed

    @staticmethod
    def _build_system_prompt(response_schema: dict[str, Any]) -> str:
        """Build a system prompt that enforces JSON-only structured output."""
        schema_str = json.dumps(response_schema, indent=2)
        return (
            "You are an expert project risk analyst and dependency mapper. "
            "Analyze the provided text and respond ONLY with valid JSON. "
            "Do not include any text, markdown, or explanation outside the JSON object.\n\n"
            f"Your response MUST conform to this JSON Schema:\n{schema_str}"
        )

    @staticmethod
    def _build_payload(
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
    ) -> dict[str, Any]:
        """Build the Bedrock InvokeModel request payload for Claude 3."""
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        }
