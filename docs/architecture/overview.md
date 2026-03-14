# Architecture Overview

## Scope

Current baseline now supports two runnable minimum chains:

- `Mock ingestion -> Event persistence -> LangGraph proposal draft -> Archive -> Discord feedback`
- `Proposal -> Research report -> Strategy -> Trading plan -> Archive`
- `Discord natural language message -> Politburo dispatch -> Direct LLM reply or intel_update hand-off`
- `Discord natural language message -> Politburo dispatch -> Direct LLM reply or web_research hand-off`
- `Scheduled policy_watch -> top-10 economy government sources -> local policy snapshot output`
- `major_task -> politburo intake -> NPC review -> state_council entry -> proposal/research/strategy/plan pipeline`
  governance output is now written back into `task.context_json`, mirrored into the `reviews` table as an NPC review record, and governance rejection can move the task into `needs_human`

It also now supports one real precondition for the next workflow stage:

- `Trading plan -> Execution record intake -> postclose_review placeholder hand-off`

## Components

- `api-service`: external API gateway, registry read APIs, politburo direct-reply API, and workflow hand-off
- `api-service` now also owns outbound web research and policy crawl execution, using host-network access so it can reuse the local HTTP proxy path
- `ingestion-service`: provider adapter abstraction + mock source
- `agent-core`: LangGraph graphs with soul/skill-aware profile resolution
- `archive-service`: archive payload to MinIO and persist metadata to PostgreSQL
- `evaluation-service`: placeholder internal API surface
- `discord-bot`: slash commands + plain-message frontend with politburo routing
- `n8n`: scheduler/orchestrator calling API workflow endpoints
- `configs/departments/<department_id>/`: filesystem source of truth for each department folder, its soul, department skills, and nested specialist folders

## Storage

- PostgreSQL for operational objects and registry projection tables
- MinIO for archived payload snapshots
- Redis/Qdrant provisioned for future capability expansion

## Interface contracts

- Shared Pydantic contracts in `libs/contracts`
- JSON schemas exported to `libs/contracts/schemas`
- Shared DB models in `libs/db/models.py`
- Registry loader in `libs/registry`
- `execution_records` API surface for recording plan-vs-action evidence before review workflows
- Registry skill manifests now support minimal `functional` runtime metadata in addition to prompt-only skills

## Reliability baseline

- Workflow trace headers: `X-Request-ID`, `X-Chain-Type`, `X-Actor`
- API key segregation: external and internal keys
- Archive write failures returned as retryable 503 with `archive_write_failed`
- `MiniMax` is the online default provider, while `heuristic` remains the offline fallback
- Discord bot now supports HTTP proxy optimization for Clash-style proxies and optional SOCKS proxy support

## Current content baseline

- Six department souls now cover politburo direct dialogue, legislative review, archive governance, task decomposition, intel normalization, and strategy-to-plan orchestration
- Six specialist souls now cover proposal drafting, planning, intraday watch, postclose review, and nightly improvement governance
- Eight seeded skills now cover event parsing, proposal drafting, market scanning, commodity logic, strategy synthesis, planning, execution comparison, and improvement ticket drafting
- National Statistics Bureau also carries `browser_research_skill` and `government_policy_crawl_skill` as the first functional-skill extension for controlled web research and local policy snapshots
- Registry-resolved runtime profiles now derive department skills from folder layout, inherit them into specialists, and include these richer instructions directly in the system prompt
