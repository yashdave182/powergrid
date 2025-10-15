"""
Streamlit app for POWERGRID Project Analytics
This is the main entry point for Streamlit Cloud deployment
"""

import sys
import os
import streamlit as st

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main application entry point"""
    try:
        # Set page config first
        st.set_page_config(
            page_title="POWERGRID Project Analytics",
            page_icon="🔌",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Import and run the main dashboard app
        from src.dashboard.app import main as dashboard_main
        dashboard_main()
    except ImportError as e:
        st.error(f"Failed to import dashboard app: {str(e)}")
        st.info("Make sure all required dependencies are installed.")
        st.code("""
# Install required dependencies:
pip install -r requirements_streamlit.txt
""")
        
        # Show a minimal app as fallback
        st.title("POWERGRID Project Analytics")
        st.error("❌ Failed to load the full dashboard")
        st.write("Please check that all dependencies are installed:")
        st.code("""
streamlit==1.25.0
pandas==2.0.3
numpy==1.24.3
plotly==5.15.0
scikit-learn==1.3.0
xgboost==1.7.6
lightgbm==4.0.0
joblib==1.3.1
matplotlib==3.7.2
seaborn==0.12.2
python-dotenv==1.0.0
pyyaml==6.0.1
""")
        
        # Try to show basic info
        st.subheader("System Info")
        st.write(f"Python version: {sys.version}")
        st.write(f"Working directory: {os.getcwd()}")
        st.write(f"sys.path: {sys.path}")
        
    except Exception as e:
        st.error(f"An error occurred while running the app: {str(e)}")
        st.info("Please check the console for more details.")
        
        # Show traceback for debugging
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()