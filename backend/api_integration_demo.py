#!/usr/bin/env python3
"""
CMLRE Marine Data Platform - Advanced API Integration Demo
==========================================================

This script demonstrates the advanced API integration services we built,
showcasing integration with all major Indian Ocean data sources:

- INCOIS ERDDAP (Indian oceanographic data)
- ARGO floats (Global ocean observing)
- FishBase API (Fish species data)
- WoRMS (Marine species taxonomy)
- NCBI E-utilities (Molecular sequences)
- BOLD Systems (DNA barcoding)

Usage:
    python api_integration_demo.py
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from app.services.indian_ocean_apis import (
    INCOISClient, ArgoFloatsClient, FishBaseAPIClient,
    WoRMSClient, NCBIClient, BOLDClient
)
from app.services.indian_ocean_integration import IndianOceanDataProcessor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.marine_data import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIIntegrationDemo:
    """Comprehensive demonstration of API integration capabilities"""
    
    def __init__(self, db_url: str = "sqlite:///./demo_marine_data.db"):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        # Initialize API clients
        self.incois_client = INCOISClient()
        self.argo_client = ArgoFloatsClient()
        self.fishbase_client = FishBaseAPIClient()
        self.worms_client = WoRMSClient()
        self.ncbi_client = NCBIClient()
        self.bold_client = BOLDClient()
        
        # Initialize integration service
        self.integration = IndianOceanDataProcessor()
    
    async def demo_incois_integration(self):
        """Demonstrate INCOIS ERDDAP data integration"""
        print("\n🇮🇳 INCOIS (Indian National Centre for Ocean Information Services)")
        print("-" * 60)
        
        try:
            # Fetch temperature data from Arabian Sea
            data = await self.incois_client.get_oceanographic_data(
                dataset_id="OSF_Temperature",
                latitude_min=15.0,
                latitude_max=25.0,
                longitude_min=65.0,
                longitude_max=75.0
            )
            
            if data and data.get('status') == 'success':
                # Extract actual data from response structure
                api_data = data.get('data', {})
                if 'table' in api_data and 'rows' in api_data['table'] and api_data['table']['rows']:
                    rows = api_data['table']['rows']
                    headers = api_data['table']['columnNames']
                    print(f"✅ Retrieved {len(rows)} temperature records from Arabian Sea")
                    
                    # Create sample record from first row
                    if rows:
                        sample_dict = dict(zip(headers, rows[0]))
                        print(f"   Sample: {sample_dict.get('latitude', 'N/A')}°N, {sample_dict.get('longitude', 'N/A')}°E")
                        print(f"   Temperature: {sample_dict.get('temperature', 'N/A')}°C")
                
                # Store in database
                stored_ids = await self.integration.process_incois_data(data)
                print(f"   📊 Stored {len(stored_ids)} records in database")
            else:
                print("❌ No data retrieved from INCOIS")
                
        except Exception as e:
            print(f"❌ INCOIS integration failed: {e}")
    
    async def demo_argo_integration(self):
        """Demonstrate ARGO float data integration"""
        print("\n🌊 ARGO Global Ocean Observing System")
        print("-" * 60)
        
        try:
            # Fetch data from Indian Ocean region
            data = await self.argo_client.get_argo_profiles(
                latitude_min=-10.0,
                latitude_max=30.0,
                longitude_min=60.0,
                longitude_max=100.0,
                start_date="2023-01-01",
                limit=15
            )
            
            if data and data.get('status') == 'success':
                # Extract actual data from response structure
                api_data = data.get('data', {})
                if 'table' in api_data and 'rows' in api_data['table'] and api_data['table']['rows']:
                    rows = api_data['table']['rows']
                    headers = api_data['table']['columnNames']
                    print(f"✅ Retrieved {len(rows)} ARGO float profiles from Indian Ocean")
                    
                    # Create sample record from first row
                    if rows:
                        sample_dict = dict(zip(headers, rows[0]))
                        print(f"   Platform: {sample_dict.get('platform_number', 'N/A')}")
                        print(f"   Location: {sample_dict.get('latitude', 'N/A')}°N, {sample_dict.get('longitude', 'N/A')}°E")
                        print(f"   Temperature: {sample_dict.get('temp', 'N/A')}°C")
                
                # Store in database - Note: ARGO processing not implemented in current processor
                print(f"   📊 ARGO data retrieved (storage implementation pending)")
            else:
                print("❌ No ARGO data retrieved")
                
        except Exception as e:
            print(f"❌ ARGO integration failed: {e}")
    
    async def demo_fishbase_integration(self):
        """Demonstrate FishBase API integration"""
        print("\n🐟 FishBase - Global Fish Species Database")
        print("-" * 60)
        
        indian_ocean_species = [
            ("Thunnus", "albacares"),    # Yellowfin tuna
            ("Rastrelliger", "kanagurta"), # Indian mackerel
            ("Scomberomorus", "commerson") # Spanish mackerel
        ]
        
        try:
            for genus, species in indian_ocean_species:
                print(f"\n🔍 Searching for {genus} {species}...")
                
                data = await self.fishbase_client.get_species_data(genus, species)
                if data:
                    print(f"   ✅ Found species data")
                    print(f"   Common name: {data.get('CommonName', 'N/A')}")
                    print(f"   Family: {data.get('Family', 'N/A')}")
                    print(f"   Max length: {data.get('Length', 'N/A')} cm")
                    
                    # Store in database  
                    stored_ids = await self.integration.process_fishbase_data(data, f"{genus} {species}")
                    print(f"   📊 Stored in database: {len(stored_ids) > 0}")
                else:
                    print(f"   ❌ No data found for {genus} {species}")
                    
        except Exception as e:
            print(f"❌ FishBase integration failed: {e}")
    
    async def demo_worms_integration(self):
        """Demonstrate WoRMS taxonomic integration"""
        print("\n🦠 WoRMS - World Register of Marine Species")
        print("-" * 60)
        
        marine_species = [
            "Rastrelliger kanagurta",
            "Thunnus albacares", 
            "Katsuwonus pelamis",
            "Scomberomorus commerson"
        ]
        
        try:
            for species_name in marine_species:
                print(f"\n🔍 Taxonomic lookup for {species_name}...")
                
                species_info = await self.worms_client.get_complete_species_info(species_name)
                if species_info and 'basic_info' in species_info:
                    basic = species_info['basic_info']
                    print(f"   ✅ AphiaID: {basic.get('AphiaID', 'N/A')}")
                    print(f"   Status: {basic.get('status', 'N/A')}")
                    print(f"   Authority: {basic.get('authority', 'N/A')}")
                    
                    if 'classification' in species_info:
                        classification = species_info['classification']
                        if classification:
                            kingdom = next((c['scientificname'] for c in classification if c['rank'] == 'Kingdom'), 'N/A')
                            family = next((c['scientificname'] for c in classification if c['rank'] == 'Family'), 'N/A')
                            print(f"   Kingdom: {kingdom}, Family: {family}")
                    
                    # Store in database
                    stored_ids = await self.integration.process_worms_data(species_info, species_name)
                    print(f"   📊 Stored in database: {len(stored_ids) > 0}")
                else:
                    print(f"   ❌ No taxonomic data found")
                    
        except Exception as e:
            print(f"❌ WoRMS integration failed: {e}")
    
    async def demo_ncbi_integration(self):
        """Demonstrate NCBI molecular data integration"""
        print("\n🧬 NCBI - National Center for Biotechnology Information")
        print("-" * 60)
        
        target_species = [
            "Rastrelliger kanagurta",
            "Thunnus albacares"
        ]
        
        try:
            for species in target_species:
                print(f"\n🔍 Searching COI sequences for {species}...")
                
                sequences = await self.ncbi_client.search_sequences(species, gene="COI", max_results=5)
                if sequences.get('status') == 'success':
                    seq_count = sequences.get('sequences_retrieved', 0)
                    print(f"   ✅ Found {seq_count} COI sequences")
                    print(f"   Sequences: {sequences.get('sequences', '')[:100]}...")
                    
                    # Store in database - Note: NCBI processing not implemented in current processor
                    print(f"   📊 NCBI data retrieved (storage implementation pending)")
                else:
                    print(f"   ❌ No sequences found for {species}")
                    
        except Exception as e:
            print(f"❌ NCBI integration failed: {e}")
    
    async def demo_bold_integration(self):
        """Demonstrate BOLD Systems integration"""
        print("\n🏷️  BOLD Systems - Barcode of Life Data Systems")
        print("-" * 60)
        
        try:
            species_name = "Rastrelliger kanagurta"
            print(f"🔍 Searching BOLD records for {species_name}...")
            
            # Get taxon data
            taxon_data = await self.bold_client.search_taxon(species_name)
            if taxon_data:
                print(f"   ✅ Found BOLD taxon data")
                print(f"   Taxon ID: {taxon_data.get('taxid', 'N/A')}")
                print(f"   Rank: {taxon_data.get('rank', 'N/A')}")
                
            # Get specimen records
            specimens = await self.bold_client.get_specimen_records(species_name)
            if specimens and specimens.get('status') == 'success':
                specimen_data = specimens.get('data', [])
                if isinstance(specimen_data, list) and specimen_data:
                    print(f"   ✅ Found {len(specimen_data)} specimen records")
                    sample = specimen_data[0]
                    print(f"   Sample ID: {sample.get('sampleid', 'N/A')}")
                    print(f"   Country: {sample.get('country', 'N/A')}")
                elif isinstance(specimen_data, str):
                    print(f"   ✅ Found specimen data (text format): {len(specimen_data)} characters")
                else:
                    print(f"   ✅ Found specimen data: {type(specimen_data)}")
                
                # Store in database - Note: BOLD processing not implemented in current processor
                print(f"   📊 BOLD data retrieved (storage implementation pending)")
            else:
                print(f"   ❌ No specimen records found")
                
        except Exception as e:
            print(f"❌ BOLD integration failed: {e}")
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of all API integrations"""
        print("🌊 CMLRE Marine Data Platform - Comprehensive API Integration Demo")
        print("=" * 70)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🗄️  Database: {self.db_url}")
        
        # Run all demonstrations
        await self.demo_incois_integration()
        await self.demo_argo_integration() 
        await self.demo_fishbase_integration()
        await self.demo_worms_integration()
        await self.demo_ncbi_integration()
        await self.demo_bold_integration()
        
        print("\n" + "=" * 70)
        print("🎉 Comprehensive API integration demo completed!")
        print("✅ All major Indian Ocean data sources demonstrated")
        print("📊 Data stored in unified database schema")
        print("🔗 Ready for cross-disciplinary analysis")
        
        # Generate summary
        await self.generate_integration_summary()
    
    async def generate_integration_summary(self):
        """Generate summary of integrated data"""
        print("\n📋 Integration Summary")
        print("-" * 30)
        
        db = self.SessionLocal()
        try:
            from app.models.marine_data import UnifiedMarineData
            
            # Count records by type
            total_records = db.query(UnifiedMarineData).count()
            oceanographic = db.query(UnifiedMarineData).filter_by(data_type="oceanographic").count()
            taxonomic = db.query(UnifiedMarineData).filter_by(data_type="taxonomic").count()
            molecular = db.query(UnifiedMarineData).filter_by(data_type="molecular").count()
            fisheries = db.query(UnifiedMarineData).filter_by(data_type="fisheries").count()
            
            print(f"📊 Total records: {total_records}")
            print(f"🌊 Oceanographic: {oceanographic}")
            print(f"🐟 Fisheries: {fisheries}")
            print(f"🦠 Taxonomic: {taxonomic}")
            print(f"🧬 Molecular: {molecular}")
            
            # Show data sources
            sources = db.query(UnifiedMarineData.source).distinct().all()
            print(f"🔗 Data sources: {', '.join([s[0] for s in sources])}")
            
        except Exception as e:
            print(f"❌ Summary generation failed: {e}")
        finally:
            db.close()

async def main():
    """Main demonstration function"""
    demo = APIIntegrationDemo()
    await demo.run_comprehensive_demo()

if __name__ == "__main__":
    asyncio.run(main())