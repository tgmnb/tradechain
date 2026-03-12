# Master Graph Placeholder

This directory stores exported graph metadata and future orchestration policies.

Current top-level behavior:

- the politburo agent acts as the outer dispatcher for Discord and API natural-language entry points
- direct chat/help and simple query tasks are handled at the top level
- research, analysis, and proposal-generation requests activate downstream workflow chains

The executable research graph implementation for Sprint 1-2 lives in `apps/agent_core/app/graphs/event_to_proposal.py`.
