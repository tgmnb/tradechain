from apps.agent_core.app.nodes.event_nodes import validate_proposal_node


def test_requires_human_when_confidence_below_threshold() -> None:
    state = {
        "proposal": {
            "id": "00000000-0000-0000-0000-000000000001",
            "confidence": 0.4,
            "status": "draft",
            "recommended_action": "monitor",
        },
        "messages": [],
    }
    out = validate_proposal_node(state)
    assert out["requires_human"] is True
    assert out["proposal"]["status"] == "pending_review"


def test_no_human_review_when_confidence_high() -> None:
    state = {
        "proposal": {
            "id": "00000000-0000-0000-0000-000000000002",
            "confidence": 0.9,
            "status": "draft",
            "recommended_action": "monitor",
        },
        "messages": [],
    }
    out = validate_proposal_node(state)
    assert out["requires_human"] is False
    assert out["proposal"]["status"] == "draft"
