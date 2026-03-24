from fastapi import FastAPI

from apps.api_service.app.api import (
    agent,
    execution_records,
    events,
    health,
    improvement,
    proposals,
    registry,
    research_reports,
    reviews,
    strategies,
    tasks,
    trading_plans,
    workflows,
)

app = FastAPI(
    title="tradechain api-service",
    version="0.2.0",
    description="Unified external API gateway for soul/skill-aware planning flows.",
)

app.include_router(health.router)
app.include_router(improvement.router)
app.include_router(tasks.router)
app.include_router(events.router)
app.include_router(proposals.router)
app.include_router(reviews.router)
app.include_router(registry.router)
app.include_router(research_reports.router)
app.include_router(strategies.router)
app.include_router(trading_plans.router)
app.include_router(execution_records.router)
app.include_router(workflows.router)
app.include_router(agent.router)
