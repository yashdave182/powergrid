@echo off
REM Deployment script for Streamlit Cloud on Windows

echo Starting POWERGRID Project Analytics deployment...

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements_streamlit.txt

REM Check if installation was successful
if %ERRORLEVEL% EQU 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    exit /b 1
)

REM Verify that required files exist
echo Checking for required files...
set REQUIRED_FILES=streamlit_app.py requirements_streamlit.txt data/processed/processed_data.csv models/preprocessor.pkl models/cost_xgboost.pkl models/time_xgboost.pkl

for %%f in (%REQUIRED_FILES%) do (
    if exist "%%f" (
        echo ✅ Found %%f
    ) else (
        echo ⚠️  Missing %%f
    )
)

echo Deployment preparation complete!
echo To run the app locally: streamlit run streamlit_app.py