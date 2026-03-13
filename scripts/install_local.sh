#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi

if ! .venv/bin/python - <<'PY' >/dev/null 2>&1
import fastapi, httpx, pydantic, sqlalchemy, yaml, discord
PY
then
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r requirements/base.txt
fi

echo "Local Python environment is ready."
