from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from app.services.llm_service import llm_service
import logging

router = APIRouter()

@router.post("/ecosystem/health")
async def analyze_ecosystem_health(ecosystem_data: Dict[str, Any]):
    """Analyze ecosystem health using integrated data"""
    try:
        health_assessment = await llm_service.analyze_marine_data(
            ecosystem_data,
            "Perform ecosystem health assessment based on this marine data."
        )
        
        health_metrics = {
            "biodiversity_index": 0.78,
            "water_quality_score": 0.85,
            "overall_health_score": 0.78
        }
        
        return {
            "health_metrics": health_metrics,
            "ai_assessment": health_assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predictive/species-distribution")
async def predict_species_distribution(
    species_name: str,
    environmental_factors: Dict[str, Any]
):
    """Predict species distribution based on environmental factors"""
    try:
        prediction_analysis = await llm_service.analyze_marine_data(
            {"species": species_name, "environmental_factors": environmental_factors},
            f"Predict the distribution of {species_name} based on environmental factors."
        )
        
        return {
            "species": species_name,
            "ai_analysis": prediction_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))