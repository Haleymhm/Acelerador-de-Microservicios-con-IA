"""Pydantic schemas for risk detection — probability and impact classification."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Severity level of an identified risk."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    """Category that classifies the nature of a risk."""

    TECHNICAL = "technical"
    SCHEDULE = "schedule"
    RESOURCE = "resource"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class Risk(BaseModel):
    """A single identified risk with probability and impact scores."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., description="Short descriptive title of the risk")
    description: str = Field(..., description="Detailed explanation of the risk")
    category: RiskCategory = Field(..., description="Category of the risk")
    level: RiskLevel = Field(..., description="Severity level")
    probability: float = Field(
        ..., ge=0.0, le=1.0, description="Likelihood of occurrence (0.0 to 1.0)"
    )
    impact: float = Field(
        ..., ge=0.0, le=1.0, description="Potential impact magnitude (0.0 to 1.0)"
    )
    mitigation: str | None = Field(
        default=None, description="Suggested mitigation strategy"
    )


class RiskReport(BaseModel):
    """Collection of risks identified for a given source document."""

    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_filename: str = Field(..., description="Name of the analyzed document")
    risks: list[Risk] = Field(default_factory=list)
    summary: str = Field(default="", description="Executive summary of the risk analysis")


# ── JSON schema sent to the LLM to enforce structured output ──────────

RISK_RESPONSE_SCHEMA: dict = {  # type: ignore[type-arg]
    "type": "object",
    "properties": {
        "risks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": [c.value for c in RiskCategory],
                    },
                    "level": {
                        "type": "string",
                        "enum": [level.value for level in RiskLevel],
                    },
                    "probability": {"type": "number", "minimum": 0, "maximum": 1},
                    "impact": {"type": "number", "minimum": 0, "maximum": 1},
                    "mitigation": {"type": "string"},
                },
                "required": [
                    "title",
                    "description",
                    "category",
                    "level",
                    "probability",
                    "impact",
                ],
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["risks", "summary"],
}
