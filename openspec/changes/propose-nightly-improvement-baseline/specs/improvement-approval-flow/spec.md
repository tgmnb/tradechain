## ADDED Requirements

### Requirement: Improvement approval flow is explicit
The system SHALL define explicit statuses and approval transitions for nightly improvement tickets.

#### Scenario: Ticket enters pending approval
- **WHEN** a nightly improvement ticket is created
- **THEN** it enters a pending approval or equivalent review state before any runtime change is applied

### Requirement: Approval flow preserves accountability
The approval flow MUST record who approved or rejected an improvement ticket.

#### Scenario: Approval actor is recorded
- **WHEN** a ticket transitions out of pending approval
- **THEN** the system records the responsible actor or reviewer for that decision
