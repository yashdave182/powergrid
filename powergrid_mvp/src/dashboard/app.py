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
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Projects",
                len(df),
                delta=None
            )
        
        with col2:
            high_risk_count = len(df[df['cost_overrun_percentage'] > 20])
            st.metric(
                "High Risk Projects",
                high_risk_count,
                delta=f"{high_risk_count/len(df)*100:.1f}%"
            )
        
        with col3:
            avg_cost_overrun = df['cost_overrun_percentage'].mean()
            st.metric(
                "Avg Cost Overrun",
                f"{avg_cost_overrun:.1f}%",
                delta=None
            )
        
        with col4:
            avg_time_overrun = df['time_overrun_percentage'].mean()
            st.metric(
                "Avg Time Overrun",
                f"{avg_time_overrun:.1f}%",
                delta=None
            )
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Project type distribution
            fig = px.pie(
                df,
                names='project_type',
                title='Project Type Distribution',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Regional distribution
            region_counts = df.groupby('region').size().reset_index()
            region_counts.columns = ['region', 'count']
            fig = px.bar(
                region_counts,
                x='region',
                y='count',
                title='Projects by Region',
                color='count',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Additional charts and analysis can be added here
        
    except Exception as e:
        st.error(f"Error loading data: {e}")

def show_single_prediction():
    """Single project prediction interface"""
    st.header("🎯 Single Project Prediction")
    st.info("Enter project details to get cost and time overrun predictions")
    
    # Placeholder for prediction form
    st.warning("Single prediction functionality coming soon!")

def show_batch_analysis():
    """Batch project analysis"""
    st.header("📈 Batch Analysis")
    st.info("Upload multiple projects for batch prediction and analysis")
    
    # Placeholder for batch analysis
    st.warning("Batch analysis functionality coming soon!")

def show_risk_hotspots():
    """Risk hotspot identification"""
    st.header("🔍 Risk Hotspots")
    st.info("Identify regions and project types with highest risk")
    
    # Placeholder for risk hotspots
    st.warning("Risk hotspot analysis coming soon!")

def show_model_performance():
    """Model performance metrics"""
    st.header("📋 Model Performance")
    st.info("View performance metrics for all trained models")
    
    # Placeholder for model performance
    st.warning("Model performance dashboard coming soon!")

# Run the app
if __name__ == "__main__":
    main()