# API Integration Documentation

## 🌊 External API Integrations

The Marine Data Platform integrates directly with external APIs to provide comprehensive marine biodiversity data and AI-powered analysis without requiring a backend server.

## 🔗 OBIS API Integration

### Overview
OBIS (Ocean Biodiversity Information System) is the primary data source for marine biodiversity information.

**Base URL**: `https://api.obis.org/v3`
**Documentation**: https://api.obis.org/

### Key Endpoints Used

#### 1. Dataset Endpoint
**URL**: `/dataset`
**Purpose**: Retrieve marine dataset metadata
**Usage in App**:
```typescript
// Frontend: directObisApi.ts
async getDatasets(limit: number = 20, offset: number = 0) {
  const response = await fetch(`https://api.obis.org/v3/dataset?limit=${limit}&offset=${offset}`);
  return await response.json();
}
```

**Response Structure**:
```json
{
  "results": [
    {
      "id": "dataset_id",
      "title": "Dataset Title",
      "description": "Dataset description",
      "records": 25000,
      "extent": {
        "spatial": "Geographic bounds",
        "temporal": "Time range"
      }
    }
  ],
  "total": 1500,
  "limit": 20,
  "offset": 0
}
```

#### 2. Occurrence Endpoint
**URL**: `/occurrence`
**Purpose**: Retrieve actual species occurrence records
**Usage in App**:
```typescript
// directObisApi.ts - Direct API integration
async getSpeciesOccurrence(scientificName: string, limit: number = 50) {
  const params = new URLSearchParams({
    scientificname: scientificName,
    limit: limit.toString()
  });
  
  const response = await fetch(`https://api.obis.org/v3/occurrence?${params}`);
  return await response.json();
}

// Get dataset-specific occurrences
async getDatasetOccurrences(datasetId: string, limit: number = 50) {
  const params = new URLSearchParams({
    datasetid: datasetId,
    limit: limit.toString()
  });
  
  const response = await fetch(`https://api.obis.org/v3/occurrence?${params}`);
  return await response.json();
}
```

**Response Structure**:
```json
{
  "results": [
    {
      "scientificName": "Gadus morhua",
      "kingdom": "Animalia",
      "phylum": "Chordata",
      "class": "Actinopterygii",
      "order": "Gadiformes",
      "family": "Gadidae",
      "genus": "Gadus",
      "species": "morhua",
      "decimalLatitude": 59.123,
      "decimalLongitude": 10.456,
      "depth": 45.5,
      "eventDate": "2023-06-15",
      "locality": "North Sea",
      "country": "Norway",
      "individualCount": 12,
      "basisOfRecord": "HumanObservation",
      "datasetName": "North Sea Fish Survey",
      "institutionCode": "IMR"
    }
  ],
  "total": 25000,
  "limit": 50,
  "offset": 0
}
```

#### 3. Statistics Endpoint
**URL**: `/statistics`
**Purpose**: Get OBIS database statistics
**Usage**: Dashboard overview and system metrics

#### 4. Taxon Endpoint
**URL**: `/taxon`
**Purpose**: Retrieve taxonomic information
**Usage**: Species classification and taxonomy validation

### OBIS API Parameters

#### Common Parameters
- `limit` - Number of results to return (max 5000)
- `offset` - Pagination offset
- `geometry` - WKT geometry for geographic filtering
- `scientificname` - Species scientific name
- `startdate` / `enddate` - Temporal filtering
- `datasetid` - Filter by specific dataset

#### Geographic Filtering
```typescript
// Example: Filter by bounding box
const geometry = "POLYGON((10 50, 20 50, 20 60, 10 60, 10 50))";
const params = new URLSearchParams({ geometry });
```

## 🤖 Google Gemini AI Integration

### Overview
Google Gemini provides AI-powered analysis of marine data for insights and recommendations.

**Service**: Google Generative AI
**Model**: gemini-2.0-flash-exp

### Integration Architecture

#### Frontend Integration
```typescript
// services/geminiApi.ts
class GeminiApiService {
  private apiKey: string;
  private model: GenerativeModel;

  async generateContent(prompt: string): Promise<string> {
    const result = await this.model.generateContent(prompt);
    return result.response.text();
  }
}
```

### AI Analysis Workflow

#### 1. Dataset Analysis (FIXED IMPLEMENTATION)
**Previous Issue**: AI received only metadata
**Fix Applied**: AI now receives actual occurrence records

```typescript
// BEFORE (only metadata)
const analysis = await this.analyzeDatasetDataWithAI(datasetMetadata);

// AFTER (metadata + real occurrence data)
const datasetMetadata = await this.fetchOBISDataset(datasetId);
const occurrenceData = await this.fetchDatasetOccurrences(datasetId, 50);
const analysis = await this.analyzeDatasetWithOccurrences(datasetMetadata, occurrenceData);
```

#### 2. AI Prompt Structure
```typescript
const prompt = `Analyze this OBIS dataset with actual occurrence data:

**Dataset Metadata:**
Title: ${dataset.title}
Total Records: ${dataset.records}
Description: ${dataset.description}

**Actual Occurrence Data Sample (${occurrences.results.length} records):**
${JSON.stringify(occurrences.results.slice(0, 10), null, 2)}

**Analysis Instructions:**
1. Species Diversity Analysis
2. Geographic Distribution Patterns  
3. Temporal Patterns
4. Data Quality Assessment
5. Ecological Insights
6. Conservation Implications
7. Research Applications

Provide scientifically rigorous insights based on the ACTUAL DATA.`;
```

#### 3. Response Processing
```typescript
// Markdown rendering for AI responses
<Markdown content={analysisResults?.ai_analysis || 'No analysis available'} />
```

## 🔄 Data Flow Integration

### 1. Complete Dataset Analysis Flow (FIXED)
```
User selects dataset →
Frontend: Analytics.tsx →
obisGeminiService.analyzeDatasetWithAI() →
  ├── fetchOBISDataset(id) → OBIS /dataset/{id} → metadata
  ├── fetchDatasetOccurrences(id) → OBIS /occurrence?datasetid={id} → real data
  └── analyzeDatasetWithOccurrences() → Gemini AI → analysis
Frontend: Markdown rendering → User sees results
```

### 2. Species Search Flow
```
User enters species name →
Frontend: AIIntegration.tsx →
obisGeminiService.searchSpeciesWithAI() →
  ├── fetchOBISSpecies() → OBIS /occurrence?scientificname={name}
  └── analyzeSpeciesDataWithAI() → Gemini AI → insights
Frontend: Display results
```

### 3. Visualization Data Flow
```
User selects filters →
Frontend: Visualizations.tsx →
obisDataService.getSpeciesOccurrenceData() →
OBIS /occurrence API →
Chart components update →
Interactive display
```

## 🔧 Error Handling and Resilience

### OBIS API Error Handling
```typescript
try {
  const response = await fetch(obisUrl);
  if (!response.ok) {
    throw new Error(`OBIS API error: ${response.status} ${response.statusText}`);
  }
  return await response.json();
} catch (error) {
  console.error('OBIS API error:', error);
  // Fallback to demo data or cached results
  return this.getFallbackData();
}
```

### Gemini AI Error Handling
```typescript
try {
  const result = await this.model.generateContent(prompt);
  return result.response.text();
} catch (error) {
  console.error('Gemini AI error:', error);
  return "Analysis temporarily unavailable. Please try again later.";
}
```

### Rate Limiting and Throttling
```typescript
// Implement request throttling for OBIS API
class RateLimiter {
  private requests: number[] = [];
  private maxRequests = 10;
  private windowMs = 60000; // 1 minute

  async throttle(): Promise<void> {
    const now = Date.now();
    this.requests = this.requests.filter(time => now - time < this.windowMs);
    
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = Math.min(...this.requests);
      const waitTime = this.windowMs - (now - oldestRequest);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    this.requests.push(now);
  }
}
```

## 📊 API Performance Optimization

### 1. Caching Strategy
```typescript
// Cache OBIS responses to reduce API calls
class CacheService {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private cacheTimeout = 5 * 60 * 1000; // 5 minutes

  get(key: string): any | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }
    return null;
  }

  set(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }
}
```

### 2. Batch Processing
```typescript
// Batch multiple dataset analyses
async batchAnalyzeDatasets(datasetIds: string[]): Promise<AnalysisResult[]> {
  const batchSize = 3; // Process 3 at a time
  const results: AnalysisResult[] = [];
  
  for (let i = 0; i < datasetIds.length; i += batchSize) {
    const batch = datasetIds.slice(i, i + batchSize);
    const batchPromises = batch.map(id => this.analyzeDatasetWithAI(id));
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
  }
  
  return results;
}
```

### 3. Progressive Loading
```typescript
// Load data progressively for better UX
async loadDatasetWithProgress(datasetId: string, onProgress: (progress: number) => void) {
  onProgress(20); // Starting
  
  const metadata = await this.fetchOBISDataset(datasetId);
  onProgress(40); // Metadata loaded
  
  const occurrences = await this.fetchDatasetOccurrences(datasetId);
  onProgress(70); // Data loaded
  
  const analysis = await this.analyzeDatasetWithOccurrences(metadata, occurrences);
  onProgress(100); // Complete
  
  return { metadata, occurrences, analysis };
}
```

## 🔐 API Security and Authentication

### Environment Variables
```typescript
// Frontend
const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const API_BASE_URL = import.meta.env.VITE_API_URL;

// Backend
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OBIS_API_KEY = os.getenv("OBIS_API_KEY")  # If required in future
```

### API Key Management
```python
# Backend: Secure API key handling
from functools import lru_cache

@lru_cache()
def get_gemini_client():
    api_key = settings.gemini_api_key
    if not api_key:
        raise ValueError("Gemini API key not configured")
    return GeminiClient(api_key)
```

## 📈 Monitoring and Analytics

### API Usage Tracking
```typescript
class APIMonitor {
  trackRequest(api: string, endpoint: string, duration: number, success: boolean) {
    console.log(`API: ${api}, Endpoint: ${endpoint}, Duration: ${duration}ms, Success: ${success}`);
    // Send to monitoring service
  }
}
```

### Health Checks
```python
# Backend: API health monitoring
@router.get("/health/apis")
async def check_api_health():
    health_status = {
        "obis": await check_obis_health(),
        "gemini": await check_gemini_health(),
        "timestamp": datetime.utcnow().isoformat()
    }
    return health_status
```

This API integration documentation provides comprehensive coverage of how the Marine Data Platform connects with external services to deliver real-time marine biodiversity data and AI-powered insights.