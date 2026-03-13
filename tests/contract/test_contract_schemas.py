from libs.contracts.event import EventIn
from libs.contracts.graph import GraphRunResponse
from libs.contracts.proposal import ProposalFinal
from libs.contracts.registry import ResolvedAgentProfile, SkillManifest, SoulManifest
from libs.contracts.research import ResearchReport
from libs.contracts.strategy import Strategy
from libs.contracts.task import TaskCreate
from libs.contracts.trading import TradingPlan



def test_task_create_schema_has_required_fields() -> None:
    schema = TaskCreate.model_json_schema()
    required = set(schema.get("required", []))
    assert {"title"}.issubset(required)



def test_event_in_schema_version_default() -> None:
    payload = EventIn(
        source="mock",
        event_type="macro",
        title="headline",
        content="body",
    )
    assert payload.schema_version == "1.0.0"



def test_proposal_final_has_metadata_and_action() -> None:
    schema = ProposalFinal.model_json_schema()
    props = schema.get("properties", {})
    assert "metadata" in props
    assert "recommended_action" in props



def test_graph_response_contains_status_and_profile() -> None:
    schema = GraphRunResponse.model_json_schema()
    props = schema.get("properties", {})
    assert "status" in props
    assert "resolved_profile" in props



def test_registry_and_planning_contracts_expose_expected_fields() -> None:
    assert "skills" in ResolvedAgentProfile.model_json_schema().get("properties", {})
    assert "prompt_template" in SkillManifest.model_json_schema().get("properties", {})
    assert "chain_bindings" in SoulManifest.model_json_schema().get("properties", {})
    assert "summary" in ResearchReport.model_json_schema().get("properties", {})
    assert "priority_score" in Strategy.model_json_schema().get("properties", {})
    assert "monitoring_points" in TradingPlan.model_json_schema().get("properties", {})
