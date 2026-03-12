#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set -a
. "$ROOT_DIR/.env"
set +a

unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy

cd "$ROOT_DIR"

while true; do
  .venv/bin/python -m apps.discord_bot.app.bot
  sleep 5
done
