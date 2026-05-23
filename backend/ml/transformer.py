"""
Optional HuggingFace transformer-based deepfake detector.

Only loaded when USE_TRANSFORMER_MODEL=true and HF_MODEL_ID is set.
Provides a secondary signal that is ensembled with the spectral detector.

Tested models (set HF_MODEL_ID to one of these):
  • MelissaAzoulay/deepfake_voice_detector
  • DunnBC22/wav2vec2-base-voice_deepfake_detection
  • mo-thecreator/voice-deepfake-detection

The detector auto-detects label mapping so it works with any binary
audio-classification model where one label represents 'fake' / 'spoof'.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

_FAKE_LABEL_KEYWORDS = {"fake", "spoof", "synthetic", "ai", "generated", "deepfake", "1"}


class TransformerDetector:
    def __init__(self, model_id: str, cache_dir: Optional[str] = None):
        from transformers import pipeline

        self._pipe = pipeline(
            "audio-classification",
            model=model_id,
            cache_dir=cache_dir,
            device=-1,      # CPU; set to 0 for GPU
        )
        self._fake_label = self._infer_fake_label()
        logger.info("TransformerDetector loaded: %s  fake_label='%s'", model_id, self._fake_label)

    def _infer_fake_label(self) -> Optional[str]:
        """Heuristically identify which label corresponds to 'fake'."""
        try:
            labels = [v for v in self._pipe.model.config.id2label.values()]
            for label in labels:
                if any(kw in label.lower() for kw in _FAKE_LABEL_KEYWORDS):
                    return label
            # Fallback: assume label index 1 is 'fake'
            return self._pipe.model.config.id2label.get(1)
        except Exception:
            return None

    def predict(self, audio: np.ndarray, sr: int) -> float:
        """Return probability of audio being fake/synthetic (0–1)."""
        results = self._pipe(
            {"array": audio.astype(np.float32), "sampling_rate": sr},
            top_k=None,
        )
        if self._fake_label:
            for r in results:
                if r["label"] == self._fake_label:
                    return float(r["score"])
        # Fallback: return highest score
        return float(max(results, key=lambda x: x["score"])["score"])
