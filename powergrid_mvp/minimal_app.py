"""
Minimal Streamlit app for POWERGRID Project Analytics
This is a fallback version that works with minimal dependencies
"""

import streamlit as st
import sys
import os

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="POWERGRID Project Analytics",
        page_icon="🔌",
        layout="wide"
    )
    
    st.title("🔌 POWERGRID Project Analytics")
    
    st.info("⚠️ This is a minimal version of the app due to deployment issues.")
    
    st.subheader("System Information")
    st.write(f"Python version: {sys.version}")
    st.write(f"Working directory: {os.getcwd()}")
    
    st.subheader("Available Libraries")
    
    # Check what libraries are available
    libraries = [
        "streamlit",
        "pandas",
        "numpy",
        "plotly",
        "sklearn",
        "xgboost",
        "lightgbm"
    ]
    
    for lib in libraries:
        try:
            __import__(lib)
            st.success(f"✅ {lib} - Available")
        except ImportError:
            st.error(f"❌ {lib} - Not available")
    
    st.subheader("Next Steps")
    st.write("""
    To get the full functionality of this app:
    
    1. Make sure all required dependencies are installed
    2. Check that the requirements.txt file is properly configured
    3. Ensure all model files are included in the repository
    4. Verify that the data files are in the correct location
    
    For deployment to Streamlit Cloud:
    - Set the main file path to `streamlit_app.py`
    - Set the requirements file path to `requirements_streamlit.txt`
    """)

if __name__ == "__main__":
    main()