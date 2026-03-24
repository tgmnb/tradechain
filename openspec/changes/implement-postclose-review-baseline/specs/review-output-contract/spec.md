## ADDED Requirements

### Requirement: Review result has a standard contract
The system MUST define a standard contract for postclose review results.

#### Scenario: Contract is stable
- **WHEN** an internal service, archive path, or later workflow consumes a review result
- **THEN** it receives the result in a consistent structured format rather than free-form text only

### Requirement: Review result captures plan-vs-execution findings
The standard review result SHALL capture the main findings from comparing the trading plan with execution evidence.

#### Scenario: Result contains comparison findings
- **WHEN** a postclose review finishes
- **THEN** the review result includes deviations, issues, and suggested follow-up actions derived from the comparison
