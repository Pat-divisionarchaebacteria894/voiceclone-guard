<div align="center">

# 🛡️ VoiceClone Guard

### Free, Open-Source Voice Deepfake Detector

**Upload or record any audio. Know in seconds if it's a real human — or an AI clone.**

[![License: MIT](https://img.shields.io/badge/License-MIT-6366f1.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-3b82f6.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com)
[![No API Key Needed](https://img.shields.io/badge/API%20Key-None%20Required-22c55e.svg)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)

<br/>

![VoiceClone Guard Demo](https://raw.githubusercontent.com/manasmourya/voiceclone-guard/main/docs/demo.png)

</div>

---

## 👋 Hey, I'm Manas — here's why I built this

I've been watching the AI voice cloning space explode over the last couple of years. Tools like ElevenLabs, Voicebox, and VALL-E can now clone someone's voice from just a few seconds of audio. That's genuinely impressive technology — but it also scares me.

Think about it: a scammer could clone your parent's voice and call you in an "emergency." A politician's speech could be fabricated. A job interview could be faked. Voice has always been one of the last things we trusted as *real* — and that trust is eroding fast.

I looked around for a tool that ordinary people could use to check if an audio clip is real or AI-generated. Everything I found was either:
- Behind a paid API
- Locked inside some company's platform
- Too technical for non-developers to use
- Or just didn't work well

So I decided to build one myself. Completely free. No account. No API key. Just upload audio and get an answer.

This is that tool.

---

## 🤔 What problem does this actually solve?

Voice deepfakes are getting used in real attacks right now:

- **Vishing (voice phishing)**: Scammers clone CEO voices to trick employees into wire transfers. This has already cost companies millions.
- **Fake evidence**: Audio recordings used as "proof" in disputes that never happened.
- **Misinformation**: Politicians, celebrities, and public figures being put in audio they never recorded.
- **Personal harm**: People receiving calls that sound like distressed family members asking for money.

VoiceClone Guard gives *anyone* — journalists, security researchers, worried families, HR teams, legal professionals — a way to get a second opinion on whether audio is genuine.

---

## 🧠 How does the detection work? (explained simply)

> Don't worry if you don't know any machine learning. I'll explain it like you're hearing it for the first time.

Real human voices are *messy* in a beautiful way. When you speak, your pitch wobbles slightly (called **jitter**), your voice has natural background noise, the energy isn't perfectly distributed across frequencies, and tiny imperfections exist in every syllable.

AI-generated voices are trying to *sound* human but they're actually created mathematically. No matter how good they get, they leave traces:

- **Too smooth** — The pitch doesn't wobble naturally. It's suspiciously regular.
- **Too clean** — Real speech always has a noise floor (room acoustics, breathing, mic noise). AI voices are often too quiet between words.
- **Flat spectrum** — The distribution of sound energy across frequencies is more uniform than a real voice, kind of like how a synthesizer sounds different from a real guitar even when playing the same note.
- **Harmonic artifacts** — AI vocoders (the part that generates the actual audio waveform) leave detectable patterns in the high-frequency range.

We measure all of these signals, weight them, and produce a score. The higher the score, the more the audio looks like it came from a machine.

```
Your audio file
      │
      ▼
┌─────────────────────────────────────────────────┐
│            SPECTRAL ANALYSIS ENGINE              │
│                                                  │
│  ① Pitch consistency check (F0 jitter/shimmer)  │
│  ② MFCC variance test (voice texture)           │
│  ③ Spectral flatness measure                    │
│  ④ Harmonic-to-noise ratio                      │
│  ⑤ Noise floor analysis                         │
│  ⑥ Spectral flux uniformity                     │
│  ⑦ High-frequency artifact scan                 │
│                                                  │
│  [Optional] HuggingFace transformer model       │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
         Weighted ensemble score
                   │
          ┌────────┴────────┐
          ▼                 ▼
       REAL ✅           FAKE ❌
   + confidence %    + confidence %
   + risk level      + risk level
   + indicators      + indicators
   + spectrogram     + spectrogram
```

---

## 🔀 Why this approach? What else could I have done?

This is the part I find most interesting, so let me walk you through the decision.

### Option 1: Use a paid third-party API
Companies like Pindrop, Resemble Detect, and Hiya offer voice deepfake detection as a paid service. The accuracy is high, but you pay per API call, you hand your audio to someone else's servers, and the moment you can't pay, your tool stops working. **I wanted this to be free forever and work offline. So no.**

### Option 2: Train my own neural network from scratch
The research papers on this are incredible. Models like **AASIST** (Audio Anti-Spoofing using Integrated Spectro-Temporal Graph Attention Networks) and **RawNet2** achieve error rates under 1% on benchmark datasets. But training them requires:
- A massive labeled dataset (ASVspoof has 100k+ samples)
- Days of GPU compute time
- Deep ML expertise to tune hyperparameters

I wanted something anyone could clone and run in 5 minutes. **Training a custom model was too heavy for that goal.**

### Option 3: Plug in a pre-trained HuggingFace model
HuggingFace has several community-trained models for audio classification that can detect deepfakes. This is actually supported in VoiceClone Guard as an **optional second signal** — you can turn it on by setting `USE_TRANSFORMER_MODEL=true` in your `.env` file.

The issue: downloading ~400MB of model weights on first run is a bad experience for someone just trying to quickly check an audio file. **So it's optional, not the default.**

### Option 4: Acoustic/spectral heuristics (what we use by default)
This is the approach I settled on. It's based on decades of research in **anti-spoofing** (detecting fake voices in phone banking systems). It uses `librosa`, a well-tested Python audio analysis library, to extract acoustic features and score them.

**Why this won:**
- No downloads. Works immediately after `pip install`.
- Explainable. We can tell you *which* features triggered the score.
- Fast. Analysis takes 1-3 seconds on a CPU.
- Transparent. Every line of detection logic is readable Python.

The tradeoff: it's not as accurate as a neural network on high-quality deepfakes. **But it catches the vast majority of voice cloning tools people actually encounter in the wild.**

The best of both worlds: run the spectral analysis by default, optionally add the transformer model for higher accuracy when you need it.

---

## ✨ Features

- 🎙️ **Upload audio files** (WAV, MP3, M4A, OGG, FLAC, WEBM, OPUS — up to 25MB)
- 🎤 **Record directly from your microphone** — no file needed
- 📊 **Spectrogram visualization** — see exactly what the model sees
- 🔍 **Human-readable indicators** — we explain *why* we flagged something
- 📋 **Analysis history** — all past analyses saved locally, filterable and deletable
- 🔌 **Full REST API** — integrate into any pipeline with OpenAPI docs at `/docs`
- 🤗 **Optional HuggingFace model** — plug in any audio classification model as a second signal
- 🆓 **100% free, forever** — no account, no API key, no rate limits, no phone home

---

## 🚀 Getting Started

### The 2-minute version (Docker)

You need [Docker Desktop](https://docs.docker.com/get-docker/) installed. That's it.

```bash
# 1. Download the project
git clone https://github.com/manasmourya/voiceclone-guard.git
cd voiceclone-guard

# 2. Run the setup script
chmod +x setup.sh
./setup.sh
```

Open your browser at **http://localhost:3000** and you're live.

API documentation is at **http://localhost:8000/docs**.

> 💡 **First time using Docker?** It's a tool that packages the app with everything it needs to run, so you don't have to install Python, Node.js, or any libraries yourself. Think of it like a self-contained box.

---

### The manual version (for developers who prefer it)

If you want to run without Docker — maybe you want to dig into the code or contribute:

**Step 1: Start the backend (Python API)**

```bash
cd backend

# Create an isolated Python environment (keeps your system clean)
python -m venv .venv

# Activate it
source .venv/bin/activate      # Mac / Linux
.venv\Scripts\activate         # Windows

# Install libraries
pip install -r requirements.txt

# Create folders the app needs
mkdir -p data/uploads data/models

# Start the server
uvicorn main:app --reload --port 8000
```

The API is now running at http://localhost:8000.

**Step 2: Start the frontend (Next.js web app)**

Open a new terminal:

```bash
cd frontend

# Install JavaScript dependencies
npm install --legacy-peer-deps

# Tell the frontend where the API is
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the dev server
npm run dev
```

Open http://localhost:3000 in your browser.

---

### Testing it works

```bash
# Quick API smoke test — should return {"status":"ok",...}
curl http://localhost:8000/api/health

# Analyze a WAV file
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@your_audio.wav"
```

---

## 📁 Project Structure — What does each file do?

If you're new to full-stack projects, here's a plain-English tour:

```
voiceclone-guard/
│
│   # 🐳 Docker (how to containerize everything)
├── docker-compose.yml      ← Wires backend + frontend together
├── setup.sh                ← The script that starts everything
├── .env.example            ← Template for your settings
│
├── backend/                ← Python API (the brains)
│   ├── main.py             ← Entry point. Starts the FastAPI web server.
│   ├── requirements.txt    ← List of Python libraries to install
│   ├── Dockerfile          ← How to build the backend container
│   │
│   ├── app/
│   │   ├── config.py       ← All settings (file paths, limits, etc.)
│   │   ├── database.py     ← SQLite database setup (stores analysis history)
│   │   │
│   │   ├── routers/        ← API endpoints (URLs the frontend calls)
│   │   │   ├── analyze.py  ← POST /api/analyze  (the main detection endpoint)
│   │   │   ├── history.py  ← GET  /api/history  (past analysis records)
│   │   │   └── health.py   ← GET  /api/health   (is the server alive?)
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py  ← Data shapes (what the API sends/receives)
│   │   │
│   │   └── services/
│   │       ├── audio_preprocessor.py  ← Loads & normalizes audio files
│   │       └── detector.py            ← Orchestrates detection + spectrogram
│   │
│   └── ml/                 ← The actual deepfake detection logic
│       ├── spectral.py     ← ⭐ Core detector (7 acoustic signals)
│       └── transformer.py  ← Optional HuggingFace model wrapper
│
└── frontend/               ← Next.js web app (what users see)
    └── src/
        ├── app/
        │   ├── layout.tsx  ← Page shell (navbar, fonts, metadata)
        │   ├── page.tsx    ← Main page (tab switcher between Analyze/History)
        │   └── globals.css ← Global styles + Tailwind CSS setup
        │
        ├── components/
        │   ├── NavBar.tsx       ← Top navigation bar
        │   ├── Hero.tsx         ← Headline + feature bullets
        │   ├── AudioAnalyzer.tsx ← Upload + record + trigger analysis
        │   ├── ResultDisplay.tsx ← Shows verdict, scores, spectrogram
        │   └── HistoryPanel.tsx  ← Past analyses table with pagination
        │
        ├── lib/
        │   └── api.ts      ← All fetch() calls to the backend
        │
        └── types/
            └── declarations.d.ts  ← TypeScript type shims for icon library
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and edit as needed:

```env
# ─── How big a file can be uploaded? ───────────────────────────
MAX_FILE_SIZE_MB=25

# ─── Optional: Enable a HuggingFace transformer model ──────────
# Set to true to download and use a second-signal ML model.
# First run downloads ~400 MB of weights. Needs internet.
USE_TRANSFORMER_MODEL=false

# If USE_TRANSFORMER_MODEL=true, pick a model from HuggingFace:
HF_MODEL_ID=MelissaAzoulay/deepfake_voice_detector

# ─── Who can call the API? ──────────────────────────────────────
CORS_ORIGINS=http://localhost:3000
```

---

## 📡 Using the API Programmatically

You don't need the web UI at all. The backend is a full REST API you can call from any language.

**Python example:**
```python
import requests

with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": ("audio.wav", f, "audio/wav")}
    )

result = response.json()
print(f"Verdict: {result['verdict']}")           # "REAL" or "FAKE"
print(f"Confidence: {result['confidence_pct']}%") # e.g. 87.3%
print(f"Risk level: {result['risk_level']}")      # "LOW", "MEDIUM", "HIGH"
print("Indicators:")
for indicator in result['indicators']:
    print(f"  - {indicator}")
```

**JavaScript example:**
```javascript
const form = new FormData();
form.append('file', audioBlob, 'recording.wav');

const res = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  body: form,
});
const result = await res.json();
console.log(result.verdict, result.confidence_pct + '%');
```

**Full API docs** (interactive, try it in browser): http://localhost:8000/docs

---

## 🔬 The 7 Detection Signals Explained

Here's exactly what we're measuring and why it matters for catching fakes:

### 1. Spectral Flatness
Measures how evenly sound energy is spread across frequencies. A real voice has uneven energy (some frequencies are louder, some quieter). AI synthesis tends to produce a more uniform distribution — like white noise vs. speech.

### 2. MFCC Variance (Mel-Frequency Cepstral Coefficients)
MFCCs are essentially a compact fingerprint of how a voice sounds. Real voices have high variance in these coefficients because of natural expressiveness. AI voices are generated deterministically and tend to be "over-smooth" — the fingerprint doesn't change enough.

### 3. Pitch Consistency (Fundamental Frequency)
Your voice pitch wobbles naturally when you speak — this is called **jitter**. Neural TTS systems produce suspiciously regular pitch because they generate it mathematically rather than through a physical vocal tract.

### 4. Harmonic-to-Noise Ratio (HNR)
Real voices have a natural ratio of harmonic (musical) content to noise. Voice cloning tools based on vocoders (like HiFi-GAN, WaveNet) often push this ratio too high or produce specific noise artifacts.

### 5. Noise Floor
Real audio recorded in any environment contains ambient noise — room tone, HVAC, mic hiss. Many TTS systems produce audio that's perfectly silent outside voiced segments. We measure what percentage of frames are below the ambient noise threshold.

### 6. Spectral Flux
How fast does the spectrum change from frame to frame? Real speech has dynamic, rapid changes. Some synthesis methods produce audio that changes too uniformly — no sharp transitions, no natural "pops" and texture.

### 7. High-Frequency Energy
Real microphones and voices produce specific patterns above 6kHz. Certain vocoders fail to model this range correctly and either produce too little energy or characteristic periodic artifacts.

---

## 🧪 Running Your Own Test

Want to see it in action with a quick sanity check?

```bash
# Generate a simple test audio file (Python)
python3 - << 'EOF'
import numpy as np, wave, struct
sr = 16000
t = np.linspace(0, 3, sr * 3)
# Simulate a "fake-like" pure sine wave
audio = np.sin(2 * np.pi * 440 * t) * 0.5
with wave.open('test_fake.wav', 'w') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
    f.writeframes(struct.pack('<' + 'h' * len(audio), *np.int16(audio * 32767)))
print("Created test_fake.wav")
EOF

# Send it to the API
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_fake.wav" | python3 -m json.tool
```

You should see the pure sine wave score high on the fake-probability because it has no natural jitter, perfect spectral uniformity, and no noise floor.

---

## 🤝 How to Contribute

Pull requests are welcome! Here are easy ways to help:

**For developers:**
- Add support for more audio formats
- Improve the spectral scoring thresholds (calibrate against real datasets)
- Add a batch analysis endpoint (analyze many files at once)
- Add WebSocket support for real-time streaming analysis
- Integrate more HuggingFace models

**For non-developers:**
- Test it on voice clips you've collected and open an issue if the verdict seems wrong
- Share it with journalists, legal teams, or security researchers who need it
- Translate the UI (add `i18n` support)
- Write blog posts about how you're using it

**For researchers:**
- Benchmark the spectral detector against ASVspoof 2019/2021 datasets
- Compare it against commercial solutions
- Help calibrate thresholds for specific TTS systems (ElevenLabs, Voicebox, etc.)

---

## 🚧 Known Limitations (be honest about what it can't do)

I want to be upfront about this because it matters:

1. **High-quality deepfakes can fool it.** The best voice cloning systems (especially when trained on hours of the target voice) will produce audio that's harder to detect. The spectral heuristics work well on "off-the-shelf" cloning tools but aren't infallible.

2. **Short clips are harder to analyze.** We need at least 2-3 seconds of audio to get reliable features. Under that, confidence will be low.

3. **Domain mismatch.** The thresholds were tuned on general speech. Very specific environments (phone calls, noisy recordings, heavy compression like Opus at low bitrate) might shift the features in unexpected ways.

4. **It's one signal, not a verdict.** Use this as one piece of evidence alongside context clues, metadata, and common sense — not as a definitive judge.

---

## 📚 Further Reading

If you want to understand the research behind this:

- [ASVspoof 2021 Challenge](https://www.asvspoof.org/) — The benchmark dataset and competition for voice anti-spoofing
- [AASIST Paper](https://arxiv.org/abs/2110.01200) — State-of-the-art anti-spoofing model (the neural net approach we chose not to use as default)
- [RawNet2 Paper](https://arxiv.org/abs/2011.01108) — Another excellent approach that works on raw waveforms
- [Librosa Documentation](https://librosa.org/doc/latest/index.html) — The audio analysis library we use
- [Voice Cloning Risks](https://www.ftc.gov/business-guidance/blog/2023/03/ftcs-voice-cloning-challenge) — FTC's take on the real-world threat landscape

---

## 📄 License

MIT License — use it however you want. Commercial use is fine. Just don't remove the license header.

---

<div align="center">

Built with ☕ and a genuine concern about AI voice cloning by **Manas Mourya**

If this helped you, a ⭐ on the repo goes a long way.

[Report a Bug](https://github.com/manasmourya/voiceclone-guard/issues) · [Request a Feature](https://github.com/manasmourya/voiceclone-guard/issues) · [Discuss](https://github.com/manasmourya/voiceclone-guard/discussions)

</div>
