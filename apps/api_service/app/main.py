from fastapi import FastAPI

from apps.api_service.app.api import agent, events, health, proposals, tasks, workflows

app = FastAPI(
    title="tradechain api-service",
    version="0.1.0",
    description="Unified external API gateway for Sprint 1-2.",
)

app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(events.router)
app.include_router(proposals.router)
app.include_router(workflows.router)
app.include_router(agent.router)
