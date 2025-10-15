import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.models.powergrid_ml import PowerGridMLModel
import numpy as np

def test_powergrid_ml():
    print("Testing PowerGridMLModel...")
    
    # Initialize model
    ml_model = PowerGridMLModel()
    
    # Load models
    print("Loading models...")
    try:
        ml_model.load_models()
        print(f"Loaded {len(ml_model.cost_models)} cost models and {len(ml_model.time_models)} time models")
        
        # Test with sample data (this should be preprocessed features)
        # For now, let's create a simple test array
        X_test = np.random.rand(1, 36)  # 36 features based on feature_names.txt
        
        print("Testing cost prediction with uncertainty...")
        cost_pred = ml_model.predict_with_uncertainty(X_test, 'cost')
        print("Cost prediction result:", cost_pred)
        
        print("Testing time prediction with uncertainty...")
        time_pred = ml_model.predict_with_uncertainty(X_test, 'time')
        print("Time prediction result:", time_pred)
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_powergrid_ml()