# Tradechain Foundation (WSL/Linux + Discord)

This repository delivers the current infrastructure and workflow baseline for the AI investment research agent system.

## What is implemented

- Monorepo foundation: `apps`, `libs`, `workflows`, `sql`, `docs`, `tests`
- Core services (FastAPI + Python):
  - `api-service` (external gateway)
  - `ingestion-service` (mock ingestion + provider adapter)
  - `agent-core` (LangGraph event -> proposal)
  - `archive-service` (DB + MinIO archive)
  - `evaluation-service` (placeholder)
  - `discord-bot` (slash command entry, profile-based)
- Data infra in compose: PostgreSQL, Redis, MinIO, Qdrant, n8n
- Alembic migration for core schema (Sprint 1-2)
- n8n workflow JSONs (one runnable, others placeholders)
- Shared contracts in `libs/contracts` + JSON Schema export

## Architecture

```text
Discord Slash Bot -> api-service -> ingestion-service -> agent-core -> archive-service
                        |                |                |
                        |                |                +-> MinIO + archives table
                        |                +-> EventIn/EventNormalized contracts
                        +-> PostgreSQL (tasks/events/proposals/reviews/archives/skill_versions)

n8n -> calls api-service workflow endpoints with standard headers
```

## Repository layout

```text
apps/
  api_service/
  ingestion_service/
  agent_core/
  archive_service/
  evaluation_service/
  discord_bot/
libs/
  contracts/
  db/
workflows/
  n8n/
  langgraph/
sql/
  migrations/
  seeds/
docs/
  architecture/
  adr/
  runbooks/
tests/
```

## Quick start (WSL/Linux)

1. Copy env file:

```bash
cp .env.example .env
```

2. Start all core services:

```bash
docker compose up --build
```

3. Apply migration (from host with Python env, or inside a service container):

```bash
docker compose exec api-service alembic -c sql/migrations/alembic.ini upgrade head
```

4. (Optional) seed initial skill versions:

```bash
docker compose exec postgres psql -U tradechain -d tradechain -f /workspace/sql/seeds/001_skill_versions.sql
```

5. (Optional) export JSON schemas:

```bash
PYTHONPATH=. python scripts/export_contract_schemas.py
```

6. Start Discord bot only when token is ready:

```bash
docker compose --profile discord up discord-bot
```

## Service ports

- `api-service`: `8000`
- `ingestion-service`: `8001`
- `agent-core`: `8002`
- `archive-service`: `8003`
- `evaluation-service`: `8004`
- `n8n`: `5678`
- `postgres`: `5432`
- `minio`: `9000` (API), `9001` (console)
- `qdrant`: `6333`

## API key and workflow headers

### Required auth headers

- External endpoints (`api-service`): `X-API-Key: $API_SERVICE_API_KEY`
- Internal endpoints: `X-API-Key: $INTERNAL_SERVICE_API_KEY`

### Workflow trace headers

- `X-Request-ID`
- `X-Chain-Type`
- `X-Actor`

These are forwarded across services for traceability.

## Public API (api-service)

- `POST /v1/tasks`
- `GET /v1/tasks/{task_id}`
- `POST /v1/events`
- `POST /v1/proposals/draft`
- `GET /v1/proposals/{proposal_id}`
- `GET /v1/proposals/latest`
- `GET /v1/improvement/scores/latest`
- `GET /v1/improvement/scores/by-agent/{agent_name}`
- `GET /v1/improvement/tickets/latest`
- `GET /v1/improvement/tickets/by-target/{target_type}/{target_name}`
- `GET /v1/reviews/latest`
- `GET /v1/reviews/by-object/{object_type}/{object_id}`
- `POST /v1/workflows/intel-update/run`
- `POST /v1/workflows/major-task/run`
- `POST /v1/workflows/daily-preopen/run`
- `POST /v1/workflows/intraday-watch/run` (placeholder)
- `POST /v1/workflows/postclose-review/run` (baseline review path)
- `POST /v1/workflows/nightly-improvement/run` (placeholder)
- `GET /healthz`

## LLM provider

`agent-core` now supports a provider abstraction for proposal generation.

- `LLM_PROVIDER=heuristic`: no external model call, local fallback generation
- `LLM_PROVIDER=minimax`: calls MiniMax through the OpenAI-compatible API

Relevant env vars:

- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_TIMEOUT_SECONDS`
- `LLM_PROXY_URL`

## Internal APIs

- `POST /internal/ingestion/fetch` (`ingestion-service`)
- `POST /internal/graphs/event-to-proposal/run` (`agent-core`)
- `POST /internal/graphs/review/run` (`agent-core`, baseline review graph)
- `POST /internal/graphs/evaluation/run` (`agent-core`, placeholder)
- `POST /internal/graphs/improvement/run` (`agent-core`, placeholder)
- `POST /internal/archive` (`archive-service`)
- `GET /internal/archive/{object_type}/{object_id}` (`archive-service`)

## Contract models (libs/contracts)

- `TaskCreate` / `TaskRead`
- `EventIn` / `EventNormalized`
- `ProposalDraftRequest` / `ProposalDraft` / `ProposalFinal`
- `AgentScore` / `ImprovementTicket`
- `ReviewRecord` / `PostcloseReview`
- `WatchObservation`
- `ArchiveCreate` / `ArchiveRef`
- `GraphRunRequest` / `GraphRunResponse` / `GraphState`

### Sample payload: `EventIn`

```json
{
  "source": "mock_news",
  "event_type": "macro",
  "title": "PBOC announces targeted liquidity support",
  "content": "Policy tools target credit easing for real economy sectors.",
  "asset_scope": ["CN10Y", "CNY", "banking"],
  "impact_direction": "positive",
  "confidence": 0.73,
  "raw_payload": {"source_url": "mock://macro/1"},
  "occurred_at": "2026-03-12T07:30:00Z",
  "schema_version": "1.0.0"
}
```

### Sample payload: `ProposalFinal`

```json
{
  "id": "8e047d7a-0600-4ced-b6e3-4e508cfce95e",
  "source_event_id": "f7a7c43f-7d04-4d27-bd7d-68018c8f6ad3",
  "theme": "PBOC announces targeted liquidity support",
  "asset_scope": ["CN10Y", "CNY", "banking"],
  "initial_logic": "Policy tools target credit easing for real economy sectors.",
  "trigger_conditions": ["When macro impact confirms in price/flow data"],
  "invalidation_conditions": ["If key evidence is contradicted by follow-up disclosures"],
  "risks": ["Headline noise may cause false positives"],
  "confidence": 0.73,
  "status": "draft",
  "recommended_action": "continue_pipeline",
  "requires_human": false,
  "metadata": {
    "generated_by": "event_to_proposal_graph",
    "schema_version": "1.0.0"
  },
  "schema_version": "1.0.0",
  "created_at": "2026-03-12T07:32:00Z",
  "updated_at": "2026-03-12T07:32:00Z"
}
```

## n8n workflows

Import these files from `workflows/n8n/`:

- `intel_update.json` (runnable minimum)
- `major_task.json` (placeholder)
- `daily_preopen.json` (placeholder)
- `intraday_watch.json` (placeholder)
- `postclose_review.json` (placeholder)
- `nightly_improvement.json` (placeholder)

## Discord slash commands

Implemented in `apps/discord_bot/app/bot.py`:

- `/task_create`
- `/proposal_latest`
- `/intel_update`
- `/system_health`

Plain channel messages also flow through a top-level politburo dispatcher:

- direct chat/help requests are answered immediately
- health and latest-proposal queries are handled without activating research chains
- research/analysis/proposal-generation requests are escalated into the downstream workflow

## Testing status

Test files and scenarios are provided under `tests/`, but this delivery intentionally does **not** execute integration/regression runs yet.

## OpenSpec planning

Project planning is now tracked in-repo through OpenSpec.

- Local CLI entrypoint: `./scripts/openspec.sh`
- List active changes: `./scripts/openspec.sh list`
- Validate a change: `./scripts/openspec.sh validate <change-name>`
- Make target: `make openspec-status`

Current active planning changes include:

- `replan-project-roadmap`
- `implement-postclose-review-baseline`
- `propose-intraday-watch-baseline`
- `propose-nightly-improvement-baseline`

Reference docs:

- `docs/plan/2026-03-24-openspec-roadmap-index.md`
- `docs/runbooks/openspec.md`

## Current boundary

Implemented now:

- Foundation infra + core schema
- Event -> proposal minimal loop with archive + Discord entry
- Proposal -> research -> strategy -> trading plan planning loop
- Postclose review baseline with structured review output and archive hand-off

Intentionally deferred:

- Real news/market data connectors
- Full intraday watch implementation with live market data
- Real-time trading execution and broker connectivity
- Full evaluation/improvement automation
