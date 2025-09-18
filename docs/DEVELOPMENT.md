# Development Guide

## 🛠️ Development Setup

This guide will help new developers set up the Marine Data Platform development environment and understand the development workflow.

## 📋 Prerequisites

### Required Software
1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

2. **Python** (v3.11 or higher)
   - Download from: https://python.org/
   - Verify: `python --version` and `pip --version`

3. **Git**
   - Download from: https://git-scm.com/
   - Verify: `git --version`

### Required API Keys
1. **Google Gemini API Key**
   - Get from: https://makersuite.google.com/app/apikey
   - Required for AI analysis features

*Note: No backend setup required - the application connects directly to OBIS API*

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-username/marine-data-platform.git
cd marine-data-platform
```

### 2. Install Dependencies and Setup
```bash
# Install frontend dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local with your API key
VITE_GEMINI_API_KEY=your_google_gemini_api_key_here

# Start development server
npm run dev
```

### 3. Verify Setup
1. **Frontend**: Open http://localhost:5173 (or port shown in terminal)
2. **OBIS API**: Test connection via the API Test page
3. **AI Integration**: Verify Gemini API key is working

*No backend setup required - the application works entirely with external APIs*

## 🏗️ Development Workflow

### 1. Project Structure Understanding
```
marine-data-platform/
├── 📁 src/                    # Frontend React app
│   ├── 📁 components/         # Reusable UI components
│   ├── 📁 pages/             # Main application pages
│   ├── 📁 services/          # API integration logic
│   ├── 📁 hooks/             # Custom React hooks
│   └── 📁 lib/               # Utility functions
├── 📁 docs/                  # Documentation files
├── 📄 package.json           # Frontend dependencies
└── 📄 README.md             # Project overview
```

### 2. Development Commands

#### Frontend Commands
```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### 3. Key Development Files

#### Frontend Entry Points
- **src/main.tsx**: Application bootstrap
- **src/App.tsx**: Main component with routing
- **src/pages/**: Individual page components

#### Backend Entry Points
- **backend/app/main.py**: FastAPI application
- **backend/app/api/routes.py**: API router setup
- **backend/app/config.py**: Configuration management

## 🧩 Adding New Features

### 1. Adding a New Page

#### Step 1: Create Page Component
```typescript
// src/pages/NewFeature.tsx
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const NewFeature = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Load initial data
    loadData();
  }, []);

  const loadData = async () => {
    // Implement data loading logic
  };

  return (
    <div className="container mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>New Feature</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Feature content */}
        </CardContent>
      </Card>
    </div>
  );
};

export default NewFeature;
```

#### Step 2: Add Route
```typescript
// src/App.tsx
import NewFeature from './pages/NewFeature';

// Add to router
<Route path="/new-feature" element={<NewFeature />} />
```

#### Step 3: Add Navigation
```typescript
// src/components/layout/Navbar.tsx
const navigationItems = [
  // ... existing items
  { name: 'New Feature', href: '/new-feature', icon: YourIcon }
];
```

### 2. Adding a New API Endpoint

#### Step 1: Create Route Handler
```python
# backend/app/api/v1/new_feature.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint():
    """New API endpoint description"""
    try:
        # Implement endpoint logic
        result = {"message": "Success", "data": {}}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/new-endpoint")
async def create_new_item(item_data: Dict[str, Any]):
    """Create new item"""
    # Implement creation logic
    return {"id": "new_item_id", "status": "created"}
```

#### Step 2: Register Router
```python
# backend/app/api/routes.py
from app.api.v1 import new_feature

# Add to main router
api_router.include_router(
    new_feature.router,
    prefix="/new-feature",
    tags=["new-feature"]
)
```

#### Step 3: Add Frontend Service
```typescript
// src/services/newFeatureApi.ts
import { apiService } from '@/lib/api';

export const newFeatureApi = {
  getData: async () => {
    return apiService.get('/new-feature/new-endpoint');
  },
  
  createItem: async (data: any) => {
    return apiService.post('/new-feature/new-endpoint', data);
  }
};
```

### 3. Adding New OBIS Integration

#### Step 1: Extend OBIS Service
```typescript
// src/services/obisGeminiService.ts
class OBISGeminiService {
  // Add new method
  async fetchNewOBISData(parameters: any): Promise<any> {
    const params = new URLSearchParams(parameters);
    const response = await fetch(`${this.obisBaseUrl}/new-endpoint?${params}`);
    
    if (!response.ok) {
      throw new Error(`OBIS API error: ${response.status}`);
    }
    
    return await response.json();
  }

  // Add AI analysis for new data
  async analyzeNewDataWithAI(data: any): Promise<string> {
    const prompt = `Analyze this new marine data: ${JSON.stringify(data)}`;
    return await geminiApi.generateContent(prompt);
  }
}
```

#### Step 2: Use in Component
```typescript
// In your page component
const [newData, setNewData] = useState(null);
const [analysis, setAnalysis] = useState('');

const handleLoadNewData = async () => {
  try {
    const data = await obisGeminiService.fetchNewOBISData(parameters);
    setNewData(data);
    
    const aiAnalysis = await obisGeminiService.analyzeNewDataWithAI(data);
    setAnalysis(aiAnalysis);
  } catch (error) {
    console.error('Error loading new data:', error);
  }
};
```

## 🧪 Testing

### Frontend Testing
```bash
# Install testing dependencies (if not included)
npm install -D @testing-library/react @testing-library/jest-dom vitest

# Run tests
npm test

# Create test file
# src/pages/__tests__/NewFeature.test.tsx
import { render, screen } from '@testing-library/react';
import NewFeature from '../NewFeature';

test('renders new feature page', () => {
  render(<NewFeature />);
  expect(screen.getByText('New Feature')).toBeInTheDocument();
});
```

### Backend Testing
```python
# backend/tests/test_new_feature.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_new_endpoint():
    response = client.get("/api/v1/new-feature/new-endpoint")
    assert response.status_code == 200
    assert "data" in response.json()

def test_create_new_item():
    test_data = {"name": "test item"}
    response = client.post("/api/v1/new-feature/new-endpoint", json=test_data)
    assert response.status_code == 200
    assert "id" in response.json()
```

## 🎨 UI/UX Development

### Using ShadCN Components
```typescript
// Import components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';

// Use in component
<Card>
  <CardContent className="space-y-4">
    <Input placeholder="Enter species name" />
    <Button onClick={handleSearch}>Search</Button>
  </CardContent>
</Card>
```

### Custom Styling
```typescript
// Use Tailwind classes
<div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
  <h2 className="text-lg font-semibold text-blue-900">Marine Data</h2>
</div>

// Custom CSS (if needed)
// src/index.css
.custom-marine-theme {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

## 🔧 Debugging

### Frontend Debugging
```typescript
// Use React Developer Tools browser extension
// Add debugging code
console.log('Component state:', { data, loading, error });

// Debug API calls
console.log('API Request:', url, parameters);
console.log('API Response:', response);

// Use browser network tab to monitor API calls
```

### Backend Debugging
```python
# Add logging
import logging
logger = logging.getLogger(__name__)

@router.get("/debug-endpoint")
async def debug_endpoint():
    logger.info("Debug endpoint called")
    logger.debug(f"Request parameters: {request.query_params}")
    
    # Use debugger
    import pdb; pdb.set_trace()  # Python debugger
    
    return {"debug": "info"}
```

### Common Issues and Solutions

#### 1. CORS Errors
```python
# Backend: Update CORS settings
cors_origins = ["http://localhost:3000", "http://localhost:5173"]
```

#### 2. Environment Variables Not Loading
```bash
# Check .env file exists and has correct format
# Restart development server after changes
```

#### 3. API Connection Issues
```typescript
// Check API URL configuration
console.log('API Base URL:', import.meta.env.VITE_API_URL);

// Test backend health endpoint
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log);
```

## 📚 Learning Resources

### Frontend Technologies
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/
- **Vite**: https://vitejs.dev/
- **TailwindCSS**: https://tailwindcss.com/
- **ShadCN/UI**: https://ui.shadcn.com/

### Backend Technologies
- **FastAPI**: https://fastapi.tiangolo.com/
- **Python**: https://docs.python.org/3/
- **Pydantic**: https://docs.pydantic.dev/

### Marine Data APIs
- **OBIS API**: https://api.obis.org/
- **GBIF API**: https://www.gbif.org/developer/summary

### AI Integration
- **Google Gemini**: https://ai.google.dev/

## 🤝 Contributing

### Code Style
- **Frontend**: ESLint + Prettier configuration
- **Backend**: Black + Flake8 for Python formatting
- **Commits**: Use conventional commit messages

### Pull Request Process
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test thoroughly
3. Run linting: `npm run lint` and `black backend/app/`
4. Submit pull request with description
5. Wait for code review and approval

This development guide provides everything a new developer needs to start contributing to the Marine Data Platform effectively.