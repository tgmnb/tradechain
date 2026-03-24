## ADDED Requirements

### Requirement: Watch triggering has explicit rules
The system SHALL define explicit watch trigger rules for baseline market observation.

#### Scenario: Trigger rule is evaluated
- **WHEN** market input is processed
- **THEN** the system evaluates configured price, volatility, or volume-related conditions before emitting an observation

### Requirement: Watch triggering enforces throttle or deduplication
The system MUST prevent repeated equivalent observations from being emitted without throttle or deduplication control.

#### Scenario: Duplicate trigger is suppressed
- **WHEN** the same watch condition fires repeatedly within a configured suppression window
- **THEN** the system suppresses or merges duplicate observations
