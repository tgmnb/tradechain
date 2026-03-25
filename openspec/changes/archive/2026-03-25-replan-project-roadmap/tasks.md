## 1. Baseline Alignment

- [x] 1.1 Confirm the current runnable workflows and placeholder workflows against the latest code paths in `apps/` and `workflows/`.
- [x] 1.2 Translate the current state into a delivery-wave summary in the architecture and planning docs.

## 2. Workflow Completion Wave

- [x] 2.1 Decide the live data and trigger approach for `intraday_watch`.
- [x] 2.2 Define the real execution record ingestion source for `postclose_review`.
- [x] 2.3 Design the scoring, ticketing, and approval chain required for `nightly_improvement`.
- [x] 2.4 Verify Discord, API, and n8n entrypoints for every workflow that is expected to run outside local testing.

## 3. Platform Hardening Wave

- [x] 3.1 Add smoke and integration coverage for the currently runnable chains.
- [x] 3.2 Add cross-service observability and failure tracing checks for workflow hand-offs.
- [x] 3.3 Define deployment-readiness checks for provider connectivity, migrations, and archive persistence.

## 4. Adoption

- [x] 4.1 Use this OpenSpec change as the baseline when creating the next implementation proposal.
- [x] 4.2 Archive this change only after the roadmap and readiness criteria are reflected in follow-on implementation work.
