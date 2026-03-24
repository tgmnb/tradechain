from apps.agent_core.app.nodes.review_nodes import review_entry_node, synthesize_review_node


def test_review_entry_blocks_without_trading_plan() -> None:
    state = {
        "metadata": {
            "execution_records": [{"id": "1", "action_type": "manual_buy"}],
        },
        "messages": [],
    }

    result = review_entry_node(state)

    assert result["status"] == "blocked"
    assert result["current_stage"] == "review_entry_blocked"
    assert result["messages"][-1]["reason"] == "no_trading_plan"


def test_review_entry_loads_plan_and_records() -> None:
    state = {
        "metadata": {
            "trading_plan": {"id": "plan-1", "title": "Plan"},
            "execution_records": [{"id": "1", "action_type": "manual_buy"}],
        },
        "messages": [],
    }

    result = review_entry_node(state)

    assert result["status"] == "running"
    assert result["trading_plan"]["id"] == "plan-1"
    assert len(result["execution_records"]) == 1


def test_synthesize_review_produces_structured_review() -> None:
    state = {
        "chain_type": "postclose_review",
        "trading_plan": {
            "id": "plan-1",
            "task_id": "task-1",
            "title": "Plan",
            "status": "active",
            "monitoring_points": ["price breakout", "volume"],
            "checklist": ["check 1", "check 2"],
        },
        "execution_records": [
            {
                "id": "1",
                "action_type": "manual_buy",
                "evidence_source": "manual",
                "result": {"price": 101.5},
            }
        ],
        "messages": [],
    }

    result = synthesize_review_node(state)
    review = result["review"]

    assert result["status"] == "completed"
    assert result["current_stage"] == "review_synthesized"
    assert review["trading_plan_id"] == "plan-1"
    assert review["decision"] in {"pass", "reject"}
    assert review["summary"]
    assert review["deviations"]
    assert review["issues"]
    assert review["follow_up_actions"]
    assert review["evidence_summary"]["execution_record_count"] == 1
