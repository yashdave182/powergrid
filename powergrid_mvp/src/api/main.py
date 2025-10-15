from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.predictor import ProjectPredictor

# Initialize FastAPI
app = FastAPI(
    title="POWERGRID Project Prediction API",
    description="MVP API for predicting project cost and timeline overruns",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
predictor = ProjectPredictor()

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    predictor.load_models()
    print("✅ Models loaded successfully")

# Pydantic models
class ProjectInput(BaseModel):
    project_id: str
    project_type: str
    region: str
    terrain_type: str
    length_km: float
    voltage_level_kv: int
    terrain_difficulty_score: float
    num_towers: int
    estimated_cost_inr: float
    material_cost_inr: float
    labor_cost_inr: float
    estimated_duration_days: int
    steel_cost_per_ton: float
    copper_cost_per_ton: float
    total_steel_tons: float
    total_copper_tons: float
    estimated_manpower: int
    labor_cost_per_day: float
    vendor_quality_score: float
    vendor_on_time_rate: float
    vendor_cost_efficiency: float
    adverse_weather_days: int
    monsoon_affected_months: int
    permit_approval_days: int
    environmental_clearance_days: int
    project_complexity_score: float
    start_date: str
    start_month: int
    start_quarter: int
    is_monsoon_start: int

class PredictionResponse(BaseModel):
    project_id: str
    estimated_cost_inr: float
    predicted_cost_inr: float
    cost_overrun_percentage: float
    cost_overrun_inr: float
    estimated_duration_days: int
    predicted_duration_days: int
    time_overrun_percentage: float
    time_overrun_days: int
    risk_score: float
    risk_category: str
    priority: str

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "POWERGRID Project Prediction API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": len(predictor.cost_models) > 0
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_project(project: ProjectInput):
    """
    Predict cost and timeline for a single project
    """
    try:
        result = predictor.predict(project.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_predict")
async def batch_predict(projects: List[ProjectInput]):
    """
    Predict for multiple projects
    """
    try:
        projects_dict = [p.dict() for p in projects]
        results = predictor.batch_predict(projects_dict)
        return {"predictions": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/info")
async def models_info():
    """
    Get information about loaded models
    """
    return {
        "cost_models": list(predictor.cost_models.keys()),
        "time_models": list(predictor.time_models.keys()),
        "feature_count": len(predictor.feature_names)
    }

# Run with: uvicorn src.api.main:app --reload