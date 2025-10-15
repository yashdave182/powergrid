@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Generating synthetic data...
python src/data/generate_synthetic_data.py

echo Preprocessing data...
python src/data/preprocess.py

echo Training models...
python src/models/train_models.py

echo Running tests...
python tests/test_mvp.py

echo.
echo Setup complete! You can now run:
echo 1. streamlit run src/dashboard/app.py
echo 2. uvicorn src.api.main:app --reload