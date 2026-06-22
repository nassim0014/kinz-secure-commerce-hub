"""Health & readiness endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from src.api.models.schemas import HealthResponse
from src.api.utils.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc),
    )
