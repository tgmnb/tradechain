from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from libs.contracts.dialogue import EvidenceBundle, EvidenceItem


@dataclass(frozen=True)
class ClarifiedDialogueTask:
    route: str
    downstream_route: str | None
    objective: str
    requested_output: str
    topic_scope: list[str]
    constraints: list[str]
    requires_research: bool
    source_policy: str


def clarify_dialogue_task(text: str) -> ClarifiedDialogueTask:
    normalized = " ".join(text.split())
    lowered = normalized.lower()

    if any(token in lowered for token in ("加降息", "美联储", "联储", "federal reserve", "rate cut", "rate hike", "利率")):
        return ClarifiedDialogueTask(
            route="governed_dialogue",
            downstream_route="web_research",
            objective="Assess the current US interest-rate stance, explain the latest hike/cut direction, and summarize implications.",
            requested_output="macro_briefing",
            topic_scope=["macro", "rates", "federal_reserve"],
            constraints=["prioritize trusted macro-policy sources", "reply in concise Chinese"],
            requires_research=True,
            source_policy="macro_policy",
        )

    if any(token in lowered for token in ("政策", "央行", "官网", "消息", "最新", "research", "分析", "研究", "网页", "search")):
        return ClarifiedDialogueTask(
            route="governed_dialogue",
            downstream_route="web_research",
            objective="Gather trusted external evidence, synthesize the latest developments, and return a structured briefing.",
            requested_output="research_briefing",
            topic_scope=["research"],
            constraints=["prefer trusted official or financial media sources", "reply in concise Chinese"],
            requires_research=True,
            source_policy="general",
        )

    if any(token in lowered for token in ("提案", "intel", "情报更新", "宏观变化", "机会")):
        return ClarifiedDialogueTask(
            route="governed_dialogue",
            downstream_route="intel_update",
            objective="Run the internal proposal-generation workflow and summarize the latest proposal-level conclusion.",
            requested_output="proposal_briefing",
            topic_scope=["proposal_generation"],
            constraints=["summarize recommendation instead of raw workflow output", "reply in concise Chinese"],
            requires_research=True,
            source_policy="general",
        )

    return ClarifiedDialogueTask(
        route="chat",
        downstream_route=None,
        objective="Handle as a direct conversation.",
        requested_output="direct_reply",
        topic_scope=["chat"],
        constraints=[],
        requires_research=False,
        source_policy="general",
    )


def build_evidence_bundle(*, task_id, request_id: str, workflow_result: dict, source_policy: str) -> EvidenceBundle:
    items = [
        EvidenceItem(
            title=str(item.get("title") or "Untitled evidence"),
            url=str(item.get("url") or ""),
            source_domain=urlparse(str(item.get("url") or "")).hostname or "unknown",
            source_type="web",
            trust_level=_trust_level(urlparse(str(item.get("url") or "")).hostname or ""),
            excerpt=str(item.get("excerpt") or ""),
            metadata={},
        )
        for item in workflow_result.get("results", [])
        if item.get("url")
    ]
    return EvidenceBundle(
        id=uuid4(),
        task_id=task_id,
        request_id=request_id,
        query=str(workflow_result.get("query") or ""),
        source_policy=source_policy,
        rewrite_strategy=str(workflow_result.get("rewrite_strategy") or "direct"),
        items=items,
        failure_state=None if items else "no_relevant_evidence",
        metadata={"provider": workflow_result.get("provider"), "result_count": workflow_result.get("result_count", len(items))},
        created_at=datetime.now(timezone.utc),
    )


def synthesize_governed_answer(*, text: str, clarified: ClarifiedDialogueTask, workflow_result: dict) -> tuple[str, dict[str, Any]]:
    if clarified.downstream_route == "web_research":
        results = workflow_result.get("results", [])
        if not results:
            return (
                "我已经按宏观研究链尝试检索，但当前没有拿到足够可信的材料，先不直接下结论。建议下一步优先检查美联储官网、议息声明和主流财经媒体的最新表述。",
                {
                    "fallback_used": True,
                    "failure_stage": "research",
                    "key_points": [],
                    "risks": ["当前证据不足，直接结论可能误导"],
                    "confidence": 0.2,
                    "evidence_refs": [],
                },
            )

        top = results[0]
        source_domain = urlparse(str(top.get("url") or "")).hostname or "unknown"
        answer = (
            f"我先按“{clarified.objective}”整理了这次问题。"
            f"当前最可信的线索来自 {source_domain}，核心信息是：{_clean_excerpt(str(top.get('excerpt') or ''))}。"
        )
        if "加降息" in text or "利率" in text or "美联储" in text:
            answer += " 就当前基线判断，更应该先回答“最近的政策表述和市场预期是什么”，而不是直接把网页结果堆给你。"
        answer += " 如果你要，我下一步应该继续把它整理成“最新表态、市场定价、可能影响”三段式结论。"
        return (
            answer,
            {
                "fallback_used": False,
                "failure_stage": None,
                "key_points": [str(top.get("title") or "top evidence"), _clean_excerpt(str(top.get("excerpt") or ""))],
                "risks": ["网页证据仍需要进一步交叉验证"],
                "confidence": 0.55,
                "evidence_refs": [str(top.get("url") or "")],
            },
        )

    proposal = workflow_result.get("proposal") or {}
    if proposal:
        answer = (
            f"我已经按研究链推进，并拿到了一个可继续处理的提案。"
            f" 当前主题是“{proposal.get('theme', '未知主题')}”，建议动作是 {proposal.get('recommended_action', 'wait_for_review')}。"
        )
        return (
            answer,
            {
                "fallback_used": False,
                "failure_stage": None,
                "key_points": [str(proposal.get("theme") or "未知主题")],
                "risks": ["提案仍需要后续研究或人工复核"],
                "confidence": 0.6,
                "evidence_refs": [],
            },
        )

    return (
        "我已经尝试按正式对话链处理，但当前下游结果还不足以形成高质量答复，所以先保守返回。",
        {
            "fallback_used": True,
            "failure_stage": "synthesis",
            "key_points": [],
            "risks": ["下游结果不足以形成稳定结论"],
            "confidence": 0.2,
            "evidence_refs": [],
        },
    )


def _trust_level(domain: str) -> str:
    domain = domain.lower()
    if any(key in domain for key in ("gov", "imf.org", "worldbank.org", "federalreserve.gov", "ecb.europa.eu", "boj.or.jp")):
        return "high"
    if any(key in domain for key in ("reuters.com", "bloomberg.com", "wsj.com", "ft.com")):
        return "medium"
    return "low"


def _clean_excerpt(text: str) -> str:
    compact = " ".join(text.split()).strip()
    if not compact:
        return "暂未提取到稳定正文摘要"
    return compact[:160]
