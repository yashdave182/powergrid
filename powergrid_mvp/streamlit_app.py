"""
Streamlit app for POWERGRID Project Analytics
This is a simplified version for Streamlit Cloud deployment
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the main app
from src.dashboard.app import main

if __name__ == "__main__":
    main()