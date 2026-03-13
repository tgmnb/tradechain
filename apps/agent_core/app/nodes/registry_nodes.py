from typing import Any

from libs.registry import load_registry



def resolve_profile_node(state: dict[str, Any]) -> dict[str, Any]:
    metadata = state.get("metadata", {})
    registry = load_registry()
    profile = registry.resolve_agent_profile(
        chain_type=state.get("chain_type", "intel_update"),
        department_id=metadata.get("department_id"),
        specialist_id=metadata.get("specialist_id"),
    )
    return {
        **state,
        "resolved_profile": profile.model_dump(mode="json"),
        "current_stage": "profile_resolved",
        "messages": [
            *state.get("messages", []),
            {
                "node": "resolve_profile",
                "ok": True,
                "department_id": profile.department_id,
                "specialist_id": profile.specialist_id,
                "skill_names": profile.skill_names,
            },
        ],
    }
