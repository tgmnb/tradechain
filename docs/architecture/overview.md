# Architecture Overview

## Scope

Sprint 1-2 infrastructure to support a minimum closed loop:

`Mock ingestion -> Event persistence -> LangGraph proposal draft -> Archive -> Discord feedback`

## Components

- `api-service`: external API gateway and orchestration hand-off
- `ingestion-service`: provider adapter abstraction + mock source
- `agent-core`: LangGraph graphs (one active, others placeholders)
- `archive-service`: archive payload to MinIO and persist metadata to PostgreSQL
- `evaluation-service`: placeholder internal API surface
- `discord-bot`: slash command frontend for initial testing
- `n8n`: scheduler/orchestrator calling API workflow endpoints

## Storage

- PostgreSQL for operational objects
- MinIO for archived payload snapshots
- Redis/Qdrant provisioned for future capability expansion

## Interface contracts

- Shared Pydantic contracts in `libs/contracts`
- JSON schemas exported to `libs/contracts/schemas`
- Shared DB models in `libs/db/models.py`

## Reliability baseline

- Workflow trace headers: `X-Request-ID`, `X-Chain-Type`, `X-Actor`
- API key segregation: external and internal keys
- Archive write failures returned as retryable 503 with `archive_write_failed`
