from fastapi import APIRouter, Depends, HTTPException, status

from apps.api_service.app.core.security import require_api_key
from libs.registry import RegistryError, load_registry

router = APIRouter(prefix="/v1/registry", tags=["registry"], dependencies=[Depends(require_api_key)])


@router.get("/souls")
async def list_souls() -> list[dict]:
    registry = load_registry()
    return [item.model_dump(mode="json") for item in registry.list_souls()]


@router.get("/souls/{soul_id}")
async def get_soul(soul_id: str) -> dict:
    registry = load_registry()
    try:
        soul = registry.get_soul(soul_id)
    except RegistryError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return soul.model_dump(mode="json")


@router.get("/skills")
async def list_skills() -> list[dict]:
    registry = load_registry()
    return [item.model_dump(mode="json") for item in registry.list_skills()]


@router.get("/skills/{skill_name}")
async def get_skill(skill_name: str) -> dict:
    registry = load_registry()
    try:
        skill = registry.get_skill(skill_name)
    except RegistryError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return skill.model_dump(mode="json")
