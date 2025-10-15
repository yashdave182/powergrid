import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.predictor import ProjectPredictor

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
        st.success("✅ Models loaded successfully!")

# Load processed data for overview
@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/processed_data.csv')
    # Date features
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
        "📋 Model Performance"
    ])
    
    if page == "📊 Overview":
        show_overview()
    elif page == "🎯 Single Project Prediction":
        show_single_prediction()
    elif page == "📈 Batch Analysis":
        show_batch_analysis()
    elif page == "🔍 Risk Hotspots":
        show_risk_hotspots()
    elif page == "📋 Model Performance":
        show_model_performance()

def show_overview():
    """Overview dashboard"""
    st.header("📊 Project Portfolio Overview")
    
    try:
        df = load_data()
        
        # KPIs - using available columns from processed data
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Projects",
                len(df),
                delta=None
            )
        
        with col2:
            # Check if cost_overrun_percentage exists, otherwise use a placeholder
            if 'cost_overrun_percentage' in df.columns:
                high_risk_count = len(df[df['cost_overrun_percentage'] > 20])
                st.metric(
                    "High Risk Projects",
                    high_risk_count,
                    delta=f"{high_risk_count/len(df)*100:.1f}%"
                )
            else:
                st.metric(
                    "High Risk Projects",
                    "N/A",
                    delta="Data not available"
                )
        
        with col3:
            if 'cost_overrun_percentage' in df.columns:
                avg_cost_overrun = df['cost_overrun_percentage'].mean()
                st.metric(
                    "Avg Cost Overrun",
                    f"{avg_cost_overrun:.1f}%",
                    delta=None
                )
            else:
                st.metric(
                    "Avg Cost Overrun",
                    "N/A",
                    delta="Data not available"
                )
        
        with col4:
            if 'time_overrun_percentage' in df.columns:
                avg_time_overrun = df['time_overrun_percentage'].mean()
                st.metric(
                    "Avg Time Overrun",
                    f"{avg_time_overrun:.1f}%",
                    delta=None
                )
            else:
                st.metric(
                    "Avg Time Overrun",
                    "N/A",
                    delta="Data not available"
                )
        
        st.divider()
        
        # Charts - using available numerical features
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution of terrain difficulty
            if 'terrain_difficulty_score' in df.columns:
                fig = px.histogram(
                    df,
                    x='terrain_difficulty_score',
                    title='Terrain Difficulty Distribution',
                    nbins=20
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Terrain difficulty data not available for visualization")
        
        with col2:
            # Distribution of project length
            if 'length_km' in df.columns:
                fig = px.histogram(
                    df,
                    x='length_km',
                    title='Project Length Distribution (km)',
                    nbins=20
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Project length data not available for visualization")
        
        st.divider()
        
        # Additional charts using available numerical features
        col1, col2 = st.columns(2)
        
        with col1:
            # Voltage level distribution
            if 'voltage_level_kv' in df.columns:
                fig = px.box(
                    df,
                    y='voltage_level_kv',
                    title='Voltage Level Distribution (kV)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Number of towers distribution
            if 'num_towers' in df.columns:
                fig = px.box(
                    df,
                    y='num_towers',
                    title='Number of Towers Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Show data summary
        st.subheader("Data Summary")
        st.write(f"Dataset shape: {df.shape}")
        st.write(f"Number of features: {len(df.columns)}")
        st.write(f"Available numerical features: {len(df.select_dtypes(include=[np.number]).columns)}")
        
    except Exception as e:
        st.error(f"Error loading data: {e}")

def show_single_prediction():
    """Single project prediction interface"""
    st.header("🎯 Single Project Prediction")
    st.info("Enter project details to get cost and time overrun predictions")
    
    # Create a more user-friendly input form
    with st.form("project_prediction_form"):
        st.subheader("Project Details")
        
        # Basic project information
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
        
        # Submit button
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
            try:
                predictions = st.session_state.predictor.predict(project_data)
                
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
                
                # Cost predictions
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("💰 Cost Analysis")
                    st.metric("Estimated Cost", f"₹{predictions['estimated_cost_inr']:,.0f}")
                    st.metric("Predicted Cost", f"₹{predictions['predicted_cost_inr']:,.0f}")
                    st.metric("Cost Overrun", f"{predictions['cost_overrun_percentage']:.1f}%")
                    if predictions['cost_overrun_inr'] > 0:
                        st.error(f"Expected cost increase: ₹{predictions['cost_overrun_inr']:,.0f}")
                    else:
                        st.success(f"Expected cost savings: ₹{abs(predictions['cost_overrun_inr']):,.0f}")
                
                # Time predictions
                with col2:
                    st.subheader("⏱️ Timeline Analysis")
                    st.metric("Estimated Duration", f"{predictions['estimated_duration_days']} days")
                    st.metric("Predicted Duration", f"{predictions['predicted_duration_days']} days")
                    st.metric("Time Overrun", f"{predictions['time_overrun_percentage']:.1f}%")
                    if predictions['time_overrun_days'] > 0:
                        st.error(f"Expected delay: {predictions['time_overrun_days']} days")
                    else:
                        st.success(f"Expected time savings: {abs(predictions['time_overrun_days'])} days")
                
                st.divider()
                
                # Recommendations based on risk level
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
                
            except Exception as e:
                st.error(f"Error making predictions: {e}")
                st.write("Please check your input data and try again.")

def show_batch_analysis():
    """Batch project analysis"""
    st.header("📈 Batch Analysis")
    st.info("Upload multiple projects for batch prediction and analysis")
    
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if uploaded_file is not None:
        try:
            batch_data = pd.read_csv(uploaded_file)
            
            # Convert DataFrame to list of dictionaries for batch prediction
            projects_list = batch_data.to_dict('records')
            
            with st.spinner("🧠 Analyzing batch data..."):
                predictions = st.session_state.predictor.batch_predict(projects_list)
            
            # Convert predictions to DataFrame for display
            pred_df = pd.DataFrame(predictions)
            
            st.subheader("📊 Batch Prediction Results")
            st.dataframe(pred_df)
            
            # Summary statistics
            if 'cost_overrun_percentage' in pred_df.columns and 'time_overrun_percentage' in pred_df.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Cost Overrun", f"{pred_df['cost_overrun_percentage'].mean():.1f}%")
                with col2:
                    st.metric("Average Time Overrun", f"{pred_df['time_overrun_percentage'].mean():.1f}%")
                with col3:
                    high_risk_count = len(pred_df[pred_df['risk_category'] == 'High'])
                    st.metric("High Risk Projects", high_risk_count)
            
            # Download results
            csv = pred_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Predictions CSV",
                data=csv,
                file_name="batch_predictions.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Error processing batch data: {e}")
            st.write("Please ensure your CSV file has the correct format with all required columns.")

def show_risk_hotspots():
    """Risk hotspot identification"""
    st.header("🔍 Risk Hotspots")
    st.info("Identify regions and project types with highest risk")
    
    try:
        # Load cluster assignments
        cluster_data = pd.read_csv('outputs/cluster_assignments.csv')
        
        st.subheader("📊 Cluster Analysis")
        
        # Show cluster distribution
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
        
        # Display cluster details
        st.subheader("🔍 Cluster Details")
        
        # Group by cluster and show statistics
        cluster_stats = cluster_data.groupby('cluster').agg({
            'length_km': ['mean', 'std'],
            'voltage_level_kv': 'mean',
            'terrain_difficulty_score': 'mean',
            'project_complexity_score': 'mean'
        }).round(2)
        
        cluster_stats.columns = ['_'.join(col).strip() for col in cluster_stats.columns]
        st.dataframe(cluster_stats)
        
        st.divider()
        
        # Show hotspot visualization
        st.subheader("🗺️ Hotspot Visualization")
        try:
            st.image('outputs/hotspot_clusters.png', caption='Project Risk Hotspots Clustering', use_column_width=True)
        except Exception as e:
            st.warning("Cluster visualization not available")
        
        st.divider()
        
        # Risk assessment based on clusters
        st.subheader("⚠️ Risk Assessment")
        
        # Analyze which clusters represent higher risk based on feature values
        for cluster_id in sorted(cluster_data['cluster'].unique()):
            cluster_subset = cluster_data[cluster_data['cluster'] == cluster_id]
            
            # Calculate risk indicators
            avg_length = cluster_subset['length_km'].mean()
            avg_terrain = cluster_subset['terrain_difficulty_score'].mean() if 'terrain_difficulty_score' in cluster_subset.columns else 5.0
            avg_complexity = cluster_subset['project_complexity_score'].mean() if 'project_complexity_score' in cluster_subset.columns else 0.5
            
            # Simple risk scoring
            risk_score = (avg_length / 200) * 0.3 + (avg_terrain / 10) * 0.4 + avg_complexity * 0.3
            
            if risk_score > 0.7:
                risk_level = "🔴 High Risk"
                color = "error"
            elif risk_score > 0.4:
                risk_level = "🟡 Medium Risk"
                color = "warning"
            else:
                risk_level = "🟢 Low Risk"
                color = "success"
            
            with st.expander(f"Cluster {cluster_id} - {risk_level}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Projects in Cluster", len(cluster_subset))
                with col2:
                    st.metric("Avg Length (km)", f"{avg_length:.1f}")
                with col3:
                    st.metric("Avg Terrain Difficulty", f"{avg_terrain:.1f}")
                
                if color == "error":
                    st.error(f"Risk Score: {risk_score:.2f}")
                elif color == "warning":
                    st.warning(f"Risk Score: {risk_score:.2f}")
                else:
                    st.success(f"Risk Score: {risk_score:.2f}")
        
    except FileNotFoundError:
        st.error("Cluster assignments file not found. Please run hotspot identification first.")
    except Exception as e:
        st.error(f"Error loading hotspot data: {e}")

def show_model_performance():
    """Model performance metrics"""
    st.header("📋 Model Performance")
    st.info("View performance metrics for all trained models")
    
    try:
        # Load metrics from JSON file
        metrics_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'models', 'metrics.json')
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        st.subheader("📊 Model Performance Summary")
        
        # Display cost prediction metrics
        if 'cost_models' in metrics:
            st.subheader("💰 Cost Prediction Models")
            cost_df = pd.DataFrame(metrics['cost_models']).T
            cost_df = cost_df.round(4)
            st.dataframe(cost_df)
            
            # Visualize cost model performance
            if not cost_df.empty:
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
        
        # Display time prediction metrics
        if 'time_models' in metrics:
            st.subheader("⏱️ Time Prediction Models")
            time_df = pd.DataFrame(metrics['time_models']).T
            time_df = time_df.round(4)
            st.dataframe(time_df)
            
            # Visualize time model performance
            if not time_df.empty:
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
        
        # Overall performance summary
        st.subheader("📈 Overall Performance Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        if 'cost_models' in metrics and metrics['cost_models']:
            best_cost_model = min(metrics['cost_models'].keys(), 
                                key=lambda x: metrics['cost_models'][x]['MAE'])
            best_cost_r2 = metrics['cost_models'][best_cost_model]['R2']
            
            with col1:
                st.metric("Best Cost Model", best_cost_model)
            with col2:
                st.metric("Best Cost R²", f"{best_cost_r2:.4f}")
        
        if 'time_models' in metrics and metrics['time_models']:
            best_time_model = min(metrics['time_models'].keys(), 
                                key=lambda x: metrics['time_models'][x]['MAE'])
            best_time_r2 = metrics['time_models'][best_time_model]['R2']
            
            with col3:
                st.metric("Best Time Model", best_time_model)
            with col4:
                st.metric("Best Time R²", f"{best_time_r2:.4f}")
        
        # Feature importance (if available)
        try:
            feature_importance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'models', 'feature_importance.json')
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
                
        except FileNotFoundError:
            st.info("Feature importance data not available.")
        
    except FileNotFoundError:
        st.error("Model metrics file not found. Please train models first.")
    except Exception as e:
        st.error(f"Error loading model performance data: {e}")

# Run the app
if __name__ == "__main__":
    main()