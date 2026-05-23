"""Health-check endpoint."""

import time
from app.models.schemas import HealthResponse
from app.services.detector import detector_service
from fastapi import APIRouter

router = APIRouter(tags=["Health"])
_START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version="1.0.0",
        models_loaded=detector_service.models_loaded,
        uptime_seconds=round(time.time() - _START_TIME, 1),
    )
