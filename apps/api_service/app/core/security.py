from fastapi import Header, HTTPException, status

from libs.contracts.enums import ErrorCode

from apps.api_service.app.core.config import get_settings


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if x_api_key != settings.api_service_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": ErrorCode.UNAUTHORIZED, "message": "invalid API key"},
        )
