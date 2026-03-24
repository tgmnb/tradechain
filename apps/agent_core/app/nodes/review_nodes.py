from datetime import datetime, timezone
from uuid import uuid4


def review_entry_node(state: dict) -> dict:
    metadata = state.get("metadata", {})
    plan = metadata.get("trading_plan") or {}
    records = metadata.get("execution_records") or []
    if not plan:
        return {
            **state,
            "status": "blocked",
            "current_stage": "review_entry_blocked",
            "messages": [*state.get("messages", []), {"node": "review_entry", "ok": False, "reason": "no_trading_plan"}],
        }
    if not records:
        return {
            **state,
            "status": "blocked",
            "current_stage": "review_entry_blocked",
            "messages": [*state.get("messages", []), {"node": "review_entry", "ok": False, "reason": "no_execution_records"}],
        }

    return {
        **state,
        "trading_plan": plan,
        "execution_records": records,
        "status": "running",
        "current_stage": "review_entry_ready",
        "messages": [
            *state.get("messages", []),
            {
                "node": "review_entry",
                "ok": True,
                "execution_record_count": len(records),
            },
        ],
    }


def synthesize_review_node(state: dict) -> dict:
    plan = state.get("trading_plan") or {}
    records = state.get("execution_records") or []

    action_types = [str(record.get("action_type", "")) for record in records if record.get("action_type")]
    evidence_sources = sorted(
        {
            str(record.get("evidence_source") or (record.get("result") or {}).get("evidence_source") or "manual")
            for record in records
        }
    )
    monitoring_points = plan.get("monitoring_points") or []
    checklist = plan.get("checklist") or []
    missing_monitoring = max(0, len(monitoring_points) - len(records))
    checklist_gap = max(0, len(checklist) - len(records))

    deviations: list[str] = []
    issues: list[str] = []
    follow_up_actions: list[str] = []

    if missing_monitoring > 0:
        deviations.append(f"{missing_monitoring} 个监控点尚未在 execution evidence 中体现。")
    if checklist_gap > 0:
        deviations.append(f"{checklist_gap} 个执行清单项缺少对应执行记录。")
    if not any("sell" in action.lower() or "exit" in action.lower() for action in action_types):
        issues.append("当前执行证据未体现退出或止损动作，需要确认是否仍在持仓观察阶段。")
    if len(evidence_sources) == 1 and evidence_sources[0] == "manual":
        issues.append("当前复盘仅依赖手工录入证据，尚未接入自动化执行回流。")

    if not deviations:
        deviations.append("计划中的关键动作与当前执行证据基本对齐。")
    if not issues:
        issues.append("未发现阻塞复盘结论的重大结构化问题。")

    follow_up_actions.extend(
        [
            "补齐与剩余监控点对应的执行或观察证据。",
            "将本次复盘结果归档，并作为 nightly improvement 的输入样本。",
        ]
    )

    score = max(0.0, min(100.0, 85.0 - missing_monitoring * 10.0 - checklist_gap * 5.0 - max(0, len(issues) - 1) * 5.0))
    decision = "pass" if score >= 60 else "reject"
    summary = (
        f"针对交易计划《{plan.get('title') or 'Untitled'}》完成了基线复盘，"
        f"共检查 {len(records)} 条执行证据，识别出 {len(deviations)} 项偏差与 {len(issues)} 项需跟进问题。"
    )

    review = {
        "id": str(uuid4()),
        "trading_plan_id": plan.get("id"),
        "task_id": plan.get("task_id"),
        "reviewer_type": "agent",
        "reviewer_name": "review_graph",
        "decision": decision,
        "summary": summary,
        "deviations": deviations,
        "issues": issues,
        "follow_up_actions": follow_up_actions,
        "evidence_summary": {
            "execution_record_count": len(records),
            "action_types": action_types,
            "evidence_sources": evidence_sources,
        },
        "score": score,
        "metadata": {
            "generated_by": "review_graph_baseline",
            "chain_type": state.get("chain_type", "postclose_review"),
            "plan_status": plan.get("status"),
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {
        **state,
        "review": review,
        "status": "completed",
        "current_stage": "review_synthesized",
        "messages": [
            *state.get("messages", []),
            {
                "node": "synthesize_review",
                "ok": True,
                "decision": decision,
                "score": score,
            },
        ],
    }
