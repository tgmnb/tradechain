from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DispatchDecision:
    route: str
    activate_chain: bool
    summary: str


HELP_PATTERNS = (
    "你是谁",
    "你能做什么",
    "怎么用",
    "help",
    "what can you do",
    "who are you",
)

HEALTH_PATTERNS = (
    "health",
    "状态",
    "健康",
    "系统",
    "system health",
)

PROPOSAL_QUERY_PATTERNS = (
    "latest proposal",
    "latest recommendation",
    "最新提案",
    "最新建议",
    "最新提议",
    "最新proposal",
)

RESEARCH_PATTERNS = (
    "intel",
    "research",
    "analyze",
    "analysis",
    "研究",
    "分析",
    "方案",
    "思考",
    "调查",
    "推演",
    "评估",
    "跑一次",
    "run workflow",
    "生成提案",
    "给我一个提案",
    "做个提案",
    "给我结论",
)


def dispatch_discord_message(text: str) -> DispatchDecision:
    lowered = " ".join(text.lower().split())

    if _matches_any(lowered, HELP_PATTERNS):
        return DispatchDecision(
            route="help",
            activate_chain=False,
            summary=(
                "Politburo agent is online. I split requests before activating research chains.\n"
                "Direct queries: health, latest proposal, help.\n"
                "Research requests: intel update, analysis, proposal generation."
            ),
        )

    if _matches_any(lowered, HEALTH_PATTERNS):
        return DispatchDecision(
            route="health",
            activate_chain=False,
            summary="Politburo agent handled this as a direct health query.",
        )

    if _matches_any(lowered, PROPOSAL_QUERY_PATTERNS):
        return DispatchDecision(
            route="proposal_latest",
            activate_chain=False,
            summary="Politburo agent handled this as a direct proposal query.",
        )

    if _matches_any(lowered, RESEARCH_PATTERNS):
        return DispatchDecision(
            route="intel_update",
            activate_chain=True,
            summary="Politburo agent escalated this request into the research workflow.",
        )

    return DispatchDecision(
        route="chat",
        activate_chain=False,
        summary=(
            "Politburo agent treated this as a direct conversation, so no downstream workflow was started.\n"
            "Ask for `system health`, `latest proposal`, or request research/analysis to activate the pipeline."
        ),
    )


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in text for pattern in patterns)
