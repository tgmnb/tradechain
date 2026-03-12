from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from apps.api_service.app.agent import dispatch_discord_message
from apps.api_service.app.api.proposals import get_latest_proposal
from apps.api_service.app.api.tasks import create_task
from apps.api_service.app.api.workflows import run_intel_update
from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from libs.contracts.task import TaskCreate, TaskRead

router = APIRouter(prefix="/v1/agent", tags=["agent"], dependencies=[Depends(require_api_key)])


class DiscordMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=4000)
    user_name: str = Field(min_length=1, max_length=200)
    user_id: str = Field(min_length=1, max_length=100)
    channel_id: str = Field(min_length=1, max_length=100)
    guild_id: str | None = Field(default=None, max_length=100)


class DiscordMessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    route: str
    summary: str
    task: dict[str, Any] | None = None
    workflow: dict[str, Any] | None = None
    proposal: dict[str, Any] | None = None


@router.post("/discord-message", response_model=DiscordMessageResponse)
async def handle_discord_message(
    payload: DiscordMessageRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> DiscordMessageResponse:
    text = payload.text.strip()
    decision = dispatch_discord_message(text)

    if decision.route == "help":
        return DiscordMessageResponse(
            route=decision.route,
            summary=decision.summary,
        )

    if decision.route == "health":
        return DiscordMessageResponse(
            route=decision.route,
            summary="System health is `ok`.",
        )

    if decision.route == "proposal_latest":
        proposal = await get_latest_proposal(db=db)
        return DiscordMessageResponse(
            route=decision.route,
            summary=_proposal_summary(proposal.model_dump(mode="json")),
            proposal=proposal.model_dump(mode="json"),
        )

    if not decision.activate_chain:
        return DiscordMessageResponse(
            route=decision.route,
            summary=decision.summary,
        )

    task = await create_task(
        TaskCreate(
            title=_title_from_text(text),
            type="intel_update",
            source="discord",
            chain_type="intel_update",
            priority=50,
            goal_json={"text": text},
            context_json={
                "discord_user_id": payload.user_id,
                "discord_user_name": payload.user_name,
                "discord_channel_id": payload.channel_id,
                "discord_guild_id": payload.guild_id,
                "conversation_id": str(uuid4()),
            },
            created_by=payload.user_name,
        ),
        db=db,
    )

    workflow_result = await run_intel_update(request=request, db=db)
    proposal = await get_latest_proposal(db=db)
    proposal_dict = proposal.model_dump(mode="json")

    return DiscordMessageResponse(
        route=decision.route,
        summary="\n".join(
            [
                decision.summary,
                f"Task `{task.id}` created.",
                f"Workflow status: `{workflow_result.get('status')}`.",
                _proposal_summary(proposal_dict),
            ]
        ),
        task=task.model_dump(mode="json"),
        workflow=workflow_result,
        proposal=proposal_dict,
    )


def _title_from_text(text: str) -> str:
    compact = " ".join(text.split())
    return compact[:200] if compact else "Discord agent request"


def _proposal_summary(proposal: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Proposal `{proposal.get('id')}`",
            f"Theme: {proposal.get('theme')}",
            f"Action: `{proposal.get('recommended_action')}`",
            f"Requires human: `{proposal.get('requires_human')}`",
        ]
    )
