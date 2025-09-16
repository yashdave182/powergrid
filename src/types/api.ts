// Types for Marine Data Platform API
export interface SpeciesData {
  id: string;
  scientificName: string;
  kingdom?: string;
  phylum?: string;
  class?: string;
  order?: string;
  family?: string;
  genus?: string;
  species?: string;
  latitude?: number;
  longitude?: number;
  depth?: number;
  temperature?: number;
  observationDate?: string;
  source: 'obis' | 'gbif';
}

export interface SpeciesSearchParams {
  scientific_name?: string;
  region?: string;
  data_source?: 'obis' | 'gbif' | 'both';
  limit?: number;
}

export interface SpeciesSearchResponse {
  query: SpeciesSearchParams;
  results: {
    obis?: any;
    gbif?: any;
    ai_insights?: {
      analysis: string;
      confidence: string;
      species_count: number;
    };
  };
  total_sources: number;
}

export interface OceanographicData {
  location: {
    latitude: number;
    longitude: number;
  };
  temperature_data: {
    profiles: Array<{
      depth: string;
      temperature: number;
      timestamp: string;
    }>;
  };
  ai_interpretation: {
    interpretation: string;
  };
}

export interface EcosystemHealthData {
  health_metrics: {
    biodiversity_index: number;
    water_quality_score: number;
    overall_health_score: number;
  };
  ai_assessment: {
    analysis: string;
  };
  alert_level: 'green' | 'yellow' | 'red';
}

export interface PipelineStatus {
  timestamp: string;
  pipeline_status: {
    data_ingestion: {
      obis_pipeline: { status: string; records_processed: number };
      gbif_pipeline: { status: string; records_processed: number };
    };
    system_health: {
      cpu_usage: number;
      memory_usage: number;
      active_connections: number;
    };
  };
  overall_health: string;
}