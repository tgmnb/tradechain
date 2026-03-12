from pydantic import Field

from libs.contracts.base import ContractModel
from libs.contracts.enums import ErrorCode


class ErrorResponse(ContractModel):
    error_code: ErrorCode
    message: str
    request_id: str | None = Field(default=None)
