from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class HeuristicProposalGenerator:
    def generate(self, *, parsed_event: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        confidence = min(max(float(parsed_event.get("confidence", 0.5)), 0.0), 1.0)
        profile = state.get("resolved_profile") or {}
        responsibilities = profile.get("responsibilities", [])
        focus = profile.get("focus", [])
        active_skills = profile.get("skill_names", [])

        trigger = f"When {parsed_event.get('event_type', 'event')} impact confirms in price/flow data"
        invalidation = "If key evidence is contradicted by follow-up disclosures"
        risk = "Headline noise may cause false positives"
        logic_suffix = ""
        if responsibilities:
            logic_suffix += f" Active responsibilities: {', '.join(responsibilities[:2])}."
        if focus:
            logic_suffix += f" Current focus: {', '.join(focus[:2])}."

        return {
            "id": str(uuid4()),
            "source_event_id": parsed_event.get("event_id"),
            "task_id": state.get("task_id"),
            "theme": parsed_event.get("title")[:200] if parsed_event.get("title") else "Untitled Proposal",
            "asset_scope": parsed_event.get("asset_scope", []),
            "initial_logic": (parsed_event.get("content") or "Initial logic generated from parsed event context.") + logic_suffix,
            "trigger_conditions": [trigger],
            "invalidation_conditions": [invalidation],
            "risks": [risk],
            "confidence": confidence,
            "status": "draft",
            "recommended_action": "monitor",
            "requires_human": False,
            "metadata": {
                "generated_by": "heuristic_proposal_generator",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "llm_provider": "heuristic",
                "department_id": profile.get("department_id"),
                "specialist_id": profile.get("specialist_id"),
                "active_skills": active_skills,
                "schema_version": "1.0.0",
            },
        }
