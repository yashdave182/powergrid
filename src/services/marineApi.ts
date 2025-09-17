import { apiService } from '@/lib/api';
import type {
  SpeciesSearchParams,
  SpeciesSearchResponse,
  OceanographicData,
  EcosystemHealthData,
  PipelineStatus,
} from '@/types/api';

// Biodiversity API Services
export const biodiversityApi = {
  // Search species across OBIS and GBIF
  searchSpecies: async (params: SpeciesSearchParams) => {
    const queryParams = new URLSearchParams();
    if (params.scientific_name) queryParams.append('scientific_name', params.scientific_name);
    if (params.region) queryParams.append('region', params.region);
    if (params.data_source) queryParams.append('data_source', params.data_source);
    if (params.limit) queryParams.append('limit', params.limit.toString());

    return apiService.get<SpeciesSearchResponse>(`/biodiversity/species/search?${queryParams}`);
  },

  // Get species details
  getSpeciesDetails: async (speciesId: string, source: 'obis' | 'gbif' = 'obis') => {
    return apiService.get(`/biodiversity/species/${speciesId}/details?source=${source}`);
  },

  // Get biodiversity statistics
  getBiodiversityStatistics: async (region?: string) => {
    const queryParams = region ? `?region=${encodeURIComponent(region)}` : '';
    return apiService.get(`/biodiversity/diversity/statistics${queryParams}`);
  },

  // Identify species using AI
  identifySpecies: async (observationData: any) => {
    return apiService.post('/biodiversity/species/identify', observationData);
  },

  // Analyze eDNA data
  analyzeEdna: async (sampleId: string, sequenceData?: string, location?: string) => {
    const queryParams = new URLSearchParams({ sample_id: sampleId });
    if (sequenceData) queryParams.append('sequence_data', sequenceData);
    if (location) queryParams.append('location', location);

    return apiService.get(`/biodiversity/edna/analysis?${queryParams}`);
  },

  // Get datasets
  getDatasets: async (limit: number = 100) => {
    return apiService.get(`/biodiversity/datasets?limit=${limit}`);
  },

  // Get species checklist
  getSpeciesChecklist: async (region?: string, taxonId?: number, limit: number = 100) => {
    const queryParams = new URLSearchParams({ limit: limit.toString() });
    if (region) queryParams.append('region', region);
    if (taxonId) queryParams.append('taxon_id', taxonId.toString());

    return apiService.get(`/biodiversity/checklist?${queryParams}`);
  },

  // Search taxa
  searchTaxa: async (scientificName?: string, rank?: string, limit: number = 100) => {
    const queryParams = new URLSearchParams({ limit: limit.toString() });
    if (scientificName) queryParams.append('scientific_name', scientificName);
    if (rank) queryParams.append('rank', rank);

    return apiService.get(`/biodiversity/taxa/search?${queryParams}`);
  },

  // Get data providers
  getDataProviders: async () => {
    return apiService.get('/biodiversity/nodes');
  },

  // Test OBIS connection
  testObisConnection: async () => {
    return apiService.get('/biodiversity/test/obis');
  },

  // Test configuration
  testConfiguration: async () => {
    return apiService.get('/biodiversity/test/config');
  },

  // Test configuration
  testConfiguration: async () => {
    return apiService.get('/biodiversity/test/config');
  },
};

// Oceanography API Services
export const oceanographyApi = {
  // Get temperature profiles
  getTemperatureProfiles: async (latitude: number, longitude: number, startDate?: string, endDate?: string) => {
    const queryParams = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
    });
    if (startDate) queryParams.append('start_date', startDate);
    if (endDate) queryParams.append('end_date', endDate);

    return apiService.get<OceanographicData>(`/oceanography/temperature/profiles?${queryParams}`);
  },

  // Get salinity measurements
  getSalinityData: async (region: string, startDate?: string, endDate?: string) => {
    const queryParams = new URLSearchParams({ region });
    if (startDate) queryParams.append('start_date', startDate);
    if (endDate) queryParams.append('end_date', endDate);

    return apiService.get(`/oceanography/salinity/measurements?${queryParams}`);
  },

  // Get nutrient data
  getNutrientData: async (location: string, nutrients: string[] = ['nitrate', 'phosphate', 'silicate']) => {
    const queryParams = new URLSearchParams({ location });
    nutrients.forEach(nutrient => queryParams.append('nutrients', nutrient));

    return apiService.get(`/oceanography/chemistry/nutrients?${queryParams}`);
  },

  // Get current analysis
  getCurrentAnalysis: async (latitude: number, longitude: number, timePeriod = 'monthly') => {
    const queryParams = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
      time_period: timePeriod,
    });

    return apiService.get(`/oceanography/currents/analysis?${queryParams}`);
  },

  // Perform quality check
  performQualityCheck: async (oceanographicData: any) => {
    return apiService.post('/oceanography/data/quality-check', oceanographicData);
  },

  // Get climate trends
  getClimateTrends: async (region: string, parameter = 'temperature', years = 10) => {
    const queryParams = new URLSearchParams({
      region,
      parameter,
      years: years.toString(),
    });

    return apiService.get(`/oceanography/climate/trends?${queryParams}`);
  },
};

// Analytics API Services
export const analyticsApi = {
  // Analyze ecosystem health
  analyzeEcosystemHealth: async (ecosystemData: any) => {
    return apiService.post<EcosystemHealthData>('/analytics/ecosystem/health', ecosystemData);
  },

  // Predict species distribution
  predictSpeciesDistribution: async (speciesName: string, environmentalFactors: any, timeframe = 'current') => {
    const queryParams = new URLSearchParams({
      species_name: speciesName,
      prediction_timeframe: timeframe,
    });

    return apiService.post(`/analytics/predictive/species-distribution?${queryParams}`, {
      environmental_factors: environmentalFactors,
    });
  },
};

// Data Integration API Services
export const dataIntegrationApi = {
  // Integrate multi-source data
  integrateMultiSourceData: async (dataSources: any) => {
    return apiService.post('/data-integration/integrate/multi-source', dataSources);
  },

  // Standardize biodiversity data
  standardizeBiodiversityData: async (rawData: any, targetStandard = 'darwin_core') => {
    const queryParams = new URLSearchParams({ target_standard: targetStandard });
    return apiService.post(`/data-integration/standardize/biodiversity?${queryParams}`, rawData);
  },

  // Get pipeline status
  getPipelineStatus: async () => {
    return apiService.get<PipelineStatus>('/data-integration/pipeline/status');
  },
};

// Health Check
export const healthApi = {
  checkHealth: async () => {
    return apiService.get('/health');
  },
};