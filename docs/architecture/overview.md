# Architecture Overview

## Scope

Current baseline now supports two runnable minimum chains:

- `Mock ingestion -> Event persistence -> LangGraph proposal draft -> Archive -> Discord feedback`
- `Proposal -> Research report -> Strategy -> Trading plan -> Archive`

## Components

- `api-service`: external API gateway, registry read APIs, and workflow hand-off
- `ingestion-service`: provider adapter abstraction + mock source
- `agent-core`: LangGraph graphs with soul/skill-aware profile resolution
- `archive-service`: archive payload to MinIO and persist metadata to PostgreSQL
- `evaluation-service`: placeholder internal API surface
- `discord-bot`: slash command frontend for initial testing
- `n8n`: scheduler/orchestrator calling API workflow endpoints
- `configs/souls/*`: filesystem source of truth for department and specialist souls
- `skills/*`: filesystem source of truth for skill manifests and prompts

## Storage

- PostgreSQL for operational objects and registry projection tables
- MinIO for archived payload snapshots
- Redis/Qdrant provisioned for future capability expansion

## Interface contracts

- Shared Pydantic contracts in `libs/contracts`
- JSON schemas exported to `libs/contracts/schemas`
- Shared DB models in `libs/db/models.py`
- Registry loader in `libs/registry`

## Reliability baseline

- Workflow trace headers: `X-Request-ID`, `X-Chain-Type`, `X-Actor`
- API key segregation: external and internal keys
- Archive write failures returned as retryable 503 with `archive_write_failed`
- `MiniMax` is the online default provider, while `heuristic` remains the offline fallback
