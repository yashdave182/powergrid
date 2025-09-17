import httpx
import asyncio
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class OBISClient:
    """Client for OBIS (Ocean Biodiversity Information System) API"""
    
    def __init__(self):
        self.base_url = settings.obis_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def search_species(self, 
                           scientific_name: Optional[str] = None,
                           geometry: Optional[str] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           limit: int = 100,
                           offset: int = 0) -> Dict[str, Any]:
        """Search for species occurrences in OBIS v3 API
        
        Args:
            scientific_name: Scientific name (e.g., "Mola mola")
            geometry: WKT geometry (e.g., "POLYGON((...))") 
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of results (default 100)
            offset: Number of results to skip (default 0)
        """
        try:
            params: Dict[str, str] = {
                "limit": str(limit),
                "offset": str(offset)
            }
            
            if scientific_name:
                params["scientificname"] = scientific_name
            if geometry:
                params["geometry"] = geometry
            if start_date:
                params["startdate"] = start_date
            if end_date:
                params["enddate"] = end_date
            
            logger.info(f"OBIS occurrence request to: {self.base_url}occurrence with params: {params}")
            response = await self.client.get(f"{self.base_url}occurrence", params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"OBIS occurrence response successful, found {data.get('total', 0)} records")
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OBIS occurrence HTTP error {e.response.status_code}: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"OBIS API error: {e.response.text}")
        except Exception as e:
            logger.error(f"OBIS occurrence request failed: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to search species: {str(e)}")
    
    async def get_taxa_info(self, taxon_id: int) -> Dict[str, Any]:
        """Get detailed taxonomic information"""
        try:
            response = await self.client.get(f"{self.base_url}taxon/{taxon_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get taxa info: {e}")
            raise
    
    async def search_taxa(self, 
                         scientific_name: Optional[str] = None,
                         rank: Optional[str] = None,
                         limit: int = 100) -> Dict[str, Any]:
        """Search for taxonomic information
        
        Args:
            scientific_name: Scientific name to search for
            rank: Taxonomic rank (e.g., 'species', 'genus', 'family')
            limit: Maximum number of results
        """
        try:
            params: Dict[str, str] = {"limit": str(limit)}
            if scientific_name:
                params["scientificname"] = scientific_name
            if rank:
                params["rank"] = rank
                
            response = await self.client.get(f"{self.base_url}taxon", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to search taxa: {e}")
            raise
    
    async def get_datasets(self, limit: int = 100) -> Dict[str, Any]:
        """Get dataset metadata from OBIS v3 API"""
        try:
            params = {"limit": str(limit)}
            logger.info(f"OBIS datasets request to: {self.base_url}dataset")
            
            response = await self.client.get(f"{self.base_url}dataset", params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"OBIS datasets response successful, data type: {type(data)}")
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OBIS datasets HTTP error {e.response.status_code}: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"OBIS API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Failed to get datasets: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve datasets: {str(e)}")
    
    async def get_checklist(self, 
                          geometry: Optional[str] = None,
                          taxon_id: Optional[int] = None,
                          limit: int = 100) -> Dict[str, Any]:
        """Get species checklist for a region or taxonomic group
        
        Args:
            geometry: WKT geometry for spatial filtering
            taxon_id: Taxonomic ID to filter by
            limit: Maximum number of results
        """
        try:
            params: Dict[str, str] = {"limit": str(limit)}
            if geometry:
                params["geometry"] = geometry
            if taxon_id:
                params["taxonid"] = str(taxon_id)
                
            response = await self.client.get(f"{self.base_url}checklist", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get checklist: {e}")
            raise
    
    async def get_nodes(self) -> Dict[str, Any]:
        """Get OBIS data provider nodes"""
        try:
            response = await self.client.get(f"{self.base_url}node")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            raise
    
    async def get_statistics(self, geometry: Optional[str] = None) -> Dict[str, Any]:
        """Get biodiversity statistics for a region"""
        try:
            params = {}
            if geometry:
                params["geometry"] = geometry
                
            response = await self.client.get(f"{self.base_url}statistics", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise

class GBIFClient:
    """Client for GBIF (Global Biodiversity Information Facility) API"""
    
    def __init__(self):
        self.base_url = settings.gbif_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def search_occurrences(self,
                                scientific_name: Optional[str] = None,
                                country: Optional[str] = None,
                                year: Optional[int] = None,
                                limit: int = 100) -> Dict[str, Any]:
        """Search for species occurrences in GBIF"""
        try:
            params: Dict[str, str] = {
                "limit": str(limit),
                "offset": "0"
            }
            
            if scientific_name:
                params["scientificName"] = scientific_name
            if country:
                params["country"] = country
            if year:
                params["year"] = str(year)
            
            response = await self.client.get(f"{self.base_url}occurrence/search", params=params)
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"GBIF API request failed: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"GBIF API HTTP error: {e}")
            raise
    
    async def get_species_info(self, species_key: int) -> Dict[str, Any]:
        """Get detailed species information"""
        try:
            response = await self.client.get(f"{self.base_url}species/{species_key}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get species info: {e}")
            raise
    
    async def search_species(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search for species by name"""
        try:
            params: Dict[str, str] = {
                "q": query,
                "limit": str(limit)
            }
            
            response = await self.client.get(f"{self.base_url}species/search", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to search species: {e}")
            raise

# Global client instances
obis_client = OBISClient()
gbif_client = GBIFClient()