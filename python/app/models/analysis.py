"""Combined analysis result schema used by the API layer."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.dependency import DependencyGraph
from app.models.risk import RiskReport


class AnalysisRequest(BaseModel):
    """Payload for requesting an analysis via raw text."""

    text: str = Field(..., min_length=10, description="Raw text to analyze")
    source_filename: str = Field(
        default="manual-input.txt",
        description="Descriptive name for the text source",
    )


class AnalysisStatus(BaseModel):
    """Lightweight status response returned immediately after submission."""

    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    status: str = Field(default="processing")
    message: str = Field(default="Analysis has been submitted for processing")


class AnalysisResult(BaseModel):
    """Full analysis output combining risk report and dependency graph."""

    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_filename: str
    status: str = Field(default="completed")
    risk_report: RiskReport
    dependency_graph: DependencyGraph
