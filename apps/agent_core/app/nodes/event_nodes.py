from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def parse_event_node(state: dict[str, Any]) -> dict[str, Any]:
    event = state.get("event", {})
    parsed = {
        "event_id": event.get("id"),
        "title": event.get("title", ""),
        "event_type": event.get("event_type", "unknown"),
        "asset_scope": event.get("asset_scope", []),
        "impact_direction": event.get("impact_direction", "neutral"),
        "confidence": float(event.get("confidence", 0.5)),
        "content": event.get("content", ""),
    }
    return {
        **state,
        "parsed_event": parsed,
        "current_stage": "parsed_event",
        "messages": [*state.get("messages", []), {"node": "parse_event", "ok": True}],
    }


def draft_proposal_node(state: dict[str, Any]) -> dict[str, Any]:
    parsed = state.get("parsed_event", {})
    confidence = min(max(float(parsed.get("confidence", 0.5)), 0.0), 1.0)

    trigger = f"When {parsed.get('event_type', 'event')} impact confirms in price/flow data"
    invalidation = "If key evidence is contradicted by follow-up disclosures"
    risk = "Headline noise may cause false positives"

    proposal = {
        "id": str(uuid4()),
        "source_event_id": parsed.get("event_id"),
        "task_id": state.get("task_id"),
        "theme": parsed.get("title")[:200] if parsed.get("title") else "Untitled Proposal",
        "asset_scope": parsed.get("asset_scope", []),
        "initial_logic": parsed.get("content") or "Initial logic generated from parsed event context.",
        "trigger_conditions": [trigger],
        "invalidation_conditions": [invalidation],
        "risks": [risk],
        "confidence": confidence,
        "status": "draft",
        "recommended_action": "monitor",
        "requires_human": False,
        "metadata": {
            "generated_by": "event_to_proposal_graph",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0.0",
        },
    }
    return {
        **state,
        "proposal": proposal,
        "current_stage": "proposal_drafted",
        "messages": [*state.get("messages", []), {"node": "draft_proposal", "ok": True}],
    }


def validate_proposal_node(state: dict[str, Any]) -> dict[str, Any]:
    proposal = state.get("proposal", {})
    confidence = float(proposal.get("confidence", 0.5))
    requires_human = confidence < 0.65

    proposal["requires_human"] = requires_human
    proposal["status"] = "pending_review" if requires_human else "draft"
    proposal["recommended_action"] = "manual_review" if requires_human else "continue_pipeline"

    return {
        **state,
        "proposal": proposal,
        "requires_human": requires_human,
        "current_stage": "proposal_validated",
        "messages": [
            *state.get("messages", []),
            {"node": "validate_proposal", "ok": True, "requires_human": requires_human},
        ],
    }
