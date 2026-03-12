# Local Runbook (WSL/Linux)

## Prerequisites

- Docker + Docker Compose
- Python 3.12 (for local utilities/migrations)

## Steps

1. `cp .env.example .env`
2. `docker compose up --build`
3. `docker compose exec api-service alembic -c sql/migrations/alembic.ini upgrade head`
4. Optional seed: `docker compose exec postgres psql -U tradechain -d tradechain -f /workspace/sql/seeds/001_skill_versions.sql`

## Verify

- `GET http://localhost:8000/healthz`
- `POST http://localhost:8000/v1/workflows/intel-update/run` with `X-API-Key`
- Check proposals in DB and archives in MinIO bucket

## n8n import

Import files from `workflows/n8n/*.json` and set environment variable `API_SERVICE_API_KEY` in n8n runtime.

## Discord bot

Set `DISCORD_BOT_TOKEN`, optional `DISCORD_GUILD_ID`, then run:

`docker compose --profile discord up discord-bot`
