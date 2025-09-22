from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.marine_data import UnifiedMarineData, TaxonomicData
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/data/create")
async def create_taxonomic_data(
    unified_data: Dict[str, Any] = Body(...),
    taxonomic_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Create new taxonomic data record with morphological information"""
    try:
        marine_data = UnifiedMarineData(
            data_type="taxonomic",
            data_category=unified_data.get("data_category", "species_identification"),
            collection_date=datetime.fromisoformat(unified_data["collection_date"]) if unified_data.get("collection_date") else None,
            latitude=unified_data.get("latitude"),
            longitude=unified_data.get("longitude"),
            scientific_name=unified_data.get("scientific_name"),
            kingdom=unified_data.get("kingdom"),
            phylum=unified_data.get("phylum"),
            class_name=unified_data.get("class_name"),
            order=unified_data.get("order"),
            family=unified_data.get("family"),
            genus=unified_data.get("genus"),
            species=unified_data.get("species")
        )
        
        db.add(marine_data)
        db.flush()
        
        tax_data = TaxonomicData(
            unified_data_id=marine_data.id,
            taxonomic_authority=taxonomic_data.get("taxonomic_authority"),
            taxonomic_status=taxonomic_data.get("taxonomic_status"),
            morphology_description=taxonomic_data.get("morphology_description"),
            otolith_data=taxonomic_data.get("otolith_data"),
            specimen_id=taxonomic_data.get("specimen_id"),
            identification_confidence=taxonomic_data.get("identification_confidence")
        )
        
        db.add(tax_data)
        db.commit()
        
        return {
            "status": "success",
            "data_id": str(marine_data.id),
            "taxonomic_id": str(tax_data.id)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create taxonomic data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create data: {str(e)}")

@router.get("/species/search")
async def search_species_taxonomy(
    scientific_name: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    has_otolith_data: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search taxonomic data with filters"""
    try:
        query = db.query(UnifiedMarineData, TaxonomicData).join(
            TaxonomicData, UnifiedMarineData.id == TaxonomicData.unified_data_id
        ).filter(UnifiedMarineData.data_type == "taxonomic")
        
        if scientific_name:
            query = query.filter(UnifiedMarineData.scientific_name.ilike(f"%{scientific_name}%"))
        if family:
            query = query.filter(UnifiedMarineData.family.ilike(f"%{family}%"))
        if has_otolith_data is not None:
            if has_otolith_data:
                query = query.filter(TaxonomicData.otolith_data.is_not(None))
        
        total_count = query.count()
        results = query.offset(offset).limit(limit).all()
        
        response_data = []
        for marine_data, tax_data in results:
            response_data.append({
                "id": str(marine_data.id),
                "scientific_name": marine_data.scientific_name,
                "family": marine_data.family,
                "specimen_id": tax_data.specimen_id,
                "has_otolith_data": bool(tax_data.otolith_data),
                "identification_confidence": tax_data.identification_confidence
            })
        
        return {
            "total_count": total_count,
            "results": response_data,
            "pagination": {"limit": limit, "offset": offset}
        }
        
    except Exception as e:
        logger.error(f"Failed to search taxonomic data: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/otolith/analysis")
async def analyze_otolith_morphology(
    species_name: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Analyze otolith morphology patterns"""
    try:
        query = db.query(UnifiedMarineData, TaxonomicData).join(
            TaxonomicData, UnifiedMarineData.id == TaxonomicData.unified_data_id
        ).filter(
            UnifiedMarineData.data_type == "taxonomic",
            TaxonomicData.otolith_data.is_not(None)
        )
        
        if species_name:
            query = query.filter(UnifiedMarineData.scientific_name.ilike(f"%{species_name}%"))
        if family:
            query = query.filter(UnifiedMarineData.family.ilike(f"%{family}%"))
        
        results = query.all()
        
        otolith_records = []
        for marine_data, tax_data in results:
            otolith_records.append({
                "species": marine_data.scientific_name,
                "family": marine_data.family,
                "otolith_data": tax_data.otolith_data,
                "specimen_id": tax_data.specimen_id
            })
        
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "otolith_analysis",
            "total_specimens": len(otolith_records),
            "species_name": species_name,
            "family": family
        })
        
        return {
            "total_specimens": len(otolith_records),
            "otolith_records": otolith_records[:100],
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze otolith morphology: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")