"""FastAPI application factory with lifespan management and middleware."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from botocore.exceptions import ClientError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.aws_provider import AWSProvider
from app.core.config import get_settings

# ── Logging setup ─────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise and tear down application-scoped resources."""
    settings = get_settings()
    aws_provider = AWSProvider(settings=settings)

    # Attach to app state so Depends can access it
    app.state.aws_provider = aws_provider

    logger.info(
        "🚀 Risk Analysis Accelerator started (env=%s, region=%s, model=%s)",
        settings.app_env,
        settings.aws_region,
        settings.bedrock_model_id,
    )
    yield
    logger.info("🛑 Risk Analysis Accelerator shutting down")


# ── App factory ───────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title="Risk Analysis Accelerator",
        description=(
            "AI-powered microservice for automated risk detection and dependency "
            "identification using Amazon Bedrock (Claude 3)."
        ),
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        debug=settings.app_debug,
    )

    # ── CORS ──────────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────
    application.include_router(v1_router)

    # ── Global exception handler for AWS quota errors ─────────────────
    @application.exception_handler(ClientError)
    async def aws_client_error_handler(
        request: Request, exc: ClientError
    ) -> JSONResponse:
        error_code = exc.response.get("Error", {}).get("Code", "Unknown")
        error_message = exc.response.get("Error", {}).get("Message", str(exc))

        if error_code in (
            "ThrottlingException",
            "LimitExceededException",
            "TooManyRequestsException",
            "ServiceQuotaExceededException",
        ):
            logger.warning("AWS quota exceeded: %s — %s", error_code, error_message)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "AWS service quota exceeded. Please retry later.",
                    "error_code": error_code,
                },
            )

        logger.error("AWS ClientError: %s — %s", error_code, error_message)
        return JSONResponse(
            status_code=502,
            content={
                "detail": "An error occurred communicating with AWS.",
                "error_code": error_code,
            },
        )

    return application


# ── Module-level app instance (used by uvicorn) ──────────────────────
app = create_app()
