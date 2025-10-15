import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import joblib
import os
import json
import warnings
warnings.filterwarnings('ignore')

class PowerGridMLModel:
    """
    Advanced ML models for POWERGRID project cost and timeline prediction
    Implements ensemble methods, stacking, and domain-specific optimizations
    """
    
    def __init__(self, models_path=None):
        if models_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.models_path = os.path.join(base_dir, 'models') + os.sep
        else:
            self.models_path = models_path
            
        self.cost_models = {}
        self.time_models = {}
        self.ensemble_models = {}
        self.meta_models = {}
        self.feature_importance = {}
        self.model_performance = {}
        
    def create_ensemble_models(self, X_train, y_train, model_type='cost'):
        """
        Create ensemble models using stacking and voting
        """
        print(f"🎯 Creating ensemble models for {model_type} prediction...")
        
        # Base models with different strengths
        base_models = [
            ('xgb', xgb.XGBRegressor(
                n_estimators=200, max_depth=8, learning_rate=0.1,
                subsample=0.8, colsample_bytree=0.8, random_state=42
            )),
            ('lgb', lgb.LGBMRegressor(
                n_estimators=200, max_depth=8, learning_rate=0.1,
                subsample=0.8, colsample_bytree=0.8, random_state=42
            )),
            ('cb', cb.CatBoostRegressor(
                iterations=200, depth=8, learning_rate=0.1,
                random_state=42, verbose=False
            )),
            ('rf', RandomForestRegressor(
                n_estimators=200, max_depth=15, random_state=42
            )),
            ('gb', GradientBoostingRegressor(
                n_estimators=200, max_depth=8, random_state=42
            )),
            ('ridge', Ridge(alpha=1.0)),
            ('lasso', Lasso(alpha=0.1)),
            ('elastic', ElasticNet(alpha=0.1, l1_ratio=0.5))
        ]
        
        # Train base models
        base_predictions = np.zeros((X_train.shape[0], len(base_models)))
        
        for i, (name, model) in enumerate(base_models):
            print(f"  Training {name}...")
            model.fit(X_train, y_train)
            base_predictions[:, i] = model.predict(X_train)
            
            if model_type == 'cost':
                self.cost_models[name] = model
            else:
                self.time_models[name] = model
        
        # Create voting ensemble (simple average)
        voting_ensemble = VotingRegressor(estimators=base_models[:4])  # Use top 4 models
        voting_ensemble.fit(X_train, y_train)
        
        # Create stacking ensemble
        meta_model = Ridge(alpha=0.1)
        meta_model.fit(base_predictions, y_train)
        
        if model_type == 'cost':
            self.ensemble_models['cost_voting'] = voting_ensemble
            self.meta_models['cost_stacking'] = meta_model
        else:
            self.ensemble_models['time_voting'] = voting_ensemble
            self.meta_models['time_stacking'] = meta_model
        
        print(f"✅ Ensemble models created for {model_type}")
        
    def hyperparameter_tuning(self, X_train, y_train, model_name='xgb'):
        """
        Perform hyperparameter tuning for optimal performance
        """
        print(f"🔧 Hyperparameter tuning for {model_name}...")
        
        if model_name == 'xgb':
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [6, 8, 10],
                'learning_rate': [0.05, 0.1, 0.15],
                'subsample': [0.7, 0.8, 0.9],
                'colsample_bytree': [0.7, 0.8, 0.9]
            }
            model = xgb.XGBRegressor(random_state=42)
            
        elif model_name == 'lgb':
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [6, 8, 10],
                'learning_rate': [0.05, 0.1, 0.15],
                'subsample': [0.7, 0.8, 0.9],
                'colsample_bytree': [0.7, 0.8, 0.9]
            }
            model = lgb.LGBMRegressor(random_state=42)
            
        elif model_name == 'cb':
            param_grid = {
                'iterations': [100, 200, 300],
                'depth': [6, 8, 10],
                'learning_rate': [0.05, 0.1, 0.15]
            }
            model = cb.CatBoostRegressor(random_state=42, verbose=False)
        
        # Time series cross-validation for temporal data
        tscv = TimeSeriesSplit(n_splits=5)
        
        grid_search = GridSearchCV(
            model, param_grid, cv=tscv, 
            scoring='neg_mean_absolute_error',
            n_jobs=-1, verbose=0
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"✅ Best parameters for {model_name}: {grid_search.best_params_}")
        print(f"✅ Best CV score: {-grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def train_domain_specific_models(self, X_train, y_train, X_val, y_val, model_type='cost'):
        """
        Train models with domain-specific optimizations
        """
        print(f"🏗️ Training domain-specific models for {model_type}...")
        
        # Feature importance-based model selection
        if model_type == 'cost':
            # Cost models should focus on material, labor, and market factors
            feature_weights = {
                'material_cost_ratio': 2.0,
                'labor_cost_ratio': 1.8,
                'demand_supply_impact': 1.5,
                'cost_escalation_risk': 1.7,
                'vendor_cost_efficiency': 1.3
            }
        else:
            # Time models should focus on regulatory, weather, and complexity factors
            feature_weights = {
                'regulatory_complexity_score': 2.0,
                'monsoon_impact_score': 1.8,
                'timeline_pressure_score': 1.6,
                'critical_path_risk': 1.5,
                'weather_impact_ratio': 1.4
            }
        
        # Train individual models with hyperparameter tuning
        model_configs = {
            'xgb': self.hyperparameter_tuning(X_train, y_train, 'xgb'),
            'lgb': self.hyperparameter_tuning(X_train, y_train, 'lgb'),
            'cb': self.hyperparameter_tuning(X_train, y_train, 'cb')
        }
        
        # Evaluate and select best models
        best_models = {}
        
        for name, model in model_configs.items():
            # Validation performance
            val_pred = model.predict(X_val)
            val_mae = mean_absolute_error(y_val, val_pred)
            val_r2 = r2_score(y_val, val_pred)
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            
            print(f"  {name} - MAE: {val_mae:.4f}, R²: {val_r2:.4f}, RMSE: {val_rmse:.4f}")
            
            best_models[name] = {
                'model': model,
                'mae': val_mae,
                'r2': val_r2,
                'rmse': val_rmse
            }
            
            if model_type == 'cost':
                self.cost_models[name] = model
            else:
                self.time_models[name] = model
        
        # Store performance metrics
        self.model_performance[model_type] = best_models
        
        print(f"✅ Domain-specific models trained for {model_type}")
        
    def train_models(self, X_train, y_train_cost, y_train_time, X_val, y_val_cost, y_val_time):
        """
        Complete training pipeline for both cost and time models
        """
        print("🚀 Starting comprehensive model training...")
        
        # Train cost prediction models
        self.train_domain_specific_models(
            X_train, y_train_cost, X_val, y_val_cost, model_type='cost'
        )
        
        # Train time prediction models
        self.train_domain_specific_models(
            X_train, y_train_time, X_val, y_val_time, model_type='time'
        )
        
        # Create ensemble models
        self.create_ensemble_models(X_train, y_train_cost, model_type='cost')
        self.create_ensemble_models(X_train, y_train_time, model_type='time')
        
        print("✅ All models trained successfully!")
        
    def predict_with_uncertainty(self, X_test, model_type='cost', confidence_level=0.95):
        """
        Make predictions with uncertainty quantification
        """
        models = self.cost_models if model_type == 'cost' else self.time_models
        
        predictions = []
        for name, model in models.items():
            pred = model.predict(X_test)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Mean prediction
        mean_pred = np.mean(predictions, axis=0)
        
        # Uncertainty (standard deviation)
        std_pred = np.std(predictions, axis=0)
        
        # Confidence intervals
        z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%
        lower_bound = mean_pred - z_score * std_pred
        upper_bound = mean_pred + z_score * std_pred
        
        return {
            'predictions': mean_pred,
            'uncertainty': std_pred,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence_level': confidence_level
        }
    
    def analyze_feature_importance(self, X_train, feature_names):
        """
        Analyze feature importance across all models
        """
        print("🔍 Analyzing feature importance...")
        
        importance_data = {}
        
        # Analyze for cost models
        cost_importance = {}
        for name, model in self.cost_models.items():
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_)
            else:
                continue
                
            cost_importance[name] = dict(zip(feature_names, importance))
        
        # Analyze for time models
        time_importance = {}
        for name, model in self.time_models.items():
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_)
            else:
                continue
                
            time_importance[name] = dict(zip(feature_names, importance))
        
        self.feature_importance = {
            'cost_features': cost_importance,
            'time_features': time_importance
        }
        
        print("✅ Feature importance analysis completed")
        
    def save_models(self):
        """
        Save all trained models and artifacts
        """
        print("💾 Saving models and artifacts...")
        
        # Save individual models
        for name, model in self.cost_models.items():
            joblib.dump(model, f'{self.models_path}cost_{name}.pkl')
        
        for name, model in self.time_models.items():
            joblib.dump(model, f'{self.models_path}time_{name}.pkl')
        
        # Save ensemble models
        for name, model in self.ensemble_models.items():
            joblib.dump(model, f'{self.models_path}{name}.pkl')
        
        # Save meta models
        for name, model in self.meta_models.items():
            joblib.dump(model, f'{self.models_path}{name}.pkl')
        
        # Save feature importance
        with open(f'{self.models_path}feature_importance.json', 'w') as f:
            json.dump(self.feature_importance, f, indent=2)
        
        # Save model performance metrics
        with open(f'{self.models_path}metrics.json', 'w') as f:
            json.dump(self.model_performance, f, indent=2)
        
        print("✅ All models and artifacts saved successfully!")
        
    def load_models(self):
        """
        Load trained models
        """
        print("📂 Loading trained models...")
        
        # Load cost models
        cost_model_files = ['cost_xgboost.pkl', 'cost_lightgbm.pkl', 'cost_random_forest.pkl']
        for file in cost_model_files:
            if os.path.exists(f'{self.models_path}{file}'):
                name = file.replace('cost_', '').replace('.pkl', '')
                self.cost_models[name] = joblib.load(f'{self.models_path}{file}')
        
        # Load time models
        time_model_files = ['time_xgboost.pkl', 'time_lightgbm.pkl', 'time_random_forest.pkl']
        for file in time_model_files:
            if os.path.exists(f'{self.models_path}{file}'):
                name = file.replace('time_', '').replace('.pkl', '')
                self.time_models[name] = joblib.load(f'{self.models_path}{file}')
        
        # Load feature importance
        if os.path.exists(f'{self.models_path}feature_importance.json'):
            with open(f'{self.models_path}feature_importance.json', 'r') as f:
                self.feature_importance = json.load(f)
        
        print(f"✅ Loaded {len(self.cost_models)} cost models and {len(self.time_models)} time models")

# Example usage
if __name__ == "__main__":
    # Initialize and train models
    ml_model = PowerGridMLModel()
    
    # Example data loading and training
    # This would be integrated with the preprocessing pipeline
    print("POWERGRID ML Model ready for training!")