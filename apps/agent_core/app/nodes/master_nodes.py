from __future__ import annotations

from typing import Any

from libs.registry import load_registry


def politburo_intake_node(state: dict[str, Any]) -> dict[str, Any]:
    task = (state.get("metadata") or {}).get("task") or {}
    registry = load_registry()
    profile = registry.resolve_agent_profile(
        chain_type="direct_dialogue",
        department_id="politburo",
        specialist_id="chairman_officer",
    )

    goal_brief = {
        "title": task.get("title") or "Untitled major task",
        "goal": (task.get("goal_json") or {}).get("text") or "待补充目标",
        "priority": task.get("priority", 50),
        "constraints": _constraints_from_task(task),
    }

    return {
        **state,
        "goal_brief": goal_brief,
        "politburo_profile": profile.model_dump(mode="json"),
        "current_stage": "politburo_intake_completed",
        "messages": [
            *state.get("messages", []),
            {
                "node": "politburo_intake",
                "ok": True,
                "department_id": profile.department_id,
                "specialist_id": profile.specialist_id,
                "goal_title": goal_brief["title"],
            },
        ],
    }


def npc_review_node(state: dict[str, Any]) -> dict[str, Any]:
    goal_brief = state.get("goal_brief") or {}
    registry = load_registry()
    profile = registry.resolve_agent_profile(
        chain_type="major_task",
        department_id="national_peoples_congress",
        specialist_id="review_clerk",
    )

    passed = bool(goal_brief.get("title")) and bool(goal_brief.get("goal"))
    review = {
        "decision": "pass" if passed else "reject",
        "reason": "目标已具备最小标题与目标描述" if passed else "目标标题或目标描述缺失",
        "review_dimensions": ["合理性", "一致性", "可衡量性"],
    }

    return {
        **state,
        "goal_review": review,
        "npc_profile": profile.model_dump(mode="json"),
        "requires_human": not passed,
        "current_stage": "npc_review_completed",
        "messages": [
            *state.get("messages", []),
            {
                "node": "npc_review",
                "ok": passed,
                "decision": review["decision"],
            },
        ],
    }


def state_council_entry_node(state: dict[str, Any]) -> dict[str, Any]:
    task = (state.get("metadata") or {}).get("task") or {}
    goal_brief = state.get("goal_brief") or {}
    review = state.get("goal_review") or {}
    registry = load_registry()
    profile = registry.resolve_agent_profile(
        chain_type="major_task",
        department_id="state_council",
        specialist_id="proposal_officer",
    )

    execution_entry = {
        "task_id": task.get("id"),
        "goal_title": goal_brief.get("title"),
        "next_stage": "proposal_generation" if review.get("decision") == "pass" else "goal_revision",
        "department_id": profile.department_id,
        "specialist_id": profile.specialist_id,
    }

    return {
        **state,
        "state_council_profile": profile.model_dump(mode="json"),
        "execution_entry": execution_entry,
        "current_stage": "state_council_entry_completed",
        "messages": [
            *state.get("messages", []),
            {
                "node": "state_council_entry",
                "ok": True,
                "next_stage": execution_entry["next_stage"],
            },
        ],
    }


def _constraints_from_task(task: dict[str, Any]) -> list[str]:
    context = task.get("context_json") or {}
    constraints: list[str] = []
    if context.get("discord_channel_id"):
        constraints.append("来源于 Discord 渠道请求")
    if context.get("discord_user_name"):
        constraints.append(f"发起人：{context['discord_user_name']}")
    if not constraints:
        constraints.append("按默认 major_task 治理流程处理")
    return constraints
