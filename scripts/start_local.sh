#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo ".env is missing. Run scripts/install_local.sh first." >&2
  exit 1
fi

if [[ "${TRADECHAIN_BUILD:-0}" == "1" ]]; then
  docker compose up -d --build
else
  docker compose up -d
fi
docker compose exec -T api-service alembic -c sql/migrations/alembic.ini upgrade head

DISCORD_BOT_TOKEN="$(awk -F= '$1=="DISCORD_BOT_TOKEN"{sub(/^[[:space:]]+/, "", $2); print $2}' .env)"
if [[ -n "${DISCORD_BOT_TOKEN}" ]]; then
  docker compose --profile discord up -d discord-bot
fi

echo "[smoke] api-service health"
docker exec tradechain-api-service python -u - <<'PY'
import urllib.request
response = urllib.request.urlopen("http://127.0.0.1:8000/healthz", timeout=30)
print("api-service", response.status, response.read().decode())
PY

echo "[smoke] politburo direct reply"
docker exec tradechain-api-service python -u - <<'PY'
import json
import urllib.request

body = json.dumps(
    {
        "text": "你是谁，你能做什么？",
        "user_name": "bootstrap",
        "user_id": "bootstrap",
        "channel_id": "bootstrap",
        "guild_id": "bootstrap",
    }
).encode()
request = urllib.request.Request(
    "http://127.0.0.1:8000/v1/agent/discord-message",
    data=body,
    method="POST",
    headers={"Content-Type": "application/json", "X-API-Key": "external-dev-key"},
)
response = urllib.request.urlopen(request, timeout=120)
print("politburo", response.status, response.read().decode())
PY

echo "[smoke] politburo research routing"
docker exec tradechain-api-service python -u - <<'PY'
import json
import urllib.request

body = json.dumps(
    {
        "text": "请帮我研究一下今天的宏观变化并给我一个提案",
        "user_name": "bootstrap",
        "user_id": "bootstrap",
        "channel_id": "bootstrap",
        "guild_id": "bootstrap",
    }
).encode()
request = urllib.request.Request(
    "http://127.0.0.1:8000/v1/agent/discord-message",
    data=body,
    method="POST",
    headers={"Content-Type": "application/json", "X-API-Key": "external-dev-key"},
)
response = urllib.request.urlopen(request, timeout=180)
print("research-route", response.status, response.read().decode())
PY

echo "Tradechain services are up."
