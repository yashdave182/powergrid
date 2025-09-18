# Backend Architecture Documentation

## 🎯 Backend Overview

The backend is a FastAPI-based Python application that provides RESTful APIs for marine data integration, AI analysis, and data processing. It serves as the bridge between the frontend, external marine data APIs (OBIS), and AI services (Google Gemini).

## 📂 Backend Directory Structure

```
backend/
├── app/                    # Main application package
│   ├── api/               # API route definitions
│   │   ├── v1/           # API version 1 endpoints
│   │   │   ├── __init__.py
│   │   │   ├── ai.py         # AI analysis endpoints
│   │   │   ├── analytics.py  # Analytics and insights endpoints
│   │   │   ├── biodiversity.py # Marine biodiversity endpoints
│   │   │   ├── data_integration.py # Data processing endpoints
│   │   │   └── oceanography.py # Oceanographic data endpoints
│   │   ├── __init__.py
│   │   └── routes.py         # Main API router
│   ├── core/              # Core application configuration
│   │   ├── __init__.py
│   │   └── database.py       # Database configuration
│   ├── services/          # Business logic and external integrations
│   │   ├── __init__.py
│   │   ├── ai_service.py     # AI service integration
│   │   ├── external_apis.py  # External API clients
│   │   └── llm_service.py    # LLM integration service
│   ├── __init__.py
│   ├── config.py         # Application configuration
│   └── main.py          # FastAPI application entry point
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
├── render.yaml         # Render deployment configuration
├── setup.bat           # Windows setup script
└── test_ai.py         # AI service testing
```

## 🔄 Backend Workflow Architecture

### 1. Request Flow
```
Client Request → FastAPI Router → Route Handler → Service Layer → External API → Response
```

### 2. Application Startup
```
main.py → FastAPI App → CORS Middleware → API Router → Route Registration
```

## 📄 Core Files Deep Dive

### main.py
**Purpose**: FastAPI application entry point and configuration

**Key Components**:
```python
# FastAPI app instance
app = FastAPI(title="Marine Data Platform API", version="1.0.0")

# CORS configuration for frontend access
app.add_middleware(CORSMiddleware, ...)

# API router inclusion
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check()
```

**Workflow**:
1. Creates FastAPI application instance
2. Configures CORS for frontend communication
3. Sets up middleware for request processing
4. Includes all API routes with `/api/v1` prefix
5. Provides health check endpoint for monitoring

**CORS Configuration**:
- **Development**: Allows all origins (`*`)
- **Production**: Configured for specific Vercel domains

### config.py
**Purpose**: Application configuration and environment variables

**Key Settings**:
```python
class Settings:
    debug: bool = True
    gemini_api_key: str
    allowed_origins: List[str]
    database_url: str = "sqlite:///./marine_data.db"
```

**Environment Variables**:
- `DEBUG` - Development/production mode
- `GEMINI_API_KEY` - Google Gemini AI key
- `ALLOWED_ORIGINS` - Frontend URLs for CORS
- `DATABASE_URL` - Database connection string

## 🛣️ API Routes Deep Dive

### api/routes.py
**Purpose**: Main API router that combines all endpoint modules

**Structure**:
```python
api_router = APIRouter()

# Health check for API
@api_router.get("/health")

# Include all module routers
api_router.include_router(biodiversity.router, prefix="/biodiversity")
api_router.include_router(oceanography.router, prefix="/oceanography")
api_router.include_router(analytics.router, prefix="/analytics")
api_router.include_router(ai.router, prefix="/ai")
api_router.include_router(data_integration.router, prefix="/data-integration")
```

### api/v1/biodiversity.py
**Purpose**: Marine biodiversity data endpoints

**Key Endpoints**:

#### `/biodiversity/species/search`
**Method**: GET
**Purpose**: Search species across OBIS and GBIF databases
**Parameters**:
- `scientific_name` - Species scientific name
- `region` - Geographic region
- `data_source` - OBIS or GBIF
- `limit` - Result limit

**Workflow**:
1. Validates input parameters
2. Calls OBIS API for species data
3. Processes and formats results
4. Returns standardized species information

#### `/biodiversity/datasets`
**Method**: GET
**Purpose**: Retrieve available marine datasets
**Parameters**:
- `limit` - Number of datasets to return

**Workflow**:
1. Fetches datasets from OBIS API
2. Enriches with metadata
3. Returns paginated results

#### `/biodiversity/species/{id}/details`
**Method**: GET
**Purpose**: Get detailed species information
**Parameters**:
- `id` - Species identifier
- `source` - Data source (OBIS/GBIF)

#### `/biodiversity/test/obis`
**Method**: GET
**Purpose**: Test OBIS API connectivity
**Returns**: Connection status and response times

### api/v1/ai.py
**Purpose**: AI analysis and machine learning endpoints

**Key Endpoints**:

#### `/ai/analyze-marine-data`
**Method**: POST
**Purpose**: Analyze marine data using Google Gemini AI
**Request Body**:
```python
class AnalysisRequest(BaseModel):
    data: Dict[str, Any]  # Marine data to analyze
```

**Workflow**:
1. Receives marine data payload
2. Calls `ai_service.analyze_marine_data()`
3. Returns AI-generated insights

#### `/ai/conservation-recommendations`
**Method**: POST
**Purpose**: Generate conservation recommendations
**Request Body**:
```python
class ConservationRequest(BaseModel):
    species_data: List[Dict[str, Any]]
```

#### `/ai/biodiversity-analysis`
**Method**: POST
**Purpose**: Analyze biodiversity patterns
**Request Body**:
```python
class BiodiversityRequest(BaseModel):
    occurrence_data: Dict[str, Any]
```

### api/v1/analytics.py
**Purpose**: Data analytics and ecosystem health endpoints

**Key Endpoints**:

#### `/analytics/ecosystem/health`
**Method**: POST
**Purpose**: Analyze ecosystem health metrics
**Workflow**:
1. Receives ecosystem data
2. Calculates health metrics
3. Generates AI assessment
4. Returns comprehensive health report

#### `/analytics/predictive/species-distribution`
**Method**: POST
**Purpose**: Predict species distribution based on environmental factors
**Parameters**:
- `species_name` - Target species
- `environmental_factors` - Environmental data
- `prediction_timeframe` - Time period for prediction

### api/v1/oceanography.py
**Purpose**: Oceanographic data endpoints

**Key Endpoints**:
- `/oceanography/temperature/profiles` - Temperature data
- `/oceanography/salinity/measurements` - Salinity data
- `/oceanography/chemistry/nutrients` - Nutrient data
- `/oceanography/currents/analysis` - Ocean current analysis

### api/v1/data_integration.py
**Purpose**: Data processing and integration endpoints

**Key Endpoints**:

#### `/data-integration/integrate/multi-source`
**Method**: POST
**Purpose**: Integrate data from multiple sources

#### `/data-integration/standardize/biodiversity`
**Method**: POST
**Purpose**: Standardize biodiversity data to Darwin Core format

#### `/data-integration/pipeline/status`
**Method**: GET
**Purpose**: Get data processing pipeline status

## 🔧 Service Layer Deep Dive

### services/ai_service.py
**Purpose**: AI service integration and processing

**Key Methods**:

#### `analyze_marine_data(data: Dict[str, Any]) -> str`
**Purpose**: Core AI analysis function
**Workflow**:
1. Preprocesses marine data
2. Constructs AI prompt for analysis
3. Calls Google Gemini API
4. Processes AI response
5. Returns formatted analysis

**Integration**: Used by frontend `obisGeminiService.ts`

### services/external_apis.py
**Purpose**: External API client integrations

**Key Clients**:

#### `OBISClient`
**Purpose**: OBIS API integration
**Methods**:
- `search_species()` - Species search
- `get_datasets()` - Dataset retrieval
- `get_occurrences()` - Occurrence data
- `get_taxonomy()` - Taxonomic information

**API Endpoints**:
- Base URL: `https://api.obis.org/v3`
- `/occurrence` - Species occurrence records
- `/dataset` - Dataset metadata
- `/taxon` - Taxonomic data

#### `GBIFClient`
**Purpose**: GBIF API integration (if needed)

### services/llm_service.py
**Purpose**: Large Language Model service abstraction

**Key Methods**:
- `analyze_marine_data()` - Generic LLM analysis
- `generate_insights()` - Insight generation
- `process_biodiversity_data()` - Biodiversity analysis

## 🗄️ Database Integration

### core/database.py
**Purpose**: Database configuration and ORM setup

**Components**:
```python
# SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
```

**Usage**: Currently optional, mainly for caching and user data

## 🔐 Security and Configuration

### Environment Variables
**Required for Production**:
```
DEBUG=false
GEMINI_API_KEY=your_gemini_api_key
ALLOWED_ORIGINS=https://your-frontend.vercel.app
DATABASE_URL=postgresql://user:pass@host:port/db
```

### CORS Configuration
**Development**:
```python
cors_origins = ["*"]
cors_allow_credentials = False
```

**Production**:
```python
cors_origins = ["https://your-frontend.vercel.app"]
cors_allow_credentials = True
```

## 🐛 Error Handling

### Exception Handlers
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### Logging Configuration
- Structured logging for debugging
- Request/response logging
- Error tracking and monitoring

## 🚀 Deployment Configuration

### Dockerfile
**Purpose**: Container configuration for deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### render.yaml
**Purpose**: Render deployment configuration
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🔄 Data Flow Examples

### 1. Species Analysis Flow
```
Frontend Request → 
/ai/analyze-marine-data → 
ai_service.analyze_marine_data() → 
Google Gemini API → 
Formatted Response → 
Frontend Display
```

### 2. Dataset Retrieval Flow
```
Frontend Request → 
/biodiversity/datasets → 
OBISClient.get_datasets() → 
OBIS API → 
Processed Results → 
Frontend Display
```

### 3. Health Check Flow
```
Frontend Request → 
/health → 
Simple Status Response → 
Frontend Status Update
```

## 🧪 Testing

### test_ai.py
**Purpose**: AI service testing and validation
**Features**:
- API connectivity tests
- Response validation
- Performance testing

## 📊 Monitoring and Observability

### Health Endpoints
- `/health` - Basic health check
- `/api/v1/health` - API health check

### Logging
- Request/response logging
- Error tracking
- Performance monitoring

This backend architecture provides a robust, scalable foundation for marine data processing with comprehensive API coverage and AI integration capabilities.