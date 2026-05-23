"use client";

import { useState } from "react";
import NavBar from "@/components/NavBar";
import Hero from "@/components/Hero";
import AudioAnalyzer from "@/components/AudioAnalyzer";
import HistoryPanel from "@/components/HistoryPanel";
import type { AnalysisResult } from "@/lib/api";

export default function Home() {
  const [latestResult, setLatestResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<"analyze" | "history">("analyze");
  const [refreshHistory, setRefreshHistory] = useState(0);

  function handleResult(result: AnalysisResult) {
    setLatestResult(result);
    setRefreshHistory((n) => n + 1);
  }

  return (
    <div className="flex flex-col min-h-screen">
      <NavBar />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-8 space-y-8">
        <Hero />

        {/* Tab switcher */}
        <div className="flex gap-1 bg-surface-900 border border-surface-700 rounded-xl p-1 w-fit">
          {(["analyze", "history"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-2 rounded-lg text-sm font-medium capitalize transition-all ${
                activeTab === tab
                  ? "bg-brand-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {tab === "analyze" ? "🎙 Analyze" : "📋 History"}
            </button>
          ))}
        </div>

        {activeTab === "analyze" && (
          <AudioAnalyzer onResult={handleResult} />
        )}

        {activeTab === "history" && (
          <HistoryPanel key={refreshHistory} />
        )}
      </main>

      <footer className="border-t border-surface-800 py-6 text-center text-sm text-slate-500">
        VoiceClone Guard — Free &amp; Open-Source Voice Deepfake Detection &nbsp;·&nbsp;
        <a href="/docs" target="_blank" className="text-brand-400 hover:text-brand-300 transition-colors">
          API Docs
        </a>
      </footer>
    </div>
  );
}
