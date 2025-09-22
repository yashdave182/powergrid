from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

class DataType(str, Enum):
    OCEANOGRAPHIC = "oceanographic"
    FISHERIES = "fisheries"
    TAXONOMIC = "taxonomic"
    MOLECULAR = "molecular"

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"

class ProcessingStatus(str, Enum):
    RAW = "raw"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"

# Base schemas
class BaseMarineDataCreate(BaseModel):
    """Base schema for creating marine data records"""
    data_type: DataType
    data_category: str
    collection_date: Optional[datetime] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    depth: Optional[float] = None
    location_name: Optional[str] = None
    region: Optional[str] = None
    source_dataset: Optional[str] = None
    source_institution: Optional[str] = None
    primary_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_data: Optional[str] = None
    project_id: Optional[str] = None
    researcher_id: Optional[str] = None
    tags: Optional[List[str]] = []
    keywords: Optional[List[str]] = []

class BaseMarineDataResponse(BaseModel):
    """Base schema for marine data responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    data_type: str
    data_category: str
    timestamp: datetime
    collection_date: Optional[datetime]
    latitude: Optional[float]
    longitude: Optional[float]
    depth: Optional[float]
    location_name: Optional[str]
    region: Optional[str]
    source_dataset: Optional[str]
    source_institution: Optional[str]
    data_quality_score: Optional[float]
    validation_status: str
    primary_data: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    scientific_name: Optional[str]
    processing_status: str
    is_validated: bool
    is_published: bool
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

# Oceanographic Data Schemas
class OceanographicDataCreate(BaseModel):
    """Schema for creating oceanographic data"""
    # Physical parameters
    temperature: Optional[float] = None
    salinity: Optional[float] = None
    pressure: Optional[float] = None
    density: Optional[float] = None
    
    # Chemical parameters
    ph: Optional[float] = Field(None, ge=0, le=14)
    dissolved_oxygen: Optional[float] = None
    nutrients: Optional[Dict[str, float]] = None
    carbon_data: Optional[Dict[str, float]] = None
    
    # Biological parameters
    chlorophyll_a: Optional[float] = None
    primary_productivity: Optional[float] = None
    biomass_data: Optional[Dict[str, float]] = None
    
    # Current and wave data
    current_speed: Optional[float] = None
    current_direction: Optional[float] = Field(None, ge=0, le=360)
    wave_height: Optional[float] = None
    wave_period: Optional[float] = None
    
    # Equipment data
    instrument_type: Optional[str] = None
    sensor_data: Optional[Dict[str, Any]] = None
    calibration_data: Optional[Dict[str, Any]] = None

class OceanographicDataResponse(BaseModel):
    """Schema for oceanographic data responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    temperature: Optional[float]
    salinity: Optional[float]
    pressure: Optional[float]
    density: Optional[float]
    ph: Optional[float]
    dissolved_oxygen: Optional[float]
    nutrients: Optional[Dict[str, float]]
    carbon_data: Optional[Dict[str, float]]
    chlorophyll_a: Optional[float]
    primary_productivity: Optional[float]
    current_speed: Optional[float]
    current_direction: Optional[float]
    wave_height: Optional[float]
    wave_period: Optional[float]
    instrument_type: Optional[str]

# Fisheries Data Schemas
class FisheriesDataCreate(BaseModel):
    """Schema for creating fisheries data"""
    # Species abundance
    abundance_count: Optional[int] = None
    abundance_density: Optional[float] = None
    biomass: Optional[float] = None
    cpue: Optional[float] = None
    
    # Life history traits
    length: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    maturity_stage: Optional[str] = None
    sex: Optional[str] = None
    
    # Morphometric data
    morphometric_data: Optional[Dict[str, float]] = None
    meristic_data: Optional[Dict[str, int]] = None
    ecological_traits: Optional[Dict[str, Any]] = None
    
    # Collection data
    fishing_method: Optional[str] = None
    gear_type: Optional[str] = None
    effort_data: Optional[Dict[str, Any]] = None
    water_conditions: Optional[Dict[str, Any]] = None
    habitat_type: Optional[str] = None

class FisheriesDataResponse(BaseModel):
    """Schema for fisheries data responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    abundance_count: Optional[int]
    abundance_density: Optional[float]
    biomass: Optional[float]
    cpue: Optional[float]
    length: Optional[float]
    weight: Optional[float]
    age: Optional[int]
    maturity_stage: Optional[str]
    sex: Optional[str]
    morphometric_data: Optional[Dict[str, float]]
    fishing_method: Optional[str]
    gear_type: Optional[str]
    habitat_type: Optional[str]

# Taxonomic Data Schemas
class TaxonomicDataCreate(BaseModel):
    """Schema for creating taxonomic data"""
    # Taxonomic information
    taxonomic_authority: Optional[str] = None
    taxonomic_status: Optional[str] = None
    vernacular_names: Optional[Dict[str, str]] = None
    
    # Morphological data
    morphology_description: Optional[str] = None
    key_characteristics: Optional[Dict[str, Any]] = None
    diagnostic_features: Optional[Dict[str, Any]] = None
    
    # Otolith data (fish specific)
    otolith_data: Optional[Dict[str, Any]] = None
    otolith_shape_analysis: Optional[Dict[str, Any]] = None
    otolith_measurements: Optional[Dict[str, float]] = None
    
    # Specimen data
    specimen_id: Optional[str] = None
    collection_method: Optional[str] = None
    preservation_method: Optional[str] = None
    museum_catalog: Optional[str] = None
    
    # Identification
    identification_confidence: Optional[float] = Field(None, ge=0, le=1)
    identification_method: Optional[str] = None
    identified_by: Optional[str] = None
    specimen_images: Optional[List[str]] = None

class TaxonomicDataResponse(BaseModel):
    """Schema for taxonomic data responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    taxonomic_authority: Optional[str]
    taxonomic_status: Optional[str]
    vernacular_names: Optional[Dict[str, str]]
    morphology_description: Optional[str]
    key_characteristics: Optional[Dict[str, Any]]
    otolith_data: Optional[Dict[str, Any]]
    specimen_id: Optional[str]
    identification_confidence: Optional[float]
    identification_method: Optional[str]
    identified_by: Optional[str]

# Molecular Data Schemas
class MolecularDataCreate(BaseModel):
    """Schema for creating molecular biology data"""
    # Sample data
    sample_type: Optional[str] = None
    dna_extraction_method: Optional[str] = None
    amplification_data: Optional[Dict[str, Any]] = None
    
    # Sequencing
    sequencing_platform: Optional[str] = None
    sequence_data: Optional[str] = None
    sequence_quality: Optional[Dict[str, Any]] = None
    
    # Genetic markers
    marker_gene: Optional[str] = None
    marker_region: Optional[str] = None
    primer_data: Optional[Dict[str, str]] = None
    
    # Analysis results
    blast_results: Optional[Dict[str, Any]] = None
    taxonomic_assignment: Optional[Dict[str, Any]] = None
    phylogenetic_data: Optional[Dict[str, Any]] = None
    
    # Quantitative data
    dna_concentration: Optional[float] = None
    read_count: Optional[int] = None
    otu_data: Optional[Dict[str, Any]] = None
    
    # eDNA specific
    detection_probability: Optional[float] = Field(None, ge=0, le=1)
    species_detection: Optional[Dict[str, Any]] = None
    biodiversity_indices: Optional[Dict[str, float]] = None
    
    # Lab info
    lab_protocol: Optional[str] = None
    lab_technician: Optional[str] = None

class MolecularDataResponse(BaseModel):
    """Schema for molecular data responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    sample_type: Optional[str]
    dna_extraction_method: Optional[str]
    sequencing_platform: Optional[str]
    marker_gene: Optional[str]
    marker_region: Optional[str]
    taxonomic_assignment: Optional[Dict[str, Any]]
    dna_concentration: Optional[float]
    read_count: Optional[int]
    detection_probability: Optional[float]
    species_detection: Optional[Dict[str, Any]]
    biodiversity_indices: Optional[Dict[str, float]]
    lab_protocol: Optional[str]

# Combined schemas for unified data
class UnifiedMarineDataCreate(BaseModel):
    """Schema for creating unified marine data with specialized details"""
    base_data: BaseMarineDataCreate
    oceanographic_data: Optional[OceanographicDataCreate] = None
    fisheries_data: Optional[FisheriesDataCreate] = None
    taxonomic_data: Optional[TaxonomicDataCreate] = None
    molecular_data: Optional[MolecularDataCreate] = None

class UnifiedMarineDataResponse(BaseModel):
    """Schema for unified marine data responses"""
    model_config = ConfigDict(from_attributes=True)
    
    base_data: BaseMarineDataResponse
    oceanographic_data: Optional[OceanographicDataResponse] = None
    fisheries_data: Optional[FisheriesDataResponse] = None
    taxonomic_data: Optional[TaxonomicDataResponse] = None
    molecular_data: Optional[MolecularDataResponse] = None

# Search and filter schemas
class MarineDataSearchFilters(BaseModel):
    """Schema for searching and filtering marine data"""
    data_type: Optional[DataType] = None
    data_category: Optional[str] = None
    scientific_name: Optional[str] = None
    region: Optional[str] = None
    latitude_min: Optional[float] = Field(None, ge=-90, le=90)
    latitude_max: Optional[float] = Field(None, ge=-90, le=90)
    longitude_min: Optional[float] = Field(None, ge=-180, le=180)
    longitude_max: Optional[float] = Field(None, ge=-180, le=180)
    depth_min: Optional[float] = None
    depth_max: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    source_dataset: Optional[str] = None
    project_id: Optional[str] = None
    validation_status: Optional[ValidationStatus] = None
    is_validated: Optional[bool] = None
    tags: Optional[List[str]] = None
    limit: Optional[int] = Field(100, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)

class MarineDataSearchResponse(BaseModel):
    """Schema for search results"""
    total_count: int
    results: List[BaseMarineDataResponse]
    filters_applied: MarineDataSearchFilters
    search_metadata: Optional[Dict[str, Any]] = None

# Analytics schemas
class BiodiversityMetrics(BaseModel):
    """Schema for biodiversity analysis results"""
    species_richness: int
    shannon_diversity: Optional[float] = None
    simpson_diversity: Optional[float] = None
    evenness: Optional[float] = None
    total_abundance: Optional[int] = None
    endemic_species_count: Optional[int] = None
    threatened_species_count: Optional[int] = None

class EcosystemHealthMetrics(BaseModel):
    """Schema for ecosystem health indicators"""
    water_quality_index: Optional[float] = None
    biodiversity_index: Optional[float] = None
    habitat_quality_score: Optional[float] = None
    pollution_indicators: Optional[Dict[str, float]] = None
    climate_impact_score: Optional[float] = None

# Research project schemas
class ResearchProjectCreate(BaseModel):
    """Schema for creating research projects"""
    project_code: str
    title: str
    description: Optional[str] = None
    principal_investigator: Optional[str] = None
    institution: Optional[str] = None
    funding_agency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    study_area: Optional[Dict[str, Any]] = None
    target_species: Optional[List[str]] = None

class ResearchProjectResponse(BaseModel):
    """Schema for research project responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_code: str
    title: str
    description: Optional[str]
    principal_investigator: Optional[str]
    institution: Optional[str]
    funding_agency: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    study_area: Optional[Dict[str, Any]]
    target_species: Optional[List[str]]
    status: str
    created_at: datetime
    updated_at: datetime