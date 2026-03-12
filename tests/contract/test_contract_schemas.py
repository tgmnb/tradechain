from libs.contracts.event import EventIn
from libs.contracts.graph import GraphRunResponse
from libs.contracts.proposal import ProposalFinal
from libs.contracts.task import TaskCreate


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


def test_graph_response_contains_status() -> None:
    schema = GraphRunResponse.model_json_schema()
    assert "status" in schema.get("properties", {})
