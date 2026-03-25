## MODIFIED Requirements

### Requirement: Operational readiness includes observability and feedback capture
The platform MUST require tracing, error visibility, and workflow feedback data capture for research, planning, and review loops that span multiple services, and MUST include source governance, replayable dialogue artifacts, and user-facing quality evaluation for the formal dialogue chain.

#### Scenario: Multi-service flows have operational controls
- **WHEN** a workflow crosses API, agent-core, archive, and bot or scheduler boundaries
- **THEN** the hardening plan requires traceability and failure diagnosis mechanisms across those hand-offs

#### Scenario: Review loops require persisted evidence
- **WHEN** a workflow depends on downstream review or improvement
- **THEN** the hardening plan requires persisted execution and evaluation evidence so later chains can run on real records

#### Scenario: Dialogue chain quality is hardened before promotion
- **WHEN** the user-facing dialogue chain is treated as a production-facing capability
- **THEN** the hardening plan requires governed source selection, replayable artifacts, bad-case evaluation coverage, and regression gates before promotion
