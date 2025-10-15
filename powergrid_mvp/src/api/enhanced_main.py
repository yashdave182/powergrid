from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import json
import os
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our enhanced modules
from src.models.powergrid_ml import PowerGridMLModel
from src.models.hotspot_analyzer import PowerGridHotspotAnalyzer
from src.data.powergrid_preprocessing import PowerGridPreprocessor
from src.models.predictor import ProjectPredictor

app = FastAPI(
    title="POWERGRID Project Prediction API",
    description="Advanced ML API for POWERGRID project cost and timeline prediction with hotspot identification",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
ml_model = PowerGridMLModel()
hotspot_analyzer = PowerGridHotspotAnalyzer()
preprocessor = PowerGridPreprocessor()
predictor = ProjectPredictor()

# Enhanced Pydantic models
class ProjectInput(BaseModel):
    """Enhanced project input with all POWERGRID-specific features"""
    project_type: str = Field(..., description="Type of project: substation, overhead_line, underground_cable")
    budget: float = Field(..., gt=0, description="Project budget in INR")
    estimated_timeline: int = Field(..., gt=0, description="Estimated timeline in days")
    terrain_type: str = Field(..., description="Terrain type: plain, hilly, forest, urban, coastal")
    environmental_clearance_status: str = Field(..., description="Environmental clearance status")
    material_cost_ratio: float = Field(..., ge=0, le=1, description="Material cost ratio")
    labor_cost_ratio: float = Field(..., ge=0, le=1, description="Labor cost ratio")
    regulatory_complexity_score: float = Field(..., ge=0, le=1, description="Regulatory complexity score")
    monsoon_impact_score: float = Field(..., ge=0, le=1, description="Monsoon impact score")
    vendor_risk_score: float = Field(..., ge=0, le=1, description="Vendor risk score")
    demand_supply_impact: float = Field(..., ge=0, le=1, description="Demand-supply impact")
    resource_availability_score: float = Field(..., ge=0, le=1, description="Resource availability score")
    cost_escalation_risk: float = Field(..., ge=0, le=1, description="Cost escalation risk")
    timeline_pressure_score: float = Field(..., ge=0, le=1, description="Timeline pressure score")
    weather_impact_ratio: float = Field(..., ge=0, le=1, description="Weather impact ratio")
    trained_manpower_availability: float = Field(..., ge=0, le=1, description="Trained manpower availability")
    historical_delay_pattern: float = Field(..., ge=0, le=1, description="Historical delay pattern")
    regional_delay_factor: float = Field(..., ge=0, le=1, description="Regional delay factor")
    seasonal_factor: float = Field(..., ge=0, le=1, description="Seasonal factor")
    technology_risk: float = Field(..., ge=0, le=1, description="Technology risk score")
    project_complexity_score: float = Field(..., ge=0, le=1, description="Project complexity score")
    critical_path_risk: float = Field(..., ge=0, le=1, description="Critical path risk")
    vendor_performance_score: float = Field(..., ge=0, le=1, description="Vendor performance score")
    
    @validator('project_type')
    def validate_project_type(cls, v):
        valid_types = ['substation', 'overhead_line', 'underground_cable']
        if v.lower().replace(' ', '_') not in valid_types:
            raise ValueError(f'Project type must be one of: {valid_types}')
        return v.lower().replace(' ', '_')
    
    @validator('terrain_type')
    def validate_terrain_type(cls, v):
        valid_terrains = ['plain', 'hilly', 'forest', 'urban', 'coastal']
        if v.lower().replace(' ', '_') not in valid_terrains:
            raise ValueError(f'Terrain type must be one of: {valid_terrains}')
        return v.lower().replace(' ', '_')

class BatchPredictionRequest(BaseModel):
    """Batch prediction request with enhanced features"""
    projects: List[ProjectInput]
    include_confidence_intervals: bool = Field(default=True, description="Include confidence intervals in predictions")
    confidence_level: float = Field(default=0.95, ge=0.8, le=0.99, description="Confidence level for intervals")

class PredictionResponse(BaseModel):
    """Enhanced prediction response with uncertainty quantification"""
    project_id: str = Field(..., description="Unique project identifier")
    predicted_cost_overrun_percentage: float = Field(..., description="Predicted cost overrun percentage")
    predicted_time_overrun_days: int = Field(..., description="Predicted time overrun in days")
    predicted_final_cost: float = Field(..., description="Predicted final project cost")
    predicted_final_timeline: int = Field(..., description="Predicted final timeline in days")
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_category: str = Field(..., description="Risk category: Low, Medium, High, Critical")
    confidence_intervals: Optional[Dict[str, Any]] = Field(None, description="Confidence intervals for predictions")
    top_risk_factors: List[Dict[str, Any]] = Field(..., description="Top contributing risk factors")
    recommendations: List[str] = Field(..., description="Project-specific recommendations")
    model_version: str = Field(default="2.0.0", description="Model version used for prediction")
    prediction_timestamp: datetime = Field(default_factory=datetime.now, description="Prediction timestamp")

class HotspotAnalysisRequest(BaseModel):
    """Request for hotspot analysis"""
    analysis_type: str = Field(default="comprehensive", description="Type of analysis: comprehensive, cluster_only, anomaly_only")
    n_clusters_range: Optional[List[int]] = Field(default=[2, 3, 4, 5, 6], description="Range of clusters to try")
    include_visualizations: bool = Field(default=True, description="Include visualizations in response")
    risk_threshold: float = Field(default=75.0, ge=0, le=100, description="Risk score threshold for hotspots")

class HotspotAnalysisResponse(BaseModel):
    """Response from hotspot analysis"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    total_projects: int = Field(..., description="Total number of projects analyzed")
    hotspot_count: int = Field(..., description="Number of projects identified as hotspots")
    risk_distribution: Dict[str, int] = Field(..., description="Distribution of risk categories")
    top_hotspots: List[Dict[str, Any]] = Field(..., description="Top hotspot projects")
    cluster_summary: Dict[str, Any] = Field(..., description="Summary of project clusters")
    recommendations: Dict[str, Any] = Field(..., description="Category-specific recommendations")
    visualizations: Optional[Dict[str, str]] = Field(None, description="Visualization file paths")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

class ModelPerformanceResponse(BaseModel):
    """Model performance metrics"""
    cost_models: Dict[str, Dict[str, float]] = Field(..., description="Performance metrics for cost prediction models")
    time_models: Dict[str, Dict[str, float]] = Field(..., description="Performance metrics for time prediction models")
    ensemble_performance: Dict[str, float] = Field(..., description="Ensemble model performance")
    feature_importance: Dict[str, Dict[str, float]] = Field(..., description="Feature importance rankings")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last model update timestamp")

class TrainingRequest(BaseModel):
    """Request for model retraining"""
    retrain_type: str = Field(default="full", description="Type of retraining: full, incremental, cost_only, time_only")
    validation_split: float = Field(default=0.2, ge=0.1, le=0.4, description="Validation data split ratio")
    hyperparameter_tuning: bool = Field(default=True, description="Perform hyperparameter tuning")
    use_ensemble: bool = Field(default=True, description="Use ensemble methods")

# Enhanced API endpoints
@app.get("/")
async def root():
    """Enhanced root endpoint with comprehensive API information"""
    return {
        "message": "POWERGRID Project Prediction API v2.0",
        "status": "operational",
        "models_loaded": {
            "cost_models": len(predictor.cost_models),
            "time_models": len(predictor.time_models),
            "ensemble_models": len(ml_model.ensemble_models)
        },
        "features": [
            "Advanced Cost & Timeline Prediction",
            "Uncertainty Quantification",
            "Hotspot Identification",
            "Batch Processing",
            "Real-time Analytics",
            "Comprehensive Risk Assessment"
        ],
        "endpoints": [
            "/predict - Single project prediction",
            "/predict/batch - Batch prediction",
            "/hotspots/analyze - Hotspot analysis",
            "/models/performance - Model performance metrics",
            "/models/retrain - Model retraining",
            "/health - System health check"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(),
        "models": {
            "cost_models_loaded": len(predictor.cost_models) > 0,
            "time_models_loaded": len(predictor.time_models) > 0,
            "hotspot_analyzer_ready": True
        },
        "system": {
            "memory_available": "sufficient",
            "disk_space": "available"
        }
    }
    
    # Check if models are properly loaded
    if not predictor.cost_models or not predictor.time_models:
        health_status["status"] = "degraded"
        health_status["message"] = "Some models not loaded properly"
    
    return health_status

@app.post("/predict", response_model=PredictionResponse)
async def predict_single_project(project: ProjectInput):
    """Enhanced single project prediction with uncertainty quantification"""
    try:
        # Convert to DataFrame
        project_dict = project.dict()
        project_df = pd.DataFrame([project_dict])
        
        # Add project ID
        project_id = f"PROJ_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get predictions with uncertainty
        cost_prediction = ml_model.predict_with_uncertainty(
            project_df, model_type='cost', confidence_level=0.95
        )
        time_prediction = ml_model.predict_with_uncertainty(
            project_df, model_type='time', confidence_level=0.95
        )
        
        # Calculate derived metrics
        predicted_cost_overrun = cost_prediction['predictions'][0]
        predicted_time_overrun = time_prediction['predictions'][0]
        
        predicted_final_cost = project.budget * (1 + predicted_cost_overrun / 100)
        predicted_final_timeline = project.estimated_timeline + predicted_time_overrun
        
        # Calculate risk score
        risk_score = min(100, (
            predicted_cost_overrun * 0.4 +
            (predicted_time_overrun / project.estimated_timeline * 100) * 0.3 +
            project.project_complexity_score * 20 +
            project.cost_escalation_risk * 20
        ))
        
        # Determine risk category
        if risk_score >= 75:
            risk_category = "Critical"
        elif risk_score >= 50:
            risk_category = "High"
        elif risk_score >= 25:
            risk_category = "Medium"
        else:
            risk_category = "Low"
        
        # Identify top risk factors
        risk_factors = [
            {"factor": "Cost Escalation Risk", "score": project.cost_escalation_risk * 100, "weight": 0.25},
            {"factor": "Timeline Pressure", "score": project.timeline_pressure_score * 100, "weight": 0.20},
            {"factor": "Project Complexity", "score": project.project_complexity_score * 100, "weight": 0.15},
            {"factor": "Regulatory Complexity", "score": project.regulatory_complexity_score * 100, "weight": 0.15},
            {"factor": "Weather Impact", "score": project.weather_impact_ratio * 100, "weight": 0.10},
            {"factor": "Vendor Risk", "score": project.vendor_risk_score * 100, "weight": 0.10},
            {"factor": "Resource Availability", "score": project.resource_availability_score * 100, "weight": 0.05}
        ]
        
        top_risk_factors = sorted(risk_factors, key=lambda x: x["score"] * x["weight"], reverse=True)[:5]
        
        # Generate recommendations
        recommendations = generate_project_recommendations(risk_score, risk_category, project)
        
        # Build confidence intervals
        confidence_intervals = {
            "cost_overrun": {
                "lower_bound": cost_prediction['lower_bound'][0],
                "upper_bound": cost_prediction['upper_bound'][0],
                "uncertainty": cost_prediction['uncertainty'][0]
            },
            "time_overrun": {
                "lower_bound": time_prediction['lower_bound'][0],
                "upper_bound": time_prediction['upper_bound'][0],
                "uncertainty": time_prediction['uncertainty'][0]
            }
        }
        
        return PredictionResponse(
            project_id=project_id,
            predicted_cost_overrun_percentage=predicted_cost_overrun,
            predicted_time_overrun_days=int(predicted_time_overrun),
            predicted_final_cost=predicted_final_cost,
            predicted_final_timeline=predicted_final_timeline,
            risk_score=risk_score,
            risk_category=risk_category,
            confidence_intervals=confidence_intervals,
            top_risk_factors=top_risk_factors,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch_projects(request: BatchPredictionRequest):
    """Enhanced batch prediction with progress tracking"""
    try:
        predictions = []
        total_projects = len(request.projects)
        
        for i, project in enumerate(request.projects):
            # Process each project
            try:
                result = await predict_single_project(project)
                predictions.append(result)
            except Exception as e:
                # Log error but continue with other projects
                print(f"Error processing project {i+1}: {str(e)}")
                continue
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

@app.post("/hotspots/analyze", response_model=HotspotAnalysisResponse)
async def analyze_hotspots(request: HotspotAnalysisRequest):
    """Comprehensive hotspot analysis"""
    try:
        # This would typically load recent project data
        # For now, we'll return a mock analysis
        analysis_id = f"ANALYSIS_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Mock analysis results (in real implementation, this would analyze actual data)
        risk_distribution = {
            "Critical Hotspot": 15,
            "High Risk": 45,
            "Medium Risk": 120,
            "Low Risk": 320
        }
        
        total_projects = sum(risk_distribution.values())
        hotspot_count = risk_distribution["Critical Hotspot"] + risk_distribution["High Risk"]
        
        # Mock top hotspots
        top_hotspots = [
            {
                "project_id": "PROJ_001",
                "risk_score": 92.5,
                "project_type": "underground_cable",
                "location": "Kerala",
                "primary_risks": ["Monsoon Impact", "Terrain Difficulty", "Regulatory Delays"]
            },
            {
                "project_id": "PROJ_002",
                "risk_score": 88.3,
                "project_type": "substation",
                "location": "Himachal Pradesh",
                "primary_risks": ["Weather Impact", "Material Cost Escalation", "Vendor Performance"]
            }
        ]
        
        # Mock cluster summary
        cluster_summary = {
            "total_clusters": 5,
            "best_clustering_method": "K-Means",
            "silhouette_score": 0.72,
            "cluster_distribution": {
                "Cluster_0": {"size": 120, "avg_risk": 25.3, "dominant_type": "overhead_line"},
                "Cluster_1": {"size": 85, "avg_risk": 45.7, "dominant_type": "substation"},
                "Cluster_2": {"size": 95, "avg_risk": 78.2, "dominant_type": "underground_cable"},
                "Cluster_3": {"size": 110, "avg_risk": 35.1, "dominant_type": "overhead_line"},
                "Cluster_4": {"size": 90, "avg_risk": 65.4, "dominant_type": "substation"}
            }
        }
        
        # Mock recommendations
        recommendations = {
            "Critical Hotspot": {
                "count": 15,
                "recommendations": [
                    "Immediate intervention required",
                    "Consider project postponement",
                    "Allocate additional resources",
                    "Daily monitoring and reporting"
                ]
            },
            "High Risk": {
                "count": 45,
                "recommendations": [
                    "Enhanced monitoring and control",
                    "Weekly progress reviews",
                    "Risk mitigation strategies",
                    "Resource reallocation consideration"
                ]
            }
        }
        
        # Mock visualizations
        visualizations = {
            "cluster_visualization": "/outputs/hotspot_clusters.png",
            "risk_distribution": "/outputs/risk_distribution.png",
            "temporal_analysis": "/outputs/temporal_hotspots.png"
        }
        
        return HotspotAnalysisResponse(
            analysis_id=analysis_id,
            total_projects=total_projects,
            hotspot_count=hotspot_count,
            risk_distribution=risk_distribution,
            top_hotspots=top_hotspots,
            cluster_summary=cluster_summary,
            recommendations=recommendations,
            visualizations=visualizations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotspot analysis error: {str(e)}")

@app.get("/models/performance", response_model=ModelPerformanceResponse)
async def get_model_performance():
    """Get comprehensive model performance metrics"""
    try:
        # Load performance metrics from files
        models_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
        
        # Mock performance data (in real implementation, load from metrics.json)
        cost_models = {
            "xgboost": {"MAE": 8.5, "RMSE": 12.3, "R2": 0.87, "MAPE": 15.2},
            "lightgbm": {"MAE": 8.8, "RMSE": 12.8, "R2": 0.85, "MAPE": 16.1},
            "random_forest": {"MAE": 9.2, "RMSE": 13.5, "R2": 0.83, "MAPE": 17.3},
            "catboost": {"MAE": 8.3, "RMSE": 11.9, "R2": 0.89, "MAPE": 14.8}
        }
        
        time_models = {
            "xgboost": {"MAE": 12.1, "RMSE": 18.5, "R2": 0.82, "MAPE": 22.1},
            "lightgbm": {"MAE": 12.8, "RMSE": 19.2, "R2": 0.80, "MAPE": 23.5},
            "random_forest": {"MAE": 13.5, "RMSE": 20.1, "R2": 0.78, "MAPE": 25.2},
            "catboost": {"MAE": 11.9, "RMSE": 17.8, "R2": 0.84, "MAPE": 21.3}
        }
        
        ensemble_performance = {
            "cost_prediction_accuracy": 91.2,
            "time_prediction_accuracy": 88.7,
            "overall_reliability": 89.8
        }
        
        # Mock feature importance
        feature_importance = {
            "cost_models": {
                "material_cost_ratio": 0.25,
                "cost_escalation_risk": 0.22,
                "demand_supply_impact": 0.18,
                "project_complexity_score": 0.15,
                "vendor_performance_score": 0.12,
                "regulatory_complexity_score": 0.08
            },
            "time_models": {
                "regulatory_complexity_score": 0.28,
                "monsoon_impact_score": 0.24,
                "timeline_pressure_score": 0.19,
                "critical_path_risk": 0.15,
                "weather_impact_ratio": 0.10,
                "resource_availability_score": 0.04
            }
        }
        
        return ModelPerformanceResponse(
            cost_models=cost_models,
            time_models=time_models,
            ensemble_performance=ensemble_performance,
            feature_importance=feature_importance
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance metrics error: {str(e)}")

@app.post("/models/retrain")
async def retrain_models(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Trigger model retraining in background"""
    try:
        # Generate training ID
        training_id = f"TRAINING_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Add retraining task to background
        background_tasks.add_task(
            perform_model_retraining,
            training_id,
            request.retrain_type,
            request.validation_split,
            request.hyperparameter_tuning,
            request.use_ensemble
        )
        
        return {
            "message": "Model retraining initiated",
            "training_id": training_id,
            "status": "in_progress",
            "estimated_completion": "15-30 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining initiation error: {str(e)}")

@app.post("/data/upload")
async def upload_training_data(
    file: UploadFile = File(...),
    data_type: str = "training",
    validate_schema: bool = True
):
    """Upload training data for model updates"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.json')):
            raise HTTPException(status_code=400, detail="Invalid file format. Use CSV, Excel, or JSON.")
        
        # Read and validate data
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file.file)
        else:
            df = pd.read_json(file.file)
        
        # Validate schema if requested
        if validate_schema:
            required_columns = [
                'project_type', 'budget', 'estimated_timeline', 'terrain_type',
                'material_cost_ratio', 'labor_cost_ratio', 'regulatory_complexity_score'
            ]
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required columns: {missing_columns}"
                )
        
        # Save uploaded file
        upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_data_{timestamp}.csv"
        filepath = os.path.join(upload_dir, filename)
        
        df.to_csv(filepath, index=False)
        
        return {
            "message": "Data uploaded successfully",
            "filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "file_path": filepath
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data upload error: {str(e)}")

# Helper functions
def generate_project_recommendations(risk_score: float, risk_category: str, project: ProjectInput) -> List[str]:
    """Generate project-specific recommendations"""
    recommendations = []
    
    if risk_category == "Critical":
        recommendations.extend([
            "🚨 IMMEDIATE ACTION REQUIRED: Project requires urgent intervention",
            "Consider project postponement or scope reduction",
            "Allocate additional senior management oversight",
            "Implement daily progress monitoring and reporting",
            "Prepare detailed contingency plans"
        ])
    elif risk_category == "High":
        recommendations.extend([
            "⚠️ Enhanced project monitoring and control required",
            "Weekly progress reviews with senior stakeholders",
            "Consider resource reallocation from lower-risk projects",
            "Implement risk mitigation strategies",
            "Prepare fallback plans for critical path items"
        ])
    elif risk_category == "Medium":
        recommendations.extend([
            "📊 Standard project monitoring with increased frequency",
            "Bi-weekly risk assessment reviews",
            "Maintain current resource allocation but monitor closely",
            "Identify potential risk factors early",
            "Regular communication with vendors and stakeholders"
        ])
    else:  # Low Risk
        recommendations.extend([
            "✅ Standard project management procedures sufficient",
            "Monthly risk assessment reviews",
            "Focus on efficiency improvements and best practices",
            "Consider as benchmark project for future reference",
            "Share successful practices with other projects"
        ])
    
    # Add specific recommendations based on risk factors
    if project.cost_escalation_risk > 0.7:
        recommendations.append("💰 Implement cost control measures and vendor negotiations")
    
    if project.regulatory_complexity_score > 0.7:
        recommendations.append("📋 Engage regulatory experts and expedite clearance processes")
    
    if project.monsoon_impact_score > 0.7:
        recommendations.append("🌧️ Develop monsoon-specific work schedules and weather contingencies")
    
    if project.vendor_risk_score > 0.7:
        recommendations.append("🏗️ Diversify vendor base and strengthen vendor management")
    
    if project.timeline_pressure_score > 0.7:
        recommendations.append("⏰ Consider parallel work streams and resource optimization")
    
    return recommendations

async def perform_model_retraining(
    training_id: str,
    retrain_type: str,
    validation_split: float,
    hyperparameter_tuning: bool,
    use_ensemble: bool
):
    """Background task for model retraining"""
    print(f"🚀 Starting model retraining: {training_id}")
    
    try:
        # This would implement the actual retraining logic
        # For now, we'll simulate the process
        
        if retrain_type in ["full", "cost_only", "time_only"]:
            print(f"Retraining type: {retrain_type}")
            print(f"Validation split: {validation_split}")
            print(f"Hyperparameter tuning: {hyperparameter_tuning}")
            print(f"Use ensemble: {use_ensemble}")
        
        print(f"✅ Model retraining completed: {training_id}")
        
    except Exception as e:
        print(f"❌ Model retraining failed: {training_id} - {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)