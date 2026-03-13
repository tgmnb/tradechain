from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.internal_clients import internal_clients
from apps.api_service.app.services.runtime_objects import (
    persist_research_report,
    proposal_model_to_payload,
    research_report_model_to_contract,
)
from apps.api_service.app.services.runtime_profiles import planning_profile_for
from libs.contracts.research import ResearchReport, ResearchReportDraftRequest
from libs.db.models import ProposalModel, ResearchReportModel

router = APIRouter(prefix="/v1/research-reports", tags=["research-reports"], dependencies=[Depends(require_api_key)])


@router.post("/draft", response_model=ResearchReport, status_code=status.HTTP_201_CREATED)
async def draft_research_report(
    payload: ResearchReportDraftRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ResearchReport:
    proposal = db.get(ProposalModel, payload.proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="proposal not found")

    chain_type = "major_task" if proposal.task_id or payload.task_id else "daily_preopen"
    profile = planning_profile_for(chain_type, department_id=payload.department_id, specialist_id=payload.specialist_id)
    graph_result = await internal_clients.run_proposal_to_plan_graph(
        request=request,
        proposal=proposal_model_to_payload(proposal),
        task_id=str(payload.task_id or proposal.task_id) if (payload.task_id or proposal.task_id) else None,
        metadata={**profile, "stop_after": "research"},
        chain_type=chain_type,
    )

    report_data = graph_result.get("research_report")
    if not report_data:
        raise HTTPException(status_code=502, detail="agent-core did not return a research report")

    report = persist_research_report(db, report_data)
    db.commit()
    db.refresh(report)
    return research_report_model_to_contract(report)


@router.get("/latest", response_model=ResearchReport)
async def get_latest_research_report(db: Session = Depends(get_db)) -> ResearchReport:
    report = db.scalar(select(ResearchReportModel).order_by(ResearchReportModel.created_at.desc()))
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="research report not found")
    return research_report_model_to_contract(report)


@router.get("/{report_id}", response_model=ResearchReport)
async def get_research_report(report_id: UUID, db: Session = Depends(get_db)) -> ResearchReport:
    report = db.get(ResearchReportModel, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="research report not found")
    return research_report_model_to_contract(report)
