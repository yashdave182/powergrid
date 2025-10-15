import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.predictor import ProjectPredictor
import pandas as pd
import numpy as np

def test_data_generation():
    """Test if synthetic data was generated correctly"""
    print("🧪 Testing data generation...")
    
    df = pd.read_csv('data/raw/projects_data.csv')
    
    assert len(df) > 0, "Data should not be empty"
    assert 'project_id' in df.columns, "Should have project_id column"
    assert 'cost_overrun_percentage' in df.columns, "Should have cost_overrun_percentage"
    
    print("✅ Data generation test passed")

def test_preprocessing():
    """Test if preprocessing works"""
    print("\n🧪 Testing preprocessing...")
    
    df = pd.read_csv('data/processed/processed_data.csv')
    
    assert 'cost_per_km' in df.columns, "Should have derived features"
    assert 'project_type_encoded' in df.columns, "Should have encoded features"
    
    print("✅ Preprocessing test passed")

def test_models_exist():
    """Test if models were saved"""
    print("\n🧪 Testing model files...")
    
    assert os.path.exists('models/cost_xgboost.pkl'), "Cost XGBoost model should exist"
    assert os.path.exists('models/time_lightgbm.pkl'), "Time LightGBM model should exist"
    assert os.path.exists('models/preprocessor.pkl'), "Preprocessor should exist"
    
    print("✅ Model files test passed")

def test_prediction():
    """Test if prediction works"""
    print("\n🧪 Testing prediction...")
    
    predictor = ProjectPredictor()
    predictor.load_models()
    
    sample_project = {
        'project_id': 'TEST_001',
        'project_type': 'Overhead Line',
        'region': 'North',
        'terrain_type': 'Hilly',
        'length_km': 150,
        'voltage_level_kv': 400,
        'terrain_difficulty_score': 6.5,
        'num_towers': 300,
        'estimated_cost_inr': 500000000,
        'material_cost_inr': 200000000,
        'labor_cost_inr': 100000000,
        'estimated_duration_days': 450,
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
        'start_date': '2024-01-15',
        'start_month': 1,
        'start_quarter': 1,
        'is_monsoon_start': 0
    }
    
    result = predictor.predict(sample_project)
    
    assert 'predicted_cost_inr' in result, "Should return predicted cost"
    assert 'predicted_duration_days' in result, "Should return predicted duration"
    assert 'risk_score' in result, "Should return risk score"
    assert result['risk_category'] in ['Low', 'Medium', 'High'], "Should have valid risk category"
    
    print(f"  Predicted cost overrun: {result['cost_overrun_percentage']:.2f}%")
    print(f"  Predicted time overrun: {result['time_overrun_percentage']:.2f}%")
    print(f"  Risk category: {result['risk_category']}")
    
    print("✅ Prediction test passed")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RUNNING MVP TESTS")
    print("=" * 60)
    
    try:
        test_data_generation()
        test_preprocessing()
        test_models_exist()
        test_prediction()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()