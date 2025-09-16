# Marine Data Platform Backend

AI-Driven Unified Data Platform for Oceanographic, Fisheries, and Molecular Biodiversity Insights

## Quick Start

### Installation
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Run
```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`

## Features
- Multi-source data integration (OBIS, GBIF)
- AI-enhanced analysis with Groq LLM
- Data standardization (Darwin Core, CF conventions)
- RESTful APIs for all operations
- Quality control and validation

## API Endpoints
- `/api/v1/biodiversity` - Species data and analysis
- `/api/v1/oceanography` - Ocean measurements
- `/api/v1/data-integration` - Multi-source integration
- `/api/v1/analytics` - AI-powered analytics

## Documentation
Visit `/docs` for interactive API documentation

## Environment Variables
Set in `.env`:
- `GROQ_API_KEY` - Your Groq API key
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection

## Deployment
Ready for Render deployment with included Dockerfile.