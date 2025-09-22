<<<<<<< HEAD
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
        
        # Handle both successful responses and error responses from the client
        if "error" in datasets:
            return {
                "status": "error",
                "message": datasets["error"],
                "details": datasets.get("details", ""),
                "total_datasets": 0,
                "datasets": [],
                "source": "OBIS"
            }
        
        return {
            "status": "success",
            "total_datasets": len(datasets.get("results", [])),
            "datasets": datasets,
            "source": "OBIS"
        }
        
    except Exception as e:
        logger.error(f"Failed to get datasets: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "total_datasets": 0,
            "datasets": [],
            "source": "OBIS"
        }

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
@router.get("/test/obis")
async def test_obis_connection():
    """Test OBIS API connection with a simple request"""
    try:
        import httpx
        
        # Direct test without using the client
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Basic API availability
            test_url = "https://api.obis.org/v3/occurrence?limit=5"
            logger.info(f"Testing OBIS API directly: {test_url}")
            
            response = await client.get(test_url)
            logger.info(f"Direct OBIS test response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "message": "OBIS API v3 connection working",
                    "test_url": test_url,
                    "total_records": data.get("total", 0),
                    "sample_count": len(data.get("results", [])),
                    "api_response_keys": list(data.keys()) if isinstance(data, dict) else "not dict"
                }
            else:
                return {
                    "status": "error",
                    "message": f"OBIS API returned status {response.status_code}",
                    "response_text": response.text[:500],
                    "test_url": test_url
                }
                
    except Exception as e:
        logger.error(f"OBIS connection test failed: {e}")
        return {
            "status": "error",
            "message": f"OBIS API connection failed: {str(e)}",
            "error_type": type(e).__name__,
            "test_url": "https://api.obis.org/v3/occurrence?limit=5"
        }

@router.get("/test/config")
async def test_configuration():
    """Test API configuration and network connectivity"""
    try:
        from app.config import settings
        import httpx
        
        # Test basic configuration
        config_info = {
            "obis_api_url": settings.obis_api_url,
            "gbif_api_url": settings.gbif_api_url,
            "environment": settings.environment,
            "debug": settings.debug
        }
        
        # Test basic network connectivity
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Test if we can reach the internet
                response = await client.get("https://httpbin.org/json")
                network_test = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code
                }
            except Exception as e:
                network_test = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Test OBIS API base URL
            try:
                response = await client.get("https://api.obis.org/")
                obis_base_test = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code
                }
            except Exception as e:
                obis_base_test = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return {
            "configuration": config_info,
            "network_test": network_test,
            "obis_base_test": obis_base_test
        }
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return {
            "error": f"Configuration test failed: {str(e)}",
            "error_type": type(e).__name__
        }

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
=======
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
        
        # Handle both successful responses and error responses from the client
        if "error" in datasets:
            return {
                "status": "error",
                "message": datasets["error"],
                "details": datasets.get("details", ""),
                "total_datasets": 0,
                "datasets": [],
                "source": "OBIS"
            }
        
        return {
            "status": "success",
            "total_datasets": len(datasets.get("results", [])),
            "datasets": datasets,
            "source": "OBIS"
        }
        
    except Exception as e:
        logger.error(f"Failed to get datasets: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "total_datasets": 0,
            "datasets": [],
            "source": "OBIS"
        }

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
@router.get("/test/obis")
async def test_obis_connection():
    """Test OBIS API connection with a simple request"""
    try:
        import httpx
        
        # Direct test without using the client
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Basic API availability
            test_url = "https://api.obis.org/v3/occurrence?limit=5"
            logger.info(f"Testing OBIS API directly: {test_url}")
            
            response = await client.get(test_url)
            logger.info(f"Direct OBIS test response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "message": "OBIS API v3 connection working",
                    "test_url": test_url,
                    "total_records": data.get("total", 0),
                    "sample_count": len(data.get("results", [])),
                    "api_response_keys": list(data.keys()) if isinstance(data, dict) else "not dict"
                }
            else:
                return {
                    "status": "error",
                    "message": f"OBIS API returned status {response.status_code}",
                    "response_text": response.text[:500],
                    "test_url": test_url
                }
                
    except Exception as e:
        logger.error(f"OBIS connection test failed: {e}")
        return {
            "status": "error",
            "message": f"OBIS API connection failed: {str(e)}",
            "error_type": type(e).__name__,
            "test_url": "https://api.obis.org/v3/occurrence?limit=5"
        }

@router.get("/test/config")
async def test_configuration():
    """Test API configuration and network connectivity"""
    try:
        from app.config import settings
        import httpx
        
        # Test basic configuration
        config_info = {
            "obis_api_url": settings.obis_api_url,
            "gbif_api_url": settings.gbif_api_url,
            "environment": settings.environment,
            "debug": settings.debug
        }
        
        # Test basic network connectivity
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Test if we can reach the internet
                response = await client.get("https://httpbin.org/json")
                network_test = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code
                }
            except Exception as e:
                network_test = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Test OBIS API base URL
            try:
                response = await client.get("https://api.obis.org/")
                obis_base_test = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code
                }
            except Exception as e:
                obis_base_test = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return {
            "configuration": config_info,
            "network_test": network_test,
            "obis_base_test": obis_base_test
        }
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return {
            "error": f"Configuration test failed: {str(e)}",
            "error_type": type(e).__name__
        }

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
>>>>>>> 362b52b683dacbc43ff77fceb651bab6d409b1b0
        raise HTTPException(status_code=500, detail=f"eDNA analysis failed: {str(e)}")