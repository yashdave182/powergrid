from fastapi import APIRouter
from app.api.v1 import biodiversity, oceanography, data_integration, analytics

api_router = APIRouter()

# Health check endpoint for API
@api_router.get("/health")
async def api_health_check():
    return {"status": "healthy", "message": "Marine Data Platform API v1 is running"}

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