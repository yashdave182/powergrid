# CMLRE Marine Data Platform - Backend

## AI-Driven Unified Data Platform for Oceanographic, Fisheries, and Molecular Biodiversity Insights

### Overview


The CMLRE Marine Data Platform is a comprehensive, AI-enabled backend system designed for the Centre for Marine Living Resources and Ecology (CMLRE), Kochi. This platform integrates heterogeneous marine data from multiple domains into a single unified storage system, enabling cross-disciplinary analysis and real-time insights.

### Key Features

#### 🌊 **Unified Data Architecture**
- **Single Storage System**: No hot/cold storage separation - all data unified in one platform
- **Multi-Domain Integration**: Oceanographic, fisheries, taxonomic, and molecular data
- **Real-time Processing**: Automated data ingestion and validation
- **Cross-Disciplinary Correlations**: Advanced analytics across all data types

#### 📊 **Comprehensive Data Management**

1. **Oceanographic Data**
   - Physical parameters (temperature, salinity, pressure, density)
   - Chemical parameters (pH, dissolved oxygen, nutrients, carbon data)
   - Biological parameters (chlorophyll-a, primary productivity)
   - Current and wave data with instrument metadata

2. **Fisheries Data**
   - Species abundance and biomass measurements
   - Life history traits (length, weight, age, maturity)
   - Ecomorphology and meristic data
   - Catch per unit effort (CPUE) and fishing method data

3. **Taxonomic Data**
   - Complete taxonomic hierarchy classification
   - Morphological descriptions and key characteristics
   - **Otolith Morphology**: Specialized fish otolith shape analysis
   - Specimen management with museum catalog integration

4. **Molecular Biology & eDNA**
   - Environmental DNA (eDNA) sample processing
   - DNA sequencing and genetic marker analysis
   - Species detection and biodiversity indices
   - Bioinformatics pipeline integration

#### 🤖 **AI-Powered Analytics**
- **Species Identification**: Automated classification using morphological and molecular data
- **Ecosystem Health Assessment**: Integrated analysis across all data types
- **Conservation Recommendations**: AI-generated conservation strategies
- **Biodiversity Pattern Recognition**: Advanced pattern analysis and trend detection
- **Data Quality Validation**: Automated quality scoring and validation

### Quick Setup

#### Prerequisites
- Python 3.8+
- PostgreSQL (production) or SQLite (development)

#### Installation

1. **Automated setup**:
```bash
cd backend
python setup_platform.py
```

2. **Manual setup**:
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Create database
python -c "from app.core.database import engine; from app.models.marine_data import Base; Base.metadata.create_all(bind=engine)"

# Start server
uvicorn app.main:app --reload
```

3. **Access the platform**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Base: http://localhost:8000/api/v1/

### API Endpoints

#### Core Data Management
- **Oceanographic**: `/api/v1/oceanography/*`
  - Data creation, search, analysis
  - Water quality assessment
  - Temperature trend analysis

- **Fisheries**: `/api/v1/fisheries/*`
  - Species abundance tracking
  - Biodiversity metrics
  - Fish size distribution analysis

- **Taxonomy**: `/api/v1/taxonomy/*`
  - Species morphology management
  - Otolith shape analysis
  - Species identification system

- **Molecular**: `/api/v1/molecular/*`
  - eDNA sample processing
  - Species detection algorithms
  - Biodiversity assessment

#### Advanced Analytics
- **Analytics**: `/api/v1/analytics/*`
  - Ecosystem health assessment
  - Temporal trend analysis
  - Spatial pattern recognition

- **Data Integration**: `/api/v1/data-integration/*`
  - Cross-domain correlations
  - Unified data views
  - Data fusion algorithms

- **AI Services**: `/api/v1/ai/*`
  - Automated analysis
  - Conservation recommendations
  - Pattern recognition

### Environment Configuration

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/marine_db

# AI Services
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key

# External APIs
OBIS_API_URL=https://api.obis.org/v3/
GBIF_API_URL=https://api.gbif.org/v1/

# Security
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development
DEBUG=True
```

### Deployment

Ready for cloud deployment with included Docker configuration:

```bash
# Build and run with Docker
docker build -t marine-platform .
docker run -p 8000:8000 marine-platform
```

### Key Differentiators

#### 🎯 **Problem Statement Alignment**
- **Unified Architecture**: Single storage system eliminating data silos
- **Multi-disciplinary Integration**: Seamless correlation across all marine data types
- **Real-time Analytics**: Instant insights from integrated datasets
- **AI-Enhanced**: Automated analysis and pattern recognition
- **Scalable Design**: Cloud-ready architecture for national deployment

#### 🔬 **Scientific Features**
- **Otolith Morphometry**: Specialized fish identification through otolith analysis
- **eDNA Processing**: Advanced environmental DNA analysis workflows
- **Cross-Domain Correlations**: Ocean conditions vs biodiversity patterns
- **Quality Assurance**: Automated data validation and quality scoring
- **Conservation Focus**: AI-generated conservation recommendations

### Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **Health Monitoring**: http://localhost:8000/health
- **Platform Report**: Generated automatically in `platform_report.json`

### Support

For technical support and questions about the CMLRE Marine Data Platform, please refer to the comprehensive API documentation or contact the development team.