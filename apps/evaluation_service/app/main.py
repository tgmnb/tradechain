from fastapi import FastAPI

from apps.evaluation_service.app.api import internal

app = FastAPI(
    title="tradechain evaluation-service",
    version="0.1.0",
    description="Placeholder evaluation service for Sprint 1-2.",
)


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(internal.router)
