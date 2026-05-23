"""Audio loading, resampling, and normalisation utilities."""

import asyncio
import logging
from typing import Tuple

import librosa
import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)

TARGET_SR = 16_000          # 16 kHz — standard for speech models
MAX_DURATION_SEC = 120.0    # Trim very long clips


async def load_audio(path: str) -> Tuple[np.ndarray, int, float]:
    """
    Load an audio file asynchronously (runs in executor to avoid blocking).

    Returns:
        audio  — float32 numpy array, shape (samples,), range [-1, 1]
        sr     — sample rate after resampling (always TARGET_SR)
        duration_sec
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _load_sync, path)


def _load_sync(path: str) -> Tuple[np.ndarray, int, float]:
    try:
        audio, sr = librosa.load(path, sr=TARGET_SR, mono=True, dtype=np.float32)
    except Exception as e:
        logger.warning("librosa failed (%s), trying soundfile", e)
        audio, sr = sf.read(path, dtype="float32", always_2d=False)
        if audio.ndim == 2:
            audio = audio.mean(axis=1)
        if sr != TARGET_SR:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=TARGET_SR)
            sr = TARGET_SR

    # Trim silence at start/end
    audio, _ = librosa.effects.trim(audio, top_db=30)

    # Truncate to max duration
    max_samples = int(MAX_DURATION_SEC * TARGET_SR)
    if len(audio) > max_samples:
        logger.info("Trimming audio from %.1fs to %.1fs", len(audio)/TARGET_SR, MAX_DURATION_SEC)
        audio = audio[:max_samples]

    # Peak-normalise to [-1, 1]
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak

    duration = len(audio) / TARGET_SR
    return audio, sr, duration
