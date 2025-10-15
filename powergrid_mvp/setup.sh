#!/bin/bash
# Setup script for Streamlit Cloud deployment

echo "Starting POWERGRID Project Analytics setup..."

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Copy config file if it exists in the powergrid_mvp directory
if [ -f "powergrid_mvp/.streamlit/config.toml" ]; then
    cp powergrid_mvp/.streamlit/config.toml .streamlit/
    echo "✅ Copied Streamlit config"
fi

# Check if we're in the right directory
if [ -f "streamlit_app.py" ]; then
    echo "✅ Found streamlit_app.py in current directory"
else
    echo "⚠️  streamlit_app.py not found in current directory"
    # Try to find it
    if [ -f "powergrid_mvp/streamlit_app.py" ]; then
        echo "✅ Found streamlit_app.py in powergrid_mvp directory"
    else
        echo "❌ streamlit_app.py not found anywhere"
    fi
fi

echo "Setup complete!"