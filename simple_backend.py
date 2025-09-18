#!/usr/bin/env python3
"""
Simple FastAPI backend to resolve the health endpoint 404 error
Run this with: python simple_backend.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Simple Marine Data Backend")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Simple backend is running"}

@app.get("/api/v1/health")
async def api_health_check():
    return {"status": "healthy", "message": "API v1 is running"}

@app.get("/")
async def root():
    return {
        "message": "Simple Marine Data Platform Backend",
        "endpoints": {
            "health": "/health",
            "api_health": "/api/v1/health"
        }
    }

if __name__ == "__main__":
    print("Starting simple backend server...")
    print("Health endpoints:")
    print("  - http://localhost:8000/health")
    print("  - http://localhost:8000/api/v1/health")
    print("  - Frontend should now work without 404 errors")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )