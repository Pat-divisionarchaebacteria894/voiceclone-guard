"use client";

import { useEffect, useState, useCallback } from "react";
import clsx from "clsx";
import { Trash2, RefreshCw, ChevronLeft, ChevronRight } from "lucide-react";
import { fetchHistory, deleteAnalysis, type HistoryItem } from "@/lib/api";

export default function HistoryPanel() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [verdictFilter, setVerdictFilter] = useState<"" | "REAL" | "FAKE">("");

  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHistory(page, PAGE_SIZE, verdictFilter || undefined);
      setItems(data.items);
      setTotal(data.total);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [page, verdictFilter]);

  useEffect(() => { load(); }, [load]);

  async function handleDelete(id: number) {
    if (!confirm("Delete this analysis record?")) return;
    try {
      await deleteAnalysis(id);
      load();
    } catch {}
  }

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Controls */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex gap-1 bg-surface-900 border border-surface-700 rounded-lg p-1">
          {(["", "REAL", "FAKE"] as const).map((v) => (
            <button
              key={v}
              onClick={() => { setVerdictFilter(v); setPage(1); }}
              className={clsx(
                "px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                verdictFilter === v
                  ? "bg-brand-600 text-white"
                  : "text-slate-400 hover:text-white"
              )}
            >
              {v || "All"}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span>{total} records</span>
          <button onClick={load} className="btn-ghost p-1.5" title="Refresh">
            <RefreshCw className={clsx("w-4 h-4", loading && "animate-spin")} />
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl p-4 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="card p-12 flex items-center justify-center">
          <RefreshCw className="w-6 h-6 text-brand-400 animate-spin" />
        </div>
      ) : items.length === 0 ? (
        <div className="card p-12 text-center text-slate-500">
          <p className="text-4xl mb-3">📂</p>
          <p className="font-medium text-slate-400">No analyses yet</p>
          <p className="text-sm mt-1">Upload or record audio to get started</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-700 text-slate-400 text-xs uppercase tracking-wide">
                  <th className="px-4 py-3 text-left">#</th>
                  <th className="px-4 py-3 text-left">File</th>
                  <th className="px-4 py-3 text-left">Duration</th>
                  <th className="px-4 py-3 text-left">Verdict</th>
                  <th className="px-4 py-3 text-left">Confidence</th>
                  <th className="px-4 py-3 text-left">Risk</th>
                  <th className="px-4 py-3 text-left">Method</th>
                  <th className="px-4 py-3 text-left">Date</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody>
                {items.map((item, i) => (
                  <tr
                    key={item.id}
                    className="border-b border-surface-800 hover:bg-surface-800/50 transition-colors"
                  >
                    <td className="px-4 py-3 text-slate-500 font-mono text-xs">{item.id}</td>
                    <td className="px-4 py-3 text-white max-w-[160px]">
                      <span className="truncate block" title={item.filename}>{item.filename}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono">
                      {item.duration_seconds ? `${item.duration_seconds.toFixed(1)}s` : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <span className={item.verdict === "REAL" ? "badge-real" : "badge-fake"}>
                        {item.verdict}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-surface-700 rounded-full h-1.5">
                          <div
                            className={clsx("h-full rounded-full", item.verdict === "REAL" ? "bg-emerald-500" : "bg-red-500")}
                            style={{ width: `${item.confidence_pct}%` }}
                          />
                        </div>
                        <span className="text-slate-300 font-mono text-xs w-12">
                          {item.confidence_pct.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={clsx(
                        "px-2 py-0.5 rounded-full text-xs font-medium border",
                        item.risk_level === "HIGH"   ? "badge-risk-high" :
                        item.risk_level === "MEDIUM" ? "badge-risk-medium" :
                                                       "badge-risk-low"
                      )}>
                        {item.risk_level}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{item.detection_method || "—"}</td>
                    <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="text-slate-600 hover:text-red-400 transition-colors p-1"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="border-t border-surface-700 px-4 py-3 flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Page {page} of {totalPages}
              </span>
              <div className="flex gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="btn-ghost p-1.5 disabled:opacity-40"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="btn-ghost p-1.5 disabled:opacity-40"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
