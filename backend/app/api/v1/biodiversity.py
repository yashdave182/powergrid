from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from app.services.external_apis import obis_client, gbif_client
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/species/search")
async def search_species(
    scientific_name: Optional[str] = Query(None, description="Scientific name of species"),
    region: Optional[str] = Query(None, description="Geographic region (WKT format)"),
    data_source: str = Query("both", description="Data source: 'obis', 'gbif', or 'both'"),
    limit: int = Query(100, description="Maximum number of results")
):
    """Search for species across biodiversity databases"""
    try:
        results = {}
        
        if data_source in ["obis", "both"]:
            obis_data = await obis_client.search_species(
                scientific_name=scientific_name,
                geometry=region,
                limit=limit
            )
            results["obis"] = obis_data
        
        if data_source in ["gbif", "both"]:
            gbif_data = await gbif_client.search_occurrences(
                scientific_name=scientific_name,
                limit=limit
            )
            results["gbif"] = gbif_data
        
        # Generate LLM insights if we have data
        if results:
            insights = await llm_service.generate_species_insights(
                [results.get("obis", {}), results.get("gbif", {})]
            )
            results["ai_insights"] = insights
        
        return {
            "query": {
                "scientific_name": scientific_name,
                "region": region,
                "data_source": data_source
            },
            "results": results,
            "total_sources": len([k for k in results.keys() if k != "ai_insights"])
        }
        
    except Exception as e:
        logger.error(f"Species search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Species search failed: {str(e)}")

@router.get("/species/{species_id}/details")
async def get_species_details(
    species_id: str,
    source: str = Query("obis", description="Data source: 'obis' or 'gbif'")
):
    """Get detailed information about a specific species"""
    try:
        if source == "obis":
            species_data = await obis_client.get_taxa_info(int(species_id))
        elif source == "gbif":
            species_data = await gbif_client.get_species_info(int(species_id))
        else:
            raise HTTPException(status_code=400, detail="Invalid source. Use 'obis' or 'gbif'")
        
        # Generate LLM analysis of the species data
        analysis = await llm_service.analyze_marine_data(
            species_data,
            f"Provide detailed analysis of this {source.upper()} species data"
        )
        
        return {
            "species_id": species_id,
            "source": source,
            "data": species_data,
            "ai_analysis": analysis
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid species ID format")
    except Exception as e:
        logger.error(f"Failed to get species details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve species details: {str(e)}")

@router.get("/diversity/statistics")
async def get_biodiversity_statistics(
    region: Optional[str] = Query(None, description="Geographic region (WKT format)"),
    include_analysis: bool = Query(True, description="Include AI analysis of statistics")
):
    """Get biodiversity statistics for a region"""
    try:
        stats = await obis_client.get_statistics(geometry=region)
        
        result = {
            "region": region,
            "statistics": stats
        }
        
        if include_analysis:
            analysis = await llm_service.analyze_marine_data(
                stats,
                "Analyze these biodiversity statistics and provide insights about ecosystem health"
            )
            result["ai_analysis"] = analysis
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get biodiversity statistics: {e}")
@router.get("/datasets")
async def get_datasets(
    limit: int = Query(100, description="Maximum number of datasets to return")
):
    """Get marine biodiversity datasets from OBIS"""
    try:
        datasets = await obis_client.get_datasets(limit=limit)
        
        return {
            "total_datasets": len(datasets.get("results", [])),
            "datasets": datasets,
            "source": "OBIS"
        }
        
    except Exception as e:
        logger.error(f"Failed to get datasets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve datasets: {str(e)}")

@router.get("/checklist")
async def get_species_checklist(
    region: Optional[str] = Query(None, description="Geographic region (WKT format)"),
    taxon_id: Optional[int] = Query(None, description="Taxonomic ID to filter by"),
    limit: int = Query(100, description="Maximum number of species")
):
    """Get species checklist for a region or taxonomic group"""
    try:
        checklist = await obis_client.get_checklist(
            geometry=region,
            taxon_id=taxon_id,
            limit=limit
        )
        
        return {
            "region": region,
            "taxon_id": taxon_id,
            "checklist": checklist,
            "total_species": len(checklist.get("results", [])),
            "source": "OBIS"
        }
        
    except Exception as e:
        logger.error(f"Failed to get checklist: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve checklist: {str(e)}")

@router.get("/taxa/search")
async def search_taxa(
    scientific_name: Optional[str] = Query(None, description="Scientific name to search for"),
    rank: Optional[str] = Query(None, description="Taxonomic rank (species, genus, family, etc.)"),
    limit: int = Query(100, description="Maximum number of results")
):
    """Search for taxonomic information in OBIS"""
    try:
        taxa_data = await obis_client.search_taxa(
            scientific_name=scientific_name,
            rank=rank,
            limit=limit
        )
        
        return {
            "query": {
                "scientific_name": scientific_name,
                "rank": rank
            },
            "taxa": taxa_data,
            "total_results": len(taxa_data.get("results", [])),
            "source": "OBIS"
        }
        
    except Exception as e:
        logger.error(f"Failed to search taxa: {e}")
        raise HTTPException(status_code=500, detail=f"Taxa search failed: {str(e)}")

@router.get("/nodes")
async def get_data_providers():
    """Get OBIS data provider nodes"""
    try:
        nodes = await obis_client.get_nodes()
        
        return {
            "nodes": nodes,
            "total_providers": len(nodes.get("results", [])),
            "source": "OBIS"
        }
        
    except Exception as e:
        logger.error(f"Failed to get data providers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data providers: {str(e)}")

@router.post("/species/identify")
async def identify_species(
    observation_data: Dict[str, Any]
):
    """Identify species based on observation data using AI"""
    try:
        # Use LLM to analyze observation data and suggest species identification
        identification = await llm_service.analyze_marine_data(
            observation_data,
            "Based on this observation data, help identify the species and provide confidence levels"
        )
        
        # Also search for similar species in databases
        potential_matches = []
        if "scientific_name" in observation_data:
            gbif_results = await gbif_client.search_species(
                observation_data["scientific_name"]
            )
            potential_matches.append(gbif_results)
        
        return {
            "observation_data": observation_data,
            "ai_identification": identification,
            "database_matches": potential_matches
        }
        
    except Exception as e:
        logger.error(f"Species identification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Species identification failed: {str(e)}")

@router.get("/edna/analysis")
async def analyze_edna_data(
    sample_id: str,
    sequence_data: Optional[str] = Query(None, description="DNA sequence data"),
    location: Optional[str] = Query(None, description="Sample location")
):
    """Analyze environmental DNA data for species detection"""
    try:
        # Simulate eDNA analysis (in real implementation, this would use bioinformatics tools)
        edna_data = {
            "sample_id": sample_id,
            "sequence_data": sequence_data,
            "location": location,
            "analysis_timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Use LLM to interpret eDNA results
        analysis = await llm_service.analyze_marine_data(
            edna_data,
            "Analyze this eDNA sample data and provide insights about species presence and biodiversity"
        )
        
        return {
            "sample_data": edna_data,
            "ai_analysis": analysis,
            "recommendations": "Consider cross-referencing with morphological data for validation"
        }
        
    except Exception as e:
        logger.error(f"eDNA analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"eDNA analysis failed: {str(e)}")