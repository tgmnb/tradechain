## ADDED Requirements

### Requirement: Postclose review runs on trading plan and execution evidence
The system SHALL run a postclose review when a trading plan exists and at least one valid execution evidence record is available for that plan.

#### Scenario: Review runs with valid evidence
- **WHEN** a postclose review request references a trading plan with one or more valid execution evidence records
- **THEN** the system produces a structured review result instead of returning a placeholder response

#### Scenario: Review fails clearly without evidence
- **WHEN** a postclose review request references a trading plan with no valid execution evidence records
- **THEN** the system returns a clear blocked or no-evidence result without attempting full review generation

### Requirement: Review output is structured and reusable
The system MUST produce a structured review output that can be persisted, archived, and consumed by later improvement workflows.

#### Scenario: Review output includes reusable fields
- **WHEN** a postclose review completes successfully
- **THEN** the output includes a summary, key deviations, risks or issues, follow-up suggestions, and metadata about the evidence used

### Requirement: Review graph has a minimum runnable path
The review graph MUST provide a minimum runnable path that compares plan intent with execution evidence and synthesizes a review result.

#### Scenario: Graph performs baseline comparison
- **WHEN** the review graph processes a trading plan and execution evidence
- **THEN** it evaluates plan-vs-execution differences and emits a baseline review result through the standard output contract
