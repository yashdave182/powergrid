# POWERGRID Project Analytics Dashboard

A comprehensive analytics dashboard for predicting and managing power grid project risks, costs, and timelines.

## Features

- **Single Project Prediction**: Predict cost and time overruns for individual projects
- **Batch Analysis**: Process multiple projects at once
- **Risk Hotspots**: Identify high-risk regions and project types
- **Enhanced Hotspot Analysis**: Advanced clustering and anomaly detection
- **Model Performance**: View detailed metrics for all trained models

## Deployment to Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your forked repository
4. Set the main file path to `streamlit_app.py`
5. Click "Deploy!"

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd powergrid_mvp

# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard

```bash
# Run the Streamlit dashboard
streamlit run streamlit_app.py
```

## Project Structure

```
powergrid_mvp/
├── streamlit_app.py          # Streamlit Cloud entry point
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── src/
│   ├── dashboard/
│   │   └── app.py           # Main dashboard application
│   ├── models/
│   │   ├── powergrid_ml.py  # ML models
│   │   ├── predictor.py     # Project predictor
│   │   └── hotspot_analyzer.py  # Hotspot analysis
│   └── data/
│       └── powergrid_preprocessing.py  # Data preprocessing
├── data/
│   └── processed/
│       └── processed_data.csv  # Processed project data
└── models/
    ├── cost_model_xgboost.pkl     # Trained cost model
    ├── time_model_lightgbm.pkl    # Trained time model
    └── preprocessor.pkl           # Data preprocessor
```

## Troubleshooting

### ModuleNotFoundError

If you encounter `ModuleNotFoundError` when deploying to Streamlit Cloud:

1. Ensure all required dependencies are listed in `requirements.txt`
2. Check that the file paths in `streamlit_app.py` are correct
3. Verify that the main file path in Streamlit Cloud is set to `streamlit_app.py`

### Data Loading Issues

If data doesn't load properly:

1. Ensure `data/processed/processed_data.csv` exists
2. Check that the file paths in the code match your directory structure

## License

This project is licensed under the MIT License.