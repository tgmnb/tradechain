from apps.agent_core.app.nodes.planning_nodes import (
    draft_research_report_node,
    draft_strategy_node,
    draft_trading_plan_node,
)



def _base_state() -> dict:
    return {
        "task_id": None,
        "chain_type": "daily_preopen",
        "proposal": {
            "id": "00000000-0000-0000-0000-000000000010",
            "task_id": None,
            "theme": "Soybean weather risk",
            "asset_scope": ["soybean", "meal"],
            "initial_logic": "Drought could tighten supply.",
            "trigger_conditions": ["Weather risk persists"],
            "invalidation_conditions": ["Rainfall normalizes"],
            "risks": ["Headline reversal"],
            "confidence": 0.74,
        },
        "resolved_profile": {
            "department_id": "central_military_commission",
            "department_name": "中央军委",
            "department_soul_id": "central_military_commission",
            "specialist_id": "plan_officer",
            "specialist_name": "计划专员",
            "chain_type": "daily_preopen",
            "mission": "生成计划",
            "responsibilities": ["形成计划"],
            "focus": ["监控清单"],
            "guardrails": ["不自动下单"],
            "style_notes": ["清单化"],
            "tone": "执行导向",
            "skill_names": ["strategy_synthesis_skill", "plan_generation_skill"],
            "skills": [
                {
                    "skill_name": "strategy_synthesis_skill",
                    "version": "v0.1.0",
                    "description": "策略综合",
                    "input_schema": "ResearchReport",
                    "output_schema": "Strategy",
                    "prompt_template": "先风险后动作",
                    "owner_department": "中央军委",
                }
            ],
            "system_prompt": "Structured planning prompt",
        },
        "metadata": {},
        "messages": [],
    }



def test_draft_research_report_node_generates_research_payload() -> None:
    out = draft_research_report_node(_base_state())
    report = out["research_report"]
    assert report["proposal_id"] == "00000000-0000-0000-0000-000000000010"
    assert report["department_id"] == "central_military_commission"
    assert report["key_points"]



def test_draft_strategy_and_plan_nodes_generate_expected_links() -> None:
    state = draft_research_report_node(_base_state())
    state = draft_strategy_node(state)
    strategy = state["strategy"]
    assert strategy["research_report_id"] == state["research_report"]["id"]
    assert strategy["target_assets"] == ["soybean", "meal"]

    state = draft_trading_plan_node(state)
    plan = state["trading_plan"]
    assert plan["strategy_id"] == strategy["id"]
    assert plan["monitoring_points"]
    assert plan["checklist"]
