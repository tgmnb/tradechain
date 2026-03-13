from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from apps.agent_core.app.config import Settings
from apps.agent_core.app.llm.structured import call_minimax_json


class MiniMaxProposalGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, *, parsed_event: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.llm_api_key:
            raise ValueError("llm_api_key is empty")

        profile = state.get("resolved_profile") or {}
        response_json = self._chat_completion(parsed_event=parsed_event, state=state, profile=profile)
        proposal = self._normalize(parsed_event=parsed_event, state=state, payload=response_json, profile=profile)
        proposal["metadata"] = {
            **proposal.get("metadata", {}),
            "generated_by": "minimax_proposal_generator",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "llm_provider": "minimax",
            "llm_model": self.settings.llm_model,
            "department_id": profile.get("department_id"),
            "specialist_id": profile.get("specialist_id"),
            "active_skills": profile.get("skill_names", []),
            "schema_version": "1.0.0",
        }
        return proposal

    def _chat_completion(self, *, parsed_event: dict[str, Any], state: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
        skill_prompts = "\n\n".join(
            f"Skill {skill['skill_name']}:\n{skill['prompt_template']}" for skill in profile.get("skills", [])
        )
        system_prompt = (
            profile.get("system_prompt")
            or "You are an investment research proposal generator producing one JSON object only."
        )
        if skill_prompts:
            system_prompt = f"{system_prompt}\n\nActive Skill Instructions:\n{skill_prompts}"
        system_prompt += (
            "\n\nReturn one JSON object only with keys: "
            "theme, asset_scope, initial_logic, trigger_conditions, "
            "invalidation_conditions, risks, confidence, recommended_action, requires_human."
        )
        user_prompt = (
            "Generate a concise proposal from this event.\n"
            f"chain_type: {state.get('chain_type', 'intel_update')}\n"
            f"event: {parsed_event}\n"
            "Rules:\n"
            "- confidence must be a float between 0 and 1\n"
            "- asset_scope, trigger_conditions, invalidation_conditions, risks must be arrays of strings\n"
            "- recommended_action should be one of continue_pipeline, monitor, wait_for_review, manual_review\n"
            "- requires_human should be boolean\n"
            "- initial_logic should be short and specific\n"
        )
        return call_minimax_json(settings=self.settings, system_prompt=system_prompt, user_prompt=user_prompt)

    def _normalize(
        self,
        *,
        parsed_event: dict[str, Any],
        state: dict[str, Any],
        payload: dict[str, Any],
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        confidence = min(max(float(payload.get("confidence", parsed_event.get("confidence", 0.5))), 0.0), 1.0)
        recommended_action = str(payload.get("recommended_action") or "wait_for_review")
        requires_human = bool(payload.get("requires_human", confidence < 0.65))

        return {
            "id": str(uuid4()),
            "source_event_id": parsed_event.get("event_id"),
            "task_id": state.get("task_id"),
            "theme": str(payload.get("theme") or parsed_event.get("title") or "Untitled Proposal")[:200],
            "asset_scope": _string_list(payload.get("asset_scope"), parsed_event.get("asset_scope", [])),
            "initial_logic": str(payload.get("initial_logic") or parsed_event.get("content") or "Initial logic generated from event context."),
            "trigger_conditions": _string_list(payload.get("trigger_conditions"), []),
            "invalidation_conditions": _string_list(payload.get("invalidation_conditions"), []),
            "risks": _string_list(payload.get("risks"), []),
            "confidence": confidence,
            "status": "pending_review" if requires_human else "draft",
            "recommended_action": recommended_action,
            "requires_human": requires_human,
            "metadata": {
                "department_id": profile.get("department_id"),
                "specialist_id": profile.get("specialist_id"),
                "active_skills": profile.get("skill_names", []),
            },
        }



def _string_list(value: Any, default: list[str]) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return default
