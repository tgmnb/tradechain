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
    "什么是tradechain",
    "什么是 tradechain",
    "甚么是tradechain",
    "甚么是 tradechain",
    "tradechain是什么",
    "tradechain 是什么",
    "政治局",
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
    "intel update",
    "intel_update",
    "情报更新",
    "跑一次intel",
    "跑一下intel",
    "run intel",
    "提案链",
    "生成提案",
    "给我一个提案",
    "做个提案",
)

WEB_RESEARCH_PATTERNS = (
    "search",
    "web",
    "news",
    "policy",
    "latest",
    "查一下",
    "查一查",
    "搜一下",
    "搜一搜",
    "搜索",
    "网页",
    "官网",
    "网站",
    "新闻",
    "消息",
    "政策",
    "最新",
    "帮我看看",
    "帮我查",
    "帮我搜",
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

    if _matches_any(lowered, WEB_RESEARCH_PATTERNS):
        return DispatchDecision(
            route="web_research",
            activate_chain=True,
            summary="Politburo agent escalated this request into the web research workflow.",
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
