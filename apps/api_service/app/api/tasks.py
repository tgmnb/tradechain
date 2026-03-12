from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from libs.contracts.enums import TaskStatus
from libs.contracts.task import TaskCreate, TaskRead
from libs.db.models import TaskModel

router = APIRouter(prefix="/v1/tasks", tags=["tasks"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    task = TaskModel(
        id=uuid4(),
        title=payload.title,
        type=payload.type,
        source=payload.source,
        status=TaskStatus.PENDING,
        priority=payload.priority,
        chain_type=payload.chain_type,
        created_by=payload.created_by,
        goal_json=payload.goal_json,
        context_json=payload.context_json,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskRead.model_validate(task, from_attributes=True)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, db: Session = Depends(get_db)) -> TaskRead:
    task = db.get(TaskModel, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    return TaskRead.model_validate(task, from_attributes=True)
