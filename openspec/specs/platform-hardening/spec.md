## ADDED Requirements

### Requirement: Production-oriented hardening is tracked separately from feature delivery
The project MUST define a platform hardening track that covers validation, observability, deployment checks, and data feedback loops independently from workflow feature completion.

#### Scenario: Hardening work is visible
- **WHEN** a contributor reviews the project plan
- **THEN** they can identify cross-cutting hardening tasks without inferring them from individual workflow notes

### Requirement: Runnable workflows require validation coverage before production-like rollout
The platform SHALL require automated validation for runnable workflow chains before they are treated as ready for production-like environments.

#### Scenario: Validation requirement is explicit
- **WHEN** a workflow is already runnable locally
- **THEN** the hardening plan still requires smoke, integration, or regression coverage before promoting that workflow further

### Requirement: Operational readiness includes observability and feedback capture
The platform MUST require tracing, error visibility, and workflow feedback data capture for research, planning, and review loops that span multiple services.

#### Scenario: Multi-service flows have operational controls
- **WHEN** a workflow crosses API, agent-core, archive, and bot or scheduler boundaries
- **THEN** the hardening plan requires traceability and failure diagnosis mechanisms across those hand-offs

#### Scenario: Review loops require persisted evidence
- **WHEN** a workflow depends on downstream review or improvement
- **THEN** the hardening plan requires persisted execution and evaluation evidence so later chains can run on real records
