from fastapi import FastAPI

from apps.ingestion_service.app.api import internal

app = FastAPI(
    title="tradechain ingestion-service",
    version="0.1.0",
    description="Mock-based ingestion with provider adapter abstraction.",
)


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(internal.router)
