# Frontend Architecture Documentation

## 🎯 Frontend Overview

The frontend is a React TypeScript application built with Vite, providing a modern, responsive interface for marine data visualization and AI-powered analysis. The application connects directly to external APIs without requiring a backend server.

## 📂 Frontend Directory Structure

```
src/
├── components/          # Reusable UI components
│   ├── layout/         # Layout components (Navbar, etc.)
│   └── ui/            # ShadCN UI components
├── pages/             # Route components (main application pages)
├── services/          # API integration and business logic
├── hooks/            # Custom React hooks
├── lib/              # Utility functions and configurations
├── App.tsx           # Main application component
├── main.tsx          # Application entry point
└── index.css         # Global styles
```

## 🔄 Application Workflow

### 1. Application Initialization
```
main.tsx → App.tsx → Router Setup → Page Components
```

**main.tsx**: Entry point that renders the App component
**App.tsx**: Sets up React Router and global providers
**Router**: Defines all application routes and navigation

### 2. Data Flow Architecture
```
User Interaction → Page Component → Service Layer → External APIs → State Update → UI Refresh
```

## 📄 Page Components Deep Dive

### Dashboard.tsx
**Purpose**: Main landing page with system overview and quick stats
**Key Features**:
- OBIS API connection monitoring
- Quick navigation to other sections
- Real-time status indicators
- Marine data statistics

**Data Sources**:
- `directObisService.testConnection()` - OBIS API health check
- `directObisService.getStatistics()` - Marine data statistics
- Demo data fallback for offline mode

**Code Flow**:
1. Component mounts → useEffect triggers
2. Calls `directObisService.testConnection()` to verify OBIS API
3. Updates state with system status
4. Renders cards with navigation links

### Datasets.tsx
**Purpose**: Browse and explore marine datasets from OBIS
**Key Features**:
- Real OBIS dataset browsing
- Search and filtering
- Loading progress indicators
- Dataset details and metadata

**Data Sources**:
- `directObisService.getDatasets()` - Direct OBIS dataset API
- `obisGeminiService.fetchOBISDatasets()` - Enhanced dataset fetching

**Code Flow**:
1. Component mounts → loads initial datasets
2. Shows progress indicator during fetch
3. Implements search filtering on title/description
4. Renders dataset cards with metadata

### Analytics.tsx
**Purpose**: AI-powered analysis of marine datasets
**Key Features**:
- Dataset selection and analysis
- Real-time AI insights generation
- Progress tracking for analysis
- Detailed analysis results with markdown rendering

**Data Sources**:
- `obisGeminiService.analyzeDatasetWithAI()`
- Real OBIS occurrence records
- Google Gemini AI analysis

**Code Flow**:
1. User selects dataset → `handleAnalyzeDataset()`
2. Fetches dataset metadata AND occurrence records
3. Sends combined data to Gemini AI
4. Renders analysis with proper markdown formatting

### Visualizations.tsx
**Purpose**: Interactive charts and data visualizations
**Key Features**:
- Species occurrence charts
- Geographic distribution maps
- Biodiversity metrics
- Interactive filtering

**Data Sources**:
- `directObisService.getSpeciesOccurrence()` - Direct species data
- `directObisService.getTaxon()` - Taxonomic information
- Real-time OBIS data

**Code Flow**:
1. Loads default visualization data
2. User interactions trigger data refetch
3. Charts update with new data
4. Responsive design adapts to screen size

### AIIntegration.tsx
**Purpose**: Direct AI interaction and species analysis
**Key Features**:
- Species search and AI analysis
- Real-time insights generation
- Species identification
- Conservation recommendations

**Data Sources**:
- `obisGeminiService.searchSpeciesWithAI()`
- `obisGeminiService.quickSpeciesLookup()`

### ApiTest.tsx
**Purpose**: Development tool for testing OBIS API connections
**Key Features**:
- OBIS API health checks
- Species search testing
- Response debugging
- Connection diagnostics

**Data Sources**:
- `directObisService.testConnection()` - OBIS API health
- `directObisService.getSpeciesOccurrence()` - Species search testing

### Tools.tsx
**Purpose**: Additional utilities and tools
**Key Features**:
- Data export tools
- Batch processing
- Utility functions

## 🔧 Service Layer Architecture

### directObisApi.ts
**Purpose**: Direct integration with OBIS API v3

**Key Methods**:

#### `getDatasets(limit, offset)`
- Fetches paginated list of OBIS datasets directly
- Returns metadata: title, description, record counts
- Used by Datasets page for browsing

#### `getSpeciesOccurrence(scientificName, limit)`
- Searches for species in OBIS database directly
- Returns occurrence records with coordinates and dates
- Used for species analysis

#### `getDatasetOccurrences(datasetId, limit)`
- Fetches actual species occurrence records from specific dataset
- Returns real species data instead of just metadata
- Enables meaningful AI analysis

#### `getStatistics()`
- Fetches OBIS database statistics
- Used for dashboard overview

#### `testConnection()`
- Tests OBIS API connectivity
- Returns connection status and response time

### obisGeminiService.ts
**Purpose**: Core integration between OBIS API and Google Gemini AI

**Key Methods**:

#### `analyzeDatasetWithAI(datasetId)`
**This is the CORE method for AI analysis**
- Fetches dataset metadata via `directObisService`
- Fetches actual occurrence records via `directObisService`
- Combines both for comprehensive AI analysis
- Returns detailed insights with real species data

#### `searchSpeciesWithAI(scientificName, geometry, limit)`
- Searches for species in OBIS database
- Analyzes results with AI
- Returns enhanced analysis with insights

### geminiApi.ts
**Purpose**: Google Gemini AI integration service

**Key Method**: `generateContent(prompt)`
- Handles AI requests to Google Gemini
- Processes marine data for analysis
- Returns formatted insights and recommendations

## 🎨 UI Components Architecture

### Layout Components

#### Navbar.tsx
**Purpose**: Main navigation component
**Features**:
- Responsive navigation menu
- Route highlighting
- Mobile menu support

### UI Components (ShadCN)
**Purpose**: Consistent, accessible UI components

**Key Components**:
- `Button` - Interactive buttons with variants
- `Card` - Content containers
- `Progress` - Loading and progress indicators
- `Tabs` - Tabbed interfaces
- `Dialog` - Modal dialogs
- `Badge` - Status indicators
- `Table` - Data tables
- `Chart` - Recharts integration
- `Markdown` - Markdown content rendering (crucial for AI responses)

### Custom Components

#### Markdown.tsx
**Purpose**: Renders AI-generated markdown content
**Key Features**:
- GitHub Flavored Markdown support
- Custom styling for marine data
- Handles empty content gracefully
- **Critical for AI response formatting**

## 🔧 Utility Libraries

### lib/api.ts
**Purpose**: Core API service configuration

**Key Features**:
- Environment-based URL configuration
- Request/response handling
- Error management
- Debug logging

**Configuration**:
```typescript
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1')
```

### lib/utils.ts
**Purpose**: Utility functions and helpers
- Class name merging for TailwindCSS
- Common utility functions

## 🎯 Key Data Flows

### 1. Dataset Analysis Flow (FIXED)
```
User clicks "Analyze" → 
Analytics.tsx → 
obisGeminiService.analyzeDatasetWithAI() → 
Fetches metadata + occurrence records → 
Sends to Gemini AI → 
Returns detailed analysis → 
Renders with Markdown component
```

### 2. Species Search Flow
```
User enters species name → 
AIIntegration.tsx → 
obisGeminiService.searchSpeciesWithAI() → 
OBIS API search → 
AI analysis → 
Results display
```

### 3. Visualization Flow
```
User selects filters → 
Visualizations.tsx → 
obisDataService APIs → 
Chart components update → 
Interactive display
```

## 🔐 Environment Configuration

### Required Environment Variables
```
VITE_API_URL=https://your-backend.onrender.com/api/v1
VITE_GEMINI_API_KEY=your_google_gemini_api_key
```

### Development vs Production
- **Development**: Uses localhost backend
- **Production**: Uses environment variables for Vercel deployment

## 🚀 Build and Deployment

### Build Process
```
npm run build → 
Vite builds optimized bundle → 
Outputs to dist/ directory → 
Ready for deployment
```

### Deployment Targets
- **Primary**: Vercel (recommended)
- **Alternative**: Netlify, AWS S3, any static host

This frontend architecture provides a robust, scalable foundation for marine data analysis with real-time API integration and AI-powered insights.