from fastapi import APIRouter, Depends, Header, HTTPException, status

router = APIRouter(prefix="/internal/evaluation", tags=["evaluation"])


def require_internal_key(x_api_key: str | None = Header(default=None)) -> None:
    from os import getenv

    expected = getenv("INTERNAL_SERVICE_API_KEY", "internal-dev-key")
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid internal API key")


@router.post("/run", dependencies=[Depends(require_internal_key)])
async def run_evaluation_placeholder() -> dict:
    return {
        "status": "placeholder",
        "message": "evaluation pipeline is reserved for Sprint 5+",
        "next": ["agent_scores", "improvement_tickets"],
    }
