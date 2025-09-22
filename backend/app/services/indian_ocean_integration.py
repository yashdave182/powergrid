"""
Indian Ocean Data Integration Pipeline
Processes data from INCOIS, ARGO, FishBase, WoRMS, NCBI, BOLD into unified storage
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.marine_data import (
    UnifiedMarineData, OceanographicData, FisheriesData,
    TaxonomicData, MolecularData, DataIngestionLog
)
from app.services.indian_ocean_apis import (
    incois_client, argo_client, fishbase_client, 
    worms_client, ncbi_client, fetch_integrated_marine_data
)
from app.services.data_ingestion import DataStandardizer
import uuid

logger = logging.getLogger(__name__)

class IndianOceanDataProcessor:
    """Processes and stores data from Indian Ocean APIs"""
    
    def __init__(self):
        self.standardizer = DataStandardizer()
    
    async def process_incois_data(self, incois_response: Dict[str, Any]) -> List[str]:
        """Process INCOIS oceanographic data"""
        processed_ids = []
        
        if incois_response.get("status") != "success":
            return processed_ids
        
        try:
            data = incois_response.get("data", {})
            if "table" in data and "rows" in data["table"]:
                headers = data["table"]["columnNames"]
                rows = data["table"]["rows"]
                
                with next(get_db()) as db:
                    for row in rows:
                        row_data = dict(zip(headers, row))
                        
                        lat, lon = self.standardizer.standardize_coordinates(
                            row_data.get("latitude"), row_data.get("longitude")
                        )
                        
                        marine_data = UnifiedMarineData(
                            data_type="oceanographic",
                            data_category="incois_measurement",
                            collection_date=self.standardizer.standardize_datetime(row_data.get("time")),
                            latitude=lat,
                            longitude=lon,
                            depth=float(row_data.get("depth", 0)) if row_data.get("depth") else None,
                            region="Indian Ocean",
                            source_dataset="INCOIS ERDDAP",
                            source_institution="INCOIS",
                            primary_data=row_data,
                            validation_status="pending"
                        )
                        
                        db.add(marine_data)
                        db.flush()
                        
                        ocean_data = OceanographicData(
                            unified_data_id=marine_data.id,
                            temperature=float(row_data.get("temperature")) if row_data.get("temperature") else None,
                            salinity=float(row_data.get("salinity")) if row_data.get("salinity") else None,
                            instrument_type="INCOIS Sensor"
                        )
                        
                        db.add(ocean_data)
                        processed_ids.append(str(marine_data.id))
                    
                    db.commit()
                    logger.info(f"Processed {len(processed_ids)} INCOIS records")
                    
        except Exception as e:
            logger.error(f"INCOIS processing error: {e}")
        
        return processed_ids
    
    async def process_fishbase_data(self, fishbase_response: Dict[str, Any], species_name: str) -> List[str]:
        """Process FishBase species data"""
        processed_ids = []
        
        if fishbase_response.get("status") != "success":
            return processed_ids
        
        try:
            species_data = fishbase_response.get("data", [])
            if not isinstance(species_data, list):
                species_data = [species_data]
            
            with next(get_db()) as db:
                for record in species_data:
                    if not record:
                        continue
                    
                    marine_data = UnifiedMarineData(
                        data_type="fisheries",
                        data_category="species_profile",
                        collection_date=datetime.now(),
                        scientific_name=self.standardizer.standardize_scientific_name(species_name),
                        family=record.get("Family"),
                        genus=record.get("Genus"),
                        species=record.get("Species"),
                        kingdom="Animalia",
                        phylum="Chordata",
                        class_name="Actinopterygii",
                        region="Indian Ocean",
                        source_dataset="FishBase",
                        source_institution="FishBase Consortium",
                        primary_data=record,
                        validation_status="validated",
                        data_quality_score=0.85
                    )
                    
                    db.add(marine_data)
                    db.flush()
                    
                    fish_data = FisheriesData(
                        unified_data_id=marine_data.id,
                        morphometric_data={
                            "max_length": record.get("Length"),
                            "max_weight": record.get("Weight")
                        },
                        ecological_traits={
                            "environment": record.get("DemersPelag"),
                            "vulnerability": record.get("Vulnerability")
                        },
                        habitat_type=record.get("DemersPelag")
                    )
                    
                    db.add(fish_data)
                    processed_ids.append(str(marine_data.id))
                
                db.commit()
                logger.info(f"Processed {len(processed_ids)} FishBase records")
                
        except Exception as e:
            logger.error(f"FishBase processing error: {e}")
        
        return processed_ids
    
    async def process_worms_data(self, worms_response: Dict[str, Any], species_name: str) -> List[str]:
        """Process WoRMS taxonomic data"""
        processed_ids = []
        
        if worms_response.get("status") != "success":
            return processed_ids
        
        try:
            classification = worms_response.get("classification", {})
            
            with next(get_db()) as db:
                marine_data = UnifiedMarineData(
                    data_type="taxonomic",
                    data_category="taxonomic_classification",
                    collection_date=datetime.now(),
                    scientific_name=species_name,
                    region="Global",
                    source_dataset="WoRMS",
                    source_institution="World Register of Marine Species",
                    primary_data=classification,
                    validation_status="validated",
                    data_quality_score=0.95
                )
                
                db.add(marine_data)
                db.flush()
                
                tax_data = TaxonomicData(
                    unified_data_id=marine_data.id,
                    taxonomic_authority="WoRMS",
                    taxonomic_status="accepted",
                    identification_confidence=0.95,
                    identification_method="WoRMS API",
                    identification_date=datetime.now()
                )
                
                db.add(tax_data)
                processed_ids.append(str(marine_data.id))
                
                db.commit()
                logger.info(f"Processed WoRMS data for {species_name}")
                
        except Exception as e:
            logger.error(f"WoRMS processing error: {e}")
        
        return processed_ids
    
    async def process_integrated_batch(self, species_list: List[str] = None) -> Dict[str, Any]:
        """Process batch of integrated data from all APIs"""
        if species_list is None:
            species_list = [
                "Rastrelliger kanagurta",  # Indian mackerel
                "Thunnus albacares",       # Yellowfin tuna
                "Katsuwonus pelamis"       # Skipjack tuna
            ]
        
        batch_results = {
            "batch_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "total_records": 0,
            "species_processed": []
        }
        
        # Process oceanographic data
        try:
            incois_data = await incois_client.get_oceanographic_data()
            incois_ids = await self.process_incois_data(incois_data)
            batch_results["total_records"] += len(incois_ids)
        except Exception as e:
            logger.error(f"Oceanographic processing error: {e}")
        
        # Process species data
        for species in species_list:
            try:
                integrated_data = await fetch_integrated_marine_data(
                    species_name=species,
                    data_types=["fisheries", "taxonomic"]
                )
                
                species_records = 0
                sources = integrated_data.get("sources", {})
                
                if "fishbase" in sources:
                    fishbase_ids = await self.process_fishbase_data(sources["fishbase"], species)
                    species_records += len(fishbase_ids)
                
                if "worms" in sources:
                    worms_ids = await self.process_worms_data(sources["worms"], species)
                    species_records += len(worms_ids)
                
                batch_results["species_processed"].append({
                    "species": species,
                    "records": species_records
                })
                batch_results["total_records"] += species_records
                
            except Exception as e:
                logger.error(f"Species {species} processing error: {e}")
        
        return batch_results

# Global processor instance
indian_ocean_processor = IndianOceanDataProcessor()