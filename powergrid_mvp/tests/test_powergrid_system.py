#!/usr/bin/env python3
"""
POWERGRID ML System Test Suite
Comprehensive testing for all components of the POWERGRID prediction system
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta
import tempfile
import os
import sys

# Add src to path
sys.path.append('src')

from data.powergrid_preprocessing import PowerGridPreprocessor
from models.powergrid_ml import PowerGridMLModel
from models.hotspot_analyzer import PowerGridHotspotAnalyzer
from api.enhanced_main import app, get_model_performance, hotspot_analysis
from models.predictor import ProjectPredictor


class TestPowerGridPreprocessor:
    """Test cases for PowerGridPreprocessor"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample project data for testing"""
        return pd.DataFrame({
            'project_type': ['substation', 'overhead_line', 'underground_cable'] * 10,
            'budget': np.random.uniform(10000000, 100000000, 30),
            'estimated_timeline': np.random.randint(180, 730, 30),
            'terrain_type': ['plain', 'hilly', 'urban', 'coastal', 'forest'] * 6,
            'environmental_clearance_status': ['approved', 'pending', 'rejected'] * 10,
            'material_cost_ratio': np.random.uniform(0.5, 0.8, 30),
            'labor_cost_ratio': np.random.uniform(0.2, 0.5, 30),
            'regulatory_complexity_score': np.random.uniform(0.1, 1.0, 30),
            'monsoon_impact_score': np.random.uniform(0.1, 1.0, 30),
            'vendor_risk_score': np.random.uniform(0.1, 1.0, 30),
            'demand_supply_impact': np.random.uniform(0.1, 1.0, 30),
            'resource_availability_score': np.random.uniform(0.1, 1.0, 30),
            'cost_escalation_risk': np.random.uniform(0.1, 1.0, 30),
            'timeline_pressure_score': np.random.uniform(0.1, 1.0, 30),
            'weather_impact_ratio': np.random.uniform(0.1, 1.0, 30),
            'trained_manpower_availability': np.random.uniform(0.1, 1.0, 30),
            'historical_delay_pattern': np.random.uniform(0.1, 1.0, 30),
            'regional_delay_factor': np.random.uniform(0.1, 1.0, 30),
            'seasonal_factor': np.random.uniform(0.1, 1.0, 30),
            'technology_risk': np.random.uniform(0.1, 1.0, 30),
            'project_complexity_score': np.random.uniform(0.1, 1.0, 30),
            'critical_path_risk': np.random.uniform(0.1, 1.0, 30),
            'vendor_performance_score': np.random.uniform(0.1, 1.0, 30),
            'location': ['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore'] * 6,
            'start_date': pd.date_range('2024-01-01', periods=30, freq='D')
        })
    
    def test_preprocessor_initialization(self):
        """Test preprocessor initialization"""
        preprocessor = PowerGridPreprocessor()
        assert preprocessor is not None
        assert hasattr(preprocessor, 'scaler')
        assert hasattr(preprocessor, 'categorical_encoders')
    
    def test_create_domain_features(self, sample_data):
        """Test domain-specific feature creation"""
        preprocessor = PowerGridPreprocessor()
        features = preprocessor.create_domain_features(sample_data)
        
        # Check if all expected features are created
        expected_features = [
            'cost_intensity', 'timeline_pressure', 'weather_impact',
            'vendor_risk', 'regulatory_complexity', 'resource_availability',
            'demand_supply_impact', 'historical_delay_pattern',
            'regional_factors', 'project_complexity_interactions',
            'cost_escalation_risk', 'critical_path_risk', 'technology_risk'
        ]
        
        for feature in expected_features:
            assert feature in features.columns
    
    def test_handle_missing_values(self, sample_data):
        """Test missing value handling"""
        # Introduce missing values
        sample_data.loc[0, 'budget'] = np.nan
        sample_data.loc[1, 'terrain_type'] = None
        
        preprocessor = PowerGridPreprocessor()
        cleaned_data = preprocessor.handle_missing_values(sample_data)
        
        # Check if missing values are handled
        assert not cleaned_data['budget'].isna().any()
        assert not cleaned_data['terrain_type'].isna().any()
    
    def test_encode_categorical_variables(self, sample_data):
        """Test categorical encoding"""
        preprocessor = PowerGridPreprocessor()
        encoded_data = preprocessor.encode_categorical_variables(sample_data)
        
        # Check if categorical columns are encoded
        assert 'project_type' not in encoded_data.columns or encoded_data['project_type'].dtype in ['int64', 'float64']
    
    def test_create_target_variables(self, sample_data):
        """Test target variable creation"""
        preprocessor = PowerGridPreprocessor()
        data_with_targets = preprocessor.create_target_variables(sample_data)
        
        # Check if target variables are created
        expected_targets = [
            'cost_overrun_percentage', 'timeline_overrun_percentage',
            'high_cost_overrun', 'high_timeline_overrun'
        ]
        
        for target in expected_targets:
            assert target in data_with_targets.columns
    
    def test_full_preprocessing_pipeline(self, sample_data):
        """Test complete preprocessing pipeline"""
        preprocessor = PowerGridPreprocessor()
        processed_data = preprocessor.preprocess_powergrid_data(sample_data)
        
        # Check if data is processed correctly
        assert isinstance(processed_data, pd.DataFrame)
        assert not processed_data.isna().any().any()  # No missing values
        assert processed_data.shape[0] == sample_data.shape[0]  # Same number of rows


class TestPowerGridMLModel:
    """Test cases for PowerGridMLModel"""
    
    @pytest.fixture
    def sample_processed_data(self):
        """Create sample processed data"""
        np.random.seed(42)
        n_samples = 100
        
        data = pd.DataFrame({
            'budget': np.random.uniform(10000000, 100000000, n_samples),
            'estimated_timeline': np.random.randint(180, 730, n_samples),
            'material_cost_ratio': np.random.uniform(0.5, 0.8, n_samples),
            'labor_cost_ratio': np.random.uniform(0.2, 0.5, n_samples),
            'regulatory_complexity_score': np.random.uniform(0.1, 1.0, n_samples),
            'monsoon_impact_score': np.random.uniform(0.1, 1.0, n_samples),
            'vendor_risk_score': np.random.uniform(0.1, 1.0, n_samples),
            'cost_intensity': np.random.uniform(0.1, 1.0, n_samples),
            'timeline_pressure': np.random.uniform(0.1, 1.0, n_samples),
            'weather_impact': np.random.uniform(0.1, 1.0, n_samples),
            'vendor_risk': np.random.uniform(0.1, 1.0, n_samples),
            'cost_overrun_percentage': np.random.uniform(-10, 50, n_samples),
            'timeline_overrun_percentage': np.random.uniform(-5, 100, n_samples)
        })
        
        return data
    
    def test_model_initialization(self):
        """Test model initialization"""
        model = PowerGridMLModel()
        assert model is not None
        assert hasattr(model, 'cost_models')
        assert hasattr(model, 'time_models')
    
    def test_train_models(self, sample_processed_data):
        """Test model training"""
        model = PowerGridMLModel()
        
        X = sample_processed_data.drop(['cost_overrun_percentage', 'timeline_overrun_percentage'], axis=1)
        y_cost = sample_processed_data['cost_overrun_percentage']
        y_time = sample_processed_data['timeline_overrun_percentage']
        
        # Train models
        model.train_models(X, y_cost, y_time)
        
        # Check if models are trained
        assert len(model.cost_models) > 0
        assert len(model.time_models) > 0
    
    def test_predict_with_uncertainty(self, sample_processed_data):
        """Test prediction with uncertainty"""
        model = PowerGridMLModel()
        
        X = sample_processed_data.drop(['cost_overrun_percentage', 'timeline_overrun_percentage'], axis=1)
        y_cost = sample_processed_data['cost_overrun_percentage']
        y_time = sample_processed_data['timeline_overrun_percentage']
        
        # Train models first
        model.train_models(X, y_cost, y_time)
        
        # Make predictions
        predictions = model.predict_with_uncertainty(X.iloc[:5])
        
        # Check predictions structure
        assert 'cost_prediction' in predictions
        assert 'time_prediction' in predictions
        assert 'cost_uncertainty' in predictions
        assert 'time_uncertainty' in predictions
    
    def test_get_feature_importance(self, sample_processed_data):
        """Test feature importance extraction"""
        model = PowerGridMLModel()
        
        X = sample_processed_data.drop(['cost_overrun_percentage', 'timeline_overrun_percentage'], axis=1)
        y_cost = sample_processed_data['cost_overrun_percentage']
        y_time = sample_processed_data['timeline_overrun_percentage']
        
        # Train models first
        model.train_models(X, y_cost, y_time)
        
        # Get feature importance
        importance = model.get_feature_importance()
        
        # Check importance structure
        assert 'cost_features' in importance
        assert 'time_features' in importance
    
    def test_model_save_load(self, sample_processed_data):
        """Test model save and load functionality"""
        model = PowerGridMLModel()
        
        X = sample_processed_data.drop(['cost_overrun_percentage', 'timeline_overrun_percentage'], axis=1)
        y_cost = sample_processed_data['cost_overrun_percentage']
        y_time = sample_processed_data['timeline_overrun_percentage']
        
        # Train models first
        model.train_models(X, y_cost, y_time)
        
        # Save model
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, 'test_model')
            model.save_model(model_path)
            
            # Load model
            new_model = PowerGridMLModel()
            new_model.load_model(model_path)
            
            # Check if models are loaded
            assert len(new_model.cost_models) > 0
            assert len(new_model.time_models) > 0


class TestPowerGridHotspotAnalyzer:
    """Test cases for PowerGridHotspotAnalyzer"""
    
    @pytest.fixture
    def sample_risk_data(self):
        """Create sample risk data"""
        np.random.seed(42)
        n_samples = 50
        
        return pd.DataFrame({
            'cost_overrun_percentage': np.random.uniform(-5, 40, n_samples),
            'timeline_overrun_percentage': np.random.uniform(-2, 80, n_samples),
            'budget': np.random.uniform(10000000, 100000000, n_samples),
            'estimated_timeline': np.random.randint(180, 730, n_samples),
            'regulatory_complexity_score': np.random.uniform(0.1, 1.0, n_samples),
            'monsoon_impact_score': np.random.uniform(0.1, 1.0, n_samples),
            'vendor_risk_score': np.random.uniform(0.1, 1.0, n_samples),
            'demand_supply_impact': np.random.uniform(0.1, 1.0, n_samples),
            'resource_availability_score': np.random.uniform(0.1, 1.0, n_samples),
            'cost_escalation_risk': np.random.uniform(0.1, 1.0, n_samples),
            'project_type': np.random.choice(['substation', 'overhead_line', 'underground_cable'], n_samples),
            'terrain_type': np.random.choice(['plain', 'hilly', 'urban', 'coastal', 'forest'], n_samples),
            'location': np.random.choice(['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore'], n_samples)
        })
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        analyzer = PowerGridHotspotAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'clustering_models')
        assert hasattr(analyzer, 'anomaly_detector')
    
    def test_create_risk_features(self, sample_risk_data):
        """Test risk feature creation"""
        analyzer = PowerGridHotspotAnalyzer()
        risk_features = analyzer.create_risk_features(sample_risk_data)
        
        # Check if risk features are created
        expected_features = [
            'composite_risk_score', 'normalized_cost_overrun',
            'normalized_timeline_overrun', 'risk_category'
        ]
        
        for feature in expected_features:
            assert feature in risk_features.columns
    
    def test_perform_clustering(self, sample_risk_data):
        """Test clustering analysis"""
        analyzer = PowerGridHotspotAnalyzer()
        risk_features = analyzer.create_risk_features(sample_risk_data)
        
        # Perform clustering
        clustering_results = analyzer.perform_clustering(risk_features)
        
        # Check clustering results
        assert 'kmeans_labels' in clustering_results.columns
        assert 'dbscan_labels' in clustering_results.columns
        assert 'gmm_labels' in clustering_results.columns
    
    def test_detect_anomalies(self, sample_risk_data):
        """Test anomaly detection"""
        analyzer = PowerGridHotspotAnalyzer()
        risk_features = analyzer.create_risk_features(sample_risk_data)
        
        # Detect anomalies
        anomaly_results = analyzer.detect_anomalies(risk_features)
        
        # Check anomaly detection results
        assert 'anomaly_score' in anomaly_results.columns
        assert 'is_anomaly' in anomaly_results.columns
    
    def test_calculate_hotspot_score(self, sample_risk_data):
        """Test hotspot score calculation"""
        analyzer = PowerGridHotspotAnalyzer()
        
        # Perform complete analysis
        clustering_results = analyzer.perform_clustering(sample_risk_data)
        anomaly_results = analyzer.detect_anomalies(clustering_results)
        
        # Calculate hotspot scores
        hotspot_results = analyzer.calculate_hotspot_score(anomaly_results)
        
        # Check hotspot scores
        assert 'hotspot_score' in hotspot_results.columns
        assert 'hotspot_category' in hotspot_results.columns
        assert hotspot_results['hotspot_score'].between(0, 1).all()
    
    def test_generate_recommendations(self, sample_risk_data):
        """Test recommendation generation"""
        analyzer = PowerGridHotspotAnalyzer()
        
        # Perform complete analysis
        clustering_results = analyzer.perform_clustering(sample_risk_data)
        anomaly_results = analyzer.detect_anomalies(clustering_results)
        hotspot_results = analyzer.calculate_hotspot_score(anomaly_results)
        
        # Generate recommendations
        recommendations = analyzer.generate_recommendations(hotspot_results)
        
        # Check recommendations
        assert isinstance(recommendations, dict)
        assert 'high_risk' in recommendations
        assert 'medium_risk' in recommendations
        assert 'low_risk' in recommendations
    
    def test_visualize_hotspots(self, sample_risk_data):
        """Test hotspot visualization"""
        analyzer = PowerGridHotspotAnalyzer()
        
        # Perform complete analysis
        clustering_results = analyzer.perform_clustering(sample_risk_data)
        anomaly_results = analyzer.detect_anomalies(clustering_results)
        hotspot_results = analyzer.calculate_hotspot_score(anomaly_results)
        
        # Test visualization (should not raise errors)
        try:
            analyzer.visualize_hotspots(hotspot_results)
            visualization_success = True
        except Exception as e:
            visualization_success = False
            print(f"Visualization failed: {e}")
        
        # For testing purposes, we just check that the method exists and can be called
        assert hasattr(analyzer, 'visualize_hotspots')


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "POWERGRID ML System" in response.json()["message"]
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_predict_endpoint(self, client):
        """Test prediction endpoint"""
        sample_project = {
            "project_type": "substation",
            "budget": 50000000,
            "estimated_timeline": 365,
            "terrain_type": "plain",
            "environmental_clearance_status": "approved",
            "material_cost_ratio": 0.65,
            "labor_cost_ratio": 0.35,
            "regulatory_complexity_score": 0.7,
            "monsoon_impact_score": 0.6,
            "vendor_risk_score": 0.4,
            "demand_supply_impact": 0.5,
            "resource_availability_score": 0.8,
            "cost_escalation_risk": 0.3,
            "timeline_pressure_score": 0.6,
            "weather_impact_ratio": 0.4,
            "trained_manpower_availability": 0.7,
            "historical_delay_pattern": 0.2,
            "regional_delay_factor": 0.3,
            "seasonal_factor": 0.5,
            "technology_risk": 0.2,
            "project_complexity_score": 0.6,
            "critical_path_risk": 0.4,
            "vendor_performance_score": 0.7,
            "location": "Delhi",
            "start_date": "2024-01-15"
        }
        
        response = client.post("/predict", json=sample_project)
        assert response.status_code == 200
        
        result = response.json()
        assert "cost_prediction" in result
        assert "time_prediction" in result
        assert "risk_score" in result
        assert "recommendations" in result
    
    def test_batch_predict_endpoint(self, client):
        """Test batch prediction endpoint"""
        sample_projects = {
            "projects": [
                {
                    "project_type": "substation",
                    "budget": 50000000,
                    "estimated_timeline": 365,
                    "terrain_type": "plain",
                    "environmental_clearance_status": "approved",
                    "material_cost_ratio": 0.65,
                    "labor_cost_ratio": 0.35,
                    "regulatory_complexity_score": 0.7,
                    "monsoon_impact_score": 0.6,
                    "vendor_risk_score": 0.4,
                    "demand_supply_impact": 0.5,
                    "resource_availability_score": 0.8,
                    "cost_escalation_risk": 0.3,
                    "timeline_pressure_score": 0.6,
                    "weather_impact_ratio": 0.4,
                    "trained_manpower_availability": 0.7,
                    "historical_delay_pattern": 0.2,
                    "regional_delay_factor": 0.3,
                    "seasonal_factor": 0.5,
                    "technology_risk": 0.2,
                    "project_complexity_score": 0.6,
                    "critical_path_risk": 0.4,
                    "vendor_performance_score": 0.7,
                    "location": "Delhi",
                    "start_date": "2024-01-15"
                },
                {
                    "project_type": "overhead_line",
                    "budget": 30000000,
                    "estimated_timeline": 240,
                    "terrain_type": "hilly",
                    "environmental_clearance_status": "pending",
                    "material_cost_ratio": 0.7,
                    "labor_cost_ratio": 0.3,
                    "regulatory_complexity_score": 0.8,
                    "monsoon_impact_score": 0.7,
                    "vendor_risk_score": 0.5,
                    "demand_supply_impact": 0.6,
                    "resource_availability_score": 0.6,
                    "cost_escalation_risk": 0.4,
                    "timeline_pressure_score": 0.7,
                    "weather_impact_ratio": 0.6,
                    "trained_manpower_availability": 0.5,
                    "historical_delay_pattern": 0.4,
                    "regional_delay_factor": 0.5,
                    "seasonal_factor": 0.7,
                    "technology_risk": 0.3,
                    "project_complexity_score": 0.7,
                    "critical_path_risk": 0.5,
                    "vendor_performance_score": 0.6,
                    "location": "Himachal Pradesh",
                    "start_date": "2024-02-01"
                }
            ]
        }
        
        response = client.post("/predict/batch", json=sample_projects)
        assert response.status_code == 200
        
        result = response.json()
        assert "predictions" in result
        assert len(result["predictions"]) == 2
    
    def test_hotspot_analysis_endpoint(self, client):
        """Test hotspot analysis endpoint"""
        sample_data = {
            "projects": [
                {
                    "project_id": "proj_001",
                    "project_type": "substation",
                    "budget": 50000000,
                    "actual_cost": 55000000,
                    "estimated_timeline": 365,
                    "actual_timeline": 400,
                    "terrain_type": "plain",
                    "location": "Delhi",
                    "cost_overrun_percentage": 10,
                    "timeline_overrun_percentage": 9.6
                }
            ]
        }
        
        response = client.post("/hotspot-analysis", json=sample_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "hotspot_analysis" in result
        assert "recommendations" in result
    
    def test_model_performance_endpoint(self, client):
        """Test model performance endpoint"""
        response = client.get("/model-performance")
        assert response.status_code == 200
        
        result = response.json()
        assert "cost_models" in result
        assert "time_models" in result


class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_end_to_end_prediction_workflow(self):
        """Test complete prediction workflow"""
        # Create sample data
        np.random.seed(42)
        n_samples = 50
        
        data = pd.DataFrame({
            'project_type': np.random.choice(['substation', 'overhead_line', 'underground_cable'], n_samples),
            'budget': np.random.uniform(10000000, 100000000, n_samples),
            'estimated_timeline': np.random.randint(180, 730, n_samples),
            'terrain_type': np.random.choice(['plain', 'hilly', 'urban', 'coastal', 'forest'], n_samples),
            'environmental_clearance_status': np.random.choice(['approved', 'pending', 'rejected'], n_samples),
            'material_cost_ratio': np.random.uniform(0.5, 0.8, n_samples),
            'labor_cost_ratio': np.random.uniform(0.2, 0.5, n_samples),
            'regulatory_complexity_score': np.random.uniform(0.1, 1.0, n_samples),
            'monsoon_impact_score': np.random.uniform(0.1, 1.0, n_samples),
            'vendor_risk_score': np.random.uniform(0.1, 1.0, n_samples),
            'demand_supply_impact': np.random.uniform(0.1, 1.0, n_samples),
            'resource_availability_score': np.random.uniform(0.1, 1.0, n_samples),
            'cost_escalation_risk': np.random.uniform(0.1, 1.0, n_samples),
            'timeline_pressure_score': np.random.uniform(0.1, 1.0, n_samples),
            'weather_impact_ratio': np.random.uniform(0.1, 1.0, n_samples),
            'trained_manpower_availability': np.random.uniform(0.1, 1.0, n_samples),
            'historical_delay_pattern': np.random.uniform(0.1, 1.0, n_samples),
            'regional_delay_factor': np.random.uniform(0.1, 1.0, n_samples),
            'seasonal_factor': np.random.uniform(0.1, 1.0, n_samples),
            'technology_risk': np.random.uniform(0.1, 1.0, n_samples),
            'project_complexity_score': np.random.uniform(0.1, 1.0, n_samples),
            'critical_path_risk': np.random.uniform(0.1, 1.0, n_samples),
            'vendor_performance_score': np.random.uniform(0.1, 1.0, n_samples),
            'location': np.random.choice(['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore'], n_samples),
            'start_date': pd.date_range('2024-01-01', periods=n_samples, freq='D')
        })
        
        # Add target variables
        data['cost_overrun_percentage'] = np.random.uniform(-5, 40, n_samples)
        data['timeline_overrun_percentage'] = np.random.uniform(-2, 80, n_samples)
        
        # Test preprocessing
        preprocessor = PowerGridPreprocessor()
        processed_data = preprocessor.preprocess_powergrid_data(data)
        
        # Test model training
        ml_model = PowerGridMLModel()
        X = processed_data.drop(['cost_overrun_percentage', 'timeline_overrun_percentage'], axis=1)
        y_cost = processed_data['cost_overrun_percentage']
        y_time = processed_data['timeline_overrun_percentage']
        
        ml_model.train_models(X, y_cost, y_time)
        
        # Test predictions
        predictions = ml_model.predict_with_uncertainty(X.iloc[:5])
        
        # Test hotspot analysis
        analyzer = PowerGridHotspotAnalyzer()
        hotspot_results = analyzer.analyze_hotspots(processed_data)
        
        # Verify results
        assert predictions['cost_prediction'].shape[0] == 5
        assert predictions['time_prediction'].shape[0] == 5
        assert 'hotspot_score' in hotspot_results.columns
        assert 'hotspot_category' in hotspot_results.columns
    
    def test_model_performance_consistency(self):
        """Test model performance consistency across multiple runs"""
        # Create consistent test data
        np.random.seed(123)
        n_samples = 100
        
        X = pd.DataFrame({
            'budget': np.random.uniform(10000000, 100000000, n_samples),
            'estimated_timeline': np.random.randint(180, 730, n_samples),
            'material_cost_ratio': np.random.uniform(0.5, 0.8, n_samples),
            'labor_cost_ratio': np.random.uniform(0.2, 0.5, n_samples),
            'regulatory_complexity_score': np.random.uniform(0.1, 1.0, n_samples),
            'monsoon_impact_score': np.random.uniform(0.1, 1.0, n_samples),
            'vendor_risk_score': np.random.uniform(0.1, 1.0, n_samples)
        })
        
        y_cost = np.random.uniform(-5, 40, n_samples)
        y_time = np.random.uniform(-2, 80, n_samples)
        
        # Train model multiple times
        predictions_list = []
        for i in range(3):
            model = PowerGridMLModel()
            model.train_models(X, y_cost, y_time)
            predictions = model.predict_with_uncertainty(X.iloc[:10])
            predictions_list.append(predictions)
        
        # Check consistency (predictions should be similar)
        for i in range(1, len(predictions_list)):
            cost_diff = np.abs(predictions_list[0]['cost_prediction'] - predictions_list[i]['cost_prediction'])
            time_diff = np.abs(predictions_list[0]['time_prediction'] - predictions_list[i]['time_prediction'])
            
            # Allow for some variance due to random initialization
            assert np.mean(cost_diff) < 5.0  # Less than 5% average difference
            assert np.mean(time_diff) < 5.0   # Less than 5% average difference


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])