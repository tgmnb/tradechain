from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api_service.app.core.security import require_api_key
from apps.api_service.app.db.session import get_db
from apps.api_service.app.services.runtime_objects import review_model_to_contract
from libs.contracts.review import ReviewRecord
from libs.db.models import ReviewModel

router = APIRouter(prefix="/v1/reviews", tags=["reviews"], dependencies=[Depends(require_api_key)])


@router.get("/latest", response_model=ReviewRecord)
async def get_latest_review(db: Session = Depends(get_db)) -> ReviewRecord:
    review = db.scalar(select(ReviewModel).order_by(ReviewModel.created_at.desc()))
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="review not found")
    return review_model_to_contract(review)


@router.get("/by-object/{object_type}/{object_id}", response_model=list[ReviewRecord])
async def list_reviews_by_object(object_type: str, object_id: UUID, db: Session = Depends(get_db)) -> list[ReviewRecord]:
    reviews = db.scalars(
        select(ReviewModel)
        .where(ReviewModel.object_type == object_type)
        .where(ReviewModel.object_id == object_id)
        .order_by(ReviewModel.created_at.desc())
    ).all()
    return [review_model_to_contract(review) for review in reviews]
