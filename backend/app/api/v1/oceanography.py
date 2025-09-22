<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.marine_data import UnifiedMarineData, OceanographicData
from app.schemas.marine_schemas import (
    UnifiedMarineDataCreate, OceanographicDataCreate,
    BaseMarineDataResponse, OceanographicDataResponse,
    MarineDataSearchFilters, MarineDataSearchResponse
)
from app.services.data_ingestion import data_ingestion_service
from app.services.external_apis import obis_client
from app.services.ai_service import ai_service
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/data/create")
async def create_oceanographic_data(
    unified_data: Dict[str, Any] = Body(...),
    oceanographic_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Create new oceanographic data record in unified storage"""
    try:
        # Create base marine data record
        marine_data = UnifiedMarineData(
            data_type="oceanographic",
            data_category=unified_data.get("data_category", "measurement"),
            collection_date=datetime.fromisoformat(unified_data["collection_date"]) if unified_data.get("collection_date") else None,
            latitude=unified_data.get("latitude"),
            longitude=unified_data.get("longitude"),
            depth=unified_data.get("depth"),
            location_name=unified_data.get("location_name"),
            region=unified_data.get("region"),
            source_dataset=unified_data.get("source_dataset"),
            source_institution=unified_data.get("source_institution"),
            primary_data=unified_data.get("primary_data"),
            metadata=unified_data.get("metadata"),
            raw_data=unified_data.get("raw_data"),
            project_id=unified_data.get("project_id"),
            researcher_id=unified_data.get("researcher_id"),
            tags=unified_data.get("tags", []),
            keywords=unified_data.get("keywords", [])
        )
        
        db.add(marine_data)
        db.flush()  # Get the ID
        
        # Create specialized oceanographic data record
        ocean_data = OceanographicData(
            unified_data_id=marine_data.id,
            temperature=oceanographic_data.get("temperature"),
            salinity=oceanographic_data.get("salinity"),
            pressure=oceanographic_data.get("pressure"),
            density=oceanographic_data.get("density"),
            ph=oceanographic_data.get("ph"),
            dissolved_oxygen=oceanographic_data.get("dissolved_oxygen"),
            nutrients=oceanographic_data.get("nutrients"),
            carbon_data=oceanographic_data.get("carbon_data"),
            chlorophyll_a=oceanographic_data.get("chlorophyll_a"),
            primary_productivity=oceanographic_data.get("primary_productivity"),
            current_speed=oceanographic_data.get("current_speed"),
            current_direction=oceanographic_data.get("current_direction"),
            wave_height=oceanographic_data.get("wave_height"),
            wave_period=oceanographic_data.get("wave_period"),
            instrument_type=oceanographic_data.get("instrument_type"),
            sensor_data=oceanographic_data.get("sensor_data"),
            calibration_data=oceanographic_data.get("calibration_data")
        )
        
        db.add(ocean_data)
        db.commit()
        
        return {
            "status": "success",
            "data_id": str(marine_data.id),
            "oceanographic_id": str(ocean_data.id),
            "message": "Oceanographic data created successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create oceanographic data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create data: {str(e)}")

@router.get("/data/search")
async def search_oceanographic_data(
    latitude_min: Optional[float] = Query(None, ge=-90, le=90),
    latitude_max: Optional[float] = Query(None, ge=-90, le=90),
    longitude_min: Optional[float] = Query(None, ge=-180, le=180),
    longitude_max: Optional[float] = Query(None, ge=-180, le=180),
    depth_min: Optional[float] = Query(None),
    depth_max: Optional[float] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    source_dataset: Optional[str] = Query(None),
    parameter_type: Optional[str] = Query(None, description="temperature, salinity, nutrients, etc."),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search oceanographic data with spatial, temporal, and parameter filters"""
    try:
        # Build query with filters
        query = db.query(UnifiedMarineData).filter(
            UnifiedMarineData.data_type == "oceanographic"
        )
        
        # Apply spatial filters
        if latitude_min is not None:
            query = query.filter(UnifiedMarineData.latitude >= latitude_min)
        if latitude_max is not None:
            query = query.filter(UnifiedMarineData.latitude <= latitude_max)
        if longitude_min is not None:
            query = query.filter(UnifiedMarineData.longitude >= longitude_min)
        if longitude_max is not None:
            query = query.filter(UnifiedMarineData.longitude <= longitude_max)
        
        # Apply depth filters
        if depth_min is not None:
            query = query.filter(UnifiedMarineData.depth >= depth_min)
        if depth_max is not None:
            query = query.filter(UnifiedMarineData.depth <= depth_max)
        
        # Apply temporal filters
        if date_from:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(UnifiedMarineData.collection_date >= from_date)
        if date_to:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(UnifiedMarineData.collection_date <= to_date)
        
        # Apply other filters
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        if source_dataset:
            query = query.filter(UnifiedMarineData.source_dataset.ilike(f"%{source_dataset}%"))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        results = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        response_data = []
        for result in results:
            response_data.append({
                "id": str(result.id),
                "data_type": result.data_type,
                "data_category": result.data_category,
                "collection_date": result.collection_date.isoformat() if result.collection_date is not None else None,
                "latitude": result.latitude,
                "longitude": result.longitude,
                "depth": result.depth,
                "location_name": result.location_name,
                "region": result.region,
                "source_dataset": result.source_dataset,
                "primary_data": result.primary_data,
                "data_quality_score": result.data_quality_score,
                "validation_status": result.validation_status
            })
        
        return {
            "total_count": total_count,
            "results": response_data,
            "filters_applied": {
                "spatial": {
                    "latitude_range": [latitude_min, latitude_max],
                    "longitude_range": [longitude_min, longitude_max]
                },
                "depth_range": [depth_min, depth_max],
                "date_range": [date_from, date_to],
                "region": region,
                "source_dataset": source_dataset,
                "parameter_type": parameter_type
            },
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to search oceanographic data: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/data/{data_id}")
async def get_oceanographic_data_details(
    data_id: UUID,
    include_analysis: bool = Query(True, description="Include AI analysis"),
    db: Session = Depends(get_db)
):
    """Get detailed oceanographic data with optional AI analysis"""
    try:
        # Get main data record
        marine_data = db.query(UnifiedMarineData).filter_by(id=data_id).first()
        if not marine_data:
            raise HTTPException(status_code=404, detail="Data record not found")
        
        # Get specialized oceanographic data
        ocean_data = db.query(OceanographicData).filter_by(unified_data_id=data_id).first()
        
        result = {
            "base_data": {
                "id": str(marine_data.id),
                "data_type": marine_data.data_type,
                "data_category": marine_data.data_category,
                "collection_date": marine_data.collection_date.isoformat() if marine_data.collection_date is not None else None,
                "latitude": marine_data.latitude,
                "longitude": marine_data.longitude,
                "depth": marine_data.depth,
                "location_name": marine_data.location_name,
                "region": marine_data.region,
                "source_dataset": marine_data.source_dataset,
                "source_institution": marine_data.source_institution,
                "primary_data": marine_data.primary_data,
                "metadata": marine_data.metadata,
                "data_quality_score": marine_data.data_quality_score,
                "validation_status": marine_data.validation_status,
                "tags": marine_data.tags,
                "created_at": marine_data.created_at.isoformat() if marine_data.created_at is not None else None,
                "updated_at": marine_data.updated_at.isoformat() if marine_data.updated_at is not None else None
            }
        }
        
        if ocean_data:
            result["oceanographic_data"] = {
                "id": str(ocean_data.id),
                "temperature": ocean_data.temperature,
                "salinity": ocean_data.salinity,
                "pressure": ocean_data.pressure,
                "density": ocean_data.density,
                "ph": ocean_data.ph,
                "dissolved_oxygen": ocean_data.dissolved_oxygen,
                "nutrients": ocean_data.nutrients,
                "carbon_data": ocean_data.carbon_data,
                "chlorophyll_a": ocean_data.chlorophyll_a,
                "primary_productivity": ocean_data.primary_productivity,
                "current_speed": ocean_data.current_speed,
                "current_direction": ocean_data.current_direction,
                "wave_height": ocean_data.wave_height,
                "wave_period": ocean_data.wave_period,
                "instrument_type": ocean_data.instrument_type
            }
        
        # Generate AI analysis if requested
        if include_analysis:
            analysis_data = {
                "base_data": result["base_data"],
                "oceanographic_data": result.get("oceanographic_data", {})
            }
            
            ai_analysis = await ai_service.analyze_marine_data(analysis_data)
            result["ai_analysis"] = ai_analysis
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get oceanographic data details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data: {str(e)}")

@router.get("/analytics/water-quality")
async def analyze_water_quality(
    region: Optional[str] = Query(None),
    depth_max: Optional[float] = Query(100, description="Maximum depth for surface water analysis"),
    db: Session = Depends(get_db)
):
    """Analyze water quality indicators from oceanographic data"""
    try:
        # Query for recent water quality data
        query = db.query(UnifiedMarineData, OceanographicData).join(
            OceanographicData, UnifiedMarineData.id == OceanographicData.unified_data_id
        ).filter(
            UnifiedMarineData.data_type == "oceanographic"
        )
        
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        if depth_max:
            query = query.filter(UnifiedMarineData.depth <= depth_max)
        
        results = query.limit(1000).all()
        
        # Process water quality indicators
        quality_data = {
            "temperature_readings": [],
            "salinity_readings": [],
            "ph_readings": [],
            "dissolved_oxygen_readings": [],
            "nutrient_data": []
        }
        
        for marine_data, ocean_data in results:
            if ocean_data.temperature:
                quality_data["temperature_readings"].append(ocean_data.temperature)
            if ocean_data.salinity:
                quality_data["salinity_readings"].append(ocean_data.salinity)
            if ocean_data.ph:
                quality_data["ph_readings"].append(ocean_data.ph)
            if ocean_data.dissolved_oxygen:
                quality_data["dissolved_oxygen_readings"].append(ocean_data.dissolved_oxygen)
            if ocean_data.nutrients:
                quality_data["nutrient_data"].append(ocean_data.nutrients)
        
        # Calculate basic statistics
        quality_summary = {}
        for param, readings in quality_data.items():
            if readings and param != "nutrient_data":
                quality_summary[param] = {
                    "count": len(readings),
                    "mean": sum(readings) / len(readings),
                    "min": min(readings),
                    "max": max(readings)
                }
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "water_quality_assessment",
            "region": region,
            "quality_data": quality_summary,
            "data_points_analyzed": len(results)
        })
        
        return {
            "region": region,
            "data_points_analyzed": len(results),
            "quality_summary": quality_summary,
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze water quality: {e}")
        raise HTTPException(status_code=500, detail=f"Water quality analysis failed: {str(e)}")

@router.post("/data/ingest")
async def ingest_external_oceanographic_data(
    source: str = Query(..., description="Data source: obis, csv, manual"),
    data_params: Dict[str, Any] = Body(..., description="Parameters for data ingestion")
):
    """Ingest oceanographic data from external sources"""
    try:
        if source == "obis":
            # Ingest from OBIS with oceanographic focus
            result = await data_ingestion_service.ingest_obis_data(
                scientific_name=data_params.get("scientific_name"),
                geometry=data_params.get("geometry"),
                limit=data_params.get("limit", 1000)
            )
            
        elif source == "csv":
            # Ingest from CSV file
            result = await data_ingestion_service.ingest_csv_file(
                file_path=data_params.get("file_path", ""),
                data_type="oceanographic",
                mapping_config=data_params.get("mapping_config", {})
            )
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported data source")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
=======
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/temperature/profiles")
async def get_temperature_profiles(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    depth_range: Optional[str] = Query(None, description="Depth range (e.g., '0-100m')")
):
    """Get temperature profiles for specified location and time range"""
    try:
        # Simulate oceanographic data (in real implementation, this would query actual databases)
        temperature_data = {
            "location": {"latitude": latitude, "longitude": longitude},
            "date_range": {"start": start_date, "end": end_date},
            "depth_range": depth_range,
            "profiles": [
                {"depth": "0m", "temperature": 28.5, "timestamp": "2024-01-01T00:00:00Z"},
                {"depth": "10m", "temperature": 27.8, "timestamp": "2024-01-01T00:00:00Z"},
                {"depth": "50m", "temperature": 25.2, "timestamp": "2024-01-01T00:00:00Z"},
                {"depth": "100m", "temperature": 22.1, "timestamp": "2024-01-01T00:00:00Z"}
            ],
            "data_source": "Simulated oceanographic station"
        }
        
        # Generate AI analysis of temperature patterns
        analysis = await llm_service.interpret_oceanographic_data(temperature_data)
        
        return {
            "query_parameters": {
                "location": {"latitude": latitude, "longitude": longitude},
                "date_range": {"start": start_date, "end": end_date},
                "depth_range": depth_range
            },
            "temperature_data": temperature_data,
            "ai_interpretation": analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to get temperature profiles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve temperature data: {str(e)}")

@router.get("/salinity/measurements")
async def get_salinity_data(
    region: str = Query(..., description="Geographic region or station ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get salinity measurements for specified region and time range"""
    try:
        # Simulate salinity data
        salinity_data = {
            "region": region,
            "date_range": {"start": start_date, "end": end_date},
            "measurements": [
                {"depth": "surface", "salinity": 35.2, "location": "Station A", "date": "2024-01-01"},
                {"depth": "50m", "salinity": 35.5, "location": "Station A", "date": "2024-01-01"},
                {"depth": "100m", "salinity": 35.8, "location": "Station A", "date": "2024-01-01"}
            ],
            "units": "PSU (Practical Salinity Units)",
            "quality_flags": "All measurements passed QC checks"
        }
        
        # Generate AI interpretation
        interpretation = await llm_service.interpret_oceanographic_data(salinity_data)
        
        return {
            "salinity_data": salinity_data,
            "ai_interpretation": interpretation
        }
        
    except Exception as e:
        logger.error(f"Failed to get salinity data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve salinity data: {str(e)}")

@router.get("/chemistry/nutrients")
async def get_nutrient_data(
    location: str = Query(..., description="Sampling location"),
    nutrients: List[str] = Query(["nitrate", "phosphate", "silicate"], description="Nutrient types to retrieve")
):
    """Get chemical oceanography data - nutrient concentrations"""
    try:
        # Simulate nutrient data
        nutrient_data = {
            "location": location,
            "nutrients_requested": nutrients,
            "measurements": {
                "nitrate": {"value": 12.5, "units": "μmol/L", "depth": "surface"},
                "phosphate": {"value": 1.8, "units": "μmol/L", "depth": "surface"},
                "silicate": {"value": 25.3, "units": "μmol/L", "depth": "surface"}
            },
            "sampling_date": "2024-01-01",
            "quality_control": "Passed standard QC procedures"
        }
        
        # Generate AI analysis of nutrient levels
        analysis = await llm_service.interpret_oceanographic_data(nutrient_data)
        
        return {
            "nutrient_data": nutrient_data,
            "ai_analysis": analysis,
            "ecosystem_implications": "Nutrient levels indicate healthy marine productivity"
        }
        
    except Exception as e:
        logger.error(f"Failed to get nutrient data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve nutrient data: {str(e)}")

@router.get("/currents/analysis")
async def get_current_analysis(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    time_period: str = Query("monthly", description="Analysis period: daily, weekly, monthly")
):
    """Get ocean current analysis for specified location"""
    try:
        # Simulate current data
        current_data = {
            "location": {"latitude": latitude, "longitude": longitude},
            "time_period": time_period,
            "current_vectors": [
                {"direction": 45, "speed": 0.25, "depth": "surface", "units": "m/s"},
                {"direction": 42, "speed": 0.20, "depth": "10m", "units": "m/s"},
                {"direction": 38, "speed": 0.15, "depth": "50m", "units": "m/s"}
            ],
            "dominant_direction": "Northeast",
            "seasonal_variation": "Moderate variation observed"
        }
        
        # Generate AI interpretation of current patterns
        interpretation = await llm_service.interpret_oceanographic_data(current_data)
        
        return {
            "current_analysis": current_data,
            "ai_interpretation": interpretation,
            "ecological_significance": "Current patterns influence larval dispersal and nutrient transport"
        }
        
    except Exception as e:
        logger.error(f"Failed to get current analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve current data: {str(e)}")

@router.post("/data/quality-check")
async def perform_quality_check(
    oceanographic_data: Dict[str, Any]
):
    """Perform quality control checks on oceanographic data"""
    try:
        # Use AI to assess data quality
        quality_assessment = await llm_service.analyze_marine_data(
            oceanographic_data,
            "Perform quality control analysis on this oceanographic data. Check for anomalies, completeness, and accuracy."
        )
        
        # Simulate quality metrics
        quality_metrics = {
            "completeness_score": 0.95,
            "accuracy_score": 0.92,
            "temporal_consistency": 0.88,
            "spatial_consistency": 0.91,
            "flagged_values": 2,
            "total_values": 100
        }
        
        return {
            "input_data_summary": f"Analyzed {len(str(oceanographic_data))} characters of data",
            "quality_metrics": quality_metrics,
            "ai_assessment": quality_assessment,
            "recommendations": [
                "Review flagged temperature values at depth >200m",
                "Verify salinity measurements from Station B",
                "Consider additional validation for outlier detection"
            ]
        }
        
    except Exception as e:
        logger.error(f"Quality check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quality check failed: {str(e)}")

@router.get("/climate/trends")
async def get_climate_trends(
    region: str = Query(..., description="Geographic region"),
    parameter: str = Query("temperature", description="Climate parameter: temperature, salinity, pH"),
    years: int = Query(10, description="Number of years for trend analysis")
):
    """Get climate change trends in oceanographic parameters"""
    try:
        # Simulate climate trend data
        trend_data = {
            "region": region,
            "parameter": parameter,
            "analysis_period": f"{years} years",
            "trend_statistics": {
                "slope": 0.02,
                "r_squared": 0.78,
                "p_value": 0.001,
                "confidence_interval": [0.015, 0.025]
            },
            "annual_means": [
                {"year": 2014, "value": 26.5},
                {"year": 2015, "value": 26.7},
                {"year": 2016, "value": 26.8},
                {"year": 2017, "value": 26.9},
                {"year": 2018, "value": 27.1},
                {"year": 2019, "value": 27.2},
                {"year": 2020, "value": 27.3},
                {"year": 2021, "value": 27.4},
                {"year": 2022, "value": 27.6},
                {"year": 2023, "value": 27.7}
            ]
        }
        
        # Generate AI interpretation of trends
        interpretation = await llm_service.interpret_oceanographic_data(trend_data)
        
        return {
            "trend_analysis": trend_data,
            "ai_interpretation": interpretation,
            "climate_implications": f"Observed warming trend of 0.02°C per year in {region}"
        }
        
    except Exception as e:
        logger.error(f"Failed to get climate trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve climate trends: {str(e)}")
>>>>>>> 362b52b683dacbc43ff77fceb651bab6d409b1b0
