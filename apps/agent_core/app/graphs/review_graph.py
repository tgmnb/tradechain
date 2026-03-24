from langgraph.graph import END, StateGraph

from apps.agent_core.app.nodes.archive_node import make_archive_node
from apps.agent_core.app.nodes.registry_nodes import resolve_profile_node
from apps.agent_core.app.nodes.review_nodes import review_entry_node, synthesize_review_node


def build_review_graph():
    graph = StateGraph(dict)

    graph.add_node("resolve_profile", resolve_profile_node)
    graph.add_node("review_entry", review_entry_node)
    graph.add_node("synthesize_review", synthesize_review_node)
    graph.add_node("archive_review", make_archive_node(state_key="review", object_type="review"))

    graph.set_entry_point("resolve_profile")
    graph.add_edge("resolve_profile", "review_entry")
    graph.add_edge("review_entry", "synthesize_review")
    graph.add_edge("synthesize_review", "archive_review")
    graph.add_edge("archive_review", END)

    return graph.compile()
