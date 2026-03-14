import pytest

from apps.api_service.app.services.politburo_responder import politburo_responder


@pytest.mark.anyio
async def test_responder_returns_politburo_identity() -> None:
    reply = await politburo_responder.reply(route="help", user_text="你是谁，你能做什么？", context={})

    assert "政治局" in reply
    assert "顶层" in reply


@pytest.mark.anyio
async def test_responder_describes_tradechain_as_ai_system_not_blockchain() -> None:
    reply = await politburo_responder.reply(route="chat", user_text="什么是Tradechain", context={})

    assert "AI 投研多 Agent 系统" in reply
    assert "区块链平台" in reply
    assert "不是" in reply


@pytest.mark.anyio
async def test_responder_fallback_uses_registry_backed_department_name() -> None:
    reply = await politburo_responder.reply(route="chat", user_text="你好", context={})

    assert "中央政治局" in reply
