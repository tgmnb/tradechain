## ADDED Requirements

### Requirement: Project roadmap is organized by delivery wave
The project SHALL define delivery waves that reflect dependency order from the current runnable baseline to production-oriented operation, rather than relying on outdated sprint labels.

#### Scenario: Roadmap defines immediate next wave
- **WHEN** a contributor reads the delivery roadmap
- **THEN** the roadmap identifies the next delivery wave after the current baseline and states the outcomes that must be completed in that wave

#### Scenario: Roadmap defines later waves
- **WHEN** a contributor reviews the roadmap end to end
- **THEN** the roadmap shows subsequent waves for workflow completion and platform readiness with clear separation between them

### Requirement: Each delivery wave states exit criteria
Each delivery wave MUST declare objective exit criteria that can be used to decide whether the next wave should start.

#### Scenario: Exit criteria are explicit
- **WHEN** a delivery wave is documented
- **THEN** it includes concrete completion signals such as runnable workflows, real data dependencies, validation coverage, or operational checks

### Requirement: Roadmap ties work to concrete repository areas
The roadmap MUST map each wave to the repository areas most affected by that wave.

#### Scenario: Roadmap identifies code and workflow surfaces
- **WHEN** a contributor scopes work from the roadmap
- **THEN** the roadmap references the relevant services, libraries, workflow definitions, and docs that are expected to change
