from langgraph.graph import END, StateGraph

from apps.agent_core.app.nodes.master_nodes import (
    npc_review_node,
    politburo_intake_node,
    state_council_entry_node,
)


def build_master_graph():
    graph = StateGraph(dict)

    graph.add_node("politburo_intake", politburo_intake_node)
    graph.add_node("npc_review", npc_review_node)
    graph.add_node("state_council_entry", state_council_entry_node)

    graph.set_entry_point("politburo_intake")
    graph.add_edge("politburo_intake", "npc_review")
    graph.add_edge("npc_review", "state_council_entry")
    graph.add_edge("state_council_entry", END)

    return graph.compile()
