"""Risk Analyzer orchestrator — coordinates dependency extraction and risk detection.

This service follows the AGENT.md rule of separating:
  1. Dependency Identification (graph) — Step 1
  2. Risk Detection (probability/impact) — Step 2

Each step makes an independent call to Amazon Bedrock with its own
JSON schema, then results are persisted to DynamoDB.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.aws_provider import AWSProvider
from app.core.config import Settings, get_settings
from app.models.analysis import AnalysisResult
from app.models.dependency import (
    DEPENDENCY_RESPONSE_SCHEMA,
    DependencyEdge,
    DependencyGraph,
    DependencyNode,
)
from app.models.risk import (
    RISK_RESPONSE_SCHEMA,
    Risk,
    RiskReport,
)
from app.services.bedrock_service import BedrockService

logger = logging.getLogger(__name__)


# ── Prompt templates ──────────────────────────────────────────────────

_DEPENDENCY_PROMPT = """\
Analyze the following project documentation and identify ALL dependencies \
between components, services, teams, and modules. For each dependency, \
describe the nature of the relationship (depends_on, blocks, consumes, produces).

---
DOCUMENT:
{text}
---

Respond with a JSON object containing "nodes" and "edges" arrays.
"""

_RISK_PROMPT = """\
Analyze the following project documentation and identify ALL risks. \
Classify each risk by category (technical, schedule, resource, security, compliance), \
assign a severity level (low, medium, high, critical), and estimate the \
probability (0.0-1.0) and impact (0.0-1.0). Suggest a mitigation strategy \
when possible.

---
DOCUMENT:
{text}
---

Respond with a JSON object containing a "risks" array and a "summary" string.
"""


class RiskAnalyzerService:
    """Orchestrates the full analysis pipeline: text → LLM → parsed results → DynamoDB.

    Usage::
        analyzer = RiskAnalyzerService(aws_provider)
        result = await analyzer.analyze("some document text...", "doc.md")
    """

    def __init__(
        self,
        aws_provider: AWSProvider,
        settings: Settings | None = None,
    ) -> None:
        self._aws = aws_provider
        self._settings = settings or get_settings()
        self._bedrock = BedrockService(aws_provider, self._settings)

    async def analyze(
        self,
        text: str,
        source_filename: str,
    ) -> AnalysisResult:
        """Run the full two-step analysis and persist results.

        Step 1 — Dependency Identification (graph).
        Step 2 — Risk Detection (probability / impact).
        Step 3 — Persist to DynamoDB.

        Args:
            text: Plain text extracted from the source document.
            source_filename: Name of the original document.

        Returns:
            Combined AnalysisResult with both dependency graph and risk report.
        """
        analysis_id = str(uuid4())
        created_at = datetime.now(timezone.utc)

        logger.info("Starting analysis %s for '%s'", analysis_id, source_filename)

        # ── Step 1: Dependency Identification ─────────────────────────
        dependency_graph = await self._extract_dependencies(text)
        logger.info(
            "Identified %d nodes and %d edges",
            len(dependency_graph.nodes),
            len(dependency_graph.edges),
        )

        # ── Step 2: Risk Detection ────────────────────────────────────
        risk_report = await self._detect_risks(text, analysis_id, source_filename, created_at)
        logger.info("Detected %d risks", len(risk_report.risks))

        # ── Compose result ────────────────────────────────────────────
        result = AnalysisResult(
            analysis_id=analysis_id,
            created_at=created_at,
            source_filename=source_filename,
            status="completed",
            risk_report=risk_report,
            dependency_graph=dependency_graph,
        )

        # ── Step 3: Persist ───────────────────────────────────────────
        await self._persist_result(result)
        logger.info("Analysis %s persisted successfully", analysis_id)

        return result

    # ── Private pipeline steps ────────────────────────────────────────

    async def _extract_dependencies(self, text: str) -> DependencyGraph:
        """Call Bedrock to identify dependencies and return a DependencyGraph."""
        prompt = _DEPENDENCY_PROMPT.format(text=text)
        raw: dict[str, Any] = await self._bedrock.invoke_claude(
            prompt=prompt,
            response_schema=DEPENDENCY_RESPONSE_SCHEMA,
        )

        nodes = [DependencyNode(**node) for node in raw.get("nodes", [])]
        edges = [DependencyEdge(**edge) for edge in raw.get("edges", [])]
        return DependencyGraph(nodes=nodes, edges=edges)

    async def _detect_risks(
        self,
        text: str,
        analysis_id: str,
        source_filename: str,
        created_at: datetime,
    ) -> RiskReport:
        """Call Bedrock to detect risks and return a RiskReport."""
        prompt = _RISK_PROMPT.format(text=text)
        raw: dict[str, Any] = await self._bedrock.invoke_claude(
            prompt=prompt,
            response_schema=RISK_RESPONSE_SCHEMA,
        )

        risks = [Risk(**risk_data) for risk_data in raw.get("risks", [])]
        return RiskReport(
            analysis_id=analysis_id,
            created_at=created_at,
            source_filename=source_filename,
            risks=risks,
            summary=raw.get("summary", ""),
        )

    async def _persist_result(self, result: AnalysisResult) -> None:
        """Save the analysis result to DynamoDB."""
        async with self._aws.get_dynamodb_resource() as dynamodb:
            table = await dynamodb.Table(self._settings.dynamodb_table_name)
            await table.put_item(
                Item={
                    "analysis_id": result.analysis_id,
                    "created_at": result.created_at.isoformat(),
                    "source_filename": result.source_filename,
                    "status": result.status,
                    "risk_report": json.loads(result.risk_report.model_dump_json()),
                    "dependency_graph": json.loads(
                        result.dependency_graph.model_dump_json()
                    ),
                }
            )

    async def get_analysis_by_id(
        self, analysis_id: str
    ) -> AnalysisResult | None:
        """Retrieve a previously stored analysis from DynamoDB.

        Args:
            analysis_id: The unique identifier of the analysis.

        Returns:
            AnalysisResult if found, None otherwise.
        """
        async with self._aws.get_dynamodb_resource() as dynamodb:
            table = await dynamodb.Table(self._settings.dynamodb_table_name)
            response: dict[str, Any] = await table.get_item(
                Key={"analysis_id": analysis_id}
            )

        item = response.get("Item")
        if not item:
            return None

        return AnalysisResult(
            analysis_id=item["analysis_id"],
            created_at=datetime.fromisoformat(item["created_at"]),
            source_filename=item["source_filename"],
            status=item["status"],
            risk_report=RiskReport(**item["risk_report"]),
            dependency_graph=DependencyGraph(**item["dependency_graph"]),
        )
