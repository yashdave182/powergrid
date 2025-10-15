# Deploying to Streamlit Cloud

## Prerequisites

1. A GitHub account
2. This repository forked to your GitHub account

## Deployment Steps

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your forked repository
5. Set the following configuration:
   - **Main file path**: `streamlit_app.py`
   - **Python version**: 3.9 or higher
   - **Dependencies file**: `requirements.txt`
6. Click "Deploy!"

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure all dependencies are listed in `requirements.txt`
2. **File not found errors**: Verify that file paths in the code match the repository structure
3. **Model loading issues**: Ensure that all model files (.pkl) are included in the repository

### Dependency Issues

If you encounter `ModuleNotFoundError` for any package:

1. Check that the package is listed in `requirements.txt`
2. Verify the package version is compatible with Streamlit Cloud
3. Some packages may need to be installed with specific flags

### Data Loading Issues

If data doesn't load properly:

1. Ensure `data/processed/processed_data.csv` exists in the repository
2. Check that the file paths in the code match your directory structure
3. Large files may need to be loaded from external storage

## File Structure for Deployment

```
powergrid_mvp/
├── streamlit_app.py          # Entry point for Streamlit Cloud
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── data/
│   └── processed/
│       └── processed_data.csv
├── models/
│   ├── cost_lightgbm.pkl
│   ├── cost_random_forest.pkl
│   ├── cost_xgboost.pkl
│   ├── time_lightgbm.pkl
│   ├── time_random_forest.pkl
│   ├── time_xgboost.pkl
│   ├── preprocessor.pkl
│   ├── metrics.json
│   └── feature_importance.json
└── src/
    ├── dashboard/
    │   └── app.py
    ├── models/
    │   ├── powergrid_ml.py
    │   ├── predictor.py
    │   └── hotspot_analyzer.py
    └── data/
        └── powergrid_preprocessing.py
```

## Support

If you continue to experience issues, please check the [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-cloud) or open an issue in this repository.