from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from libs.contracts.base import ContractModel


class ArchiveCreate(ContractModel):
    object_type: str = Field(max_length=50)
    object_id: UUID
    payload: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    storage_type: str = Field(default="minio", max_length=30)


class ArchiveRef(ContractModel):
    id: UUID
    object_type: str
    object_id: UUID
    archive_key: str
    storage_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
