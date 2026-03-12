from fastapi import APIRouter, Depends, Header, HTTPException, status

from apps.ingestion_service.app.adapters.mock_news import MockNewsAdapter
from libs.contracts.event import IngestionFetchRequest, IngestionFetchResponse

router = APIRouter(prefix="/internal/ingestion", tags=["ingestion"])


def require_internal_key(x_api_key: str | None = Header(default=None)) -> None:
    from os import getenv

    expected = getenv("INTERNAL_SERVICE_API_KEY", "internal-dev-key")
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid internal API key")


@router.post("/fetch", response_model=IngestionFetchResponse, dependencies=[Depends(require_internal_key)])
async def fetch_events(payload: IngestionFetchRequest) -> IngestionFetchResponse:
    adapter = MockNewsAdapter()
    events = await adapter.fetch(limit=payload.limit)
    return IngestionFetchResponse(events=events)
