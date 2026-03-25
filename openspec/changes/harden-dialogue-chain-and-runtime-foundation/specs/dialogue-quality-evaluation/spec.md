## ADDED Requirements

### Requirement: Dialogue chain has a maintained evaluation set
The system MUST maintain a representative evaluation set for the governed dialogue chain, including real user prompts and known bad cases.

#### Scenario: Real bad case enters evaluation set
- **WHEN** a user interaction reveals an obvious dialogue failure
- **THEN** that prompt and its expected behavior can be recorded in the evaluation set for future regression checks

### Requirement: Dialogue chain quality is scored across multiple dimensions
The system SHALL score dialogue-chain quality using at least routing or task-clarification correctness, evidence relevance, structured artifact completeness, and final-answer usefulness.

#### Scenario: Evaluation reports multi-axis quality
- **WHEN** the dialogue chain is evaluated
- **THEN** the result includes separate scores or pass/fail judgments for task clarification, evidence quality, artifact completeness, and reply usefulness

### Requirement: Dialogue updates are gated by regression checks
The system MUST require regression validation before prompts, routing logic, or source-governance rules for the dialogue chain are promoted.

#### Scenario: Dialogue change is blocked by regression failure
- **WHEN** a dialogue-chain change causes evaluation regressions beyond the allowed threshold
- **THEN** the change cannot be treated as ready until the regression is resolved or explicitly approved through governance
