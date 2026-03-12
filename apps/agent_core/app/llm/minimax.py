from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import httpx

from apps.agent_core.app.config import Settings


class MiniMaxProposalGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, *, parsed_event: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.llm_api_key:
            raise ValueError("llm_api_key is empty")

        response_json = self._chat_completion(parsed_event=parsed_event, state=state)
        proposal = self._normalize(parsed_event=parsed_event, state=state, payload=response_json)
        proposal["metadata"] = {
            **proposal.get("metadata", {}),
            "generated_by": "minimax_proposal_generator",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "llm_provider": "minimax",
            "llm_model": self.settings.llm_model,
            "schema_version": "1.0.0",
        }
        return proposal

    def _chat_completion(self, *, parsed_event: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        body = {
            "model": self.settings.llm_model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an investment research proposal generator. "
                        "Return one JSON object only with keys: "
                        "theme, asset_scope, initial_logic, trigger_conditions, "
                        "invalidation_conditions, risks, confidence, recommended_action, requires_human."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Generate a concise proposal from this event.\n"
                        f"chain_type: {state.get('chain_type', 'intel_update')}\n"
                        f"event: {json.dumps(parsed_event, ensure_ascii=True)}\n"
                        "Rules:\n"
                        "- confidence must be a float between 0 and 1\n"
                        "- asset_scope, trigger_conditions, invalidation_conditions, risks must be arrays of strings\n"
                        "- recommended_action should be one of continue_pipeline, monitor, wait_for_review, manual_review\n"
                        "- requires_human should be boolean\n"
                        "- initial_logic should be short and specific\n"
                    ),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(
            base_url=self.settings.llm_base_url.rstrip("/"),
            timeout=self.settings.llm_timeout_seconds,
            proxy=self.settings.llm_proxy_url or None,
            trust_env=False,
        ) as client:
            response = client.post("/chat/completions", json=body, headers=headers)
            response.raise_for_status()
            payload = response.json()

        content = payload["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("unexpected response content type")
        return _extract_json_object(content)

    def _normalize(self, *, parsed_event: dict[str, Any], state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
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
            "metadata": {},
        }


def _extract_json_object(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return json.loads(candidate)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or start >= end:
        raise ValueError("model did not return a JSON object")
    return json.loads(cleaned[start : end + 1])


def _string_list(value: Any, default: list[str]) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return default
