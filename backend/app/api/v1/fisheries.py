from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.marine_data import UnifiedMarineData, FisheriesData
from app.schemas.marine_schemas import (
    UnifiedMarineDataCreate, FisheriesDataCreate,
    BaseMarineDataResponse, FisheriesDataResponse,
    MarineDataSearchFilters, BiodiversityMetrics
)
from app.services.data_ingestion import data_ingestion_service
from app.services.external_apis import obis_client, gbif_client
from app.services.ai_service import ai_service
import logging
import json
import math

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/data/create")
async def create_fisheries_data(
    unified_data: Dict[str, Any] = Body(...),
    fisheries_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Create new fisheries data record in unified storage"""
    try:
        # Create base marine data record
        marine_data = UnifiedMarineData(
            data_type="fisheries",
            data_category=unified_data.get("data_category", "fish_survey"),
            collection_date=datetime.fromisoformat(unified_data["collection_date"]) if unified_data.get("collection_date") else None,
            latitude=unified_data.get("latitude"),
            longitude=unified_data.get("longitude"),
            depth=unified_data.get("depth"),
            location_name=unified_data.get("location_name"),
            region=unified_data.get("region"),
            source_dataset=unified_data.get("source_dataset"),
            source_institution=unified_data.get("source_institution"),
            scientific_name=unified_data.get("scientific_name"),
            kingdom=unified_data.get("kingdom", "Animalia"),
            phylum=unified_data.get("phylum", "Chordata"),
            class_name=unified_data.get("class_name", "Actinopterygii"),
            order=unified_data.get("order"),
            family=unified_data.get("family"),
            genus=unified_data.get("genus"),
            species=unified_data.get("species"),
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
        
        # Create specialized fisheries data record
        fish_data = FisheriesData(
            unified_data_id=marine_data.id,
            abundance_count=fisheries_data.get("abundance_count"),
            abundance_density=fisheries_data.get("abundance_density"),
            biomass=fisheries_data.get("biomass"),
            cpue=fisheries_data.get("cpue"),
            length=fisheries_data.get("length"),
            weight=fisheries_data.get("weight"),
            age=fisheries_data.get("age"),
            maturity_stage=fisheries_data.get("maturity_stage"),
            sex=fisheries_data.get("sex"),
            morphometric_data=fisheries_data.get("morphometric_data"),
            meristic_data=fisheries_data.get("meristic_data"),
            ecological_traits=fisheries_data.get("ecological_traits"),
            fishing_method=fisheries_data.get("fishing_method"),
            gear_type=fisheries_data.get("gear_type"),
            effort_data=fisheries_data.get("effort_data"),
            water_conditions=fisheries_data.get("water_conditions"),
            habitat_type=fisheries_data.get("habitat_type")
        )
        
        db.add(fish_data)
        db.commit()
        
        return {
            "status": "success",
            "data_id": str(marine_data.id),
            "fisheries_id": str(fish_data.id),
            "message": "Fisheries data created successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create fisheries data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create data: {str(e)}")

@router.get("/data/search")
async def search_fisheries_data(
    scientific_name: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    fishing_method: Optional[str] = Query(None),
    gear_type: Optional[str] = Query(None),
    habitat_type: Optional[str] = Query(None),
    latitude_min: Optional[float] = Query(None, ge=-90, le=90),
    latitude_max: Optional[float] = Query(None, ge=-90, le=90),
    longitude_min: Optional[float] = Query(None, ge=-180, le=180),
    longitude_max: Optional[float] = Query(None, ge=-180, le=180),
    depth_min: Optional[float] = Query(None),
    depth_max: Optional[float] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search fisheries data with comprehensive filters"""
    try:
        # Build query with filters
        query = db.query(UnifiedMarineData).filter(
            UnifiedMarineData.data_type == "fisheries"
        )
        
        # Apply taxonomic filters
        if scientific_name:
            query = query.filter(UnifiedMarineData.scientific_name.ilike(f"%{scientific_name}%"))
        if family:
            query = query.filter(UnifiedMarineData.family.ilike(f"%{family}%"))
        
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
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        results = query.offset(offset).limit(limit).all()
        
        # Get associated fisheries data
        marine_ids = [result.id for result in results]
        fisheries_query = db.query(FisheriesData).filter(
            FisheriesData.unified_data_id.in_(marine_ids)
        )
        
        # Apply fisheries-specific filters
        if fishing_method:
            fisheries_query = fisheries_query.filter(
                FisheriesData.fishing_method.ilike(f"%{fishing_method}%")
            )
        if gear_type:
            fisheries_query = fisheries_query.filter(
                FisheriesData.gear_type.ilike(f"%{gear_type}%")
            )
        if habitat_type:
            fisheries_query = fisheries_query.filter(
                FisheriesData.habitat_type.ilike(f"%{habitat_type}%")
            )
        
        fisheries_data = fisheries_query.all()
        fisheries_dict = {fd.unified_data_id: fd for fd in fisheries_data}
        
        # Convert to response format
        response_data = []
        for result in results:
            fish_data = fisheries_dict.get(result.id)
            response_item = {
                "id": str(result.id),
                "data_type": result.data_type,
                "data_category": result.data_category,
                "collection_date": result.collection_date.isoformat() if result.collection_date is not None else None,
                "latitude": result.latitude,
                "longitude": result.longitude,
                "depth": result.depth,
                "location_name": result.location_name,
                "region": result.region,
                "scientific_name": result.scientific_name,
                "family": result.family,
                "genus": result.genus,
                "species": result.species,
                "source_dataset": result.source_dataset,
                "data_quality_score": result.data_quality_score,
                "validation_status": result.validation_status
            }
            
            if fish_data:
                response_item["fisheries_data"] = {
                    "abundance_count": fish_data.abundance_count,
                    "biomass": fish_data.biomass,
                    "cpue": fish_data.cpue,
                    "length": fish_data.length,
                    "weight": fish_data.weight,
                    "age": fish_data.age,
                    "maturity_stage": fish_data.maturity_stage,
                    "sex": fish_data.sex,
                    "fishing_method": fish_data.fishing_method,
                    "gear_type": fish_data.gear_type,
                    "habitat_type": fish_data.habitat_type
                }
            
            response_data.append(response_item)
        
        return {
            "total_count": total_count,
            "results": response_data,
            "filters_applied": {
                "taxonomic": {
                    "scientific_name": scientific_name,
                    "family": family
                },
                "spatial": {
                    "latitude_range": [latitude_min, latitude_max],
                    "longitude_range": [longitude_min, longitude_max],
                    "depth_range": [depth_min, depth_max]
                },
                "temporal": {
                    "date_range": [date_from, date_to]
                },
                "fisheries_specific": {
                    "fishing_method": fishing_method,
                    "gear_type": gear_type,
                    "habitat_type": habitat_type
                },
                "region": region
            },
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to search fisheries data: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/species/{species_name}/abundance")
async def get_species_abundance(
    species_name: str,
    region: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get abundance data for a specific species"""
    try:
        # Build query for species abundance
        query = db.query(UnifiedMarineData, FisheriesData).join(
            FisheriesData, UnifiedMarineData.id == FisheriesData.unified_data_id
        ).filter(
            UnifiedMarineData.data_type == "fisheries",
            UnifiedMarineData.scientific_name.ilike(f"%{species_name}%")
        )
        
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        
        if year:
            query = query.filter(
                func.extract('year', UnifiedMarineData.collection_date) == year
            )
        
        results = query.all()
        
        # Process abundance data
        abundance_records = []
        total_abundance = 0
        total_biomass = 0.0
        cpue_values = []
        
        for marine_data, fish_data in results:
            record = {
                "location": {
                    "latitude": marine_data.latitude,
                    "longitude": marine_data.longitude,
                    "depth": marine_data.depth,
                    "region": marine_data.region
                },
                "date": marine_data.collection_date.isoformat() if marine_data.collection_date else None,
                "abundance_count": fish_data.abundance_count,
                "abundance_density": fish_data.abundance_density,
                "biomass": fish_data.biomass,
                "cpue": fish_data.cpue,
                "fishing_method": fish_data.fishing_method,
                "gear_type": fish_data.gear_type
            }
            abundance_records.append(record)
            
            # Accumulate statistics
            if fish_data.abundance_count:
                total_abundance += fish_data.abundance_count
            if fish_data.biomass:
                total_biomass += fish_data.biomass
            if fish_data.cpue:
                cpue_values.append(fish_data.cpue)
        
        # Calculate summary statistics
        avg_cpue = sum(cpue_values) / len(cpue_values) if cpue_values else 0
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "species_abundance",
            "species_name": species_name,
            "region": region,
            "year": year,
            "total_records": len(abundance_records),
            "abundance_summary": {
                "total_abundance": total_abundance,
                "total_biomass": total_biomass,
                "average_cpue": avg_cpue
            }
        })
        
        return {
            "species_name": species_name,
            "region": region,
            "year": year,
            "total_records": len(abundance_records),
            "abundance_summary": {
                "total_abundance": total_abundance,
                "total_biomass": total_biomass,
                "average_cpue": avg_cpue,
                "spatial_distribution": len(set((r["location"]["latitude"], r["location"]["longitude"]) for r in abundance_records if r["location"]["latitude"]))
            },
            "abundance_records": abundance_records,
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to get species abundance: {e}")
        raise HTTPException(status_code=500, detail=f"Abundance query failed: {str(e)}")

@router.get("/analytics/biodiversity")
async def analyze_biodiversity(
    region: Optional[str] = Query(None),
    latitude_min: Optional[float] = Query(None),
    latitude_max: Optional[float] = Query(None),
    longitude_min: Optional[float] = Query(None),
    longitude_max: Optional[float] = Query(None),
    depth_min: Optional[float] = Query(None),
    depth_max: Optional[float] = Query(None),
    time_period_months: int = Query(12, description="Time period in months for analysis"),
    db: Session = Depends(get_db)
):
    """Analyze biodiversity metrics from fisheries data"""
    try:
        # Build query with spatial and temporal filters
        query = db.query(UnifiedMarineData).filter(
            UnifiedMarineData.data_type == "fisheries",
            UnifiedMarineData.scientific_name.is_not(None)
        )
        
        # Apply spatial filters
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        if latitude_min is not None:
            query = query.filter(UnifiedMarineData.latitude >= latitude_min)
        if latitude_max is not None:
            query = query.filter(UnifiedMarineData.latitude <= latitude_max)
        if longitude_min is not None:
            query = query.filter(UnifiedMarineData.longitude >= longitude_min)
        if longitude_max is not None:
            query = query.filter(UnifiedMarineData.longitude <= longitude_max)
        if depth_min is not None:
            query = query.filter(UnifiedMarineData.depth >= depth_min)
        if depth_max is not None:
            query = query.filter(UnifiedMarineData.depth <= depth_max)
        
        # Apply temporal filter
        from_date = datetime.now().replace(month=max(1, datetime.now().month - time_period_months))
        query = query.filter(UnifiedMarineData.collection_date >= from_date)
        
        results = query.all()
        
        # Calculate biodiversity metrics
        species_counts = {}
        family_counts = {}
        total_individuals = 0
        
        for record in results:
            species = record.scientific_name
            family = record.family
            
            # Count species occurrences
            species_counts[species] = species_counts.get(species, 0) + 1
            
            # Count family occurrences
            if family is not None:
                family_counts[family] = family_counts.get(family, 0) + 1
            
            total_individuals += 1
        
        # Calculate diversity indices
        species_richness = len(species_counts)
        
        # Shannon diversity index
        shannon_diversity = 0.0
        if total_individuals > 0:
            for count in species_counts.values():
                if count > 0:
                    p = count / total_individuals
                    shannon_diversity -= p * math.log(p)
        
        # Simpson diversity index
        simpson_diversity = 0.0
        if total_individuals > 1:
            for count in species_counts.values():
                if count > 1:
                    simpson_diversity += (count * (count - 1)) / (total_individuals * (total_individuals - 1))
            simpson_diversity = 1 - simpson_diversity
        
        # Evenness (Pielou's evenness)
        evenness = 0.0
        if species_richness > 1:
            max_diversity = math.log(species_richness)
            evenness = shannon_diversity / max_diversity
        
        # Most common species
        most_common_species = sorted(species_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        most_common_families = sorted(family_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        biodiversity_metrics = {
            "species_richness": species_richness,
            "shannon_diversity": round(shannon_diversity, 4),
            "simpson_diversity": round(simpson_diversity, 4),
            "evenness": round(evenness, 4),
            "total_abundance": total_individuals,
            "family_richness": len(family_counts),
            "most_common_species": most_common_species,
            "most_common_families": most_common_families
        }
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "biodiversity_assessment",
            "region": region,
            "spatial_bounds": {
                "latitude_range": [latitude_min, latitude_max],
                "longitude_range": [longitude_min, longitude_max],
                "depth_range": [depth_min, depth_max]
            },
            "time_period_months": time_period_months,
            "biodiversity_metrics": biodiversity_metrics,
            "sample_size": len(results)
        })
        
        return {
            "analysis_parameters": {
                "region": region,
                "spatial_bounds": {
                    "latitude_range": [latitude_min, latitude_max],
                    "longitude_range": [longitude_min, longitude_max],
                    "depth_range": [depth_min, depth_max]
                },
                "time_period_months": time_period_months,
                "sample_size": len(results)
            },
            "biodiversity_metrics": biodiversity_metrics,
            "ai_analysis": ai_analysis,
            "conservation_status": {
                "diversity_rating": "High" if shannon_diversity > 2.5 else "Medium" if shannon_diversity > 1.5 else "Low",
                "evenness_rating": "High" if evenness > 0.7 else "Medium" if evenness > 0.5 else "Low",
                "species_dominance": "Low" if simpson_diversity > 0.8 else "Medium" if simpson_diversity > 0.6 else "High"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze biodiversity: {e}")
        raise HTTPException(status_code=500, detail=f"Biodiversity analysis failed: {str(e)}")

@router.get("/analytics/fish-size-distribution")
async def analyze_fish_size_distribution(
    species_name: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    gear_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Analyze fish size distribution and life history traits"""
    try:
        # Build query
        query = db.query(UnifiedMarineData, FisheriesData).join(
            FisheriesData, UnifiedMarineData.id == FisheriesData.unified_data_id
        ).filter(
            UnifiedMarineData.data_type == "fisheries"
        )
        
        # Apply filters
        if species_name:
            query = query.filter(UnifiedMarineData.scientific_name.ilike(f"%{species_name}%"))
        if family:
            query = query.filter(UnifiedMarineData.family.ilike(f"%{family}%"))
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        if gear_type:
            query = query.filter(FisheriesData.gear_type.ilike(f"%{gear_type}%"))
        
        results = query.all()
        
        # Process size data
        length_data = []
        weight_data = []
        age_data = []
        maturity_stages = {}
        sex_distribution = {}
        
        for marine_data, fish_data in results:
            if fish_data.length:
                length_data.append({
                    "species": marine_data.scientific_name,
                    "length": fish_data.length,
                    "weight": fish_data.weight,
                    "age": fish_data.age,
                    "sex": fish_data.sex,
                    "maturity_stage": fish_data.maturity_stage,
                    "location": marine_data.region
                })
            
            if fish_data.weight:
                weight_data.append(fish_data.weight)
            if fish_data.age:
                age_data.append(fish_data.age)
            if fish_data.maturity_stage:
                maturity_stages[fish_data.maturity_stage] = maturity_stages.get(fish_data.maturity_stage, 0) + 1
            if fish_data.sex:
                sex_distribution[fish_data.sex] = sex_distribution.get(fish_data.sex, 0) + 1
        
        # Calculate statistics
        size_statistics = {}
        
        if length_data:
            lengths = [d["length"] for d in length_data if d["length"]]
            if lengths:
                size_statistics["length"] = {
                    "count": len(lengths),
                    "mean": sum(lengths) / len(lengths),
                    "min": min(lengths),
                    "max": max(lengths),
                    "median": sorted(lengths)[len(lengths)//2]
                }
        
        if weight_data:
            size_statistics["weight"] = {
                "count": len(weight_data),
                "mean": sum(weight_data) / len(weight_data),
                "min": min(weight_data),
                "max": max(weight_data),
                "median": sorted(weight_data)[len(weight_data)//2]
            }
        
        if age_data:
            size_statistics["age"] = {
                "count": len(age_data),
                "mean": sum(age_data) / len(age_data),
                "min": min(age_data),
                "max": max(age_data),
                "median": sorted(age_data)[len(age_data)//2]
            }
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "fish_size_distribution",
            "species_name": species_name,
            "family": family,
            "region": region,
            "gear_type": gear_type,
            "sample_size": len(length_data),
            "size_statistics": size_statistics,
            "maturity_distribution": maturity_stages,
            "sex_distribution": sex_distribution
        })
        
        return {
            "analysis_parameters": {
                "species_name": species_name,
                "family": family,
                "region": region,
                "gear_type": gear_type,
                "sample_size": len(results)
            },
            "size_statistics": size_statistics,
            "life_history_data": {
                "maturity_stages": maturity_stages,
                "sex_distribution": sex_distribution
            },
            "length_data": length_data[:1000],  # Limit for response size
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze fish size distribution: {e}")
        raise HTTPException(status_code=500, detail=f"Size analysis failed: {str(e)}")

@router.post("/data/ingest")
async def ingest_fisheries_data(
    source: str = Query(..., description="Data source: obis, gbif, csv, manual"),
    data_params: Dict[str, Any] = Body(..., description="Parameters for data ingestion")
):
    """Ingest fisheries data from external sources"""
    try:
        if source == "obis":
            # Ingest from OBIS with fisheries focus
            result = await data_ingestion_service.ingest_obis_data(
                scientific_name=data_params.get("scientific_name"),
                geometry=data_params.get("geometry"),
                limit=data_params.get("limit", 1000)
            )
            
        elif source == "gbif":
            # Ingest from GBIF
            gbif_data = await gbif_client.search_occurrences(
                scientific_name=data_params.get("scientific_name"),
                country=data_params.get("country"),
                year=data_params.get("year"),
                limit=data_params.get("limit", 1000)
            )
            
            # Process GBIF data (simplified)
            result = {
                "status": "success",
                "records_processed": len(gbif_data.get("results", [])),
                "source": "GBIF"
            }
            
        elif source == "csv":
            # Ingest from CSV file
            result = await data_ingestion_service.ingest_csv_file(
                file_path=data_params.get("file_path") or "",
                data_type="fisheries",
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