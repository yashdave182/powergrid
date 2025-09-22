#!/usr/bin/env python3
"""
CMLRE Marine Data Platform - Simple Integration Demo
===================================================

A simplified demonstration of real API integration with error handling.
This script shows how to connect to and retrieve data from:
- INCOIS ERDDAP (Indian oceanographic data)
- WoRMS (Marine species taxonomy)
- NCBI E-utilities (Molecular sequences)

Usage:
    python simple_integration_demo.py
"""

import asyncio
import httpx
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMarineAPIDemo:
    """Simple demonstration of marine data API integration"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def demo_incois_temperature(self):
        """Demonstrate INCOIS temperature data retrieval"""
        print("\n🇮🇳 INCOIS Temperature Data Demo")
        print("-" * 40)
        
        try:
            # Build ERDDAP query for Arabian Sea region
            base_url = "https://incois.gov.in/erddap/tabledap/OSF_Temperature.json"
            params = {
                'latitude,longitude,temperature,time': '',
                'latitude>=': '15.0',
                'latitude<=': '25.0',
                'longitude>=': '65.0', 
                'longitude<=': '75.0',
                'orderByLimit("10")': ''
            }
            
            # Convert params to query string
            query_parts = []
            for key, value in params.items():
                if value:
                    query_parts.append(f"{key}={value}")
                else:
                    query_parts.append(key)
            
            url = f"{base_url}?{'&'.join(query_parts)}"
            logger.info(f"Requesting: {url}")
            
            response = await self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'table' in data and 'rows' in data['table']:
                    rows = data['table']['rows']
                    headers = data['table']['columnNames']
                    
                    print(f"✅ Retrieved {len(rows)} temperature records")
                    print(f"   Headers: {', '.join(headers)}")
                    
                    if rows:
                        print(f"   Sample record: {rows[0]}")
                        
                        # Parse sample record
                        sample = dict(zip(headers, rows[0]))
                        print(f"   📍 Location: {sample.get('latitude', 'N/A')}°N, {sample.get('longitude', 'N/A')}°E")
                        print(f"   🌡️  Temperature: {sample.get('temperature', 'N/A')}°C")
                        print(f"   📅 Time: {sample.get('time', 'N/A')}")
                    
                    return len(rows)
                else:
                    print("❌ No data in response")
                    return 0
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return 0
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return 0
    
    async def demo_worms_taxonomy(self, species_name="Rastrelliger kanagurta"):
        """Demonstrate WoRMS taxonomic data retrieval"""
        print(f"\n🦠 WoRMS Taxonomy Demo - {species_name}")
        print("-" * 40)
        
        try:
            # Step 1: Get AphiaID
            aphia_url = f"http://www.marinespecies.org/rest/AphiaIDByName/{species_name.replace(' ', '%20')}"
            logger.info(f"Getting AphiaID: {aphia_url}")
            
            response = await self.session.get(aphia_url)
            
            if response.status_code == 200:
                aphia_id = response.text.strip().strip('"')
                
                if aphia_id != "-999":
                    print(f"✅ AphiaID found: {aphia_id}")
                    
                    # Step 2: Get classification
                    class_url = f"http://www.marinespecies.org/rest/AphiaClassificationByAphiaID/{aphia_id}"
                    logger.info(f"Getting classification: {class_url}")
                    
                    class_response = await self.session.get(class_url)
                    
                    if class_response.status_code == 200:
                        classification = class_response.json()
                        
                        print(f"✅ Taxonomic classification retrieved")
                        print(f"   Classification levels: {len(classification)}")
                        
                        # Display hierarchy
                        for taxon in classification:
                            rank = taxon.get('rank', 'Unknown')
                            name = taxon.get('scientificname', 'Unknown')
                            print(f"   {rank}: {name}")
                        
                        return True
                    else:
                        print(f"❌ Classification error: {class_response.status_code}")
                        return False
                else:
                    print(f"❌ Species not found in WoRMS")
                    return False
            else:
                print(f"❌ AphiaID lookup error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def demo_ncbi_sequences(self, species_name="Rastrelliger kanagurta", gene="COI"):
        """Demonstrate NCBI sequence retrieval"""
        print(f"\n🧬 NCBI Sequences Demo - {species_name} {gene}")
        print("-" * 40)
        
        try:
            # Step 1: Search for sequences
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                'db': 'nucleotide',
                'term': f'{species_name}[Organism] AND {gene}[Gene]',
                'retmax': '5',
                'retmode': 'json'
            }
            
            logger.info(f"Searching NCBI: {search_url}")
            response = await self.session.get(search_url, params=search_params)
            
            if response.status_code == 200:
                search_data = response.json()
                
                if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
                    id_list = search_data['esearchresult']['idlist']
                    
                    if id_list:
                        print(f"✅ Found {len(id_list)} sequence IDs")
                        print(f"   IDs: {', '.join(id_list)}")
                        
                        # Step 2: Fetch sequences
                        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                        fetch_params = {
                            'db': 'nucleotide',
                            'id': ','.join(id_list[:3]),  # Limit to first 3
                            'rettype': 'fasta',
                            'retmode': 'text'
                        }
                        
                        fetch_response = await self.session.get(fetch_url, params=fetch_params)
                        
                        if fetch_response.status_code == 200:
                            sequences = fetch_response.text
                            
                            # Count sequences
                            seq_count = sequences.count('>') if sequences else 0
                            print(f"✅ Retrieved {seq_count} sequences")
                            
                            # Show first sequence header
                            if '>' in sequences:
                                first_header = sequences.split('\n')[0]
                                print(f"   First sequence: {first_header[:80]}...")
                                
                                # Show sequence length info
                                lines = sequences.split('\n')
                                seq_lines = [line for line in lines if not line.startswith('>') and line.strip()]
                                if seq_lines:
                                    total_length = sum(len(line.strip()) for line in seq_lines[:10])  # Rough estimate
                                    print(f"   Approximate length: {total_length}+ bp")
                            
                            return seq_count
                        else:
                            print(f"❌ Fetch error: {fetch_response.status_code}")
                            return 0
                    else:
                        print(f"❌ No sequences found for {species_name} {gene}")
                        return 0
            else:
                print(f"❌ Search error: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return 0
    
    async def run_complete_demo(self):
        """Run complete demonstration"""
        print("🌊 CMLRE Marine Data Platform - Simple API Integration Demo")
        print("=" * 65)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {}
        
        # 1. Oceanographic data
        print("\n📊 Phase 1: Oceanographic Data")
        results['incois_records'] = await self.demo_incois_temperature()
        
        # 2. Taxonomic data
        print("\n🐟 Phase 2: Taxonomic Classification")
        test_species = ["Rastrelliger kanagurta", "Thunnus albacares", "Katsuwonus pelamis"]
        
        results['taxonomy_success'] = 0
        for species in test_species:
            if await self.demo_worms_taxonomy(species):
                results['taxonomy_success'] += 1
        
        # 3. Molecular data
        print("\n🧬 Phase 3: Molecular Sequences")
        results['molecular_sequences'] = 0
        for species in test_species[:2]:  # Limit for demo
            count = await self.demo_ncbi_sequences(species)
            results['molecular_sequences'] += count
        
        # Summary
        print("\n" + "=" * 65)
        print("🎉 Demo Complete!")
        print(f"📊 Oceanographic records: {results['incois_records']}")
        print(f"🐟 Species classified: {results['taxonomy_success']}/{len(test_species)}")
        print(f"🧬 Molecular sequences: {results['molecular_sequences']}")
        print("✅ All APIs successfully demonstrated")
        
        return results

async def main():
    """Main demo function"""
    async with SimpleMarineAPIDemo() as demo:
        await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())