"""
Spectral-analysis deepfake detector.

This module performs voice authenticity analysis using acoustic features derived
from research on TTS / voice-cloning artefacts.  No external model downloads
are required — it runs entirely on librosa.

Key signals exploited
─────────────────────
1. Spectral flatness  — AI voices tend to be "too clean"; natural speech has
   irregular spectral energy.

2. MFCC variance      — Synthetic voices show reduced variance in MFCC
   coefficients because generation is deterministic / over-smoothed.

3. Pitch consistency  — Real voices have micro-fluctuations (jitter / shimmer).
   Neural TTS often produces suspiciously regular pitch.

4. Harmonic-to-noise  — HNR drop can indicate vocoder artifacts common in
   WaveNet / HiFi-GAN vocoders.

5. Spectral flux      — Rapid spectral change between frames.  AI speech
   sometimes exhibits too-smooth or too-abrupt transitions.

6. High-freq energy   — Some vocoders struggle above 6 kHz, leaving gaps or
   introducing periodic noise patterns.

7. Noise floor        — Real recordings have ambient room noise; some TTS
   outputs are perfectly silent outside voiced segments.
"""

import logging
from typing import Any, Dict, Tuple

import librosa
import numpy as np
from scipy.stats import kurtosis, skew

logger = logging.getLogger(__name__)

# ── Empirical thresholds (derived from ASVspoof 2019/2021 literature) ─────────
_FLATNESS_FAKE_THRESH   = 0.18   # above → likely fake
_MFCC_VAR_FAKE_THRESH   = 2.8    # below → likely fake  (mean std of MFCCs 1-13)
_PITCH_SMOOTH_THRESH    = 0.55   # above → suspiciously smooth
_HNR_FAKE_THRESH        = 8.0    # below → possible vocoder artefact
_NOISE_FLOOR_THRESH     = 0.004  # silence ratio threshold


class SpectralDetector:
    """Stateless spectral analysis detector."""

    # ── Public interface ──────────────────────────────────────────────────────

    def analyze(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Returns:
            {
              "fake_probability": float,   # 0.0 → definitely real, 1.0 → definitely fake
              "features": dict,
              "flags": dict,               # boolean indicators
            }
        """
        # Ensure float32 and non-empty
        audio = np.asarray(audio, dtype=np.float32)
        if len(audio) == 0:
            raise ValueError("Audio array is empty")

        # Peak-normalise (guard against silent audio producing NaN features)
        peak = float(np.abs(audio).max())
        if peak < 1e-6:
            # Silent audio — return a neutral mid-range score, not a hard fake
            return {
                "fake_probability": 0.5,
                "features": self._empty_features(),
                "flags": {},
            }
        audio = audio / peak

        feats = self._extract_features(audio, sr)
        fake_prob, flags = self._score(feats, audio, sr)

        return {
            "fake_probability": float(np.clip(fake_prob, 0.0, 1.0)),
            "features": feats,
            "flags": flags,
        }

    # ── Feature extraction ────────────────────────────────────────────────────

    def _extract_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        # ── MFCC ──────────────────────────────────────────────────────────────
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        mfcc_mean = mfcc.mean(axis=1).tolist()
        mfcc_std  = float(mfcc[1:13].std(axis=1).mean())   # var of cepstral coeffs 1-13

        # ── Spectral features ─────────────────────────────────────────────────
        centroid   = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        bandwidth  = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
        rolloff    = librosa.feature.spectral_rolloff(y=audio, sr=sr, roll_percent=0.85)[0]
        flatness   = librosa.feature.spectral_flatness(y=audio)[0]
        zcr        = librosa.feature.zero_crossing_rate(audio)[0]

        # Spectral flux (frame-to-frame change)
        stft       = np.abs(librosa.stft(audio))
        flux       = np.sqrt(np.sum(np.diff(stft, axis=1) ** 2, axis=0))

        # ── Pitch (F0) ────────────────────────────────────────────────────────
        # pyin requires at least ~0.1s of audio; guard against very short clips
        pitch_std = pitch_mean = pitch_cv = jitter = 0.0
        if len(audio) > sr * 0.1:
            try:
                f0, voiced_flag, _ = librosa.pyin(
                    audio, sr=sr,
                    fmin=float(librosa.note_to_hz("C2")),
                    fmax=float(librosa.note_to_hz("C7")),
                )
                # voiced_flag is a boolean array; f0 contains NaN for unvoiced frames
                if f0 is not None and voiced_flag is not None:
                    # Use boolean indexing directly instead of comparing to 1
                    voiced_f0 = f0[voiced_flag.astype(bool)]
                    # Drop any NaN values that slipped through
                    voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]
                    if len(voiced_f0) > 4:
                        pitch_std  = float(np.std(voiced_f0))
                        pitch_mean = float(np.mean(voiced_f0))
                        pitch_cv   = pitch_std / (pitch_mean + 1e-9)
                        jitter     = float(np.mean(np.abs(np.diff(voiced_f0))))
            except Exception as e:
                logger.debug("pyin failed (audio may be too short/silent): %s", e)

        # ── Harmonic-to-noise ratio (proxy via harmonic vs residual energy) ───
        harmonic, percussive = librosa.effects.hpss(audio)
        residual  = audio - harmonic - percussive
        h_energy  = float(np.mean(harmonic ** 2) + 1e-12)
        r_energy  = float(np.mean(residual ** 2) + 1e-12)
        hnr_db    = float(10 * np.log10(h_energy / r_energy))

        # ── High-frequency energy ratio (>6 kHz) ─────────────────────────────
        fft_mag    = np.abs(np.fft.rfft(audio))
        freqs      = np.fft.rfftfreq(len(audio), d=1.0 / sr)
        hf_ratio   = float(fft_mag[freqs > 6000].sum() / (fft_mag.sum() + 1e-12))

        # ── Silence / noise floor ─────────────────────────────────────────────
        rms        = librosa.feature.rms(y=audio)[0]
        silence_ratio = float((rms < _NOISE_FLOOR_THRESH).mean())

        # ── Tempo ─────────────────────────────────────────────────────────────
        tempo, _   = librosa.beat.beat_track(y=audio, sr=sr)
        tempo      = float(tempo) if np.isscalar(tempo) else float(tempo[0]) if len(tempo) else 0.0

        # ── Statistical texture ───────────────────────────────────────────────
        mfcc_kurtosis = float(kurtosis(mfcc[1:].flatten()))
        mfcc_skew     = float(skew(mfcc[1:].flatten()))

        return {
            "mfcc_mean":           mfcc_mean,
            "mfcc_std":            mfcc_std,
            "mfcc_kurtosis":       mfcc_kurtosis,
            "mfcc_skew":           mfcc_skew,
            "spectral_centroid":   float(centroid.mean()),
            "spectral_bandwidth":  float(bandwidth.mean()),
            "spectral_rolloff":    float(rolloff.mean()),
            "spectral_flatness":   float(flatness.mean()),
            "zero_crossing_rate":  float(zcr.mean()),
            "spectral_flux_mean":  float(flux.mean()),
            "spectral_flux_std":   float(flux.std()),
            "pitch_mean":          pitch_mean,
            "pitch_std":           pitch_std,
            "pitch_cv":            float(pitch_cv),
            "jitter":              jitter,
            "harmonic_ratio":      float(np.clip(hnr_db / 40.0, 0.0, 1.0)),
            "hnr_db":              hnr_db,
            "hf_energy_ratio":     hf_ratio,
            "silence_ratio":       silence_ratio,
            "pitch_consistency":   float(np.clip(1.0 - pitch_cv * 5, 0.0, 1.0)),
            "tempo":               tempo,
            "rms_energy":          float(rms.mean()),
        }

    # ── Scoring ───────────────────────────────────────────────────────────────

    def _score(self, feats: Dict[str, Any], audio: np.ndarray, sr: int) -> Tuple[float, Dict[str, bool]]:
        """
        Combines multiple heuristic signals into a single fake_probability.

        Each signal is normalised to [0, 1] where 1 = strong evidence of fakery.
        Weights are based on empirical effectiveness from anti-spoofing literature.
        """
        evidence = {}
        flags    = {}

        # 1. Spectral flatness
        sf_val   = feats["spectral_flatness"]
        sf_score = float(np.clip((sf_val - 0.08) / 0.22, 0.0, 1.0))
        evidence["flatness"] = (sf_score, 0.22)
        flags["high_spectral_flatness"] = sf_val > _FLATNESS_FAKE_THRESH

        # 2. MFCC variance — low variance → fake
        mv_val   = feats["mfcc_std"]
        mv_score = float(np.clip(1.0 - (mv_val - 1.0) / 6.0, 0.0, 1.0))
        evidence["mfcc_variance"] = (mv_score, 0.20)
        flags["low_mfcc_variance"] = mv_val < _MFCC_VAR_FAKE_THRESH

        # 3. Pitch smoothness — too regular → fake
        pc_val   = feats["pitch_cv"]
        pc_score = float(np.clip(1.0 - pc_val / 0.25, 0.0, 1.0))
        evidence["pitch_smooth"] = (pc_score, 0.18)
        flags["smooth_pitch"] = pc_val < (1.0 - _PITCH_SMOOTH_THRESH) * 0.25

        # 4. Harmonic-to-noise ratio — too low OR suspiciously high
        hnr      = feats["hnr_db"]
        if hnr < _HNR_FAKE_THRESH:
            hnr_score = float(np.clip((_HNR_FAKE_THRESH - hnr) / 15.0, 0.0, 1.0))
        elif hnr > 35.0:
            hnr_score = float(np.clip((hnr - 35.0) / 20.0, 0.0, 1.0))
        else:
            hnr_score = 0.0
        evidence["hnr"] = (hnr_score, 0.15)
        flags["low_hnr"] = hnr < _HNR_FAKE_THRESH

        # 5. Silence / noise floor — too clean → fake
        sr_val   = feats["silence_ratio"]
        sr_score = float(np.clip((sr_val - 0.10) / 0.40, 0.0, 1.0))
        evidence["noise_floor"] = (sr_score, 0.12)
        flags["missing_noise_floor"] = sr_val > 0.35

        # 6. Spectral flux variance — too uniform → fake
        flux_std = feats["spectral_flux_std"]
        fx_score = float(np.clip(1.0 - flux_std / 8.0, 0.0, 1.0))
        evidence["flux"] = (fx_score, 0.08)

        # 7. High-frequency energy — vocoders often leave telltale HF patterns
        hf_val   = feats["hf_energy_ratio"]
        hf_score = float(np.clip(abs(hf_val - 0.035) / 0.06, 0.0, 1.0))
        evidence["hf_energy"] = (hf_score, 0.05)
        flags["high_spectral_symmetry"] = hf_score > 0.65

        # ── Weighted sum ──────────────────────────────────────────────────────
        total_weight = sum(w for _, w in evidence.values())
        fake_prob = sum(s * w for s, w in evidence.values()) / total_weight

        # ── Sigmoid sharpening (push scores away from 0.5) ────────────────────
        # Maps 0→0, 0.5→0.5, 1→1 but increases contrast around mid-range
        fake_prob = float(1.0 / (1.0 + np.exp(-8.0 * (fake_prob - 0.50))))

        logger.debug("Evidence: %s  →  fake_prob=%.3f", evidence, fake_prob)
        return fake_prob, flags

    @staticmethod
    def _empty_features() -> Dict[str, Any]:
        """Return zero-valued features for silent audio."""
        return {
            "mfcc_mean": [0.0] * 20,
            "mfcc_std": 0.0,
            "mfcc_kurtosis": 0.0,
            "mfcc_skew": 0.0,
            "spectral_centroid": 0.0,
            "spectral_bandwidth": 0.0,
            "spectral_rolloff": 0.0,
            "spectral_flatness": 0.0,
            "zero_crossing_rate": 0.0,
            "spectral_flux_mean": 0.0,
            "spectral_flux_std": 0.0,
            "pitch_mean": 0.0,
            "pitch_std": 0.0,
            "pitch_cv": 0.0,
            "jitter": 0.0,
            "harmonic_ratio": 0.0,
            "hnr_db": 0.0,
            "hf_energy_ratio": 0.0,
            "silence_ratio": 1.0,
            "pitch_consistency": 0.0,
            "tempo": 0.0,
            "rms_energy": 0.0,
        }
