"""Orchestrates spectral + optional transformer detection and spectrogram generation."""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)


class DetectorService:
    """Singleton service loaded once at startup."""

    def __init__(self):
        self._spectral = None
        self._transformer = None
        self._ready = False

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def models_loaded(self) -> Dict[str, bool]:
        return {
            "spectral": self._spectral is not None,
            "transformer": self._transformer is not None,
        }

    # ── Warm-up ───────────────────────────────────────────────────────────────

    async def warm_up(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_models)
        self._ready = True

    def _load_models(self):
        # Always load spectral
        from ml.spectral import SpectralDetector
        self._spectral = SpectralDetector()
        logger.info("Spectral detector ready")

        # Optionally load transformer
        if settings.USE_TRANSFORMER_MODEL and settings.HF_MODEL_ID:
            try:
                from ml.transformer import TransformerDetector
                self._transformer = TransformerDetector(
                    model_id=settings.HF_MODEL_ID,
                    cache_dir=settings.hf_cache_dir,
                )
                logger.info("Transformer detector ready (%s)", settings.HF_MODEL_ID)
            except Exception as e:
                logger.warning("Transformer model failed to load (%s) — using spectral only", e)
                self._transformer = None

    # ── Main detection ────────────────────────────────────────────────────────

    async def detect(self, audio: np.ndarray, sr: int, uid: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._detect_sync, audio, sr, uid)

    def _detect_sync(self, audio: np.ndarray, sr: int, uid: str) -> Dict[str, Any]:
        # ── Spectral analysis (always) ─────────────────────────────────────
        spectral_result = self._spectral.analyze(audio, sr)
        spectral_fake_prob = spectral_result["fake_probability"]   # 0 → real, 1 → fake

        # ── Transformer (if loaded) ────────────────────────────────────────
        transformer_fake_prob: Optional[float] = None
        if self._transformer is not None:
            try:
                transformer_fake_prob = self._transformer.predict(audio, sr)
            except Exception as e:
                logger.warning("Transformer inference failed: %s", e)

        # ── Ensemble ──────────────────────────────────────────────────────
        if transformer_fake_prob is not None:
            fake_prob = 0.4 * spectral_fake_prob + 0.6 * transformer_fake_prob
            method = "ensemble"
        else:
            fake_prob = spectral_fake_prob
            method = "spectral"

        # ── Verdict ───────────────────────────────────────────────────────
        verdict = "FAKE" if fake_prob >= 0.5 else "REAL"
        confidence = fake_prob if verdict == "FAKE" else (1.0 - fake_prob)
        confidence = float(np.clip(confidence, 0.0, 1.0))

        # Risk level
        if confidence >= 0.80:
            risk_level = "HIGH"
        elif confidence >= 0.55:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # ── Spectrogram ────────────────────────────────────────────────────
        spec_path = self._generate_spectrogram(audio, sr, uid)

        # ── Indicators ─────────────────────────────────────────────────────
        indicators = self._build_indicators(spectral_result, verdict)

        return {
            "verdict": verdict,
            "confidence": confidence,
            "risk_level": risk_level,
            "spectral_score": float(spectral_fake_prob),
            "transformer_score": float(transformer_fake_prob) if transformer_fake_prob is not None else None,
            "features": spectral_result["features"],
            "spectrogram_path": spec_path,
            "detection_method": method,
            "indicators": indicators,
        }

    # ── Spectrogram generation ─────────────────────────────────────────────

    def _generate_spectrogram(self, audio: np.ndarray, sr: int, uid: str) -> Optional[str]:
        try:
            import librosa
            import librosa.display
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(2, 1, figsize=(10, 6), facecolor="#0f172a")
            fig.subplots_adjust(hspace=0.4)

            # Mel spectrogram
            mel = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
            mel_db = librosa.power_to_db(mel, ref=np.max)
            ax1 = axes[0]
            ax1.set_facecolor("#0f172a")
            img = librosa.display.specshow(mel_db, sr=sr, x_axis="time", y_axis="mel",
                                           fmax=8000, ax=ax1, cmap="inferno")
            ax1.set_title("Mel Spectrogram", color="white", fontsize=10, pad=4)
            ax1.tick_params(colors="white")
            ax1.yaxis.label.set_color("white")
            ax1.xaxis.label.set_color("white")

            # Waveform
            ax2 = axes[1]
            ax2.set_facecolor("#0f172a")
            times = np.linspace(0, len(audio) / sr, len(audio))
            ax2.plot(times, audio, color="#6366f1", linewidth=0.5, alpha=0.8)
            ax2.set_title("Waveform", color="white", fontsize=10, pad=4)
            ax2.tick_params(colors="white")
            ax2.set_xlabel("Time (s)", color="white")
            ax2.set_ylabel("Amplitude", color="white")
            for spine in ax2.spines.values():
                spine.set_edgecolor("#334155")

            out_path = os.path.join(settings.UPLOAD_DIR, f"{uid}_spec.png")
            plt.savefig(out_path, dpi=100, bbox_inches="tight",
                        facecolor="#0f172a", edgecolor="none")
            plt.close(fig)
            return out_path
        except Exception as e:
            logger.warning("Spectrogram generation failed: %s", e)
            return None

    # ── Human-readable indicators ──────────────────────────────────────────

    @staticmethod
    def _build_indicators(spectral_result: Dict, verdict: str) -> list:
        feats = spectral_result.get("features", {})
        flags = spectral_result.get("flags", {})
        indicators = []

        if flags.get("high_spectral_flatness"):
            indicators.append("Unusually uniform spectral energy — characteristic of synthesis")
        if flags.get("low_mfcc_variance"):
            indicators.append("Low MFCC variance — synthetic voices often lack natural micro-variation")
        if flags.get("smooth_pitch"):
            indicators.append("Overly regular pitch contour — real voices have natural micro-fluctuations")
        if flags.get("low_hnr"):
            indicators.append("Low harmonic-to-noise ratio — may indicate vocoder artifacts")
        if flags.get("missing_noise_floor"):
            indicators.append("Unusually clean noise floor — real recordings typically contain ambient noise")
        if flags.get("high_spectral_symmetry"):
            indicators.append("Symmetric spectral patterns detected — common in GAN-based voice synthesis")

        if not indicators:
            if verdict == "REAL":
                indicators.append("Natural spectral variation consistent with authentic human speech")
            else:
                indicators.append("Multiple subtle spectral anomalies suggest AI-generated speech")

        return indicators


# Singleton
detector_service = DetectorService()
