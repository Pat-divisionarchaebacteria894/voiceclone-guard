#!/usr/bin/env bash
# ── VoiceClone Guard — Quick Setup Script ────────────────────────────────────
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "╔══════════════════════════════════════╗"
echo "║       VoiceClone Guard Setup          ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# ── Check prerequisites ───────────────────────────────────────────────────────
check_cmd() {
  if ! command -v "$1" &>/dev/null; then
    echo -e "${RED}✗ $1 not found. Please install it and re-run.${NC}"
    exit 1
  fi
  echo -e "${GREEN}✓ $1 found${NC}"
}

echo "Checking prerequisites..."
check_cmd docker
check_cmd docker-compose || check_cmd "docker compose"

# ── Copy .env if missing ──────────────────────────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  echo -e "${YELLOW}Created .env from .env.example — edit it to customise settings.${NC}"
fi

# ── Create local data dirs (bind-mount fallback) ──────────────────────────────
mkdir -p backend/data/uploads backend/data/models

# ── Build & start ─────────────────────────────────────────────────────────────
echo ""
echo "Building Docker images (first run may take a few minutes)..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

# ── Wait for backend health ────────────────────────────────────────────────────
echo ""
echo "Waiting for backend to be ready..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
    break
  fi
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo -e "${RED}Backend did not start in time. Check logs: docker-compose logs backend${NC}"
    exit 1
  fi
done

echo ""
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  VoiceClone Guard is running!             ${NC}"
echo -e "${GREEN}  Frontend : http://localhost:3000          ${NC}"
echo -e "${GREEN}  API docs : http://localhost:8000/docs     ${NC}"
echo -e "${GREEN}══════════════════════════════════════════${NC}"
