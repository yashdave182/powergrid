from fastapi import APIRouter
from app.api.v1 import biodiversity, oceanography, data_integration, analytics, ai

api_router = APIRouter()

# Health check endpoint for API
@api_router.get("/health")
async def api_health_check():
    return {"status": "healthy", "message": "Marine Data Platform API v1 is running"}

# Explicit OPTIONS handler for API health endpoint
@api_router.options("/health")
async def api_health_check_options():
    return {}

# Include all API route modules
api_router.include_router(
    biodiversity.router,
    prefix="/biodiversity",
    tags=["biodiversity"]
)

api_router.include_router(
    oceanography.router,
    prefix="/oceanography", 
    tags=["oceanography"]
)

api_router.include_router(
    data_integration.router,
    prefix="/data-integration",
    tags=["data-integration"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["ai"]
)