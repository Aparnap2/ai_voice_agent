"""
API v1 router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import webhooks

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["webhooks"]
)