export default function Hero() {
  return (
    <div className="text-center space-y-4 py-4">
      <div className="inline-flex items-center gap-2 bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-medium px-3 py-1.5 rounded-full">
        <span className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-pulse" />
        Free · Open-source · No sign-up required
      </div>

      <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
        Detect{" "}
        <span className="bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent">
          Voice Deepfakes
        </span>
        <br />
        in Seconds
      </h1>

      <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
        Upload or record any audio clip. Our multi-signal AI analysis instantly
        determines if it&apos;s authentic human speech or AI-generated / voice-cloned audio.
      </p>

      <div className="flex flex-wrap justify-center gap-6 pt-2 text-sm text-slate-500">
        {[
          ["🎵", "WAV · MP3 · M4A · OGG · FLAC"],
          ["⚡", "Results in &lt; 5 seconds"],
          ["🔒", "Audio processed locally"],
          ["📊", "Spectrogram + feature analysis"],
        ].map(([icon, label]) => (
          <span key={label} className="flex items-center gap-1.5">
            <span>{icon}</span>
            <span dangerouslySetInnerHTML={{ __html: label }} />
          </span>
        ))}
      </div>
    </div>
  );
}
