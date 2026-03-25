# Local Runbook (WSL/Linux)

## Prerequisites

- Docker + Docker Compose
- Python 3.12
- Project dependencies from `requirements/base.txt`

## Setup

1. `cp .env.example .env`
2. For offline local work, set `LLM_PROVIDER=heuristic` in `.env`
3. Keep `GOVERNED_DIALOGUE_ENABLED=true` if you want natural-language research prompts to use the new governed dialogue chain
4. Preferred bootstrap: `bash scripts/install_local.sh`
5. Preferred startup: `bash scripts/start_local.sh`
6. Manual fallback: `docker compose up --build`
7. Manual migration: `docker compose exec api-service alembic -c sql/migrations/alembic.ini upgrade head`
8. Optional SQL seed: `docker compose exec postgres psql -U tradechain -d tradechain -f /workspace/sql/seeds/001_skill_versions.sql`
9. Optional registry projection: `PYTHONPATH=. python scripts/sync_registry_to_db.py`
10. Optional schema export: `PYTHONPATH=. python scripts/export_contract_schemas.py`

## Python Validation Environment

`scripts/install_local.sh` now supports two paths:

- preferred: use `python3 -m venv .venv`
- fallback: if `ensurepip` / `venv` bootstrap is unavailable, use `scripts/bootstrap_python_env.sh` to create a repository-local pip + virtualenv toolchain under `.local/`

Validated local commands:

- `.venv/bin/python scripts/export_contract_schemas.py`
- `.venv/bin/pytest -q`
- `./scripts/openspec.sh validate replan-project-roadmap`
- `./scripts/openspec.sh validate implement-postclose-review-baseline`
- `./scripts/openspec.sh validate propose-intraday-watch-baseline`
- `./scripts/openspec.sh validate propose-nightly-improvement-baseline`

## Smoke Checks

- Health: `curl --noproxy '*' http://127.0.0.1:8000/healthz`
- Intel loop: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/intel-update/run -H 'X-API-Key: external-dev-key'`
- Daily preopen chain: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/daily-preopen/run -H 'X-API-Key: external-dev-key'`
- Web research: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/web-research/run -H 'X-API-Key: external-dev-key' -H 'Content-Type: application/json' -d '{"query":"日本央行最新政策","max_results":5}'`
- Policy crawl: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/policy-crawl/run -H 'X-API-Key: external-dev-key' -H 'Content-Type: application/json' -d '{"limit_per_source": 5}'`
- Intraday watch baseline: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/intraday-watch/run -H 'X-API-Key: external-dev-key' -H 'Content-Type: application/json' -d '{"input_mode":"mock_replay","snapshots":[{"asset":"IF_MAIN","observed_at":"2026-03-25T09:35:00Z","last_price":103.2,"prev_close":100.0,"session_high":103.2,"session_low":100.4,"volume":2600,"average_volume":1000}]}'`
- Nightly improvement baseline: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/nightly-improvement/run -H 'X-API-Key: external-dev-key' -H 'Content-Type: application/json' -d '{"minimum_score_threshold":75,"approval_role":"improvement_officer"}'`
- Registry view: `curl --noproxy '*' http://127.0.0.1:8000/v1/registry/souls -H 'X-API-Key: external-dev-key'`
- Politburo direct reply: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/agent/discord-message -H 'X-API-Key: external-dev-key' -H 'Content-Type: application/json' -d '{"text":"你是谁","user_name":"local","user_id":"local","channel_id":"local","guild_id":"local"}'`
- Governed dialogue smoke: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/agent/discord-message -H 'X-API-Key: external-dev-key' -H 'Content-Type: application/json' -d '{"text":"你研究一下，美国的加降息情况","user_name":"local","user_id":"local","channel_id":"local","guild_id":"local"}'`

## Soul / Skill Authoring

- `LLM_PROVIDER=heuristic` keeps proposal generation local and deterministic.
- `LLM_PROVIDER=minimax` enables MiniMax proposal generation through `LLM_BASE_URL`.
- `api-service` uses the same `LLM_*` settings for top-level direct replies from the politburo agent.
- `api-service` now runs with `network_mode: host` so it can use host-local web proxies and still reach other services through published localhost ports.
- In the current environment, `agent-core` can reach MiniMax directly, so `LLM_PROXY_URL` should stay empty unless container networking changes.
- Web search and policy crawl use `WEB_PROXY_URL`, which should stay as `http://127.0.0.1:7890` when host-side Clash HTTP proxy is available.
- Department folders live in `configs/departments/<department_id>/`
- Department soul lives in `configs/departments/<department_id>/soul.yaml`
- Department skills live in `configs/departments/<department_id>/skills/<skill_name>/`
- Specialist folders live in `configs/departments/<department_id>/specialists/<specialist_id>/`
- Specialist soul lives in `configs/departments/<department_id>/specialists/<specialist_id>/soul.yaml`
- Specialist skills live in `configs/departments/<department_id>/specialists/<specialist_id>/skills/<skill_name>/`
- Functional skills can declare `skill_type: functional` plus a `runtime:` block in `manifest.yaml`
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
- Live market data ownership and alert routing for `intraday_watch`
- Approval actor integration and long-window score quality for `nightly_improvement`
- Docker Compose execution in restricted sandbox environments that cannot join the host mount namespace

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
  - research/search requests first escalate into the downstream `web_research` chain, which currently uses Bing RSS results plus page fetch summarization
  - explicit intel-update style requests still escalate into the `intel_update` chain
  - scheduled government policy intake belongs to `policy_watch`, not direct chat
