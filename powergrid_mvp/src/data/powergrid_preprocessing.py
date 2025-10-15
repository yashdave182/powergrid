import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.impute import SimpleImputer, KNNImputer
import os
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class PowerGridPreprocessor:
    """
    Advanced preprocessing pipeline specifically designed for POWERGRID project data
    Handles all project types: substation, overhead line, underground cable
    """
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        self.feature_importance = {}
        
    def create_powergrid_specific_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create domain-specific features for POWERGRID projects
        """
        df = df.copy()
        
        # 1. Project Type Specific Features
        df['is_overhead_line'] = (df['project_type'] == 'Overhead Line').astype(int)
        df['is_underground_cable'] = (df['project_type'] == 'Underground Cable').astype(int)
        df['is_substation'] = (df['project_type'] == 'Substation').astype(int)
        
        # 2. Terrain and Environmental Impact Scoring
        df['terrain_environmental_risk'] = (
            df['terrain_difficulty_score'] * 0.4 +
            df['environmental_sensitivity_score'] * 0.3 +
            df['altitude_meters'] / 1000 * 0.3
        )
        
        # 3. Cost Intensity Metrics
        df['cost_per_km_by_voltage'] = df['estimated_cost_inr'] / (df['length_km'] * df['voltage_level_kv'] / 100 + 1)
        df['material_cost_ratio'] = df['material_cost_inr'] / (df['estimated_cost_inr'] + 1)
        df['labor_cost_ratio'] = df['labor_cost_inr'] / (df['estimated_cost_inr'] + 1)
        df['equipment_cost_ratio'] = df['equipment_cost_inr'] / (df['estimated_cost_inr'] + 1)
        
        # 4. Timeline Pressure Indicators
        df['timeline_pressure_score'] = (
            df['estimated_duration_days'] / (df['length_km'] + 1) * 0.3 +
            df['regulatory_requirements_count'] * 5 * 0.4 +
            df['stakeholder_count'] * 2 * 0.3
        )
        
        # 5. Weather and Seasonal Impact
        df['monsoon_impact_score'] = (
            df['monsoon_affected_months'] * 10 * 0.4 +
            df['adverse_weather_days'] * 0.3 +
            df['extreme_weather_events'] * 15 * 0.3
        )
        
        # 6. Vendor and Supply Chain Risk
        df['supply_chain_risk_score'] = (
            (10 - df['vendor_reliability_score']) * 0.3 +
            df['material_lead_time_days'] * 0.01 * 0.4 +
            df['single_source_vendors'] * 20 * 0.3
        )
        
        # 7. Regulatory and Permitting Complexity
        df['regulatory_complexity_score'] = (
            df['permit_approval_days'] * 0.01 * 0.3 +
            df['environmental_clearance_days'] * 0.01 * 0.3 +
            df['land_acquisition_days'] * 0.01 * 0.2 +
            df['forest_clearance_days'] * 0.01 * 0.2
        )
        
        # 8. Resource Availability and Manpower
        df['resource_constraint_score'] = (
            df['skilled_manpower_shortage'] * 15 * 0.4 +
            df['equipment_availability_score'] * 0.3 +
            df['remote_location_factor'] * 10 * 0.3
        )
        
        # 9. Demand-Supply Impact
        df['demand_supply_impact'] = (
            df['material_demand_supply_gap'] * 20 * 0.5 +
            df['market_volatility_index'] * 0.4 +
            df['currency_fluctuation_impact'] * 5 * 0.1
        )
        
        # 10. Historical Delay Patterns
        df['historical_delay_risk'] = (
            df['similar_project_delays_avg'] * 0.4 +
            df['regional_delay_factor'] * 10 * 0.3 +
            df['contractor_past_performance'] * 0.3
        )
        
        # 11. Regional and Geographic Factors
        df['regional_risk_multiplier'] = (
            df['naxal_affected_area'] * 25 * 0.4 +
            df['flood_prone_area'] * 15 * 0.3 +
            df['earthquake_zone_factor'] * 10 * 0.3
        )
        
        # 12. Project Complexity Interactions
        df['complexity_terrain_weather'] = (
            df['project_complexity_score'] * 
            df['terrain_difficulty_score'] * 
            df['weather_impact_ratio']
        )
        
        df['complexity_regulatory'] = (
            df['project_complexity_score'] * 
            df['regulatory_requirements_count'] * 0.1
        )
        
        # 13. Cost Escalation Risk Factors
        df['cost_escalation_risk'] = (
            df['inflation_rate'] * 10 * 0.3 +
            df['material_price_volatility'] * 15 * 0.4 +
            df['fuel_price_impact'] * 8 * 0.3
        )
        
        # 14. Critical Path Risk Indicators
        df['critical_path_risk'] = (
            df['critical_activities_count'] * 5 * 0.4 +
            df['parallel_activities_risk'] * 8 * 0.3 +
            df['dependency_count'] * 3 * 0.3
        )
        
        # 15. Technology and Innovation Factors
        df['technology_risk_score'] = (
            df['new_technology_adoption'] * 20 * 0.5 +
            df['equipment_modernization_score'] * 0.2 +
            df['digital_integration_complexity'] * 12 * 0.3
        )
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Advanced missing value handling for POWERGRID data
        """
        df = df.copy()
        
        # Separate numerical and categorical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # For numerical columns, use KNN imputation for better accuracy
        if numerical_cols:
            knn_imputer = KNNImputer(n_neighbors=5, weights='distance')
            df[numerical_cols] = knn_imputer.fit_transform(df[numerical_cols])
            self.imputers['numerical'] = knn_imputer
        
        # For categorical columns, use mode imputation or domain knowledge
        for col in categorical_cols:
            if col in ['project_type', 'region', 'terrain_type']:
                # Use domain knowledge for critical fields
                if col == 'project_type':
                    df[col].fillna('Overhead Line', inplace=True)
                elif col == 'region':
                    df[col].fillna('North', inplace=True)
                elif col == 'terrain_type':
                    df[col].fillna('Plain', inplace=True)
            else:
                # Use mode for other categoricals
                mode_imputer = SimpleImputer(strategy='most_frequent')
                df[col] = mode_imputer.fit_transform(df[[col]]).ravel()
                self.imputers[f'categorical_{col}'] = mode_imputer
        
        return df
    
    def encode_categorical_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Advanced categorical encoding for POWERGRID data
        """
        df = df.copy()
        
        # High-cardinality categorical features
        high_cardinality_cols = ['contractor_name', 'vendor_name', 'project_location']
        
        for col in high_cardinality_cols:
            if col in df.columns:
                # Target encoding for high-cardinality features
                if 'cost_overrun_percentage' in df.columns:
                    target_mean = df.groupby(col)['cost_overrun_percentage'].mean()
                    df[f'{col}_encoded'] = df[col].map(target_mean)
                else:
                    # Frequency encoding if target not available
                    freq_encoding = df[col].value_counts()
                    df[f'{col}_encoded'] = df[col].map(freq_encoding)
                
                # Store encoder
                self.encoders[col] = target_mean if 'cost_overrun_percentage' in df.columns else freq_encoding
        
        # Ordinal encoding for ordered categories
        ordinal_mappings = {
            'complexity_level': {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4},
            'risk_category': {'Low': 1, 'Medium': 2, 'High': 3},
            'terrain_difficulty': {'Plain': 1, 'Rolling': 2, 'Hilly': 3, 'Mountainous': 4}
        }
        
        for col, mapping in ordinal_mappings.items():
            if col in df.columns:
                df[f'{col}_encoded'] = df[col].map(mapping)
                self.encoders[col] = mapping
        
        # One-hot encoding for remaining categoricals
        remaining_categoricals = [col for col in df.select_dtypes(include=['object']).columns 
                                 if col not in high_cardinality_cols + list(ordinal_mappings.keys())]
        
        if remaining_categoricals:
            df_encoded = pd.get_dummies(df[remaining_categoricals], prefix=remaining_categoricals)
            df = df.drop(columns=remaining_categoricals)
            df = pd.concat([df, df_encoded], axis=1)
        
        return df
    
    def scale_features(self, df: pd.DataFrame, target_cols: List[str] = None) -> pd.DataFrame:
        """
        Advanced feature scaling with different strategies
        """
        df = df.copy()
        
        if target_cols is None:
            # Auto-detect numerical columns that need scaling
            target_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                          if not col.endswith('_encoded') and col not in ['cost_overrun_percentage', 'time_overrun_percentage']]
        
        # Use RobustScaler for features with outliers
        robust_scaler = RobustScaler()
        df[target_cols] = robust_scaler.fit_transform(df[target_cols])
        self.scalers['robust'] = robust_scaler
        
        return df
    
    def create_target_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create target variables for cost and timeline prediction
        """
        df = df.copy()
        
        # Cost overrun percentage
        if 'actual_cost_inr' in df.columns and 'estimated_cost_inr' in df.columns:
            df['cost_overrun_percentage'] = ((df['actual_cost_inr'] - df['estimated_cost_inr']) / df['estimated_cost_inr']) * 100
        
        # Time overrun percentage
        if 'actual_duration_days' in df.columns and 'estimated_duration_days' in df.columns:
            df['time_overrun_percentage'] = ((df['actual_duration_days'] - df['estimated_duration_days']) / df['estimated_duration_days']) * 100
        
        # Binary classification targets
        df['cost_overrun_high'] = (df['cost_overrun_percentage'] > 20).astype(int)
        df['time_overrun_high'] = (df['time_overrun_percentage'] > 15).astype(int)
        
        return df
    
    def feature_selection(self, df: pd.DataFrame, target_col: str, top_n: int = 50) -> List[str]:
        """
        Select most important features using correlation and domain knowledge
        """
        if target_col not in df.columns:
            return df.columns.tolist()
        
        # Calculate correlations
        correlations = df.corr()[target_col].abs().sort_values(ascending=False)
        
        # Domain knowledge - important features for POWERGRID
        domain_important = [
            'project_type', 'voltage_level_kv', 'length_km', 'terrain_difficulty_score',
            'estimated_cost_inr', 'estimated_duration_days', 'material_cost_ratio',
            'regulatory_complexity_score', 'weather_impact_score', 'supply_chain_risk_score',
            'monsoon_impact_score', 'historical_delay_risk', 'regional_risk_multiplier'
        ]
        
        # Combine correlation-based and domain-based selection
        correlation_features = correlations.head(top_n).index.tolist()
        
        # Ensure domain important features are included
        selected_features = list(set(correlation_features + domain_important))
        
        # Remove target variable if present
        if target_col in selected_features:
            selected_features.remove(target_col)
        
        return selected_features[:top_n]
    
    def preprocess_powergrid_data(self, input_path: str, output_path: str, 
                                 target_variable: str = 'cost_overrun_percentage') -> Tuple[pd.DataFrame, Dict]:
        """
        Complete preprocessing pipeline for POWERGRID data
        """
        print("🚀 Starting POWERGRID data preprocessing...")
        
        # Load data
        df = pd.read_csv(input_path)
        print(f"📊 Loaded {len(df)} projects with {len(df.columns)} features")
        
        # Create POWERGRID-specific features
        print("🔧 Creating domain-specific features...")
        df = self.create_powergrid_specific_features(df)
        
        # Handle missing values
        print("🔍 Handling missing values...")
        df = self.handle_missing_values(df)
        
        # Create target variables
        print("🎯 Creating target variables...")
        df = self.create_target_variables(df)
        
        # Encode categorical variables
        print("🔤 Encoding categorical variables...")
        df = self.encode_categorical_variables(df)
        
        # Feature selection
        print("🎛️ Selecting important features...")
        selected_features = self.feature_selection(df, target_variable)
        df_selected = df[selected_features + [target_variable]]
        
        # Scale features
        print("⚖️ Scaling features...")
        df_scaled = self.scale_features(df_selected)
        
        # Save processed data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_scaled.to_csv(output_path, index=False)
        
        # Save preprocessing artifacts
        artifacts = {
            'scalers': self.scalers,
            'encoders': self.encoders,
            'imputers': self.imputers,
            'selected_features': selected_features,
            'target_variable': target_variable
        }
        
        print(f"✅ Preprocessing completed! Saved {len(df_scaled)} projects with {len(df_scaled.columns)} features")
        
        return df_scaled, artifacts

if __name__ == "__main__":
    preprocessor = PowerGridPreprocessor()
    
    # Process training data
    input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'raw', 'powergrid_projects.csv')
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed', 'powergrid_processed.csv')
    
    processed_data, artifacts = preprocessor.preprocess_powergrid_data(input_path, output_path)
    
    print(f"Processed data shape: {processed_data.shape}")
    print(f"Selected features: {len(artifacts['selected_features'])}")
    print("Sample features:", artifacts['selected_features'][:10])