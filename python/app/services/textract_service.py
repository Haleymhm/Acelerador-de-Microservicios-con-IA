"""Document text extraction service using Amazon Textract and plain-text fallback."""

import logging
from typing import Any

from app.core.aws_provider import AWSProvider

logger = logging.getLogger(__name__)

# File extensions that can be read directly as text without Textract
_PLAIN_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".yaml", ".yml"}


class TextractService:
    """Extracts text from documents stored in S3.

    - For plain text / markdown files: reads the object body directly.
    - For PDFs and images: uses Amazon Textract DetectDocumentText.
    """

    def __init__(self, aws_provider: AWSProvider) -> None:
        self._aws = aws_provider

    async def extract_text_from_s3(
        self, bucket: str, key: str
    ) -> str:
        """Download a file from S3 and extract its textual content.

        Args:
            bucket: S3 bucket name.
            key: S3 object key (path).

        Returns:
            Extracted plain text.
        """
        extension = _get_extension(key)

        if extension in _PLAIN_TEXT_EXTENSIONS:
            return await self._read_plain_text(bucket, key)

        return await self._extract_with_textract(bucket, key)

    # ── Private helpers ───────────────────────────────────────────────

    async def _read_plain_text(self, bucket: str, key: str) -> str:
        """Read an S3 object as UTF-8 text."""
        async with self._aws.get_s3_client() as s3:
            response: dict[str, Any] = await s3.get_object(Bucket=bucket, Key=key)
            body_bytes: bytes = await response["Body"].read()
            logger.info("Read plain text from s3://%s/%s (%d bytes)", bucket, key, len(body_bytes))
            return body_bytes.decode("utf-8")

    async def _extract_with_textract(self, bucket: str, key: str) -> str:
        """Use Textract DetectDocumentText for PDFs / images."""
        async with self._aws.get_textract_client() as textract:
            response: dict[str, Any] = await textract.detect_document_text(
                Document={
                    "S3Object": {
                        "Bucket": bucket,
                        "Name": key,
                    }
                }
            )

        blocks: list[dict[str, Any]] = response.get("Blocks", [])
        lines = [
            block["Text"]
            for block in blocks
            if block.get("BlockType") == "LINE" and "Text" in block
        ]
        extracted_text = "\n".join(lines)
        logger.info(
            "Extracted %d lines from s3://%s/%s via Textract",
            len(lines),
            bucket,
            key,
        )
        return extracted_text


def _get_extension(key: str) -> str:
    """Return the lowercase file extension from an S3 key."""
    dot_index = key.rfind(".")
    if dot_index == -1:
        return ""
    return key[dot_index:].lower()
