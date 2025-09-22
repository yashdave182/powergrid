#!/usr/bin/env python3
"""
CMLRE Marine Data Platform - Sample Integration Pipeline
========================================================

This script demonstrates a complete data pipeline that:
1. Queries real-world APIs (Copernicus, WoRMS, NCBI)
2. Processes and standardizes the data
3. Stores results in PostgreSQL/PostGIS database

APIs Demonstrated:
- Oceanographic: ARGO floats (via IFREMER ERDDAP)
- Taxonomy: WoRMS (World Register of Marine Species)
- Molecular: NCBI E-utilities

Usage:
    python sample_integration_pipeline.py
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.marine_data import (
    Base, UnifiedMarineData, OceanographicData, 
    TaxonomicData, MolecularData
)
from app.services.data_standardizer import DataStandardizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SampleIntegrationPipeline:
    """Sample integration pipeline demonstrating real API connections"""
    
    def __init__(self, db_url: str = "sqlite:///./sample_marine_data.db"):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.standardizer = DataStandardizer()
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        # API endpoints
        self.argo_endpoint = "https://erddap.ifremer.fr/erddap/tabledap/ArgoFloats.json"
        self.worms_endpoint = "http://www.marinespecies.org/rest"
        self.ncbi_endpoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    async def fetch_argo_data(self, session: aiohttp.ClientSession) -> List[Dict]:
        """
        Fetch oceanographic data from ARGO floats in Indian Ocean
        """
        logger.info("Fetching ARGO float data from Indian Ocean...")
        
        # Query parameters for Indian Ocean region
        params = {
            'platform_number,latitude,longitude,temperature,psal,time': '',
            'latitude>=': '-30',
            'latitude<=': '30', 
            'longitude>=': '60',
            'longitude<=': '100',
            'time>=': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'orderBy': 'time'
        }
        
        try:
            async with session.get(self.argo_endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # ERDDAP returns data in format: {"table": {"columnNames": [...], "rows": [...]}}
                    if 'table' in data:
                        columns = data['table']['columnNames']
                        rows = data['table']['rows']
                        
                        # Convert to list of dictionaries
                        results = []
                        for row in rows[:100]:  # Limit to 100 records for demo
                            record = dict(zip(columns, row))
                            results.append(record)
                        
                        logger.info(f"Retrieved {len(results)} ARGO records")
                        return results
                    
        except Exception as e:
            logger.error(f"Error fetching ARGO data: {e}")
            
        return []
    
    async def fetch_worms_species_data(self, session: aiohttp.ClientSession, 
                                     species_name: str) -> Dict:
        """
        Fetch taxonomic data from WoRMS for a given species
        """
        logger.info(f"Fetching WoRMS data for {species_name}...")
        
        try:
            # First, get AphiaID by name
            search_url = f"{self.worms_endpoint}/AphiaIDByName/{species_name}"
            async with session.get(search_url) as response:
                if response.status == 200:
                    aphia_id = await response.text()
                    aphia_id = aphia_id.strip('"')  # Remove quotes
                    
                    if aphia_id and aphia_id != '-999':
                        # Get full taxonomic classification
                        classification_url = f"{self.worms_endpoint}/AphiaClassificationByAphiaID/{aphia_id}"
                        async with session.get(classification_url) as class_response:
                            if class_response.status == 200:
                                classification = await class_response.json()
                                
                                # Get species record
                                record_url = f"{self.worms_endpoint}/AphiaRecordByAphiaID/{aphia_id}"
                                async with session.get(record_url) as record_response:
                                    if record_response.status == 200:
                                        record = await record_response.json()
                                        
                                        result = {
                                            'aphia_id': aphia_id,
                                            'scientific_name': species_name,
                                            'classification': classification,
                                            'record': record
                                        }
                                        
                                        logger.info(f"Retrieved WoRMS data for {species_name}")
                                        return result
                                        
        except Exception as e:
            logger.error(f"Error fetching WoRMS data for {species_name}: {e}")
            
        return {}
    
    async def fetch_ncbi_sequences(self, session: aiohttp.ClientSession, 
                                 species_name: str, gene: str = "COI") -> List[Dict]:
        """
        Fetch molecular sequences from NCBI for a given species
        """
        logger.info(f"Fetching NCBI {gene} sequences for {species_name}...")
        
        try:
            # Search for sequences
            search_params = {
                'db': 'nucleotide',
                'term': f'{species_name}[Organism] AND {gene}[Gene]',
                'retmax': '10',  # Limit for demo
                'retmode': 'json'
            }
            
            search_url = f"{self.ncbi_endpoint}/esearch.fcgi"
            async with session.get(search_url, params=search_params) as response:
                if response.status == 200:
                    search_data = await response.json()
                    
                    if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
                        id_list = search_data['esearchresult']['idlist']
                        
                        if id_list:
                            # Fetch sequence details
                            fetch_params = {
                                'db': 'nucleotide',
                                'id': ','.join(id_list),
                                'rettype': 'fasta',
                                'retmode': 'text'
                            }
                            
                            fetch_url = f"{self.ncbi_endpoint}/efetch.fcgi"
                            async with session.get(fetch_url, params=fetch_params) as fetch_response:
                                if fetch_response.status == 200:
                                    fasta_data = await fetch_response.text()
                                    
                                    # Parse FASTA sequences
                                    sequences = self._parse_fasta(fasta_data)
                                    
                                    logger.info(f"Retrieved {len(sequences)} {gene} sequences for {species_name}")
                                    return sequences
                                    
        except Exception as e:
            logger.error(f"Error fetching NCBI sequences for {species_name}: {e}")
            
        return []
    
    def _parse_fasta(self, fasta_text: str) -> List[Dict]:
        """Parse FASTA format text into sequence records"""
        sequences = []
        current_header = None
        current_sequence = []
        
        for line in fasta_text.split('\n'):
            line = line.strip()
            if line.startswith('>'):
                if current_header and current_sequence:
                    sequences.append({
                        'header': current_header,
                        'sequence': ''.join(current_sequence),
                        'length': len(''.join(current_sequence))
                    })
                current_header = line[1:]  # Remove '>'
                current_sequence = []
            elif line:
                current_sequence.append(line)
        
        # Add last sequence
        if current_header and current_sequence:
            sequences.append({
                'header': current_header,
                'sequence': ''.join(current_sequence),
                'length': len(''.join(current_sequence))
            })
            
        return sequences
    
    def store_oceanographic_data(self, argo_data: List[Dict]) -> int:
        """Store ARGO oceanographic data in database"""
        logger.info("Storing oceanographic data...")
        
        db = self.SessionLocal()
        stored_count = 0
        
        try:
            for record in argo_data:
                try:
                    # Create unified record
                    unified_data = UnifiedMarineData(
                        data_type="oceanographic",
                        source="ARGO_IFREMER",
                        source_id=str(record.get('platform_number', '')),
                        collection_date=datetime.fromisoformat(record.get('time', '').replace('T', ' ').replace('Z', '')),
                        latitude=float(record.get('latitude', 0)),
                        longitude=float(record.get('longitude', 0)),
                        depth=0.0,  # Surface data
                        quality_score=0.9,  # ARGO data is high quality
                        metadata_json={
                            "platform_number": record.get('platform_number'),
                            "data_source": "ARGO Global Ocean Observing System"
                        }
                    )
                    
                    db.add(unified_data)
                    db.flush()  # Get the ID
                    
                    # Create specialized oceanographic record
                    ocean_data = OceanographicData(
                        unified_data_id=unified_data.id,
                        temperature=float(record.get('temperature', 0)) if record.get('temperature') else None,
                        salinity=float(record.get('psal', 0)) if record.get('psal') else None,
                        measurement_type="CTD_profile",
                        instrument="ARGO_float",
                        processing_level="real_time"
                    )
                    
                    db.add(ocean_data)
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing ARGO record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Stored {stored_count} oceanographic records")
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
            
        return stored_count
    
    def store_taxonomic_data(self, species_data: Dict) -> bool:
        """Store WoRMS taxonomic data in database"""
        if not species_data:
            return False
            
        logger.info("Storing taxonomic data...")
        
        db = self.SessionLocal()
        
        try:
            # Create unified record
            unified_data = UnifiedMarineData(
                data_type="taxonomic",
                source="WoRMS",
                source_id=species_data.get('aphia_id', ''),
                collection_date=datetime.now(),
                latitude=0.0,  # Global taxonomic data
                longitude=0.0,
                depth=0.0,
                quality_score=0.95,  # WoRMS is authoritative
                metadata_json=species_data.get('record', {})
            )
            
            db.add(unified_data)
            db.flush()
            
            # Extract taxonomic hierarchy
            classification = species_data.get('classification', {})
            kingdom = genus = family = order = class_name = phylum = ""
            
            if isinstance(classification, list):
                for taxon in classification:
                    rank = taxon.get('rank', '').lower()
                    if rank == 'kingdom':
                        kingdom = taxon.get('scientificname', '')
                    elif rank == 'phylum':
                        phylum = taxon.get('scientificname', '')
                    elif rank == 'class':
                        class_name = taxon.get('scientificname', '')
                    elif rank == 'order':
                        order = taxon.get('scientificname', '')
                    elif rank == 'family':
                        family = taxon.get('scientificname', '')
                    elif rank == 'genus':
                        genus = taxon.get('scientificname', '')
            
            # Create specialized taxonomic record
            taxonomic_data = TaxonomicData(
                unified_data_id=unified_data.id,
                scientific_name=species_data.get('scientific_name', ''),
                common_name=species_data.get('record', {}).get('vernacular', ''),
                taxonomic_status=species_data.get('record', {}).get('status', ''),
                kingdom=kingdom,
                phylum=phylum,
                class_name=class_name,
                order=order,
                family=family,
                genus=genus,
                species=species_data.get('scientific_name', '').split()[-1] if ' ' in species_data.get('scientific_name', '') else '',
                authority=species_data.get('record', {}).get('authority', ''),
                taxonomic_database="WoRMS",
                confidence_score=0.95
            )
            
            db.add(taxonomic_data)
            db.commit()
            
            logger.info(f"Stored taxonomic data for {species_data.get('scientific_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing taxonomic data: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def store_molecular_data(self, species_name: str, sequences: List[Dict]) -> int:
        """Store NCBI molecular sequences in database"""
        logger.info("Storing molecular data...")
        
        db = self.SessionLocal()
        stored_count = 0
        
        try:
            for seq_record in sequences:
                try:
                    # Create unified record
                    unified_data = UnifiedMarineData(
                        data_type="molecular",
                        source="NCBI",
                        source_id=seq_record.get('header', '').split()[0],
                        collection_date=datetime.now(),
                        latitude=0.0,  # Unknown location for molecular data
                        longitude=0.0,
                        depth=0.0,
                        quality_score=0.85,  # Good quality for NCBI data
                        metadata_json={
                            "sequence_header": seq_record.get('header'),
                            "sequence_length": seq_record.get('length')
                        }
                    )
                    
                    db.add(unified_data)
                    db.flush()
                    
                    # Create specialized molecular record
                    molecular_data = MolecularData(
                        unified_data_id=unified_data.id,
                        species_name=species_name,
                        gene_name="COI",
                        sequence_type="DNA",
                        sequence_data=seq_record.get('sequence', ''),
                        sequence_length=seq_record.get('length', 0),
                        database_source="NCBI",
                        accession_number=seq_record.get('header', '').split()[0],
                        quality_metrics={"source": "NCBI_GenBank"}
                    )
                    
                    db.add(molecular_data)
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing molecular record: {e}")
                    continue
            
            db.commit()
            logger.info(f"Stored {stored_count} molecular sequences")
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
            
        return stored_count
    
    async def run_complete_pipeline(self):
        """
        Run the complete integration pipeline
        """
        logger.info("🌊 Starting CMLRE Marine Data Integration Pipeline...")
        
        async with aiohttp.ClientSession() as session:
            # 1. Fetch oceanographic data from ARGO
            logger.info("\n📊 Phase 1: Oceanographic Data Collection")
            argo_data = await self.fetch_argo_data(session)
            oceanographic_count = self.store_oceanographic_data(argo_data)
            
            # 2. Fetch taxonomic data from WoRMS
            logger.info("\n🐟 Phase 2: Taxonomic Data Collection")
            test_species = [
                "Rastrelliger kanagurta",  # Indian mackerel
                "Thunnus albacares",       # Yellowfin tuna
                "Katsuwonus pelamis"       # Skipjack tuna
            ]
            
            taxonomic_count = 0
            for species in test_species:
                species_data = await self.fetch_worms_species_data(session, species)
                if self.store_taxonomic_data(species_data):
                    taxonomic_count += 1
            
            # 3. Fetch molecular data from NCBI
            logger.info("\n🧬 Phase 3: Molecular Data Collection")
            molecular_count = 0
            for species in test_species[:2]:  # Limit for demo
                sequences = await self.fetch_ncbi_sequences(session, species)
                molecular_count += self.store_molecular_data(species, sequences)
        
        # 4. Summary report
        logger.info("\n✅ Pipeline Complete!")
        logger.info("="*50)
        logger.info(f"📊 Oceanographic records stored: {oceanographic_count}")
        logger.info(f"🐟 Taxonomic records stored: {taxonomic_count}")
        logger.info(f"🧬 Molecular sequences stored: {molecular_count}")
        logger.info(f"🗄️  Database: {self.db_url}")
        logger.info("="*50)
        
        return {
            'oceanographic': oceanographic_count,
            'taxonomic': taxonomic_count,
            'molecular': molecular_count
        }

async def main():
    """Main function to run the integration pipeline"""
    print("🌊 CMLRE Marine Data Platform - Sample Integration Pipeline")
    print("=" * 60)
    
    # Initialize pipeline with SQLite for demo (change to PostgreSQL for production)
    pipeline = SampleIntegrationPipeline()
    
    try:
        # Run the complete pipeline
        results = await pipeline.run_complete_pipeline()
        
        print("\n🎉 Integration pipeline completed successfully!")
        print(f"Total records processed: {sum(results.values())}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\n❌ Pipeline failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())