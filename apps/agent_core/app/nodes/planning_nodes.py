from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from apps.agent_core.app.config import get_settings
from apps.agent_core.app.llm.structured import call_minimax_json


END_NODE = "__end__"



def planning_entry_node(state: dict[str, Any]) -> dict[str, Any]:
    return {
        **state,
        "current_stage": "planning_entry",
        "messages": [*state.get("messages", []), {"node": "planning_entry", "ok": True}],
    }



def route_planning_entry(state: dict[str, Any]) -> str:
    if state.get("strategy"):
        return "draft_trading_plan"
    if state.get("research_report"):
        return "draft_strategy"
    return "draft_research_report"



def draft_research_report_node(state: dict[str, Any]) -> dict[str, Any]:
    proposal = state.get("proposal", {})
    profile = state.get("resolved_profile") or {}
    settings = get_settings()

    try:
        report = _build_research_report_with_provider(settings=settings, proposal=proposal, profile=profile, state=state)
        provider = report.get("metadata", {}).get("llm_provider", "heuristic")
        message = {"node": "draft_research_report", "ok": True, "provider": provider}
    except Exception as exc:  # noqa: BLE001
        report = _build_research_report_fallback(proposal=proposal, profile=profile, state=state, note=str(exc))
        message = {"node": "draft_research_report", "ok": True, "provider": "fallback", "note": str(exc)}

    return {
        **state,
        "research_report": report,
        "current_stage": "research_report_drafted",
        "messages": [*state.get("messages", []), message],
    }



def draft_strategy_node(state: dict[str, Any]) -> dict[str, Any]:
    proposal = state.get("proposal", {})
    report = state.get("research_report", {})
    profile = state.get("resolved_profile") or {}
    settings = get_settings()

    try:
        strategy = _build_strategy_with_provider(settings=settings, proposal=proposal, report=report, profile=profile, state=state)
        provider = strategy.get("metadata", {}).get("llm_provider", "heuristic")
        message = {"node": "draft_strategy", "ok": True, "provider": provider}
    except Exception as exc:  # noqa: BLE001
        strategy = _build_strategy_fallback(proposal=proposal, report=report, profile=profile, state=state, note=str(exc))
        message = {"node": "draft_strategy", "ok": True, "provider": "fallback", "note": str(exc)}

    return {
        **state,
        "strategy": strategy,
        "current_stage": "strategy_drafted",
        "messages": [*state.get("messages", []), message],
    }



def draft_trading_plan_node(state: dict[str, Any]) -> dict[str, Any]:
    strategy = state.get("strategy", {})
    profile = state.get("resolved_profile") or {}
    settings = get_settings()

    try:
        plan = _build_plan_with_provider(settings=settings, strategy=strategy, profile=profile, state=state)
        provider = plan.get("metadata", {}).get("llm_provider", "heuristic")
        message = {"node": "draft_trading_plan", "ok": True, "provider": provider}
    except Exception as exc:  # noqa: BLE001
        plan = _build_plan_fallback(strategy=strategy, profile=profile, state=state, note=str(exc))
        message = {"node": "draft_trading_plan", "ok": True, "provider": "fallback", "note": str(exc)}

    return {
        **state,
        "trading_plan": plan,
        "current_stage": "trading_plan_drafted",
        "messages": [*state.get("messages", []), message],
    }



def route_after_research(state: dict[str, Any]) -> str:
    return END_NODE if state.get("stop_after") == "research" else "draft_strategy"



def route_after_strategy(state: dict[str, Any]) -> str:
    return END_NODE if state.get("stop_after") == "strategy" else "draft_trading_plan"



def _build_research_report_with_provider(
    *,
    settings,
    proposal: dict[str, Any],
    profile: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    if settings.llm_provider.strip().lower() != "minimax" or not settings.llm_api_key:
        return _build_research_report_fallback(proposal=proposal, profile=profile, state=state)

    payload = call_minimax_json(
        settings=settings,
        system_prompt=_compose_system_prompt(profile, expected_keys=["title", "summary", "key_points", "risk_points", "next_actions", "confidence"]),
        user_prompt=(
            "Write a compact research report JSON from this proposal.\n"
            f"proposal: {proposal}\n"
            "Rules:\n"
            "- key_points, risk_points, next_actions are arrays of strings\n"
            "- confidence is a float between 0 and 1\n"
            "- summary should be concise and decision-oriented\n"
        ),
    )
    return {
        "id": str(uuid4()),
        "proposal_id": proposal.get("id"),
        "task_id": state.get("task_id") or proposal.get("task_id"),
        "department_id": profile.get("department_id"),
        "specialist_id": profile.get("specialist_id"),
        "title": str(payload.get("title") or f"{proposal.get('theme', 'Untitled')} 研究摘要")[:200],
        "summary": str(payload.get("summary") or proposal.get("initial_logic") or ""),
        "key_points": _string_list(payload.get("key_points"), [proposal.get("initial_logic", "")]),
        "risk_points": _string_list(payload.get("risk_points"), proposal.get("risks", [])),
        "next_actions": _string_list(payload.get("next_actions"), ["继续跟踪触发条件与确认信号"]),
        "confidence": _bounded_confidence(payload.get("confidence", proposal.get("confidence", 0.5))),
        "metadata": _base_metadata(profile, provider="minimax", generated_by="minimax_research_report_generator"),
        "schema_version": "1.0.0",
    }



def _build_research_report_fallback(
    *,
    proposal: dict[str, Any],
    profile: dict[str, Any],
    state: dict[str, Any],
    note: str | None = None,
) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "proposal_id": proposal.get("id"),
        "task_id": state.get("task_id") or proposal.get("task_id"),
        "department_id": profile.get("department_id"),
        "specialist_id": profile.get("specialist_id"),
        "title": f"{proposal.get('theme', 'Untitled')} 研究摘要"[:200],
        "summary": (
            f"{profile.get('department_name', '研究部门')}围绕议案主题“{proposal.get('theme', '未命名主题')}”形成初步研究摘要，"
            f"核心逻辑为：{proposal.get('initial_logic', '待补充')}"
        ),
        "key_points": _unique_list([
            proposal.get("initial_logic", ""),
            *(proposal.get("trigger_conditions", [])[:2]),
            *(profile.get("focus", [])[:2]),
        ]),
        "risk_points": _unique_list(proposal.get("risks", []) or ["需要等待更多确认信号"]),
        "next_actions": _unique_list([
            "跟踪触发条件的兑现情况",
            "确认是否进入策略排序",
            *(profile.get("responsibilities", [])[:1]),
        ]),
        "confidence": _bounded_confidence(proposal.get("confidence", 0.5)),
        "metadata": {
            **_base_metadata(profile, provider="heuristic", generated_by="heuristic_research_report_generator"),
            **({"fallback_reason": note} if note else {}),
        },
        "schema_version": "1.0.0",
    }



def _build_strategy_with_provider(
    *,
    settings,
    proposal: dict[str, Any],
    report: dict[str, Any],
    profile: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    if settings.llm_provider.strip().lower() != "minimax" or not settings.llm_api_key:
        return _build_strategy_fallback(proposal=proposal, report=report, profile=profile, state=state)

    payload = call_minimax_json(
        settings=settings,
        system_prompt=_compose_system_prompt(profile, expected_keys=["title", "thesis", "target_assets", "setup_conditions", "invalidation_conditions", "risk_controls", "confidence", "priority_score"]),
        user_prompt=(
            "Generate a strategy JSON from this research report and proposal.\n"
            f"proposal: {proposal}\n"
            f"research_report: {report}\n"
            "Rules:\n"
            "- target_assets, setup_conditions, invalidation_conditions, risk_controls are arrays of strings\n"
            "- confidence is a float between 0 and 1\n"
            "- priority_score is a number between 0 and 100\n"
        ),
    )
    return {
        "id": str(uuid4()),
        "proposal_id": proposal.get("id"),
        "research_report_id": report.get("id"),
        "task_id": state.get("task_id") or proposal.get("task_id"),
        "title": str(payload.get("title") or f"{proposal.get('theme', 'Untitled')} 策略草案")[:200],
        "thesis": str(payload.get("thesis") or report.get("summary") or proposal.get("initial_logic") or ""),
        "target_assets": _string_list(payload.get("target_assets"), proposal.get("asset_scope", [])),
        "setup_conditions": _string_list(payload.get("setup_conditions"), proposal.get("trigger_conditions", [])),
        "invalidation_conditions": _string_list(payload.get("invalidation_conditions"), proposal.get("invalidation_conditions", [])),
        "risk_controls": _string_list(payload.get("risk_controls"), report.get("risk_points", [])),
        "confidence": _bounded_confidence(payload.get("confidence", report.get("confidence", 0.5))),
        "priority_score": _bounded_priority(payload.get("priority_score", report.get("confidence", 0.5) * 100)),
        "status": "draft",
        "metadata": _base_metadata(profile, provider="minimax", generated_by="minimax_strategy_generator"),
        "schema_version": "1.0.0",
    }



def _build_strategy_fallback(
    *,
    proposal: dict[str, Any],
    report: dict[str, Any],
    profile: dict[str, Any],
    state: dict[str, Any],
    note: str | None = None,
) -> dict[str, Any]:
    confidence = _bounded_confidence(report.get("confidence", proposal.get("confidence", 0.5)))
    return {
        "id": str(uuid4()),
        "proposal_id": proposal.get("id"),
        "research_report_id": report.get("id"),
        "task_id": state.get("task_id") or proposal.get("task_id"),
        "title": f"{proposal.get('theme', 'Untitled')} 策略草案"[:200],
        "thesis": report.get("summary") or proposal.get("initial_logic") or "",
        "target_assets": proposal.get("asset_scope", []),
        "setup_conditions": _unique_list([*proposal.get("trigger_conditions", []), *report.get("key_points", [])[:1]]),
        "invalidation_conditions": _unique_list(proposal.get("invalidation_conditions", []) or report.get("risk_points", [])[:2]),
        "risk_controls": _unique_list(report.get("risk_points", [])[:2] or ["若关键验证失败则停止推进"]),
        "confidence": confidence,
        "priority_score": _bounded_priority(confidence * 100),
        "status": "draft",
        "metadata": {
            **_base_metadata(profile, provider="heuristic", generated_by="heuristic_strategy_generator"),
            **({"fallback_reason": note} if note else {}),
        },
        "schema_version": "1.0.0",
    }



def _build_plan_with_provider(*, settings, strategy: dict[str, Any], profile: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    if settings.llm_provider.strip().lower() != "minimax" or not settings.llm_api_key:
        return _build_plan_fallback(strategy=strategy, profile=profile, state=state)

    payload = call_minimax_json(
        settings=settings,
        system_prompt=_compose_system_prompt(profile, expected_keys=["title", "objective", "entry_conditions", "exit_conditions", "monitoring_points", "checklist"]),
        user_prompt=(
            "Generate a trading plan JSON from this strategy.\n"
            f"strategy: {strategy}\n"
            "Rules:\n"
            "- entry_conditions, exit_conditions, monitoring_points, checklist are arrays of strings\n"
            "- avoid auto-execution wording\n"
        ),
    )
    return {
        "id": str(uuid4()),
        "strategy_id": strategy.get("id"),
        "task_id": state.get("task_id") or strategy.get("task_id"),
        "plan_date": _plan_date(state),
        "title": str(payload.get("title") or f"{strategy.get('title', 'Untitled')} 盘前计划")[:200],
        "objective": str(payload.get("objective") or strategy.get("thesis") or ""),
        "entry_conditions": _string_list(payload.get("entry_conditions"), strategy.get("setup_conditions", [])),
        "exit_conditions": _string_list(payload.get("exit_conditions"), strategy.get("invalidation_conditions", [])),
        "monitoring_points": _string_list(payload.get("monitoring_points"), _default_monitoring_points(strategy)),
        "checklist": _string_list(payload.get("checklist"), _default_checklist()),
        "status": "draft",
        "metadata": _base_metadata(profile, provider="minimax", generated_by="minimax_plan_generator"),
        "schema_version": "1.0.0",
    }



def _build_plan_fallback(
    *,
    strategy: dict[str, Any],
    profile: dict[str, Any],
    state: dict[str, Any],
    note: str | None = None,
) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "strategy_id": strategy.get("id"),
        "task_id": state.get("task_id") or strategy.get("task_id"),
        "plan_date": _plan_date(state),
        "title": f"{strategy.get('title', 'Untitled')} 盘前计划"[:200],
        "objective": strategy.get("thesis") or "执行策略草案并跟踪关键验证点",
        "entry_conditions": strategy.get("setup_conditions", []),
        "exit_conditions": strategy.get("invalidation_conditions", []),
        "monitoring_points": _default_monitoring_points(strategy),
        "checklist": _default_checklist(),
        "status": "draft",
        "metadata": {
            **_base_metadata(profile, provider="heuristic", generated_by="heuristic_plan_generator"),
            **({"fallback_reason": note} if note else {}),
        },
        "schema_version": "1.0.0",
    }



def _compose_system_prompt(profile: dict[str, Any], *, expected_keys: list[str]) -> str:
    skill_prompts = "\n\n".join(
        f"Skill {skill['skill_name']}:\n{skill['prompt_template']}" for skill in profile.get("skills", [])
    )
    base = profile.get("system_prompt") or "You are a structured investment research agent."
    if skill_prompts:
        base = f"{base}\n\nActive Skill Instructions:\n{skill_prompts}"
    return f"{base}\n\nReturn one JSON object only with keys: {', '.join(expected_keys)}."



def _base_metadata(profile: dict[str, Any], *, provider: str, generated_by: str) -> dict[str, Any]:
    return {
        "generated_by": generated_by,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "llm_provider": provider,
        "department_id": profile.get("department_id"),
        "specialist_id": profile.get("specialist_id"),
        "active_skills": profile.get("skill_names", []),
    }



def _default_monitoring_points(strategy: dict[str, Any]) -> list[str]:
    assets = strategy.get("target_assets", [])
    if assets:
        return [f"跟踪 {asset} 的价格、量能与消息验证" for asset in assets[:3]]
    return ["跟踪价格确认", "跟踪量能变化", "跟踪后续消息验证"]



def _default_checklist() -> list[str]:
    return ["确认触发条件是否成立", "记录盘中偏离与处理", "盘后复核执行结果"]



def _plan_date(state: dict[str, Any]) -> str:
    metadata = state.get("metadata", {})
    plan_date = metadata.get("plan_date")
    if plan_date:
        return str(plan_date)
    return date.today().isoformat()



def _bounded_confidence(value: Any) -> float:
    return min(max(float(value), 0.0), 1.0)



def _bounded_priority(value: Any) -> float:
    return min(max(float(value), 0.0), 100.0)



def _string_list(value: Any, default: list[str]) -> list[str]:
    if isinstance(value, list):
        return _unique_list([str(item) for item in value if str(item).strip()])
    return _unique_list(default)



def _unique_list(values: list[str]) -> list[str]:
    items: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in items:
            items.append(text)
    return items
