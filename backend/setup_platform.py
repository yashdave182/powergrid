#!/usr/bin/env python3
\"\"\"
CMLRE Marine Data Platform Setup Script
Unified storage architecture for oceanographic, fisheries, taxonomic, and molecular data
\"\"\"

import sys
import os
from pathlib import Path
import subprocess
import json
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

class MarineDataPlatformSetup:
    def __init__(self):
        self.app_dir = Path(__file__).parent
        
    def install_dependencies(self):
        print(\"📦 Installing dependencies...\")
        try:
            subprocess.run([sys.executable, \"-m\", \"pip\", \"install\", \"-r\", \"requirements.txt\"], check=True)
            print(\"✅ Dependencies installed\")
            return True
        except subprocess.CalledProcessError as e:
            print(f\"❌ Failed to install dependencies: {e}\")
            return False
    
    def setup_environment(self):
        print(\"🔧 Setting up environment...\")
        env_vars = {
            \"DATABASE_URL\": \"sqlite:///./marine_data.db\",
            \"GEMINI_API_KEY\": \"your-gemini-api-key-here\",
            \"ENVIRONMENT\": \"development\",
            \"DEBUG\": \"True\"
        }
        
        with open(\".env\", \"w\") as f:
            for key, value in env_vars.items():
                f.write(f\"{key}={value}\n\")
        
        print(\"✅ Environment configured\")
        return True
    
    def create_database(self):
        print(\"🗄️ Creating database...\")
        try:
            from app.core.database import engine
            from app.models.marine_data import Base
            Base.metadata.create_all(bind=engine)
            print(\"✅ Database created\")
            return True
        except Exception as e:
            print(f\"❌ Database creation failed: {e}\")
            return False
    
    def create_sample_data(self):
        print(\"🎯 Creating sample data...\")
        try:
            from app.core.database import get_db
            from app.models.marine_data import UnifiedMarineData, OceanographicData
            
            sample_data = UnifiedMarineData(
                data_type=\"oceanographic\",
                data_category=\"water_quality\",
                collection_date=datetime.now(),
                latitude=12.9716,
                longitude=74.7965,
                region=\"Arabian Sea\",
                scientific_name=\"Test Species\",
                validation_status=\"validated\"
            )
            
            with next(get_db()) as db:
                db.add(sample_data)
                db.commit()
            
            print(\"✅ Sample data created\")
            return True
        except Exception as e:
            print(f\"❌ Sample data creation failed: {e}\")
            return False
    
    def generate_report(self):
        print(\"📊 Generating report...\")
        report = {
            \"platform\": \"CMLRE Marine Data Platform\",
            \"version\": \"1.0.0\",
            \"setup_date\": datetime.now().isoformat(),
            \"features\": [
                \"Unified marine data storage\",
                \"Oceanographic data management\",
                \"Fisheries data analysis\",
                \"Taxonomic classification\",
                \"Molecular biology and eDNA\",
                \"AI-powered analytics\",
                \"Cross-disciplinary integration\"
            ],
            \"endpoints\": {
                \"docs\": \"http://localhost:8000/docs\",
                \"health\": \"http://localhost:8000/health\",
                \"api\": \"http://localhost:8000/api/v1/\"
            }
        }
        
        with open(\"platform_report.json\", \"w\") as f:
            json.dump(report, f, indent=2)
        
        print(\"✅ Report generated\")
        return True
    
    def run_setup(self):
        print(\"🚀 CMLRE Marine Data Platform Setup\n\")
        
        steps = [
            (\"Installing dependencies\", self.install_dependencies),
            (\"Setting up environment\", self.setup_environment),
            (\"Creating database\", self.create_database),
            (\"Creating sample data\", self.create_sample_data),
            (\"Generating report\", self.generate_report)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f\"❌ Setup failed at: {step_name}\")
                return False
        
        print(\"\n🎉 Setup completed successfully!\")
        print(\"\n📋 Platform Features:\")
        print(\"   • Unified marine data storage\")
        print(\"   • AI-powered analytics\")
        print(\"   • Cross-disciplinary integration\")
        print(\"\n🚀 Start server: python -m uvicorn app.main:app --reload\")
        print(\"📖 API docs: http://localhost:8000/docs\")
        return True

if __name__ == \"__main__\":
    setup = MarineDataPlatformSetup()
    setup.run_setup()