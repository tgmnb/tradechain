## ADDED Requirements

### Requirement: Execution evidence has minimum reviewable fields
Execution evidence used by postclose review MUST include enough structured information to identify what action occurred, who recorded it, and what result was observed.

#### Scenario: Evidence satisfies minimum fields
- **WHEN** an execution evidence record is accepted for review
- **THEN** it includes at least the related trading plan identifier, action type, recorded source or actor, and a result payload or note describing the observed outcome

### Requirement: Execution evidence source is traceable
The system SHALL preserve the source of execution evidence so review consumers can distinguish manual entry from future automated ingestion.

#### Scenario: Source is recorded
- **WHEN** an execution evidence record is created
- **THEN** the system stores source metadata that can be referenced by the review result
