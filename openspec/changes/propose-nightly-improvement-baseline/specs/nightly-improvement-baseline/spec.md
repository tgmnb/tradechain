## ADDED Requirements

### Requirement: Nightly improvement consumes historical workflow evidence
The system SHALL run nightly improvement on historical workflow evidence collected from completed proposal, planning, and review activity.

#### Scenario: Nightly run aggregates historical inputs
- **WHEN** a nightly improvement run starts
- **THEN** it loads the configured historical evidence window instead of requiring live workflow execution

### Requirement: Nightly improvement emits improvement tickets
The system MUST emit structured improvement tickets rather than free-form summaries only.

#### Scenario: Ticket is generated
- **WHEN** nightly improvement detects a repeated issue or weak pattern
- **THEN** it produces a structured improvement ticket for downstream approval
