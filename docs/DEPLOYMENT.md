# Deployment and DevOps Documentation

## 🚀 Deployment Architecture

The Marine Data Platform uses a modern cloud deployment architecture with separate frontend and backend hosting for optimal performance and scalability.

```
Production Architecture:
├── Frontend (Vercel)
│   ├── React TypeScript App
│   ├── Static Asset CDN
│   └── Edge Functions
├── Backend (Render)
│   ├── FastAPI Python App
│   ├── Docker Container
│   └── Auto-scaling
└── External APIs
    ├── OBIS API (obis.org)
    └── Google Gemini AI
```

## 🌐 Frontend Deployment (Vercel)

### Why Vercel?
- **Optimized for React**: Built specifically for React applications
- **Edge Network**: Global CDN for fast loading
- **Automatic Deployments**: Git-based CI/CD
- **Environment Variables**: Secure config management
- **Zero Configuration**: Works out of the box with Vite

### Deployment Configuration

#### vercel.json
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "env": {
    "VITE_API_URL": "@api_url",
    "VITE_GEMINI_API_KEY": "@gemini_api_key"
  },
  "build": {
    "env": {
      "VITE_API_URL": "@api_url",
      "VITE_GEMINI_API_KEY": "@gemini_api_key"
    }
  }
}
```

#### Build Process
```bash
# Vercel automatically runs:
npm install          # Install dependencies
npm run build        # Vite build process
# Deploy to global CDN
```

#### Environment Variables (Vercel Dashboard)
```
VITE_API_URL=https://your-backend.onrender.com/api/v1
VITE_GEMINI_API_KEY=your_google_gemini_api_key_here
```

### Deployment Steps
1. **Connect Repository**: Link GitHub repo to Vercel
2. **Configure Project**: 
   - Framework: Vite
   - Root Directory: `.` (project root)
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. **Set Environment Variables**: Add API URLs and keys
4. **Deploy**: Automatic deployment on git push

### Custom Domain Setup
```bash
# Vercel CLI
vercel domains add your-domain.com
vercel domains add www.your-domain.com
```

## 🖥️ Backend Deployment (Render)

### Why Render?
- **Easy Python Deployment**: Native Python support
- **Docker Support**: Containerized deployments
- **Auto-scaling**: Automatic resource scaling
- **Free Tier**: Good for development and testing
- **Environment Variables**: Secure configuration
- **Health Checks**: Built-in monitoring

### Deployment Configuration

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Start command
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT:-8000}/health || exit 1
```

#### render.yaml
```yaml
services:
  - type: web
    name: marine-data-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DEBUG
        value: false
      - key: GEMINI_API_KEY
        sync: false  # Sensitive, set manually
      - key: ALLOWED_ORIGINS
        value: https://your-frontend.vercel.app
```

#### Environment Variables (Render Dashboard)
```
DEBUG=false
GEMINI_API_KEY=your_google_gemini_api_key
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://marine-data-platform.vercel.app
DATABASE_URL=postgresql://user:pass@host:port/db  # If using database
```

### Deployment Steps
1. **Create Render Account**: Sign up at render.com
2. **Connect Repository**: Link GitHub repository
3. **Create Web Service**:
   - Repository: Your GitHub repo
   - Branch: `main` or `production`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Configure Environment**: Set environment variables
5. **Deploy**: Automatic deployment on git push

## 🔄 CI/CD Pipeline

### Git Workflow
```
Development Branch → Pull Request → Main Branch → Auto Deploy
```

### Automatic Deployments
**Frontend (Vercel)**:
- Triggers on push to `main` branch
- Runs build process automatically
- Deploys to production URL
- Preview deployments for PRs

**Backend (Render)**:
- Triggers on push to `main` branch
- Builds Docker container
- Deploys to production URL
- Zero-downtime deployments

### Environment-Based Deployments
```
main branch     → Production (live site)
develop branch  → Staging (testing)
feature/*       → Preview (PR previews)
```

## 🔧 Configuration Management

### Environment Variables Strategy

#### Development (.env.local)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_GEMINI_API_KEY=your_dev_gemini_key
```

#### Production (Vercel + Render)
```env
# Frontend (Vercel)
VITE_API_URL=https://marine-backend.onrender.com/api/v1
VITE_GEMINI_API_KEY=your_prod_gemini_key

# Backend (Render)
DEBUG=false
GEMINI_API_KEY=your_prod_gemini_key
ALLOWED_ORIGINS=https://marine-platform.vercel.app
```

### Configuration Validation
```python
# Backend: config.py
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    debug: bool = True
    gemini_api_key: str
    allowed_origins: List[str] = []
    
    @validator('gemini_api_key')
    def gemini_key_required(cls, v):
        if not v:
            raise ValueError('GEMINI_API_KEY is required')
        return v
    
    class Config:
        env_file = ".env"
```

## 📊 Monitoring and Observability

### Health Checks

#### Frontend Health
```typescript
// Automatic health monitoring
const healthCheck = {
  frontend: "OK",
  backend: await fetch('/api/v1/health'),
  apis: {
    obis: await testOBISConnection(),
    gemini: await testGeminiConnection()
  }
};
```

#### Backend Health
```python
# app/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.debug
    }

@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "services": {
            "database": await check_database(),
            "obis_api": await check_obis_api(),
            "gemini_api": await check_gemini_api()
        }
    }
```

### Logging and Monitoring

#### Frontend Monitoring
```typescript
// Error tracking and analytics
class MonitoringService {
  trackError(error: Error, context: string) {
    console.error(`Frontend Error [${context}]:`, error);
    // Send to monitoring service (e.g., Sentry, LogRocket)
  }
  
  trackPerformance(metric: string, value: number) {
    console.log(`Performance [${metric}]: ${value}ms`);
    // Send to analytics service
  }
}
```

#### Backend Monitoring
```python
# Structured logging
import logging
import structlog

logger = structlog.get_logger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        "request_completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration=duration
    )
    return response
```

### Performance Monitoring

#### Key Metrics to Track
1. **Frontend**:
   - Page load times
   - API response times
   - Error rates
   - User interactions

2. **Backend**:
   - Request/response times
   - Error rates
   - Resource usage
   - External API latency

3. **External APIs**:
   - OBIS API response times
   - Gemini AI response times
   - Rate limiting status

## 🔒 Security Configuration

### HTTPS and SSL
```javascript
// Vercel automatically provides HTTPS
// Render automatically provides HTTPS
// Force HTTPS redirects in production
```

### CORS Security
```python
# Production CORS configuration
if not settings.debug:
    cors_origins = [
        "https://marine-platform.vercel.app",
        "https://your-custom-domain.com"
    ]
    cors_allow_credentials = True
```

### API Key Security
```typescript
// Frontend: Never expose API keys
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY; // Build-time only

// Backend: Secure key handling
@lru_cache()
def get_api_keys():
    return {
        "gemini": os.getenv("GEMINI_API_KEY"),
        "obis": os.getenv("OBIS_API_KEY")  # If required
    }
```

## 🚨 Error Handling and Recovery

### Frontend Error Boundaries
```typescript
class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to monitoring service
    MonitoringService.trackError(error, 'React Error Boundary');
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

### Backend Error Recovery
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": str(uuid.uuid4())}
    )
```

## 📈 Scaling and Performance

### Frontend Optimization
- **Code Splitting**: Lazy loading of routes
- **Asset Optimization**: Image compression, minification
- **CDN**: Global edge caching
- **Bundle Analysis**: Webpack bundle analyzer

### Backend Scaling
- **Horizontal Scaling**: Multiple instances
- **Caching**: Redis for API responses
- **Database**: Connection pooling
- **Load Balancing**: Automatic with Render

### Database Scaling (Future)
```python
# Database optimization
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

## 🔄 Maintenance and Updates

### Update Strategy
1. **Dependencies**: Regular security updates
2. **API Versions**: Monitor OBIS and Gemini API changes
3. **Performance**: Regular performance audits
4. **Security**: Security scanning and updates

### Rollback Strategy
```bash
# Vercel: Instant rollback to previous deployment
vercel --prod rollback

# Render: Rollback to previous Docker image
# Through Render dashboard or API
```

This deployment documentation provides a comprehensive guide for deploying and maintaining the Marine Data Platform in a production environment with modern DevOps practices.