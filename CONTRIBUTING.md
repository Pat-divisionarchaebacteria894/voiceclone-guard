# Contributing to VoiceClone Guard

Thanks for wanting to help! Here's how to get started.

## Quick setup for contributors

```bash
git clone https://github.com/manasmourya/voiceclone-guard.git
cd voiceclone-guard
cp .env.example .env
./setup.sh          # Docker — or follow the manual steps in README.md
```

## Submitting changes

1. Fork the repo on GitHub
2. Create a branch: `git checkout -b my-feature`
3. Make your changes
4. Test: `curl http://localhost:8000/api/health` should return `{"status":"ok",...}`
5. Open a Pull Request — describe what you changed and why

## Ideas for contributions

- Better threshold calibration against ASVspoof datasets
- More audio format support
- Batch upload endpoint
- Internationalization (i18n)
- Docker image size reduction
- More unit tests

## Code style

- Python: follow PEP 8, use type hints
- TypeScript: strict mode, no `any`
- Keep functions small and well-named — a newcomer should be able to read `ml/spectral.py` and understand each signal

## Questions?

Open a [Discussion](https://github.com/manasmourya/voiceclone-guard/discussions) — no question is too basic.
