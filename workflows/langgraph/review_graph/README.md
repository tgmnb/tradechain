# Review Graph Baseline

Review graph interfaces are exposed at `/internal/graphs/review/run`.

Current baseline behavior:

- consumes one `trading_plan` plus one or more `execution_records`
- rejects the review path when execution evidence is missing
- compares plan monitoring/checklist coverage against current execution evidence
- emits a structured review payload with:
  - `summary`
  - `deviations`
  - `issues`
  - `follow_up_actions`
  - `evidence_summary`
  - `score`
- archives the generated review payload for downstream reuse

Current limitations:

- review synthesis is heuristic and rule-based
- no broker / OMS execution backfill yet
- no nightly scoring or approval loop yet

This baseline is intended to unblock `postclose_review` and prepare inputs for later `nightly_improvement` work.
