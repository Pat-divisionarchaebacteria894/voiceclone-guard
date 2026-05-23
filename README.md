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

</div>

---

## 👋 Hey, I'm Manas — here's the honest story behind this

I'm not a researcher. I'm not a big company. I'm someone who got genuinely unsettled watching what AI voice cloning can do — and couldn't find a free tool to fight back against it.

Here's what was going through my head while I was building this:

**The moment it hit me:** I watched a demo where someone cloned a voice from a 10-second clip. Literally 10 seconds. They fed it into ElevenLabs and what came out sounded *exactly* like that person. My first thought was: *if my mom got a phone call that sounded like me in trouble, she'd believe it immediately.* That scared me enough to start building.

**The frustration that pushed me:** Every tool I found was either $0.10/minute to run through some company's API, required an account, or was some academic demo that stopped working three years ago. The people who actually need this — worried parents, journalists checking sources, HR teams vetting interviews, court systems handling audio evidence — they can't afford a subscription or they don't know how to use an API. That's backwards. The threat is free to use, the defense shouldn't cost anything.

**What I was second-guessing while building:** Is acoustic analysis even good enough? Will this give people false confidence? I wrestled with this. I almost stopped. My honest answer: it's not perfect — and I say so clearly in the Limitations section — but *something* is better than nothing. Right now, people have zero tools. Even a 75% accurate free tool changes the game versus 0% accurate and inaccessible.

**What I hope this becomes:** I'd love this to be the starting point for a community. Not a company. Not a product. A shared tool that people improve together. If you're a researcher who knows how to squeeze better accuracy out of this pipeline, please do it. If you're a journalist who found a voice clip and wants to understand what you're looking at, this is for you.

That's why everything is MIT licensed. Take it, fork it, build on it.

---

## 🤔 The problem in plain English

AI voice cloning is being used in real attacks *right now*, today:

- **Scam calls from "your kid"**: You get a call. It sounds exactly like your child saying they've been in an accident and need money immediately. This has happened to hundreds of families.
- **CEO fraud**: Scammers clone a CEO's voice and call the CFO to authorize a wire transfer. This has cost companies millions. It's documented. It's growing.
- **Fake evidence**: Audio recordings used in legal disputes that were never actually recorded — fabricated from scratch using someone's public interviews or social media.
- **Political misinformation**: Politicians "saying" things they never said. Audio of world leaders being faked and spread on social media before anyone can verify.

VoiceClone Guard gives *anyone* a way to get a second opinion. Journalists. Security researchers. Lawyers. Families. HR teams. People who just feel something is off about an audio clip.

---

## 🧠 How does the detection work? (no ML knowledge required)

Real human voices are *messy* in a beautiful way. When you speak, your pitch wobbles slightly (called **jitter**). There's natural background noise in any room you record in. The energy isn't perfectly spread across frequencies. And tiny organic imperfections exist in every single syllable.

AI-generated voices are trying to *imitate* human speech but they're generated mathematically. No matter how good they get, they leave traces. Here's how to think about it:

- **Too smooth**: The pitch doesn't wobble the way a real voice does. It's suspiciously regular — like a metronome vs. a human drummer.
- **Too clean**: Real recordings always have ambient noise (room tone, HVAC hum, mic hiss). AI audio is often completely silent between words in a way that just doesn't happen in the real world.
- **Flat spectrum**: Real speech has uneven energy distribution across frequencies — some are much louder than others depending on the vowel, consonant, or tone. AI synthesis tends to flatten this out.
- **Vocoder artifacts**: The part of a voice cloning system that generates the final audio waveform (called a vocoder) leaves fingerprints in the high-frequency range that real microphones don't produce.

VoiceClone Guard measures 7 of these signals, weights them, and produces a single score.

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
   + plain-English   + plain-English
     indicators        indicators
   + spectrogram     + spectrogram
```

---

## 🔀 Why this approach? What else could I have done?

This is the decision I spent the most time on. Let me walk you through every option I considered.

### Option 1: Use a paid third-party API
Companies like Pindrop, Resemble Detect, and Hiya offer voice deepfake detection as a paid service. Accuracy is high. But you pay per API call, you hand your audio to someone else's servers, and the moment you can't pay — or the company shuts down — your tool stops working. **I wanted this to be free forever and work completely offline. So no.**

### Option 2: Train my own neural network from scratch
The research is genuinely amazing. Models like **AASIST** (Audio Anti-Spoofing using Integrated Spectro-Temporal Graph Attention Networks) and **RawNet2** achieve error rates under 1% on benchmark datasets. But training them requires:
- A massive labeled dataset (ASVspoof has 100,000+ samples)
- Days of GPU compute time (and a good GPU to start)
- Deep ML expertise to tune properly

I wanted something anyone could clone and run in under 5 minutes on a normal laptop. Training a custom model was too heavy for that. **I wanted to lower the barrier to zero.**

### Option 3: Plug in a pre-trained HuggingFace model
HuggingFace has community-trained models for audio classification that detect deepfakes. And honestly — this is actually built in as an *optional second signal*. You can turn it on with one environment variable.

The catch: downloading 400MB of weights on first run is a rough experience for someone just wanting to quickly check a clip. So it's opt-in, not the default.

### Option 4: Acoustic/spectral heuristics (the default approach)
This is what I went with. It's grounded in decades of **anti-spoofing research** — originally developed for detecting fake voices in phone banking systems. It uses `librosa`, a well-tested Python audio library, to extract and score acoustic features.

**Why this won:**
- Zero downloads. Works immediately after `pip install`.
- Explainable. The code can tell you *which* specific features triggered the score — not just "the model says so."
- Fast. 1-3 seconds on a regular CPU.
- Readable. Every line of detection logic is in `backend/ml/spectral.py` and a newcomer can follow it.

The honest tradeoff: it's not as accurate as a neural network against the very best deepfakes. But it catches the vast majority of voice cloning tools people actually encounter in the real world. And you can always layer the transformer model on top for higher stakes use cases.

---

## ✨ What it does

- 🎙️ **Upload audio files** — WAV, MP3, M4A, OGG, FLAC, WEBM, OPUS, up to 25MB
- 🎤 **Record directly from your microphone** — no file needed, works in browser
- 📊 **Spectrogram visualization** — see the frequency fingerprint of the audio
- 🔍 **Plain-English indicators** — explains *why* something was flagged, not just a number
- 📋 **Analysis history** — every result saved locally, filterable by verdict, deletable
- 🔌 **Full REST API** — use it from any language, full OpenAPI docs at `/docs`
- 🤗 **Optional transformer model** — layer in any HuggingFace audio classifier as a second signal
- 🆓 **Completely free** — no account, no API key, no rate limits, no data leaves your machine

---

## 🚀 Getting Started — Complete Beginner Guide

> **Never used Git, Python, or Docker before?** No problem. Follow these steps exactly and it will work.

### What you need first

Before anything else, install these two things:

**1. Git** — for downloading the project
- Mac: Open Terminal and type `git --version`. If it asks to install developer tools, say yes.
- Windows: Download from [git-scm.com](https://git-scm.com/download/win) and install.
- Linux: `sudo apt install git`

**2. Docker Desktop** — packages the app so you don't have to install Python or Node.js yourself
- Download from [docker.com/get-started](https://www.docker.com/get-started/)
- Install it and make sure the Docker icon appears in your menu bar (Mac) or system tray (Windows)
- You'll know it's running when the icon shows "Docker Desktop is running"

That's it. You don't need Python. You don't need Node.js. Docker handles everything.

---

### Step-by-step: Running with Docker (recommended)

**Step 1 — Download the project**

Open Terminal (Mac/Linux) or Command Prompt (Windows) and run:

```bash
git clone https://github.com/Manas470/voiceclone-guard.git
cd voiceclone-guard
```

You should now be inside a folder called `voiceclone-guard`.

**Step 2 — Run the setup script**

```bash
# Mac / Linux:
chmod +x setup.sh
./setup.sh

# Windows (in Command Prompt):
docker-compose up --build
```

This will take 2-5 minutes the first time while Docker downloads and builds everything. You'll see a lot of text scrolling — that's normal.

**Step 3 — Open the app**

When you see output like `frontend_1 | ready started server`, open your browser and go to:

```
http://localhost:3000
```

You should see the VoiceClone Guard interface.

**Step 4 — Test it**

Click "Upload Audio" and choose any audio file (WAV, MP3, etc.). Click "Analyze." In a few seconds you'll see a verdict: REAL or FAKE, with a confidence percentage and a plain-English explanation.

> 💡 **Tip**: If it says port 3000 or 8000 is already in use, another program is using that port. Run `docker-compose down` then try again.

---

### Running without Docker (for developers)

If you're comfortable with the command line and want to poke around the code:

**Backend (Python API):**

```bash
cd backend

# Create an isolated Python environment
python -m venv .venv

# Activate it
source .venv/bin/activate      # Mac / Linux
.venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Create the data folders the app needs
mkdir -p data/uploads data/models

# Start the API server
uvicorn main:app --reload --port 8000
```

The API is now running at [http://localhost:8000](http://localhost:8000). You can see the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

**Frontend (Next.js web app):**

Open a new terminal:

```bash
cd frontend

# Install JavaScript dependencies
npm install --legacy-peer-deps

# Tell the frontend where the API lives
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### Verifying it works

```bash
# Should return: {"status":"ok", "model":"loaded", ...}
curl http://localhost:8000/api/health

# Analyze an audio file from the command line
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@your_audio_file.wav"
```

---

## 📁 Project Structure — Plain-English Tour

If you're new to full-stack projects, here's what every file does:

```
voiceclone-guard/
│
├── docker-compose.yml       ← Wires backend + frontend into one command
├── setup.sh                 ← The script that starts everything
├── .env.example             ← Template for your settings (copy to .env)
│
├── backend/                 ← Python API (the brains of the operation)
│   ├── main.py              ← Entry point. Starts the FastAPI server.
│   ├── requirements.txt     ← Python libraries to install
│   ├── Dockerfile           ← Recipe for building the backend container
│   │
│   ├── app/
│   │   ├── config.py        ← All settings (paths, limits, feature flags)
│   │   ├── database.py      ← SQLite setup (stores every analysis you run)
│   │   │
│   │   ├── routers/         ← API endpoints (the URLs the frontend calls)
│   │   │   ├── analyze.py   ← POST /api/analyze  — the main detection call
│   │   │   ├── history.py   ← GET  /api/history  — paginated past results
│   │   │   └── health.py    ← GET  /api/health   — is the server alive?
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py   ← Data shapes: what the API sends and receives
│   │   │
│   │   └── services/
│   │       ├── audio_preprocessor.py  ← Loads and normalizes audio
│   │       └── detector.py            ← Orchestrates detection + spectrogram
│   │
│   └── ml/                  ← The actual deepfake detection logic
│       ├── spectral.py      ← ⭐ Core detector — 7 acoustic signals
│       └── transformer.py   ← Optional HuggingFace model wrapper
│
└── frontend/                ← Next.js web app (what users see)
    └── src/
        ├── app/
        │   ├── layout.tsx   ← Page shell (navbar, fonts, meta tags)
        │   ├── page.tsx     ← Home page (Analyze tab + History tab)
        │   └── globals.css  ← Global styles and Tailwind CSS config
        │
        ├── components/
        │   ├── NavBar.tsx        ← Top navigation bar
        │   ├── Hero.tsx          ← Headline section and feature list
        │   ├── AudioAnalyzer.tsx ← Upload widget + microphone recorder
        │   ├── ResultDisplay.tsx ← Verdict card, scores, spectrogram
        │   └── HistoryPanel.tsx  ← Past analyses table with pagination
        │
        ├── lib/
        │   └── api.ts       ← All fetch() calls to the backend in one place
        │
        └── types/
            └── declarations.d.ts  ← TypeScript type shims for icon library
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize:

```env
# ─── Upload limit ─────────────────────────────────────────
MAX_FILE_SIZE_MB=25

# ─── Optional transformer model ───────────────────────────
# Set to true to download and use a second HuggingFace model.
# First run will download ~400 MB. Requires internet.
# Adds ~0.5-1s to analysis time.
USE_TRANSFORMER_MODEL=false
HF_MODEL_ID=MelissaAzoulay/deepfake_voice_detector

# ─── CORS (who can call the API) ──────────────────────────
# For production, change this to your actual domain.
CORS_ORIGINS=http://localhost:3000
```

---

## 📡 Using the API from your own code

The backend is a full REST API. You can call it from any language without using the web UI at all.

**Python:**
```python
import requests

with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": ("audio.wav", f, "audio/wav")}
    )

result = response.json()
print(f"Verdict:    {result['verdict']}")            # "REAL" or "FAKE"
print(f"Confidence: {result['confidence_pct']}%")    # e.g. 87.3
print(f"Risk level: {result['risk_level']}")         # "LOW", "MEDIUM", "HIGH"
for line in result['indicators']:
    print(f"  • {line}")
```

**JavaScript / Node.js:**
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

**curl:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@clip.mp3" | python3 -m json.tool
```

**Interactive docs** (try any endpoint in your browser): [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔬 The 7 Detection Signals

Here's exactly what's being measured and why it matters:

**1. Spectral Flatness** — How evenly is sound energy spread across frequencies? Real speech is uneven (some frequencies dominate depending on the sound). AI synthesis tends to flatten this distribution in a way that's measurably different from organic speech.

**2. MFCC Variance** — MFCCs (Mel-Frequency Cepstral Coefficients) are essentially a compact fingerprint of how a voice sounds. Real voices have high variance because natural expressiveness is hard to fake. AI voices are generated deterministically and come out "over-smooth."

**3. Pitch Consistency (F0)** — Your pitch wobbles naturally as you speak — this is called jitter. Neural TTS systems generate pitch mathematically and produce suspiciously regular patterns that don't match the irregularity of a real vocal tract.

**4. Harmonic-to-Noise Ratio** — Real voices have a natural mix of harmonic (tonal) content and noise. Voice cloning vocoders (HiFi-GAN, WaveNet, etc.) often push this ratio into ranges you don't see in natural speech.

**5. Noise Floor** — Real recordings made anywhere contain ambient noise. Many TTS systems produce audio that is perfectly silent between voiced segments — a dead giveaway that no physical room or microphone was involved.

**6. Spectral Flux** — How fast does the audio spectrum change frame to frame? Real speech has rapid, dynamic changes. Some synthesis methods produce too-uniform transitions that sound right to the ear but look wrong to the analyzer.

**7. High-Frequency Energy** — Real microphones and voices produce specific patterns above 6kHz. Many vocoders fail to model this range accurately, either producing too little energy there or periodic artifacts that natural recordings don't have.

---

## 🧪 Quick Sanity Test

Generate a test file and run it through the API:

```bash
python3 - << 'EOF'
import numpy as np, wave, struct
sr = 16000
t = np.linspace(0, 3, sr * 3)
audio = np.sin(2 * np.pi * 440 * t) * 0.5  # Pure sine wave — highly "fake-like"
with wave.open('test_fake.wav', 'w') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
    f.writeframes(struct.pack('<' + 'h' * len(audio), *np.int16(audio * 32767)))
print("Created test_fake.wav")
EOF

curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_fake.wav" | python3 -m json.tool
```

A pure sine wave will score very high on fake probability — perfect pitch regularity, flat spectrum, zero noise floor. That's exactly what the detector is looking for.

---

## 🏭 Is this production-ready?

Yes, for personal and small-team use right now. Here's an honest breakdown:

| Area | Status | Notes |
|---|---|---|
| Core detection | ✅ Production-ready | 7-signal pipeline, tested on real and synthetic audio |
| REST API | ✅ Production-ready | FastAPI with Pydantic validation, error handling, health endpoint |
| Frontend | ✅ Production-ready | Next.js 14, TypeScript strict mode, handles all edge cases |
| Database | ✅ Production-ready | Async SQLite, auto-migration on startup |
| Docker deploy | ✅ Production-ready | One command, persistent volume, restart policies |
| Authentication | ⚪ Not included | Not needed for local/internal use. Add an API gateway if exposing publicly |
| Rate limiting | ⚪ Not included | Add Nginx or Cloudflare in front if deploying publicly at scale |
| HTTPS | ⚪ Not included | Add a reverse proxy (Nginx + Let's Encrypt) for internet-facing deploys |
| Accuracy vs best deepfakes | ⚠️ Good, not perfect | Works well against common tools. Can be fooled by very high-quality synthesis |

**To expose this to the internet properly**, add Nginx as a reverse proxy with SSL. A simple config would put Nginx on port 443 in front of both services.

---

## 🤝 How to Contribute

**If you're a developer:**
- Improve the spectral scoring thresholds using ASVspoof 2019/2021 datasets
- Add a batch analysis endpoint
- Add WebSocket streaming for real-time analysis
- Help reduce the Docker image size

**If you're a researcher:**
- Benchmark against commercial deepfake detectors
- Help calibrate for specific TTS systems (ElevenLabs, Voicebox, Tortoise, VALL-E)
- Add formal evaluation metrics (EER, t-DCF)

**If you're not technical:**
- Test it on clips you're suspicious about and open an issue if the verdict seems wrong
- Share it with journalists, lawyers, HR teams, or security researchers who need it
- Write about it — blog posts, tweets, Reddit threads. People need to know this exists.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

---

## 🚧 Limitations (I want to be honest)

1. **High-quality deepfakes can fool it.** The best voice cloning systems — especially when trained on hours of the target voice — will produce audio that's harder to catch. This tool works well against off-the-shelf cloning tools but is not infallible.

2. **Short clips are harder.** We need at least 2-3 seconds of clear audio to get reliable features. Under that, confidence will be low.

3. **Compressed audio adds noise.** Phone call audio, highly compressed Opus files, or recordings with heavy noise may shift the acoustic features in ways that affect accuracy.

4. **Use it as one signal, not a final verdict.** Treat this as one piece of evidence alongside context, metadata, and common sense. Not as the sole judge.

---

## 📚 Further Reading

- [ASVspoof 2021 Challenge](https://www.asvspoof.org/) — The benchmark dataset for voice anti-spoofing research
- [AASIST Paper](https://arxiv.org/abs/2110.01200) — State-of-the-art anti-spoofing neural network
- [RawNet2 Paper](https://arxiv.org/abs/2011.01108) — Raw waveform-based anti-spoofing approach
- [Librosa Docs](https://librosa.org/doc/latest/index.html) — The audio analysis library powering the core detector
- [FTC on Voice Cloning](https://www.ftc.gov/business-guidance/blog/2023/03/ftcs-voice-cloning-challenge) — Real-world threat landscape from the FTC

---

## 📄 License

MIT — use it however you want. Build products with it. Integrate it into your pipeline. Just keep the license header.

---

<div align="center">

Built with ☕ and genuine concern about AI voice cloning by **Manas Mourya**

If this helped you, a ⭐ on the repo goes a long way.

[Report a Bug](https://github.com/Manas470/voiceclone-guard/issues) · [Request a Feature](https://github.com/Manas470/voiceclone-guard/issues) · [Start a Discussion](https://github.com/Manas470/voiceclone-guard/discussions)

</div>
