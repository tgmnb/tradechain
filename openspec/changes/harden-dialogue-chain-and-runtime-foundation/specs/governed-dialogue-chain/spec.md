## ADDED Requirements

### Requirement: Dialogue entry performs governance-style task clarification
The system SHALL transform natural-language user requests into a structured task brief before triggering downstream research or workflow execution.

#### Scenario: Macro question becomes structured task brief
- **WHEN** the user asks a macro research question such as interest-rate direction, policy stance, or market impact
- **THEN** the system produces a structured task brief containing objective, topic scope, constraints, requested output shape, and whether downstream research is required

### Requirement: Dialogue chain orchestrates research through governed execution stages
The system MUST execute the user-facing dialogue chain as a staged flow of clarification, research delegation, evidence synthesis, and final reply generation instead of directly exposing workflow routes.

#### Scenario: Research path is mediated by governance stages
- **WHEN** the clarified task requires external evidence or deeper analysis
- **THEN** the system invokes the appropriate downstream research capability, collects structured evidence, and returns a synthesized answer rather than raw workflow status output

### Requirement: Dialogue chain returns structured answer artifacts and user-facing reply
The system SHALL produce both internal structured artifacts and a final user-facing response for each governed dialogue run.

#### Scenario: User receives answer while system keeps artifacts
- **WHEN** the dialogue chain completes successfully
- **THEN** the system stores structured task, evidence, and conclusion artifacts and returns a concise answer aligned with the clarified objective

### Requirement: Dialogue chain preserves safe fallback behavior
The system MUST degrade safely when research is incomplete, sources are weak, or downstream execution fails.

#### Scenario: Weak evidence triggers bounded fallback
- **WHEN** the dialogue chain cannot gather sufficiently relevant or trusted evidence
- **THEN** the system returns a bounded fallback answer that states uncertainty and avoids presenting low-quality search output as a confident conclusion
