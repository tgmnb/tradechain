from langgraph.graph import END, StateGraph

from apps.agent_core.app.nodes.archive_node import archive_write_node
from apps.agent_core.app.nodes.event_nodes import (
    draft_proposal_node,
    parse_event_node,
    validate_proposal_node,
)
from apps.agent_core.app.nodes.registry_nodes import resolve_profile_node



def build_event_to_proposal_graph():
    graph = StateGraph(dict)

    graph.add_node("resolve_profile", resolve_profile_node)
    graph.add_node("parse_event", parse_event_node)
    graph.add_node("draft_proposal", draft_proposal_node)
    graph.add_node("validate_proposal", validate_proposal_node)
    graph.add_node("archive_write", archive_write_node)

    graph.set_entry_point("resolve_profile")
    graph.add_edge("resolve_profile", "parse_event")
    graph.add_edge("parse_event", "draft_proposal")
    graph.add_edge("draft_proposal", "validate_proposal")
    graph.add_edge("validate_proposal", "archive_write")
    graph.add_edge("archive_write", END)

    return graph.compile()
