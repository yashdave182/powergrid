"""
Indian Ocean & International Marine Data APIs Integration
Specifically designed for CMLRE Marine Data Platform
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote
import logging

logger = logging.getLogger(__name__)

class INCOISClient:
    """Client for INCOIS (Indian National Centre for Ocean Information Services)"""
    
    def __init__(self):
        self.base_url = "https://incois.gov.in/erddap"
        self.client = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
    
    async def close(self):
        await self.client.aclose()
    
    async def get_oceanographic_data(self, 
                                   dataset_id: str = "OSF_Temperature",
                                   latitude_min: float = 8.0,
                                   latitude_max: float = 15.0,
                                   longitude_min: float = 72.0,
                                   longitude_max: float = 78.0,
                                   start_date: str = "2023-01-01",
                                   end_date: str = "2024-01-01",
                                   variables: List[str] = None) -> Dict[str, Any]:
        """Get oceanographic data from INCOIS ERDDAP server"""
        try:
            if variables is None:
                variables = ["latitude", "longitude", "depth", "temperature", "salinity"]
            
            # Build ERDDAP query
            params = {
                "latitude": f">={latitude_min}",
                "latitude_max": f"<={latitude_max}",
                "longitude": f">={longitude_min}", 
                "longitude_max": f"<={longitude_max}",
                "time": f">={start_date}",
                "time_max": f"<={end_date}"
            }
            
            # Construct URL
            variable_str = ",".join(variables)
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.base_url}/tabledap/{dataset_id}.json?{variable_str}&{query_params}"
            
            logger.info(f"INCOIS request: {url}")
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "INCOIS",
                    "dataset": dataset_id,
                    "status": "success",
                    "data": data,
                    "query_params": params
                }
            else:
                return {
                    "source": "INCOIS", 
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "dataset": dataset_id
                }
                
        except Exception as e:
            logger.error(f"INCOIS API error: {e}")
            return {
                "source": "INCOIS",
                "status": "error", 
                "error": str(e),
                "dataset": dataset_id
            }

class ArgoFloatsClient:
    """Client for ARGO Global Float Data (Indian Ocean)"""
    
    def __init__(self):
        self.base_url = "https://erddap.ifremer.fr/erddap"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def get_argo_profiles(self,
                              latitude_min: float = -20.0,
                              latitude_max: float = 30.0, 
                              longitude_min: float = 30.0,
                              longitude_max: float = 120.0,
                              start_date: str = "2023-01-01",
                              limit: int = 1000) -> Dict[str, Any]:
        """Get ARGO float profiles for Indian Ocean region"""
        try:
            params = {
                "latitude": f">={latitude_min}",
                "latitude_max": f"<={latitude_max}",
                "longitude": f">={longitude_min}",
                "longitude_max": f"<={longitude_max}",
                "time": f">={start_date}"
            }
            
            variables = ["platform_number", "latitude", "longitude", "time", "pres", "temp", "psal"]
            variable_str = ",".join(variables)
            query_params = "&".join([f"{k}={v}" for k, v in params.items()])
            
            url = f"{self.base_url}/tabledap/ArgoFloats.json?{variable_str}&{query_params}&orderByLimit(\"{limit}\")"
            
            logger.info(f"ARGO request: {url}")
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "ARGO",
                    "status": "success", 
                    "data": data,
                    "region": "Indian Ocean",
                    "query_params": params
                }
            else:
                return {
                    "source": "ARGO",
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"ARGO API error: {e}")
            return {
                "source": "ARGO",
                "status": "error",
                "error": str(e)
            }

class FishBaseAPIClient:
    """Client for FishBase API"""
    
    def __init__(self):
        self.base_url = "https://fishbaseapi.azurewebsites.net"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def get_species_data(self, genus: str, species: str) -> Dict[str, Any]:
        """Get species data from FishBase"""
        try:
            url = f"{self.base_url}/species/Genus={genus}&Species={species}"
            
            logger.info(f"FishBase request: {url}")
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "FishBase",
                    "status": "success",
                    "species": f"{genus} {species}",
                    "data": data
                }
            else:
                return {
                    "source": "FishBase",
                    "status": "error", 
                    "species": f"{genus} {species}",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"FishBase API error: {e}")
            return {
                "source": "FishBase",
                "status": "error",
                "species": f"{genus} {species}",
                "error": str(e)
            }
    
    async def search_indian_ocean_species(self) -> Dict[str, Any]:
        """Search for common Indian Ocean fish species"""
        # Common Indian Ocean species to query
        species_list = [
            ("Rastrelliger", "kanagurta"),  # Indian mackerel
            ("Thunnus", "albacares"),       # Yellowfin tuna
            ("Katsuwonus", "pelamis"),      # Skipjack tuna
            ("Selar", "crumenophthalmus"),  # Bigeye scad
            ("Decapterus", "russelli")      # Indian scad
        ]
        
        results = []
        for genus, species in species_list:
            species_data = await self.get_species_data(genus, species)
            results.append(species_data)
        
        return {
            "source": "FishBase",
            "query": "Indian Ocean species search",
            "results": results,
            "total_species": len(results)
        }

class WoRMSClient:
    """Client for World Register of Marine Species (WoRMS)"""
    
    def __init__(self):
        self.base_url = "http://www.marinespecies.org/rest"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def get_aphia_id(self, scientific_name: str) -> Dict[str, Any]:
        """Get AphiaID for a scientific name"""
        try:
            encoded_name = quote(scientific_name)
            url = f"{self.base_url}/AphiaIDByName/{encoded_name}"
            
            logger.info(f"WoRMS AphiaID request: {url}")
            response = await self.client.get(url)
            
            if response.status_code == 200:
                aphia_id = response.text.strip()
                if aphia_id != "-999":  # WoRMS returns -999 for not found
                    return {
                        "source": "WoRMS",
                        "status": "success",
                        "scientific_name": scientific_name,
                        "aphia_id": int(aphia_id)
                    }
                else:
                    return {
                        "source": "WoRMS",
                        "status": "not_found",
                        "scientific_name": scientific_name,
                        "aphia_id": None
                    }
            else:
                return {
                    "source": "WoRMS",
                    "status": "error",
                    "scientific_name": scientific_name,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"WoRMS API error: {e}")
            return {
                "source": "WoRMS",
                "status": "error",
                "scientific_name": scientific_name,
                "error": str(e)
            }
    
    async def get_taxonomic_classification(self, aphia_id: int) -> Dict[str, Any]:
        """Get complete taxonomic classification for an AphiaID"""
        try:
            url = f"{self.base_url}/AphiaClassificationByAphiaID/{aphia_id}"
            
            logger.info(f"WoRMS classification request: {url}")
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "WoRMS",
                    "status": "success",
                    "aphia_id": aphia_id,
                    "classification": data
                }
            else:
                return {
                    "source": "WoRMS", 
                    "status": "error",
                    "aphia_id": aphia_id,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"WoRMS classification error: {e}")
            return {
                "source": "WoRMS",
                "status": "error", 
                "aphia_id": aphia_id,
                "error": str(e)
            }
    
    async def get_complete_species_info(self, scientific_name: str) -> Dict[str, Any]:
        """Get complete species information including taxonomy"""
        # First get AphiaID
        aphia_result = await self.get_aphia_id(scientific_name)
        
        if aphia_result["status"] == "success" and aphia_result["aphia_id"]:
            # Then get classification
            classification = await self.get_taxonomic_classification(aphia_result["aphia_id"])
            
            return {
                "source": "WoRMS",
                "scientific_name": scientific_name,
                "aphia_id": aphia_result["aphia_id"],
                "classification": classification.get("classification", {}),
                "status": "success"
            }
        else:
            return aphia_result

class NCBIClient:
    """Client for NCBI E-utilities API (Molecular data)"""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def search_sequences(self, 
                             organism: str,
                             gene: str = "COI",
                             database: str = "nucleotide",
                             max_results: int = 100) -> Dict[str, Any]:
        """Search for DNA sequences in NCBI"""
        try:
            # Build search term
            search_term = f"{organism}[Organism] AND {gene}[Gene]"
            
            # Search step
            search_params = {
                "db": database,
                "term": search_term,
                "retmax": str(max_results),
                "retmode": "json"
            }
            
            search_url = f"{self.base_url}/esearch.fcgi"
            logger.info(f"NCBI search: {search_url}?{urlencode(search_params)}")
            
            search_response = await self.client.get(search_url, params=search_params)
            
            if search_response.status_code != 200:
                return {
                    "source": "NCBI",
                    "status": "error",
                    "error": f"Search failed: HTTP {search_response.status_code}"
                }
            
            search_data = search_response.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return {
                    "source": "NCBI",
                    "status": "no_results",
                    "organism": organism,
                    "gene": gene,
                    "search_term": search_term
                }
            
            # Fetch sequences
            fetch_params = {
                "db": database,
                "id": ",".join(id_list[:20]),  # Limit to first 20 results
                "rettype": "fasta",
                "retmode": "text"
            }
            
            fetch_url = f"{self.base_url}/efetch.fcgi"
            fetch_response = await self.client.get(fetch_url, params=fetch_params)
            
            if fetch_response.status_code == 200:
                sequences = fetch_response.text
                return {
                    "source": "NCBI",
                    "status": "success",
                    "organism": organism,
                    "gene": gene,
                    "search_term": search_term,
                    "sequence_count": len(id_list),
                    "sequences_retrieved": len(id_list[:20]),
                    "sequences": sequences,
                    "id_list": id_list[:20]
                }
            else:
                return {
                    "source": "NCBI",
                    "status": "error",
                    "error": f"Fetch failed: HTTP {fetch_response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"NCBI API error: {e}")
            return {
                "source": "NCBI",
                "status": "error",
                "organism": organism,
                "gene": gene,
                "error": str(e)
            }

class BOLDClient:
    """Client for BOLD (Barcode of Life) Systems API"""
    
    def __init__(self):
        self.base_url = "http://v3.boldsystems.org/index.php/API_Public"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def search_taxon(self, taxon_name: str) -> Dict[str, Any]:
        """Search for taxon data in BOLD"""
        try:
            params = {"taxName": taxon_name}
            url = f"{self.base_url}/TaxonSearch"
            
            logger.info(f"BOLD taxon search: {url}?{urlencode(params)}")
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                # BOLD returns various formats - try to parse as JSON
                try:
                    data = response.json()
                except:
                    # If not JSON, return as text
                    data = response.text
                
                return {
                    "source": "BOLD",
                    "status": "success",
                    "taxon_name": taxon_name,
                    "data": data
                }
            else:
                return {
                    "source": "BOLD",
                    "status": "error",
                    "taxon_name": taxon_name,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"BOLD API error: {e}")
            return {
                "source": "BOLD",
                "status": "error",
                "taxon_name": taxon_name,
                "error": str(e)
            }
    
    async def get_specimen_records(self, taxon_name: str) -> Dict[str, Any]:
        """Get specimen records from BOLD"""
        try:
            params = {"taxon": taxon_name}
            url = f"{self.base_url}/Specimen"
            
            logger.info(f"BOLD specimen search: {url}?{urlencode(params)}")
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    data = response.text
                
                return {
                    "source": "BOLD",
                    "status": "success",
                    "taxon_name": taxon_name,
                    "data_type": "specimens",
                    "data": data
                }
            else:
                return {
                    "source": "BOLD",
                    "status": "error",
                    "taxon_name": taxon_name,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"BOLD specimen API error: {e}")
            return {
                "source": "BOLD",
                "status": "error",
                "taxon_name": taxon_name,
                "error": str(e)
            }

# Global client instances
incois_client = INCOISClient()
argo_client = ArgoFloatsClient()
fishbase_client = FishBaseAPIClient()
worms_client = WoRMSClient()
ncbi_client = NCBIClient()
bold_client = BOLDClient()

# Unified integration function
async def fetch_integrated_marine_data(
    species_name: Optional[str] = None,
    region: str = "indian_ocean",
    data_types: List[str] = None
) -> Dict[str, Any]:
    """
    Fetch integrated marine data from multiple Indian Ocean and international sources
    """
    if data_types is None:
        data_types = ["oceanographic", "fisheries", "taxonomic", "molecular"]
    
    results = {
        "query": {
            "species_name": species_name,
            "region": region,
            "data_types": data_types,
            "timestamp": datetime.now().isoformat()
        },
        "sources": {}
    }
    
    # Oceanographic data
    if "oceanographic" in data_types:
        try:
            # INCOIS data
            incois_data = await incois_client.get_oceanographic_data()
            results["sources"]["incois"] = incois_data
            
            # ARGO data
            argo_data = await argo_client.get_argo_profiles()
            results["sources"]["argo"] = argo_data
            
        except Exception as e:
            logger.error(f"Oceanographic data fetch error: {e}")
    
    # Fisheries data
    if "fisheries" in data_types and species_name:
        try:
            # Extract genus and species
            name_parts = species_name.split()
            if len(name_parts) >= 2:
                genus, species = name_parts[0], name_parts[1]
                fishbase_data = await fishbase_client.get_species_data(genus, species)
                results["sources"]["fishbase"] = fishbase_data
            
        except Exception as e:
            logger.error(f"Fisheries data fetch error: {e}")
    
    # Taxonomic data
    if "taxonomic" in data_types and species_name:
        try:
            worms_data = await worms_client.get_complete_species_info(species_name)
            results["sources"]["worms"] = worms_data
            
        except Exception as e:
            logger.error(f"Taxonomic data fetch error: {e}")
    
    # Molecular data
    if "molecular" in data_types and species_name:
        try:
            # NCBI sequences
            ncbi_data = await ncbi_client.search_sequences(species_name, "COI")
            results["sources"]["ncbi"] = ncbi_data
            
            # BOLD data
            bold_data = await bold_client.search_taxon(species_name)
            results["sources"]["bold"] = bold_data
            
        except Exception as e:
            logger.error(f"Molecular data fetch error: {e}")
    
    return results