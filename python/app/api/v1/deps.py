"""FastAPI dependency-injection helpers for the v1 API layer."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.core.aws_provider import AWSProvider
from app.core.config import Settings, get_settings
from app.services.risk_analyzer import RiskAnalyzerService


def _get_aws_provider(request: Request) -> AWSProvider:
    """Retrieve the AWSProvider instance attached to the app state."""
    provider: AWSProvider = request.app.state.aws_provider
    return provider


def _get_risk_analyzer(
    aws_provider: AWSProvider = Depends(_get_aws_provider),
    settings: Settings = Depends(get_settings),
) -> RiskAnalyzerService:
    """Build a RiskAnalyzerService with injected dependencies."""
    return RiskAnalyzerService(aws_provider=aws_provider, settings=settings)


# ── Annotated shortcuts for cleaner endpoint signatures ───────────────

SettingsDep = Annotated[Settings, Depends(get_settings)]
AWSProviderDep = Annotated[AWSProvider, Depends(_get_aws_provider)]
RiskAnalyzerDep = Annotated[RiskAnalyzerService, Depends(_get_risk_analyzer)]
