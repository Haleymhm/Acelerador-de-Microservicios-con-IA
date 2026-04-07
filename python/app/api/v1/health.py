"""Health-check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Service health check",
    response_model=dict[str, str],
)
async def health_check() -> dict[str, str]:
    """Return a simple status indicator for load-balancers and monitoring."""
    return {"status": "ok", "service": "risk-analysis-accelerator"}
