"""
API v1 router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import webhooks, speech, llm, agents, research

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["webhooks"]
)

api_router.include_router(
    speech.router,
    prefix="/speech",
    tags=["speech"]
)

api_router.include_router(
    llm.router,
    prefix="/llm",
    tags=["llm"]
)

api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["agents"]
)

api_router.include_router(
    research.router,
    prefix="/research",
    tags=["research"]
)