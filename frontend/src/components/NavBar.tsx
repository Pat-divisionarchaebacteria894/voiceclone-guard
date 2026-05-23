"use client";

import { ShieldCheck } from "lucide-react";
import Link from "next/link";

export default function NavBar() {
  return (
    <header className="sticky top-0 z-50 border-b border-surface-800 bg-surface-950/80 backdrop-blur-md">
      <nav className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 font-semibold text-lg">
          <span className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-white" />
          </span>
          <span className="text-white">VoiceClone</span>
          <span className="text-brand-400">Guard</span>
        </Link>

        <div className="flex items-center gap-3">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost text-xs"
          >
            GitHub
          </a>
          <a
            href="/docs"
            target="_blank"
            className="btn-ghost text-xs"
          >
            API Docs
          </a>
        </div>
      </nav>
    </header>
  );
}
