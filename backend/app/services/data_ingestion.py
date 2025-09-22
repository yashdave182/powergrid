from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import asyncio
import logging
import json
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db, engine
from app.models.marine_data import (
    UnifiedMarineData, OceanographicData, FisheriesData, 
    TaxonomicData, MolecularData, DataIngestionLog
)
from app.schemas.marine_schemas import (
    UnifiedMarineDataCreate, BaseMarineDataCreate,
    OceanographicDataCreate, FisheriesDataCreate,
    TaxonomicDataCreate, MolecularDataCreate
)
from app.services.external_apis import obis_client, gbif_client
import uuid

logger = logging.getLogger(__name__)

class DataStandardizer:
    """Standardizes incoming data to unified format following international standards"""
    
    @staticmethod
    def standardize_coordinates(lat: Any, lon: Any) -> tuple[Optional[float], Optional[float]]:
        """Standardize coordinate formats"""
        try:
            if lat is not None and lon is not None:
                lat_float = float(lat)
                lon_float = float(lon)
                
                # Validate coordinate ranges
                if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
                    return lat_float, lon_float
                    
            return None, None
        except (ValueError, TypeError):
            return None, None
    
    @staticmethod
    def standardize_datetime(date_value: Any) -> Optional[datetime]:
        """Standardize various datetime formats"""
        if date_value is None:
            return None
            
        try:
            if isinstance(date_value, datetime):
                return date_value
            elif isinstance(date_value, str):
                # Try multiple datetime formats
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%d/%m/%Y",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_value, fmt)
                    except ValueError:
                        continue
                        
            return None
        except Exception:
            return None
    
    @staticmethod
    def standardize_scientific_name(name: Any) -> Optional[str]:
        """Standardize scientific name format"""
        if not name:
            return None
            
        try:
            name_str = str(name).strip()
            # Basic cleaning - remove extra spaces, fix case
            words = name_str.split()
            if len(words) >= 2:
                # Genus should be capitalized, species lowercase
                standardized = f"{words[0].capitalize()} {words[1].lower()}"
                if len(words) > 2:
                    # Handle subspecies/varieties
                    standardized += f" {' '.join(words[2:]).lower()}"
                return standardized
            return name_str
        except Exception:
            return None
    
    @staticmethod
    def extract_taxonomy_from_name(scientific_name: str) -> Dict[str, Optional[str]]:
        """Extract taxonomic components from scientific name"""
        if not scientific_name:
            return {}
            
        parts = scientific_name.strip().split()
        if len(parts) >= 2:
            return {
                "genus": parts[0].capitalize(),
                "species": parts[1].lower(),
                "subspecies": parts[2].lower() if len(parts) > 2 else None
            }
        return {}

class UnifiedDataIngestionService:
    """Service for ingesting and processing marine data from various sources"""
    
    def __init__(self):
        self.standardizer = DataStandardizer()
        self.logger = logging.getLogger(__name__)
    
    async def ingest_obis_data(self, 
                             scientific_name: Optional[str] = None,
                             geometry: Optional[str] = None,
                             limit: int = 1000) -> Dict[str, Any]:
        """Ingest data from OBIS API"""
        ingestion_id = uuid.uuid4()
        start_time = datetime.utcnow()
        
        try:
            # Log ingestion start
            with next(get_db()) as db:
                log_entry = DataIngestionLog(
                    id=ingestion_id,
                    source_name="OBIS",
                    source_type="api",
                    source_url="https://api.obis.org/v3/",
                    status="in_progress"
                )
                db.add(log_entry)
                db.commit()
            
            # Fetch data from OBIS
            obis_data = await obis_client.search_species(
                scientific_name=scientific_name,
                geometry=geometry,
                limit=limit
            )
            
            if "error" in obis_data:
                return {
                    "status": "error",
                    "message": obis_data["error"],
                    "ingestion_id": str(ingestion_id)
                }
            
            # Process and store data
            processed_count = 0
            failed_count = 0
            errors = []
            
            with next(get_db()) as db:
                for record in obis_data.get("results", []):
                    try:
                        # Standardize the record
                        standardized_record = await self._standardize_obis_record(record)
                        
                        # Store in unified format
                        marine_data = UnifiedMarineData(**standardized_record)
                        db.add(marine_data)
                        processed_count += 1
                        
                    except Exception as e:
                        failed_count += 1
                        errors.append({"record_id": record.get("id"), "error": str(e)})
                        self.logger.error(f"Failed to process OBIS record: {e}")
                
                # Update ingestion log
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                db.query(DataIngestionLog).filter_by(id=ingestion_id).update({
                    DataIngestionLog.records_processed: processed_count + failed_count,
                    DataIngestionLog.records_successful: processed_count,
                    DataIngestionLog.records_failed: failed_count,
                    DataIngestionLog.status: "completed",
                    DataIngestionLog.processing_time_seconds: processing_time,
                    DataIngestionLog.error_log: errors if errors else None
                })
                db.commit()
            
            return {
                "status": "success",
                "ingestion_id": str(ingestion_id),
                "records_processed": processed_count,
                "records_failed": failed_count,
                "processing_time_seconds": processing_time,
                "errors": errors
            }
            
        except Exception as e:
            # Update log with error
            with next(get_db()) as db:
                log_entry = db.query(DataIngestionLog).filter_by(id=ingestion_id).first()
                if log_entry:
                    # Create a new instance with updated values
                    log_entry = DataIngestionLog(
                        id=log_entry.id,
                        source_name=log_entry.source_name,
                        source_type=log_entry.source_type,
                        source_url=log_entry.source_url,
                        status="failed",
                        records_processed=0,
                        records_successful=0,
                        records_failed=1,
                        processing_time_seconds=0,
                        error_log=[{"error": str(e)}],
                        created_at=log_entry.created_at,
                        updated_at=datetime.utcnow()
                    )
                db.commit()
            
            self.logger.error(f"OBIS ingestion failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "ingestion_id": str(ingestion_id)
            }
    
    async def ingest_csv_file(self, 
                            file_path: str,
                            data_type: str,
                            mapping_config: Dict[str, str]) -> Dict[str, Any]:
        """Ingest data from CSV file with column mapping"""
        ingestion_id = uuid.uuid4()
        start_time = datetime.utcnow()
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            processed_count = 0
            failed_count = 0
            errors = []
            
            with next(get_db()) as db:
                # Log ingestion start
                log_entry = DataIngestionLog(
                    id=ingestion_id,
                    source_name=f"CSV: {file_path}",
                    source_type="file",
                    source_url=file_path,
                    status="in_progress"
                )
                db.add(log_entry)
                db.commit()
                
                for index, row in df.iterrows():
                    try:
                        # Map columns to standardized format
                        standardized_record = await self._map_csv_row_to_unified(
                            row, data_type, mapping_config
                        )
                        
                        # Store in unified format
                        marine_data = UnifiedMarineData(**standardized_record)
                        db.add(marine_data)
                        processed_count += 1
                        
                    except Exception as e:
                        failed_count += 1
                        errors.append({"row_index": index, "error": str(e)})
                        self.logger.error(f"Failed to process CSV row {index}: {e}")
                
                # Update ingestion log
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                log_entry = db.query(DataIngestionLog).filter_by(id=ingestion_id).first()
                if log_entry:
                    # Create updated log entry
                    updated_log = DataIngestionLog(
                        id=log_entry.id,
                        source_name=log_entry.source_name,
                        source_type=log_entry.source_type,
                        source_url=log_entry.source_url,
                        status="completed",
                        records_processed=processed_count + failed_count,
                        records_successful=processed_count,
                        records_failed=failed_count,
                        processing_time_seconds=processing_time,
                        error_log=errors if errors else None,
                        created_at=log_entry.created_at,
                        updated_at=datetime.utcnow()
                    )
                    db.merge(updated_log)
                
                db.commit()
            
            return {
                "status": "success",
                "ingestion_id": str(ingestion_id),
                "records_processed": processed_count,
                "records_failed": failed_count,
                "processing_time_seconds": processing_time,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error(f"CSV ingestion failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "ingestion_id": str(ingestion_id)
            }
    
    async def _standardize_obis_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize OBIS record to unified format"""
        # Extract coordinates
        lat, lon = self.standardizer.standardize_coordinates(
            record.get("decimalLatitude"),
            record.get("decimalLongitude")
        )
        
        # Extract datetime
        collection_date = self.standardizer.standardize_datetime(
            record.get("eventDate")
        )
        
        # Extract scientific name
        scientific_name = self.standardizer.standardize_scientific_name(
            record.get("scientificName")
        )
        
        # Extract taxonomy
        taxonomy = self.standardizer.extract_taxonomy_from_name(scientific_name or "")
        
        # Build standardized record
        standardized = {
            "data_type": "biodiversity",
            "data_category": "occurrence",
            "collection_date": collection_date,
            "latitude": lat,
            "longitude": lon,
            "depth": float(record.get("minimumDepthInMeters", 0)) if record.get("minimumDepthInMeters") else None,
            "location_name": record.get("locality"),
            "region": record.get("stateProvince") or record.get("country"),
            "source_dataset": record.get("datasetName"),
            "source_institution": record.get("institutionCode"),
            "scientific_name": scientific_name,
            "kingdom": record.get("kingdom"),
            "phylum": record.get("phylum"),
            "class_name": record.get("class"),
            "order": record.get("order"),
            "family": record.get("family"),
            "genus": taxonomy.get("genus"),
            "species": taxonomy.get("species"),
            "primary_data": {
                "obis_id": record.get("id"),
                "basis_of_record": record.get("basisOfRecord"),
                "occurrence_status": record.get("occurrenceStatus"),
                "individual_count": record.get("individualCount"),
                "sampling_protocol": record.get("samplingProtocol")
            },
            "metadata": {
                "data_source": "OBIS",
                "original_record": record
            },
            "validation_status": "pending",
            "processing_status": "processed"
        }
        
        return standardized
    
    async def _map_csv_row_to_unified(self, 
                                    row: pd.Series,
                                    data_type: str,
                                    mapping_config: Dict[str, str]) -> Dict[str, Any]:
        """Map CSV row to unified format using provided mapping"""
        # Apply column mapping
        mapped_data = {}
        for standard_field, csv_column in mapping_config.items():
            if csv_column in row.index and pd.notna(row[csv_column]).any():
                mapped_data[standard_field] = row[csv_column]
        
        # Standardize common fields
        lat, lon = self.standardizer.standardize_coordinates(
            mapped_data.get("latitude"),
            mapped_data.get("longitude")
        )
        
        collection_date = self.standardizer.standardize_datetime(
            mapped_data.get("collection_date")
        )
        
        scientific_name = self.standardizer.standardize_scientific_name(
            mapped_data.get("scientific_name")
        )
        
        taxonomy = self.standardizer.extract_taxonomy_from_name(scientific_name or "")
        
        # Handle depth conversion safely
        try:
            depth_val = mapped_data.get("depth")
            if depth_val is not None and depth_val != '':
                depth_float = float(depth_val)
            else:
                depth_float = None
        except (ValueError, TypeError):
            depth_float = None
        
        # Build standardized record
        standardized = {
            "data_type": data_type,
            "data_category": mapped_data.get("data_category", "unknown"),
            "collection_date": collection_date,
            "latitude": lat,
            "longitude": lon,
            "depth": depth_float,
            "location_name": mapped_data.get("location_name"),
            "region": mapped_data.get("region"),
            "source_dataset": mapped_data.get("source_dataset"),
            "source_institution": mapped_data.get("source_institution"),
            "scientific_name": scientific_name,
            "genus": taxonomy.get("genus"),
            "species": taxonomy.get("species"),
            "primary_data": {k: v for k, v in mapped_data.items() if k not in [
                "latitude", "longitude", "collection_date", "scientific_name",
                "location_name", "region", "source_dataset", "source_institution"
            ]},
            "metadata": {
                "data_source": "CSV",
                "mapping_config": mapping_config
            },
            "validation_status": "pending",
            "processing_status": "processed"
        }
        
        return standardized
    
    async def validate_data_quality(self, data_id: uuid.UUID) -> Dict[str, Any]:
        """Validate data quality and assign quality scores"""
        try:
            with next(get_db()) as db:
                marine_data = db.query(UnifiedMarineData).filter_by(id=data_id).first()
                
                if not marine_data:
                    return {"error": "Data record not found"}
                
                quality_score = 0.0
                quality_issues = []
                
                # Check coordinate validity
                lat_val = getattr(marine_data, 'latitude', None)
                lon_val = getattr(marine_data, 'longitude', None)
                try:
                    lat_float = float(lat_val) if lat_val is not None else None
                    lon_float = float(lon_val) if lon_val is not None else None
                    if (lat_float is not None and lon_float is not None and
                        -90 <= lat_float <= 90 and -180 <= lon_float <= 180):
                        quality_score += 0.2
                    else:
                        quality_issues.append("Invalid coordinates")
                except (ValueError, TypeError):
                    quality_issues.append("Invalid coordinate format")
                
                # Check temporal data
                date_val = getattr(marine_data, 'collection_date', None)
                try:
                    if (date_val is not None and 
                        date_val <= datetime.utcnow()):
                        quality_score += 0.2
                    else:
                        quality_issues.append("Future collection date")
                except (TypeError):
                    quality_issues.append("Invalid date format")
                
                # Check taxonomic information
                if marine_data.scientific_name is not None:
                    quality_score += 0.2
                    if (marine_data.genus is not None and marine_data.species is not None):
                        quality_score += 0.1
                else:
                    quality_issues.append("Missing scientific name")
                
                # Check data completeness
                if marine_data.primary_data is not None:
                    quality_score += 0.2
                else:
                    quality_issues.append("Missing primary data")
                
                # Check source information
                if (marine_data.source_dataset is not None and marine_data.source_institution is not None):
                    quality_score += 0.1
                else:
                    quality_issues.append("Incomplete source information")
                
                # Update quality score
                db.query(UnifiedMarineData).filter_by(id=marine_data.id).update({
                    UnifiedMarineData.data_quality_score: quality_score
                })
                if quality_score >= 0.8:
                    db.query(UnifiedMarineData).filter_by(id=marine_data.id).update({
                        UnifiedMarineData.validation_status: "validated"
                    })
                elif quality_score >= 0.5:
                    db.query(UnifiedMarineData).filter_by(id=marine_data.id).update({
                        UnifiedMarineData.validation_status: "needs_review"
                    })
                else:
                    db.query(UnifiedMarineData).filter_by(id=marine_data.id).update({
                        UnifiedMarineData.validation_status: "rejected"
                    })
                
                db.commit()
                
                return {
                    "data_id": str(data_id),
                    "quality_score": quality_score,
                    "validation_status": marine_data.validation_status,
                    "quality_issues": quality_issues
                }
                
        except Exception as e:
            self.logger.error(f"Data validation failed: {e}")
            return {"error": str(e)}

# Global service instance
data_ingestion_service = UnifiedDataIngestionService()