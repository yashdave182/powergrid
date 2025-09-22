from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid

from app.core.database import Base

class UnifiedMarineData(Base):
    """
    Unified storage model for all marine data types - oceanographic, fisheries, taxonomic, and molecular
    This replaces the hot/cold storage approach with a single unified storage system
    """
    __tablename__ = "unified_marine_data"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_type = Column(String(50), nullable=False, index=True)  # oceanographic, fisheries, taxonomic, molecular
    data_category = Column(String(100), nullable=False, index=True)  # physical, chemical, biological, species, etc.
    
    # Temporal information
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    collection_date = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Spatial information
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    depth = Column(Float)
    location_name = Column(String(255))
    region = Column(String(100), index=True)
    
    # Data source and quality
    source_dataset = Column(String(255), index=True)
    source_institution = Column(String(255))
    data_quality_score = Column(Float)
    validation_status = Column(String(50), default="pending")
    
    # Core data storage
    primary_data = Column(JSON)  # Main structured data
    metadata = Column(JSON)  # Additional metadata
    raw_data = Column(Text)  # Raw/unprocessed data
    
    # Scientific identification (for biological data)
    scientific_name = Column(String(255), index=True)
    taxon_id = Column(String(100), index=True)
    kingdom = Column(String(100))
    phylum = Column(String(100))
    class_name = Column(String(100))
    order = Column(String(100))
    family = Column(String(100))
    genus = Column(String(100))
    species = Column(String(100))
    
    # Measurement data
    measurement_type = Column(String(100))
    measurement_value = Column(Float)
    measurement_unit = Column(String(50))
    measurement_method = Column(String(255))
    
    # Research context
    project_id = Column(String(100), index=True)
    researcher_id = Column(String(100))
    expedition_id = Column(String(100))
    
    # Status and workflow
    processing_status = Column(String(50), default="raw")
    is_validated = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    
    # Tags and classification
    tags = Column(ARRAY(String), default=[])
    keywords = Column(ARRAY(String), default=[])
    
    # Create indexes for better performance
    __table_args__ = (
        Index('idx_marine_data_type_category', 'data_type', 'data_category'),
        Index('idx_marine_data_location', 'latitude', 'longitude'),
        Index('idx_marine_data_time', 'timestamp', 'collection_date'),
        Index('idx_marine_data_taxonomy', 'kingdom', 'phylum', 'class_name'),
        Index('idx_marine_data_search', 'scientific_name', 'region', 'data_type'),
    )

class OceanographicData(Base):
    """Specialized model for oceanographic measurements"""
    __tablename__ = "oceanographic_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unified_data_id = Column(UUID(as_uuid=True), ForeignKey('unified_marine_data.id'), nullable=False)
    
    # Physical parameters
    temperature = Column(Float)
    salinity = Column(Float)
    pressure = Column(Float)
    density = Column(Float)
    
    # Chemical parameters
    ph = Column(Float)
    dissolved_oxygen = Column(Float)
    nutrients = Column(JSON)  # NO3, PO4, SiO4, etc.
    carbon_data = Column(JSON)  # CO2, alkalinity, etc.
    
    # Biological parameters
    chlorophyll_a = Column(Float)
    primary_productivity = Column(Float)
    biomass_data = Column(JSON)
    
    # Current and wave data
    current_speed = Column(Float)
    current_direction = Column(Float)
    wave_height = Column(Float)
    wave_period = Column(Float)
    
    # Equipment and methods
    instrument_type = Column(String(255))
    sensor_data = Column(JSON)
    calibration_data = Column(JSON)
    
    # Relationship
    unified_data = relationship("UnifiedMarineData", back_populates="oceanographic_details")

class FisheriesData(Base):
    """Specialized model for fisheries and fish ecology data"""
    __tablename__ = "fisheries_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unified_data_id = Column(UUID(as_uuid=True), ForeignKey('unified_marine_data.id'), nullable=False)
    
    # Species abundance
    abundance_count = Column(Integer)
    abundance_density = Column(Float)
    biomass = Column(Float)
    cpue = Column(Float)  # Catch per unit effort
    
    # Life history traits
    length = Column(Float)
    weight = Column(Float)
    age = Column(Integer)
    maturity_stage = Column(String(50))
    sex = Column(String(10))
    
    # Ecomorphology data
    morphometric_data = Column(JSON)  # Body measurements
    meristic_data = Column(JSON)  # Countable features
    ecological_traits = Column(JSON)
    
    # Fishing/collection data
    fishing_method = Column(String(255))
    gear_type = Column(String(100))
    effort_data = Column(JSON)
    
    # Environmental conditions during collection
    water_conditions = Column(JSON)
    habitat_type = Column(String(100))
    
    # Relationship
    unified_data = relationship("UnifiedMarineData", back_populates="fisheries_details")

class TaxonomicData(Base):
    """Specialized model for taxonomic classification and morphology"""
    __tablename__ = "taxonomic_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unified_data_id = Column(UUID(as_uuid=True), ForeignKey('unified_marine_data.id'), nullable=False)
    
    # Taxonomic hierarchy (detailed)
    taxonomic_authority = Column(String(255))
    taxonomic_status = Column(String(50))
    vernacular_names = Column(JSON)
    
    # Morphological data
    morphology_description = Column(Text)
    key_characteristics = Column(JSON)
    diagnostic_features = Column(JSON)
    
    # Otolith morphology (specific to fish)
    otolith_data = Column(JSON)
    otolith_shape_analysis = Column(JSON)
    otolith_measurements = Column(JSON)
    
    # Images and media
    specimen_images = Column(JSON)  # URLs to images
    microscopy_data = Column(JSON)
    
    # Specimen data
    specimen_id = Column(String(255))
    collection_method = Column(String(255))
    preservation_method = Column(String(100))
    museum_catalog = Column(String(255))
    
    # Identification confidence
    identification_confidence = Column(Float)
    identification_method = Column(String(255))
    identified_by = Column(String(255))
    identification_date = Column(DateTime)
    
    # Relationship
    unified_data = relationship("UnifiedMarineData", back_populates="taxonomic_details")

class MolecularData(Base):
    """Specialized model for molecular biology and eDNA data"""
    __tablename__ = "molecular_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unified_data_id = Column(UUID(as_uuid=True), ForeignKey('unified_marine_data.id'), nullable=False)
    
    # eDNA specific data
    sample_type = Column(String(100))  # water, sediment, tissue
    dna_extraction_method = Column(String(255))
    amplification_data = Column(JSON)  # PCR details
    
    # Sequencing data
    sequencing_platform = Column(String(100))
    sequence_data = Column(Text)  # Raw sequences
    sequence_quality = Column(JSON)
    
    # Genetic markers
    marker_gene = Column(String(100))  # 16S, 18S, COI, etc.
    marker_region = Column(String(100))
    primer_data = Column(JSON)
    
    # Bioinformatics analysis
    blast_results = Column(JSON)
    taxonomic_assignment = Column(JSON)
    phylogenetic_data = Column(JSON)
    
    # Quantitative data
    dna_concentration = Column(Float)
    read_count = Column(Integer)
    otu_data = Column(JSON)  # Operational Taxonomic Units
    
    # Environmental DNA detection
    detection_probability = Column(Float)
    species_detection = Column(JSON)
    biodiversity_indices = Column(JSON)
    
    # Laboratory data
    lab_protocol = Column(String(255))
    processing_date = Column(DateTime)
    lab_technician = Column(String(255))
    
    # Relationship
    unified_data = relationship("UnifiedMarineData", back_populates="molecular_details")

class DataIngestionLog(Base):
    """Log for tracking data ingestion and processing"""
    __tablename__ = "data_ingestion_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Source information
    source_name = Column(String(255), nullable=False)
    source_type = Column(String(100))  # api, file, manual
    source_url = Column(String(500))
    
    # Processing information
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Status and errors
    status = Column(String(50), default="in_progress")  # in_progress, completed, failed
    error_log = Column(JSON)
    processing_time_seconds = Column(Float)
    
    # Data quality metrics
    quality_metrics = Column(JSON)
    validation_results = Column(JSON)

class ResearchProject(Base):
    """Model for organizing data by research projects"""
    __tablename__ = "research_projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_code = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Project metadata
    principal_investigator = Column(String(255))
    institution = Column(String(255))
    funding_agency = Column(String(255))
    
    # Temporal scope
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Spatial scope
    study_area = Column(JSON)  # Geographic boundaries
    target_species = Column(ARRAY(String))
    
    # Project status
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Add relationships to UnifiedMarineData
UnifiedMarineData.oceanographic_details = relationship("OceanographicData", back_populates="unified_data", cascade="all, delete-orphan")
UnifiedMarineData.fisheries_details = relationship("FisheriesData", back_populates="unified_data", cascade="all, delete-orphan")
UnifiedMarineData.taxonomic_details = relationship("TaxonomicData", back_populates="unified_data", cascade="all, delete-orphan")
UnifiedMarineData.molecular_details = relationship("MolecularData", back_populates="unified_data", cascade="all, delete-orphan")