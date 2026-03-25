## ADDED Requirements

### Requirement: Each workflow chain has a declared readiness state
The project SHALL classify each major workflow chain by readiness state, including runnable, partial, or blocked, based on operational capability rather than route existence alone.

#### Scenario: Existing runnable workflows are distinguished
- **WHEN** the workflow readiness spec is reviewed
- **THEN** `intel_update`, `daily_preopen`, and other already-runnable chains are identified separately from placeholder or partially implemented chains

#### Scenario: Placeholder workflows are not overstated
- **WHEN** a workflow depends on missing live inputs, review logic, or scoring loops
- **THEN** the readiness spec marks that workflow as partial or blocked and names the missing dependency

### Requirement: Each workflow chain has explicit gate conditions
Every major workflow MUST define the upstream inputs, downstream outputs, and blocking dependencies required for it to be considered ready for the next delivery wave.

#### Scenario: Intraday workflow gate is documented
- **WHEN** a contributor evaluates `intraday_watch`
- **THEN** the spec states that real-time market data and trigger logic are required before the workflow can be considered ready

#### Scenario: Review workflow gate is documented
- **WHEN** a contributor evaluates `postclose_review` or `nightly_improvement`
- **THEN** the spec states the required execution evidence, scoring, and approval-loop dependencies before those workflows count as ready

### Requirement: Readiness planning covers orchestration entrypoints
Workflow readiness planning MUST cover the human and automation entrypoints that invoke the chain, including API endpoints, Discord hand-off, and scheduled orchestration where applicable.

#### Scenario: Entry surfaces are accounted for
- **WHEN** a workflow chain is documented
- **THEN** the spec identifies whether it is invoked through API routes, Discord routing, n8n scheduling, or internal graph calls
