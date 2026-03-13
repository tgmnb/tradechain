from langgraph.graph import END, StateGraph

from apps.agent_core.app.nodes.archive_node import make_archive_node
from apps.agent_core.app.nodes.planning_nodes import (
    draft_research_report_node,
    draft_strategy_node,
    draft_trading_plan_node,
    planning_entry_node,
    route_after_research,
    route_after_strategy,
    route_planning_entry,
)
from apps.agent_core.app.nodes.registry_nodes import resolve_profile_node



def build_proposal_to_plan_graph():
    graph = StateGraph(dict)

    graph.add_node("resolve_profile", resolve_profile_node)
    graph.add_node("planning_entry", planning_entry_node)
    graph.add_node("draft_research_report", draft_research_report_node)
    graph.add_node("archive_research_report", make_archive_node(state_key="research_report", object_type="research_report"))
    graph.add_node("draft_strategy", draft_strategy_node)
    graph.add_node("archive_strategy", make_archive_node(state_key="strategy", object_type="strategy"))
    graph.add_node("draft_trading_plan", draft_trading_plan_node)
    graph.add_node("archive_trading_plan", make_archive_node(state_key="trading_plan", object_type="trading_plan"))

    graph.set_entry_point("resolve_profile")
    graph.add_edge("resolve_profile", "planning_entry")
    graph.add_conditional_edges(
        "planning_entry",
        route_planning_entry,
        {
            "draft_research_report": "draft_research_report",
            "draft_strategy": "draft_strategy",
            "draft_trading_plan": "draft_trading_plan",
        },
    )
    graph.add_edge("draft_research_report", "archive_research_report")
    graph.add_conditional_edges(
        "archive_research_report",
        route_after_research,
        {
            "draft_strategy": "draft_strategy",
            END: END,
        },
    )
    graph.add_edge("draft_strategy", "archive_strategy")
    graph.add_conditional_edges(
        "archive_strategy",
        route_after_strategy,
        {
            "draft_trading_plan": "draft_trading_plan",
            END: END,
        },
    )
    graph.add_edge("draft_trading_plan", "archive_trading_plan")
    graph.add_edge("archive_trading_plan", END)

    return graph.compile()
