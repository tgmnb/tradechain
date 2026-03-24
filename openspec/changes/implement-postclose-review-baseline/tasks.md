## 1. Contracts

- [ ] 1.1 Define the execution evidence minimum-field contract for review consumption.
- [ ] 1.2 Define the structured postclose review output contract.
- [ ] 1.3 Add or map persistence fields needed to store the baseline review result.

## 2. Graph Baseline

- [ ] 2.1 Replace the current `review_graph` placeholder with a minimum runnable comparison path.
- [ ] 2.2 Load the relevant trading plan and execution evidence into the graph state.
- [ ] 2.3 Emit the review result using the standard output contract.

## 3. API Integration

- [ ] 3.1 Update the review entrypoint to enforce the no-evidence or blocked path explicitly.
- [ ] 3.2 Persist and archive successful review results.
- [ ] 3.3 Return the structured review output through the existing workflow surface.

## 4. Verification

- [ ] 4.1 Add a test covering the no-evidence path.
- [ ] 4.2 Add a test covering successful review generation with at least one execution record.
