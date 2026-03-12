from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from apps.archive_service.app.db import get_db
from apps.archive_service.app.services.storage import archive_storage
from libs.contracts.archive import ArchiveCreate, ArchiveRef
from libs.db.models import ArchiveModel

router = APIRouter(prefix="/internal/archive", tags=["archive"])


def require_internal_key(x_api_key: str | None = Header(default=None)) -> None:
    from os import getenv

    expected = getenv("INTERNAL_SERVICE_API_KEY", "internal-dev-key")
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid internal API key")


@router.post("", response_model=ArchiveRef, dependencies=[Depends(require_internal_key)])
async def archive_object(payload: ArchiveCreate, db: Session = Depends(get_db)) -> ArchiveRef:
    try:
        archive_key = archive_storage.store_json(payload.object_type, str(payload.object_id), payload.payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "archive_write_failed",
                "retryable": True,
                "message": str(exc),
            },
        ) from exc

    row = ArchiveModel(
        id=uuid4(),
        object_type=payload.object_type,
        object_id=payload.object_id,
        archive_key=archive_key,
        storage_type=payload.storage_type,
        metadata_json=payload.metadata,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return ArchiveRef(
        id=row.id,
        object_type=row.object_type,
        object_id=row.object_id,
        archive_key=row.archive_key,
        storage_type=row.storage_type,
        metadata=row.metadata_json,
        created_at=row.created_at,
    )


@router.get("/{object_type}/{object_id}", response_model=ArchiveRef, dependencies=[Depends(require_internal_key)])
async def get_archive(object_type: str, object_id: UUID, db: Session = Depends(get_db)) -> ArchiveRef:
    row = db.scalar(
        select(ArchiveModel)
        .where(ArchiveModel.object_type == object_type, ArchiveModel.object_id == object_id)
        .order_by(desc(ArchiveModel.created_at))
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="archive not found")

    return ArchiveRef(
        id=row.id,
        object_type=row.object_type,
        object_id=row.object_id,
        archive_key=row.archive_key,
        storage_type=row.storage_type,
        metadata=row.metadata_json,
        created_at=row.created_at,
    )
