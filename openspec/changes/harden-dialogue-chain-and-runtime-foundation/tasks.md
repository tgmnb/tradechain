## 1. Runtime Foundation

- [x] 1.1 Define the structured runtime artifacts for dialogue intent, evidence bundle, conclusion draft, final reply, and failure state.
- [x] 1.2 Add persistence and archive wiring so secretary-style records can store and retrieve dialogue artifacts with trace and version metadata.
- [x] 1.3 Add source-governance configuration and query-rewrite hooks for macro, policy, and market research prompts.

## 2. Flagship Dialogue Chain

- [x] 2.1 Replace keyword-only top-level routing with a governed task-clarification step for the politburo dialogue entry.
- [x] 2.2 Implement the staged dialogue execution path: clarification, downstream research delegation, evidence synthesis, and user reply generation.
- [x] 2.3 Ensure the final user response no longer exposes raw workflow route/task dumps when a governed answer can be synthesized.
- [x] 2.4 Add bounded fallback behavior for weak evidence, low-trust sources, and downstream execution failures.

## 3. Evaluation and Hardening

- [ ] 3.1 Create a dialogue-chain evaluation set from real prompts, including current known bad cases.
- [ ] 3.2 Add regression checks for task clarification quality, evidence relevance, artifact completeness, and final-answer usefulness.
- [ ] 3.3 Add replay and observability tooling for dialogue runs so failures can be inspected end to end.

## 4. Rollout Sequence

- [ ] 4.1 Introduce the governed dialogue chain behind a controlled rollout path that can fall back to the current baseline routes.
- [ ] 4.2 Update local runbooks, readiness docs, and follow-on planning to treat the dialogue chain as the primary production-facing quality gate.
