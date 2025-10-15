import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import os

def identify_hotspots(data, outputs_path):
    """Identify hotspots using clustering."""
    print("Identifying hotspots...")

    # Use all available features for clustering
    features = data

    # Standardize features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(scaled_features)

    # Add cluster assignments to data
    data['cluster'] = clusters

    # Save cluster assignments
    cluster_output_path = os.path.join(outputs_path, 'cluster_assignments.csv')
    data.to_csv(cluster_output_path, index=False)
    print(f"Cluster assignments saved to {cluster_output_path}")

    # Visualize clusters (example: first two features)
    plt.figure(figsize=(8, 6))
    plt.scatter(scaled_features[:, 0], scaled_features[:, 1], c=clusters, cmap='viridis', s=50)
    plt.title("Hotspot Clusters")
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.colorbar(label="Cluster")

    # Save visualization
    visualization_path = os.path.join(outputs_path, 'hotspot_clusters.png')
    plt.savefig(visualization_path)
    print(f"Cluster visualization saved to {visualization_path}")

if __name__ == "__main__":
    processed_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed', 'processed_data.csv')
    outputs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs')

    print(f"Loading processed data from {processed_data_path}...")
    data = pd.read_csv(processed_data_path)

    os.makedirs(outputs_path, exist_ok=True)

    identify_hotspots(data, outputs_path)
    print("Hotspot identification completed.")