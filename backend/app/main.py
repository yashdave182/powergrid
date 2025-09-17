from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from app.config import settings
from app.api.routes import api_router
from app.core.database import engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Marine Data Platform API",
    description="AI-Driven Unified Data Platform for Oceanographic, Fisheries, and Molecular Biodiversity Insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
# Compute safe CORS settings: Star origin cannot be used with credentials=True
if settings.debug:
    cors_origins = ["*"]
    cors_allow_credentials = False
else:
    cors_origins = settings.allowed_origins
    cors_allow_credentials = True

logger.info("CORS configuration: origins=%s, allow_credentials=%s", cors_origins, cors_allow_credentials)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Marine Data Platform API...")
    # Database table creation disabled for development
    # Uncomment when database is properly configured:
    # Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Marine Data Platform API...")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Marine Data Platform API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Marine Data Platform API",
        "docs_url": "/docs",
        "health_check": "/health"
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )