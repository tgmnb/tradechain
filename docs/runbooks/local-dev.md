# Local Runbook (WSL/Linux)

## Prerequisites

- Docker + Docker Compose
- Python 3.12 (for local utilities/migrations)

## Steps

1. `cp .env.example .env`
2. `docker compose up --build`
3. `docker compose exec api-service alembic -c sql/migrations/alembic.ini upgrade head`
4. Optional seed: `docker compose exec postgres psql -U tradechain -d tradechain -f /workspace/sql/seeds/001_skill_versions.sql`

## Common Checks

- `curl --noproxy '*' http://127.0.0.1:8000/healthz`
- `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/intel-update/run -H 'X-API-Key: external-dev-key'`
- `docker compose ps`
- `docker compose logs --tail=100 api-service ingestion-service agent-core archive-service`

## LLM Config

- `LLM_PROVIDER=heuristic` keeps proposal generation local and deterministic.
- `LLM_PROVIDER=minimax` enables MiniMax proposal generation through `LLM_BASE_URL`.
- In the current environment, `agent-core` can reach MiniMax directly, so `LLM_PROXY_URL` should stay empty unless container networking changes.

## Verify

- `GET http://localhost:8000/healthz`
- `POST http://localhost:8000/v1/workflows/intel-update/run` with `X-API-Key`
- Check proposals in DB and archives in MinIO bucket

## n8n import

Import files from `workflows/n8n/*.json` and set environment variable `API_SERVICE_API_KEY` in n8n runtime.

## Discord bot

Set `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`, optional `DISCORD_GUILD_ID`, then run:

`docker compose --profile discord up discord-bot`

Recommended:

- Set `DISCORD_GUILD_ID` if you want slash commands to sync quickly in one server.
- Use a dedicated channel for the bot and set `DISCORD_CHANNEL_ID` to restrict commands there.
- If Discord access needs a proxy, set `DISCORD_PROXY_URL=http://host.docker.internal:7890`.
- Enable `Message Content Intent` for the bot in the Discord developer portal if you want plain channel messages to trigger the agent flow.
- After the bot starts, use `/system_health`, `/proposal_latest`, `/intel_update`, `/task_create`.

If your proxy only listens on host `127.0.0.1`, run the bot on the host instead of Docker:

- `nohup ./scripts/run_discord_bot_host.sh >/tmp/tradechain-discord-bot.log 2>&1 &`
- `tail -f /tmp/tradechain-discord-bot.log`
