#!/bin/bash
# Deployment script for Streamlit Cloud

echo "Starting POWERGRID Project Analytics deployment..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements_streamlit.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Verify that required files exist
echo "Checking for required files..."
REQUIRED_FILES=(
    "streamlit_app.py"
    "requirements_streamlit.txt"
    "data/processed/processed_data.csv"
    "models/preprocessor.pkl"
    "models/cost_xgboost.pkl"
    "models/time_xgboost.pkl"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Found $file"
    else
        echo "⚠️  Missing $file"
    fi
done

echo "Deployment preparation complete!"
echo "To run the app locally: streamlit run streamlit_app.py"