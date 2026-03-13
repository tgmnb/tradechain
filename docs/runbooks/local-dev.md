# Local Runbook (WSL/Linux)

## Prerequisites

- Docker + Docker Compose
- Python 3.12
- Project dependencies from `requirements/base.txt`

## Setup

1. `cp .env.example .env`
2. For offline local work, set `LLM_PROVIDER=heuristic` in `.env`
3. `docker compose up --build`
4. `docker compose exec api-service alembic -c sql/migrations/alembic.ini upgrade head`
5. Optional SQL seed: `docker compose exec postgres psql -U tradechain -d tradechain -f /workspace/sql/seeds/001_skill_versions.sql`
6. Optional registry projection: `PYTHONPATH=. python scripts/sync_registry_to_db.py`
7. Optional schema export: `PYTHONPATH=. python scripts/export_contract_schemas.py`

## Smoke Checks

- Health: `curl --noproxy '*' http://127.0.0.1:8000/healthz`
- Intel loop: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/intel-update/run -H 'X-API-Key: external-dev-key'`
- Daily preopen chain: `curl --noproxy '*' -X POST http://127.0.0.1:8000/v1/workflows/daily-preopen/run -H 'X-API-Key: external-dev-key'`
- Registry view: `curl --noproxy '*' http://127.0.0.1:8000/v1/registry/souls -H 'X-API-Key: external-dev-key'`

## Soul / Skill Authoring

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
