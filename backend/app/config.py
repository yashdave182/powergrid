from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables from .env file (useful for local development)
load_dotenv()

# Parse allowed origins from comma-separated env var if provided
_allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
_default_allowed = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]
_parsed_allowed = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()] if _allowed_origins_env else _default_allowed


class Settings(BaseModel):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/marine_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API URLs
    obis_api_url: str = os.getenv("OBIS_API_URL", "https://api.obis.org/v3/")
    gbif_api_url: str = os.getenv("GBIF_API_URL", "https://api.gbif.org/v1/")
    
    # LLM API
    groq_api_key: str = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    allowed_origins: List[str] = _parsed_allowed


settings = Settings()