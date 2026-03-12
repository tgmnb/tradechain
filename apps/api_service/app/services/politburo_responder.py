from __future__ import annotations

import json
import re
from typing import Any

import httpx

from apps.api_service.app.core.config import get_settings


class PolitburoResponder:
    async def reply(self, *, route: str, user_text: str, context: dict[str, Any] | None = None) -> str:
        settings = get_settings()
        response = await self._call_llm(route=route, user_text=user_text, context=context or {}, settings=settings)
        return response or _fallback_reply(route=route, context=context or {})

    async def _call_llm(self, *, route: str, user_text: str, context: dict[str, Any], settings) -> str | None:
        if settings.llm_provider.lower() != "minimax" or not settings.llm_api_key:
            return None

        body = {
            "model": settings.llm_model,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the top-level politburo agent of Tradechain. "
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


def _fallback_reply(*, route: str, context: dict[str, Any]) -> str:
    if route == "health":
        return f"系统当前状态是 {context.get('status', 'unknown')}。"

    if route == "proposal_latest":
        return (
            f"当前最新提案主题是“{context.get('theme', '未知主题')}”，"
            f"建议动作是 {context.get('recommended_action', 'wait_for_review')}。"
        )

    if route == "help":
        return "我是 Tradechain 的顶层调度 agent。你可以直接问状态、提案，或者让我做研究和分析。"

    return "我在。简单问题我会直接回答；需要研究和分析时，我会继续调起后续链路。"


politburo_responder = PolitburoResponder()


def _sanitize_response(content: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
    return cleaned or content.strip()
