"""Centralised configuration via environment variables."""

import os
from pydantic_settings import BaseSettings

# Compute the backend root directory from this file's location
# (backend/app/config.py → backend/)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    # ── Database ─────────────────────────────────────────────────────────────
    # Absolute path so it works regardless of the caller's cwd
    DATABASE_URL: str = f"sqlite+aiosqlite:///{_BACKEND_DIR}/data/voiceguard.db"

    # ── File storage ─────────────────────────────────────────────────────────
    UPLOAD_DIR: str = os.path.join(_BACKEND_DIR, "data", "uploads")
    MODEL_CACHE_DIR: str = os.path.join(_BACKEND_DIR, "data", "models")
    MAX_FILE_SIZE_MB: int = 25

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000"

    # ── ML model ──────────────────────────────────────────────────────────────
    USE_TRANSFORMER_MODEL: bool = False
    HF_MODEL_ID: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def max_file_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def hf_cache_dir(self) -> str:
        return os.path.join(self.MODEL_CACHE_DIR, "hf_cache")


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
os.makedirs(settings.hf_cache_dir, exist_ok=True)
