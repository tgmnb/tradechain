## Context

Tradechain already has a runnable baseline, but the planning context is fragmented across `README.md`, architecture notes, and dated progress logs. The repository now spans multiple services, multiple workflow families, and a growing config-driven registry model. The immediate problem is no longer "how to bootstrap the repo"; it is "what gets finished next, in what order, and with what gate before the next wave starts".

## Goals / Non-Goals

**Goals:**
- Convert the current status into an explicit roadmap with delivery waves.
- Define measurable workflow readiness gates instead of placeholder labels.
- Separate workflow-specific completion work from cross-cutting platform hardening.
- Make future implementation changes traceable through OpenSpec artifacts.

**Non-Goals:**
- Implement any new production logic in this change.
- Replace existing architecture docs or progress notes.
- Lock the team into exact dates or staffing assumptions.

## Decisions

### 1. Model the replan as three capabilities
The roadmap is split into `delivery-roadmap`, `workflow-readiness`, and `platform-hardening`.

Rationale:
- The project has both vertical concerns (workflow chains) and horizontal concerns (testing, observability, deployment).
- A single monolithic planning spec would blur dependencies and weaken later change tracking.

Alternatives considered:
- One large "project-plan" spec. Rejected because it would be too broad to validate and evolve.
- Service-by-service planning. Rejected because the next delivery risks are workflow and platform driven, not service-local.

### 2. Use delivery waves instead of sprint labels
The roadmap will define waves such as baseline stabilization, workflow completion, and production readiness.

Rationale:
- Existing docs already show scope drift beyond the original Sprint 1-2 framing.
- Waves reflect dependency order better than dated sprint numbers.

Alternatives considered:
- Keep the Sprint 1/2/3 model. Rejected because the current state already overlaps multiple future sprints.

### 3. Treat workflow readiness as gated by real inputs and outputs
Each workflow must define what real data or feedback loop is still missing.

Rationale:
- The main gap is not route exposure; it is absence of real upstream inputs, downstream evidence, or scoring loops.
- This avoids over-counting placeholders as delivered features.

Alternatives considered:
- Define readiness only by API availability. Rejected because several APIs already exist without operational value.

### 4. Keep platform hardening separate from feature completion
Observability, automated tests, data capture, and deployment verification are tracked as first-class requirements.

Rationale:
- Current runnable chains are not the same as production-ready chains.
- Cross-cutting engineering work otherwise gets perpetually deferred behind new workflow features.

Alternatives considered:
- Fold hardening items into each workflow spec. Rejected because many requirements are shared across chains.

## Risks / Trade-offs

- [Roadmap becomes too abstract] -> Mitigation: tie every wave to workflow and platform exit criteria.
- [Specs drift away from actual code] -> Mitigation: reference concrete directories and validate follow-on changes against these specs.
- [Future work still gets prioritized ad hoc] -> Mitigation: use the tasks artifact as the default backlog seed for the next implementation changes.
- [Capability overlap causes ambiguity] -> Mitigation: keep roadmap focused on sequencing, workflow-readiness on chain gates, and platform-hardening on horizontal controls.

## Migration Plan

1. Initialize OpenSpec in the repository and keep the config in-repo.
2. Add the replan change with proposal, design, specs, and tasks.
3. Validate the change with OpenSpec CLI.
4. Use this change as the planning baseline for future implementation proposals.

Rollback is low risk: remove the local tooling wrapper and the `openspec/` artifacts if the team chooses a different planning process.

## Open Questions

- Which external market data source should back `intraday_watch` in the next implementation wave?
- Which system becomes the source of truth for execution records in review workflows?
- Whether `policy_watch` should remain API-service owned or move into a dedicated ingestion/research path.
