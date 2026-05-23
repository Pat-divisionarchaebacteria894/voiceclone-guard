"""POST /api/analyze — accept an audio file and return deepfake verdict."""

import json
import logging
import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import Analysis, get_db
from app.models.schemas import AnalysisResult, SpectralFeatures
from app.services.audio_preprocessor import load_audio
from app.services.detector import detector_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analysis"])

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm", ".opus"}


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    summary="Analyze an audio file for deepfake content",
    description=(
        "Upload a WAV, MP3, M4A, OGG, FLAC, WEBM, or OPUS file. "
        "Returns a verdict (REAL/FAKE), confidence score, and feature analysis."
    ),
)
async def analyze_audio(
    file: Annotated[UploadFile, File(description="Audio file to analyse (max 25 MB)")],
    db: AsyncSession = Depends(get_db),
):
    # ── Validate ──────────────────────────────────────────────────────────────
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > settings.max_file_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit.",
        )
    if len(contents) < 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too small to analyse.",
        )

    # ── Save raw upload ───────────────────────────────────────────────────────
    uid = uuid.uuid4().hex
    raw_path = os.path.join(settings.UPLOAD_DIR, f"{uid}{ext}")
    with open(raw_path, "wb") as f:
        f.write(contents)

    try:
        # ── Load & preprocess audio ───────────────────────────────────────────
        audio, sr, duration = await load_audio(raw_path)

        # ── Run detection ─────────────────────────────────────────────────────
        result = await detector_service.detect(audio, sr, uid)

        # ── Persist to DB ─────────────────────────────────────────────────────
        analysis = Analysis(
            filename=file.filename or f"audio{ext}",
            file_size_bytes=len(contents),
            duration_seconds=round(duration, 2),
            sample_rate=sr,
            verdict=result["verdict"],
            confidence=result["confidence"],
            risk_level=result["risk_level"],
            spectral_score=result.get("spectral_score"),
            transformer_score=result.get("transformer_score"),
            features_json=json.dumps(result.get("features", {})),
            spectrogram_path=result.get("spectrogram_path"),
            detection_method=result.get("detection_method"),
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

        # ── Build response ────────────────────────────────────────────────────
        spectrogram_url = None
        if analysis.spectrogram_path:
            spectrogram_url = f"/uploads/{os.path.basename(analysis.spectrogram_path)}"

        features_data = result.get("features")
        features_obj = SpectralFeatures(**features_data) if features_data else None

        return AnalysisResult(
            id=analysis.id,
            filename=analysis.filename,
            file_size_bytes=analysis.file_size_bytes,
            duration_seconds=analysis.duration_seconds,
            sample_rate=analysis.sample_rate,
            verdict=analysis.verdict,
            confidence=analysis.confidence,
            confidence_pct=round(analysis.confidence * 100, 1),
            risk_level=analysis.risk_level,
            spectral_score=analysis.spectral_score,
            transformer_score=analysis.transformer_score,
            features=features_obj,
            spectrogram_url=spectrogram_url,
            detection_method=analysis.detection_method,
            created_at=analysis.created_at,
            indicators=result.get("indicators", []),
        )

    except Exception as e:
        logger.exception("Analysis failed for %s", file.filename)
        # Clean up raw file on error
        if os.path.exists(raw_path):
            os.remove(raw_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis error: {str(e)}",
        )
