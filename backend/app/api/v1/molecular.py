from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.marine_data import UnifiedMarineData, MolecularData
from app.services.ai_service import ai_service
from app.services.data_ingestion import data_ingestion_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/data/create")
async def create_molecular_data(
    unified_data: Dict[str, Any] = Body(...),
    molecular_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Create new molecular biology/eDNA data record"""
    try:
        marine_data = UnifiedMarineData(
            data_type="molecular",
            data_category=unified_data.get("data_category", "edna_sample"),
            collection_date=datetime.fromisoformat(unified_data["collection_date"]) if unified_data.get("collection_date") else None,
            latitude=unified_data.get("latitude"),
            longitude=unified_data.get("longitude"),
            depth=unified_data.get("depth"),
            scientific_name=unified_data.get("scientific_name"),
            kingdom=unified_data.get("kingdom"),
            phylum=unified_data.get("phylum"),
            class_name=unified_data.get("class_name"),
            family=unified_data.get("family"),
            genus=unified_data.get("genus"),
            species=unified_data.get("species"),
            region=unified_data.get("region"),
            source_dataset=unified_data.get("source_dataset")
        )
        
        db.add(marine_data)
        db.flush()
        
        mol_data = MolecularData(
            unified_data_id=marine_data.id,
            sample_type=molecular_data.get("sample_type"),
            dna_extraction_method=molecular_data.get("dna_extraction_method"),
            sequencing_platform=molecular_data.get("sequencing_platform"),
            sequence_data=molecular_data.get("sequence_data"),
            marker_gene=molecular_data.get("marker_gene"),
            marker_region=molecular_data.get("marker_region"),
            taxonomic_assignment=molecular_data.get("taxonomic_assignment"),
            dna_concentration=molecular_data.get("dna_concentration"),
            read_count=molecular_data.get("read_count"),
            detection_probability=molecular_data.get("detection_probability"),
            species_detection=molecular_data.get("species_detection"),
            biodiversity_indices=molecular_data.get("biodiversity_indices"),
            lab_protocol=molecular_data.get("lab_protocol")
        )
        
        db.add(mol_data)
        db.commit()
        
        return {
            "status": "success",
            "data_id": str(marine_data.id),
            "molecular_id": str(mol_data.id)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create molecular data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create data: {str(e)}")

@router.get("/edna/search")
async def search_edna_samples(
    region: Optional[str] = Query(None),
    sample_type: Optional[str] = Query(None),
    marker_gene: Optional[str] = Query(None),
    latitude_min: Optional[float] = Query(None),
    latitude_max: Optional[float] = Query(None),
    longitude_min: Optional[float] = Query(None),
    longitude_max: Optional[float] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search eDNA samples with comprehensive filters"""
    try:
        query = db.query(UnifiedMarineData, MolecularData).join(
            MolecularData, UnifiedMarineData.id == MolecularData.unified_data_id
        ).filter(UnifiedMarineData.data_type == "molecular")
        
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        if sample_type:
            query = query.filter(MolecularData.sample_type.ilike(f"%{sample_type}%"))
        if marker_gene:
            query = query.filter(MolecularData.marker_gene.ilike(f"%{marker_gene}%"))
        
        # Spatial filters
        if latitude_min is not None:
            query = query.filter(UnifiedMarineData.latitude >= latitude_min)
        if latitude_max is not None:
            query = query.filter(UnifiedMarineData.latitude <= latitude_max)
        if longitude_min is not None:
            query = query.filter(UnifiedMarineData.longitude >= longitude_min)
        if longitude_max is not None:
            query = query.filter(UnifiedMarineData.longitude <= longitude_max)
        
        # Temporal filters
        if date_from:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(UnifiedMarineData.collection_date >= from_date)
        if date_to:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(UnifiedMarineData.collection_date <= to_date)
        
        total_count = query.count()
        results = query.offset(offset).limit(limit).all()
        
        response_data = []
        for marine_data, mol_data in results:
            response_data.append({
                "id": str(marine_data.id),
                "location": {
                    "latitude": marine_data.latitude,
                    "longitude": marine_data.longitude,
                    "region": marine_data.region,
                    "depth": marine_data.depth
                },
                "collection_date": marine_data.collection_date.isoformat() if marine_data.collection_date else None,
                "sample_info": {
                    "sample_type": mol_data.sample_type,
                    "dna_concentration": mol_data.dna_concentration,
                    "marker_gene": mol_data.marker_gene,
                    "sequencing_platform": mol_data.sequencing_platform,
                    "read_count": mol_data.read_count
                },
                "species_detection": mol_data.species_detection,
                "biodiversity_indices": mol_data.biodiversity_indices,
                "detection_probability": mol_data.detection_probability
            })
        
        return {
            "total_count": total_count,
            "results": response_data,
            "filters_applied": {
                "region": region,
                "sample_type": sample_type,
                "marker_gene": marker_gene,
                "spatial_bounds": {
                    "latitude_range": [latitude_min, latitude_max],
                    "longitude_range": [longitude_min, longitude_max]
                },
                "date_range": [date_from, date_to]
            },
            "pagination": {"limit": limit, "offset": offset, "has_more": offset + limit < total_count}
        }
        
    except Exception as e:
        logger.error(f"Failed to search eDNA samples: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/species/{species_name}/detection")
async def get_species_edna_detection(
    species_name: str,
    region: Optional[str] = Query(None),
    marker_gene: Optional[str] = Query(None),
    min_detection_probability: float = Query(0.5, ge=0, le=1),
    db: Session = Depends(get_db)
):
    """Get eDNA detection data for a specific species"""
    try:
        query = db.query(UnifiedMarineData, MolecularData).join(
            MolecularData, UnifiedMarineData.id == MolecularData.unified_data_id
        ).filter(
            UnifiedMarineData.data_type == "molecular",
            UnifiedMarineData.scientific_name.ilike(f"%{species_name}%"),
            MolecularData.detection_probability >= min_detection_probability
        )
        
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        if marker_gene:
            query = query.filter(MolecularData.marker_gene.ilike(f"%{marker_gene}%"))
        
        results = query.all()
        
        detection_records = []
        detection_summary = {
            "total_detections": 0,
            "high_confidence_detections": 0,
            "regions": set(),
            "marker_genes": set(),
            "avg_detection_probability": 0.0
        }
        
        for marine_data, mol_data in results:
            record = {
                "location": {
                    "latitude": marine_data.latitude,
                    "longitude": marine_data.longitude,
                    "region": marine_data.region,
                    "depth": marine_data.depth
                },
                "collection_date": marine_data.collection_date.isoformat() if marine_data.collection_date else None,
                "detection_data": {
                    "detection_probability": mol_data.detection_probability,
                    "marker_gene": mol_data.marker_gene,
                    "read_count": mol_data.read_count,
                    "dna_concentration": mol_data.dna_concentration
                },
                "taxonomic_assignment": mol_data.taxonomic_assignment,
                "sample_type": mol_data.sample_type
            }
            detection_records.append(record)
            
            detection_summary["total_detections"] += 1
            if mol_data.detection_probability and mol_data.detection_probability > 0.8:
                detection_summary["high_confidence_detections"] += 1
            if marine_data.region:
                detection_summary["regions"].add(marine_data.region)
            if mol_data.marker_gene:
                detection_summary["marker_genes"].add(mol_data.marker_gene)
        
        # Calculate averages
        if detection_records:
            probabilities = [r["detection_data"]["detection_probability"] for r in detection_records if r["detection_data"]["detection_probability"]]
            detection_summary["avg_detection_probability"] = sum(probabilities) / len(probabilities) if probabilities else 0
        
        detection_summary["regions"] = list(detection_summary["regions"])
        detection_summary["marker_genes"] = list(detection_summary["marker_genes"])
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "species_edna_detection",
            "species_name": species_name,
            "detection_summary": detection_summary,
            "sample_size": len(detection_records),
            "filters": {
                "region": region,
                "marker_gene": marker_gene,
                "min_detection_probability": min_detection_probability
            }
        })
        
        return {
            "species_name": species_name,
            "detection_summary": detection_summary,
            "detection_records": detection_records,
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to get species eDNA detection: {e}")
        raise HTTPException(status_code=500, detail=f"Detection query failed: {str(e)}")

@router.get("/biodiversity/edna-assessment")
async def assess_edna_biodiversity(
    region: Optional[str] = Query(None),
    sample_type: Optional[str] = Query(None),
    marker_gene: Optional[str] = Query(None),
    latitude_min: Optional[float] = Query(None),
    latitude_max: Optional[float] = Query(None),
    longitude_min: Optional[float] = Query(None),
    longitude_max: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Assess biodiversity from eDNA data"""
    try:
        query = db.query(UnifiedMarineData, MolecularData).join(
            MolecularData, UnifiedMarineData.id == MolecularData.unified_data_id
        ).filter(
            UnifiedMarineData.data_type == "molecular",
            MolecularData.species_detection.is_not(None)
        )
        
        # Apply filters
        if region:
            query = query.filter(UnifiedMarineData.region.ilike(f"%{region}%"))
        if sample_type:
            query = query.filter(MolecularData.sample_type.ilike(f"%{sample_type}%"))
        if marker_gene:
            query = query.filter(MolecularData.marker_gene.ilike(f"%{marker_gene}%"))
        
        # Spatial filters
        if latitude_min is not None:
            query = query.filter(UnifiedMarineData.latitude >= latitude_min)
        if latitude_max is not None:
            query = query.filter(UnifiedMarineData.latitude <= latitude_max)
        if longitude_min is not None:
            query = query.filter(UnifiedMarineData.longitude >= longitude_min)
        if longitude_max is not None:
            query = query.filter(UnifiedMarineData.longitude <= longitude_max)
        
        results = query.all()
        
        # Process biodiversity data
        all_species = set()
        sample_biodiversity = []
        taxonomic_groups = {}
        
        for marine_data, mol_data in results:
            sample_info = {
                "sample_id": str(marine_data.id),
                "location": {
                    "latitude": marine_data.latitude,
                    "longitude": marine_data.longitude,
                    "region": marine_data.region
                },
                "collection_date": marine_data.collection_date.isoformat() if marine_data.collection_date else None,
                "species_detected": [],
                "biodiversity_indices": mol_data.biodiversity_indices or {}
            }
            
            # Extract species from detection data
            if mol_data.species_detection:
                if isinstance(mol_data.species_detection, dict):
                    for species, data in mol_data.species_detection.items():
                        all_species.add(species)
                        sample_info["species_detected"].append(species)
                        
                        # Group by taxonomy if available
                        if mol_data.taxonomic_assignment and species in mol_data.taxonomic_assignment:
                            tax_data = mol_data.taxonomic_assignment[species]
                            if isinstance(tax_data, dict):
                                phylum = tax_data.get("phylum", "Unknown")
                                if phylum not in taxonomic_groups:
                                    taxonomic_groups[phylum] = set()
                                taxonomic_groups[phylum].add(species)
            
            sample_biodiversity.append(sample_info)
        
        # Convert sets to lists for JSON serialization
        for phylum in taxonomic_groups:
            taxonomic_groups[phylum] = list(taxonomic_groups[phylum])
        
        # Calculate regional biodiversity metrics
        biodiversity_summary = {
            "total_species_detected": len(all_species),
            "total_samples": len(sample_biodiversity),
            "taxonomic_groups": taxonomic_groups,
            "species_per_sample_avg": sum(len(s["species_detected"]) for s in sample_biodiversity) / len(sample_biodiversity) if sample_biodiversity else 0,
            "detection_methods": list(set(r[1].marker_gene for r in results if r[1].marker_gene)),
            "sample_types": list(set(r[1].sample_type for r in results if r[1].sample_type))
        }
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "edna_biodiversity_assessment",
            "biodiversity_summary": biodiversity_summary,
            "region": region,
            "sample_count": len(sample_biodiversity),
            "filters": {
                "region": region,
                "sample_type": sample_type,
                "marker_gene": marker_gene,
                "spatial_bounds": {
                    "latitude_range": [latitude_min, latitude_max],
                    "longitude_range": [longitude_min, longitude_max]
                }
            }
        })
        
        return {
            "analysis_parameters": {
                "region": region,
                "sample_type": sample_type,
                "marker_gene": marker_gene,
                "spatial_bounds": {
                    "latitude_range": [latitude_min, latitude_max],
                    "longitude_range": [longitude_min, longitude_max]
                }
            },
            "biodiversity_summary": biodiversity_summary,
            "sample_biodiversity": sample_biodiversity[:500],  # Limit for response size
            "ai_analysis": ai_analysis,
            "conservation_insights": {
                "diversity_rating": "High" if len(all_species) > 50 else "Medium" if len(all_species) > 20 else "Low",
                "detection_coverage": "Good" if len(sample_biodiversity) > 10 else "Limited",
                "taxonomic_coverage": len(taxonomic_groups)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to assess eDNA biodiversity: {e}")
        raise HTTPException(status_code=500, detail=f"Biodiversity assessment failed: {str(e)}")

@router.post("/sequence/analyze")
async def analyze_dna_sequence(
    sequence_data: str = Body(..., description="DNA sequence to analyze"),
    marker_gene: str = Body(..., description="Marker gene type (16S, 18S, COI, etc.)"),
    analysis_type: str = Body("species_identification", description="Type of analysis to perform"),
    db: Session = Depends(get_db)
):
    """Analyze DNA sequence for species identification and comparison"""
    try:
        # Basic sequence validation
        sequence_clean = sequence_data.upper().replace(" ", "").replace("\n", "")
        valid_bases = set("ATCG")
        if not all(base in valid_bases for base in sequence_clean):
            raise HTTPException(status_code=400, detail="Invalid DNA sequence - contains non-standard bases")
        
        # Query for similar sequences in database
        query = db.query(UnifiedMarineData, MolecularData).join(
            MolecularData, UnifiedMarineData.id == MolecularData.unified_data_id
        ).filter(
            UnifiedMarineData.data_type == "molecular",
            MolecularData.marker_gene.ilike(f"%{marker_gene}%"),
            MolecularData.sequence_data.is_not(None)
        )
        
        results = query.limit(1000).all()
        
        # Simple sequence comparison (in production, use BLAST or similar)
        sequence_matches = []
        for marine_data, mol_data in results:
            if mol_data.sequence_data:
                stored_sequence = mol_data.sequence_data.upper().replace(" ", "").replace("\n", "")
                
                # Calculate simple similarity (Hamming distance for same length sequences)
                if len(stored_sequence) == len(sequence_clean):
                    matches = sum(a == b for a, b in zip(sequence_clean, stored_sequence))
                    similarity = matches / len(sequence_clean)
                    
                    if similarity > 0.8:  # High similarity threshold
                        sequence_matches.append({
                            "species": marine_data.scientific_name,
                            "similarity": similarity,
                            "sequence_length": len(stored_sequence),
                            "marker_gene": mol_data.marker_gene,
                            "taxonomic_assignment": mol_data.taxonomic_assignment,
                            "detection_probability": mol_data.detection_probability,
                            "location": {
                                "region": marine_data.region,
                                "latitude": marine_data.latitude,
                                "longitude": marine_data.longitude
                            }
                        })
        
        # Sort by similarity
        sequence_matches.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Generate AI analysis
        ai_analysis = await ai_service.analyze_marine_data({
            "analysis_type": "sequence_analysis",
            "sequence_length": len(sequence_clean),
            "marker_gene": marker_gene,
            "analysis_requested": analysis_type,
            "matches_found": len(sequence_matches),
            "top_matches": sequence_matches[:5]
        })
        
        return {
            "sequence_info": {
                "length": len(sequence_clean),
                "gc_content": (sequence_clean.count("G") + sequence_clean.count("C")) / len(sequence_clean),
                "marker_gene": marker_gene,
                "analysis_type": analysis_type
            },
            "sequence_matches": sequence_matches[:20],  # Top 20 matches
            "identification_summary": {
                "total_matches": len(sequence_matches),
                "high_confidence_matches": len([m for m in sequence_matches if m["similarity"] > 0.95]),
                "most_likely_species": sequence_matches[0]["species"] if sequence_matches else None,
                "confidence_score": sequence_matches[0]["similarity"] if sequence_matches else 0
            },
            "ai_analysis": ai_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze DNA sequence: {e}")
        raise HTTPException(status_code=500, detail=f"Sequence analysis failed: {str(e)}")

@router.post("/data/ingest")
async def ingest_molecular_data(
    source: str = Query(..., description="Data source: csv, manual, lab_export"),
    data_params: Dict[str, Any] = Body(..., description="Parameters for data ingestion")
):
    """Ingest molecular biology data from various sources"""
    try:
        if source == "csv":
            # Ingest from CSV file with molecular data
            result = await data_ingestion_service.ingest_csv_file(
                file_path=data_params.get("file_path", ""),
                data_type="molecular",
                mapping_config=data_params.get("mapping_config", {})
            )
            
        elif source == "lab_export":
            # Handle laboratory data export format
            result = {
                "status": "success",
                "message": "Lab export ingestion would be implemented here",
                "records_processed": 0
            }
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported data source")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Molecular data ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")