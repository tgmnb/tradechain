from __future__ import annotations

import json
from typing import Any

import httpx

from apps.agent_core.app.config import Settings



def call_minimax_json(*, settings: Settings, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    body = {
        "model": settings.llm_model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(
        base_url=settings.llm_base_url.rstrip("/"),
        timeout=settings.llm_timeout_seconds,
        proxy=settings.llm_proxy_url or None,
        trust_env=False,
    ) as client:
        response = client.post("/chat/completions", json=body, headers=headers)
        response.raise_for_status()
        payload = response.json()

    content = payload["choices"][0]["message"]["content"]
    if not isinstance(content, str):
        raise ValueError("unexpected response content type")
    return extract_json_object(content)



def extract_json_object(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return json.loads(candidate)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or start >= end:
        raise ValueError("model did not return a JSON object")
    return json.loads(cleaned[start : end + 1])
