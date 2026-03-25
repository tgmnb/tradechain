from datetime import date
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.intraday_watch_service import run_intraday_watch as execute_intraday_watch
from apps.api_service.app.services.internal_clients import internal_clients
from apps.api_service.app.services.policy_crawl_service import run_policy_crawl
from apps.api_service.app.services.web_research_service import run_web_research
from apps.api_service.app.services.runtime_objects import (
    execution_record_model_to_payload,
    event_model_to_payload,
    postclose_review_to_review_record,
    persist_proposal,
    persist_research_report,
    persist_review_record,
    persist_strategy,
    persist_trading_plan,
    proposal_model_to_payload,
    review_payload_to_contract,
    trading_plan_model_to_payload,
)
from apps.api_service.app.services.runtime_profiles import planning_profile_for, proposal_profile_for
from libs.contracts.enums import TaskStatus
from libs.contracts.event import EventIn, build_event_dedup_key
from libs.contracts.watch import IntradayWatchRequest
from libs.db.models import EventModel, ExecutionRecordModel, ProposalModel, ReviewModel, TaskModel, TradingPlanModel

router = APIRouter(prefix="/v1/workflows", tags=["workflows"], dependencies=[Depends(require_api_key)])


class PolicyCrawlRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit_per_source: int = Field(default=5, ge=1, le=20)
    source_ids: list[str] = Field(default_factory=list)


class WebResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=10)


@router.post("/intel-update/run")
async def run_intel_update(request: Request, db: Session = Depends(get_db)) -> dict:
    events = await internal_clients.fetch_mock_events(request, limit=5)

    created_events = 0
    created_proposals = 0

    for item in events:
        payload = EventIn.model_validate(item)
        dedup_key = build_event_dedup_key(payload)

        event = db.scalar(select(EventModel).where(EventModel.dedup_key == dedup_key))
        if not event:
            event = EventModel(
                source=payload.source,
                event_type=payload.event_type,
                title=payload.title,
                content=payload.content,
                asset_scope={"assets": payload.asset_scope},
                impact_direction=payload.impact_direction,
                confidence=payload.confidence,
                raw_payload=payload.raw_payload,
                dedup_key=dedup_key,
                occurred_at=payload.occurred_at,
            )
            db.add(event)
            db.flush()
            created_events += 1

        graph_result = await internal_clients.run_event_to_proposal_graph(
            request=request,
            event=event_model_to_payload(event),
            task_id=None,
            metadata={
                **proposal_profile_for("intel_update"),
                "source": "workflow_intel_update",
            },
            chain_type="intel_update",
        )

        proposal_data = graph_result.get("proposal")
        proposal_id = UUID(str(proposal_data["id"])) if proposal_data else None
        if proposal_data and proposal_id and not db.get(ProposalModel, proposal_id):
            persist_proposal(db, proposal_data, source_event_id=event.id)
            created_proposals += 1

    db.commit()
    return {
        "status": "success",
        "ingested": len(events),
        "created_events": created_events,
        "created_proposals": created_proposals,
    }


@router.post("/policy-crawl/run")
async def run_policy_crawl_workflow(payload: PolicyCrawlRequest | None = None) -> dict:
    request_payload = payload or PolicyCrawlRequest()
    result = run_policy_crawl(
        limit_per_source=request_payload.limit_per_source,
        source_ids=request_payload.source_ids,
    )
    return {
        "status": result["status"],
        "run_id": result["run_id"],
        "source_count": result["source_count"],
        "document_count": result["document_count"],
        "output_dir": result["output_dir"],
        "sources": result["sources"],
    }


@router.post("/web-research/run")
async def run_web_research_workflow(payload: WebResearchRequest) -> dict:
    return run_web_research(query=payload.query, max_results=payload.max_results)


@router.post("/major-task/run")
async def run_major_task(request: Request, db: Session = Depends(get_db)) -> dict:
    task = db.scalar(select(TaskModel).where(TaskModel.chain_type == "major_task").order_by(TaskModel.created_at.desc()))
    if not task:
        return {
            "status": "blocked",
            "reason": "no_major_task",
            "message": "Create a major_task first before running this workflow.",
        }

    master_result = await internal_clients.run_master_graph(
        request=request,
        chain_type="major_task",
        task={
            "id": str(task.id),
            "title": task.title,
            "type": task.type,
            "chain_type": task.chain_type,
            "priority": task.priority,
            "goal_json": task.goal_json or {},
            "context_json": task.context_json or {},
        },
        metadata={"stage": "task_intake"},
    )
    task.context_json = {
        **(task.context_json or {}),
        "governance": {
            "master_graph": master_result,
        },
    }
    goal_review = master_result.get("goal_review") or {}
    existing_review = db.scalar(
        select(ReviewModel)
        .where(ReviewModel.object_type == "task")
        .where(ReviewModel.object_id == task.id)
        .where(ReviewModel.reviewer_name == "review_clerk")
        .order_by(ReviewModel.created_at.desc())
    )
    persist_review_record(
        db,
        {
            "id": str(existing_review.id) if existing_review else str(uuid4()),
            "object_type": "task",
            "object_id": str(task.id),
            "reviewer_type": "agent",
            "reviewer_name": "review_clerk",
            "decision": goal_review.get("decision", "reject"),
            "comments": goal_review.get("reason", ""),
        },
    )

    if master_result.get("requires_human") or (master_result.get("goal_review") or {}).get("decision") == "reject":
        task.status = TaskStatus.NEEDS_HUMAN
        db.add(task)
        db.commit()
        db.refresh(task)
        return {
            "status": "needs_human",
            "reason": "governance_review_required",
            "task_id": str(task.id),
            "master_graph": master_result,
        }

    task.status = TaskStatus.RUNNING
    db.add(task)
    db.commit()
    db.refresh(task)

    proposal = db.scalar(select(ProposalModel).where(ProposalModel.task_id == task.id).order_by(ProposalModel.created_at.desc()))
    if not proposal:
        event = db.scalar(select(EventModel).order_by(EventModel.created_at.desc()))
        if not event:
            return {
                "status": "blocked",
                "reason": "no_event_context",
                "message": "No event is available to draft a proposal for the latest major task.",
            }

        proposal_result = await internal_clients.run_event_to_proposal_graph(
            request=request,
            event=event_model_to_payload(event),
            task_id=str(task.id),
            metadata={
                **proposal_profile_for("major_task"),
                "source": "workflow_major_task",
            },
            chain_type="major_task",
        )
        proposal_data = proposal_result.get("proposal")
        if not proposal_data:
            return {
                "status": "failed",
                "reason": "proposal_generation_failed",
                "message": "agent-core did not return a proposal for the latest major task.",
            }
        proposal = persist_proposal(db, proposal_data, task_id=task.id, source_event_id=event.id)
        db.flush()

    plan_result = await internal_clients.run_proposal_to_plan_graph(
        request=request,
        proposal=proposal_model_to_payload(proposal),
        task_id=str(task.id),
        metadata={
            **planning_profile_for("major_task"),
            "stop_after": "trading_plan",
            "plan_date": date.today().isoformat(),
        },
        chain_type="major_task",
    )

    report_data = plan_result.get("research_report")
    strategy_data = plan_result.get("strategy")
    plan_data = plan_result.get("trading_plan")
    if not (report_data and strategy_data and plan_data):
        return {
            "status": "failed",
            "reason": "planning_pipeline_failed",
            "message": "agent-core did not return the full research -> strategy -> plan chain.",
        }

    report = persist_research_report(db, report_data)
    strategy = persist_strategy(db, strategy_data)
    plan = persist_trading_plan(db, plan_data)
    db.commit()
    db.refresh(report)
    db.refresh(strategy)
    db.refresh(plan)
    db.refresh(task)

    return {
        "status": "success",
        "task_id": str(task.id),
        "master_graph": master_result,
        "proposal_id": str(proposal.id),
        "research_report_id": str(report.id),
        "strategy_id": str(strategy.id),
        "trading_plan_id": str(plan.id),
    }


@router.post("/daily-preopen/run")
async def run_daily_preopen(request: Request, db: Session = Depends(get_db)) -> dict:
    proposal = db.scalar(select(ProposalModel).order_by(ProposalModel.created_at.desc()))
    if not proposal:
        return {
            "status": "blocked",
            "reason": "no_proposal",
            "message": "Run intel-update or draft a proposal before daily-preopen.",
        }

    plan_result = await internal_clients.run_proposal_to_plan_graph(
        request=request,
        proposal=proposal_model_to_payload(proposal),
        task_id=str(proposal.task_id) if proposal.task_id else None,
        metadata={
            **planning_profile_for("daily_preopen"),
            "stop_after": "trading_plan",
            "plan_date": date.today().isoformat(),
        },
        chain_type="daily_preopen",
    )

    report_data = plan_result.get("research_report")
    strategy_data = plan_result.get("strategy")
    plan_data = plan_result.get("trading_plan")
    if not (report_data and strategy_data and plan_data):
        return {
            "status": "failed",
            "reason": "planning_pipeline_failed",
            "message": "agent-core did not return the full daily-preopen planning chain.",
        }

    report = persist_research_report(db, report_data)
    strategy = persist_strategy(db, strategy_data)
    plan = persist_trading_plan(db, plan_data)
    db.commit()
    db.refresh(report)
    db.refresh(strategy)
    db.refresh(plan)

    return {
        "status": "success",
        "proposal_id": str(proposal.id),
        "research_report_id": str(report.id),
        "strategy_id": str(strategy.id),
        "trading_plan_id": str(plan.id),
        "plan_date": plan.plan_date.isoformat(),
    }


@router.post("/intraday-watch/run")
async def run_intraday_watch_workflow(payload: IntradayWatchRequest | None = None) -> dict:
    return execute_intraday_watch(payload)


@router.post("/postclose-review/run")
async def run_postclose_review(request: Request, db: Session = Depends(get_db)) -> dict:
    plan = db.scalar(select(TradingPlanModel).order_by(TradingPlanModel.created_at.desc()))
    if not plan:
        return {
            "status": "blocked",
            "reason": "no_trading_plan",
            "message": "postclose-review needs at least one trading plan before it can compare execution results.",
        }

    execution_records = db.scalars(
        select(ExecutionRecordModel)
        .where(ExecutionRecordModel.trading_plan_id == plan.id)
        .order_by(ExecutionRecordModel.created_at.asc())
    ).all()
    if not execution_records:
        return {
            "status": "blocked",
            "reason": "execution_records_required",
            "message": "postclose-review already has execution_compare_skill in registry, but still needs execution records and plan-vs-action comparison inputs before it can run.",
            "trading_plan_id": str(plan.id),
        }

    review_result = await internal_clients.run_review_graph(
        request=request,
        chain_type="postclose_review",
        metadata={
            "trading_plan": trading_plan_model_to_payload(plan),
            "execution_records": [execution_record_model_to_payload(record) for record in execution_records],
            "execution_record_count": len(execution_records),
        },
    )
    review_payload = review_result.get("review")
    if not review_payload:
        return {
            "status": "failed",
            "reason": "review_generation_failed",
            "message": "review_graph did not return a structured review result.",
            "trading_plan_id": str(plan.id),
        }

    persisted_review = persist_review_record(db, postclose_review_to_review_record(review_payload))
    db.commit()
    db.refresh(persisted_review)
    structured_review = review_payload_to_contract(review_payload)
    return {
        "status": "success",
        "trading_plan_id": str(plan.id),
        "execution_record_count": len(execution_records),
        "review_id": str(persisted_review.id),
        "review": structured_review.model_dump(mode="json"),
        "review_graph": review_result,
    }


@router.post("/nightly-improvement/run")
async def run_nightly_improvement_placeholder() -> dict:
    return {
        "status": "blocked",
        "reason": "evaluation_pipeline_required",
        "message": "nightly-improvement already has improvement_ticket_skill in registry, but still needs evaluation signals, scores, and approval workflow before it can run.",
    }
