## 1. Inputs

- [ ] 1.1 Decide the baseline market input mode: mock-replay, single live source, or both.
- [ ] 1.2 Define the minimum market fields required by intraday watch.

## 2. Triggering

- [ ] 2.1 Define baseline trigger categories for price, volatility, and volume.
- [ ] 2.2 Define throttle and deduplication behavior for repeated triggers.

## 3. Outputs

- [ ] 3.1 Define the structured watch observation contract.
- [ ] 3.2 Decide which fields are required for downstream routing to Discord, n8n, or research workflows.

## 4. Baseline Implementation

- [ ] 4.1 Replace the current blocked placeholder with a baseline watch execution path.
- [ ] 4.2 Add tests covering no-input, trigger, and duplicate-suppression paths.
