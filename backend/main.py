"""VoiceClone Guard — FastAPI entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import analyze, health, history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("VoiceClone Guard starting up…")
    await init_db()

    # Warm-up: pre-load the ML model so the first request is fast
    from app.services.detector import detector_service
    await detector_service.warm_up()

    logger.info("Ready ✓")
    yield
    logger.info("VoiceClone Guard shutting down…")


app = FastAPI(
    title="VoiceClone Guard API",
    description=(
        "Free, open-source voice deepfake detection. "
        "Upload or record audio to find out if it's real or AI-generated."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(history.router, prefix="/api")

# ── Static files (spectrograms) ───────────────────────────────────────────────
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
