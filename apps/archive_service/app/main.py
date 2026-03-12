from fastapi import FastAPI

from apps.archive_service.app.api import internal

app = FastAPI(
    title="tradechain archive-service",
    version="0.1.0",
    description="Archive writer and lookup service for object persistence and traceability.",
)


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(internal.router)
