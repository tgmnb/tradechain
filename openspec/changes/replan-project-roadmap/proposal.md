## Why

The repository has moved beyond a bare Sprint 1-2 scaffold: two end-to-end chains are runnable, several workflow branches exist as placeholders, and new registry/policy research capabilities have been added across services. The project now needs a single roadmap artifact that turns scattered progress notes into an execution sequence with clear capability boundaries and delivery gates.

## What Changes

- Define a roadmap capability that organizes the project into delivery waves with explicit outcomes and dependencies.
- Define workflow readiness requirements for `intel_update`, `daily_preopen`, `major_task`, `intraday_watch`, `postclose_review`, and `nightly_improvement`.
- Define platform hardening requirements covering tests, observability, data feedback loops, and deployment readiness before production-like rollout.
- Convert the current status from ad hoc docs into OpenSpec artifacts that can be validated, extended, and tracked in future changes.

## Capabilities

### New Capabilities
- `delivery-roadmap`: Phase the project from current runnable baseline to production-oriented workflow coverage.
- `workflow-readiness`: Define entry criteria, blockers, and completion signals for each workflow chain.
- `platform-hardening`: Define cross-cutting engineering requirements for reliability, validation, and operations.

### Modified Capabilities

None.

## Impact

Affected systems include `apps/api_service`, `apps/agent_core`, `apps/discord_bot`, `apps/ingestion_service`, `apps/archive_service`, `libs/contracts`, `libs/db`, `libs/registry`, workflow definitions under `workflows/`, operational docs under `docs/`, and local developer workflow through the new OpenSpec tooling entrypoint.
