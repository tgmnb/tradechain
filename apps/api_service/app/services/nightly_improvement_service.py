from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.services.runtime_objects import improvement_ticket_model_to_contract, to_float
from libs.contracts.improvement import NightlyImprovementRequest
from libs.db.models import AgentScoreModel, ImprovementTicketModel, ProposalModel, ReviewModel, TradingPlanModel


def run_nightly_improvement(db: Session, payload: NightlyImprovementRequest | dict | None = None) -> dict:
    request = payload if isinstance(payload, NightlyImprovementRequest) else NightlyImprovementRequest.model_validate(payload or {})
    if request.transition is not None:
        return _apply_ticket_transition(db, request)
    return _generate_tickets(db, request)


def _generate_tickets(db: Session, request: NightlyImprovementRequest) -> dict:
    window_end = date.today()
    window_start = window_end - timedelta(days=request.evidence_window_days - 1)
    created_after = datetime.combine(window_start, time.min, tzinfo=timezone.utc)

    scores = db.scalars(
        select(AgentScoreModel)
        .where(AgentScoreModel.period_end >= window_start)
        .where(AgentScoreModel.period_start <= window_end)
        .order_by(AgentScoreModel.period_end.desc(), AgentScoreModel.created_at.desc())
    ).all()
    reviews = db.scalars(select(ReviewModel).where(ReviewModel.created_at >= created_after)).all()
    proposals = db.scalars(select(ProposalModel).where(ProposalModel.created_at >= created_after)).all()
    trading_plans = db.scalars(select(TradingPlanModel).where(TradingPlanModel.created_at >= created_after)).all()

    evidence_summary = {
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "proposal_count": len(proposals),
        "trading_plan_count": len(trading_plans),
        "review_count": len(reviews),
        "agent_score_count": len(scores),
        "rejected_review_count": sum(1 for review in reviews if review.decision == "reject"),
    }

    if not any(evidence_summary[key] for key in ("proposal_count", "trading_plan_count", "review_count", "agent_score_count")):
        return {
            "status": "blocked",
            "reason": "no_historical_evidence",
            "message": "nightly-improvement baseline needs historical proposals, plans, reviews, or scores before it can aggregate evidence.",
            "evidence_summary": evidence_summary,
        }

    if not scores:
        return {
            "status": "blocked",
            "reason": "no_scoring_evidence",
            "message": "nightly-improvement baseline needs at least one agent score in the evidence window before it can generate tickets.",
            "evidence_summary": evidence_summary,
        }

    persisted: list[ImprovementTicketModel] = []
    for score in scores:
        total_score = to_float(score.total_score, 0.0)
        if total_score >= request.minimum_score_threshold:
            continue

        ticket = ImprovementTicketModel(
            target_type="agent",
            target_name=score.agent_name,
            source_period_start=score.period_start,
            source_period_end=score.period_end,
            issue_summary=(
                f"Agent {score.agent_name} scored {total_score:.2f}, below nightly threshold {request.minimum_score_threshold:.2f}."
            ),
            impact_description=(
                "Nightly aggregation detected a weak performance pattern that should be reviewed before runtime changes are considered."
            ),
            root_cause={
                "score_breakdown": score.detail_json or {},
                "total_score": total_score,
                "evidence_summary": evidence_summary,
            },
            proposed_fix={
                "actions": [
                    "review recent outputs tied to the low score window",
                    "tighten the relevant prompt, heuristic, or routing rule",
                    "re-run validation before any rollout",
                ],
                "approval_role": request.approval_role,
            },
            status="pending_approval",
            approved_by=None,
        )
        db.add(ticket)
        persisted.append(ticket)

    db.commit()
    for ticket in persisted:
        db.refresh(ticket)

    return {
        "status": "success",
        "evidence_summary": evidence_summary,
        "generated_ticket_count": len(persisted),
        "tickets": [improvement_ticket_model_to_contract(ticket).model_dump(mode="json") for ticket in persisted],
        "approval_role": request.approval_role,
    }


def _apply_ticket_transition(db: Session, request: NightlyImprovementRequest) -> dict:
    transition = request.transition
    if transition is None:
        raise ValueError("transition is required")

    ticket = db.get(ImprovementTicketModel, transition.ticket_id)
    if not ticket:
        return {
            "status": "blocked",
            "reason": "ticket_not_found",
            "message": f"improvement ticket {transition.ticket_id} was not found.",
        }

    allowed_transitions = {
        "pending_approval": {"approved", "rejected"},
        "approved": {"applied"},
        "rejected": set(),
        "applied": set(),
    }
    current_status = ticket.status
    next_status = transition.status
    if next_status not in allowed_transitions.get(current_status, set()):
        return {
            "status": "blocked",
            "reason": "invalid_ticket_transition",
            "message": f"cannot move improvement ticket from {current_status} to {next_status}.",
            "ticket": improvement_ticket_model_to_contract(ticket).model_dump(mode="json"),
        }

    ticket.status = next_status
    if current_status == "pending_approval":
        ticket.approved_by = transition.actor

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "status": "success",
        "transitioned_ticket_id": str(ticket.id),
        "ticket": improvement_ticket_model_to_contract(ticket).model_dump(mode="json"),
    }
