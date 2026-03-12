#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set -a
. "$ROOT_DIR/.env"
set +a

cd "$ROOT_DIR"
exec .venv/bin/python -m apps.discord_bot.app.bot
