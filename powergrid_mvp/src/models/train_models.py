import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
import os

class ModelTrainer:
    """Train and evaluate ML models"""
    
    def __init__(self):
        self.cost_models = {}
        self.time_models = {}
        self.metrics = {}
        
    def load_data(self):
        """Load preprocessed data"""
        X_train = np.load('data/processed/X_train.npy')
        X_test = np.load('data/processed/X_test.npy')
        y_cost_train = np.load('data/processed/y_cost_train.npy')
        y_cost_test = np.load('data/processed/y_cost_test.npy')
        y_time_train = np.load('data/processed/y_time_train.npy')
        y_time_test = np.load('data/processed/y_time_test.npy')
        
        with open('data/processed/feature_names.txt', 'r') as f:
            feature_names = [line.strip() for line in f]
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_cost_train': y_cost_train,
            'y_cost_test': y_cost_test,
            'y_time_train': y_time_train,
            'y_time_test': y_time_test,
            'feature_names': feature_names
        }
    
    def create_models(self):
        """Initialize ML models"""
        
        # Cost prediction models
        self.cost_models = {
            'xgboost': XGBRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            ),
            'lightgbm': LGBMRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                num_leaves=31,
                random_state=42,
                verbose=-1,
                n_jobs=-1
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        }
        
        # Timeline prediction models
        self.time_models = {
            'xgboost': XGBRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            ),
            'lightgbm': LGBMRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                num_leaves=31,
                random_state=42,
                verbose=-1,
                n_jobs=-1
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        }
    
    def train_cost_models(self, X_train, y_train):
        """Train cost prediction models"""
        print("\n🔵 Training Cost Prediction Models...")
        
        for name, model in self.cost_models.items():
            print(f"  Training {name}...")
            model.fit(X_train, y_train)
            print(f"  ✅ {name} trained")
    
    def train_time_models(self, X_train, y_train):
        """Train timeline prediction models"""
        print("\n🟢 Training Timeline Prediction Models...")
        
        for name, model in self.time_models.items():
            print(f"  Training {name}...")
            model.fit(X_train, y_train)
            print(f"  ✅ {name} trained")
    
    def evaluate_models(self, X_test, y_cost_test, y_time_test):
        """Evaluate all models"""
        print("\n📊 Evaluating Models...")
        
        metrics = {
            'cost_models': {},
            'time_models': {}
        }
        
        # Evaluate cost models
        print("\n  Cost Prediction Metrics:")
        for name, model in self.cost_models.items():
            y_pred = model.predict(X_test)
            
            mae = mean_absolute_error(y_cost_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_cost_test, y_pred))
            r2 = r2_score(y_cost_test, y_pred)
            mape = np.mean(np.abs((y_cost_test - y_pred) / (y_cost_test + 1e-10))) * 100
            
            metrics['cost_models'][name] = {
                'MAE': round(mae, 4),
                'RMSE': round(rmse, 4),
                'R2': round(r2, 4),
                'MAPE': round(mape, 4)
            }
            
            print(f"    {name:15} | MAE: {mae:6.2f} | RMSE: {rmse:6.2f} | R²: {r2:6.3f} | MAPE: {mape:6.2f}%")
        
        # Evaluate time models
        print("\n  Timeline Prediction Metrics:")
        for name, model in self.time_models.items():
            y_pred = model.predict(X_test)
            
            mae = mean_absolute_error(y_time_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_time_test, y_pred))
            r2 = r2_score(y_time_test, y_pred)
            mape = np.mean(np.abs((y_time_test - y_pred) / (y_time_test + 1e-10))) * 100
            
            metrics['time_models'][name] = {
                'MAE': round(mae, 4),
                'RMSE': round(rmse, 4),
                'R2': round(r2, 4),
                'MAPE': round(mape, 4)
            }
            
            print(f"    {name:15} | MAE: {mae:6.2f} | RMSE: {rmse:6.2f} | R²: {r2:6.3f} | MAPE: {mape:6.2f}%")
        
        self.metrics = metrics
        return metrics
    
    def save_models(self):
        """Save trained models"""
        os.makedirs('models', exist_ok=True)
        
        # Save cost models
        for name, model in self.cost_models.items():
            joblib.dump(model, f'models/cost_{name}.pkl')
        
        # Save time models
        for name, model in self.time_models.items():
            joblib.dump(model, f'models/time_{name}.pkl')
        
        # Save metrics
        with open('models/metrics.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print("\n✅ All models saved to models/ directory")
    
    def get_feature_importance(self, feature_names):
        """Extract feature importance"""
        importance_data = []
        
        # Get from best cost model (e.g., XGBoost)
        if hasattr(self.cost_models['xgboost'], 'feature_importances_'):
            importances = self.cost_models['xgboost'].feature_importances_
            
            for feat, imp in zip(feature_names, importances):
                importance_data.append({
                    'feature': feat,
                    'importance': float(imp)
                })
            
            # Sort by importance
            importance_data = sorted(importance_data, key=lambda x: x['importance'], reverse=True)
        
        return importance_data[:20]  # Top 20

# Main execution
if __name__ == "__main__":
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Load data
    data = trainer.load_data()
    
    # Create models
    trainer.create_models()
    
    # Train models
    trainer.train_cost_models(data['X_train'], data['y_cost_train'])
    trainer.train_time_models(data['X_train'], data['y_time_train'])
    
    # Evaluate
    metrics = trainer.evaluate_models(
        data['X_test'],
        data['y_cost_test'],
        data['y_time_test']
    )
    
    # Save models
    trainer.save_models()
    
    # Get feature importance
    importance = trainer.get_feature_importance(data['feature_names'])
    
    with open('models/feature_importance.json', 'w') as f:
        json.dump(importance, f, indent=2)
    
    print("\n🎉 Model training completed!")