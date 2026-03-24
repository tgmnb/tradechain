## ADDED Requirements

### Requirement: Intraday watch consumes controlled market input
The system SHALL run intraday watch against a controlled market data input, using mock-replay or a single supported live source in the baseline version.

#### Scenario: Baseline watch runs with mock-replay
- **WHEN** intraday watch is executed in a local or development environment
- **THEN** it can consume a controlled replay or equivalent non-production input to evaluate watch behavior

### Requirement: Intraday watch emits a reusable observation result
The system MUST produce a structured observation or alert result instead of free-form notification text only.

#### Scenario: Watch emits structured output
- **WHEN** a watch trigger condition is met
- **THEN** the system returns a structured observation payload that can be consumed by downstream notification or research paths
