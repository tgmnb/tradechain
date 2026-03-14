from __future__ import annotations

import json
import re
from typing import Any

import httpx

from apps.api_service.app.core.config import get_settings
from libs.registry import load_registry


class PolitburoResponder:
    async def reply(self, *, route: str, user_text: str, context: dict[str, Any] | None = None) -> str:
        context = context or {}
        profile = _politburo_profile()
        direct = _rule_based_reply(route=route, user_text=user_text, context=context)
        if direct:
            return direct

        settings = get_settings()
        response = await self._call_llm(
            route=route,
            user_text=user_text,
            context=context,
            settings=settings,
            system_prompt=profile.system_prompt,
        )
        return response or _fallback_reply(route=route, context=context, profile=profile)

    async def _call_llm(self, *, route: str, user_text: str, context: dict[str, Any], settings, system_prompt: str) -> str | None:
        if settings.llm_provider.lower() != "minimax" or not settings.llm_api_key:
            return None

        body = {
            "model": settings.llm_model,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"{system_prompt}\n\n"
                        "Answer in concise natural Chinese. "
                        "Handle direct questions yourself. "
                        "Do not mention internal routing unless the user asks. "
                        "If context is provided, use it faithfully and do not invent facts."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"route: {route}\n"
                        f"user_text: {user_text}\n"
                        f"context: {json.dumps(context, ensure_ascii=False)}\n"
                        "Reply directly to the user in Chinese."
                    ),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                base_url=settings.llm_base_url.rstrip("/"),
                timeout=settings.llm_timeout_seconds,
                proxy=settings.llm_proxy_url or None,
                trust_env=False,
            ) as client:
                response = await client.post("/chat/completions", json=body, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return None

        content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not isinstance(content, str) or not content.strip():
            return None
        return _sanitize_response(content)


def _fallback_reply(*, route: str, context: dict[str, Any], profile) -> str:
    if route == "health":
        return f"系统当前状态是 {context.get('status', 'unknown')}。"

    if route == "proposal_latest":
        return (
            f"当前最新提案主题是“{context.get('theme', '未知主题')}”，"
            f"建议动作是 {context.get('recommended_action', 'wait_for_review')}。"
        )

    if route == "help":
        return (
            f"我是 {profile.department_name}的顶层决策中枢。"
            "Tradechain 不是区块链平台，而是一套 AI 投研多 Agent 系统。"
            "你可以直接问我系统状态、最新提案，或者让我发起研究分析链路。"
        )

    return (
        f"我是 {profile.department_name}角色，负责顶层判断与分流。"
        "简单问题我会直接回答；需要研究和分析时，我会调起后续链路。"
    )


politburo_responder = PolitburoResponder()


def _sanitize_response(content: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
    return cleaned or content.strip()


def _politburo_profile():
    registry = load_registry()
    return registry.resolve_agent_profile(
        chain_type="direct_dialogue",
        department_id="politburo",
        specialist_id="chairman_officer",
    )


def _rule_based_reply(*, route: str, user_text: str, context: dict[str, Any]) -> str | None:
    lowered = " ".join(user_text.lower().split())

    if _asks_identity_or_capability(lowered):
        return (
            "我是 Tradechain 的政治局顶层决策中枢，负责接收请求、直接答复简单问题，"
            "并把需要继续处理的任务分派给下游部门和专员链路。"
        )

    if _asks_project_definition(lowered):
        return (
            "Tradechain 不是贸易金融区块链平台。它是一套 AI 投研多 Agent 系统，"
            "用于把事件线索推进成提案、研究报告、策略和交易计划，并逐步扩展到盘中巡检、"
            "盘后复盘和夜间改进。当前我在这里扮演政治局角色，负责顶层判断与调度。"
        )

    if route == "help" and context.get("capabilities"):
        return (
            "我是 Tradechain 的政治局顶层决策中枢。"
            "我可以直接回答身份、状态、最新提案等问题，也可以把研究分析类请求升级到后续链路。"
        )

    return None


def _asks_identity_or_capability(text: str) -> bool:
    patterns = (
        "你是谁",
        "你是？",
        "你是?",
        "你能做什么",
        "你可以做什么",
        "who are you",
        "what can you do",
    )
    return any(pattern in text for pattern in patterns)


def _asks_project_definition(text: str) -> bool:
    patterns = (
        "什么是tradechain",
        "什么是 tradechain",
        "甚么是tradechain",
        "甚么是 tradechain",
        "tradechain是什么",
        "tradechain 是什么",
        "什么是 trade chain",
    )
    return any(pattern in text for pattern in patterns)
