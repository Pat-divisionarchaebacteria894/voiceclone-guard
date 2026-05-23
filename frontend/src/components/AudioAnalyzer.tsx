"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Upload, Mic, MicOff, X, FileAudio, Loader2 } from "lucide-react";
import clsx from "clsx";
import { analyzeAudio, type AnalysisResult } from "@/lib/api";
import ResultDisplay from "./ResultDisplay";

interface Props {
  onResult: (r: AnalysisResult) => void;
}

type Mode = "idle" | "recording" | "recorded" | "analyzing" | "done" | "error";

export default function AudioAnalyzer({ onResult }: Props) {
  const [mode, setMode] = useState<Mode>("idle");
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioURL, setAudioURL] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // ── File selection ────────────────────────────────────────────────────────

  const handleFile = useCallback((file: File) => {
    const allowed = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg",
                     "audio/flac", "audio/webm", "audio/opus", "audio/x-m4a"];
    const ext = file.name.split(".").pop()?.toLowerCase();
    const allowedExts = ["wav","mp3","m4a","ogg","flac","webm","opus"];

    if (!allowed.includes(file.type) && !allowedExts.includes(ext || "")) {
      setError("Unsupported file type. Please upload WAV, MP3, M4A, OGG, FLAC, WEBM, or OPUS.");
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setError("File exceeds 25 MB limit.");
      return;
    }

    const url = URL.createObjectURL(file);
    setAudioURL(url);
    setSelectedFile(file);
    setError(null);
    setMode("recorded");
  }, []);

  // ── Drag & drop ───────────────────────────────────────────────────────────

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  // ── Microphone recording ──────────────────────────────────────────────────

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      const mr = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mr;

      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mr.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: mimeType });
        const file = new File([blob], `recording_${Date.now()}.webm`, { type: mimeType });
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
        setSelectedFile(file);
        setMode("recorded");
      };

      mr.start(200);
      setMode("recording");
      setRecordingTime(0);
      timerRef.current = setInterval(() => setRecordingTime((t) => t + 1), 1000);
    } catch (e) {
      setError("Microphone access denied. Please allow microphone permission.");
    }
  }

  function stopRecording() {
    if (timerRef.current) clearInterval(timerRef.current);
    mediaRecorderRef.current?.stop();
  }

  // ── Cleanup ───────────────────────────────────────────────────────────────

  useEffect(() => () => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (audioURL) URL.revokeObjectURL(audioURL);
  }, []);

  // ── Analysis ──────────────────────────────────────────────────────────────

  async function runAnalysis() {
    if (!selectedFile) return;
    setMode("analyzing");
    setError(null);
    try {
      const r = await analyzeAudio(selectedFile);
      setResult(r);
      onResult(r);
      setMode("done");
    } catch (e: any) {
      setError(e.message || "Analysis failed");
      setMode("error");
    }
  }

  function reset() {
    if (audioURL) URL.revokeObjectURL(audioURL);
    setMode("idle");
    setSelectedFile(null);
    setResult(null);
    setError(null);
    setAudioURL(null);
    setRecordingTime(0);
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6 animate-fade-in">
      {mode === "done" && result ? (
        <div className="space-y-4 animate-slide-up">
          <ResultDisplay result={result} />
          <div className="flex justify-center">
            <button onClick={reset} className="btn-ghost flex items-center gap-2 text-sm">
              <X className="w-4 h-4" /> Analyze another file
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Upload / Record cards */}
          {(mode === "idle" || mode === "error") && (
            <div className="grid md:grid-cols-2 gap-4">
              {/* Upload */}
              <div
                className={clsx("drop-zone", dragOver && "drag-over")}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="w-14 h-14 rounded-2xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center">
                  <Upload className="w-7 h-7 text-brand-400" />
                </div>
                <div>
                  <p className="font-semibold text-white">Upload Audio File</p>
                  <p className="text-slate-400 text-sm mt-1">
                    Drag &amp; drop or click to browse
                  </p>
                  <p className="text-slate-500 text-xs mt-1">
                    WAV · MP3 · M4A · OGG · FLAC · WEBM — max 25 MB
                  </p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="audio/*"
                  className="hidden"
                  onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                />
              </div>

              {/* Record */}
              <div
                className="drop-zone cursor-pointer select-none"
                onClick={startRecording}
              >
                <div className="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                  <Mic className="w-7 h-7 text-red-400" />
                </div>
                <div>
                  <p className="font-semibold text-white">Record from Microphone</p>
                  <p className="text-slate-400 text-sm mt-1">
                    Click to start recording
                  </p>
                  <p className="text-slate-500 text-xs mt-1">
                    Speak naturally for at least 3 seconds
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Recording in progress */}
          {mode === "recording" && (
            <div className="card p-8 flex flex-col items-center gap-6">
              <div className="relative">
                <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center">
                  <Mic className="w-10 h-10 text-red-400" />
                </div>
                <span className="absolute inset-0 rounded-full bg-red-500/20 animate-ping" />
              </div>
              <div className="text-center">
                <p className="font-semibold text-white text-lg">Recording…</p>
                <p className="text-slate-400 font-mono mt-1">{formatTime(recordingTime)}</p>
              </div>
              <button
                onClick={stopRecording}
                className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-xl transition-colors font-medium"
              >
                <MicOff className="w-5 h-5" /> Stop Recording
              </button>
            </div>
          )}

          {/* File ready */}
          {mode === "recorded" && selectedFile && (
            <div className="card p-6 space-y-4 animate-slide-up">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-brand-500/10 flex items-center justify-center flex-shrink-0">
                  <FileAudio className="w-5 h-5 text-brand-400" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-white truncate">{selectedFile.name}</p>
                  <p className="text-sm text-slate-400">{formatBytes(selectedFile.size)}</p>
                </div>
                <button onClick={reset} className="text-slate-500 hover:text-white transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {audioURL && (
                <audio controls src={audioURL} className="w-full h-10 rounded-lg" />
              )}

              <button onClick={runAnalysis} className="btn-primary w-full flex items-center justify-center gap-2">
                🔍 Analyze for Deepfake
              </button>
            </div>
          )}

          {/* Analyzing */}
          {mode === "analyzing" && (
            <div className="card p-12 flex flex-col items-center gap-6 animate-fade-in">
              <div className="relative w-20 h-20">
                <div className="absolute inset-0 rounded-full border-4 border-surface-700" />
                <div className="absolute inset-0 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 text-brand-400 animate-spin" />
                </div>
              </div>
              <div className="text-center">
                <p className="font-semibold text-white text-lg">Analyzing audio…</p>
                <p className="text-slate-400 text-sm mt-1">
                  Running spectral analysis &amp; deepfake detection
                </p>
              </div>
              <div className="flex gap-2 text-xs text-slate-500">
                {["Preprocessing", "Feature extraction", "Classification"].map((step, i) => (
                  <span key={step} className="flex items-center gap-1">
                    {i > 0 && <span className="text-surface-600">›</span>}
                    <span className="animate-pulse" style={{ animationDelay: `${i * 0.3}s` }}>
                      {step}
                    </span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-start gap-3">
              <span className="text-red-400 text-lg">⚠</span>
              <div>
                <p className="text-red-400 font-medium">Error</p>
                <p className="text-red-300/80 text-sm mt-0.5">{error}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function formatTime(sec: number) {
  const m = Math.floor(sec / 60).toString().padStart(2, "0");
  const s = (sec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
