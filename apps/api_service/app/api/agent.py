from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from apps.api_service.app.agent import dispatch_discord_message, dispatch_gateway_command
from apps.api_service.app.api.proposals import get_latest_proposal
from apps.api_service.app.api.tasks import create_task
from apps.api_service.app.api.workflows import (
    PolicyCrawlRequest,
    WebResearchRequest,
    run_intel_update,
    run_policy_crawl_workflow,
    run_web_research_workflow,
)
from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import SessionLocal
from apps.api_service.app.services.dialogue_chain_service import build_evidence_bundle, clarify_dialogue_task, synthesize_governed_answer
from apps.api_service.app.services.dialogue_runtime_service import dialogue_runtime_service
from apps.api_service.app.services.politburo_responder import politburo_responder
from libs.contracts.task import TaskCreate, TaskRead

router = APIRouter(prefix="/v1/agent", tags=["agent"], dependencies=[Depends(require_api_key)])
db_session_factory = SessionLocal


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
) -> DiscordMessageResponse:
    text = payload.text.strip()
    gateway = dispatch_gateway_command(text)
    decision = dispatch_discord_message(text) if not gateway.handled else None

    if gateway.handled and gateway.route == "help":
        return DiscordMessageResponse(
            route=gateway.route,
            summary=await politburo_responder.reply(
                route=gateway.route,
                user_text=text,
                context={
                    "capabilities": [
                        "health",
                        "proposal_latest",
                        "web_research",
                        "policy_watch",
                        "analysis",
                        "proposal_generation",
                    ],
                    "entry_layer": "gateway",
                },
            ),
        )

    if gateway.handled and gateway.route == "health":
        return DiscordMessageResponse(
            route=gateway.route,
            summary=await politburo_responder.reply(
                route=gateway.route,
                user_text=text,
                context={"status": "ok", "entry_layer": "gateway"},
            ),
        )

    if gateway.handled and gateway.route == "proposal_latest":
        with _db_session() as db:
            proposal = await get_latest_proposal(db=db)
            proposal_dict = proposal.model_dump(mode="json")
            return DiscordMessageResponse(
                route=gateway.route,
                summary=await politburo_responder.reply(
                    route=gateway.route,
                    user_text=text,
                    context={**proposal_dict, "entry_layer": "gateway"},
                ),
                proposal=proposal_dict,
            )

    if decision and decision.route == "help":
        return DiscordMessageResponse(
            route=decision.route,
            summary=await politburo_responder.reply(
                route=decision.route,
                user_text=text,
                context={
                    "capabilities": [
                        "health",
                        "proposal_latest",
                        "web_research",
                        "policy_watch",
                        "analysis",
                        "proposal_generation",
                    ]
                },
            ),
        )

    if decision and decision.route == "health":
        return DiscordMessageResponse(
            route=decision.route,
            summary=await politburo_responder.reply(
                route=decision.route,
                user_text=text,
                context={"status": "ok"},
            ),
        )

    if decision and decision.route == "proposal_latest":
        with _db_session() as db:
            proposal = await get_latest_proposal(db=db)
            proposal_dict = proposal.model_dump(mode="json")
            return DiscordMessageResponse(
                route=decision.route,
                summary=await politburo_responder.reply(
                    route=decision.route,
                    user_text=text,
                    context=proposal_dict,
                ),
                proposal=proposal_dict,
            )

    if gateway.handled and gateway.route in {"intel_update", "web_research", "policy_watch"}:
        decision_summary = gateway.summary
        final_route = gateway.route
    elif decision and decision.activate_chain:
        decision_summary = decision.summary
        final_route = decision.route
    else:
        decision_summary = ""
        final_route = decision.route if decision else gateway.route

    if decision and not decision.activate_chain:
        return DiscordMessageResponse(
            route=decision.route,
            summary=await politburo_responder.reply(
                route=decision.route,
                user_text=text,
                context={"policy": "direct_reply_without_research_workflow", "entry_layer": "politburo"},
            ),
        )

    if decision and decision.activate_chain and decision.route == "governed_dialogue":
        return await _run_governed_dialogue(payload, request, decision_summary)

    with _db_session() as db:
        task = await create_task(
            TaskCreate(
                title=_title_from_text(text),
                type=final_route,
                source="discord",
                chain_type=final_route,
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

        if final_route == "web_research":
            workflow_result = await run_web_research_workflow(WebResearchRequest(query=text))
            return DiscordMessageResponse(
                route=final_route,
                summary="\n".join(
                    [
                        decision_summary,
                        f"Task `{task.id}` created.",
                        workflow_result.get("summary", ""),
                    ]
                ).strip(),
                task=task.model_dump(mode="json"),
                workflow=workflow_result,
            )

        if final_route == "policy_watch":
            workflow_result = await run_policy_crawl_workflow(PolicyCrawlRequest())
            return DiscordMessageResponse(
                route=final_route,
                summary="\n".join(
                    [
                        decision_summary,
                        f"Task `{task.id}` created.",
                        (
                            f"已执行政策抓取，共处理 `{workflow_result.get('source_count')}` 个来源，"
                            f"整理出 `{workflow_result.get('document_count')}` 条候选政策线索。"
                        ),
                        f"输出目录：`{workflow_result.get('output_dir')}`",
                    ]
                ),
                task=task.model_dump(mode="json"),
                workflow=workflow_result,
            )

        workflow_result = await run_intel_update(request=request, db=db)
        proposal = await get_latest_proposal(db=db)
        proposal_dict = proposal.model_dump(mode="json")

        return DiscordMessageResponse(
            route=final_route,
            summary="\n".join(
                [
                    decision_summary,
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


def _db_session():
    return db_session_factory()


async def _run_governed_dialogue(
    payload: DiscordMessageRequest,
    request: Request,
    decision_summary: str,
) -> DiscordMessageResponse:
    clarified = clarify_dialogue_task(payload.text)
    with _db_session() as db:
        task, intent = dialogue_runtime_service.create_dialogue_task(
            db,
            payload={
                "text": payload.text,
                "user_name": payload.user_name,
                "channel_id": payload.channel_id,
                "guild_id": payload.guild_id,
                "conversation_id": str(uuid4()),
                "request_id": request.headers.get("X-Request-ID", str(uuid4())),
                "topic_scope": clarified.topic_scope,
                "constraints": clarified.constraints,
            },
            route=clarified.route,
            objective=clarified.objective,
            requested_output=clarified.requested_output,
            requires_research=clarified.requires_research,
        )

        archive_refs = dialogue_runtime_service.archive_dialogue_artifacts(request, intent=intent)
        evidence_bundle = None
        failure = None
        workflow_result: dict[str, Any] = {}

        if clarified.downstream_route == "web_research":
            workflow_result = await run_web_research_workflow(WebResearchRequest(query=payload.text))
            evidence_bundle = build_evidence_bundle(
                task_id=task.id,
                request_id=intent.request_id,
                workflow_result=workflow_result,
                source_policy=clarified.source_policy,
            )
            archive_refs.extend(dialogue_runtime_service.archive_dialogue_artifacts(request, evidence_bundle=evidence_bundle))
        elif clarified.downstream_route == "intel_update":
            workflow_result = await run_intel_update(request=request, db=db)
            latest = await get_latest_proposal(db=db)
            workflow_result = {**workflow_result, "proposal": latest.model_dump(mode="json")}

        answer_text, conclusion_data = synthesize_governed_answer(
            text=payload.text,
            clarified=clarified,
            workflow_result=workflow_result,
        )
        if conclusion_data["fallback_used"]:
            failure = dialogue_runtime_service.build_failure(
                task_id=task.id,
                request_id=intent.request_id,
                stage=str(conclusion_data["failure_stage"] or "research"),
                cause_category="weak_evidence",
                fallback_behavior="return bounded uncertainty",
                retryable=True,
                metadata={"downstream_route": clarified.downstream_route},
            )
            archive_refs.extend(dialogue_runtime_service.archive_dialogue_artifacts(request, failure=failure))

        conclusion = dialogue_runtime_service.build_conclusion(
            task_id=task.id,
            request_id=intent.request_id,
            summary=answer_text,
            key_points=conclusion_data["key_points"],
            risks=conclusion_data["risks"],
            recommended_action="research" if clarified.requires_research else "notify",
            confidence=conclusion_data["confidence"],
            evidence_refs=conclusion_data["evidence_refs"],
            metadata={"downstream_route": clarified.downstream_route, "source_policy": clarified.source_policy},
        )
        archive_refs.extend(dialogue_runtime_service.archive_dialogue_artifacts(request, conclusion=conclusion))

        reply = dialogue_runtime_service.build_reply(
            task_id=task.id,
            request_id=intent.request_id,
            route="governed_dialogue",
            answer_text=answer_text,
            archive_refs=archive_refs,
            fallback_used=conclusion_data["fallback_used"],
            failure_stage=conclusion_data["failure_stage"],
            metadata={"requested_output": clarified.requested_output},
        )
        archive_refs.extend(dialogue_runtime_service.archive_dialogue_artifacts(request, reply=reply))
        reply.archive_refs = archive_refs

        summary = "\n".join(
            part
            for part in (
                decision_summary,
                reply.answer_text,
            )
            if part
        )
        workflow_view = {
            "status": workflow_result.get("status", "success"),
            "downstream_route": clarified.downstream_route,
            "source_policy": clarified.source_policy,
            "result_count": workflow_result.get("result_count"),
        }
        return DiscordMessageResponse(
            route="governed_dialogue",
            summary=summary,
            task=TaskRead.model_validate(task, from_attributes=True).model_dump(mode="json"),
            workflow=workflow_view,
        )
