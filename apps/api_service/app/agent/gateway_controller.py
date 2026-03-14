from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayDecision:
    route: str
    handled: bool
    activate_chain: bool
    summary: str


def dispatch_gateway_command(text: str) -> GatewayDecision:
    normalized = text.strip()
    lowered = normalized.lower()

    if not normalized.startswith("/"):
        return GatewayDecision(
            route="pass_through",
            handled=False,
            activate_chain=False,
            summary="Plain natural-language input should be passed through to the politburo layer.",
        )

    command = lowered.split()[0]
    if command in {"/help", "/h", "/?"}:
        return GatewayDecision(
            route="help",
            handled=True,
            activate_chain=False,
            summary="Gateway handled this as a direct help command.",
        )

    if command in {"/health", "/status"}:
        return GatewayDecision(
            route="health",
            handled=True,
            activate_chain=False,
            summary="Gateway handled this as a direct health command.",
        )

    if command in {"/proposal", "/latest", "/latest_proposal"}:
        return GatewayDecision(
            route="proposal_latest",
            handled=True,
            activate_chain=False,
            summary="Gateway handled this as a direct latest-proposal command.",
        )

    if command in {"/intel", "/intel_update", "/research"}:
        return GatewayDecision(
            route="intel_update",
            handled=True,
            activate_chain=True,
            summary="Gateway handled this as an explicit research workflow command.",
        )

    if command in {"/search", "/web", "/web_research"}:
        return GatewayDecision(
            route="web_research",
            handled=True,
            activate_chain=True,
            summary="Gateway handled this as an explicit web research command.",
        )

    if command in {"/policy", "/policy_watch", "/crawl_policy"}:
        return GatewayDecision(
            route="policy_watch",
            handled=True,
            activate_chain=True,
            summary="Gateway handled this as an explicit policy-watch command.",
        )

    return GatewayDecision(
        route="help",
        handled=True,
        activate_chain=False,
        summary="Gateway did not recognize this slash command and returned help instead.",
    )
