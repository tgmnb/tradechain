## ADDED Requirements

### Requirement: Dialogue runtime emits structured artifacts with provenance
The system MUST emit structured runtime artifacts for dialogue intent, evidence, conclusion, and final reply, each with traceable provenance metadata.

#### Scenario: Artifact provenance is retained
- **WHEN** a governed dialogue run executes
- **THEN** every major artifact includes trace identity, generation stage, source references, and version metadata sufficient for replay and audit

### Requirement: Dialogue runtime enforces source governance
The system SHALL evaluate and select evidence sources using explicit governance rules rather than accepting arbitrary web search results.

#### Scenario: Research source is filtered by governance policy
- **WHEN** the dialogue chain gathers external evidence
- **THEN** the runtime applies source allow/deny rules, relevance filtering, and domain-aware query rewriting before evidence is accepted into the answer path

### Requirement: Dialogue runtime archives replayable records
The system MUST persist enough structured data for the 书记处-style archive layer to replay and inspect a governed dialogue run.

#### Scenario: Dialogue run is replayable
- **WHEN** a user-facing answer has been produced
- **THEN** the runtime stores the task brief, evidence bundle, conclusion artifact, and final reply in a form that can be retrieved for review and improvement analysis

### Requirement: Dialogue runtime exposes bounded failure states
The system SHALL classify dialogue failures into explicit states that downstream monitoring and evaluation can inspect.

#### Scenario: Failure state is structured
- **WHEN** clarification, research, or synthesis fails
- **THEN** the runtime records a structured failure state with stage, cause category, and fallback behavior instead of only emitting free-form logs
