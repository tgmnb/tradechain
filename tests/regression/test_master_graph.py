from apps.agent_core.app.graphs.master_graph import build_master_graph


def test_master_graph_builds_governance_handoff() -> None:
    graph = build_master_graph()

    result = graph.invoke(
        {
            "chain_type": "major_task",
            "metadata": {
                "task": {
                    "id": "task-1",
                    "title": "Review soybean setup",
                    "priority": 55,
                    "goal_json": {"text": "Clarify whether soybean weather risk should enter strategy maintenance."},
                    "context_json": {"discord_user_name": "tester"},
                }
            },
            "messages": [],
        }
    )

    assert result["goal_brief"]["title"] == "Review soybean setup"
    assert result["goal_review"]["decision"] == "pass"
    assert result["execution_entry"]["next_stage"] == "proposal_generation"
    assert any(msg["node"] == "politburo_intake" for msg in result["messages"])
