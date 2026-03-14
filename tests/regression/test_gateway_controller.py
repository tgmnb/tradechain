from apps.api_service.app.agent import dispatch_gateway_command


def test_gateway_handles_slash_help() -> None:
    decision = dispatch_gateway_command("/help")

    assert decision.handled is True
    assert decision.route == "help"
    assert decision.activate_chain is False


def test_gateway_passes_plain_text_to_politburo() -> None:
    decision = dispatch_gateway_command("你是谁")

    assert decision.handled is False
    assert decision.route == "pass_through"


def test_gateway_routes_search_and_policy_commands() -> None:
    search = dispatch_gateway_command("/search japan central bank policy")
    policy = dispatch_gateway_command("/policy_watch")

    assert search.handled is True
    assert search.route == "web_research"
    assert search.activate_chain is True
    assert policy.handled is True
    assert policy.route == "policy_watch"
    assert policy.activate_chain is True
