## ADDED Requirements

### Requirement: Watch observation has a standard contract
The system MUST define a standard contract for intraday watch observations or alerts.

#### Scenario: Observation contract is consumable
- **WHEN** a watch result is produced
- **THEN** it includes asset or scope, trigger type, supporting evidence, severity or priority, and follow-up recommendation fields

### Requirement: Observation output supports downstream routing
The observation contract SHALL allow downstream consumers to decide whether to notify, research, or ignore the watch result.

#### Scenario: Downstream routing decision can be made
- **WHEN** Discord, n8n, or a later workflow receives a watch observation
- **THEN** the payload contains enough structured fields to make a routing decision without reparsing free text
