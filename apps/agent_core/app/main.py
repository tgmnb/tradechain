from fastapi import FastAPI

from apps.agent_core.app.api import internal_graphs

app = FastAPI(
    title="tradechain agent-core",
    version="0.1.0",
    description="LangGraph orchestration core for Sprint 2 event->proposal loop.",
)


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(internal_graphs.router)
