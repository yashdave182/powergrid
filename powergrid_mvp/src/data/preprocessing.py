import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import os

def preprocess_data(input_path, output_path):
    """Preprocess the raw project data."""
    # Load raw data
    print(f"Loading data from {input_path}...")
    data = pd.read_csv(input_path)

    # Handle missing values
    print("Handling missing values...")
    imputer = SimpleImputer(strategy='mean')
    numerical_columns = data.select_dtypes(include=['float64', 'int64']).columns
    data[numerical_columns] = imputer.fit_transform(data[numerical_columns])

    # Encode categorical variables
    print("Encoding categorical variables...")
    categorical_columns = data.select_dtypes(include=['object']).columns
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoded_data = pd.DataFrame(encoder.fit_transform(data[categorical_columns]))
    encoded_data.columns = encoder.get_feature_names_out(categorical_columns)
    data = data.drop(columns=[col for col in categorical_columns if col != 'start_date']).join(encoded_data)

    # Retain and format 'start_date'
    if 'start_date' in data.columns:
        data['start_date'] = pd.to_datetime(data['start_date'])

    # Normalize numerical variables
    print("Normalizing numerical variables...")
    scaler = StandardScaler()
    data[numerical_columns] = scaler.fit_transform(data[numerical_columns])

    # Save processed data
    print(f"Saving processed data to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data.to_csv(output_path, index=False)
    print("Data preprocessing completed successfully.")

if __name__ == "__main__":
    raw_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'raw', 'projects_data.csv')
    processed_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed', 'processed_data.csv')
    preprocess_data(raw_data_path, processed_data_path)