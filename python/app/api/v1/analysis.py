"""Analysis endpoints — submit documents for risk/dependency analysis and retrieve results."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.api.v1.deps import AWSProviderDep, RiskAnalyzerDep, SettingsDep
from app.models.analysis import AnalysisRequest, AnalysisResult, AnalysisStatus
from app.services.textract_service import TextractService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["Analysis"])

# ── In-memory store for background task results (MVP) ─────────────────
# In production, always query DynamoDB via RiskAnalyzerService.get_analysis_by_id
_background_results: dict[str, AnalysisResult] = {}


# ── POST /analyze — submit raw text ──────────────────────────────────


@router.post(
    "/analyze",
    response_model=AnalysisStatus,
    status_code=202,
    summary="Submit text for risk & dependency analysis",
    description=(
        "Accepts raw text and triggers a background analysis. "
        "Returns an analysis_id to poll for results."
    ),
)
async def submit_analysis(
    payload: AnalysisRequest,
    background_tasks: BackgroundTasks,
    analyzer: RiskAnalyzerDep,
) -> AnalysisStatus:
    """Submit text for asynchronous analysis (non-blocking)."""
    status = AnalysisStatus()
    analysis_id = status.analysis_id

    background_tasks.add_task(
        _run_analysis,
        analyzer=analyzer,
        text=payload.text,
        source_filename=payload.source_filename,
        analysis_id=analysis_id,
    )

    logger.info("Analysis %s submitted for processing", analysis_id)
    return status


# ── POST /analyze/file — submit a file ───────────────────────────────


@router.post(
    "/analyze/file",
    response_model=AnalysisStatus,
    status_code=202,
    summary="Upload a file for risk & dependency analysis",
    description=(
        "Upload a document (txt, md, pdf, image) to be analyzed. "
        "The file is uploaded to S3, text is extracted, and analysis runs in the background."
    ),
)
async def submit_file_analysis(
    background_tasks: BackgroundTasks,
    analyzer: RiskAnalyzerDep,
    aws_provider: AWSProviderDep,
    settings: SettingsDep,
    file: UploadFile = File(..., description="Document to analyze"),
) -> AnalysisStatus:
    """Upload a file, store in S3, extract text, and trigger analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Upload to S3
    file_content = await file.read()
    s3_key = f"uploads/{file.filename}"

    async with aws_provider.get_s3_client() as s3:
        await s3.put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=file_content,
        )
    logger.info("Uploaded %s to s3://%s/%s", file.filename, settings.s3_bucket_name, s3_key)

    status = AnalysisStatus()
    analysis_id = status.analysis_id

    background_tasks.add_task(
        _run_file_analysis,
        analyzer=analyzer,
        aws_provider=aws_provider,
        bucket=settings.s3_bucket_name,
        key=s3_key,
        source_filename=file.filename,
        analysis_id=analysis_id,
    )

    return status


# ── GET /analysis/{analysis_id} — retrieve results ───────────────────


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResult,
    summary="Get analysis result by ID",
    responses={
        404: {"description": "Analysis not found or still processing"},
    },
)
async def get_analysis(
    analysis_id: str,
    analyzer: RiskAnalyzerDep,
) -> AnalysisResult:
    """Retrieve a completed analysis result by its ID."""
    # Check in-memory cache first (background tasks store here)
    if analysis_id in _background_results:
        return _background_results[analysis_id]

    # Fall back to DynamoDB
    result = await analyzer.get_analysis_by_id(analysis_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis '{analysis_id}' not found or still processing",
        )
    return result


# ── Background task runners ──────────────────────────────────────────


async def _run_analysis(
    analyzer: Any,
    text: str,
    source_filename: str,
    analysis_id: str,
) -> None:
    """Execute analysis in the background and cache the result."""
    try:
        result = await analyzer.analyze(text=text, source_filename=source_filename)
        # Override the auto-generated ID with the one returned to the user
        result.analysis_id = analysis_id
        _background_results[analysis_id] = result
        logger.info("Background analysis %s completed", analysis_id)
    except Exception:
        logger.exception("Background analysis %s failed", analysis_id)


async def _run_file_analysis(
    analyzer: Any,
    aws_provider: Any,
    bucket: str,
    key: str,
    source_filename: str,
    analysis_id: str,
) -> None:
    """Extract text from S3, then run analysis in the background."""
    try:
        textract = TextractService(aws_provider)
        text = await textract.extract_text_from_s3(bucket=bucket, key=key)
        result = await analyzer.analyze(text=text, source_filename=source_filename)
        result.analysis_id = analysis_id
        _background_results[analysis_id] = result
        logger.info("Background file analysis %s completed", analysis_id)
    except Exception:
        logger.exception("Background file analysis %s failed", analysis_id)
