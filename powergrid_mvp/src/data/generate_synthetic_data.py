import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

class SyntheticDataGenerator:
    """Generate realistic synthetic project data for MVP"""
    
    def __init__(self, n_projects=500):
        self.n_projects = n_projects
        self.project_types = ['Substation', 'Overhead Line', 'Underground Cable']
        self.regions = ['North', 'South', 'East', 'West', 'Central', 'Northeast']
        self.terrains = ['Plain', 'Hilly', 'Coastal', 'Forest', 'Urban', 'Mixed']
        
    def generate_projects(self):
        """Generate main project dataset"""
        
        data = []
        
        for i in range(self.n_projects):
            project_type = random.choice(self.project_types)
            region = random.choice(self.regions)
            terrain = random.choice(self.terrains)
            
            # Base characteristics
            if project_type == 'Substation':
                length_km = np.random.uniform(0.5, 5)
                voltage_level = random.choice([132, 220, 400, 765])
                base_cost = np.random.uniform(50, 500) * 1e6  # 50M to 500M
                base_duration = np.random.randint(180, 730)  # 6-24 months
            
            elif project_type == 'Overhead Line':
                length_km = np.random.uniform(10, 500)
                voltage_level = random.choice([132, 220, 400, 765])
                base_cost = length_km * np.random.uniform(5, 15) * 1e6
                base_duration = int(length_km * np.random.uniform(1.5, 3))
            
            else:  # Underground Cable
                length_km = np.random.uniform(5, 100)
                voltage_level = random.choice([132, 220, 400])
                base_cost = length_km * np.random.uniform(15, 30) * 1e6
                base_duration = int(length_km * np.random.uniform(2, 4))
            
            # Terrain difficulty (1-10 scale)
            terrain_difficulty = {
                'Plain': np.random.uniform(1, 3),
                'Urban': np.random.uniform(3, 5),
                'Coastal': np.random.uniform(4, 6),
                'Hilly': np.random.uniform(6, 8),
                'Forest': np.random.uniform(7, 9),
                'Mixed': np.random.uniform(4, 7)
            }[terrain]
            
            # Number of towers (for overhead lines)
            num_towers = int(length_km / np.random.uniform(0.3, 0.5)) if project_type == 'Overhead Line' else 0
            
            # Material costs
            steel_cost_per_ton = np.random.uniform(50000, 80000)
            copper_cost_per_ton = np.random.uniform(700000, 900000)
            cement_cost_per_ton = np.random.uniform(300, 500)
            
            total_steel_tons = length_km * np.random.uniform(10, 50)
            total_copper_tons = length_km * np.random.uniform(1, 5)
            total_cement_tons = length_km * np.random.uniform(50, 200)
            
            material_cost = (
                steel_cost_per_ton * total_steel_tons +
                copper_cost_per_ton * total_copper_tons +
                cement_cost_per_ton * total_cement_tons
            )
            
            # Labor
            estimated_manpower = int(base_duration * np.random.uniform(10, 50))
            labor_cost_per_person_day = np.random.uniform(500, 1500)
            total_labor_cost = estimated_manpower * labor_cost_per_person_day * base_duration
            
            # Vendor score (1-10)
            vendor_quality_score = np.random.uniform(4, 10)
            vendor_on_time_rate = np.random.uniform(0.6, 1.0)
            vendor_cost_efficiency = np.random.uniform(0.7, 1.0)
            
            # Regulatory timeline
            permit_days = np.random.randint(30, 180)
            clearance_days = np.random.randint(45, 200)
            
            # Weather factors
            monsoon_months = np.random.randint(2, 5)
            adverse_weather_days = np.random.randint(20, 120)
            
            # Start date
            start_date = datetime.now() - timedelta(days=np.random.randint(0, 730))
            
            # Calculate expected cost and duration
            expected_cost = base_cost + material_cost + total_labor_cost
            expected_duration = base_duration + permit_days + clearance_days
            
            # Calculate ACTUAL cost and duration (with realistic variations)
            # Factors that increase cost/time
            terrain_factor = 1 + (terrain_difficulty - 5) * 0.05
            weather_factor = 1 + (adverse_weather_days / 365) * 0.3
            vendor_factor = 2 - vendor_quality_score / 10
            regulatory_factor = 1 + ((permit_days + clearance_days) / 180 - 1) * 0.2
            
            # Random variation
            random_variation = np.random.uniform(0.9, 1.3)
            
            # Actual cost
            actual_cost = expected_cost * terrain_factor * weather_factor * vendor_factor * random_variation
            
            # Actual duration
            actual_duration = int(expected_duration * terrain_factor * weather_factor * vendor_factor * random_variation)
            
            # Cost and time overruns
            cost_overrun_pct = (actual_cost - expected_cost) / expected_cost
            time_overrun_pct = (actual_duration - expected_duration) / expected_duration
            
            # Project complexity score
            complexity_score = (
                (voltage_level / 765) * 0.3 +
                (terrain_difficulty / 10) * 0.3 +
                (length_km / 100) * 0.2 +
                (num_towers / 500) * 0.2
            )
            
            project = {
                'project_id': f'PG_{region[:2].upper()}_{i+1:04d}',
                'project_name': f'{project_type} Project {region} {i+1}',
                'project_type': project_type,
                'region': region,
                'terrain_type': terrain,
                'terrain_difficulty_score': round(terrain_difficulty, 2),
                
                # Technical specs
                'length_km': round(length_km, 2),
                'voltage_level_kv': voltage_level,
                'num_towers': num_towers,
                
                # Cost components
                'estimated_cost_inr': round(expected_cost, 2),
                'material_cost_inr': round(material_cost, 2),
                'labor_cost_inr': round(total_labor_cost, 2),
                'actual_cost_inr': round(actual_cost, 2),
                
                # Material details
                'steel_cost_per_ton': round(steel_cost_per_ton, 2),
                'copper_cost_per_ton': round(copper_cost_per_ton, 2),
                'total_steel_tons': round(total_steel_tons, 2),
                'total_copper_tons': round(total_copper_tons, 2),
                
                # Timeline
                'estimated_duration_days': expected_duration,
                'permit_approval_days': permit_days,
                'environmental_clearance_days': clearance_days,
                'actual_duration_days': actual_duration,
                'start_date': start_date.strftime('%Y-%m-%d'),
                
                # Resources
                'estimated_manpower': estimated_manpower,
                'labor_cost_per_day': round(labor_cost_per_person_day, 2),
                
                # Vendor metrics
                'vendor_id': f'V_{np.random.randint(1, 51):03d}',
                'vendor_quality_score': round(vendor_quality_score, 2),
                'vendor_on_time_rate': round(vendor_on_time_rate, 3),
                'vendor_cost_efficiency': round(vendor_cost_efficiency, 3),
                
                # Weather
                'monsoon_affected_months': monsoon_months,
                'adverse_weather_days': adverse_weather_days,
                
                # Calculated metrics
                'project_complexity_score': round(complexity_score, 3),
                'cost_overrun_percentage': round(cost_overrun_pct * 100, 2),
                'time_overrun_percentage': round(time_overrun_pct * 100, 2),
                
                # Status
                'status': random.choice(['Completed', 'Ongoing', 'Planned']) if i < 400 else 'Planned'
            }
            
            data.append(project)
        
        return pd.DataFrame(data)
    
    def generate_and_save(self, output_path='data/raw/projects_data.csv'):
        """Generate and save dataset"""
        print(f"Generating {self.n_projects} synthetic projects...")
        df = self.generate_projects()
        
        # Save
        df.to_csv(output_path, index=False)
        print(f"✅ Data saved to {output_path}")
        print(f"Shape: {df.shape}")
        print(f"\nSample statistics:")
        print(f"Average Cost Overrun: {df['cost_overrun_percentage'].mean():.2f}%")
        print(f"Average Time Overrun: {df['time_overrun_percentage'].mean():.2f}%")
        print(f"\nProject Type Distribution:")
        print(df['project_type'].value_counts())
        
        return df

# Generate data
if __name__ == "__main__":
    generator = SyntheticDataGenerator(n_projects=500)
    df = generator.generate_and_save()