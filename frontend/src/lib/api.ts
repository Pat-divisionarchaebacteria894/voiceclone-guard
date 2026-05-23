const BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface AnalysisResult {
  id: number;
  filename: string;
  file_size_bytes: number | null;
  duration_seconds: number | null;
  sample_rate: number | null;
  verdict: "REAL" | "FAKE";
  confidence: number;
  confidence_pct: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  spectral_score: number | null;
  transformer_score: number | null;
  features: {
    mfcc_mean: number[];
    spectral_centroid: number;
    spectral_bandwidth: number;
    spectral_rolloff: number;
    spectral_flatness: number;
    zero_crossing_rate: number;
    harmonic_ratio: number;
    pitch_consistency: number;
    tempo: number;
    rms_energy: number;
  } | null;
  spectrogram_url: string | null;
  detection_method: string | null;
  created_at: string;
  indicators: string[];
}

export interface HistoryItem {
  id: number;
  filename: string;
  duration_seconds: number | null;
  verdict: "REAL" | "FAKE";
  confidence_pct: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  detection_method: string | null;
  created_at: string;
}

export interface HistoryResponse {
  total: number;
  items: HistoryItem[];
}

export interface HealthResponse {
  status: string;
  version: string;
  models_loaded: Record<string, boolean>;
  uptime_seconds: number;
}

export async function analyzeAudio(file: File): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/api/analyze`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

export async function fetchHistory(page = 1, pageSize = 20, verdict?: string): Promise<HistoryResponse> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (verdict) params.set("verdict", verdict);
  const res = await fetch(`${BASE}/api/history?${params}`);
  if (!res.ok) throw new Error("Failed to load history");
  return res.json();
}

export async function fetchAnalysis(id: number): Promise<AnalysisResult> {
  const res = await fetch(`${BASE}/api/history/${id}`);
  if (!res.ok) throw new Error("Not found");
  return res.json();
}

export async function deleteAnalysis(id: number): Promise<void> {
  const res = await fetch(`${BASE}/api/history/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE}/api/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}
