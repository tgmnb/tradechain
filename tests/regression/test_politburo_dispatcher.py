from apps.api_service.app.agent import dispatch_discord_message


def test_dispatcher_routes_help_requests_to_direct_reply() -> None:
    decision = dispatch_discord_message("你是谁，你能做什么？")

    assert decision.route == "help"
    assert decision.activate_chain is False


def test_dispatcher_routes_research_requests_to_intel_update() -> None:
    decision = dispatch_discord_message("请帮我研究一下今天的宏观变化并给我一个提案")

    assert decision.route == "intel_update"
    assert decision.activate_chain is True
