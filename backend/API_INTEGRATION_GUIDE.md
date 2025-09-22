# 🌊 CMLRE Marine Data Platform - API Integration Guide

## 📋 Quick Reference for Real-World API Integration

This guide provides ready-to-use endpoints and integration patterns for the CMLRE Marine Data Platform, specifically designed for Indian Ocean marine data collection and analysis.

---

## 🟦 **Oceanographic Data Sources**

### 1. **INCOIS (Indian National Centre for Ocean Information Services)**
```python
# Example Integration
from app.services.indian_ocean_apis import INCOISClient

client = INCOISClient()
data = await client.get_oceanographic_data(
    dataset_id="OSF_Temperature",
    latitude_min=15.0, latitude_max=25.0,
    longitude_min=65.0, longitude_max=75.0,
    start_date="2023-01-01"
)
```

**Direct ERDDAP Endpoint:**
```bash
curl "https://incois.gov.in/erddap/tabledap/OSF_Temperature.json?latitude,longitude,temperature,time&latitude>=15.0&latitude<=25.0&longitude>=65.0&longitude<=75.0&time>=2023-01-01"
```

### 2. **ARGO Global Ocean Observing System**
```python
# Example Integration
from app.services.indian_ocean_apis import ArgoFloatsClient

client = ArgoFloatsClient()
data = await client.get_argo_profiles(
    latitude_min=-10.0, latitude_max=30.0,
    longitude_min=60.0, longitude_max=100.0,
    start_date="2023-01-01",
    limit=1000
)
```

**Direct ERDDAP Endpoint:**
```bash
curl "https://erddap.ifremer.fr/erddap/tabledap/ArgoFloats.json?platform_number,latitude,longitude,temp,psal&latitude>=-10&latitude<=30&longitude>=60&longitude<=100&time>=2023-01-01"
```

---

## 🟦 **Fisheries & Species Data**

### 3. **FishBase API**
```python
# Example Integration
from app.services.indian_ocean_apis import FishBaseAPIClient

client = FishBaseAPIClient()
data = await client.get_species_data("Rastrelliger", "kanagurta")
```

**Direct API Endpoint:**
```bash
curl "https://fishbaseapi.azurewebsites.net/species/Genus=Rastrelliger&Species=kanagurta"
```

### 4. **WoRMS (World Register of Marine Species)**
```python
# Example Integration
from app.services.indian_ocean_apis import WoRMSClient

client = WoRMSClient()
data = await client.get_complete_species_info("Rastrelliger kanagurta")
```

**Direct API Endpoints:**
```bash
# Get AphiaID
curl "http://www.marinespecies.org/rest/AphiaIDByName/Rastrelliger%20kanagurta"

# Get Classification
curl "http://www.marinespecies.org/rest/AphiaClassificationByAphiaID/126436"
```

---

## 🟦 **Molecular Biology Data**

### 5. **NCBI E-utilities**
```python
# Example Integration
from app.services.indian_ocean_apis import NCBIClient

client = NCBIClient()
data = await client.search_sequences(
    organism="Rastrelliger kanagurta",
    gene="COI",
    max_results=100
)
```

**Direct API Endpoints:**
```bash
# Search sequences
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nucleotide&term=Rastrelliger+kanagurta[Organism]+COI[Gene]&retmax=10&retmode=json"

# Fetch sequences (replace IDs with actual results)
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nucleotide&id=123456,789012&rettype=fasta&retmode=text"
```

### 6. **BOLD Systems (Barcode of Life)**
```python
# Example Integration
from app.services.indian_ocean_apis import BOLDClient

client = BOLDClient()
taxon_data = await client.search_taxon("Rastrelliger kanagurta")
specimens = await client.get_specimen_records("Rastrelliger kanagurta")
```

**Direct API Endpoints:**
```bash
# Taxon search
curl "http://v3.boldsystems.org/index.php/API_Public/TaxonSearch?taxName=Rastrelliger%20kanagurta"

# Specimen records
curl "http://v3.boldsystems.org/index.php/API_Public/Specimen?taxon=Rastrelliger%20kanagurta"
```

---

## 🚀 **Quick Start Integration**

### Run Complete Demo Pipeline
```bash
cd backend/
python run_api_demos.py
```

### Test Individual APIs
```bash
# Simple API connectivity tests
python simple_integration_demo.py

# Full integration pipeline
python sample_integration_pipeline.py
```

### Use Integrated Services
```python
# Import the unified integration function
from app.services.indian_ocean_apis import fetch_integrated_marine_data

# Fetch data from all sources for a species
data = await fetch_integrated_marine_data(
    species_name="Rastrelliger kanagurta",
    region="indian_ocean",
    data_types=["oceanographic", "fisheries", "taxonomic", "molecular"]
)
```

---

## 📊 **Data Processing Pipeline**

### 1. **Raw Data Ingestion**
- Automated API polling from INCOIS, ARGO, FishBase, WoRMS, NCBI, BOLD
- Real-time data validation and quality scoring
- Standardized format conversion (JSON, FASTA, NetCDF → Unified schema)

### 2. **Unified Storage**
```python
# All data stored in unified schema
UnifiedMarineData:
    - data_type: "oceanographic" | "fisheries" | "taxonomic" | "molecular"
    - source: "INCOIS" | "ARGO" | "FishBase" | "WoRMS" | "NCBI" | "BOLD"
    - spatial_temporal coordinates
    - quality_score: 0.0-1.0
    - standardized metadata
```

### 3. **Cross-Disciplinary Analysis**
- Spatial-temporal correlation between oceanographic and fisheries data
- Species distribution mapping with environmental parameters
- Molecular phylogeny integration with morphological data
- AI-powered ecosystem health assessment

---

## 🗄️ **Database Integration**

### Unified Schema Design
```sql
-- Core unified table
unified_marine_data (
    id, data_type, source, collection_date,
    latitude, longitude, depth, region,
    scientific_name, quality_score, metadata_json
)

-- Specialized tables
oceanographic_data (temperature, salinity, pressure, ...)
fisheries_data (species_count, biomass, catch_data, ...)
taxonomic_data (classification, authority, confidence, ...)
molecular_data (sequence_data, gene_name, accession, ...)
```

### Query Examples
```python
# Get all data for a species
session.query(UnifiedMarineData)\
    .filter_by(scientific_name="Rastrelliger kanagurta")\
    .all()

# Get oceanographic data in region
session.query(UnifiedMarineData, OceanographicData)\
    .join(OceanographicData)\
    .filter(UnifiedMarineData.latitude.between(10, 20))\
    .filter(UnifiedMarineData.longitude.between(70, 80))\
    .all()
```

---

## 🌐 **API Status & Availability**

| Data Source | Status | Response Format | Rate Limit | Authentication |
|-------------|--------|-----------------|------------|----------------|
| INCOIS ERDDAP | ✅ Active | JSON/CSV/NetCDF | Reasonable | None |
| ARGO IFREMER | ✅ Active | JSON/CSV/NetCDF | Reasonable | None |
| FishBase API | ✅ Active | JSON | Moderate | None |
| WoRMS REST | ✅ Active | JSON/XML | Good | None |
| NCBI E-utils | ✅ Active | JSON/XML/FASTA | 3 req/sec | None |
| BOLD Systems | ✅ Active | JSON/CSV/FASTA | Moderate | None |

---

## 🔧 **Integration Best Practices**

### 1. **Error Handling**
```python
try:
    data = await client.get_data()
    if data.get('status') == 'success':
        # Process successful response
        process_data(data['data'])
    else:
        # Handle API-level errors
        logger.error(f"API error: {data.get('error')}")
except Exception as e:
    # Handle connection/network errors
    logger.error(f"Connection error: {e}")
```

### 2. **Rate Limiting**
```python
import asyncio
from datetime import datetime, timedelta

# Implement delays between requests
await asyncio.sleep(0.5)  # 0.5 second delay

# Batch processing with rate limits
async def batch_process(items, delay=1.0):
    for item in items:
        result = await process_item(item)
        await asyncio.sleep(delay)
```

### 3. **Data Validation**
```python
from app.services.data_standardizer import DataStandardizer

standardizer = DataStandardizer()

# Validate coordinates
lat, lon = standardizer.standardize_coordinates(
    raw_data.get('latitude'), 
    raw_data.get('longitude')
)

# Validate datetime
date = standardizer.standardize_datetime(raw_data.get('timestamp'))

# Calculate quality score
quality = standardizer.calculate_quality_score(raw_data)
```

---

## 🎯 **Common Use Cases**

### 1. **Regional Oceanographic Analysis**
```python
# Get all oceanographic data for Arabian Sea
incois_data = await incois_client.get_oceanographic_data(
    latitude_min=15.0, latitude_max=25.0,
    longitude_min=65.0, longitude_max=75.0
)

argo_data = await argo_client.get_argo_profiles(
    latitude_min=15.0, latitude_max=25.0,
    longitude_min=65.0, longitude_max=75.0
)
```

### 2. **Species-Centric Research**
```python
species = "Rastrelliger kanagurta"

# Get all data types for a species
fisheries = await fishbase_client.get_species_data(*species.split())
taxonomy = await worms_client.get_complete_species_info(species)
sequences = await ncbi_client.search_sequences(species, "COI")
barcodes = await bold_client.search_taxon(species)
```

### 3. **Ecosystem Health Assessment**
```python
# Combine environmental and biological data
from app.services.ai_service import AIService

ai_service = AIService()
health_report = await ai_service.analyze_ecosystem_health(
    region="Arabian Sea",
    time_period="2023-01-01:2024-01-01",
    data_types=["oceanographic", "fisheries", "molecular"]
)
```

---

## 📞 **Support & Resources**

- **Backend Documentation**: `README.md`
- **API Client Code**: `app/services/indian_ocean_apis.py`
- **Integration Pipeline**: `app/services/indian_ocean_integration.py`
- **Database Models**: `app/models/marine_data.py`
- **Demo Scripts**: `sample_integration_pipeline.py`, `run_api_demos.py`

---

## ✅ **Ready for Production**

The CMLRE Marine Data Platform backend is now equipped with:

1. ✅ **Complete API Integration** - All major Indian Ocean data sources connected
2. ✅ **Unified Storage Architecture** - Single schema for all marine data types
3. ✅ **Real-time Processing** - Automated data ingestion and validation
4. ✅ **Cross-disciplinary Analysis** - Spatial-temporal correlation capabilities
5. ✅ **AI-Powered Insights** - Machine learning integration for ecosystem analysis
6. ✅ **Scalable Design** - Cloud-ready, containerized deployment
7. ✅ **Quality Assurance** - Comprehensive validation and error handling

**Next Step**: Frontend integration to provide interactive visualization and user interface for the unified marine data platform.