"""Async SQLite database with SQLAlchemy 2."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Use aiosqlite driver
_db_url = settings.DATABASE_URL
if _db_url.startswith("sqlite:///") and not _db_url.startswith("sqlite+aiosqlite"):
    _db_url = _db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

engine = create_async_engine(_db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    sample_rate = Column(Integer, nullable=True)

    # Detection result
    verdict = Column(String(10), nullable=False)          # "REAL" | "FAKE"
    confidence = Column(Float, nullable=False)             # 0.0 – 1.0
    risk_level = Column(String(10), nullable=False)        # "LOW" | "MEDIUM" | "HIGH"

    # Sub-scores
    spectral_score = Column(Float, nullable=True)
    transformer_score = Column(Float, nullable=True)

    # Feature data (JSON string)
    features_json = Column(Text, nullable=True)

    # Spectrogram image path (relative to UPLOAD_DIR)
    spectrogram_path = Column(String(512), nullable=True)

    # Method used
    detection_method = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
