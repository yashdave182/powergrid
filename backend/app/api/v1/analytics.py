<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.models.marine_data import (
    UnifiedMarineData, OceanographicData, FisheriesData, 
    TaxonomicData, MolecularData
)
from app.services.ai_service import ai_service
import logging
import json
import math

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/ecosystem/health")
async def analyze_ecosystem_health(
    region: Optional[str] = Query(None),
    latitude_min: Optional[float] = Query(None),
    latitude_max: Optional[float] = Query(None),
    longitude_min: Optional[float] = Query(None),
    longitude_max: Optional[float] = Query(None),
    time_period_months: int = Query(12, description="Time period for analysis in months"),
    db: Session = Depends(get_db)
):
    """Comprehensive ecosystem health analysis integrating all data types"""
    try:
        # Define time range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_period_months * 30)
        
        # Base query filters
        base_filters = [UnifiedMarineData.collection_date >= start_date]
        
        if region:
            base_filters.append(UnifiedMarineData.region.ilike(f"%{region}%"))
        if latitude_min is not None:
            base_filters.append(UnifiedMarineData.latitude >= latitude_min)
        if latitude_max is not None:
            base_filters.append(UnifiedMarineData.latitude <= latitude_max)
        if longitude_min is not None:
            base_filters.append(UnifiedMarineData.longitude >= longitude_min)
        if longitude_max is not None:
            base_filters.append(UnifiedMarineData.longitude <= longitude_max)
        
        # Collect data from all sources
        ecosystem_data = {
            "oceanographic": {},
            "biodiversity": {},
            "water_quality": {},
            "species_health": {}
        }
        
        # Oceanographic indicators
        ocean_query = db.query(UnifiedMarineData, OceanographicData).join(
            OceanographicData, UnifiedMarineData.id == OceanographicData.unified_data_id
        ).filter(and_(*base_filters, UnifiedMarineData.data_type == "oceanographic"))
        
        ocean_results = ocean_query.all()
        
        if ocean_results:
            temps = [r[1].temperature for r in ocean_results if r[1].temperature]
            ph_values = [r[1].ph for r in ocean_results if r[1].ph]
            oxygen_levels = [r[1].dissolved_oxygen for r in ocean_results if r[1].dissolved_oxygen]
            
            ecosystem_data["oceanographic"] = {
                "temperature": {
                    "mean": sum(temps) / len(temps) if temps else None,
                    "range": [min(temps), max(temps)] if temps else None,
                    "samples": len(temps)
                },
                "ph": {
                    "mean": sum(ph_values) / len(ph_values) if ph_values else None,
                    "range": [min(ph_values), max(ph_values)] if ph_values else None,
                    "samples": len(ph_values)
                },
                "dissolved_oxygen": {
                    "mean": sum(oxygen_levels) / len(oxygen_levels) if oxygen_levels else None,
                    "range": [min(oxygen_levels), max(oxygen_levels)] if oxygen_levels else None,
                    "samples": len(oxygen_levels)
                }
            }
        
        # Biodiversity indicators
        bio_query = db.query(UnifiedMarineData).filter(
            and_(*base_filters, 
                 or_(UnifiedMarineData.data_type == "fisheries", 
                     UnifiedMarineData.data_type == "molecular"),
                 UnifiedMarineData.scientific_name.is_not(None))
        )
        
        bio_results = bio_query.all()
        
        if bio_results:
            species_count = len(set(r.scientific_name for r in bio_results))
            family_count = len(set(r.family for r in bio_results if r.family is not None))
            
            ecosystem_data["biodiversity"] = {
                "species_richness": species_count,
                "family_richness": family_count,
                "total_observations": len(bio_results)
            }
        
        # Calculate overall ecosystem health score
        health_score = 0.0
        score_components = []
        
        # Water quality component (40%)
        if ecosystem_data["oceanographic"]:
            water_score = 0.0
            if ecosystem_data["oceanographic"]["ph"]["mean"]:
                ph_mean = ecosystem_data["oceanographic"]["ph"]["mean"]
                ph_score = max(0, 1 - abs(ph_mean - 8.1) / 1.0)  # Optimal marine pH ~8.1
                water_score += ph_score * 0.5
            
            if ecosystem_data["oceanographic"]["dissolved_oxygen"]["mean"]:
                do_mean = ecosystem_data["oceanographic"]["dissolved_oxygen"]["mean"]
                do_score = min(1.0, do_mean / 8.0)  # Optimal >8 mg/L
                water_score += do_score * 0.5
            
            health_score += water_score * 0.4
            score_components.append({"component": "water_quality", "score": water_score, "weight": 0.4})
        
        # Biodiversity component (60%)
        if ecosystem_data["biodiversity"]:
            bio_score = min(1.0, ecosystem_data["biodiversity"]["species_richness"] / 50.0)
            health_score += bio_score * 0.6
            score_components.append({"component": "biodiversity", "score": bio_score, "weight": 0.6})
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "ecosystem_health_assessment",
            "region": region,
            "time_period_months": time_period_months,
            "ecosystem_data": ecosystem_data,
            "health_score": health_score
        })
        
        return {
            "analysis_parameters": {
                "region": region,
                "time_period_months": time_period_months
            },
            "ecosystem_health_score": round(health_score, 3),
            "health_rating": (
                "Excellent" if health_score > 0.8 else
                "Good" if health_score > 0.6 else
                "Fair" if health_score > 0.4 else
                "Poor"
            ),
            "score_components": score_components,
            "ecosystem_indicators": ecosystem_data,
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze ecosystem health: {e}")
        raise HTTPException(status_code=500, detail=f"Ecosystem analysis failed: {str(e)}")

@router.get("/biodiversity/summary")
async def get_biodiversity_summary(
    region: Optional[str] = Query(None),
    data_type: Optional[str] = Query(None, description="fisheries, molecular, or all"),
    db: Session = Depends(get_db)
):
    """Get comprehensive biodiversity summary across all data types"""
    try:
        # Build query
        query = db.query(UnifiedMarineData).filter(
            UnifiedMarineData.scientific_name.is_not(None)
        )
        
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        
        if data_type and data_type != "all":
            query = query.filter(UnifiedMarineData.data_type == data_type)
        else:
            query = query.filter(or_(
                UnifiedMarineData.data_type == "fisheries",
                UnifiedMarineData.data_type == "molecular",
                UnifiedMarineData.data_type == "taxonomic"
            ))
        
        results = query.all()
        
        # Calculate biodiversity metrics
        species = set()
        families = set()
        orders = set()
        classes = set()
        data_sources = set()
        
        for record in results:
            if record.scientific_name is not None:
                species.add(record.scientific_name)
            if record.family is not None:
                families.add(record.family)
            if record.order is not None:
                orders.add(record.order)
            if record.class_name is not None:
                classes.add(record.class_name)
            data_sources.add(record.data_type)
        
        biodiversity_summary = {
            "species_richness": len(species),
            "family_richness": len(families),
            "order_richness": len(orders),
            "class_richness": len(classes),
            "total_records": len(results),
            "data_sources": list(data_sources),
            "top_species": [],
            "top_families": []
        }
        
        # Get most common species and families
        from collections import Counter
        species_counts = Counter(r.scientific_name for r in results if r.scientific_name is not None)
        family_counts = Counter(r.family for r in results if r.family is not None)
        
        biodiversity_summary["top_species"] = species_counts.most_common(10)
        biodiversity_summary["top_families"] = family_counts.most_common(10)
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "biodiversity_summary",
            "region": region,
            "data_type": data_type,
            "biodiversity_summary": biodiversity_summary
        })
        
        return {
            "region": region,
            "data_type": data_type or "all",
            "biodiversity_summary": biodiversity_summary,
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to get biodiversity summary: {e}")
        raise HTTPException(status_code=500, detail=f"Biodiversity summary failed: {str(e)}")

@router.get("/data/quality-overview")
async def get_data_quality_overview(
    data_type: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get overview of data quality across the platform"""
    try:
        # Build query
        query = db.query(UnifiedMarineData)
        
        if data_type:
            query = query.filter(UnifiedMarineData.data_type == data_type)
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        
        results = query.all()
        
        # Calculate quality metrics
        total_records = len(results)
        validated_records = len([r for r in results if r.is_validated is True])
        
        # Count high quality records
        high_quality_records = 0
        for r in results:
            try:
                score = getattr(r, 'data_quality_score', None)
                if score is not None and score > 0.8:
                    high_quality_records += 1
            except (TypeError, AttributeError):
                continue
        
        # Group by validation status
        validation_stats = {}
        for record in results:
            status = record.validation_status or "unknown"
            validation_stats[status] = validation_stats.get(status, 0) + 1
        
        # Group by data type
        data_type_stats = {}
        for record in results:
            dtype = record.data_type
            data_type_stats[dtype] = data_type_stats.get(dtype, 0) + 1
        
        quality_overview = {
            "total_records": total_records,
            "validated_records": validated_records,
            "high_quality_records": high_quality_records,
            "validation_rate": validated_records / total_records if total_records > 0 else 0,
            "high_quality_rate": high_quality_records / total_records if total_records > 0 else 0,
            "validation_status_breakdown": validation_stats,
            "data_type_breakdown": data_type_stats
        }
        
        return {
            "filters": {
                "data_type": data_type,
                "region": region
            },
            "quality_overview": quality_overview,
            "recommendations": [
                "Focus validation efforts on pending records",
                "Improve data collection protocols for low-quality sources",
                "Implement automated quality checks",
                "Regular quality assessments and reviews"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get data quality overview: {e}")
        raise HTTPException(status_code=500, detail=f"Quality overview failed: {str(e)}")
=======
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
>>>>>>> 362b52b683dacbc43ff77fceb651bab6d409b1b0
