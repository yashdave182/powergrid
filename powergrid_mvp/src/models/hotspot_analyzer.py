import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class PowerGridHotspotAnalyzer:
    """
    Advanced hotspot identification for POWERGRID projects using multiple clustering techniques
    and anomaly detection methods
    """
    
    def __init__(self, models_path=None):
        if models_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.models_path = os.path.join(base_dir, 'models') + os.sep
        else:
            self.models_path = models_path
            
        self.clustering_models = {}
        self.anomaly_models = {}
        self.cluster_assignments = None
        self.hotspot_scores = None
        self.risk_categories = None
        
    def create_risk_features(self, df):
        """
        Create comprehensive risk features for clustering analysis
        """
        print("🔍 Creating comprehensive risk features...")
        
        risk_features = pd.DataFrame()
        
        # Cost risk features
        risk_features['cost_overrun_risk'] = (
            df.get('material_cost_ratio', 0) * 0.3 +
            df.get('labor_cost_ratio', 0) * 0.25 +
            df.get('cost_escalation_risk', 0) * 0.25 +
            df.get('demand_supply_impact', 0) * 0.2
        )
        
        # Timeline risk features
        risk_features['timeline_risk'] = (
            df.get('regulatory_complexity_score', 0) * 0.3 +
            df.get('monsoon_impact_score', 0) * 0.25 +
            df.get('timeline_pressure_score', 0) * 0.25 +
            df.get('critical_path_risk', 0) * 0.2
        )
        
        # Technical risk features
        risk_features['technical_risk'] = (
            df.get('technology_risk', 0) * 0.4 +
            df.get('project_complexity_score', 0) * 0.3 +
            df.get('vendor_risk_score', 0) * 0.3
        )
        
        # Environmental risk features
        risk_features['environmental_risk'] = (
            df.get('terrain_difficulty_score', 0) * 0.4 +
            df.get('weather_impact_ratio', 0) * 0.3 +
            df.get('seasonal_factor', 0) * 0.3
        )
        
        # Resource risk features
        risk_features['resource_risk'] = (
            df.get('resource_availability_score', 0) * 0.4 +
            df.get('trained_manpower_availability', 0) * 0.3 +
            df.get('vendor_performance_score', 0) * 0.3
        )
        
        # Historical risk features
        risk_features['historical_risk'] = (
            df.get('historical_delay_pattern', 0) * 0.5 +
            df.get('regional_delay_factor', 0) * 0.5
        )
        
        # Composite risk score
        risk_features['composite_risk_score'] = (
            risk_features['cost_overrun_risk'] * 0.25 +
            risk_features['timeline_risk'] * 0.25 +
            risk_features['technical_risk'] * 0.2 +
            risk_features['environmental_risk'] * 0.15 +
            risk_features['resource_risk'] * 0.1 +
            risk_features['historical_risk'] * 0.05
        )
        
        # Project type risk multipliers
        project_type_multipliers = {
            'substation': 1.2,  # Higher complexity
            'overhead_line': 1.0,  # Standard complexity
            'underground_cable': 1.4  # Highest complexity
        }
        
        if 'project_type' in df.columns:
            risk_features['project_type_multiplier'] = df['project_type'].map(
                project_type_multipliers
            ).fillna(1.0)
            
            risk_features['composite_risk_score'] *= risk_features['project_type_multiplier']
        
        print("✅ Risk features created successfully")
        return risk_features
    
    def perform_multiple_clustering(self, X, n_clusters_range=range(2, 11)):
        """
        Perform multiple clustering algorithms and select the best one
        """
        print("🔬 Performing multiple clustering analysis...")
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        clustering_results = {}
        
        # K-Means Clustering
        print("  Running K-Means clustering...")
        kmeans_scores = {}
        for n_clusters in n_clusters_range:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            
            silhouette = silhouette_score(X_scaled, labels)
            calinski = calinski_harabasz_score(X_scaled, labels)
            
            kmeans_scores[n_clusters] = {
                'model': kmeans,
                'labels': labels,
                'silhouette': silhouette,
                'calinski': calinski
            }
        
        # Select best K-Means based on silhouette score
        best_k = max(kmeans_scores.keys(), key=lambda k: kmeans_scores[k]['silhouette'])
        clustering_results['kmeans'] = kmeans_scores[best_k]
        
        # DBSCAN Clustering
        print("  Running DBSCAN clustering...")
        dbscan_scores = {}
        eps_values = [0.1, 0.3, 0.5, 0.7, 1.0]
        
        for eps in eps_values:
            dbscan = DBSCAN(eps=eps, min_samples=5)
            labels = dbscan.fit_predict(X_scaled)
            
            # Only evaluate if we have more than one cluster
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            if n_clusters > 1:
                silhouette = silhouette_score(X_scaled, labels)
                dbscan_scores[eps] = {
                    'model': dbscan,
                    'labels': labels,
                    'silhouette': silhouette,
                    'n_clusters': n_clusters
                }
        
        if dbscan_scores:
            best_eps = max(dbscan_scores.keys(), key=lambda eps: dbscan_scores[eps]['silhouette'])
            clustering_results['dbscan'] = dbscan_scores[best_eps]
        
        # Gaussian Mixture Model
        print("  Running Gaussian Mixture Model...")
        gmm_scores = {}
        for n_clusters in n_clusters_range:
            gmm = GaussianMixture(n_components=n_clusters, random_state=42)
            labels = gmm.fit_predict(X_scaled)
            
            silhouette = silhouette_score(X_scaled, labels)
            gmm_scores[n_clusters] = {
                'model': gmm,
                'labels': labels,
                'silhouette': silhouette
            }
        
        best_gmm_k = max(gmm_scores.keys(), key=lambda k: gmm_scores[k]['silhouette'])
        clustering_results['gmm'] = gmm_scores[best_gmm_k]
        
        # Agglomerative Clustering
        print("  Running Agglomerative Clustering...")
        agg_scores = {}
        for n_clusters in n_clusters_range:
            agg = AgglomerativeClustering(n_clusters=n_clusters)
            labels = agg.fit_predict(X_scaled)
            
            silhouette = silhouette_score(X_scaled, labels)
            agg_scores[n_clusters] = {
                'model': agg,
                'labels': labels,
                'silhouette': silhouette
            }
        
        best_agg_k = max(agg_scores.keys(), key=lambda k: agg_scores[k]['silhouette'])
        clustering_results['agglomerative'] = agg_scores[best_agg_k]
        
        # Select overall best clustering
        best_method = max(clustering_results.keys(), 
                         key=lambda method: clustering_results[method]['silhouette'])
        
        print(f"✅ Best clustering method: {best_method} (Silhouette: {clustering_results[best_method]['silhouette']:.3f})")
        
        return clustering_results, best_method, scaler
    
    def detect_anomalies(self, X):
        """
        Detect anomalies and extreme cases
        """
        print("🔍 Detecting anomalies...")
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X_scaled)
        
        # Get anomaly scores
        anomaly_scores = iso_forest.decision_function(X_scaled)
        
        # Convert to risk scores (higher = more risky)
        risk_scores = -anomaly_scores  # Invert so higher values indicate higher risk
        
        self.anomaly_models['isolation_forest'] = iso_forest
        
        print(f"✅ Detected {np.sum(anomaly_labels == -1)} anomalies out of {len(X)} projects")
        
        return anomaly_labels, risk_scores, scaler
    
    def calculate_hotspot_scores(self, clustering_results, anomaly_scores, best_method):
        """
        Calculate comprehensive hotspot scores
        """
        print("🎯 Calculating hotspot scores...")
        
        # Get best clustering labels
        best_labels = clustering_results[best_method]['labels']
        
        # Calculate cluster-based risk scores
        cluster_risk_scores = np.zeros(len(best_labels))
        
        for cluster_id in np.unique(best_labels):
            cluster_mask = best_labels == cluster_id
            
            # Risk factors for this cluster
            cluster_size = np.sum(cluster_mask)
            
            # Smaller clusters might be riskier (outliers)
            size_score = 1.0 / max(cluster_size, 1)
            
            # Anomaly scores in this cluster
            cluster_anomaly_scores = anomaly_scores[cluster_mask]
            avg_anomaly_score = np.mean(cluster_anomaly_scores)
            
            # Combined cluster risk score
            cluster_risk = (size_score * 0.3 + avg_anomaly_score * 0.7)
            cluster_risk_scores[cluster_mask] = cluster_risk
        
        # Combine with individual anomaly scores
        final_hotspot_scores = (
            cluster_risk_scores * 0.4 +  # Cluster-based risk
            anomaly_scores * 0.6  # Individual anomaly risk
        )
        
        # Normalize to 0-100 scale
        final_hotspot_scores = (
            (final_hotspot_scores - final_hotspot_scores.min()) / 
            (final_hotspot_scores.max() - final_hotspot_scores.min()) * 100
        )
        
        # Categorize hotspots
        hotspot_categories = pd.cut(
            final_hotspot_scores,
            bins=[0, 25, 50, 75, 100],
            labels=['Low Risk', 'Medium Risk', 'High Risk', 'Critical Hotspot']
        )
        
        print("✅ Hotspot scores calculated successfully")
        
        return final_hotspot_scores, hotspot_categories
    
    def visualize_hotspots(self, X, hotspot_scores, hotspot_categories, clustering_results, best_method):
        """
        Create comprehensive hotspot visualizations
        """
        print("📊 Creating hotspot visualizations...")
        
        # Create output directory
        output_dir = os.path.join(os.path.dirname(self.models_path), 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        # Reduce dimensions for visualization
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # PCA for 2D visualization
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X_scaled)
        
        # t-SNE for alternative visualization
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        X_tsne = tsne.fit_transform(X_scaled)
        
        # Create comprehensive visualization
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('POWERGRID Project Hotspot Analysis', fontsize=16, fontweight='bold')
        
        # 1. Clustering visualization (PCA)
        scatter1 = axes[0, 0].scatter(
            X_pca[:, 0], X_pca[:, 1], 
            c=clustering_results[best_method]['labels'],
            cmap='viridis', alpha=0.7, s=50
        )
        axes[0, 0].set_title(f'Project Clusters ({best_method}) - PCA View')
        axes[0, 0].set_xlabel('First Principal Component')
        axes[0, 0].set_ylabel('Second Principal Component')
        plt.colorbar(scatter1, ax=axes[0, 0])
        
        # 2. Hotspot scores (PCA)
        scatter2 = axes[0, 1].scatter(
            X_pca[:, 0], X_pca[:, 1],
            c=hotspot_scores, cmap='Reds', alpha=0.7, s=50
        )
        axes[0, 1].set_title('Hotspot Risk Scores - PCA View')
        axes[0, 1].set_xlabel('First Principal Component')
        axes[0, 1].set_ylabel('Second Principal Component')
        plt.colorbar(scatter2, ax=axes[0, 1], label='Risk Score')
        
        # 3. Hotspot categories (PCA)
        category_colors = {'Low Risk': 'green', 'Medium Risk': 'yellow', 
                          'High Risk': 'orange', 'Critical Hotspot': 'red'}
        for category in hotspot_categories.unique():
            mask = hotspot_categories == category
            axes[0, 2].scatter(
                X_pca[mask, 0], X_pca[mask, 1],
                c=category_colors.get(category, 'gray'),
                label=category, alpha=0.7, s=50
            )
        axes[0, 2].set_title('Risk Categories - PCA View')
        axes[0, 2].set_xlabel('First Principal Component')
        axes[0, 2].set_ylabel('Second Principal Component')
        axes[0, 2].legend()
        
        # 4. Clustering visualization (t-SNE)
        scatter4 = axes[1, 0].scatter(
            X_tsne[:, 0], X_tsne[:, 1],
            c=clustering_results[best_method]['labels'],
            cmap='viridis', alpha=0.7, s=50
        )
        axes[1, 0].set_title(f'Project Clusters ({best_method}) - t-SNE View')
        axes[1, 0].set_xlabel('t-SNE Component 1')
        axes[1, 0].set_ylabel('t-SNE Component 2')
        plt.colorbar(scatter4, ax=axes[1, 0])
        
        # 5. Hotspot scores distribution
        axes[1, 1].hist(hotspot_scores, bins=30, alpha=0.7, color='red', edgecolor='black')
        axes[1, 1].set_title('Distribution of Hotspot Risk Scores')
        axes[1, 1].set_xlabel('Risk Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].axvline(x=75, color='red', linestyle='--', label='High Risk Threshold')
        axes[1, 1].legend()
        
        # 6. Risk category distribution
        category_counts = hotspot_categories.value_counts()
        colors = [category_colors.get(cat, 'gray') for cat in category_counts.index]
        axes[1, 2].pie(category_counts.values, labels=category_counts.index, 
                      colors=colors, autopct='%1.1f%%', startangle=90)
        axes[1, 2].set_title('Distribution of Risk Categories')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}hotspot_clusters.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Hotspot visualizations saved to {output_dir}hotspot_clusters.png")
    
    def generate_hotspot_recommendations(self, df, hotspot_scores, hotspot_categories):
        """
        Generate specific recommendations for different hotspot categories
        """
        print("💡 Generating hotspot recommendations...")
        
        recommendations = {}
        
        # Critical Hotspots
        critical_mask = hotspot_categories == 'Critical Hotspot'
        if critical_mask.any():
            critical_projects = df[critical_mask].copy()
            critical_projects['risk_score'] = hotspot_scores[critical_mask]
            
            recommendations['Critical Hotspot'] = {
                'count': critical_mask.sum(),
                'avg_risk_score': hotspot_scores[critical_mask].mean(),
                'recommendations': [
                    'Immediate project review and intervention required',
                    'Consider project postponement or scope reduction',
                    'Allocate additional resources and expert teams',
                    'Implement daily monitoring and reporting',
                    'Prepare contingency plans and risk mitigation strategies'
                ],
                'top_projects': critical_projects.nlargest(5, 'risk_score')[
                    ['project_id', 'risk_score', 'project_type', 'location']
                ].to_dict('records') if 'project_id' in critical_projects.columns else []
            }
        
        # High Risk
        high_risk_mask = hotspot_categories == 'High Risk'
        if high_risk_mask.any():
            high_risk_projects = df[high_risk_mask].copy()
            high_risk_projects['risk_score'] = hotspot_scores[high_risk_mask]
            
            recommendations['High Risk'] = {
                'count': high_risk_mask.sum(),
                'avg_risk_score': hotspot_scores[high_risk_mask].mean(),
                'recommendations': [
                    'Enhanced project monitoring and control',
                    'Regular risk assessment reviews',
                    'Consider resource reallocation',
                    'Implement preventive measures',
                    'Weekly progress reviews with stakeholders'
                ],
                'top_projects': high_risk_projects.nlargest(10, 'risk_score')[
                    ['project_id', 'risk_score', 'project_type', 'location']
                ].to_dict('records') if 'project_id' in high_risk_projects.columns else []
            }
        
        # Medium Risk
        medium_risk_mask = hotspot_categories == 'Medium Risk'
        if medium_risk_mask.any():
            recommendations['Medium Risk'] = {
                'count': medium_risk_mask.sum(),
                'avg_risk_score': hotspot_scores[medium_risk_mask].mean(),
                'recommendations': [
                    'Standard project monitoring procedures',
                    'Monthly risk assessments',
                    'Maintain current resource allocation',
                    'Regular progress tracking',
                    'Identify potential risk factors early'
                ]
            }
        
        # Low Risk
        low_risk_mask = hotspot_categories == 'Low Risk'
        if low_risk_mask.any():
            recommendations['Low Risk'] = {
                'count': low_risk_mask.sum(),
                'avg_risk_score': hotspot_scores[low_risk_mask].mean(),
                'recommendations': [
                    'Standard project management procedures',
                    'Quarterly risk reviews',
                    'Focus on efficiency improvements',
                    'Share best practices with other projects',
                    'Consider as benchmark projects'
                ]
            }
        
        print("✅ Hotspot recommendations generated")
        
        return recommendations
    
    def analyze_hotspots(self, df):
        """
        Complete hotspot analysis pipeline
        """
        print("🚀 Starting comprehensive hotspot analysis...")
        
        # Create risk features
        risk_features = self.create_risk_features(df)
        
        # Perform clustering
        clustering_results, best_method, scaler = self.perform_multiple_clustering(risk_features)
        
        # Detect anomalies
        anomaly_labels, anomaly_scores, anomaly_scaler = self.detect_anomalies(risk_features)
        
        # Calculate hotspot scores
        hotspot_scores, hotspot_categories = self.calculate_hotspot_scores(
            clustering_results, anomaly_scores, best_method
        )
        
        # Create visualizations
        self.visualize_hotspots(risk_features, hotspot_scores, hotspot_categories, 
                               clustering_results, best_method)
        
        # Generate recommendations
        recommendations = self.generate_hotspot_recommendations(
            df, hotspot_scores, hotspot_categories
        )
        
        # Save results
        output_dir = os.path.join(os.path.dirname(self.models_path), 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save cluster assignments
        cluster_df = pd.DataFrame({
            'project_index': range(len(df)),
            'cluster_label': clustering_results[best_method]['labels'],
            'hotspot_score': hotspot_scores,
            'risk_category': hotspot_categories,
            'anomaly_score': anomaly_scores
        })
        
        # Add original project data if available
        if 'project_id' in df.columns:
            cluster_df['project_id'] = df['project_id'].values
        if 'project_type' in df.columns:
            cluster_df['project_type'] = df['project_type'].values
        if 'location' in df.columns:
            cluster_df['location'] = df['location'].values
        
        cluster_df.to_csv(f'{output_dir}cluster_assignments.csv', index=False)
        
        # Save recommendations
        import json
        with open(f'{output_dir}hotspot_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        # Save model artifacts
        joblib.dump(self.clustering_models, f'{self.models_path}clustering_models.pkl')
        joblib.dump(self.anomaly_models, f'{self.models_path}anomaly_models.pkl')
        
        print("✅ Comprehensive hotspot analysis completed!")
        
        return {
            'clustering_results': clustering_results,
            'best_method': best_method,
            'hotspot_scores': hotspot_scores,
            'hotspot_categories': hotspot_categories,
            'recommendations': recommendations,
            'cluster_df': cluster_df,
            'risk_features': risk_features
        }

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = PowerGridHotspotAnalyzer()
    
    print("POWERGRID Hotspot Analyzer ready!")
    print("Use analyzer.analyze_hotspots(df) to analyze your project data")