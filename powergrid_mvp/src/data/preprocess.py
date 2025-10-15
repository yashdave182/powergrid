import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

class DataPreprocessor:
    """Preprocess data for model training"""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def load_data(self, filepath='data/raw/projects_data.csv'):
        """Load raw data"""
        df = pd.read_csv(filepath)
        print(f"✅ Loaded data: {df.shape}")
        return df
    
    def create_features(self, df):
        """Engineer features"""
        df = df.copy()
        
        # Date features
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['start_year'] = df['start_date'].dt.year
        df['start_month'] = df['start_date'].dt.month
        df['start_quarter'] = df['start_date'].dt.quarter
        df['is_monsoon_start'] = df['start_month'].apply(lambda x: 1 if x in [6,7,8,9] else 0)
        
        # Derived features
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
        
        # Interaction features
        df['complexity_terrain_interaction'] = df['project_complexity_score'] * df['terrain_difficulty_score']
        df['weather_terrain_interaction'] = df['weather_impact_ratio'] * df['terrain_difficulty_score']
        
        return df
    
    def encode_categorical(self, df, cat_columns=['project_type', 'region', 'terrain_type']):
        """Encode categorical variables"""
        df = df.copy()
        
        for col in cat_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        return df
    
    def prepare_train_test(self, df, test_size=0.2):
        """Prepare training and testing sets"""
        
        # Only use completed/ongoing projects for training
        train_df = df[df['status'].isin(['Completed', 'Ongoing'])].copy()
        
        # Features for modeling
        feature_cols = [
            # Basic features
            'length_km', 'voltage_level_kv', 'terrain_difficulty_score',
            'num_towers', 'estimated_cost_inr', 'estimated_duration_days',
            
            # Material costs
            'steel_cost_per_ton', 'copper_cost_per_ton',
            'total_steel_tons', 'total_copper_tons',
            
            # Resources
            'estimated_manpower', 'labor_cost_per_day',
            
            # Vendor
            'vendor_quality_score', 'vendor_on_time_rate', 'vendor_cost_efficiency',
            'vendor_reliability_score',
            
            # Weather & Regulatory
            'adverse_weather_days', 'monsoon_affected_months',
            'permit_approval_days', 'environmental_clearance_days',
            'regulatory_delay_days',
            
            # Derived features
            'project_complexity_score', 'cost_per_km', 'duration_per_km',
            'manpower_intensity', 'material_to_total_cost_ratio',
            'labor_to_total_cost_ratio', 'weather_impact_ratio',
            'complexity_terrain_interaction', 'weather_terrain_interaction',
            
            # Encoded categoricals
            'project_type_encoded', 'region_encoded', 'terrain_type_encoded',
            
            # Date features
            'start_month', 'start_quarter', 'is_monsoon_start'
        ]
        
        # Target variables
        target_cost = 'cost_overrun_percentage'
        target_time = 'time_overrun_percentage'
        
        # Remove any rows with missing targets
        train_df = train_df.dropna(subset=[target_cost, target_time])
        
        # Get available feature columns
        available_features = [col for col in feature_cols if col in train_df.columns]
        
        X = train_df[available_features].fillna(0)
        y_cost = train_df[target_cost]
        y_time = train_df[target_time]
        
        # Split
        from sklearn.model_selection import train_test_split
        
        X_train, X_test, y_cost_train, y_cost_test, y_time_train, y_time_test = train_test_split(
            X, y_cost, y_time, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert back to DataFrame to preserve column names
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=available_features, index=X_train.index)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=available_features, index=X_test.index)
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_cost_train': y_cost_train,
            'y_cost_test': y_cost_test,
            'y_time_train': y_time_train,
            'y_time_test': y_time_test,
            'feature_names': available_features
        }
    
    def save_preprocessor(self, path='models/preprocessor.pkl'):
        """Save preprocessor objects"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'scaler': self.scaler,
            'label_encoders': self.label_encoders
        }, path)
        print(f"✅ Preprocessor saved to {path}")
    
    def load_preprocessor(self, path='models/preprocessor.pkl'):
        """Load preprocessor objects"""
        objects = joblib.load(path)
        self.scaler = objects['scaler']
        self.label_encoders = objects['label_encoders']
        print(f"✅ Preprocessor loaded from {path}")

# Main execution
if __name__ == "__main__":
    # Initialize
    preprocessor = DataPreprocessor()
    
    # Load data
    df = preprocessor.load_data()
    
    # Create features
    df = preprocessor.create_features(df)
    
    # Encode categoricals
    df = preprocessor.encode_categorical(df)
    
    # Save processed data
    df.to_csv('data/processed/processed_data.csv', index=False)
    print(f"✅ Processed data saved")
    
    # Prepare train/test
    data_dict = preprocessor.prepare_train_test(df)
    
    # Save preprocessor
    preprocessor.save_preprocessor()
    
    # Save train/test sets
    np.save('data/processed/X_train.npy', data_dict['X_train'].values)
    np.save('data/processed/X_test.npy', data_dict['X_test'].values)
    np.save('data/processed/y_cost_train.npy', data_dict['y_cost_train'].values)
    np.save('data/processed/y_cost_test.npy', data_dict['y_cost_test'].values)
    np.save('data/processed/y_time_train.npy', data_dict['y_time_train'].values)
    np.save('data/processed/y_time_test.npy', data_dict['y_time_test'].values)
    
    # Save feature names
    with open('data/processed/feature_names.txt', 'w') as f:
        f.write('\n'.join(data_dict['feature_names']))
    
    print(f"\n📊 Data Summary:")
    print(f"Training samples: {len(data_dict['X_train'])}")
    print(f"Testing samples: {len(data_dict['X_test'])}")
    print(f"Number of features: {len(data_dict['feature_names'])}")