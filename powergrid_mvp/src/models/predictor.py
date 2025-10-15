import joblib
import numpy as np
import pandas as pd
from typing import Dict, List
import os
import json

class ProjectPredictor:
    """Make predictions on new projects"""
    
    def __init__(self, models_path=None):
        if models_path is None:
            # Use absolute path to the main models directory (not src/models)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.models_path = os.path.join(base_dir, 'models') + os.sep
        else:
            self.models_path = models_path
        self.cost_models = {}
        self.time_models = {}
        self.preprocessor = None
        self.feature_names = []
        
    def load_models(self):
        """Load all trained models"""
        # Load preprocessor
        prep_data = joblib.load(f'{self.models_path}preprocessor.pkl')
        self.preprocessor = prep_data
        
        # Load cost models
        for model_name in ['xgboost', 'lightgbm', 'random_forest']:
            path = f'{self.models_path}cost_{model_name}.pkl'
            if os.path.exists(path):
                self.cost_models[model_name] = joblib.load(path)
        
        # Load time models
        for model_name in ['xgboost', 'lightgbm', 'random_forest']:
            path = f'{self.models_path}time_{model_name}.pkl'
            if os.path.exists(path):
                self.time_models[model_name] = joblib.load(path)
        
        # Load feature names
        feature_names_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed', 'feature_names.txt')
        with open(feature_names_path, 'r') as f:
            self.feature_names = [line.strip() for line in f]
        
        print(f"✅ Loaded {len(self.cost_models)} cost models and {len(self.time_models)} time models")
    
    def preprocess_input(self, project_data: Dict) -> np.ndarray:
        """Preprocess input data"""
        
        # Convert to DataFrame
        df = pd.DataFrame([project_data])
        
        # Create derived features (same as training)
        df['cost_per_km'] = df['estimated_cost_inr'] / (df['length_km'] + 1)
        df['duration_per_km'] = df['estimated_duration_days'] / (df['length_km'] + 1)
        df['manpower_intensity'] = df['estimated_manpower'] / (df['estimated_duration_days'] + 1)
        df['material_to_total_cost_ratio'] = df['material_cost_inr'] / (df['estimated_cost_inr'] + 1)
        df['labor_to_total_cost_ratio'] = df['labor_cost_inr'] / (df['estimated_cost_inr'] + 1)
        df['regulatory_delay_days'] = df['permit_approval_days'] + df['environmental_clearance_days']
        df['weather_impact_ratio'] = df['adverse_weather_days'] / (df['estimated_duration_days'] + 1)
        df['vendor_reliability_score'] = (
            df['vendor_quality_score'] * 0.4 +
            df['vendor_on_time_rate'] * 10 * 0.3 +
            df['vendor_cost_efficiency'] * 10 * 0.3
        )
        df['complexity_terrain_interaction'] = df['project_complexity_score'] * df['terrain_difficulty_score']
        df['weather_terrain_interaction'] = df['weather_impact_ratio'] * df['terrain_difficulty_score']
        
        # Date features
        if 'start_date' in df.columns:
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['start_month'] = df['start_date'].dt.month
            df['start_quarter'] = df['start_date'].dt.quarter
            df['is_monsoon_start'] = df['start_month'].apply(lambda x: 1 if x in [6,7,8,9] else 0)
        
        # Encode categoricals
        if self.preprocessor and 'label_encoders' in self.preprocessor:
            for col, encoder in self.preprocessor['label_encoders'].items():
                if col in df.columns:
                    df[f'{col}_encoded'] = encoder.transform(df[col].astype(str))
        
        # Select features
        X = df[self.feature_names].fillna(0)
        
        # Scale
        if self.preprocessor and 'scaler' in self.preprocessor:
            X_scaled = self.preprocessor['scaler'].transform(X)
        else:
            X_scaled = X.values
            
        # Ensure we return a numpy array
        return np.array(X_scaled)
    
    def predict(self, project_data: Dict) -> Dict:
        """Make prediction for a single project"""
        
        # Preprocess
        X = self.preprocess_input(project_data)
        
        # Ensemble predictions for cost
        cost_predictions = []
        for model in self.cost_models.values():
            pred = model.predict(X)[0]
            cost_predictions.append(pred)
        
        cost_overrun_pct = np.mean(cost_predictions)
        
        # Ensemble predictions for time
        time_predictions = []
        for model in self.time_models.values():
            pred = model.predict(X)[0]
            time_predictions.append(pred)
        
        time_overrun_pct = np.mean(time_predictions)
        
        # Calculate predicted values
        estimated_cost = project_data.get('estimated_cost_inr', 0)
        estimated_duration = project_data.get('estimated_duration_days', 0)
        
        predicted_cost = estimated_cost * (1 + cost_overrun_pct / 100)
        predicted_duration = estimated_duration * (1 + time_overrun_pct / 100)
        
        # Risk score
        risk_score = (abs(cost_overrun_pct) * 0.5 + abs(time_overrun_pct) * 0.5) / 100
        
        # Risk category
        if risk_score > 0.3:
            risk_category = "High"
            priority = "🔴 Critical"
        elif risk_score > 0.15:
            risk_category = "Medium"
            priority = "🟡 Monitor"
        else:
            risk_category = "Low"
            priority = "🟢 On Track"
        
        return {
            'project_id': project_data.get('project_id', 'N/A'),
            'estimated_cost_inr': estimated_cost,
            'predicted_cost_inr': round(predicted_cost, 2),
            'cost_overrun_percentage': round(cost_overrun_pct, 2),
            'cost_overrun_inr': round(predicted_cost - estimated_cost, 2),
            
            'estimated_duration_days': estimated_duration,
            'predicted_duration_days': int(predicted_duration),
            'time_overrun_percentage': round(time_overrun_pct, 2),
            'time_overrun_days': int(predicted_duration - estimated_duration),
            
            'risk_score': round(risk_score, 3),
            'risk_category': risk_category,
            'priority': priority
        }
    
    def batch_predict(self, projects_list: List[Dict]) -> List[Dict]:
        """Make predictions for multiple projects"""
        results = []
        
        for project in projects_list:
            try:
                result = self.predict(project)
                results.append(result)
            except Exception as e:
                print(f"Error predicting for project {project.get('project_id')}: {e}")
                results.append({
                    'project_id': project.get('project_id'),
                    'error': str(e)
                })
        
        return results

# Test the predictor
if __name__ == "__main__":
    predictor = ProjectPredictor()
    predictor.load_models()
    
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
        'start_date': '2024-01-15',
        'start_month': 1,
        'start_quarter': 1,
        'is_monsoon_start': 0
    }
    
    result = predictor.predict(sample_project)
    print("Prediction result:", result)