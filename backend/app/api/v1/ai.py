from fastapi import APIRouter, HTTPException, Depends
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from app.services.ai_service import ai_service
from app.services.external_apis import obis_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai"])

class AnalysisRequest(BaseModel):
    data: Dict[str, Any]

class ConservationRequest(BaseModel):
    species_data: List[Dict[str, Any]]

class BiodiversityRequest(BaseModel):
    occurrence_data: Dict[str, Any]

class ChatRequest(BaseModel):
    question: str
    context_data: Optional[Dict[str, Any]] = None

@router.post("/analyze-marine-data")
async def analyze_marine_data(request: AnalysisRequest):
    """Analyze marine biodiversity data using Gemini AI."""
    try:
        result = await ai_service.analyze_marine_data(request.data)
        return result
    except Exception as e:
        logger.error(f"Error in marine data analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/conservation-recommendations")
async def generate_conservation_recommendations(request: ConservationRequest):
    """Generate conservation recommendations based on species data."""
    try:
        result = await ai_service.generate_conservation_recommendations(request.species_data)
        return result
    except Exception as e:
        logger.error(f"Error generating conservation recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Conservation analysis failed: {str(e)}")

@router.post("/explain-biodiversity")
async def explain_biodiversity_patterns(request: BiodiversityRequest):
    """Explain biodiversity patterns from occurrence data."""
    try:
        result = await ai_service.explain_biodiversity_patterns(request.occurrence_data)
        return result
    except Exception as e:
        logger.error(f"Error explaining biodiversity patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

@router.post("/chat")
async def chat_about_marine_data(request: ChatRequest):
    """Interactive chat about marine data and biodiversity."""
    try:
        result = await ai_service.chat_about_marine_data(request.question, request.context_data)
        return result
    except Exception as e:
        logger.error(f"Error in marine data chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/analyze-obis-dataset/{dataset_id}")
async def analyze_obis_dataset(dataset_id: str):
    """Fetch OBIS dataset and analyze it with AI."""
    try:
        # Fetch dataset from OBIS
        dataset_data = await obis_client.get_dataset_details(dataset_id)
        
        if "error" in dataset_data:
            raise HTTPException(status_code=400, detail=dataset_data["error"])
        
        # Analyze with AI
        analysis = await ai_service.analyze_marine_data(dataset_data)
        
        return {
            "dataset": dataset_data,
            "ai_analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error analyzing OBIS dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dataset analysis failed: {str(e)}")

@router.get("/quick-insights")
async def get_quick_marine_insights():
    """Get quick AI insights about marine biodiversity trends."""
    try:
        # Fetch some sample data from OBIS
        sample_data = await obis_client.get_datasets(limit=10)
        
        if "error" in sample_data:
            # Provide general insights if OBIS is unavailable
            question = "What are the current major trends and challenges in marine biodiversity conservation?"
        else:
            question = f"Based on recent marine biodiversity datasets, what are the key conservation priorities?"
        
        insights = await ai_service.chat_about_marine_data(question, sample_data if "error" not in sample_data else None)
        
        return {
            "insights": insights,
            "data_source": "OBIS API" if "error" not in sample_data else "General Knowledge"
        }
    except Exception as e:
        logger.error(f"Error getting quick insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@router.get("/test")
async def test_ai_service():
    """Test the AI service connection."""
    try:
        test_data = {
            "species_count": 25,
            "location": "Pacific Ocean",
            "depth_range": "0-200m",
            "temperature": "15-25°C"
        }
        
        result = await ai_service.analyze_marine_data(test_data)
        
        return {
            "status": "success",
            "test_result": result,
            "message": "Gemini AI service is working correctly"
        }
    except Exception as e:
        logger.error(f"AI service test failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Gemini AI service test failed"
        }