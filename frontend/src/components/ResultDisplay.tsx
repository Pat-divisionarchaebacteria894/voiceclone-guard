"use client";

import clsx from "clsx";
import { CheckCircle, XCircle, AlertTriangle, Cpu, BarChart3, Clock, Volume2, Info } from "lucide-react";
import type { AnalysisResult } from "@/lib/api";

interface Props {
  result: AnalysisResult;
}

export default function ResultDisplay({ result }: Props) {
  const isFake = result.verdict === "FAKE";
  const BASE = process.env.NEXT_PUBLIC_API_URL || "";

  return (
    <div className="space-y-4 animate-slide-up">
      {/* Main verdict card */}
      <div
        className={clsx(
          "card p-6 border-2",
          isFake
            ? "border-red-500/40 bg-red-950/20"
            : "border-emerald-500/40 bg-emerald-950/20"
        )}
      >
        <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
          {/* Icon + verdict */}
          <div className="flex items-center gap-4">
            <div
              className={clsx(
                "w-16 h-16 rounded-2xl flex items-center justify-center flex-shrink-0",
                isFake ? "bg-red-500/20" : "bg-emerald-500/20"
              )}
            >
              {isFake
                ? <XCircle className="w-9 h-9 text-red-400" />
                : <CheckCircle className="w-9 h-9 text-emerald-400" />}
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-1">Verdict</p>
              <p
                className={clsx(
                  "text-3xl font-bold",
                  isFake ? "text-red-400" : "text-emerald-400"
                )}
              >
                {isFake ? "DEEPFAKE DETECTED" : "AUTHENTIC VOICE"}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className={clsx("px-2 py-0.5 rounded-full text-xs font-medium border",
                  result.risk_level === "HIGH"   ? "badge-risk-high" :
                  result.risk_level === "MEDIUM" ? "badge-risk-medium" :
                                                   "badge-risk-low"
                )}>
                  {result.risk_level} RISK
                </span>
                <span className="text-slate-400 text-sm">via {result.detection_method}</span>
              </div>
            </div>
          </div>

          {/* Confidence meter */}
          <div className="flex-1 w-full">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-400">Confidence</span>
              <span className={clsx("font-bold text-lg", isFake ? "text-red-400" : "text-emerald-400")}>
                {result.confidence_pct.toFixed(1)}%
              </span>
            </div>
            <div className="progress-bar">
              <div
                className={isFake ? "progress-fill-fake" : "progress-fill-real"}
                style={{ width: `${result.confidence_pct}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Real</span>
              <span>Fake</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Sub-scores */}
        <div className="card p-5 space-y-4">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-brand-400" /> Detection Scores
          </h3>

          <ScoreRow
            label="Spectral Analysis"
            score={result.spectral_score}
            description="Based on spectral features, MFCC, pitch, and harmonic analysis"
          />
          {result.transformer_score !== null && (
            <ScoreRow
              label="Transformer Model"
              score={result.transformer_score}
              description="HuggingFace audio classification model"
            />
          )}
        </div>

        {/* File info */}
        <div className="card p-5 space-y-3">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-brand-400" /> Audio Details
          </h3>
          <InfoRow icon={<Clock className="w-3.5 h-3.5" />} label="Duration"
            value={result.duration_seconds ? `${result.duration_seconds.toFixed(2)}s` : "—"} />
          <InfoRow icon={<Cpu className="w-3.5 h-3.5" />} label="Sample Rate"
            value={result.sample_rate ? `${(result.sample_rate / 1000).toFixed(1)} kHz` : "—"} />
          <InfoRow label="File" value={result.filename} truncate />
          {result.features && (
            <>
              <InfoRow label="Spectral Centroid"
                value={`${result.features.spectral_centroid.toFixed(0)} Hz`} />
              <InfoRow label="Spectral Flatness"
                value={result.features.spectral_flatness.toFixed(4)} />
              <InfoRow label="Pitch Consistency"
                value={`${(result.features.pitch_consistency * 100).toFixed(1)}%`} />
              <InfoRow label="Harmonic Ratio"
                value={`${(result.features.harmonic_ratio * 100).toFixed(1)}%`} />
            </>
          )}
        </div>
      </div>

      {/* Indicators */}
      {result.indicators.length > 0 && (
        <div className="card p-5 space-y-3">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <Info className="w-4 h-4 text-brand-400" /> Analysis Indicators
          </h3>
          <ul className="space-y-2">
            {result.indicators.map((ind, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
                <span className={clsx("mt-0.5 flex-shrink-0 w-4 h-4 rounded-full flex items-center justify-center text-xs",
                  isFake ? "bg-red-500/20 text-red-400" : "bg-emerald-500/20 text-emerald-400"
                )}>
                  {isFake ? "!" : "✓"}
                </span>
                {ind}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Spectrogram */}
      {result.spectrogram_url && (
        <div className="card p-5 space-y-3">
          <h3 className="font-semibold text-white flex items-center gap-2">
            📊 Spectrogram
          </h3>
          <img
            src={`${BASE}${result.spectrogram_url}`}
            alt="Audio spectrogram"
            className="w-full rounded-xl border border-surface-700"
          />
          <p className="text-xs text-slate-500">
            Top: Mel spectrogram (frequency content over time). Bottom: Waveform.
            Unusual uniformity or artifacts may indicate synthetic speech.
          </p>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-4 flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-yellow-300/80">
          This tool uses acoustic analysis and is not 100% accurate. Results should be used
          as one signal among others. High-quality deepfakes may evade detection. For critical
          decisions, combine with other verification methods.
        </p>
      </div>
    </div>
  );
}

function ScoreRow({ label, score, description }: {
  label: string; score: number | null; description: string;
}) {
  if (score === null) return null;
  const pct = Math.round(score * 100);
  const color = pct >= 60 ? "bg-red-500" : pct >= 40 ? "bg-yellow-500" : "bg-emerald-500";

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className={clsx("font-mono font-semibold", pct >= 60 ? "text-red-400" : "text-emerald-400")}>
          {pct}% fake
        </span>
      </div>
      <div className="progress-bar h-2">
        <div className={clsx("h-full rounded-full transition-all duration-700", color)}
          style={{ width: `${pct}%` }} />
      </div>
      <p className="text-xs text-slate-500">{description}</p>
    </div>
  );
}

function InfoRow({ icon, label, value, truncate }: {
  icon?: React.ReactNode; label: string; value: string; truncate?: boolean;
}) {
  return (
    <div className="flex justify-between gap-2 text-sm">
      <span className="text-slate-400 flex items-center gap-1 flex-shrink-0">
        {icon} {label}
      </span>
      <span className={clsx("text-white font-mono text-right", truncate && "truncate max-w-[180px]")}>
        {value}
      </span>
    </div>
  );
}
