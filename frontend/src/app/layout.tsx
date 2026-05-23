import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VoiceClone Guard — Free Voice Deepfake Detector",
  description:
    "Upload or record audio to instantly detect whether it's real human speech or AI-generated / cloned voice. 100% free, open-source, no API keys required.",
  keywords: ["voice deepfake", "audio deepfake detection", "voice cloning detector", "AI voice detection", "anti-spoofing"],
  openGraph: {
    title: "VoiceClone Guard",
    description: "Free, open-source voice deepfake detection",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-surface-950 text-slate-100">
        {children}
      </body>
    </html>
  );
}
