## ADDED Requirements

### Requirement: Improvement ticket has a standard contract
The system MUST define a standard contract for improvement tickets.

#### Scenario: Ticket carries actionable fields
- **WHEN** an improvement ticket is created
- **THEN** it includes target type, target name, issue summary, impact description, root cause, proposed fix, and status

### Requirement: Ticket links to its evidence window
The improvement ticket contract SHALL preserve the source evidence window used to justify the ticket.

#### Scenario: Ticket records source period
- **WHEN** a nightly ticket is generated
- **THEN** it includes the source period or evidence scope that led to the ticket
