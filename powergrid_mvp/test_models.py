import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.models.predictor import ProjectPredictor

def test_models():
    print("Testing ML models...")
    
    # Initialize predictor
    predictor = ProjectPredictor()
    
    # Load models
    print("Loading models...")
    predictor.load_models()
    print(f"Loaded {len(predictor.cost_models)} cost models and {len(predictor.time_models)} time models")
    
    # Test with sample data
    sample_project = {
        'project_id': 'TEST_001',
        'length_km': 150,
        'voltage_level_kv': 400,
        'terrain_difficulty_score': 6.5,
        'num_towers': 300,
        'estimated_cost_inr': 500000000,
        'estimated_duration_days': 450,
        'material_cost_inr': 200000000,
        'labor_cost_inr': 100000000,
        'steel_cost_per_ton': 65000,
        'copper_cost_per_ton': 800000,
        'total_steel_tons': 2000,
        'total_copper_tons': 300,
        'estimated_manpower': 5000,
        'labor_cost_per_day': 800,
        'vendor_quality_score': 7.5,
        'vendor_on_time_rate': 0.85,
        'vendor_cost_efficiency': 0.90,
        'adverse_weather_days': 60,
        'monsoon_affected_months': 3,
        'permit_approval_days': 90,
        'environmental_clearance_days': 120,
        'project_complexity_score': 0.65,
        'project_type': 'Overhead Line',
        'region': 'North',
        'terrain_type': 'Hilly',
        'start_date': '2024-01-15'
    }
    
    print("Making prediction...")
    result = predictor.predict(sample_project)
    print("Prediction result:", result)
    print("Test completed successfully!")

if __name__ == "__main__":
    test_models()