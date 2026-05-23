"""Pydantic schemas for API request / response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Analysis response ─────────────────────────────────────────────────────────

class SpectralFeatures(BaseModel):
    mfcc_mean: List[float] = Field(default_factory=list, description="Mean of 20 MFCC coefficients")
    spectral_centroid: float = Field(..., description="Mean spectral centroid (Hz)")
    spectral_bandwidth: float = Field(..., description="Mean spectral bandwidth (Hz)")
    spectral_rolloff: float = Field(..., description="Mean spectral rolloff frequency (Hz)")
    spectral_flatness: float = Field(..., description="Mean spectral flatness (0–1)")
    zero_crossing_rate: float = Field(..., description="Mean zero-crossing rate")
    harmonic_ratio: float = Field(..., description="Harmonic-to-noise ratio estimate")
    pitch_consistency: float = Field(..., description="Pitch regularity score (0–1)")
    tempo: float = Field(..., description="Estimated tempo (BPM)")
    rms_energy: float = Field(..., description="Mean RMS energy")


class AnalysisResult(BaseModel):
    id: int
    filename: str
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None

    verdict: str = Field(..., description="REAL or FAKE")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0–1")
    confidence_pct: float = Field(..., ge=0.0, le=100.0, description="Confidence score 0–100")
    risk_level: str = Field(..., description="LOW | MEDIUM | HIGH")

    spectral_score: Optional[float] = Field(None, description="Spectral analysis sub-score 0–1")
    transformer_score: Optional[float] = Field(None, description="Transformer model sub-score 0–1")

    features: Optional[SpectralFeatures] = None
    spectrogram_url: Optional[str] = None
    detection_method: Optional[str] = None

    created_at: datetime

    indicators: List[str] = Field(
        default_factory=list,
        description="Human-readable indicators explaining the verdict",
    )

    class Config:
        from_attributes = True


class AnalysisListItem(BaseModel):
    id: int
    filename: str
    duration_seconds: Optional[float] = None
    verdict: str
    confidence_pct: float
    risk_level: str
    detection_method: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisHistoryResponse(BaseModel):
    total: int
    items: List[AnalysisListItem]


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: Dict[str, bool]
    uptime_seconds: float
