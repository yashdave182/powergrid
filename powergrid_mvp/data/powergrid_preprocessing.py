# src/dashboard/app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import required modules
from models.predictor import ProjectPredictor
from models.powergrid_ml import PowerGridMLModel
from models.hotspot_analyzer import PowerGridHotspotAnalyzer
from data.powergrid_preprocessing import PowerGridPreprocessor

# Page config
st.set_page_config(
    page_title="POWERGRID Project Analytics",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .high-risk {
        color: #d62728;
        font-weight: bold;
    }
    .medium-risk {
        color: #ff7f0e;
        font-weight: bold;
    }
    .low-risk {
        color: #2ca02c;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        border-right: 1px solid #ddd;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'predictor' not in st.session_state:
    with st.spinner("Loading models..."):
        st.session_state.predictor = ProjectPredictor()
        st.session_state.predictor.load_models()
        st.session_state.preprocessor = PowerGridPreprocessor()
        st.session_state.powergrid_ml = PowerGridMLModel()
        st.session_state.hotspot_analyzer = PowerGridHotspotAnalyzer()
        st.success("✅ All POWERGRID ML models loaded successfully!")

# Load processed data
@st.cache_data
def load_data():
    data_path = os.path.join(parent_dir, 'data', 'processed', 'processed_data.csv')
    df = pd.read_csv(data_path)
    
    # Date features
    if 'start_date' in df.columns:
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['start_year'] = df['start_date'].dt.year
        df['start_month'] = df['start_date'].dt.month
        df['start_quarter'] = df['start_date'].dt.quarter
        df['is_monsoon_start'] = df['start_month'].apply(lambda x: 1 if x in [6,7,8,9] else 0)
    
    return df

# Main app
def main():
    # Header
    st.markdown('<div class="main-header">🔌 POWERGRID Project Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "📊 Overview",
        "🎯 Single Project Prediction",
        "📈 Batch Analysis",
        "🔍 Risk Hotspots",
        "⚡ Enhanced Hotspot Analysis",
        "📋 Model Performance",
        "🔧 Advanced ML Analysis"
    ])
    
    if page == "📊 Overview":
        show_overview()
    elif page == "🎯 Single Project Prediction":
        show_single_prediction()
    elif page == "📈 Batch Analysis":
        show_batch_analysis()
    elif page == "🔍 Risk Hotspots":
        show_risk_hotspots()
    elif page == "⚡ Enhanced Hotspot Analysis":
        show_enhanced_hotspot_analysis()
    elif page == "📋 Model Performance":
        show_model_performance()
    elif page == "🔧 Advanced ML Analysis":
        show_advanced_ml_analysis()

def show_overview():
    """Overview dashboard"""
    st.header("📊 Project Portfolio Overview")
    
    df = load_data()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Projects", len(df))
    
    with col2:
        high_risk_count = len(df[df['cost_overrun_percentage'] > 20])
        st.metric("High Risk Projects", high_risk_count, delta=f"{high_risk_count/len(df)*100:.1f}%")
    
    with col3:
        avg_cost_overrun = df['cost_overrun_percentage'].mean()
        st.metric("Avg Cost Overrun", f"{avg_cost_overrun:.1f}%")
    
    with col4:
        avg_time_overrun = df['time_overrun_percentage'].mean()
        st.metric("Avg Time Overrun", f"{avg_time_overrun:.1f}%")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            df,
            x='terrain_difficulty_score',
            title='Terrain Difficulty Distribution',
            nbins=20,
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(
            df,
            x='length_km',
            title='Project Length Distribution (km)',
            nbins=20,
            color_discrete_sequence=['#ff7f0e']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.box(
            df,
            y='voltage_level_kv',
            title='Voltage Level Distribution (kV)',
            color_discrete_sequence=['#2ca02c']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.box(
            df,
            y='num_towers',
            title='Number of Towers Distribution',
            color_discrete_sequence=['#d62728']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Data summary
    st.subheader("📋 Data Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dataset Rows", df.shape[0])
    with col2:
        st.metric("Total Features", len(df.columns))
    with col3:
        st.metric("Numerical Features", len(df.select_dtypes(include=[np.number]).columns))
    
    # Show sample data
    with st.expander("View Sample Data"):
        st.dataframe(df.head(10))

def show_single_prediction():
    """Single project prediction interface"""
    st.header("🎯 Single Project Prediction")
    st.info("Enter project details to get cost and time overrun predictions")
    
    with st.form("project_prediction_form"):
        st.subheader("Project Details")
        
        # Basic information
        col1, col2 = st.columns(2)
        with col1:
            project_id = st.text_input("Project ID", value="PG_TEST_001")
            length_km = st.number_input("Length (km)", value=100.0, min_value=0.0)
            voltage_level_kv = st.number_input("Voltage Level (kV)", value=400.0, min_value=0.0)
            terrain_difficulty_score = st.number_input("Terrain Difficulty Score", value=5.0, min_value=0.0, max_value=10.0)
            num_towers = st.number_input("Number of Towers", value=200, min_value=0)
            estimated_cost_inr = st.number_input("Estimated Cost (INR)", value=100000000.0, min_value=0.0)
            estimated_duration_days = st.number_input("Estimated Duration (days)", value=365, min_value=0)
        
        with col2:
            material_cost_inr = st.number_input("Material Cost (INR)", value=40000000.0, min_value=0.0)
            labor_cost_inr = st.number_input("Labor Cost (INR)", value=30000000.0, min_value=0.0)
            steel_cost_per_ton = st.number_input("Steel Cost per Ton", value=65000.0, min_value=0.0)
            copper_cost_per_ton = st.number_input("Copper Cost per Ton", value=800000.0, min_value=0.0)
            total_steel_tons = st.number_input("Total Steel (tons)", value=1500.0, min_value=0.0)
            total_copper_tons = st.number_input("Total Copper (tons)", value=200.0, min_value=0.0)
            estimated_manpower = st.number_input("Estimated Manpower", value=3000, min_value=0)
        
        # Additional details
        st.subheader("Additional Details")
        col3, col4 = st.columns(2)
        with col3:
            labor_cost_per_day = st.number_input("Labor Cost per Day", value=800.0, min_value=0.0)
            vendor_quality_score = st.number_input("Vendor Quality Score", value=7.0, min_value=0.0, max_value=10.0)
            vendor_on_time_rate = st.number_input("Vendor On-time Rate", value=0.85, min_value=0.0, max_value=1.0)
            vendor_cost_efficiency = st.number_input("Vendor Cost Efficiency", value=0.90, min_value=0.0, max_value=1.0)
            adverse_weather_days = st.number_input("Adverse Weather Days", value=45, min_value=0)
            monsoon_affected_months = st.number_input("Monsoon Affected Months", value=3, min_value=0, max_value=12)
        
        with col4:
            permit_approval_days = st.number_input("Permit Approval Days", value=60, min_value=0)
            environmental_clearance_days = st.number_input("Environmental Clearance Days", value=90, min_value=0)
            project_complexity_score = st.number_input("Project Complexity Score", value=0.6, min_value=0.0, max_value=1.0)
            project_type = st.selectbox("Project Type", ["Overhead Line", "Underground Cable", "Substation"])
            region = st.selectbox("Region", ["North", "South", "East", "West"])
            terrain_type = st.selectbox("Terrain Type", ["Plain", "Hilly", "Mountainous", "Desert"])
            start_date = st.date_input("Start Date")
        
        submitted = st.form_submit_button("🔮 Get Predictions")
    
    if submitted:
        # Prepare input data
        project_data = {
            'project_id': project_id,
            'length_km': length_km,
            'voltage_level_kv': voltage_level_kv,
            'terrain_difficulty_score': terrain_difficulty_score,
            'num_towers': num_towers,
            'estimated_cost_inr': estimated_cost_inr,
            'estimated_duration_days': estimated_duration_days,
            'material_cost_inr': material_cost_inr,
            'labor_cost_inr': labor_cost_inr,
            'steel_cost_per_ton': steel_cost_per_ton,
            'copper_cost_per_ton': copper_cost_per_ton,
            'total_steel_tons': total_steel_tons,
            'total_copper_tons': total_copper_tons,
            'estimated_manpower': estimated_manpower,
            'labor_cost_per_day': labor_cost_per_day,
            'vendor_quality_score': vendor_quality_score,
            'vendor_on_time_rate': vendor_on_time_rate,
            'vendor_cost_efficiency': vendor_cost_efficiency,
            'adverse_weather_days': adverse_weather_days,
            'monsoon_affected_months': monsoon_affected_months,
            'permit_approval_days': permit_approval_days,
            'environmental_clearance_days': environmental_clearance_days,
            'project_complexity_score': project_complexity_score,
            'project_type': project_type,
            'region': region,
            'terrain_type': terrain_type,
            'start_date': start_date.strftime('%Y-%m-%d')
        }
        
        # Make predictions
        with st.spinner("🧠 Analyzing project data..."):
            predictions = st.session_state.predictor.predict(project_data)
            
            # Enhanced predictions
            enhanced_cost_pred = st.session_state.powergrid_ml.predict_with_uncertainty(project_data, 'cost')
            enhanced_time_pred = st.session_state.powergrid_ml.predict_with_uncertainty(project_data, 'time')
            
            # Display results
            st.subheader("📊 Prediction Results")
            
            # Risk assessment
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Category", predictions['risk_category'])
            with col2:
                st.metric("Priority Level", predictions['priority'])
            with col3:
                st.metric("Risk Score", f"{predictions['risk_score']:.3f}")
            
            st.divider()
            
            # Cost and Time predictions
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Cost Analysis")
                st.metric("Estimated Cost", f"₹{predictions['estimated_cost_inr']:,.0f}")
                st.metric("Predicted Cost", f"₹{predictions['predicted_cost_inr']:,.0f}")
                st.metric("Cost Overrun", f"{predictions['cost_overrun_percentage']:.1f}%")
                
                st.info(f"Confidence: {enhanced_cost_pred['confidence']:.1%}")
                st.info(f"Uncertainty: ±₹{enhanced_cost_pred['uncertainty']:,.0f}")
                st.info(f"Prediction Interval: ₹{enhanced_cost_pred['prediction_interval'][0]:,.0f} - ₹{enhanced_cost_pred['prediction_interval'][1]:,.0f}")
                
                if predictions['cost_overrun_inr'] > 0:
                    st.error(f"Expected cost increase: ₹{predictions['cost_overrun_inr']:,.0f}")
                else:
                    st.success(f"Expected cost savings: ₹{abs(predictions['cost_overrun_inr']):,.0f}")
            
            with col2:
                st.subheader("⏱️ Timeline Analysis")
                st.metric("Estimated Duration", f"{predictions['estimated_duration_days']} days")
                st.metric("Predicted Duration", f"{predictions['predicted_duration_days']} days")
                st.metric("Time Overrun", f"{predictions['time_overrun_percentage']:.1f}%")
                
                st.info(f"Confidence: {enhanced_time_pred['confidence']:.1%}")
                st.info(f"Uncertainty: ±{enhanced_time_pred['uncertainty']:.1f} days")
                st.info(f"Prediction Interval: {enhanced_time_pred['prediction_interval'][0]:.1f} - {enhanced_time_pred['prediction_interval'][1]:.1f} days")
                
                if predictions['time_overrun_days'] > 0:
                    st.error(f"Expected delay: {predictions['time_overrun_days']} days")
                else:
                    st.success(f"Expected time savings: {abs(predictions['time_overrun_days'])} days")
            
            st.divider()
            
            # Domain-specific analysis
            st.subheader("🔧 Domain-Specific Analysis")
            
            domain_features = st.session_state.preprocessor.create_domain_specific_features(project_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Key Domain Features:**")
                st.info(f"Project Type Score: {domain_features.get('project_type_encoded', 0):.2f}")
                st.info(f"Terrain Risk Score: {domain_features.get('terrain_risk_score', 0):.2f}")
                st.info(f"Cost Intensity: ₹{domain_features.get('cost_intensity_per_km', 0):,.0f}/km")
                st.info(f"Timeline Pressure: {domain_features.get('timeline_pressure_score', 0):.2f}")
            
            with col2:
                st.write("**Risk Factors:**")
                weather_risk = "High" if domain_features.get('weather_impact_score', 0) > 0.7 else "Medium" if domain_features.get('weather_impact_score', 0) > 0.4 else "Low"
                st.info(f"Weather Impact: {weather_risk}")
                
                vendor_risk = "High" if domain_features.get('vendor_risk_score', 0) > 0.7 else "Medium" if domain_features.get('vendor_risk_score', 0) > 0.4 else "Low"
                st.info(f"Vendor Risk: {vendor_risk}")
                
                reg_risk = "High" if domain_features.get('regulatory_complexity_score', 0) > 0.7 else "Medium" if domain_features.get('regulatory_complexity_score', 0) > 0.4 else "Low"
                st.info(f"Regulatory Complexity: {reg_risk}")
                
                resource_risk = "High" if domain_features.get('resource_availability_score', 0) < 0.3 else "Medium" if domain_features.get('resource_availability_score', 0) < 0.6 else "Low"
                st.info(f"Resource Risk: {resource_risk}")
            
            st.divider()
            
            # Recommendations
            st.subheader("💡 Recommendations")
            if predictions['risk_category'] == "High":
                st.error("⚠️ High Risk Project - Immediate attention required!")
                st.write("**Recommended Actions:**")
                st.write("- Conduct detailed risk assessment and mitigation planning")
                st.write("- Increase project monitoring frequency")
                st.write("- Consider buffer allocation for cost and timeline")
                st.write("- Engage experienced project managers")
            elif predictions['risk_category'] == "Medium":
                st.warning("⚡ Medium Risk Project - Regular monitoring recommended")
                st.write("**Recommended Actions:**")
                st.write("- Implement standard risk management procedures")
                st.write("- Schedule regular progress reviews")
                st.write("- Monitor key performance indicators closely")
            else:
                st.success("✅ Low Risk Project - Standard procedures apply")
                st.write("**Recommended Actions:**")
                st.write("- Follow standard project management protocols")
                st.write("- Regular milestone tracking")
                st.write("- Maintain current best practices")

def show_batch_analysis():
    """Batch project analysis"""
    st.header("📈 Batch Analysis")
    st.info("Upload multiple projects for batch prediction and analysis")
    
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    
    if uploaded_file is not None:
        batch_data = pd.read_csv(uploaded_file)
        
        st.write("**Preview of uploaded data:**")
        st.dataframe(batch_data.head())
        
        # Convert to list of dictionaries
        projects_list = batch_data.to_dict('records')
        
        with st.spinner("🧠 Analyzing batch data..."):
            predictions = st.session_state.predictor.batch_predict(projects_list)
        
        # Convert to DataFrame
        pred_df = pd.DataFrame(predictions)
        
        st.subheader("📊 Batch Prediction Results")
        
        # Column selector
        available_columns = pred_df.columns.tolist()
        default_columns = [col for col in ['project_id', 'predicted_cost_inr', 'predicted_duration_days', 
                                            'risk_category', 'cost_overrun_percentage', 'time_overrun_percentage'] 
                          if col in available_columns]
        
        selected_columns = st.multiselect(
            "Select columns to display:",
            available_columns,
            default=default_columns if default_columns else available_columns[:6]
        )
        
        if selected_columns:
            st.dataframe(pred_df[selected_columns], use_container_width=True)
        else:
            st.dataframe(pred_df, use_container_width=True)
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Projects", len(pred_df))
        
        with col2:
            high_risk = len(pred_df[pred_df['risk_category'] == 'High'])
            st.metric("High Risk Projects", high_risk)
        
        with col3:
            avg_cost = pred_df['cost_overrun_percentage'].mean()
            st.metric("Avg Cost Overrun", f"{avg_cost:.1f}%")
        
        with col4:
            avg_time = pred_df['time_overrun_percentage'].mean()
            st.metric("Avg Time Overrun", f"{avg_time:.1f}%")
        
        # Visualizations
        st.subheader("📊 Analysis Charts")
        col1, col2 = st.columns(2)
        
        with col1:
            risk_counts = pred_df['risk_category'].value_counts()
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title='Risk Category Distribution',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.histogram(
                pred_df,
                x='cost_overrun_percentage',
                title='Cost Overrun Distribution',
                nbins=20
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Download results
        csv = pred_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Predictions CSV",
            data=csv,
            file_name=f"batch_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_risk_hotspots():
    """Risk hotspot identification"""
    st.header("🔍 Risk Hotspots")
    st.info("Identify regions and project types with highest risk")
    
    cluster_path = os.path.join(parent_dir, 'outputs', 'cluster_assignments.csv')
    cluster_data = pd.read_csv(cluster_path)
    
    st.subheader("📊 Cluster Analysis")
    
    # Cluster distribution
    cluster_counts = cluster_data['cluster'].value_counts().sort_index()
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=cluster_counts.values,
            names=cluster_counts.index,
            title='Project Distribution by Cluster',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=cluster_counts.index,
            y=cluster_counts.values,
            title='Projects per Cluster',
            labels={'x': 'Cluster', 'y': 'Number of Projects'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Cluster statistics
    st.subheader("🔍 Cluster Details")
    
    numeric_cols = cluster_data.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col != 'cluster']
    
    cluster_stats = cluster_data.groupby('cluster')[numeric_cols].mean().round(2)
    st.dataframe(cluster_stats)
    
    # Hotspot visualization
    st.divider()
    st.subheader("🗺️ Hotspot Visualization")
    
    img_path = os.path.join(parent_dir, 'outputs', 'hotspot_clusters.png')
    st.image(img_path, caption='Project Risk Hotspots Clustering', use_column_width=True)
    
    # Risk assessment
    st.divider()
    st.subheader("⚠️ Risk Assessment by Cluster")
    
    for cluster_id in sorted(cluster_data['cluster'].unique()):
        cluster_subset = cluster_data[cluster_data['cluster'] == cluster_id]
        
        # Calculate risk score
        avg_length = cluster_subset['length_km'].mean()
        avg_terrain = cluster_subset['terrain_difficulty_score'].mean()
        avg_complexity = cluster_subset['project_complexity_score'].mean()
        
        risk_score = (avg_length / 200) * 0.3 + (avg_terrain / 10) * 0.4 + avg_complexity * 0.3
        
        if risk_score > 0.7:
            risk_level = "🔴 High Risk"
        elif risk_score > 0.4:
            risk_level = "🟡 Medium Risk"
        else:
            risk_level = "🟢 Low Risk"
        
        with st.expander(f"Cluster {cluster_id} - {risk_level}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Projects", len(cluster_subset))
            with col2:
                st.metric("Avg Length (km)", f"{avg_length:.1f}")
            with col3:
                st.metric("Risk Score", f"{risk_score:.2f}")

def show_enhanced_hotspot_analysis():
    """Enhanced hotspot analysis"""
    st.header("⚡ Enhanced Hotspot Analysis")
    st.info("Advanced clustering and anomaly detection for project risk identification")
    
    df = load_data()
    
    # Configuration
    with st.expander("🔧 Analysis Configuration"):
        col1, col2 = st.columns(2)
        with col1:
            n_clusters = st.slider("Number of Clusters", 2, 10, 4)
            contamination = st.slider("Anomaly Contamination", 0.01, 0.2, 0.05, 0.01)
        with col2:
            clustering_method = st.selectbox("Clustering Method", ["kmeans", "dbscan", "gmm", "agglomerative"])
            enable_anomaly = st.checkbox("Enable Anomaly Detection", True)
    
    # Perform analysis
    with st.spinner("🧠 Performing advanced hotspot analysis..."):
        risk_features = st.session_state.hotspot_analyzer.create_risk_features(df)
        
        cluster_results = st.session_state.hotspot_analyzer.perform_clustering(
            risk_features, n_clusters=n_clusters, method=clustering_method
        )
        
        anomaly_scores = np.zeros(len(df))
        if enable_anomaly:
            anomaly_scores = st.session_state.hotspot_analyzer.detect_anomalies(
                risk_features, contamination=contamination
            )
        
        hotspot_scores = st.session_state.hotspot_analyzer.calculate_hotspot_score(
            cluster_results['cluster_labels'], anomaly_scores, cluster_results['silhouette_scores']
        )
        
        recommendations = st.session_state.hotspot_analyzer.generate_recommendations(
            hotspot_scores, cluster_results['cluster_labels']
        )
        
        df['cluster'] = cluster_results['cluster_labels']
        df['anomaly_score'] = anomaly_scores
        df['hotspot_score'] = hotspot_scores
        df['recommendation'] = recommendations
    
    # Display results
    st.subheader("📊 Hotspot Analysis Results")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        n_hotspots = len(df[df['hotspot_score'] > 0.7])
        st.metric("High Risk Hotspots", n_hotspots)
    with col2:
        n_anomalies = len(df[df['anomaly_score'] > 0.5])
        st.metric("Anomalies Detected", n_anomalies)
    with col3:
        avg_score = df['hotspot_score'].mean()
        st.metric("Avg Hotspot Score", f"{avg_score:.3f}")
    with col4:
        best_cluster = df.groupby('cluster')['hotspot_score'].mean().idxmin()
        st.metric("Best Cluster", f"Cluster {best_cluster}")
    
    st.divider()
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter_3d(
            df,
            x='length_km',
            y='voltage_level_kv',
            z='hotspot_score',
            color='cluster',
            size='hotspot_score',
            title='3D Hotspot Visualization'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(
            df,
            x='hotspot_score',
            nbins=20,
            title='Hotspot Score Distribution',
            color='cluster'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Risk categorization
    st.subheader("🎯 Risk Categorization")
    
    df['risk_level'] = pd.cut(
        df['hotspot_score'],
        bins=[0, 0.3, 0.7, 1.0],
        labels=['Low Risk', 'Medium Risk', 'High Risk']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        risk_summary = df['risk_level'].value_counts()
        fig = px.pie(
            values=risk_summary.values,
            names=risk_summary.index,
            title='Project Risk Distribution',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        risk_cluster = pd.crosstab(df['cluster'], df['risk_level'])
        fig = px.bar(
            risk_cluster,
            title='Risk Level by Cluster',
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # High priority projects
    st.subheader("🚨 High Priority Projects")
    high_risk = df[df['hotspot_score'] > 0.7].sort_values('hotspot_score', ascending=False)
    
    if len(high_risk) > 0:
        display_cols = ['project_id', 'hotspot_score', 'recommendation']
        st.dataframe(high_risk[display_cols].head(10))
    else:
        st.success("No high-risk projects detected!")
    
    # Export
    st.divider()
    export_cols = ['project_id', 'cluster', 'hotspot_score', 'anomaly_score', 'risk_level', 'recommendation']
    export_df = df[export_cols]
    csv = export_df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download Hotspot Analysis",
        data=csv,
        file_name=f"hotspot_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def show_advanced_ml_analysis():
    """Advanced ML analysis"""
    st.header("🔧 Advanced ML Analysis")
    st.info("Advanced machine learning analysis with uncertainty quantification and feature importance")
    
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Feature Importance Analysis", "Uncertainty Quantification", "Model Comparison"]
    )
    
    if analysis_type == "Feature Importance Analysis":
        st.subheader("🔍 Feature Importance Analysis")
        
        with st.spinner("Analyzing feature importance..."):
            cost_importance = st.session_state.powergrid_ml.get_feature_importance('cost')
            time_importance = st.session_state.powergrid_ml.get_feature_importance('time')
        
        col1, col2 = st.columns(2)
        
        with col1:
            cost_df = pd.DataFrame(list(cost_importance.items()), columns=['Feature', 'Importance'])
            cost_df = cost_df.sort_values('Importance', ascending=True).tail(15)
            
            fig = px.bar(
                cost_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title='Top 15 Features - Cost Prediction',
                color='Importance',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            time_df = pd.DataFrame(list(time_importance.items()), columns=['Feature', 'Importance'])
            time_df = time_df.sort_values('Importance', ascending=True).tail(15)
            
            fig = px.bar(
                time_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title='Top 15 Features - Time Prediction',
                color='Importance',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Uncertainty Quantification":
        st.subheader("📊 Uncertainty Quantification")
        
        df = load_data()
        sample_size = min(50, len(df))
        sample_df = df.sample(n=sample_size, random_state=42)
        
        with st.spinner("Calculating prediction uncertainties..."):
            uncertainties = []
            
            for _, project in sample_df.iterrows():
                project_dict = project.to_dict()
                
                cost_pred = st.session_state.powergrid_ml.predict_with_uncertainty(project_dict, 'cost')
                time_pred = st.session_state.powergrid_ml.predict_with_uncertainty(project_dict, 'time')
                
                uncertainties.append({
                    'project_id': project_dict.get('project_id', 'Unknown'),
                    'cost_prediction': cost_pred['prediction'],
                    'cost_std': cost_pred['uncertainty'],
                    'cost_confidence': cost_pred['confidence'],
                    'time_prediction': time_pred['prediction'],
                    'time_std': time_pred['uncertainty'],
                    'time_confidence': time_pred['confidence']
                })
        
        uncertainty_df = pd.DataFrame(uncertainties)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                uncertainty_df,
                x='cost_prediction',
                y='cost_std',
                size='cost_confidence',
                title='Cost Prediction Uncertainty'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                uncertainty_df,
                x='time_prediction',
                y='time_std',
                size='time_confidence',
                title='Time Prediction Uncertainty'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(uncertainty_df.round(3))
    
    elif analysis_type == "Model Comparison":
        st.subheader("🏆 Model Comparison")
        
        model_types = ['random_forest', 'xgboost', 'lightgbm']
        comparison_results = []
        
        for model_type in model_types:
            cost_metrics = st.session_state.powergrid_ml.get_model_performance(model_type, 'cost')
            time_metrics = st.session_state.powergrid_ml.get_model_performance(model_type, 'time')
            
            comparison_results.append({
                'Model': model_type.upper(),
                'Cost_R2': cost_metrics['r2'],
                'Cost_MAE': cost_metrics['mae'],
                'Time_R2': time_metrics['r2'],
                'Time_MAE': time_metrics['mae'],
                'Overall_Score': (cost_metrics['r2'] + time_metrics['r2']) / 2
            })
        
        comparison_df = pd.DataFrame(comparison_results)
        comparison_df = comparison_df.sort_values('Overall_Score', ascending=False)
        
        st.dataframe(comparison_df.round(4))
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                comparison_df,
                x='Model',
                y=['Cost_R2', 'Time_R2'],
                title='R² Score Comparison',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                comparison_df,
                x='Model',
                y=['Cost_MAE', 'Time_MAE'],
                title='MAE Comparison (Lower is Better)',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        best_model = comparison_df.iloc[0]['Model']
        st.success(f"🏆 Recommended Model: {best_model}")

def show_model_performance():
    """Model performance metrics"""
    st.header("📋 Model Performance")
    st.info("View performance metrics for all trained models")
    
    metrics_path = os.path.join(parent_dir, 'models', 'metrics.json')
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    st.subheader("📊 Model Performance Summary")
    
    # Cost models
    if 'cost_models' in metrics:
        st.subheader("💰 Cost Prediction Models")
        cost_df = pd.DataFrame(metrics['cost_models']).T.round(4)
        st.dataframe(cost_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                x=cost_df.index,
                y=cost_df['MAE'],
                title='Cost Model - Mean Absolute Error',
                labels={'x': 'Model', 'y': 'MAE'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                x=cost_df.index,
                y=cost_df['R2'],
                title='Cost Model - R² Score',
                labels={'x': 'Model', 'y': 'R² Score'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Time models
    if 'time_models' in metrics:
        st.subheader("⏱️ Time Prediction Models")
        time_df = pd.DataFrame(metrics['time_models']).T.round(4)
        st.dataframe(time_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                x=time_df.index,
                y=time_df['MAE'],
                title='Time Model - Mean Absolute Error',
                labels={'x': 'Model', 'y': 'MAE'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                x=time_df.index,
                y=time_df['R2'],
                title='Time Model - R² Score',
                labels={'x': 'Model', 'y': 'R² Score'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Overall summary
    st.subheader("📈 Overall Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    if 'cost_models' in metrics:
        best_cost = min(metrics['cost_models'].keys(), 
                      key=lambda x: metrics['cost_models'][x]['MAE'])
        best_cost_r2 = metrics['cost_models'][best_cost]['R2']
        
        with col1:
            st.metric("Best Cost Model", best_cost)
        with col2:
            st.metric("Best Cost R²", f"{best_cost_r2:.4f}")
    
    if 'time_models' in metrics:
        best_time = min(metrics['time_models'].keys(),
                      key=lambda x: metrics['time_models'][x]['MAE'])
        best_time_r2 = metrics['time_models'][best_time]['R2']
        
        with col3:
            st.metric("Best Time Model", best_time)
        with col4:
            st.metric("Best Time R²", f"{best_time_r2:.4f}")
    
    # Feature importance
    feature_importance_path = os.path.join(parent_dir, 'models', 'feature_importance.json')
    
    with open(feature_importance_path, 'r') as f:
        feature_importance = json.load(f)
    
    st.subheader("🔍 Feature Importance")
    
    if 'cost_features' in feature_importance:
        st.write("**Cost Prediction - Top Features:**")
        cost_features = pd.DataFrame(list(feature_importance['cost_features'].items()), 
                                   columns=['Feature', 'Importance'])
        cost_features = cost_features.sort_values('Importance', ascending=False).head(10)
        
        fig = px.bar(
            data_frame=cost_features,
            x='Importance',
            y='Feature',
            orientation='h',
            title='Top 10 Features for Cost Prediction'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if 'time_features' in feature_importance:
        st.write("**Time Prediction - Top Features:**")
        time_features = pd.DataFrame(list(feature_importance['time_features'].items()), 
                                   columns=['Feature', 'Importance'])
        time_features = time_features.sort_values('Importance', ascending=False).head(10)
        
        fig = px.bar(
            data_frame=time_features,
            x='Importance',
            y='Feature',
            orientation='h',
            title='Top 10 Features for Time Prediction'
        )
        st.plotly_chart(fig, use_container_width=True)

# Run the app
if __name__ == "__main__":
    main()