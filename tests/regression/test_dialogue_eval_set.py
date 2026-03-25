import json
from pathlib import Path

from apps.api_service.app.agent import dispatch_discord_message
from apps.api_service.app.services.dialogue_chain_service import clarify_dialogue_task


def test_dialogue_eval_set_matches_current_clarification_behavior() -> None:
    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "dialogue_eval_cases.json"
    cases = json.loads(fixture_path.read_text(encoding="utf-8"))

    for case in cases:
        decision = dispatch_discord_message(case["prompt"])
        assert decision.route == case["expected_route"]

        if case["expected_route"] == "governed_dialogue":
            clarified = clarify_dialogue_task(case["prompt"])
            assert clarified.downstream_route == case["expected_downstream_route"]
            assert clarified.source_policy == case["expected_source_policy"]
            assert clarified.requires_research is case["requires_research"]
        else:
            assert case["requires_research"] is False
