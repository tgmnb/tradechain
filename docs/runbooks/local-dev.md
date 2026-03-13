# Local Runbook (WSL/Linux)

## Prerequisites

- Docker + Docker Compose
- Python 3.12
- Project dependencies from `requirements/base.txt`

## Setup

1. `cp .env.example .env`
2. For offline local work, set `LLM_PROVIDER=heuristic` in `.env`
3. Preferred bootstrap: `bash scripts/install_local.sh`
4. Preferred startup: `bash scripts/start_local.sh`
5. Manual fallback: `docker compose up --build`
6. Manual migration: `docker compose exec api-service alembic -c sql/migrations/alembic.ini upgrade head`
7. Optional SQL seed: `docker compose exec postgres psql -U tradechain -d tradechain -f /workspace/sql/seeds/001_skill_versions.sql`
8. Optional registry projection: `PYTHONPATH=. python scripts/sync_registry_to_db.py`
9. Optional schema export: `PYTHONPATH=. python scripts/export_contract_schemas.py`

## Smoke Checks

- Health: `curl --noproxy '*' http://127.0.0.1:8000/healthz`
- Intel loop: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/intel-update/run -H 'X-API-Key: external-dev-key'`
- Daily preopen chain: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/daily-preopen/run -H 'X-API-Key: external-dev-key'`
- Registry view: `curl --noproxy '*' http://127.0.0.1:8000/v1/registry/souls -H 'X-API-Key: external-dev-key'`
- Politburo direct reply: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/agent/discord-message -H 'X-API-Key: external-dev-key' -H 'Content-Type: application/json' -d '{"text":"你是谁","user_name":"local","user_id":"local","channel_id":"local","guild_id":"local"}'`

## Soul / Skill Authoring

- `LLM_PROVIDER=heuristic` keeps proposal generation local and deterministic.
- `LLM_PROVIDER=minimax` enables MiniMax proposal generation through `LLM_BASE_URL`.
- `api-service` uses the same `LLM_*` settings for top-level direct replies from the politburo agent.
- In the current environment, `agent-core` can reach MiniMax directly, so `LLM_PROXY_URL` should stay empty unless container networking changes.
- Department souls live in `configs/souls/departments/`
- Specialist souls live in `configs/souls/specialists/`
- Skill manifests live in `skills/<skill_name>/manifest.yaml`
- Skill prompts live in `skills/<skill_name>/prompt.md`
- After editing manifests, rerun `PYTHONPATH=. python scripts/sync_registry_to_db.py` if you want the DB mirror updated

## Provider Notes

- `LLM_PROVIDER=minimax` is the online default and should be used in deployment environments with a valid `LLM_API_KEY`
- `LLM_PROVIDER=heuristic` is the offline fallback for local structure debugging without network access
- The same contracts and graphs are used in both cases; only the provider implementation changes

## Deployment-Only Validation

These checks still need the deployment environment or external connectivity:

- Real `MiniMax` connectivity and proxy behavior
- Discord bot command sync and channel restrictions
- n8n import plus scheduled execution
- Live market data / intraday watch behavior

## Discord bot

Set `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`, optional `DISCORD_GUILD_ID`, then run:

`docker compose --profile discord up -d discord-bot`

Recommended:

- Set `DISCORD_GUILD_ID` if you want slash commands to sync quickly in one server.
- Use a dedicated channel for the bot and set `DISCORD_CHANNEL_ID` to restrict commands there.
- The current Docker setup runs `discord-bot` with `network_mode: host`, so host-local proxies should be configured as `DISCORD_PROXY_URL=http://127.0.0.1:7890`.
- For Clash-style HTTP proxies, keep `DISCORD_PROXY_FORCE_IPV4=true` and `DISCORD_PROXY_DNS_CACHE_SECONDS=300`.
- SOCKS proxies are also supported via `socks5://...` once the local port is reachable.
- Enable `Message Content Intent` for the bot in the Discord developer portal if you want plain channel messages to trigger the agent flow.
- After the bot starts, use `/system_health`, `/proposal_latest`, `/intel_update`, `/task_create`, `/ask`.
- Plain channel messages now go through the top-level politburo agent:
  - simple chat/help queries are answered directly
  - health/proposal queries are served directly
  - research/analysis requests escalate into the downstream `intel_update` chain
