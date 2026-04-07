"""Tests for Pydantic models — risk, dependency, and analysis schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.risk import Risk, RiskCategory, RiskLevel, RiskReport, RISK_RESPONSE_SCHEMA
from app.models.dependency import (
    DependencyEdge,
    DependencyGraph,
    DependencyNode,
    DEPENDENCY_RESPONSE_SCHEMA,
)
from app.models.analysis import AnalysisRequest, AnalysisResult, AnalysisStatus


# ── Risk Models ───────────────────────────────────────────────────────


class TestRisk:
    """Tests for the Risk Pydantic model."""

    def test_valid_risk(self) -> None:
        """A correctly formed risk should instantiate without errors."""
        risk = Risk(
            title="Database migration failure",
            description="Migration may fail during peak hours",
            category=RiskCategory.TECHNICAL,
            level=RiskLevel.HIGH,
            probability=0.7,
            impact=0.9,
            mitigation="Run during maintenance window",
        )
        assert risk.title == "Database migration failure"
        assert risk.category == RiskCategory.TECHNICAL
        assert risk.level == RiskLevel.HIGH
        assert risk.probability == 0.7
        assert risk.impact == 0.9
        assert risk.id  # auto-generated UUID

    def test_risk_auto_generates_id(self) -> None:
        """Each Risk should get a unique auto-generated ID."""
        risk1 = Risk(
            title="R1",
            description="Desc",
            category=RiskCategory.SCHEDULE,
            level=RiskLevel.LOW,
            probability=0.1,
            impact=0.2,
        )
        risk2 = Risk(
            title="R2",
            description="Desc",
            category=RiskCategory.RESOURCE,
            level=RiskLevel.MEDIUM,
            probability=0.3,
            impact=0.4,
        )
        assert risk1.id != risk2.id

    def test_risk_probability_out_of_range(self) -> None:
        """Probability must be between 0.0 and 1.0."""
        with pytest.raises(ValidationError):
            Risk(
                title="Bad",
                description="Out of range",
                category=RiskCategory.TECHNICAL,
                level=RiskLevel.LOW,
                probability=1.5,
                impact=0.5,
            )

    def test_risk_impact_out_of_range(self) -> None:
        """Impact must be between 0.0 and 1.0."""
        with pytest.raises(ValidationError):
            Risk(
                title="Bad",
                description="Out of range",
                category=RiskCategory.TECHNICAL,
                level=RiskLevel.LOW,
                probability=0.5,
                impact=-0.1,
            )

    def test_risk_mitigation_optional(self) -> None:
        """Mitigation is optional and defaults to None."""
        risk = Risk(
            title="R",
            description="D",
            category=RiskCategory.SECURITY,
            level=RiskLevel.CRITICAL,
            probability=0.9,
            impact=0.9,
        )
        assert risk.mitigation is None


class TestRiskReport:
    """Tests for the RiskReport model."""

    def test_empty_risk_report(self) -> None:
        """A report with no risks should be valid."""
        report = RiskReport(source_filename="empty.md")
        assert report.risks == []
        assert report.summary == ""
        assert report.analysis_id  # auto-generated

    def test_risk_report_with_risks(self) -> None:
        """A report containing risks should serialize them correctly."""
        risk = Risk(
            title="R1",
            description="D",
            category=RiskCategory.COMPLIANCE,
            level=RiskLevel.MEDIUM,
            probability=0.5,
            impact=0.5,
        )
        report = RiskReport(
            source_filename="project.md",
            risks=[risk],
            summary="One risk found",
        )
        assert len(report.risks) == 1
        assert report.summary == "One risk found"


class TestRiskResponseSchema:
    """Validate the JSON schema constant for LLM output."""

    def test_schema_has_required_fields(self) -> None:
        """The schema must require 'risks' and 'summary'."""
        assert "risks" in RISK_RESPONSE_SCHEMA["required"]
        assert "summary" in RISK_RESPONSE_SCHEMA["required"]

    def test_schema_risk_item_properties(self) -> None:
        """Each risk item must define title, description, category, level, probability, impact."""
        item_props = RISK_RESPONSE_SCHEMA["properties"]["risks"]["items"]["properties"]
        expected = {"title", "description", "category", "level", "probability", "impact", "mitigation"}
        assert set(item_props.keys()) == expected


# ── Dependency Models ─────────────────────────────────────────────────


class TestDependencyGraph:
    """Tests for DependencyNode, DependencyEdge, and DependencyGraph."""

    def test_valid_graph(self) -> None:
        """A graph with nodes and edges should instantiate correctly."""
        node_a = DependencyNode(id="a", name="Auth Service", type="service")
        node_b = DependencyNode(id="b", name="Payment Service", type="service")
        edge = DependencyEdge(
            source_id="b",
            target_id="a",
            relationship="depends_on",
        )
        graph = DependencyGraph(nodes=[node_a, node_b], edges=[edge])

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert graph.edges[0].relationship == "depends_on"

    def test_empty_graph(self) -> None:
        """An empty graph is valid."""
        graph = DependencyGraph()
        assert graph.nodes == []
        assert graph.edges == []


class TestDependencyResponseSchema:
    """Validate the JSON schema constant for LLM dependency output."""

    def test_schema_has_required_fields(self) -> None:
        """The schema must require 'nodes' and 'edges'."""
        assert "nodes" in DEPENDENCY_RESPONSE_SCHEMA["required"]
        assert "edges" in DEPENDENCY_RESPONSE_SCHEMA["required"]


# ── Analysis Models ───────────────────────────────────────────────────


class TestAnalysisRequest:
    """Tests for the analysis request payload."""

    def test_valid_request(self) -> None:
        """A request with text content should be valid."""
        req = AnalysisRequest(
            text="The payment service depends on authentication.",
            source_filename="notes.md",
        )
        assert req.text.startswith("The payment")
        assert req.source_filename == "notes.md"

    def test_request_text_minimum_length(self) -> None:
        """Text must have at least 10 characters."""
        with pytest.raises(ValidationError):
            AnalysisRequest(text="short")

    def test_request_default_filename(self) -> None:
        """Source filename should default to manual-input.txt."""
        req = AnalysisRequest(text="A sufficiently long text for analysis")
        assert req.source_filename == "manual-input.txt"


class TestAnalysisStatus:
    """Tests for the lightweight status response."""

    def test_default_status(self) -> None:
        """Default status should be 'processing'."""
        status = AnalysisStatus()
        assert status.status == "processing"
        assert status.analysis_id  # auto-generated
        assert "submitted" in status.message.lower()
