#!/usr/bin/env bash
# NL2SQL Chat – environment bootstrap
set -euo pipefail

PYTHON=${PYTHON:-python3}  # allow PYTHON override
VENV=".venv"

echo "🔧  Creating virtual-env ($VENV)…"
$PYTHON -m venv $VENV
source $VENV/bin/activate

echo "📦  Installing Python deps…"
pip install --upgrade pip
pip install -r requirements.txt

echo "💻  Installing front-end deps…"
pushd frontend >/dev/null
if command -v pnpm &>/dev/null; then pnpm install
elif command -v yarn &>/dev/null; then yarn install
else npm install; fi
popd >/dev/null

echo -e "\n✅  Done!
→ source $VENV/bin/activate
→ uvicorn api.main:app --reload --port 8000   # backend
→ cd frontend && npm run dev                 # frontend"
