"""GET /api/history — paginated list of past analyses."""

import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Analysis, get_db
from app.models.schemas import AnalysisHistoryResponse, AnalysisListItem, AnalysisResult, SpectralFeatures

router = APIRouter(tags=["History"])


@router.get("/history", response_model=AnalysisHistoryResponse)
async def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    verdict: Optional[str] = Query(None, description="Filter: REAL | FAKE"),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    q = select(Analysis).order_by(Analysis.created_at.desc())
    total_q = select(func.count()).select_from(Analysis)

    if verdict:
        q = q.where(Analysis.verdict == verdict.upper())
        total_q = total_q.where(Analysis.verdict == verdict.upper())

    total_result = await db.execute(total_q)
    total = total_result.scalar_one()

    result = await db.execute(q.offset(offset).limit(page_size))
    rows = result.scalars().all()

    items = [
        AnalysisListItem(
            id=r.id,
            filename=r.filename,
            duration_seconds=r.duration_seconds,
            verdict=r.verdict,
            confidence_pct=round(r.confidence * 100, 1),
            risk_level=r.risk_level,
            detection_method=r.detection_method,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return AnalysisHistoryResponse(total=total, items=items)


@router.get("/history/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")

    spectrogram_url = None
    if row.spectrogram_path:
        spectrogram_url = f"/uploads/{os.path.basename(row.spectrogram_path)}"

    features_raw = json.loads(row.features_json) if row.features_json else None
    features_obj = SpectralFeatures(**features_raw) if features_raw else None

    return AnalysisResult(
        id=row.id,
        filename=row.filename,
        file_size_bytes=row.file_size_bytes,
        duration_seconds=row.duration_seconds,
        sample_rate=row.sample_rate,
        verdict=row.verdict,
        confidence=row.confidence,
        confidence_pct=round(row.confidence * 100, 1),
        risk_level=row.risk_level,
        spectral_score=row.spectral_score,
        transformer_score=row.transformer_score,
        features=features_obj,
        spectrogram_url=spectrogram_url,
        detection_method=row.detection_method,
        created_at=row.created_at,
        indicators=[],
    )


@router.delete("/history/{analysis_id}", status_code=204)
async def delete_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    await db.delete(row)
    await db.commit()
