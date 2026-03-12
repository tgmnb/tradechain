# ADR-0001: Sprint 1-2 Foundation Stack

- Status: Accepted
- Date: 2026-03-12

## Context

The project needs a fast, extensible, and governance-friendly baseline to implement Sprint 1-2 with minimum loop delivery.

## Decision

1. Use all-Python service stack for Sprint 1-2.
2. Use FastAPI for service APIs and SQLAlchemy + Alembic for data layer.
3. Use LangGraph in `agent-core` for event->proposal state machine.
4. Use Discord slash commands as first interaction channel.
5. Use n8n workflows as orchestration wrappers around API workflow endpoints.
6. Use mock ingestion adapters in Sprint 2 while preserving a provider interface.

## Consequences

- Faster initial implementation and shared typing/contracts.
- Lower integration risk for early closed-loop demos.
- Real data connectors and advanced graphs deferred to next sprints.
- Contract-first foundation reduces rework when adding new departments and skills.
