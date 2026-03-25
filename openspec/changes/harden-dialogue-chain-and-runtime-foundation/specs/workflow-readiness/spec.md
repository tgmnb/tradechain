## MODIFIED Requirements

### Requirement: Each workflow chain has a declared readiness state
The project SHALL classify each major workflow chain by readiness state, including runnable, partial, or blocked, based on operational capability rather than route existence alone, and SHALL treat the formal user-facing dialogue chain as a first-class readiness target rather than a thin wrapper over baseline workflows.

#### Scenario: Existing runnable workflows are distinguished
- **WHEN** the workflow readiness spec is reviewed
- **THEN** `intel_update`, `daily_preopen`, and other already-runnable chains are identified separately from placeholder or partially implemented chains

#### Scenario: Placeholder workflows are not overstated
- **WHEN** a workflow depends on missing live inputs, review logic, or scoring loops
- **THEN** the readiness spec marks that workflow as partial or blocked and names the missing dependency

#### Scenario: Dialogue chain has explicit readiness status
- **WHEN** the team evaluates the user-facing dialogue path
- **THEN** readiness is judged by task clarification quality, governed research execution, structured artifact output, and final answer quality rather than by route availability alone
