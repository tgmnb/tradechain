## 1. Inputs

- [x] 1.1 Decide the baseline market input mode: mock-replay, single live source, or both.
- [x] 1.2 Define the minimum market fields required by intraday watch.

## 2. Triggering

- [x] 2.1 Define baseline trigger categories for price, volatility, and volume.
- [x] 2.2 Define throttle and deduplication behavior for repeated triggers.

## 3. Outputs

- [x] 3.1 Define the structured watch observation contract.
- [x] 3.2 Decide which fields are required for downstream routing to Discord, n8n, or research workflows.

## 4. Baseline Implementation

- [x] 4.1 Replace the current blocked placeholder with a baseline watch execution path.
- [x] 4.2 Add tests covering no-input, trigger, and duplicate-suppression paths.
