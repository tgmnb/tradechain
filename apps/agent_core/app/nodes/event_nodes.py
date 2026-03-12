from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from apps.agent_core.app.llm import get_proposal_generator


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
    generator = get_proposal_generator()
    try:
        proposal = generator.generate(parsed_event=parsed, state=state)
        message = {"node": "draft_proposal", "ok": True, "provider": proposal.get("metadata", {}).get("llm_provider", "unknown")}
    except Exception as exc:  # noqa: BLE001
        fallback = {
            "id": str(uuid4()),
            "source_event_id": parsed.get("event_id"),
            "task_id": state.get("task_id"),
            "theme": parsed.get("title")[:200] if parsed.get("title") else "Untitled Proposal",
            "asset_scope": parsed.get("asset_scope", []),
            "initial_logic": parsed.get("content") or "Initial logic generated from parsed event context.",
            "trigger_conditions": [f"When {parsed.get('event_type', 'event')} impact confirms in price/flow data"],
            "invalidation_conditions": ["If key evidence is contradicted by follow-up disclosures"],
            "risks": ["Headline noise may cause false positives"],
            "confidence": min(max(float(parsed.get("confidence", 0.5)), 0.0), 1.0),
            "status": "draft",
            "recommended_action": "monitor",
            "requires_human": False,
            "metadata": {
                "generated_by": "heuristic_fallback",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "llm_provider": "fallback",
                "fallback_reason": str(exc),
                "schema_version": "1.0.0",
            },
        }
        proposal = fallback
        message = {"node": "draft_proposal", "ok": True, "provider": "fallback", "note": str(exc)}

    return {
        **state,
        "proposal": proposal,
        "current_stage": "proposal_drafted",
        "messages": [*state.get("messages", []), message],
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
