#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[MedAssist] Starting on cloud/Linux."
echo "[MedAssist] This script does not train models. Configure Qwen only on a machine with enough GPU/RAM."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_rag_index.py
python -m uvicorn medassist_lung_agent.main:app --host 0.0.0.0 --port "${PORT:-8000}"

